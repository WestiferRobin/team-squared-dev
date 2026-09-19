#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
source scripts/infra-config.sh
action=${1:?Missing action}
mode=${2-local}
project=${3:-team-squared-$mode}
registry=config/components.tsv
fail() { echo "Error: $*" >&2; exit 2; }
case "$action" in list|build|run|stop|logs|migrate|test|smoke) ;; *) fail "Unknown action: $action" ;; esac
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

load_compose() {
  infra_load || fail 'Invalid infra machine configuration.'
  [[ "$infra_legacy_local" == 0 && ! -e infra/.env.dev ]] || fail 'Run make setup to migrate infra configuration.'
  if [[ "$mode" == local ]]; then FRONTEND_PORT=$LOCAL_FRONTEND_PORT; else FRONTEND_PORT=$DEV_FRONTEND_PORT; fi
  export FRONTEND_PORT
  compose=(docker compose --env-file /dev/null -p "$project" -f "infra/compose.$mode.yml")
}

# Classify approved Python backends before executing any child tooling.
check_python_contracts() {
  local role name path rest errors=0
  while read -r role name path rest; do
    [[ "$role" == active && "$path" == backend/* ]] || continue
    python3 -I -B scripts/service-contract.py "$path" || errors=1
  done < "$registry"
  return "$errors"
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

if [[ "$action" == test ]]; then
  check_python_contracts || fail 'Python service not ready; no active suite was run.'
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
case "$action" in
  build|run|migrate|smoke) check_python_contracts || fail 'Python service not ready; no runtime tooling was run.' ;;
esac
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
