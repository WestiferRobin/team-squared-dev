# Team Squared canonical workspace

Clone once, prepare the workspace, develop in independent child repositories, and
sync approved integration pins. The parent owns gitlinks and full-stack composition.

**Workspace setup is independent of runtime readiness.** Setup/sync need no Docker.
The certified template and published containerized app scaffold are pinned for
development. Template Mac verification passed; standalone app manual verification
remains pending. The active user service remains runtime-pending, so full-stack
commands remain blocked until its contract is complete. See [readiness](docs/READINESS.md).

## First use and daily sync

On macOS, install Git (with submodule support), GNU Make 3.81+, Bash 3.2+, OpenSSH,
and ordinary shell utilities (`cat`, `dirname`, `mkdir`, `mv`, `rm`, plus Git's normal
system tools). Apple's command-line developer tools supply Git and GNU Make.
Configure your SSH key and GitHub repository access for the URLs in `.gitmodules`.
Git reports authentication/download errors when initialization needs the network.
No host Node/.NET or Docker is required for workspace preparation.

```bash
git clone git@github.com:WestiferRobin/team-squared-dev.git
cd team-squared-dev
make setup
# Open this root directory in your editor.
# Daily, on clean parent master with children at approved pins:
make sync
```

Setup prepares the **current** parent commit, initializes all five children at exact
pins, and creates only missing parent LOCAL/DEV env files. It never pulls the parent.
Sync fast-forwards parent master and adopts only its approved child pins; it never
changes env files. Both preserve developer work by refusing dirty or off-pin state.
Owned repositories use master only; RoadToTheFinal retains its main exception.
Detached children at pins are normal. Scaffold attaches its safe destination to
existing master automatically during installation; preview does not attach.

## Bootstrap an approved service

`make scaffold-service SERVICE=goalstats-user-service DOMAIN=User DRY_RUN=true`
previews transforming identity in exact tracked files from the parent-pinned reference template into an approved
placeholder. Omit `DRY_RUN=true` to install after a successful preview. The destination
must be clean on master or safely detached, with HEAD, local master, origin/master,
parent pin and approved placeholder SHA equal. Missing/mismatched refs or another
branch refuse; no branch is created. Scaffold remains offline after setup. Parent
changes, including untracked TODO.md, block the command; unrelated child work does
not. Python 3.9+ is required. No Docker or network is required after setup.

Scaffolding preserves the destination Git repository and leaves unstaged child
changes. It maps GoalStats.Template.* and TemplateDbContext to GoalStats.<DOMAIN>.* and
<DOMAIN>DbContext. Item/Action remain examples; no business-domain generation or
runtime certification occurs. DOMAIN is required and must match registry approval. A second
invocation refuses. See the [scaffold contract and beginner workflow](docs/DEVELOPMENT.md#service-scaffolding)
before use. The generated User skeleton passed disposable build, EF, test and
LOCAL/DEV runtime certification. It still contains example Item/Action behavior,
not real User functionality. Real-service use requires resolving local safety
blockers and reviewing a successful preview in a separate explicit task.

## Repositories

| Role | Path |
| --- | --- |
| ACTIVE frontend | frontend/goal-stats-app |
| ACTIVE, runtime-pending | backend/goalstats-user-service |
| REFERENCE template | backend/template-goalstats-service |
| REFERENCE legacy frontend | frontend/RoadToTheFinal |
| DOCS project/class documentation | docs/goal-stats-wiki |

`config/components.tsv` defines runtime roles. References/docs are synchronized,
but excluded from normal build/run/migrate/test/smoke and Compose.

## Public commands

```text
make help
make setup
make sync
make scaffold-service SERVICE=<approved-service> DOMAIN=<approved-domain> [DRY_RUN=true]
make build [ENV=local|dev]
make run [ENV=local|dev]
make stop [ENV=local|dev]
make logs [ENV=local|dev]
make migrate [ENV=local|dev]
make test
make smoke [ENV=local|dev]
```

ENV defaults to local. LOCAL means developer containers (frontend port 33000); DEV
means built verification containers (33001), not remote deployment. Container
workflows require Docker with Compose v2 and complete active contracts. Migrations
are explicit; stop preserves volumes and affects only the selected box project.
Normal `make test` delegates all ACTIVE child normal suites with app E2E disabled,
and fails before delegation if an active test interface is missing.

Windows is **not certified**. WSL with Git/Make/Bash and Docker Desktop integration
is the preferred candidate. Git Bash plus GNU Make remains possible after testing.
Native PowerShell is not the primary supported script interface.

[Development](docs/DEVELOPMENT.md) explains child branches, manual parent integration,
ignored files, safety refusals, interrupted sync, and configuration.
[Validation](docs/VALIDATION.md) records workspace checks and runtime limitations.
