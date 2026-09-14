# Workspace ready; active runtime pending

The parent provides Git-only setup and safe sync. Workspace readiness means every
child is present at its approved gitlink SHA, with canonical URLs and parent env
files prepared by setup. It does not certify application runtime behavior.

| Role | Component | Pinned SHA | State |
| --- | --- | --- | --- |
| ACTIVE | frontend/goal-stats-app | d7e77e711b4286481a35ffb3a98c8b2892ffe8cf | Published containerized scaffold; standalone manual verification pending. |
| ACTIVE | backend/goalstats-user-service | 70c77c692993fc18e9f484bf22266a15288c0541 | Runtime contract pending; no application/container/test contract. |
| REFERENCE | backend/template-goalstats-service | 07a75b4a8e6e83429c41c51527691870884d76e8 | Certified template baseline; Mac verification passed. Reference only. |
| REFERENCE | frontend/RoadToTheFinal | 4c77197e209292f70ae788e6d4539bb89189e963 | Excluded from active operations. |
| DOCS | docs/goal-stats-wiki | d3992eb4d0c2e2b0b99fee0ab9da14da422c2071 | Project/class documentation; excluded from runtime and dev tests. |

## Workspace scope

`make setup` succeeds on a safe checkout even while runtime is pending. It prepares
the current parent commit, including feature branches or historical commits.
`make sync` requires clean parent master and children at current pins, fast-forwards
to published master, then materializes its exact approved pins. Neither requires
Docker. This adoption advances only the template to the exact approved commit
above. User-service, app, wiki, and RoadToTheFinal pins are preserved.
No child source, application feature, or runtime topology changes here.
See [validation](VALIDATION.md) for exercised cases and [development](DEVELOPMENT.md)
for safe child development and parent pin review.

## Runtime boundary

GOALSTATS-USER-SERVICE REMAINS ACTIVE BUT RUNTIME-PENDING

FULL-STACK RUNTIME VERIFICATION DEFERRED UNTIL GOALSTATS-USER-SERVICE IS IMPLEMENTED

The registry retains pending migration/readiness/health/smoke values for the user
service. Neither Compose file defines its runtime contract. The app now contains
its Dockerfile and Makefile, but standalone app manual verification remains pending.
Complete-stack build/run/migrate/smoke refuse partial
operations, and `make test` requires every active child's normal test interface.
References and documentation cannot substitute for an active service.

No full-stack runtime, migration, connectivity, smoke, or active test certification
is claimed. Workspace success with these runtime blockers is intentional.

## User-service bootstrap boundary

Source: `backend/template-goalstats-service` at
`07a75b4a8e6e83429c41c51527691870884d76e8`. Its approved certification includes
Mac verification; this parent task verifies the selected contents without rerunning
standalone template certification.

Destination: `backend/goalstats-user-service` at placeholder commit
`70c77c692993fc18e9f484bf22266a15288c0541`. The workspace provides both repositories
for a later tracked template export into user-service master. No export,
branch creation, or product implementation is performed by pin adoption.

## Scaffold tooling boundary

The parent now provides `make scaffold-service SERVICE=<approved-service> DOMAIN=<approved-domain>` and
`DRY_RUN=true` for an explicitly approved placeholder on clean master or safely detached at its approved master pin.
This is deterministic identity transformation using Python 3.9+, independent of
Docker/network after setup. DOMAIN is required and registry-approved.
It does not implement or certify the destination service. Actual-template disposable
certification passed, including exact payload and Git preservation checks. A successful
real dry run is still required before using it on the real user service. The real
child needs matching existing master/origin/master refs; scaffold previews attachment
without writes and attaches only during installation. Any dirty parent work must be
resolved before preview. TODO.md is already tracked and must remain preserved.
Only the certified template pin is adopted. The real user service remains untouched
and runtime-pending. The disposable generated User skeleton passed build, EF,
553 tests (260 unit / 293 integration) and LOCAL/DEV runtime checks. This does not certify the real placeholder
or the active parent composition. Item/Action remain examples; no business-domain
generation occurs.
