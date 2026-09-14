#!/usr/bin/env bash
# Exact tracked-file bootstrap; Bash 3.2, Git, tar, Python 3.9+ and ordinary OS utilities.
set -euo pipefail
export GIT_OPTIONAL_LOCKS=0 GIT_NO_LAZY_FETCH=1 GIT_ALLOW_PROTOCOL=''
# Disable status helpers; attachment uses symbolic HEAD only, never checkout/network.
git() { command git -c core.fsmonitor=false -c submodule.recurse=false "$@"; }
cd "$(dirname "$0")/.."
root=$(pwd -P)
fail() { echo "Scaffold refused: $*" >&2; exit 2; }
operational() { echo "Scaffold failed: $*" >&2; exit 1; }
source "$root/scripts/git-safety.sh"
source_path=backend/template-goalstats-service
scratch='' lock='' journal='' installing=0 success=0 current_path='(preparation)'
finish() {
  local code=$?
  trap - EXIT
  if [[ "$installing" == 1 && "$success" == 0 ]]; then
    printf '%s\n' "$current_path" > "$scratch/failed-phase.txt" || true
    echo "Scaffold INCOMPLETE at: $current_path. No automatic rollback was attempted." >&2
    echo "Recovery directory: $scratch; operation indicator: $journal" >&2
    echo 'Inspect completed.txt, the manifest, and original placeholders. Preserve work and reconcile manually before removing the indicator. Rerun is refused.' >&2
    code=1
  elif [[ -n "$scratch" ]]; then
    rm -rf -- "$scratch"
  fi
  [[ -z "$lock" ]] || rmdir "$lock" 2>/dev/null || true
  if (( code != 0 && code != 2 )); then
    echo "Operational failure during $current_path; destination writes started: $installing" >&2
    code=1
  fi
  exit "$code"
}
trap finish EXIT
trap 'operational "Interrupted during $current_path"' HUP INT TERM

valid_service() { [[ "$1" =~ ^goalstats-[a-z0-9]+(-[a-z0-9]+)*-service$ ]]; }
[[ $# == 0 ]] || fail 'No positional arguments; use SERVICE, DOMAIN and DRY_RUN.'
service=${SERVICE-}; domain=${DOMAIN-}; dry=${DRY_RUN-false}
valid_service "$service" || fail 'SERVICE must be an approved goalstats-<name>-service token.'
[[ "$dry" == true || "$dry" == false ]] || fail 'DRY_RUN accepts exactly true or false.'
for tool in git tar mktemp mkdir rmdir rm cp chmod find sort cmp cat dirname tr; do
  command -v "$tool" >/dev/null || operational "Missing required tool: $tool"
done
command -v python3 >/dev/null || operational 'Missing required tool: Python 3.9+ (python3).'
python3 -I -B -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' || operational 'Python 3.9+ is required and must be usable.'
python3 -I -B scripts/scaffold-transform.py --domain="$domain"
parent_sha=$(git rev-parse --verify HEAD)
parent_git=$(git rev-parse --absolute-git-dir)
journal="$parent_git/team-squared-scaffold-incomplete"

parent_check() {
  [[ "$(git rev-parse HEAD)" == "$parent_sha" ]] || fail 'Parent HEAD changed during scaffolding.'
  clean_check "$root" parent
  [[ ! -e "$parent_git/team-squared-workspace-sync" ]] || fail 'Finish the incomplete workspace sync first.'
  [[ ! -e "$journal" && ! -L "$journal" ]] || fail "Incomplete scaffold requires manual review: $journal"
}
parent_check
# A per-workspace lock outside repositories also keeps dry run repository-read-only.
lock_key=$(printf '%s' "$parent_git" | git hash-object --stdin)
lock_candidate="/tmp/team-squared-scaffold-$lock_key.lock"
if ! (umask 077; mkdir "$lock_candidate") 2>/dev/null; then
  fail "Scaffold lock exists: $lock_candidate. Ensure no scaffold is running before manually removing a stale empty lock."
fi
lock=$lock_candidate

submodules=$(metadata "$root" "$parent_sha")
components=$(git show "$parent_sha:config/components.tsv")
approvals=$(git show "$parent_sha:config/scaffolds.tsv")
source_sha='' source_url='' dest_path='' dest_sha='' dest_url='' approved=''
component_match() {
  local wanted=$1 expected_role=$2 row role name path rest count=0
  while IFS= read -r row; do
    [[ -n "$row" && "$row" != \#* ]] || continue
    read -r role name path rest <<< "$row"
    if [[ "$path" == "$wanted" ]]; then
      [[ "$role" == "$expected_role" ]] || fail "Wrong component role for $wanted"
      count=$((count+1))
    fi
  done <<< "$components"
  [[ "$count" == 1 ]] || fail "Missing/duplicate component mapping for $wanted"
}
submodule_match() {
  local wanted=$1 path sha url count=0
  matched_sha=''; matched_url=''
  while IFS=$'\t' read -r path sha url; do
    if [[ "$path" == "$wanted" ]]; then
      matched_sha=$sha; matched_url=$url; count=$((count+1))
    fi
  done <<< "$submodules"
  [[ "$count" == 1 ]] || fail "Missing/duplicate submodule mapping for $wanted"
}
component_match "$source_path" reference
submodule_match "$source_path"; source_sha=$matched_sha; source_url=$matched_url
seen=$'\n'; domains=$'\n'
while IFS= read -r row; do
  [[ -n "$row" && "$row" != \#* ]] || continue
  [[ "$row" == *$'\t'*$'\t'* ]] || fail 'Approval rows require exactly three tab-separated fields.'
  name=${row%%$'\t'*}; rest=${row#*$'\t'}
  sha=${rest%%$'\t'*}; approved_domain=${rest#*$'\t'}
  [[ "$approved_domain" != *$'\t'* ]] || fail 'Approval rows require exactly three tab-separated fields.'
  python3 -I -B scripts/scaffold-transform.py --domain="$approved_domain"
  lower_domain=$(printf '%s' "$approved_domain" | tr '[:upper:]' '[:lower:]')
  [[ "$domains" != *$'\n'"$lower_domain"$'\n'* ]] || fail 'Duplicate derived domain identity.'
  domains="$domains$lower_domain"$'\n'
  valid_service "$name" && [[ "$sha" =~ ^[0-9a-f]{40}$ ]] || fail 'Malformed approval row.'
  [[ "$seen" != *$'\n'"$name"$'\n'* ]] || fail "Duplicate approval: $name"
  seen="$seen$name"$'\n'
  path="backend/$name"
  [[ "$path" != "$source_path" ]] || fail 'Template cannot be a scaffold destination.'
  component_match "$path" active
  submodule_match "$path"
  path_check "$root/$path"
  [[ -e "$root/$path/.git" ]] || fail "Approved destination is uninitialized: $path; use make setup separately."
  git -C "$root/$path" cat-file -e "$sha^{commit}" 2>/dev/null || fail "Unresolved placeholder commit for $name"
  if [[ "$name" == "$service" ]]; then
    [[ "$domain" == "$approved_domain" ]] || fail 'DOMAIN differs from approved registry DOMAIN.'
    dest_path=$path; dest_sha=$matched_sha; dest_url=$matched_url; approved=$sha
  fi
done <<< "$approvals"
[[ -n "$dest_path" ]] || fail "Unsupported service: $service"
src="$root/$source_path"; dest="$root/$dest_path"

repo_check() {
  local repo=$1 label=$2 sha=$3 url=$4
  path_check "$repo"
  [[ -e "$repo/.git" && ! -L "$repo/.git" ]] || fail "$label must be initialized with ordinary Git metadata; run make setup separately."
  [[ "$(git -C "$repo" rev-parse --show-toplevel)" == "$repo" ]] || fail "$label is not an independent repository."
  clean_check "$repo" "$label"
  [[ "$(git -C "$repo" rev-parse HEAD)" == "$sha" ]] || fail "$label is off-pin; preserve its commit and select the approved pin deliberately."
  [[ "$(git -C "$repo" remote get-url origin)" == "$url" ]] || fail "$label has a noncanonical origin."
}
state_check() {
  parent_check
  repo_check "$src" "$source_path" "$source_sha" "$source_url"
  repo_check "$dest" "$dest_path" "$dest_sha" "$dest_url"
  [[ "$dest_sha" == "$approved" ]] || fail 'Destination pin differs from approved placeholder commit.'
  branch=$(git -C "$dest" symbolic-ref --quiet HEAD || true)
  [[ -z "$branch" || "$branch" == refs/heads/master ]] || fail 'destination must be master or safely detached at the approved master pin.'
  [[ -z "$branch" ]] || branch=master
  for ref in refs/heads/master refs/remotes/origin/master; do
    [[ -z "$(git -C "$dest" symbolic-ref -q "$ref" || true)" ]] || fail 'Master refs must be ordinary commit refs.'
    git -C "$dest" show-ref --verify --quiet "$ref" || fail 'local master or origin/master is missing; no branch was created.'
  done
  master_sha=$(git -C "$dest" rev-parse refs/heads/master)
  tracking_sha=$(git -C "$dest" rev-parse refs/remotes/origin/master)
  [[ "$master_sha" == "$approved" && "$tracking_sha" == "$approved" ]] || fail 'destination HEAD, master, origin/master and approved placeholder pin must match.'
  # Plumbing attachment must enforce the branch ownership normally checked by switch.
  worktrees=$(git -C "$dest" worktree list --porcelain)
  owners=$(printf '%s\n' "$worktrees" | python3 -I -B -c 'import sys; print(sum(x == "branch refs/heads/master" for x in sys.stdin.read().splitlines()))')
  if [[ -z "$branch" ]]; then
    [[ "$owners" == 0 ]] || fail 'master is already checked out in another worktree.'
  else
    [[ "$owners" == 1 ]] || fail 'master is already checked out in another worktree.'
  fi
  [[ -z "$(git -C "$dest" ls-files --others --ignored --exclude-standard)" ]] || fail 'Ignored destination files must be preserved outside the destination before scaffolding.'
}
state_check
initial_branch=$branch
scratch=$(umask 077; mktemp -d "${TMPDIR:-/tmp}/team-squared-scaffold.XXXXXXXX")
mkdir "$scratch/payload" "$scratch/original"

# Restrict paths to portable, unambiguous names; Git administration is never payload.
validate_path() {
  local path=$1 lower component oldifs
  [[ "$path" =~ ^[a-zA-Z0-9._/-]+$ ]] || fail "Unsupported payload filename: $path"
  case "$path" in /*|*/../*|../*|*/..|*/./*|./*|*/.|*//*|-*) fail "Unsafe payload path: $path" ;; esac
  lower=$(printf '%s' "$path" | tr '[:upper:]' '[:lower:]')
  oldifs=$IFS; IFS=/; read -r -a parts <<< "$lower"; IFS=$oldifs
  for component in "${parts[@]}"; do
    case "$component" in
      .git|bin|obj|testresults|artifacts|coverage|logs|.vs|.vscode|.idea|pgdata|postgres-data|redis-data) fail "Forbidden tracked payload: $path" ;;
      .env|.env.*) [[ "$path" == .env.example ]] || fail "Forbidden tracked dotenv: $path" ;;
      *.user|*.suo|.ds_store|*.log|*.dump|*.backup|*.rdb|*.aof|*.sqlite|*.sqlite3) fail "Forbidden tracked runtime file: $path" ;;
    esac
  done
  case "/$lower/" in */docker/data/*|*/docker/volumes/*) fail "Forbidden Docker runtime data: $path" ;; esac
}

manifest() {
  local row mode type hash path lower has_readme=0 has_ignore=0 seen=$'\n'
  git -C "$src" ls-tree -rz "$source_sha" > "$scratch/tree"
  : > "$scratch/manifest.tsv"
  : > "$scratch/paths"
  while IFS= read -r -d '' row; do
    path=${row#*$'\t'}; read -r mode type hash <<< "${row%%$'\t'*}"
    [[ "$type" == blob && ( "$mode" == 100644 || "$mode" == 100755 ) ]] || fail "Unsupported payload type/mode: $path"
    validate_path "$path"
    [[ "$path" != README.md ]] || has_readme=1
    [[ "$path" != .gitignore ]] || has_ignore=1
    lower=$(printf '%s' "$path" | tr '[:upper:]' '[:lower:]')
    [[ "$seen" != *$'\n'"$lower"$'\n'* ]] || fail "Case-colliding payload path: $path"
    seen="$seen$lower"$'\n'
    printf '%s\t%s\t%s\n' "$mode" "$hash" "$path" >> "$scratch/manifest.tsv"
    printf '%s\n' "$path" >> "$scratch/paths"
  done < "$scratch/tree"
  [[ -s "$scratch/paths" ]] || fail 'Empty template payload.'
  [[ "$has_readme" == 1 && "$has_ignore" == 1 ]] || fail 'Template must track exact README.md and .gitignore paths.'
}
manifest

placeholder_check() {
  local row mode type hash path count=0
  git -C "$dest" ls-tree -rz "$approved" > "$scratch/placeholder-tree"
  while IFS= read -r -d '' row; do
    path=${row#*$'\t'}; read -r mode type hash <<< "${row%%$'\t'*}"
    [[ "$mode" == 100644 && "$type" == blob && ( "$path" == README.md || "$path" == .gitignore ) ]] || fail 'Placeholder must contain only regular README.md and .gitignore files.'
    [[ -f "$dest/$path" && ! -L "$dest/$path" && ! -x "$dest/$path" ]] || fail "Unexpected placeholder mode: $path"
    [[ "$(git hash-object --no-filters -- "$dest/$path")" == "$hash" ]] || fail "Customized placeholder: $path"
    count=$((count+1))
  done < "$scratch/placeholder-tree"
  [[ "$count" == 2 ]] || fail 'Both placeholder files are required.'
  [[ -z "$(find "$dest" -path "$dest/.git" -prune -o -mindepth 1 -type d -print)" ]] || fail 'Unexpected destination directories require manual preservation.'
}
placeholder_check

# Ignore compatibility is deliberately conservative, never an automatic merge.
ignore_rules() {
  local line
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" != *$'\r'* ]] || fail 'CRLF ignore rules require manual reconciliation.'
    [[ -z "$line" || "$line" == \#* ]] || printf '%s\n' "$line"
  done
}
ignore_check() {
git -C "$dest" show "$approved:.gitignore" | ignore_rules > "$scratch/dest-rules"
cat "$scratch/output/.gitignore" | ignore_rules > "$scratch/source-rules"
if ! cmp -s "$scratch/dest-rules" "$scratch/source-rules"; then
  rules=(); while IFS= read -r rule; do
    [[ "$rule" != '!'* ]] || fail 'Different ignore files with destination negations require manual reconciliation.'
    rules+=("$rule")
  done < "$scratch/dest-rules"
  next=0
  while IFS= read -r rule; do
    if [[ "$rule" == '!'* ]]; then
      [[ "$rule" == '!.env.example' ]] || fail 'Unsupported template ignore negation.'
      if git -C "$dest" check-ignore --no-index -q -- .env.example; then
        fail 'Template exception would undo destination .env.example exclusion.'
      fi
    fi
    if (( next < ${#rules[@]} )) && [[ "$rule" == "${rules[$next]}" ]]; then next=$((next+1)); fi
  done < "$scratch/source-rules"
  (( next == ${#rules[@]} )) || fail 'Template drops or reorders destination ignore rules.'
fi
}

payload_error() {
  if [[ "$installing" == 1 ]]; then operational "$*"; else fail "$*"; fi
}
verify_payload() {
  local directory=$1 mode hash path actual
  while IFS=$'\t' read -r mode hash path; do
    [[ -f "$directory/$path" && ! -L "$directory/$path" ]] || payload_error "Payload missing/nonregular: $path"
    actual=$(git hash-object --no-filters -- "$directory/$path")
    [[ "$actual" == "$hash" ]] || payload_error "Payload content mismatch: $path"
    if [[ "$mode" == 100755 ]]; then
      [[ -x "$directory/$path" ]] || payload_error "Missing executable bit: $path"
    else [[ ! -x "$directory/$path" ]] || payload_error "Unexpected executable bit: $path"; fi
  done < "$scratch/manifest.tsv"
  if [[ "$directory" == "$dest" ]]; then
    (cd "$directory"; find . -path ./.git -prune -o -print) | LC_ALL=C sort > "$scratch/actual-paths"
  else
    (cd "$directory"; find . -print) | LC_ALL=C sort > "$scratch/actual-paths"
  fi
  {
    printf '.\n'
    while IFS= read -r path; do
      printf './%s\n' "$path"
      while [[ "$path" == */* ]]; do path=${path%/*}; printf './%s\n' "$path"; done
    done < "$scratch/paths"
  } | LC_ALL=C sort -u > "$scratch/expected-paths"
  cmp -s "$scratch/actual-paths" "$scratch/expected-paths" || payload_error 'Payload paths differ from the committed tree.'
}
identity() {
  local repo=$1 gitdir index
  gitdir=$(git -C "$repo" rev-parse --absolute-git-dir)
  index=$(git -C "$repo" rev-parse --git-path index)
  [[ "$index" == /* ]] || index="$repo/$index"
  printf 'repo %s\ngitdir %s\n' "$repo" "$gitdir"
  git -C "$repo" rev-parse HEAD
  [[ "${2:-}" == attachment ]] || git -C "$repo" symbolic-ref --quiet HEAD || true
  git -C "$repo" show-ref || true
  git -C "$repo" config --local --list
  git hash-object --no-filters -- "$index"
  if [[ -f "$repo/.git" ]]; then git hash-object --no-filters -- "$repo/.git"; fi
}
identity "$root" > "$scratch/parent.identity"
identity "$dest" > "$scratch/dest.identity"
identity "$dest" attachment > "$scratch/dest.attachment-before"
current_path='archive/export'
git -C "$src" -c tar.umask=0022 archive --format=tar "$source_sha" > "$scratch/template.tar"
tar -xpf "$scratch/template.tar" -C "$scratch/payload"
verify_payload "$scratch/payload"
[[ -f "$scratch/payload/README.md" && -f "$scratch/payload/.gitignore" ]] || fail 'Template must supply both placeholder replacements.'

cp "$scratch/manifest.tsv" "$scratch/source-manifest.tsv"
current_path='identity transformation'
printf 'SERVICE=%s\n' "$service"
python3 -I -B scripts/scaffold-transform.py --domain="$domain" --source="$scratch/payload" --source-manifest="$scratch/source-manifest.tsv" --output="$scratch/output" --evidence="$scratch" --source-sha="$source_sha"
cp "$scratch/transformed.tsv" "$scratch/manifest.tsv"
: > "$scratch/paths"
while IFS=$'\t' read -r mode hash path; do
  validate_path "$path"
  printf '%s\n' "$path" >> "$scratch/paths"
done < "$scratch/manifest.tsv"
verify_payload "$scratch/output"
ignore_check

current_path='pre-install validation'
state_check
[[ "$branch" == "$initial_branch" ]] || fail 'Destination branch changed during preparation.'
placeholder_check
identity "$root" > "$scratch/parent.recheck"
identity "$dest" > "$scratch/dest.recheck"
cmp -s "$scratch/parent.identity" "$scratch/parent.recheck" || fail 'Parent Git identity changed during preparation.'
cmp -s "$scratch/dest.identity" "$scratch/dest.recheck" || fail 'Destination Git identity changed during preparation.'
if [[ -z "$branch" ]]; then
  echo 'DESTINATION STATE: DETACHED AT APPROVED PIN'
  echo 'PLANNED BRANCH ACTION: ATTACH TO master'
  echo 'Destination is detached at the approved master pin; scaffold would attach it to master before installation.'
else
  echo 'DESTINATION STATE: master'
  echo 'PLANNED BRANCH ACTION: NONE'
fi
printf 'DESTINATION HEAD: %s\nMASTER HEAD: %s\nORIGIN/MASTER HEAD: %s\nPLACEHOLDER SHA: %s\n' "$dest_sha" "$master_sha" "$tracking_sha" "$approved"
printf 'Scaffold (DRY_RUN=%s)\nSource: %s @ %s\nDestination: %s @ %s [%s]\n' "$dry" "$source_path" "$source_sha" "$dest_path" "$dest_sha" "$branch"
while IFS= read -r path; do
  case "$path" in README.md|.gitignore) printf '  REPLACE approved placeholder %s\n' "$path" ;; *) printf '  ADD %s\n' "$path" ;; esac
done < "$scratch/paths"
if [[ "$dry" == true ]]; then
  echo 'Dry run validated. No repository files or Git state were changed.'
  exit 0
fi
if [[ -z "$branch" ]]; then
  current_path='master attachment'
  if ! git -C "$dest" symbolic-ref -m "scaffold: attach approved destination to master" HEAD refs/heads/master; then
    git -C "$dest" status --short --branch >&2 || true
    git -C "$dest" rev-parse HEAD >&2 || true
    operational 'could not attach destination to master. No scaffold files were written.'
  fi
  echo "Attached $dest_path to master at $dest_sha."
fi
current_path='post-attachment validation (no scaffold files written)'
state_check
[[ "$branch" == master ]] || fail 'Destination changed after attachment; no scaffold files were written.'
placeholder_check
identity "$dest" attachment > "$scratch/dest.attachment-after"
cmp -s "$scratch/dest.attachment-before" "$scratch/dest.attachment-after" || fail 'Destination identity changed during attachment; no scaffold files were written.'
identity "$root" > "$scratch/parent.recheck"
cmp -s "$scratch/parent.identity" "$scratch/parent.recheck" || fail 'Parent Git identity changed during attachment.'
# Preserve the original evidence; installation has its own verified baseline.
identity "$dest" > "$scratch/dest.installation"
cp "$dest/README.md" "$scratch/original/README.md"
cp "$dest/.gitignore" "$scratch/original/.gitignore"
: > "$scratch/completed.txt"
(umask 077; mkdir "$journal")
installing=1
printf '%s\n' "$scratch" > "$journal/recovery-directory"
while IFS=$'\t' read -r mode hash path; do
  current_path=$path
  mkdir -p "$(dirname "$dest/$path")"
  cp "$scratch/output/$path" "$dest/$path"
  if [[ "$mode" == 100755 ]]; then chmod 755 "$dest/$path"; else chmod 644 "$dest/$path"; fi
  printf '%s\n' "$path" >> "$scratch/completed.txt"
done < "$scratch/manifest.tsv"
current_path='final verification'
verify_payload "$dest"
identity "$root" > "$scratch/parent.after"
identity "$dest" > "$scratch/dest.after"
cmp -s "$scratch/parent.identity" "$scratch/parent.after" || operational 'Parent Git identity changed.'
cmp -s "$scratch/dest.installation" "$scratch/dest.after" || operational 'Destination Git identity changed.'
rm "$journal/recovery-directory"
rmdir "$journal"
success=1
printf 'Scaffold complete from %s. Child files are intentionally unstaged; parent pin and post-attachment Git identity are unchanged.\n' "$source_sha"
echo 'Review child git status --short and git diff, including untracked files. Identity transformation only; Item/Action and migration operations are unchanged. No runtime certification was performed.'
