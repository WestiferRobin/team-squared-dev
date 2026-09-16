# Python scaffold policy v2 — certification

## Prompt 2 independent certification (2026-09-16)

Canonical template: `f4e2a94371dd894ffae70eee818f51f92179d183`.
A fresh disposable parent candidate was built from exactly the intended parent
changes and canonical template gitlink, excluding dirty TODO and real User work.
Setup and sync initialized all five approved pins without application setup.

An independent checker read every committed template blob and compared generated
paths, bytes, Git modes and directory sets: **120 files, 50 package paths renamed,
58 content changes**. These are observations for this commit, not policy constants.
Item/Action identity, migration `b7f42e9c1a60`, migration bytes, requirements,
Docker digests and framework identities are preserved. No User business logic
is introduced. No residual service identity or unexpected files remain.

Both preview and installation passed under a macOS sandbox denying network access.
Preview preserved a complete filesystem/Git snapshot, including directories and
metadata. Installation attached existing master without changing destination HEAD,
refs, origin, index, Git pointer or parent destination pin. Both repeat forms refused.
The fresh candidate parent run passed **75 tests, zero failures, zero skips**:
13 transformer, 35 scaffold, 19 workspace and eight service-contract tests.
Six additional disposable certification tests passed. They covered attachment
failure with retained phase evidence,
wrong parent branch, mismatched master/origin-master, missing origin-master and
delegation across all four static states. Historical recovery machinery remains
removed and retained policy-1 evidence is not consumed.

Generated runtime certification used a fresh Python 3.12 venv with only
`pip install -r requirements.txt`. Ruff lint, formatting (86 files) and mypy
(52 source files) passed. Unit **85**, integration **49**, full **134**, smoke **8**
and workflow tooling **19** tests passed, with zero unexplained skips. Coverage
was **99%** (775 statements, two misses). All unit/integration/smoke/tooling node IDs
matched the canonical template after approved identity normalization.

Real PostgreSQL catalog comparison found no schema change. Migration upgrade,
repeat upgrade, downgrade/re-upgrade and migration-check passed without pending
model changes. OpenAPI and route methods matched after normalizing only the API
title. LOCAL reload/read-only source mount/Swagger and LOCAL/DEV persistence passed.
DEV ran built non-root Gunicorn; TEST remained isolated. Health/readiness outages,
cache fallback, Problem Details, built smoke, failure cleanup, SIGTERM/SIGINT and
unrelated-resource preservation passed through `make certify`. Its deliberately
failing smoke assertion is an expected cleanup test, not a normal-suite failure.
The workflow compared Docker inventories (baseline: five containers, 63 images,
six networks, 11 volumes), preserving pre-existing resources; no global prune ran.

Real User files and Git metadata and the pre-existing TODO change are preserved.
User remains pinned at `70c77c692993fc18e9f484bf22266a15288c0541`; sibling pins
are unchanged. Parent full-stack readiness and real User reconciliation remain
separate work. This record describes pre-publication certification; publication
and verification of the published fresh clone are reported with the release result.

## Prompt 1 implementation record

Canonical template: `f4e2a94371dd894ffae70eee818f51f92179d183`.
The following implementation record predates the independent Prompt 2 results above.

Run parent tests with Python 3.12 and bytecode disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 -B -m unittest discover -s tests -p '*_test.py'
```

Fixtures read the canonical template commit from the local template object database;
they create only disposable parent/child repositories and local origins. Independent
golden substitution checks compare all canonical files, paths and modes. Tests cover
write-free preview, exact installation, Git preservation, attachment, failures,
concurrency, offline behavior, strict artifacts, and static runtime guards. Existing
workspace setup/sync regression coverage remains separate and unchanged.

The real User and existing tracked TODO modifications are never fixture inputs to
mutate. The only intended child working gitlink change is template adoption. No
staging, commit, push, real scaffold or application runtime certification occurs here.

## Prompt 1 results (2026-09-16)

The final combined parent run passed **75 tests, 0 failures, 0 skips**:
13 transformer, 35 scaffold, 8 service-contract, and 19 unchanged workspace tests.
Expected injected preparation/install/final-verification errors are asserted negative
cases; they are not normal-suite failures. Concurrency uses explicit synchronization;
an earlier timing-dependent test was corrected before the final successful run.

Canonical independent mapping observed 120 files, 50 renamed package paths and
58 files with changed content for the selected SHA. These are observations, not
permanent count requirements. Python/shell syntax, Make help, active local doc links,
parent implementation static checks, and git diff whitespace checks passed.
TODO and real User bytes/deleted-ignore state, User HEAD/master/origin-master and
parent index were preserved. Template working checkout is canonical; staging its
new gitlink is deliberately deferred to Prompt 2. No generated runtime certification
or publication is claimed by these parent test results.

# Historical archive — all records below predate Python policy v2

The following records describe older workspace/.NET implementation and recovery
work. Their pins, test counts, commands, readiness claims and local-state observations
are historical, not current instructions. In particular policy-1 recovery is removed
from the active Python interface. Retained evidence remains untouched.

# Canonical workspace and approved-pin validation

Validated on macOS with Apple Git 2.50.1, Bash 3.2.57, and GNU Make 3.81.
Workspace readiness is independent of full-stack readiness. Template Mac
verification passed as part of its approved baseline; this parent adoption does
not rerun standalone template certification. App standalone manual verification
remains pending and is not certified here.

## Earlier approved workspace integration

The earlier workspace integration advanced these two gitlinks (historical evidence):

| Component | Previous pin | Approved pin |
| --- | --- | --- |
| template-goalstats-service | 47ed7cb27c1a00bf6a4b784276f86182ca3c6d05 | e89164842ca2c0f2954919a38da3ed4924d5f3ac |
| goal-stats-app | e01a3475b92fe55808006bf91a470fe97eb2b4ef | d7e77e711b4286481a35ffb3a98c8b2892ffe8cf |

Both approved commits are published on their canonical SSH remotes and were
selected by exact SHA. The user-service, wiki, and RoadToTheFinal pins remain
unchanged; the complete matrix is in [READINESS.md](READINESS.md).
Child source, including child documentation, is unchanged. The parent retains
its registry, Compose definitions, runtime guards, and reference/docs exclusions.

## Reproducible local Git fixtures

From this repository, with Python 3.9+ available:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'workspace_test.py'
```

The suite creates real disposable parent/child repositories and local remotes.
Setup/sync themselves do not require Python. Test subprocesses use
`PATH=/usr/bin:/bin:/usr/sbin:/sbin` and assert Docker cannot be found. Test Git
identity and file transport permission are confined to subprocess environments;
user Git configuration and real remote history are not modified.

All 19 fixture tests passed. The suite covers:

- Fresh nonrecursive setup, pending-runtime success, exact pins, feature/detached
  parent preservation, and no parent fetch even with an inaccessible parent origin.
- Missing env creation, repeated setup preserving binary env bytes, and attached
  child branch preservation at the correct SHA.
- Current-master sync, fast-forward to an updated child pin, new child initialization,
  reloading the updated helper, canonical URL repair, no env changes, and refusing
  newer unapproved child remote HEADs even with recursive user Git config enabled.
- Parent staged/unstaged/untracked changes, edited/staged `.gitmodules`, staged
  gitlinks, feature/detached branches, locally ahead/divergent history, real merge
  conflicts, and merge/rebase/cherry-pick/revert/sequencer markers.
- Child staged/unstaged/untracked work and clean off-pin commits; nested dirty/off-pin
  work, nested operation state, and staged nested gitlinks. Refusals preserve parent
  HEAD. Unexpected nonempty uninitialized paths are preserved.
- Incoming occupied submodule removal, ignored-file collisions, and an incoming
  file replacing an ignored directory; local ignored content survives refusal.
- A child download failure after parent fast-forward: the old child remains intact,
  sync reports a safe retry, and `make sync` succeeds once its remote becomes
  available. An unrelated child commit introduced during interruption is refused.

These tests are separate from public `make test`, whose existing ACTIVE child suite
delegation remains unchanged. No new public Make test aliases are introduced.

## Candidate fresh clone and real pin adoption

A disposable nonrecursive parent clone received the intended parent workspace
files in a fixture commit at the old pins. A clean clone of that fixture ran
`make setup`; a subsequent fixture commit adopted exactly the two approved pins.
`make sync` fast-forwarded the old workspace and materialized both exact approved
SHAs without modifying env files. Real remote history was not manipulated. The
local fixture suite separately proves that newer unapproved child remote HEADs
are never selected.

A separate nonrecursive clone of the resulting candidate then passed:

- Docker absent from PATH, not merely installed and unused.
- `make setup` exit 0, all five children initialized at the required SHAs, canonical
  origins, parent env files prepared, workspace-ready and runtime-pending output.
- Template Make/Docker/service source/unit/integration test structure present.
- App Make/Docker/source/component-test/browser-test scaffold present.
- User-service still contains only its tracked `.gitignore` and `README.md`.
- Repeated setup with identical env SHA-256 hashes, parent HEAD, and child SHAs.
- Current-state `make sync` exit 0 with unchanged pins, env hashes, and clean status.
- Actual selected app dirty-work and clean off-pin refusal, preserving the modified
  bytes or selected commit. The fixture was restored and verified clean afterward.

These clones use a disposable local parent origin for unpublished-candidate
verification, and actual canonical SSH child origins. They do not substitute for
post-push verification of the published parent.

## Published verification

After the validated parent is committed and pushed normally to master, the final
certification step is one new nonrecursive clone from:

```bash
git clone --branch master git@github.com:WestiferRobin/team-squared-dev.git
cd team-squared-dev
PATH=/usr/bin:/bin:/usr/sbin:/sbin make setup
```

The validation harness first asserts that this PATH contains no Docker executable.
It requires the exact pushed parent SHA, all five required child SHAs, canonical
origins, clean status, env preparation, and workspace-ready/runtime-pending output.
The execution report records the pushed commit and final published-clone result.
Only disposable verification clones/fixtures are removed after certification.

## Existing checkout safety

`TODO.md` remains untracked and byte-for-byte preserved, with SHA-256:

```text
57af1c8c8453c8e2e11c018600afd438a5a7f10c30773f98d44590825ddadccd
```

Real-workspace setup/sync refusal while TODO.md or implementation changes are
present is expected conservative behavior. No exception is added. Deliberate pin
adoption selects only the two approved clean child commits; automated setup/sync
is certified in disposable clean workspaces. Staging uses explicit intended
parent file and gitlink paths, excluding TODO.md, env files, and generated artifacts.

## Runtime guard regression

In the initialized candidate, both LOCAL and DEV build/run/migrate/smoke fail
before build, migration, or startup because the active user-service contract is
missing. `make test` fails before active-suite delegation. The new app Makefile
and Dockerfile are present and are no longer reported missing.

The user service still lacks its Dockerfile/Makefile and Compose definition;
its migration/readiness/health/smoke fields remain pending. No reference component
is activated to compensate. No containers, migrations, or child test suites are
started by these checks. App standalone manual runtime verification remains pending.

Shell syntax checks, grouped `make help`, and `git diff --check` pass. The Prompt 1
workspace helper and tests are included with pin adoption; runtime changes only
separate the former setup dispatch. All runtime guards and normal active test
semantics remain intact, including E2E=false and reference/docs exclusions.

## Bootstrap and platform boundaries

The tracked bootstrap source is `backend/template-goalstats-service` at
`e89164842ca2c0f2954919a38da3ed4924d5f3ac`. The destination is
`backend/goalstats-user-service` at `70c77c692993fc18e9f484bf22266a15288c0541`.
The workspace makes both available for a later tracked export, user-service feature
branch, and concrete implementation. No export or implementation is performed here.

Windows is not certified. WSL with Git/Make/Bash and Docker Desktop integration is
the preferred candidate; Git Bash plus GNU Make needs verification. Native
PowerShell is not the primary script interface. Full-stack runtime, migrations,
health/connectivity, smoke, and active-suite certification remain deferred.

GOALSTATS-USER-SERVICE REMAINS RUNTIME-PENDING

## Historical DOMAIN-aware scaffold implementation validation

Run the independent fixture suites (Python 3.9+ is now also a scaffold prerequisite):

```bash
python3 -B tests/scaffold_transform_test.py
python3 -B tests/scaffold_service_test.py
python3 -B tests/workspace_test.py
```

The source is the certified `GoalStats.Template.*` / `TemplateDbContext` template at
`8d05ddfb5d2ece712f26000efcf38408ff33bfe4`. Only this parent template pin changes. The approved registry row is
`goalstats-user-service<TAB>70c77c692993fc18e9f484bf22266a15288c0541<TAB>User`.

```bash
make scaffold-service SERVICE=goalstats-user-service DOMAIN=User DRY_RUN=true
```

DOMAIN is required and must match registry approval. Valid forms include User,
Match, Team and PlayerStats; the latter derives playerstats without word splitting.
Generated identity is `GoalStats.<DOMAIN>.*` / `<DOMAIN>DbContext`. This is identity
transformation only: Item/Action remain examples; no business-domain generation.

Fixtures preserve all existing Git safety scenarios and use independently authored
expected output. Source export must equal the committed source; destination must
equal the expected transformed paths, bytes and modes. Tests cover boundaries,
opaque files, text encoding, collisions, required anchors, failure cleanup/recovery,
Python availability, literal Make inputs and concurrency. Docker is absent from
fixture PATH; scaffold Git transport is disabled, including lazy fetch.

Disposable candidates verify the newly pinned actual template without running the
command against the real user service. Generated User build, EF and runtime
certification results are recorded below. A successful install intentionally leaves the
child dirty and unstaged. Review, then commit/publish the child and deliberately
adopt its approved pin later; the scaffold does neither.

Setup/sync behavior and active runtime topology remain unchanged. Parent build,
run, migrate, test and smoke must still refuse the runtime-pending user service.
The real child stays at its placeholder SHA; TODO.md is preserved. No real scaffold,
staging, commit or push is part of this implementation.

Recorded implementation checks on macOS Bash 3.2.57 / GNU Make 3.81:

- Transformer suite: **25 passed, 0 failed, 0 skipped, 25 total**.
- Scaffold suite: **67 passed, 0 failed, 0 skipped, 67 total**.
- Workspace suite: **19 passed, 0 failed, 0 skipped, 19 total**.
- Python syntax, Bash syntax, Make help and whitespace checks passed.
- `/usr/bin/python3` is **3.9.6**; missing/unusable Python and simulated Python 3.8 refusal are fixture-tested.
- Actual-template preview and installation passed in a disposable candidate with
  Docker absent. All **139 files** matched independently calculated transformed
  paths, bytes and modes; parent/destination Git identity was preserved.
- Migration filenames retain `20260908043250_InitialCreate`; all non-token bytes,
  including schema operations, routes, package versions and Item/Action, match.
- All five real runtime guards refused the incomplete active User contract.
- Only the template pin advances from `e89164842ca2c0f2954919a38da3ed4924d5f3ac`
  to `8d05ddfb5d2ece712f26000efcf38408ff33bfe4`, verified against canonical remote
  master. The clean real User placeholder, other child pins and TODO.md are preserved.

REAL GOALSTATS-USER-SERVICE REMAINS UNSCAFFOLDED


## Historical generated User release certification (Prompt 4)

The candidate parent was cloned into a fresh disposable checkout. `make setup`
retrieved the actual canonical child pins independently of the active developer
worktrees. The approved template was
`8d05ddfb5d2ece712f26000efcf38408ff33bfe4`; the disposable User destination began at
`70c77c692993fc18e9f484bf22266a15288c0541` on `feat/architecture-prototype`.

Production preview and installation passed. An independent byte/path comparison
mapped all 139 source entries exactly once, with zero reserved template tokens.
Git pointer/resolution, origin/config, branch, HEAD, refs/history and index were
preserved, as were parent HEAD/index and destination gitlink. Both actual and
preview repeats refused after uncommitted generation and after a disposable child
commit. A separate fresh beginner walkthrough exercised setup, branch creation,
preview, installation, child status and diff; nothing was staged by the command.

The parent suites passed with no skips: 25 transformer, 67 scaffold and 19 workspace
tests (111 total). All original 58 scaffold safety scenarios remain represented.
The fresh candidate also passed its 25 transformer and 67 scaffold tests. Coverage
includes transformation/collision refusals, archive mismatch, partial-install and
final-verification failures, recovery evidence and concurrency during transformation.

Generated-service checks passed:

- `GoalStats.User.sln` build: **0 warnings, 0 errors**; API Release publish and Docker
  development/runtime builds passed.
- `UserDbContext`; exactly `20260908043250_InitialCreate`; no pending model changes.
  Fresh PostgreSQL migration application and repeat/current application passed.
- Unit: **304 passed, 0 failed, 0 skipped**.
- Integration: **271 passed, 0 failed, 0 skipped**.
- Full suite: **575 passed, 0 failed, 0 skipped, 575 total**.
- Documented Make setup/build/migrate/run/stop/restart workflows passed for LOCAL
  (Development, source watch) and DEV (Staging, built non-root runtime, no source
  mount). Unique project names and host ports isolated these runs.
- Health/readiness, Swagger JSON title `GoalStats.User.Api`, UI initialization label
  `GoalStats.User.Api v1`, Item/Action CRUD, cascade and Redis cache invalidation
  passed. The UI label is served in `/swagger/index.js`.
- Identity-only comparison preserves migration IDs, Up/Down/schema operations,
  routes, DTOs/enums, package versions and non-token bytes. HTTP contracts and
  Item/Action behavior remain template-equivalent; no User functionality is generated.
- Generated `./scripts/smoke.sh` passed and removed its owned resources.

The real parent runtime guards still refuse the incomplete active User contract.
The real User repository was never scaffolded, branched or modified. TODO.md is
preserved and excluded from publication. Only the approved template gitlink changes;
User, app, wiki and RoadToTheFinal retain their recorded pins.

The unmodified generated `python3 scripts/certify-workflows.py` passed LOCAL/DEV
CRUD/cache checks, two persistence cycles in each mode, normal test/smoke execution,
two controlled failures (exit 73) and SIGTERM (exit 143) for each script. Owned
resources were removed, LOCAL/DEV sentinel rows survived, and pre-existing Docker
containers/states, networks and volumes were preserved. An additional controlled
User test failure preserved a disposable template-named container without restart
and an unrelated sentinel volume. Those sentinels were then explicitly removed.
No certification image tags remained. All candidate resources/evidence are
confined to disposable storage; no template or real User source was edited.

No production fixes were required by certification. The only harness correction
was checking the Swagger UI label in its separate initialization script rather
than assuming the label appeared directly in the HTML document.

DOMAIN-AWARE SCAFFOLDING READY FOR REAL GOALSTATS USER SERVICE

Resolve real-workspace prerequisites, create `feat/architecture-prototype` inside
the User service, and run the real DOMAIN=User preview/scaffold only as a separate
explicit task. This certification does not perform that action.

## Test-aligned template adoption and generated User certification (historical)

The selected template advances from
`8d05ddfb5d2ece712f26000efcf38408ff33bfe4` to
`f5c1c9d652d74ce11bcc381df4155027ec5a713e`, the exact certified/published
Prompt 2 commit. The earlier 304/271/575 results above are historical.
That certified baseline was **260 unit / 276 integration / 536 total**.

A disposable parent candidate carried this pin and current parent metadata. A
fresh clone of that candidate ran `make setup` against canonical child remotes.
Only its exact User placeholder at
`70c77c692993fc18e9f484bf22266a15288c0541` received
`feat/architecture-prototype`. Production DOMAIN=User preview and installation
passed. An independent literal byte/path transformation verified all **140 files**,
including modes, one-to-one path mapping, no missing/extra files and zero reserved
template tokens. Dry run changed no repository files. Installation preserved Git
metadata, origin, branch, HEAD/history, index and the parent destination gitlink.
Both preview and actual repeats refused after dirty generation and after a
disposable child commit.

The working parent and fresh candidate each passed **25 transformer / 67 scaffold /
19 workspace tests**, with no failures or skips. No transformer, scaffold or runtime
implementation changed; existing safety scenarios remain intact. Real parent
build/run/migrate/test/smoke all refused the incomplete active User contract before
partial execution. No real User scaffold or dry run was performed.

Generated architecture preserves integration-only controllers, direct DTO/enum/
exception-class/model/mapper/service unit coverage, real framework/provider
integration and linked pure test support. Startup, Fixtures and FixtureTests retain
separate responsibilities. No cosmetic mirrored suites were introduced.

Generated User validation passed:

- Unit **260**, integration **276**, full **536**; zero failures/skips, exact agreement
  with the certified template and individual suite discovery.
- `GoalStats.User.sln` build: **0 warnings / 0 errors**; API publish succeeded.
- `UserDbContext`, migration `20260908043250_InitialCreate`, no pending model changes;
  initial and repeated PostgreSQL migration application succeeded.
- Public Make setup/build/migrate/run/stop/restart in LOCAL Development and DEV
  Staging, including built DEV runtime without source mounts, User Swagger identity,
  health/readiness, Item/Action behavior, Redis invalidation and persistence.
- Existing smoke and workflow scripts: normal runs, two controlled failures per
  script, SIGTERM cleanup, two LOCAL/DEV persistence cycles and preserved sentinel
  rows. No generated production/schema/HTTP/cache changes beyond identity tokens.

Resource review found unchanged user-created networks, volumes and image inventory,
no pre-existing containers, and no certification-owned resources left. Docker's
built-in `bridge` ID changed from `51c3ac11f33e` to `f8bfb4ab272b` near the first
unit tooling build; no certification command targeted it. The subsequent complete
workflow certification preserved its before/after inventory, including that bridge.
This environmental observation is recorded rather than claiming the initial network
IDs all matched.

The pinned README's historical claim that DOMAIN scaffolding is planned remains
unchanged in exact generated output; parent development guidance clarifies that the
command is available. Generated content is an Item/Action skeleton, not User
business logic or authentication. The real User service remains unscaffolded;
TODO.md and User/App/Wiki/RoadToTheFinal pins are preserved. Real-workspace
prerequisites and an explicit separate task are required before real scaffolding.

## MetaController template adoption and generated User certification

The parent adopts the certified and published template commit
`07a75b4a8e6e83429c41c51527691870884d76e8`, replacing
`f5c1c9d652d74ce11bcc381df4155027ec5a713e`. The current baseline is
**260 unit / 293 integration / 553 total**. No scaffold implementation or runtime
topology changes were needed.

A fresh disposable clone of the parent candidate ran `make setup` against canonical
child remotes. Its exact User placeholder alone received `feat/architecture-prototype`.
Production DOMAIN=User dry run and scaffold passed. Independent literal byte/path
transformation verified all **141 files**, modes, one-to-one mapping, no missing or
extra files, no collisions and zero residual reserved tokens. Dry run wrote nothing;
installation preserved Git metadata, origin, branch, HEAD/history and index. Actual
and preview repeats refused both dirty and committed generated destinations.

Working parent and fresh candidate each passed **25 transformer / 67 scaffold /
19 workspace tests**, with no failures or skips. Real parent build/run/migrate/test/
smoke refused the incomplete active User contract before partial execution.

The generated service passed:

- Unit **260**, integration **293**, full **553**, zero failures/skips and exact
  certified discovery counts. Controllers, including MetaController, remain
  integration-only; logic, provider/framework and test-support placement is preserved.
- Solution build with **0 warnings / 0 errors**, API publish, `UserDbContext`,
  `20260908043250_InitialCreate`, no pending model changes, and initial/repeated
  migration application against disposable PostgreSQL.
- **72 live HTTP comparisons** against the exact template: two operational routes,
  GET/HEAD/POST/OPTIONS, three Accept values and Healthy/Degraded/Unhealthy states.
  Status, body, content type, cache headers and content-length behavior matched.
  MetaController owns both routes; Program has no direct mappings. Predicates/tags
  and provider logic are unchanged by the exact transformation.
- Redis outage with healthy PostgreSQL produced **200 Degraded**; PostgreSQL outage
  produced **503 Unhealthy** on readiness. Health remained **200 Healthy**. Recovery
  passed; startup waits still require **200 Healthy**. Neither route appears in
  Swagger; User identity and the Item/Action HTTP contracts are preserved.
- LOCAL Development and DEV Staging public Make workflows, published DEV runtime
  without source mounts, Swagger, Item/Action CRUD/cache/cascade and persistence.
- Unmodified smoke and workflow certification: normal runs, two controlled failures
  per script, SIGTERM cleanup, LOCAL/DEV persistence cycles and sentinel preservation.

No certification-owned Docker resources remain. Container, volume and image
inventories match the initial inventory; all user-created network IDs are unchanged.
Docker's built-in `bridge` ID changed from `77803372f8e9` to `b8b0de50c4e2` during
certification; no certification command targeted it. The complete workflow script
subsequently verified unchanged unrelated resources across normal/failure/SIGTERM
runs. This environmental difference is recorded rather than asserting identical
initial/final network IDs.

The real User remains the clean detached placeholder at
`70c77c692993fc18e9f484bf22266a15288c0541`; no real dry run, branch or scaffold was
performed. User/App/Wiki/RoadToTheFinal pins are unchanged. User-owned TODO.md was
already tracked at the starting parent commit and remains byte-for-byte unchanged;
it is excluded from this adoption commit. Generated files and certification resources
are disposable, not parent payload. Real User scaffolding requires a separate
explicit task and successful real preview.

## Safe master auto-attach implementation (Prompt 1)

This supersedes earlier feature-branch prerequisite guidance; historical certification
records above describe the workflow tested at that time. Owned repos now use master;
RoadToTheFinal remains the main exception. Preview accepts a clean, exact approved
detached destination with matching local master/origin/master and performs no
repository writes. Actual installation attaches only after payload preparation and
revalidates identity before copying files. Scaffold remains offline after setup.

Prompt 1 automated fixture validation covers detached/master preview and installation,
identity preservation, linked-worktree refusal, attachment failure and concurrent
state changes. Full real-template fresh-clone certification and publication belong
to Prompt 2. The real User remains untouched and unscaffolded.

Automated validation passed: **75 scaffold / 25 transformer / 19 workspace tests**,
zero failures or skips. Shell/Python syntax, make help and diff whitespace checks
passed. The disposable detached preview/install sequence passed without manual
branch attachment between commands. Child pins, real User and TODO.md are unchanged;
no staging, commit or push was performed in Prompt 1.

## Safe master auto-attach certification (Prompt 2)

Two independent fresh disposable clones of the final parent candidate ran normal
`make setup`, then DOMAIN=User preview and installation without any manual child
branch commands. Both began detached at the exact approved User pin. Preview
preserved complete repository file bytes/modes, including refs, reflogs, config,
indexes and placeholders. Installation attached only the destination to existing
master without moving HEAD or refs; the parent gitlink remained unchanged.
Independent literal transformation verified all **141 files**, paths, bytes and
modes with zero residual reserved tokens, missing/extra files or collisions.
Dirty and committed repeats refused both preview and actual installation.

Parent suites passed **75 scaffold / 25 transformer / 19 workspace tests**, with
zero failures or skips. Fixtures covered already-master preview/install, linked
worktrees, missing/mismatched refs, incorrect branches, operations, dirty content,
locking, preparation races, attachment failure, post-attachment refusal and
mid-install recovery. Shell/Python syntax, help and diff checks passed. Scaffold
remains offline after setup; setup/sync Git behavior and DOMAIN transformation
are unchanged. Real parent runtime commands still refused incomplete User contracts
before partial work.

Generated User passed **260 unit / 293 integration / 553 total** with zero
failures/skips, matching the certified template. Solution build had **0 warnings /
0 errors**; API publish passed. EF verified UserDbContext,
`20260908043250_InitialCreate` and no pending model changes. MetaController and
integration-only controller architecture were preserved exactly.

Generated smoke and unchanged workflow certification passed LOCAL/DEV, Swagger,
Item/Action CRUD/cache/cascade, PostgreSQL/Redis, repeated persistence cycles,
controlled failures and SIGTERM cleanup. Additional hosted GET/HEAD/POST/OPTIONS
checks verified health remained 200 Healthy, readiness became 200 Degraded with
Redis unavailable and 503 Unhealthy with PostgreSQL unavailable, then recovered.
Plain-text/cache behavior and Healthy-only waits were preserved.

Final Docker container, network, volume and image inventories exactly matched the
initial inventory. Certification-owned resources were removed. All child pins,
TODO.md and the real User placeholder were unchanged. Owned repositories retained
master only; RoadToTheFinal retained main. No real User preview/scaffold was run.

## Real-workspace attachment config fix (Prompt 1)

A deterministic real-submodule regression reproduced the published failure before
the fix: VS Code adding `branch.master.vscode-merge-base=origin/master` immediately
after symbolic HEAD attachment caused full-config identity comparison to refuse.
The comparison now parses local config entries and permits only that absent-to-single
value transition during attachment. Existing entries and all other config remain
strict. HEAD reflog verification permits exactly the approved same-commit attachment
entry, preserving prior history; installation uses a strict post-attachment baseline.

Attachment failures retain private temporary diagnostics instead of deleting the
only evidence. Already-master preview reports `MASTER AT APPROVED PIN`, with no
attachment comparison or branch action. Full certification/publication is reserved
for Prompt 2. The real User remains on master, clean and unscaffolded.

Prompt 1 validation passed **84 scaffold / 25 transformer / 19 workspace tests**,
zero failures/skips, plus shell/embedded-Python syntax, make help and diff checks.
The injected exact VS Code addition failed against the pre-fix implementation and
passed after the fix. Wrong/duplicate metadata, removals/replacements, other config
changes, extra reflog entries and index mutation refused without payload writes.
Existing-metadata detached and already-master paths passed. No real User command,
pin change, staging, commit or push was performed.

## Real-workspace attachment config certification (Prompt 2)

Two fresh disposable clones ran normal setup against canonical child remotes. The
detached case ran preview and actual scaffold without manual child branch commands;
a Git wrapper injected exactly the VS Code config addition immediately after the
real symbolic-ref operation. The other clone started on approved master with the
metadata already present. Both previews preserved complete repository bytes/modes.
Both installations passed production identity checks and independent literal
DOMAIN=User transformation equality for all **141 files**, including paths, bytes,
modes, no collisions/extras/missing files and zero residual reserved tokens.
Git metadata comparisons preserved refs/index/config except the explicitly approved
detached attachment artifacts. Prior HEAD reflog history and one expected attachment
entry were verified. Dirty and committed repeats refused both commands.

Parent certification passed **84 scaffold / 25 transformer / 19 workspace tests**,
zero failures/skips, including wrong/duplicate/removed/replaced metadata, unrelated
config mutations, extra reflog entries, index changes, retained private diagnostics,
linked worktrees, operations, races and repeat refusal. Shell/embedded-Python syntax,
help and diff checks passed. No production changes beyond Prompt 1 were required.

Generated User passed **260 unit / 293 integration / 553 total** with no failures
or skips, matching the template. Solution build had **0 warnings / 0 errors**; API
publish passed. EF verified UserDbContext, `20260908043250_InitialCreate` and no
pending model changes. MetaController and integration-only controller architecture
were preserved. Smoke and unchanged workflow certification passed LOCAL/DEV,
Swagger, Item/Action CRUD/cache/cascade, PostgreSQL/Redis, persistence, controlled
failures and SIGTERM cleanup. Additional hosted method checks verified Healthy,
200 Degraded during Redis outage, 503 Unhealthy during PostgreSQL outage, recovery
and plain-text/cache behavior. Real parent runtime guards refused before partial work.

No certification-owned Docker resources remain. Container, volume and image
inventories and all user-created network IDs match the initial inventory. Docker's
built-in bridge ID changed from `d4a0b64a2881` to `bba9250b7d0e`; no certification
command targeted it. The complete workflow script preserved unrelated resources
across its normal/failure/SIGTERM checks. This environmental observation is recorded
rather than claiming identical initial/final network IDs.

The complete real User worktree/Git-file snapshot and TODO.md remained unchanged.
Real User is still clean on master at the approved placeholder with its existing
VS Code metadata; no real preview or scaffold was run. All child pins and the
RoadToTheFinal main exception are unchanged.


## Final payload verification and explicit recovery implementation

The scaffold suite retains its original 84 scenarios and adds eight cases with
subcase matrices for project-root build artifacts, unexpected extras, exact payload
failures, evidence mismatch, recovery preview/finalization, Git/pin refusals and
Codex capture refs. Fixtures run actual installation and create `bin/obj` output
before final verification. Recovery independently reconstructs the pinned payload;
preview and refusal snapshots prove preservation, while successful finalization
preserves child files/Git identity and archives only the operation marker.

Validation commands:

```bash
python3 -B tests/scaffold_service_test.py
python3 -B tests/scaffold_transform_test.py
python3 -B tests/workspace_test.py
bash -n scripts/scaffold-service.sh scripts/workspace.sh
make help
git diff --check
```

Python files and embedded scaffold Python blocks are parsed without writing bytecode.
The real User worktree, its Git metadata, incomplete marker and retained recovery
files are compared by SHA-256 and mode against the initial preservation snapshot.
No real scaffold/recovery execution, staging, commit, push or pin update is part of
this implementation validation. Publishing changes the parent HEAD; recovery of an
older operation intentionally refuses under the required strict HEAD policy. That
boundary needs explicit resolution before the later real-recovery task.

Implementation results: scaffold **92 passed / 0 failed / 0 skipped**; transformer
**25 passed / 0 failed / 0 skipped**; workspace **19 passed / 0 failed / 0 skipped**.
Shell/Python syntax, Make help and diff checks passed. All **489** baseline files
across real User, its Git metadata, marker and recovery evidence remained hash/mode
exact. This is implementation validation; publication and real recovery were not run.

## Final verification/recovery certification — publication blocked

Prompt 2 certification passed **92 scaffold / 25 transformer / 19 workspace**
tests, zero failures/skips, plus shell/Python syntax, Make help and diff checks.
Two fresh disposable canonical parent clones completed `make setup`. Normal
preview was write-free; production scaffold installed all **141** independently
reconstructed byte/mode-exact User files while six representative build artifacts
were injected across all three declared project roots immediately before inventory.
A separate fresh clone retained a completed interrupted installation, then passed
explicit recovery preview and finalization with payload, build output and child Git
identity unchanged. Evidence was retained and only its marker was archived. Both
preview and actual ordinary repeats refused after finalization.

Six additional production-path cases covered detached/master destinations with
artifact creation during copying, after the last copy, and before final inventory.
An expanded recovery refusal matrix preserved marker/evidence for arbitrary and
ignored extras, `.env`, editor metadata, caches, root/non-project bin/obj, sibling
generated directories, wrong SERVICE/DOMAIN, missing/corrupt/mode-changed payload,
residual identity, symlinks/path escapes, wrong branch and a merge operation.
Retained-manifest/mapping/completed-write and parent/pin safety cases also passed.
Missing/extra/corrupt diagnostics included counts and paths without the misleading
“committed tree” message. Scaffold and recovery use pinned local sources offline.

Generated `make unit`, `make integration` and `make test` passed **260 unit / 293
integration / 553 total**, zero failures/skips. Solution build and API publish
passed with **0 warnings / 0 errors**. EF confirmed UserDbContext,
`20260908043250_InitialCreate`, and no pending model changes. Exact generation
preserved MetaController and Item/Action examples with zero reserved template tokens.
Smoke and unchanged workflow certification passed LOCAL/DEV, Swagger, health/ready,
CRUD/cache/cascade, PostgreSQL/Redis, two persistence cycles, controlled failures
and SIGTERM cleanup. Real-parent build/run/migrate/smoke refused before runtime
actions; no real User scaffold, recovery or test execution was performed.

**P1 publication blocker:** a disposable publication transition reproduced
`Recovery refused: Parent HEAD differs from interrupted operation`. The current
strict policy cannot recover the existing real operation after publishing the fix.
Prompt 2 requires every gate, including recovery with published tooling, to pass
before committing/pushing. Therefore publication was not performed. A decision on
an explicit, narrowly constrained operation-parent transition is required before
changing this safety policy; no override has been added.

All certification-owned Docker resources were removed. Container, volume and image
inventories and user-created network IDs matched the initial inventory. Docker's
built-in bridge ID changed from `bba9250b7d0e` to `570dab75a4ab`; no certification
command targeted that bridge. The workflow's own before/after resource and unrelated
container-state preservation checks passed. This environmental observation is not
reported as an identical full network inventory.

Real User remains in its incomplete-scaffold state: master at the approved pin,
141 exact payload files, two modified placeholders, 139 untracked payload files,
10 ignored build files, nothing staged. The full 489-file worktree/Git/marker/
recovery evidence hash-and-mode baseline is preserved. All five child pins and
TODO.md remain unchanged. No parent staging, commit, or push was performed.

## Recovery parent-HEAD compatibility implementation

This implementation supersedes the strict-parent-HEAD publication blocker above;
certification/publication and real recovery remain separate tasks. The recovery
interface now requires explicit original `OPERATION_PARENT` and externally approved
`RECOVERY_TOOLING_SHA` values. The latter must match HEAD, master and origin/master.
No SHA is inferred as a substitute for the caller's certification decision.

Every intervening commit must form a complete linear descendant chain. Only the
nine exact recovery/scaffold/test/docs/Make paths listed in DEVELOPMENT.md may
change. Every child gitlink, full `.gitmodules`, both registries and the original
transformer blob/mode are frozen across every commit. Prohibited changes later
reverted still refuse. Replace refs, grafts, missing/shallow history, merges,
unrelated ancestry and conflicting staged/working parent changes refuse.

The original operation definition is read from its original Git commit. Recovery
loads the original committed transformer as an in-memory module with its CLI
inactive, invokes its pure planning logic on original template blobs, and compares
that result with the identical current transformer and retained operation evidence.
No installer or template code runs. The verified real original transformer blob is
`f061825f61c1ddcf5273ebb1af0ea7a62db969de`; the transformer itself is unchanged.

Historical index bytes are not reused as the current baseline. Instead the current
index must represent the approved committed tree, and every tracked parent file
must match its approved blob/mode. The original HEAD reflog prefix is verified by
its retained hash; appended old/new SHA pairs must follow the approved commit chain.
Master/origin-master transitions are explicit, unrelated refs/config remain strict,
and current parent identity is preserved across both verification passes. Original
snapshots are never rewritten to claim the operation happened under newer tooling.

Eight new regression cases extend the existing 92 scenarios: approved multi-commit
advancement, explicit SHA refusal, prohibited intermediate reverts, all five child
gitlinks and critical files, replace/graft substitution, merge/unrelated history,
reflog/index refusal, and an actual multi-commit publication fast-forward. The
positive case preserves historical evidence while
proving legitimate HEAD/ref/index/reflog advancement, write-free preview and actual
marker-only finalization. Recovery-specific cases are included in the scaffold suite.


Compatibility implementation validation passed **100 scaffold / 25 transformer /
19 workspace tests**, zero failures/skips. The scaffold suite includes **14
recovery-specific cases**. Additional targeted checks passed for an unavailable
original commit object (with unchanged operation evidence) and parent worktree
mutation during payload reconstruction. Syntax, Make help and diff checks passed.
The complete real 489-file User/Git/marker/recovery snapshot remained hash/mode exact;
all five child pins, transformer, registries, `.gitmodules` and TODO.md are unchanged.
No real recovery/scaffold, parent staging, commit or push was performed. This is
ready for separate certification/publication, not authorization to recover real User.

## Recovery-compatible tooling certification

A fresh canonical parent clone at original operation commit
`01b3245e937eb7644e844972f810310198d261ba` completed setup and started with the
approved two-file User placeholder. The original production scaffold installed
all **141** exact transformed files while six representative `bin/obj` artifacts
were created across the three project roots. Its old final verifier failed with
“Payload paths differ from the committed tree”; the completed-write record, marker
and original operation evidence were retained. The clone then advanced through a
parent-only candidate tooling commit, with master and origin/master aligned.
Explicit old-parent/new-tooling recovery preview and actual finalization passed.

Independent reconstruction used the original committed transformer blob
`f061825f61c1ddcf5273ebb1af0ea7a62db969de` and original template pin
`07a75b4a8e6e83429c41c51527691870884d76e8`. All 141 payload files matched bytes and
modes with zero reserved template tokens. Publication changed the parent index and
HEAD reflog, while historical evidence stayed exact. Preview wrote no repository
files. Actual recovery preserved every child file, all six build artifacts and
child Git identity; it only archived the marker. Ordinary scaffold refused with
the marker present and both ordinary repeats refused after recovery.

Additional disposable histories changed and then restored **each of all five
child gitlinks and all four critical files**, independently. All nine refused even
with empty endpoint diffs and preserved marker/evidence/payload. A disallowed
noncritical file change followed by removal also refused. Replayed/rebased history
with identical trees refused ancestry validation. Approved multi-commit docs/tooling
advancement and an actual publication-like multi-commit fast-forward passed in the
regression suite; merge, unrelated, missing-object, replace/graft, explicit-SHA,
staging, ref/reflog and concurrent tracked-file mutation refusals were covered too.

Additional recovery checks refused `.env`, editor/cache files, root/non-project
`bin/obj`, sibling generated directories, symlinks/path escapes, a hidden tracked
execution-file edit and unauthorized parent config. Recovery preview and actual
passed with a network-command tripwire and zero attempts. The existing scaffold
suite also checks that no network commands are attempted after setup. Setup, sync,
normal scaffold interface, auto-attachment, transformer and all child pins are
unchanged.

The recovered disposable User passed `make unit`, `make integration` and `make
test`: **260 unit / 293 integration / 553 total**, zero failures/skips. Solution
build and API publish passed with **0 warnings / 0 errors**. EF confirmed
`UserDbContext`, migration `20260908043250_InitialCreate`, and no pending model
changes. Smoke and unchanged workflow certification passed LOCAL/DEV, Swagger,
MetaController health/readiness, Item/Action CRUD/cache/cascade, PostgreSQL/Redis,
and two persistence cycles per mode. Normal, repeated injected-failure and SIGTERM
test/smoke runs cleaned their resources and preserved unrelated container state
and LOCAL/DEV sentinel data.

All certification-owned Docker resources were removed. Container, image and volume
inventories and every non-bridge network ID matched the initial inventory. Docker's
built-in bridge ID changed from `570dab75a4ab` to `6e64154903c7`; no certification
command targeted it. The unchanged workflow's own full before/after inventory and
unrelated-container state checks passed. This environmental observation is recorded
rather than claiming an identical full network inventory.

The real incomplete User operation is outside this certification: no real scaffold
or recovery was invoked. All **489** real User/Git/marker/evidence baseline files
remain hash/mode exact, User remains on master at its approved placeholder, and
nothing in User is staged. Publication of this parent tooling and subsequent real
recovery are distinct steps; real recovery requires the exact published commit SHA
from this certification, not a branch name or an inferred current HEAD.

The certification rerun passed **100 scaffold / 25 transformer / 19 workspace
tests**, with **14 recovery-specific cases included** in the scaffold count and
zero failures/skips. All parent shell scripts, Python files and embedded scaffold
Python blocks passed syntax checks; `make help` and `git diff --check` passed.
Every prepublication certification gate passed. The publication commit is the
externally reviewed recovery-tooling anchor; real recovery remains a separate task.

## Codex turn-diff snapshot ref compatibility implementation

The real recovery preview refused because a retained Codex checkpoint ref had
been removed. The installed editor implementation uses direct tree snapshots,
creates replacement checkpoints, and releases previous checkpoint/capture refs.
The prior capture test incorrectly used a commit target. This implementation
changes only historical snapshot-ref compatibility; real recovery and publication
remain separate tasks.

Recovery classifies publication refs, exact checkpoint/capture snapshot refs, and
strict other refs. Checkpoint names require two lowercase 64-hex components,
decimal milliseconds and a canonical lowercase UUID. Capture names require decimal
milliseconds, a canonical lowercase UUID and exactly `base` or `head`. Present
snapshots must be direct readable local trees. No committed-history reachability
is required, and removed historical snapshot objects need not remain available.
These trees never supply operation identity, history trust or payload definitions.
The original ref snapshot and all operation evidence remain immutable.

Nine new regression cases exercise the exact real checkpoint shape and lifecycle,
checkpoint/capture additions, removals and retargeting, unreachable tree targets,
removed historical tree objects, wrong object types, malformed/unknown refs,
symbolic refs (including dangling refs omitted by Git enumeration), strict other
ref transitions, simultaneous critical-state changes, and execution-time mutations.
The original capture regression now uses a tree while retaining a commit target
for its unrelated-branch refusal. Full current ref inventory, including symbolic
targets, stays frozen across recovery; a same-object symbolic conversion also
refuses. Positive recovery fixtures preserve payload and historical evidence and
archive only the marker. All recovery/scaffold executions use disposable fixtures.

Implementation validation passed **109 scaffold / 25 transformer / 19 workspace
tests**, zero failures/skips. The final complete scaffold suite ran in three
isolated, disjoint batches (37 + 36 + 36), covering every current test exactly once;
**23 recovery-specific cases are included**. Shell/Python/embedded-Python syntax,
Make help and diff checks passed. The real 141-file payload was independently
reconstructed and remained byte/mode exact, with 10 approved build-artifact files
and no unexpected extras. All 489 real User/Git/marker/evidence baseline files
remained hash/mode exact. All child pins and transformer remain unchanged. No real
recovery/scaffold, staging, commit or push was performed. Ready for separate
certification/publication; this is not authorization to recover real User.

## Codex snapshot recovery certification

Full certification passed **109 scaffold / 25 transformer / 19 workspace tests**,
zero failures/skips; 23 recovery-specific cases are included in the scaffold suite.
Syntax checks covered parent shell/Python files and embedded Python blocks. Make
help and diff checks passed. Exact checkpoint/capture forms, direct tree targets,
unreachable snapshot trees, historical addition/removal/retargeting and removed
historical objects passed. Malformed/unknown refs, commit/blob/tag/missing targets,
symbolic/dangling refs and combined critical-state violations refused.

A fresh canonical clone was prepared at original operation parent
`01b3245e937eb7644e844972f810310198d261ba` with a tree-backed checkpoint present.
The original production scaffold installed all 141 transformed User files while
six approved build artifacts were injected across the three project roots. The
old verifier failed, retaining its original checkpoint in operation evidence.
The parent then advanced through the previously published tooling commit and a
candidate snapshot-policy commit. The original checkpoint was removed; a new
checkpoint and capture `base`/`head` refs were created with direct tree targets.
Explicit SHA-bound recovery preview and finalization passed. Historical evidence
was byte-exact, preview wrote no repository files, and actual recovery only
archived the marker. All 141 payload bytes/modes, six artifacts and child Git state
were preserved; ordinary preview and actual scaffold repeats refused.

The suite exercises checkpoint/capture mutations during execution, including
same-SHA symbolic conversion. Six additional disposable cases changed master,
origin/master or a custom ref during preview/actual reconstruction: every case
refused while preserving marker/evidence/payload. Additional exact-payload cases
refused missing/corrupt/mode-changed files, residual template tokens, altered
placeholders, incomplete writes and manifest mismatch. Extra ignored files,
symlinks/path escapes, hidden tracked edits and config changes also refused.
Recovery preview/actual passed a Git network-command tripwire with zero attempts.

The recovered disposable service passed `make unit`, `make integration` and
`make test`: **260 unit / 293 integration / 553 total**, zero failures/skips.
Build and API publish passed with **0 warnings / 0 errors**. EF confirmed
`UserDbContext`, migration `20260908043250_InitialCreate`, and no pending model
changes. Smoke and unchanged workflow certification passed LOCAL/DEV, Swagger,
MetaController health/readiness, Item/Action CRUD/cache/cascade, PostgreSQL/Redis,
two persistence cycles per mode, and normal/repeated-failure/SIGTERM cleanup.
LOCAL/DEV sentinel data and unrelated container state survived the workflow runs.

All certification-owned Docker resources were removed. Container, image and volume
inventories and every non-bridge network ID matched the starting inventory.
Docker's built-in bridge ID changed from `6e64154903c7` to `37448b924746`; no
certification command targeted it. The workflow's own before/after resource checks
passed. This observation is recorded rather than claiming identical bridge IDs.

All prepublication gates passed. Real User was independently verified as 141 exact
payload files with 10 approved artifact files and no unexpected extras. Its entire
489-file User/Git/marker/evidence baseline remained hash/mode exact. All five pins,
template and transformer are unchanged. Real recovery was not invoked. The new
published commit from this certification must be supplied as `RECOVERY_TOOLING_SHA`
for the separate real recovery task; the older tooling SHA is not a substitute.
