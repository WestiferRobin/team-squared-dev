# Readiness: structure synchronized, runtime pending

The parent records five submodule gitlinks and canonical repository URLs.
The template/app paths were reconciled without upgrading their commits. The
user-service and RoadToTheFinal pins are also preserved. The wiki pin deliberately
uses its published default-branch HEAD at synchronization time.

| Role | Component | Pinned SHA | State |
| --- | --- | --- | --- |
| ACTIVE | frontend/goal-stats-app | e01a3475b92fe55808006bf91a470fe97eb2b4ef | Preserved pin; no Dockerfile or Makefile. |
| ACTIVE | backend/goalstats-user-service | 70c77c692993fc18e9f484bf22266a15288c0541 | Runtime contract pending; no application/container/test contract. |
| REFERENCE | backend/template-goalstats-service | 47ed7cb27c1a00bf6a4b784276f86182ca3c6d05 | Never substitute for the active backend. |
| REFERENCE | frontend/RoadToTheFinal | 4c77197e209292f70ae788e6d4539bb89189e963 | Excluded from active operations. |
| DOCS | docs/goal-stats-wiki | d3992eb4d0c2e2b0b99fee0ab9da14da422c2071 | Project/class documentation; excluded from runtime and dev tests. |

## Structural scope

The synchronization commit records `.gitmodules` and all five gitlinks together.
No existing child pin is upgraded and no child application source is changed.
Next: **RUN PROMPT 2 FRESH-CLONE SUBMODULE VERIFICATION**.
A fresh recursive clone should resolve these paths at their recorded pins; that
structural readiness does not imply runtime readiness.

## Runtime boundary

GOALSTATS-USER-SERVICE REMAINS ACTIVE BUT RUNTIME-PENDING

FULL-STACK RUNTIME VERIFICATION DEFERRED UNTIL GOALSTATS-USER-SERVICE IS IMPLEMENTED

The registry deliberately retains pending migration/readiness/health/smoke values
for the user-service. Neither Compose file defines its runtime contract. Both
frontend contexts use `frontend/goal-stats-app`, but the preserved app pin also
lacks its Dockerfile/Makefile. Updating child versions is separate future work.

Complete-stack build/run/migrate/smoke remain guarded against partial startup.
Dev `make test` requires every active child's Makefile and remains blocked at these
pins. `make setup` can initialize committed submodules and still fail the runtime
contract checks. Missing runtime contracts are expected and do not invalidate
repository/submodule structural synchronization.

No backend implementation, migrations, endpoints, runtime tests, Compose backend
service, or fabricated health contract is part of this synchronization. References
and docs cannot stand in for missing active components. No full-stack runtime,
connectivity, smoke, or test certification is claimed.
