# Validation status

## Implemented checks

- Exact public Make interface; no unit/integration/migration-to-reference aliases.
- Explicit active/reference registry and reference-free Compose definitions.
- Unsupported ENV/project validation before lifecycle actions.
- Existing parent env-file preservation; no runtime started by setup.
- Committed-parent-pin requirement and dirty-child guard before any checkout changes.
- Missing active contracts fail build/run/migrate/smoke before partial startup.
- Missing active Makefiles fail test before any partial delegation.
- Selected Compose files render their known frontend definition under separate projects.

## Blocked end-to-end checks

Current active pins are README-only, and the parent has no committed gitlinks.
Consequently none of the following is certified:

- Successful fresh-clone pinned initialization.
- Complete LOCAL/DEV image builds, migrations, startup, readiness, or logs.
- Active-service tests or aggregate child test counts.
- Real stack smoke, database/cache wiring, browser API integration, or persistence.
- Active app/service standalone workflows at these pins.
- A complete fresh clone without host Node/.NET.

Guard/failure-path tests do not substitute for those checks. The parent scripts
require no host Node/.NET, but no host installation can supply the missing active
service or unpublished app contract. Resolve READINESS.md before certification.

## Executed validation

- `make help` and `bash -n scripts/box.sh`: passed.
- `make setup`: exit 2 as expected; preserved existing configuration and refused
  staged-only submodule metadata before any checkout changes.
- `make build`, `make run`, `make migrate`, `make smoke`, and `make test`, each
  with LOCAL and DEV: exit 2 as expected for missing active contracts. No child
  tests executed; pass/fail/skip counts are unavailable.
- Invalid `ENV=prod`, empty ENV, and a child-style `PROJECT=app-local` were rejected.
- Both Compose configurations parsed; references are absent; only LOCAL has
  application source bind mounts. These are incomplete topology checks.
- A fresh local clone of the actual committed parent, overlaid with the new
  parent files, reproduced the missing committed-pin failure.
- An isolated dirty child in that fixture retained its untracked work and HEAD;
  the existing environment file remained byte-identical after setup failed.
- The fixture was removed. Docker container inventory was unchanged.
- `git diff --check`: passed. All four real submodules remain clean at their
  original indexed SHAs. No staging, commits, pushes, or child edits occurred.

Actual stack logs, stop/recreation persistence, successful pinned initialization,
containerized child suites, and the no-host-toolchain workflow remain untested
because the required active implementations are absent. Validation logs are local,
ignored files under `artifacts/`.
