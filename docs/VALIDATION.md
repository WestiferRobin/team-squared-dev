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

## Test-aligned template adoption and generated User certification

The selected template advances from
`8d05ddfb5d2ece712f26000efcf38408ff33bfe4` to
`f5c1c9d652d74ce11bcc381df4155027ec5a713e`, the exact certified/published
Prompt 2 commit. The earlier 304/271/575 results above are historical.
The current certified baseline is **260 unit / 276 integration / 536 total**.

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
