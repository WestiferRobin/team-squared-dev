# Development-box contract

## Ownership

Children own Dockerfiles, development/build/runtime commands, migration logic, and
normal tests. The box owns the active registry, Compose project/network, host ports,
combined configuration, lifecycle, aggregate logs, and stack-level smoke.

No child standalone make run is called by the box. Each ENV has one project:
team-squared-local or team-squared-dev. Optional PROJECT overrides must begin with
the corresponding name plus a dash. Stop/logs can still operate on that owned
project when a child contract becomes unavailable, so diagnosis/cleanup stays possible.

## Canonical workspace and daily synchronization

Clone the parent once, then edit the independent repositories under backend/,
frontend/, and docs/. The parent gitlink is an **approved integration commit**;
a child branch holds active development history. Dirty child content is unfinished
work. A published child commit is a candidate for later parent integration, not an
automatic pin upgrade.

```bash
git clone git@github.com:WestiferRobin/team-squared-dev.git
cd team-squared-dev
make setup
# Open this root directory in your editor.
# Later, with parent master and all repositories clean and at approved pins:
make sync
```

`setup` prepares the currently checked-out parent, including a feature branch or
historical detached commit. It never fetches or moves the parent. `sync` requires
parent `master`, fetches `origin/master` without submodule recursion, refuses local
ahead/divergent history, and fast-forwards only. It then uses the updated parent's
metadata and helper to materialize exact approved pins. Neither command needs
Docker, calls Compose, runs child setup/tests, or validates runtime contracts.
Missing runtime contracts do not prevent workspace readiness.

Both commands inspect parent and every initialized child, recursively, before
checkout movement. Staged/unstaged tracked changes, nonignored untracked files,
conflicts, in-progress merge/rebase/cherry-pick/revert/bisect operations, edited
metadata/gitlinks, and clean off-pin children cause refusal. Missing child paths
must be empty, and symlinks cannot occupy them. Work is never automatically stashed,
reset, cleaned, staged, or discarded. Any untracked parent work such as `TODO.md` is
subject to the same policy and is preserved; it is not an exception.

Ignored files are excluded according to Git's normal ignore rules: this parent's
`.DS_Store`, `artifacts/`, `infra/.env.local`, and `infra/.env.dev`, plus effective
repository-local/global excludes and each child's ignore rules. They are harmless
only if incoming tracked content will not replace them. Sync checks such collisions
before the relevant checkout. Do not run concurrent Git edits during setup/sync.

Canonical URLs come from committed `.gitmodules`; setup/sync synchronize them at
each nesting level. Children are initialized at gitlink SHAs, never remote branch
heads. Already attached child branches at the required SHA stay attached. When sync
adopts another approved SHA, detached HEAD is normal; existing branch refs remain.
Clean off-pin checkouts may contain unpublished work, so preserve their commits on
a branch and deliberately select the current approved pin before synchronization.

Incoming parent removal/rename of an occupied submodule path requires manual
reconciliation before parent movement. Ordinary new submodules can initialize
normally. Git sync is not atomic: if the parent advances and a child download fails,
repositories are preserved and a journal under the parent's Git directory records
the target and exact prior child SHAs. Resolve the issue and retry `make sync`.
The retry completes that recorded target before a later sync fetches newer master.
It still refuses dirty state or unrelated off-pin commits; no rollback is fabricated.
Do not delete the journal to bypass safety. `setup` asks you to finish an interrupted
sync first. Changes to repositories outside that recorded transition require manual
review. SSH credentials and repository access are checked by Git when it needs to
fetch; an already complete offline setup does not probe GitHub unnecessarily.

## Developing and publishing a child

```bash
cd backend/goalstats-user-service
# Service scaffold has already attached this destination to master.
# edit/test using the child's available tools
# review changes before staging
git add .
git commit -m "Implement architecture prototype"
git push origin master
```

The same independent-repository workflow applies to `frontend/goal-stats-app` and
`docs/goal-stats-wiki`: enter the clean child, deliberately select its master for development, edit/test, and
commit/publish there. App standalone manual runtime verification remains pending.
Wiki edits do not change the parent pin until an approved wiki commit is integrated.

For the upcoming user-service bootstrap, the tracked template source is
`backend/template-goalstats-service` at `720260c7d8d5096bddbd0cc6d6f90f9f311d809a`;
the destination remains `backend/goalstats-user-service` at
`70c77c692993fc18e9f484bf22266a15288c0541`. Scaffold previews safe attachment and attaches the destination to master only on
installation. No manual child branch command is needed. Pin adoption performs neither.
The template and RoadToTheFinal remain references, excluded from active composition.

Parent status may show a modified child because its content is dirty or HEAD differs
from the approved gitlink. Publishing the child does not update the parent pin.
After child review, parent integration is separate and deliberate:

1. Verify the selected child commit is published and approved.
2. Select that commit in the child, then return to the parent.
3. Stage only its gitlink: `git add backend/goalstats-user-service`.
4. Review `git diff --cached --submodule=log`.
5. Commit and publish the parent pin update through normal review.

There is no automated upgrade command. Use a separate integration checkout when
needed; setup/sync intentionally refuse an off-pin development checkout.

## Service scaffolding

The canonical source is the parent's committed template gitlink, adopted as
`720260c7d8d5096bddbd0cc6d6f90f9f311d809a`. Never select latest remote master or
`legacy/dotnet`. Source and destination must be initialized, clean, on approved
pins, and have canonical origins from committed `.gitmodules`. The exactly
three-column `config/scaffolds.tsv` approves SERVICE, placeholder SHA and DOMAIN.
Only registered active backend destinations are eligible; template stays a reference.

```sh
make scaffold-service SERVICE=goalstats-user-service DOMAIN=User DRY_RUN=true
make scaffold-service SERVICE=goalstats-user-service DOMAIN=User
```

Use Python 3.12. Parent must be clean master, including no staged gitlinks; existing
TODO changes are not ignored or moved. Unrelated child work is not repaired. The
child must contain only its approved regular 100644 README.md and .gitignore,
with exact bytes and no untracked/ignored files or extra directories. Those two
placeholder files are fully replaced by generated canonical versions. Old ignore
rules are not merged. Existing destination HEAD, master, origin/master, registry
SHA and parent pin must agree. Another worktree owning master refuses.

### Flat-src identity policy (policy-v2 evidence)

SERVICE grammar is `goalstats-<lowercase-alphanumeric-segments>-service`.
DOMAIN is 2–15 ASCII PascalCase characters, excluding Template and acronyms, and
must match its registry approval. SERVICE is parsed once; multiword segments remain
separate (`player-stats` → logger `goalstats_player_stats`, runtime `goalstats-player-stats-py`).
Duplicate domains/derived identities and overlong database names refuse.

| Source | User output |
| --- | --- |
| `template-goalstats-service` | `goalstats-user-service` |
| Logger label `goalstats_template` | `goalstats_user` (not a Python package) |
| `GoalStats Template API` | `GoalStats User API` |
| `goalstats-template-py` | `goalstats-user-py` |
| `goalstats_template_py_local` / `_dev` | `goalstats_user_py_local` / `_dev` |
| CI concurrency `goalstats-template-${{` | `goalstats-user-${{` (CI file and its documented anchor) |

PATH TRANSFORMATIONS: NONE. PYTHON PACKAGE DIRECTORY TRANSFORMATION: NO.
Every canonical path remains unchanged, including `src/main.py`, `src/composition.py`,
`src/enums/`, `src/exceptions/`, `src/settings/`, `src/models/`, `src/schemas/`,
`src/infra/`, `src/services/` and `src/routers/`. The factory stays `main:create_app()`;
imports and coverage stay flat. No `src/goalstats_user/` directory is created.
Runtime/tooling images, Compose project constructors, cache prefixes, smoke guards,
disposable ownership regexes, tool containers and CI identities change together.
Generated cleanup accepts only its own test/cert namespace. Internal
app/runner/postgres/redis services remain generic.

The committed baseline and certified IDE delta's TRANSFORM inventory is path-scoped in
`scripts/scaffold-transform.py:IDENTITY_PATHS`:

| Identity | Exact permitted paths |
| --- | --- |
| Database prefix `goalstats_template_py` | `.env.example`; `docker/compose.local.yml`; `docker/compose.dev.yml`; `docs/service/development.md`; `docs/standard/template.md`; `scripts/host_development.py`; `scripts/smoke/runtime.py`; `scripts/validation/certify_workflows.py`; `tests/fixtures/smoke.py` |
| Logger label `goalstats_template` | `src/main.py`; `docs/standard/template.md` |
| Runtime `goalstats-template-py` | `.env.example`; `docker/compose.local.yml`; `docker/compose.dev.yml`; `docker/compose.test.yml`; `docs/service/development.md`; `docs/standard/template.md`; `scripts/host_development.py`; `scripts/smoke/runtime.py`; `scripts/test_ownership.py`; `scripts/tests/test_host_development.py`; `scripts/tests/test_workflow.py`; `scripts/validation/certify_workflows.py`; `scripts/workflow.py`; `src/settings/base.py`; `tests/fixtures/smoke.py`; `tests/unit/schemas/test_domain.py` |
| API `GoalStats Template API` | `src/main.py`; `docs/standard/template.md` |
| Repository `template-goalstats-service` | `docs/standard/template.md` |
| CI `goalstats-template-${{` | `.github/workflows/ci.yml`; `docs/standard/template.md` |

Database substitutions cover `_local`, `_dev` and the quoted `_` runtime constructor.
Identifiers must have valid boundaries. Any listed identity at an unapproved path,
embedded identity, unexpected database suffix, service-package path/import, or
unrecognized template-specific residual is INVALID. Generic `template`, `GoalStats`
and `User` words are PRESERVE, not replacement tokens. Logger labels are service
identities even though they share the spelling of the former package.

ITEM/ACTION TRANSFORMATION: NO. Keep Item/Action models, enums, business routes,
contracts and behavior. Flat imports and business identifiers do not change.
Alembic revision `b7f42e9c1a60` and its entire migration file remain byte-identical;
Alembic env.py imports already use the flat architecture and remain unchanged.
requirements.txt is byte-identical and remains the sole
dependency file. Makefile/make modules, mypy/pytest/Ruff configuration remain identical.
No formatting, source execution, migration generation, provider calls or dependency
installation occurs during transformation. Generic framework prose and Flask extension
keys remain unchanged. TEST DB stays `goalstats_test_runtime`, within independent
providers/networks; UUID fixture prefixes remain generic and scoped.

The pure transformer maps every committed blob's path, bytes and mode. It rejects
missing Python anchors, reserved residual identities, unexpected embeddings, unsafe
paths, case/file-directory collisions, links, opaque identity data, invalid UTF-8 text,
NUL text and generated artifacts. UTF-8 BOM/newline/final-newline bytes and executable
modes are preserved. requirements and migration exclusions are checked explicitly.
Committed blobs are read directly, avoiding archive export attributes.

### Preview, installation and failure

Dry run is in memory: no temporary export, lock creation, journal, bytecode, optional
index refresh or branch attachment. It prints SERVICE, DOMAIN, source/destination SHAs,
`SOURCE_LAYOUT=flat-src`, `FACTORY_TARGET=main:create_app()`,
`PYTHON_PACKAGE_DIRECTORY_TRANSFORMATION=NO`, `PATH_TRANSFORMATIONS=0`,
runtime/API/database/cache identities, dynamic file count and branch
action, with `ITEM_ACTION_TRANSFORMATION=NO` and `WRITES=NONE`. An existing operation
or lock refuses. Preview is not a reservation; actual operation revalidates.

Actual installation takes an exclusive `team-squared-scaffold-v2.lock` under parent
Git administration. It prepares/verifies output, safely attaches existing master if
needed, records snapshots/backups/manifest, installs descriptor-relative checked files
with atomic per-file replacement, and verifies the complete destination and Git state.
The entire tree is not atomic. Child HEAD, refs, index, origin, .git pointer and parent
User gitlink stay unchanged; generated files are unstaged. Only safe attachment changes
symbolic HEAD and its normal same-commit reflog entry; the narrowly documented absent
VS Code merge-base metadata addition is allowed. No branch creation, reset or stash.

A failure retains `team-squared-scaffold-incomplete/` containing policy 2, source and
parent SHAs, mapping, hashes/modes, original placeholders, Git snapshots, prepared
output, progress events and the failed phase. Preparation failures do not alter child
payload. During installation partial output is preserved; retries refuse. Evidence may
contain private Git configuration; it is stored privately. Do not remove markers or
blindly rerun. There is no automatic rollback or old-policy recovery interface. Historical
policy-1 markers are refused without interpretation or deletion. Manual reconciliation
is a separate reviewed action. SIGKILL or host loss can leave the lock; inspect ownership
before deliberate removal. No global cleanup commands are used.

### Certification boundary

Parent fixture tests validate safety and exact transformation without Docker. Full
post-scaffold certification must use a fresh disposable generated service: clean
Python 3.12 install via requirements.txt, import/factory checks, Ruff/format/mypy,
normalized suite discovery equality, unit/integration/full/coverage, migrations,
LOCAL/DEV/TEST, OpenAPI with only title normalized, built smoke, and cleanup/failure
checks. Do not impose historical test counts. No real User is used for tooling tests.

Standalone default ports remain 5100/5200; simultaneous services need distinct private
APP_PORT values. Disposable certification uses allocated ports. Service identity alone
does not make host ports unique.

The beginner sequence is setup, preview, install, review child status including untracked
files, then separate runtime certification. Child publication comes before an intentional
parent User gitlink update. Scaffold never stages, commits or pushes.

## Configuration and ports

The parent owns infra/.env.local and infra/.env.dev, created only when absent from
corresponding .example files. The existing .env.dev placeholder is preserved.
The current parser supports FRONTEND_PORT only, treating files as data rather than
executing shell content. Selected file/defaults take precedence over inherited exports.
No child dotenv files are copied, sourced, or overwritten.

| Mode | Frontend host port | Container port | Compose project |
| --- | --- | --- | --- |
| LOCAL | 33000 | 3000 | team-squared-local |
| DEV | 33001 | 3000 | team-squared-dev |

Backend/database/cache ports and credentials remain unassigned until the real
active service contract is known. Add only required settings and disposable example
values when that contract is implemented. Real secrets must not enter committed
examples or browser-visible frontend configuration. The current app has no API URL
variable or browser API client; inventing one here would not wire a feature.

## Compose, migrations, and readiness

Both Compose files reuse the active app's Dockerfile targets. LOCAL uses src/public
mounts and a project-owned Next cache; DEV uses the runtime target without mounts.
Neither file currently defines the unimplemented active backend. Make checks every
active registry entry and refuses partial build/run/migrate/smoke operations.

Register future migration tooling as a Compose service in the tooling profile,
using the child's actual tooling target/command. It must depend on the selected
box database being healthy and receive the box's internal database connection.
The registry names that migration service; make migrate runs it with Compose
run --rm --build in this project. No EF command or database endpoint is guessed or
duplicated in the box script. Mark migrations none only when the service truly has
no migration responsibility; pending deliberately blocks execution.

Run builds/starts the default active services with a bounded Compose readiness
wait, then runs scripts/probe.cjs through the frontend container's Node runtime.
Per-component readiness URLs/bodies come from the registry. Failure identifies
failed checks and leaves the box available for logs; no implicit migration occurs.
After readiness the frontend URL is printed. Backend host URLs must be added when
its actual port/API contract is implemented; no fictitious API URL is printed now.

Normal stop uses Compose down without volume deletion. It never calls child stop,
removes another project's data, or kills host processes. Logs follow the aggregate
project output; interrupting log following does not stop the stack.

## Test and smoke boundaries

Make test first verifies every ACTIVE child has a Makefile, then runs normal child
tests serially. It clears parent Make/environment overrides and explicitly supplies
E2E=false. A failure stops later delegation and remains nonzero; GNU Make retains its
usual outer recipe-error status rather than preserving a runner's numeric code verbatim.
Testing does not depend on a running box or complete runtime Compose definitions.
References and docs are excluded, and no successful partial test suite is reported.

Make smoke checks the already-running box: frontend response, registered service
readiness and health, and a representative non-destructive GET. Requests originate
inside the frontend container and use Compose DNS, verifying container-to-service
connectivity without host Node. These transport checks cannot certify browser API
integration that the app has not implemented. Child unit/provider suites are not
repeated by smoke. The probe is prepared but unverified against a real active stack.

App-owned E2E remains in the app repository. Future tests spanning multiple deployed
components belong here; no broad browser/full-stack suite is invented now.

## Adding an active service

1. Implement and publish its standalone container/Make contract in its own repository.
2. Add and deliberately pin its submodule; register active in config/components.tsv.
3. Add LOCAL/DEV Compose definitions pointing to its child-owned Dockerfile targets.
4. Configure dependencies, network DNS, env values, unique host ports, and volumes.
5. Register migration tooling if applicable, scoped to this box's database.
6. Supply readiness/health/representative GET contracts; normal tests delegate via
   that child's Makefile automatically once it is registered.
7. Update URLs/docs and validate LOCAL/DEV, persistence, smoke, and child independence.

Do not infer active components by enumerating submodules or activate a template to
satisfy a missing product service.

## Team workflow

Beginners use this Makefile for the whole box, the app Makefile for frontend-only
work, and the ACTIVE service Makefile for backend-only work. Mid/senior engineers
use the same interface, with raw Compose/Docker or child tooling for focused diagnosis,
IDE integration, and schema authoring. There is no separate privileged workflow.

Raw Compose can bypass the completeness guards and currently starts only a partial
frontend definition; it is not evidence of a functioning full-stack box. Do not use
it as a workaround for the prerequisites in READINESS.md.

## Existing checkouts

Use `make sync` on clean parent master with children at current pins. Resolve its
reported safety refusal deliberately; do not force checkout or delete old paths to
bypass it. `make setup` initializes missing pins and env files for the current parent
checkout without updating master. Inspect pins with `git submodule status --recursive`
or `bash scripts/workspace.sh status`.

The wiki is documentation; the template and RoadToTheFinal are references. All are
pinned and synchronized but excluded from normal runtime and active tests.

### Branch policy and historical recovery

Owned repositories develop on master; RoadToTheFinal retains main. Setup/sync may
materialize detached approved child pins. Actual Python scaffold attaches only an
existing matching master, never a new branch. Historical .NET recovery certifications
are retained in VALIDATION.md; they are not active Python commands or requirements.


## IDE development inheritance

The certified template IDE delta is propagated to the existing User service as a
reviewed identity-adjusted delta. Do not rerun `scaffold-service` over an already
generated service. The parent transformer supports the same delta for future
services, once the certified template is published and its pin is adopted separately.
This change does not update any child gitlink or the approved baseline SHA.

Generated services retain flat `src/` and `main:create_app()`. Direct `src/main.py`
is LOCAL-only, binds loopback on `HOST_APP_PORT` (5300 by default), constructs the
factory once, and disables generic Flask dotenv loading, the Flask debugger and the reloader.
Use Python 3.12, a repository `.venv`, and the single `requirements.txt`.

Inside a service repository, `make providers ENV=local` starts only PostgreSQL and
Redis on loopback (defaults 55432/56379), retains LOCAL data, and generates private
`.env.host.local` from validated service-specific configuration. Build initially,
then `make migrate ENV=local`; start PyCharm's Python-script configuration or VS
Code's **Flask: host LOCAL**. Select `.venv/bin/python`; Sources Root is optional
editor assistance. Direct main loads the host file without any IDE env profile. Stop the
IDE process before `make providers-stop ENV=local`. Full Docker workflows remain
available. See each service's README and `docs/service/development.md`.

Ordinary integration testing remains `make integration`. Optional `make test-providers`
owns fresh disposable TEST PostgreSQL/Redis, generated credentials, dynamic loopback
ports, a private env file and ownership manifest, and a foreground lease. Fixtures
verify that lease and the exact Docker project, container IDs, labels and endpoints
before destructive database or server-wide Redis tests. Ctrl-C/SIGTERM cleans only
the owned session. LOCAL/DEV providers are never reused for those tests.

Only `.vscode/launch.json`, `.vscode/settings.json` and optional
`.vscode/extensions.json` are permitted IDE payloads. JSON must be portable and must
not embed credentials, provider URLs, absolute machine paths, or generated session
paths. `.idea/`, `.venv/`, `.host-sessions/`, `.env.host.local`, `.env.host.test.*`, and
all other real dotenv files remain forbidden payloads; `.env.example` is the sole
tracked environment source. The implementation uses `.host-sessions/<project>/test.env`
for private TEST files rather than a `.env.host.test.*` naming convention.

Scaffold validation checks a complete IDE-support profile when the source opts in.
The existing business-runtime classifier deliberately retains its runtime anchors:
optional IDE configuration does not determine whether a service can build/run.
Independent tests cover both the published pre-IDE baseline and the new profile.
`tests/ide-template-delta.patch` freezes the certified IDE delta including direct host loading over the
unchanged baseline for reproducible disposable fixtures; tests never consume a mutable
real template worktree or rerun scaffolding over real User. Remove/rebase that fixture
only as part of a separately reviewed baseline adoption.

Run parent validation without Docker using Python 3.12:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest discover -s tests -p '*test.py'
```

These tests create Git histories only in disposable fixture repositories. Actual
IDE breakpoints/discovery, final publication, and child pin adoption remain Prompt 3.
TODO and unrelated workspace state are outside this change.

### Zero-friction direct Flask startup

Future services inherit the service-neutral `src/settings/host.py` loader. After
`make providers ENV=local` and `make migrate ENV=local`, plain `python src/main.py`,
PyCharm Python-script Run/Debug and VS Code F5 all load the repository's private
host file without IDE env profiles. Sources Root is editor assistance only. The
factory, Docker, Alembic and test ownership behavior remain unchanged. An existing
runtime image must be rebuilt after dependency/migration changes.

Scaffold guards require the shared loader and forbid application-launch envFile/env
injection. The separate owned TEST debug envFile remains supported. No identity
replacement rules or package-path transformations change. The frozen IDE payload
fixture and its digest cover this correction; generated private files remain forbidden.
