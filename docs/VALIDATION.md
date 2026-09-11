# Structural synchronization validation

This validation covers the parent repository structure only. The synchronization
commit records five canonical `.gitmodules` entries and five matching gitlinks.
The four pre-existing pins are preserved; only the wiki receives a new pin.

## Checks completed

- `bash -n scripts/box.sh` and `make help` pass; all five components are listed.
- Both LOCAL/DEV Compose files parse without starting containers. Their only
  service is the frontend, with the renamed build context; LOCAL mounts use the
  renamed app path. Missing Dockerfiles at preserved pins are runtime blockers,
  not configuration syntax failures.
- Registry paths match the five submodule paths, with two active, two reference,
  and one docs entry. User-service runtime fields remain pending.
- Active-only selection is preserved for build/run/migrate/test/smoke. Reference
  and docs components have no Compose definitions and are excluded from those
  operations. Existing incomplete-stack and dirty-child guards remain intact.
- All five children initialize from canonical SSH URLs at the intended pins.
  Their HEADs equal the parent index pins, origins match `.gitmodules`, and
  worktrees are clean, with detached HEADs. Published remote history contains
  every selected commit.
- Parent documentation links and component paths resolve. Parent-owned text has
  zero stale repository names. `git diff --check` passes.

## Child-owned stale references

The recursive text scan also examines initialized children. Four stale references
remain inside preserved child commits: `frontend/goal-stats-app/README.md` lines
9 and 16, and `docs/goal-stats-wiki/README.md` lines 7 and 8. These are stale child
repository documentation, not intentional current role mappings. They are outside
this parent-only change and are not edited or used to infer runtime components.
The parent README and registry define the current active/reference/docs roles.
No child pin was advanced to remove these references.

## Deferred verification

FRESH RECURSIVE CLONE STRUCTURE READY

Initialization and metadata checks establish structural readiness; a separate
fresh recursive clone of the published parent is the next verification step:
**RUN PROMPT 2 FRESH-CLONE SUBMODULE VERIFICATION**.

GOALSTATS-USER-SERVICE REMAINS ACTIVE BUT RUNTIME-PENDING

FULL-STACK RUNTIME VERIFICATION DEFERRED UNTIL GOALSTATS-USER-SERVICE IS IMPLEMENTED

No full-stack run, backend migration/health check, frontend-to-backend connectivity,
dev smoke, or dev test was executed or certified. The preserved app pin also lacks
its Dockerfile and Makefile. `make setup` includes runtime contract checks and may
remain intentionally blocked after successful pinned initialization. No child
source, env files, or generated artifacts are part of this synchronization change.
