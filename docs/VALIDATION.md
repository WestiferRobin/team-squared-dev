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
