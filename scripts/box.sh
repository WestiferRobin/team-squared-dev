#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
action=${1:?Missing action}
mode=${2-local}
project=${3:-team-squared-$mode}
registry=config/components.tsv
fail() { echo "Error: $*" >&2; exit 2; }
case "$action" in list|setup|build|run|stop|logs|migrate|test|smoke) ;; *) fail "Unknown action: $action" ;; esac
if [[ "$action" == list ]]; then
  while read -r role name path service migration ready body health smoke; do
    [[ "$role" == active || "$role" == reference || "$role" == docs ]] || continue
    printf '  %-9s %-18s %s\n' "$role" "$name" "$path"
  done < "$registry"
  exit 0
fi
case "$mode" in local|dev) ;; *) fail "Unsupported ENV=$mode. Use local or dev." ;; esac
case "$project" in team-squared-$mode|team-squared-$mode-*) ;; *) fail "PROJECT must be team-squared-$mode or begin team-squared-$mode-." ;; esac
[[ "$project" =~ ^[a-z0-9][a-z0-9_-]*$ ]] || fail 'Invalid project name.'

# Every configured submodule must have a COMMITTED gitlink; staged-only pins cannot
# define a reproducible checkout. Inspect all children before changing any checkout.
check_pins() {
  local errors=0 path record staged actual dirty
  if ! git cat-file -e HEAD:.gitmodules 2>/dev/null; then
    echo 'Missing committed .gitmodules. Current staged additions are not published pins.' >&2
    errors=1
  elif ! git diff --quiet HEAD -- .gitmodules; then
    echo '.gitmodules differs from HEAD; setup will not use uncommitted URLs.' >&2
    errors=1
  fi
  while read -r key path; do
    [[ -n "$path" ]] || continue
    if [[ -e "$path/.git" ]]; then
      dirty=$(git -C "$path" status --porcelain --untracked-files=all --ignore-submodules=none)
      if [[ -n "$dirty" ]]; then
        echo "Dirty submodule preserved: $path. Setup will not checkout or overwrite it." >&2
        errors=1
      fi
    fi
    record=$(git ls-tree HEAD -- "$path")
    if [[ "$record" != 160000\ commit\ * ]]; then
      echo "Missing committed submodule pin: $path" >&2
      errors=1
      continue
    fi
    staged=$(git ls-files --stage -- "$path")
    if [[ $(printf '%s\n' "$record" | awk '{print $3}') != $(printf '%s\n' "$staged" | awk '{print $2}') ]]; then
      echo "Staged pin differs from HEAD: $path; no automatic pointer changes." >&2
      errors=1
    fi
  done < <(git config --file .gitmodules --get-regexp '^submodule\..*\.path$' || true)
  return "$errors"
}

load_compose() {
  if [[ "$mode" == local ]]; then FRONTEND_PORT=33000; else FRONTEND_PORT=33001; fi
  local file="infra/.env.$mode" line key value
  if [[ -f "$file" ]]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
      line=${line%$'\r'}
      [[ "$line" =~ ^[[:space:]]*(#.*)?$ ]] && continue
      [[ "$line" == *=* ]] || fail "Invalid assignment in $file"
      key=${line%%=*}; value=${line#*=}
      [[ "$key" == FRONTEND_PORT ]] || fail "Unsupported configuration key $key in $file"
      FRONTEND_PORT=$value
    done < "$file"
  fi
  [[ "$FRONTEND_PORT" =~ ^[0-9]{1,5}$ ]] && (( 10#$FRONTEND_PORT >= 1 && 10#$FRONTEND_PORT <= 65535 )) || fail 'FRONTEND_PORT must be 1–65535.'
  export FRONTEND_PORT
  compose=(docker compose --env-file /dev/null -p "$project" -f "infra/compose.$mode.yml")
}

# Fail as a complete box, never silently run just the frontend or the template.
check_contracts() {
  local errors=0 services
  services=$("${compose[@]}" --profile tooling config --services) || return $?
  while read -r role name path service migration ready body health smoke; do
    [[ "$role" == active ]] || continue
    for file in Dockerfile Makefile; do
      if [[ ! -f "$path/$file" ]]; then
        echo "Missing active child contract: $path/$file" >&2
        errors=1
      fi
    done
    if ! printf '%s\n' "$services" | grep -Fxq "$service"; then
      echo "Active service $name has no $mode Compose definition ($service)." >&2
      errors=1
    fi
    if [[ "$migration" == pending || "$ready" == pending || "$body" == pending || "$health" == pending || "$smoke" == pending ]]; then
      echo "Unverified active contract: $path (migration/readiness/health/request details pending)." >&2
      errors=1
    fi
    if [[ "$migration" != none && "$migration" != pending ]] && ! printf '%s\n' "$services" | grep -Fxq "$migration"; then
      echo "Missing child tooling Compose service: $migration ($path)" >&2
      errors=1
    fi
  done < "$registry"
  return "$errors"
}
probe() {
  local probe_mode=$1
  local arguments=()
  while read -r role name path service migration ready body health smoke; do
    [[ "$role" == active ]] || continue
    arguments+=("$name" "$ready" "$body" "$health" "$smoke")
  done < "$registry"
  "${compose[@]}" exec -T frontend node - "$probe_mode" "${arguments[@]}" < scripts/probe.cjs
}

if [[ "$action" == setup ]]; then
  for command in git docker make; do command -v "$command" >/dev/null || fail "Missing $command"; done
  make_version=$(make --version)
  [[ "$make_version" =~ GNU\ Make\ ([0-9]+)\.([0-9]+) ]] || fail 'GNU Make 3.81+ is required.'
  (( BASH_REMATCH[1] > 3 || (BASH_REMATCH[1] == 3 && BASH_REMATCH[2] >= 81) )) || fail 'GNU Make 3.81+ is required.'
  docker compose version
  docker info >/dev/null || fail 'Start Docker Engine/Desktop.'
  for selected in local dev; do
    file="infra/.env.$selected"
    if [[ -e "$file" || -L "$file" ]]; then echo "Preserved $file"
    else (set -o noclobber; cat "infra/.env.$selected.example" > "$file"); echo "Created $file"; fi
  done
  check_pins || fail 'Submodule setup blocked before any child checkout changes. See docs/READINESS.md.'
  git submodule sync --recursive
  git submodule update --init --recursive --checkout
  load_compose
  check_contracts || fail 'Active child contracts are incomplete. No stack was started.'
  echo 'Setup complete. Child setup is unnecessary: images prepare tooling; box configuration is parent-owned.'
  exit 0
fi
if [[ "$action" == test ]]; then
  missing=0
  while read -r role name path service migration ready body health smoke; do
    [[ "$role" == active ]] || continue
    if [[ ! -f "$path/Makefile" ]]; then echo "Missing active test interface: $path/Makefile" >&2; missing=1; fi
  done < "$registry"
  (( missing == 0 )) || fail 'Active child test interfaces are missing; no partial suite was run.'
  while read -r role name path service migration ready body health smoke; do
    [[ "$role" == active ]] || continue
    echo "Testing ACTIVE $name: $path (normal suite; E2E=false)"
    env -u ENV -u PROJECT -u MAKEFLAGS -u MFLAGS -u MAKEOVERRIDES -u E2E \
      make -C "$path" test E2E=false
  done < "$registry"
  exit 0
fi
load_compose
case "$action" in
  stop) exec "${compose[@]}" down ;;
  logs) exec "${compose[@]}" logs -f ;;
esac
check_contracts || fail 'Complete active box unavailable; no build, migration, or startup was attempted.'
case "$action" in
  build) "${compose[@]}" build ;;
  migrate)
    while read -r role name path service migration ready body health smoke; do
      [[ "$role" == active && "$migration" != none ]] || continue
      echo "Migrating ACTIVE $name using $migration in $project"
      "${compose[@]}" --profile tooling run --rm --build "$migration"
    done < "$registry" ;;
  run)
    echo "Starting COMPLETE ACTIVE box: $project ($mode)"
    bash scripts/box.sh list
    if ! "${compose[@]}" up -d --build --wait --wait-timeout 180; then
      "${compose[@]}" ps -a >&2
      fail "Startup failed; containers retained. Inspect make logs ENV=$mode PROJECT=$project"
    fi
    if ! probe readiness; then
      fail "Readiness failed; containers retained. Inspect make logs ENV=$mode PROJECT=$project; apply migrations explicitly with make migrate ENV=$mode PROJECT=$project"
    fi
    echo "Frontend: http://127.0.0.1:$FRONTEND_PORT" ;;
  smoke) probe smoke ;;
esac
