#!/usr/bin/env bash
# Python policy v2; no shell expansion of SERVICE/DOMAIN values.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -I -B scripts/scaffold-service.py "$@"
