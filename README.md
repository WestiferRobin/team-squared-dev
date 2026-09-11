# Team Squared Development Box

Canonical workspace for running the complete ACTIVE frontend and product services
in one Docker Compose project. Children remain independently usable.

**Current status: BLOCKED.** The pinned active children do not yet contain the
required implementation/contracts, and parent submodule pins are staged rather
than committed. See [exact prerequisites](docs/READINESS.md). The commands and
frontend composition are prepared, but a working full stack is not certified.

## Active and reference repositories

| Role | Path |
| --- | --- |
| Active frontend | frontend/team-squared-app |
| Active backend | backend/goalstats-user-service |
| Reference template only | backend/team-squared-service |
| Legacy reference only | frontend/RoadToTheFinal |

`config/components.tsv` is the explicit registry. Being a submodule does not make
a repository active. References may be initialized/pinned by setup but are never
built, started, migrated, or tested by normal box operations.

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
