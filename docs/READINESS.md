# Workspace, scaffold and runtime readiness

The workspace adopts canonical Flask template
`720260c7d8d5096bddbd0cc6d6f90f9f311d809a` with compatible flat-src identity tooling and policy-v2 failure evidence.
The template gitlink and compatible parent tooling are released together.

| Component | Intended pin | State |
| --- | --- | --- |
| Template (reference) | 720260c7d8d5096bddbd0cc6d6f90f9f311d809a | Canonical Python 3.12 Flask template; disposable generated runtime certified |
| User (active) | 70c77c692993fc18e9f484bf22266a15288c0541 | Placeholder commit; real working tree dirty and preserved |
| App (active) | d7e77e711b4286481a35ffb3a98c8b2892ffe8cf | Unchanged; standalone manual verification not claimed |
| Wiki (docs) | d3992eb4d0c2e2b0b99fee0ab9da14da422c2071 | Unchanged |
| RoadToTheFinal (reference) | 4c77197e209292f70ae788e6d4539bb89189e963 | Unchanged; main exception |

Setup materializes committed pins; sync fast-forwards approved parent master and
materializes its exact pins. Both remain Git-only and preserve dirty/off-pin work.
The working-tree implementation cannot be used to bypass committed-source/clean-parent
checks. Use disposable candidate commits during independent certification.

## Static Python state and runtime boundary

`service-contract.py` reports PLACEHOLDER, SCAFFOLDED, INCOMPLETE or INVALID without
executing child code. Flat `src/main.py`/`src/composition.py` and `main:create_app()`
are required; old service-package or mixed layouts refuse. Placeholder, partial
installation, mixed legacy/Python, residual
identity and missing anchors block delegation. SCAFFOLDED means structural readiness,
not certified runtime behavior. Parent test validates all backend contracts before any
active suite is invoked. Full-stack commands additionally require complete parent
registry/Compose contracts; frontend-only startup is never substituted.

User registry migration/readiness/health/smoke fields remain pending; parent Compose
remains frontend-only. No full-stack runtime readiness is claimed. Template/reference
and docs components remain excluded from active operations.

## Remaining sequence

Prompt 2 certifies disposable generation and full generated runtime and releases
parent tooling and pin adoption together. Prompt 3 separately preserves and
reconciles real User, generates/certifies/publishes its Item/Action baseline, then
updates the parent User pin. Actual User business logic and parent runtime integration
are later work. Existing TODO changes and User README/deleted .gitignore remain unchanged.

Historical .NET certification and policy-1 recovery evidence are archival only; see
[validation history](VALIDATION.md). The Python scaffold never consumes or deletes it.
