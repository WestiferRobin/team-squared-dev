#!/usr/bin/env bash
# Parent frontend machine preferences. No child credentials or TEST policy live here.
infra_read_file() {
  local file=$1 legacy=$2 line key value seen='|'
  [[ ! -L "$file" && -f "$file" && -O "$file" ]] || { echo 'Unsafe infra configuration file.' >&2; return 1; }
  while IFS= read -r line || [[ -n "$line" ]]; do
    line=${line%$'\r'}
    [[ "$line" =~ ^[[:space:]]*(#.*)?$ ]] && continue
    [[ "$line" == *=* ]] || { echo 'Invalid infra assignment.' >&2; return 1; }
    key=${line%%=*}; value=${line#*=}
    [[ "$seen" != *"|$key|"* ]] || { echo 'Duplicate infra key.' >&2; return 1; }
    seen+="$key|"
    [[ "$value" =~ ^[0-9]{1,5}$ ]] && (( 10#$value >= 1 && 10#$value <= 65535 )) || { echo 'Invalid frontend port.' >&2; return 1; }
    case "$key:$legacy" in
      LOCAL_FRONTEND_PORT:local)
        [[ "$infra_legacy_local" == 0 || "$LOCAL_FRONTEND_PORT" == "$value" ]] || { echo 'Conflicting LOCAL frontend ports.' >&2; return 1; }
        LOCAL_FRONTEND_PORT=$value; infra_local_explicit=1 ;;
      DEV_FRONTEND_PORT:local) DEV_FRONTEND_PORT=$value; infra_dev_explicit=1 ;;
      FRONTEND_PORT:local)
        [[ "$infra_local_explicit" == 0 || "$LOCAL_FRONTEND_PORT" == "$value" ]] || { echo 'Conflicting LOCAL frontend ports.' >&2; return 1; }
        LOCAL_FRONTEND_PORT=$value; infra_legacy_local=1 ;;
      FRONTEND_PORT:dev)
        [[ "$infra_dev_explicit" == 0 || "$DEV_FRONTEND_PORT" == "$value" ]] || { echo 'Conflicting DEV frontend ports; files preserved.' >&2; return 1; }
        DEV_FRONTEND_PORT=$value ;;
      *) echo 'Unsupported infra key.' >&2; return 1 ;;
    esac
  done < "$file"
}

infra_load() {
  LOCAL_FRONTEND_PORT=33000
  DEV_FRONTEND_PORT=33001
  infra_dev_explicit=0
  infra_local_explicit=0
  infra_legacy_local=0
  if [[ -e infra/.env.local || -L infra/.env.local ]]; then infra_read_file infra/.env.local local || return; fi
}

infra_setup() (
  set -e
  umask 077
  mkdir -p infra
  infra_load
  if [[ -e infra/.env.dev || -L infra/.env.dev ]]; then
    infra_read_file infra/.env.dev dev
  elif [[ -f infra/.env.local && "$infra_legacy_local" == 0 ]]; then
    echo 'Preserved infra/.env.local'
    exit 0
  fi
  [[ "$LOCAL_FRONTEND_PORT" != "$DEV_FRONTEND_PORT" ]] || { echo 'Frontend ports must differ.' >&2; exit 1; }
  local state=infra/.config-state temporary
  mkdir -p "$state"
  [[ ! -L "$state" && -O "$state" ]] || { echo 'Unsafe infra internal state.' >&2; exit 1; }
  chmod 700 "$state"
  mkdir "$state/lock" || { echo 'Another infra setup is active; inspect its lock.' >&2; exit 1; }
  trap 'rmdir "$state/lock"' EXIT
  for file in infra/.env.local infra/.env.dev; do
    if [[ -f "$file" ]]; then
      temporary=$(mktemp "$state/backup.XXXXXX")
      cat "$file" > "$temporary"
      chmod 600 "$temporary"
    fi
  done
  temporary=$(mktemp "$state/config.XXXXXX")
  printf 'LOCAL_FRONTEND_PORT=%s\nDEV_FRONTEND_PORT=%s\n' "$LOCAL_FRONTEND_PORT" "$DEV_FRONTEND_PORT" > "$temporary"
  mv "$temporary" infra/.env.local
  if [[ -f infra/.env.dev ]]; then rm infra/.env.dev; fi
  echo 'Private infra/.env.local ready; frontend ports preserved.'
)
