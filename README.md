# Team Squared Development Box

Canonical workspace for running the complete ACTIVE frontend and product services
in one Docker Compose project. Children remain independently usable.

**Repository structure: synchronized. Runtime: BLOCKED.** The parent records five
submodule pins at canonical paths. The four existing child versions are preserved;
this synchronization adds only the wiki pin. This does not certify a working stack.
See [readiness boundaries](docs/READINESS.md).

## Active, reference, and documentation repositories

| Role | Path |
| --- | --- |
| ACTIVE frontend | frontend/goal-stats-app |
| ACTIVE — runtime contract pending | backend/goalstats-user-service |
| REFERENCE template | backend/template-goalstats-service |
| REFERENCE legacy frontend | frontend/RoadToTheFinal |
| DOCS project/class documentation | docs/goal-stats-wiki |

`config/components.tsv` is the explicit registry. Being a submodule does not make
a repository active. References and docs are initialized/pinned by the dev repo
and available to developers, but never built, run, migrated, tested, or smoked by
normal box operations. They are not included in Compose.

For structure-only verification, clone recursively and inspect `git submodule
status`. Next: **Prompt 2 fresh-clone submodule verification**. Existing checkouts
must follow the [safe synchronization workflow](docs/DEVELOPMENT.md#existing-checkouts).
`make setup` also checks runtime contracts and may intentionally remain blocked.

## Intended first-use workflow

After the prerequisites in READINESS.md are resolved and committed:

```bash
git clone --recurse-submodules git@github.com:WestiferRobin/team-squared-dev.git
cd team-squared-dev
make setup
make migrate
make run
make logs
make test
make smoke
make stop
```

These commands require Git, Docker Compose v2+, GNU Make 3.81+, and Bash/core OS
utilities on macOS/Linux. The orchestration does not invoke host Node or .NET.
Missing application implementations cannot be repaired by installing host tools.

## Environment meaning

- LOCAL: the complete active stack in developer containers, with child-supported
  source mounts/watch/HMR. Default ENV; box frontend port 33000.
- DEV: the complete stack built from the checked-out active source, with no
  source-mounted runtimes. Box frontend port 33001; not remote deployment.

```bash
make migrate ENV=dev
make run ENV=dev
make logs ENV=dev
make smoke ENV=dev
make stop ENV=dev
```

Build/run/smoke refuse incomplete active contracts. Migrations stay explicit.
Stop preserves volumes and affects only the selected box project.

## Command scope

```text
make help
make setup
make build [ENV=local|dev]
make run [ENV=local|dev]
make stop [ENV=local|dev]
make logs [ENV=local|dev]
make migrate [ENV=local|dev]
make test
make smoke [ENV=local|dev]
```

No dev unit/integration/certify aliases. Normal tests delegate to all active child
Makefiles with app E2E disabled. Detailed test layers remain child-owned.

For app-only or service-only work, enter that active child and use its Makefile
once its published interface is available. The reference template is not a product
service. Beginners and experienced engineers share the same normal commands.

[Development details](docs/DEVELOPMENT.md) cover ownership, safe pins, configuration,
raw tooling, readiness, and adding a service. [Validation](docs/VALIDATION.md)
distinguishes implemented guards from currently blocked runtime checks.
