# Workspace ready; active runtime pending

The parent provides Git-only setup and safe sync. Workspace readiness means every
child is present at its approved gitlink SHA, with canonical URLs and parent env
files prepared by setup. It does not certify application runtime behavior.

| Role | Component | Pinned SHA | State |
| --- | --- | --- | --- |
| ACTIVE | frontend/goal-stats-app | d7e77e711b4286481a35ffb3a98c8b2892ffe8cf | Published containerized scaffold; standalone manual verification pending. |
| ACTIVE | backend/goalstats-user-service | 70c77c692993fc18e9f484bf22266a15288c0541 | Runtime contract pending; no application/container/test contract. |
| REFERENCE | backend/template-goalstats-service | e89164842ca2c0f2954919a38da3ed4924d5f3ac | Certified template baseline; Mac verification passed. Reference only. |
| REFERENCE | frontend/RoadToTheFinal | 4c77197e209292f70ae788e6d4539bb89189e963 | Excluded from active operations. |
| DOCS | docs/goal-stats-wiki | d3992eb4d0c2e2b0b99fee0ab9da14da422c2071 | Project/class documentation; excluded from runtime and dev tests. |

## Workspace scope

`make setup` succeeds on a safe checkout even while runtime is pending. It prepares
the current parent commit, including feature branches or historical commits.
`make sync` requires clean parent master and children at current pins, fast-forwards
to published master, then materializes its exact approved pins. Neither requires
Docker. Deliberate integration advances only the template and app pins to the exact
approved commits above. User-service, wiki, and RoadToTheFinal pins are preserved.
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
`e89164842ca2c0f2954919a38da3ed4924d5f3ac`. Its approved certification includes
Mac verification; this parent task verifies the selected contents without rerunning
standalone template certification.

Destination: `backend/goalstats-user-service` at placeholder commit
`70c77c692993fc18e9f484bf22266a15288c0541`. The workspace provides both repositories
for a later tracked template export into a user-service feature branch. No export,
branch creation, or product implementation is performed by pin adoption.
