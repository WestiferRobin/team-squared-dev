#!/usr/bin/env bash
# Git-only workspace preparation. Compatible with macOS Bash 3.2.
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
fail() { echo "Workspace error: $*" >&2; exit 2; }
git_safe() { git -c submodule.recurse=false -c fetch.recurseSubmodules=false "$@"; }

prerequisites() {
  local tool version
  for tool in git make bash ssh cat dirname mkdir mv rm; do
    command -v "$tool" >/dev/null || fail "Missing $tool; see README workspace prerequisites."
  done
  version=$(make --version)
  [[ "$version" =~ GNU\ Make\ ([0-9]+)\.([0-9]+) ]] || fail 'GNU Make 3.81+ is required.'
  (( BASH_REMATCH[1] > 3 || (BASH_REMATCH[1] == 3 && BASH_REMATCH[2] >= 81) )) || fail 'GNU Make 3.81+ is required.'
  git rev-parse --verify HEAD >/dev/null || fail 'A committed parent checkout is required.'
}

# Emit validated path<TAB>gitlink<TAB>URL rows from a COMMIT, never the worktree.
metadata() {
  local repo=$1 ref=$2 rows='' key path name url record mode type sha actual seen=$'\n'
  if git -C "$repo" cat-file -e "$ref:.gitmodules" 2>/dev/null; then
    rows=$(git -C "$repo" config --blob "$ref:.gitmodules" --get-regexp '^submodule\..*\.path$') || {
      [[ $? == 1 ]] || fail "Cannot read .gitmodules in $repo at $ref."
    }
  fi
  while read -r key path; do
    [[ -n "$key" ]] || continue
    case "$path" in ''|/*|.*|*/../*|*/..|*/./*|*/.|*/.git|*/.git/*|*\\*|*$'\t'*|*$'\n'*) fail "Unsafe submodule path: $path" ;; esac
    [[ "$seen" != *$'\n'"$path"$'\n'* ]] || fail "Duplicate submodule path: $path"
    seen="$seen$path"$'\n'
    name=${key#submodule.}; name=${name%.path}
    url=$(git -C "$repo" config --blob "$ref:.gitmodules" --get "submodule.$name.url") || fail "Missing URL for $path"
    [[ -n "$url" && "$url" != *$'\n'* && "$url" != *$'\t'* ]] || fail "Invalid URL for $path"
    record=$(git -C "$repo" ls-tree "$ref" -- "$path")
    read -r mode type sha actual <<< "$record"
    [[ "$mode" == 160000 && "$type" == commit ]] || fail "No committed gitlink for $path at $ref"
    printf '%s\t%s\t%s\n' "$path" "$sha" "$url"
  done <<< "$rows"
  while IFS= read -r -d '' record; do
    [[ "$record" == 160000\ commit\ * ]] || continue
    path=${record#*$'\t'}
    [[ "$seen" == *$'\n'"$path"$'\n'* ]] || fail "Unregistered gitlink: $path"
  done < <(git -C "$repo" ls-tree -rz "$ref")
}

operation_check() {
  local repo=$1 label=$2 marker
  for marker in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply sequencer BISECT_START; do
    if (cd "$repo" && [[ -e "$(git rev-parse --git-path "$marker")" ]]); then
      fail "Git operation in progress in $label ($marker). Finish or deliberately abort it first."
    fi
  done
}

clean_check() {
  local repo=$1 label=$2 dirty staged
  operation_check "$repo" "$label"
  dirty=$(git -C "$repo" status --porcelain=v1 --untracked-files=all --ignore-submodules=all)
  staged=$(git -C "$repo" diff --cached --name-status --ignore-submodules=none HEAD)
  if [[ -n "$dirty" || -n "$staged" ]]; then
    printf 'Unsafe work preserved in %s:\n%s\n%s\n' "$label" "$dirty" "$staged" >&2
    fail 'Commit or preserve work deliberately before setup/sync. No automatic stash/reset/clean.'
  fi
}

path_check() {
  local full=$1 part=$1
  while [[ "$part" != "$root" && "$part" != / ]]; do
    [[ ! -L "$part" ]] || fail "Symlink occupies submodule path: $part"
    part=${part%/*}
  done
  if [[ ! -e "$full/.git" ]]; then
    [[ ! -e "$full" || -d "$full" ]] || fail "Unexpected occupied child path: $full"
    if [[ -d "$full" ]]; then
      local entries=("$full"/* "$full"/.[!.]* "$full"/..?*) entry
      for entry in "${entries[@]}"; do
        [[ ! -e "$entry" && ! -L "$entry" ]] || fail "Unexpected nonempty child path preserved: $full"
      done
    fi
  else
    [[ "$(git -C "$full" rev-parse --show-toplevel)" == "$full" ]] || fail "Invalid child repository at $full"
  fi
}

# A resume journal permits only the exact pre-sync child commits, never arbitrary off-pin work.
old_allowed() {
  local label=$1 sha=$2 p s
  [[ "$resume" == 1 ]] || return 1
  while IFS=$'\t' read -r p s; do
    [[ "$p" != "$label" || "$s" != "$sha" ]] || return 0
  done < "$journal/children"
  return 1
}

inspect_tree() {
  local repo=$1 label=$2 ref=$3 rows path sha url full child actual
  clean_check "$repo" "$label"
  rows=$(metadata "$repo" "$ref") || return $?
  while IFS=$'\t' read -r path sha url; do
    [[ -n "$path" ]] || continue
    full="$repo/$path"; child=${full#"$root/"}
    path_check "$full"
    if [[ -e "$full/.git" ]]; then
      actual=$(git -C "$full" rev-parse HEAD)
      if [[ "$actual" != "$sha" ]] && ! old_allowed "$child" "$actual"; then
        fail "Clean off-pin child preserved: $child (HEAD $actual; pin $sha). Select its approved pin manually or integrate its commit deliberately."
      fi
      inspect_tree "$full" "$child" "$actual"
    fi
  done <<< "$rows"
}

snapshot_children() {
  local repo=$1 rows path sha url full
  rows=$(metadata "$repo" HEAD) || return $?
  while IFS=$'\t' read -r path sha url; do
    [[ -n "$path" ]] || continue
    full="$repo/$path"
    if [[ -e "$full/.git" ]]; then
      printf '%s\t%s\n' "${full#"$root/"}" "$(git -C "$full" rev-parse HEAD)"
      snapshot_children "$full"
    fi
  done <<< "$rows"
}

transition_check() {
  local repo=$1 target=$2 old new path sha url p s u found file candidate record
  old=$(metadata "$repo" HEAD) || return $?
  new=$(metadata "$repo" "$target") || return $?
  while IFS=$'\t' read -r path sha url; do
    [[ -n "$path" ]] || continue
    found=0
    while IFS=$'\t' read -r p s u; do [[ "$p" != "$path" ]] || found=1; done <<< "$new"
    if [[ "$found" == 0 && ( -e "$repo/$path" || -L "$repo/$path" ) ]]; then
      fail "Incoming removal/rename of $path requires manual reconciliation; repositories preserved."
    fi
  done <<< "$old"
  while IFS=$'\t' read -r path sha url; do
    [[ -n "$path" ]] || continue
    path_check "$repo/$path"
  done <<< "$new"
  # Ignored artifacts are harmless only while incoming commits do not track them.
  while IFS= read -r -d '' file; do
    candidate=$file
    while [[ -n "$candidate" ]]; do
      record=$(git -C "$repo" ls-tree "$target" -- "$candidate")
      if [[ -n "$record" && "$record" != 040000\ tree\ * ]]; then
        fail "Incoming commit would replace ignored file $repo/$file; preserve it manually first."
      fi
      [[ "$candidate" == */* ]] || break
      candidate=${candidate%/*}
    done
  done < <(git -C "$repo" ls-files --others --ignored --exclude-standard -z)
}

materialize() {
  local repo=$1 rows path sha url full actual
  rows=$(metadata "$repo" HEAD) || return $?
  git_safe -C "$repo" submodule sync
  while IFS=$'\t' read -r path sha url; do
    [[ -n "$path" ]] || continue
    full="$repo/$path"
    path_check "$full"
    if [[ -e "$full/.git" ]]; then
      actual=$(git -C "$full" rev-parse HEAD)
      if [[ "$actual" != "$sha" ]]; then
        git -C "$full" cat-file -e "$sha^{commit}" 2>/dev/null || git_safe -C "$full" fetch --no-recurse-submodules origin "$sha"
        transition_check "$full" "$sha"
        git_safe -C "$repo" submodule update --init --checkout --no-fetch -- "$path"
      fi
    else
      git_safe -C "$repo" submodule update --init --checkout -- "$path"
    fi
    [[ "$(git -C "$full" rev-parse HEAD)" == "$sha" ]] || fail "Child pin verification failed: $full"
    materialize "$full"
  done <<< "$rows"
}

report() {
  local repo=$1 rows path sha url full branch
  rows=$(metadata "$repo" HEAD) || return $?
  while IFS=$'\t' read -r path sha url; do
    [[ -n "$path" ]] || continue
    full="$repo/$path"
    if [[ -e "$full/.git" ]]; then
      branch=$(git -C "$full" symbolic-ref --quiet --short HEAD || true)
      printf '  %s %s [%s]\n' "$(git -C "$full" rev-parse HEAD)" "${full#"$root/"}" "${branch:-detached}"
      report "$full"
    else printf '  %s [uninitialized; pin %s]\n' "${full#"$root/"}" "$sha"; fi
  done <<< "$rows"
}

on_exit() {
  local status=$?
  if (( status != 0 )) && [[ -d "$journal" ]]; then
    echo 'Sync incomplete; no rollback/reset was attempted. Repositories and resume metadata were preserved.' >&2
    echo 'Resolve the reported issue, then retry: make sync' >&2
  fi
}

# Keep execution inside a parsed function: merge may replace this script on disk.
main() {
  local action=${1:-} version branch head target selected file state_tmp
  prerequisites
  journal="$(git rev-parse --absolute-git-dir)/team-squared-workspace-sync"
  resume=0
  case "$action" in setup|sync|status|_resume) ;; *) fail 'Usage: workspace.sh setup|sync|status' ;; esac
  if [[ "$action" == status ]]; then report "$root"; return; fi
  if [[ "$action" == sync || "$action" == _resume ]]; then
    branch=$(git symbolic-ref --quiet --short HEAD || true)
    [[ "$branch" == master ]] || fail 'Sync requires parent master. Switch deliberately; setup can prepare another branch or detached commit.'
  fi
  if [[ -d "$journal" ]]; then
    [[ "$action" != setup ]] || fail 'A sync is incomplete. Finish it with make sync before setup.'
    read -r target < "$journal/target"
    read -r head < "$journal/before"
    [[ "$(git rev-parse HEAD)" == "$head" || "$(git rev-parse HEAD)" == "$target" ]] || fail 'Parent moved outside the recorded sync. Inspect resume metadata manually.'
    resume=1
  elif [[ "$action" == _resume ]]; then fail 'No interrupted sync to resume.'; fi
  inspect_tree "$root" parent HEAD
  if [[ "$action" == setup ]]; then
    materialize "$root"
    inspect_tree "$root" parent HEAD
    for selected in local dev; do
      file="infra/.env.$selected"
      if [[ -e "$file" || -L "$file" ]]; then echo "Preserved $file"
      else (set -o noclobber; cat "infra/.env.$selected.example" > "$file"); echo "Created $file"; fi
    done
  else
    trap on_exit EXIT
    if [[ "$resume" == 0 ]]; then
      git_safe fetch --no-recurse-submodules origin refs/heads/master:refs/remotes/origin/master
      head=$(git rev-parse HEAD); target=$(git rev-parse refs/remotes/origin/master)
      git merge-base --is-ancestor "$head" "$target" || fail 'Parent is locally ahead or divergent. Publish/reconcile deliberately; sync will not merge or reset it.'
      transition_check "$root" "$target"
      state_tmp="$journal.tmp.$$"
      mkdir "$state_tmp"
      printf '%s\n' "$head" > "$state_tmp/before"
      printf '%s\n' "$target" > "$state_tmp/target"
      snapshot_children "$root" > "$state_tmp/children"
      mv "$state_tmp" "$journal"
    fi
    if [[ "$(git rev-parse HEAD)" != "$target" ]]; then
      transition_check "$root" "$target"
      git_safe -c core.hooksPath=/dev/null merge --ff-only --no-autostash --no-overwrite-ignore "$target"
      # Resume through the UPDATED helper and metadata, without fetching another parent target.
      exec bash scripts/workspace.sh _resume
    fi
    materialize "$root"
    resume=0
    inspect_tree "$root" parent HEAD
    rm -r "$journal"
  fi
  echo 'Workspace ready. Submodules are at approved commits; runtime readiness is separate.'
  report "$root"
  echo 'Detached HEAD is normal. Before editing a child: cd <child>; git switch -c <feature-branch>'
  echo 'Docker is needed only for container workflows. goalstats-user-service remains runtime-pending until implemented.'
}
main "$@"
