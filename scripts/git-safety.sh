#!/usr/bin/env bash
# Read-only checks shared by workspace commands. Caller supplies root and fail().
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
    fail 'Commit or preserve work deliberately before workspace changes. No automatic stash/reset/clean.'
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
