# Canonical workspace and approved-pin validation

Validated on macOS with Apple Git 2.50.1, Bash 3.2.57, and GNU Make 3.81.
Workspace readiness is independent of full-stack readiness. Template Mac
verification passed as part of its approved baseline; this parent adoption does
not rerun standalone template certification. App standalone manual verification
remains pending and is not certified here.

## Approved integration

Only these two gitlinks advance:

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

From this repository, with Python 3 available for the test harness only:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p '*_test.py'
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

## Scaffold command release certification

Run the dedicated fixture suite independently of public active-service tests:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'scaffold_service_test.py'
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'workspace_test.py'
```

Fixtures create disposable real repositories, approved placeholder commits, and
local remotes; they never scaffold the real user service. The scaffold helper has
no runtime Python dependency. Tests exercise exact payload and executable modes,
Git identity/index preservation, literal Make inputs, preview, source/destination
safety, approval metadata, ignore compatibility, archive attributes, forbidden
artifacts, unrelated child work, repeat refusal, and operational recovery.
Fixture-scoped command wrappers inject failures; no production failure-injection
option is exposed. Docker is absent from fixture PATH and Git transport is disabled
inside the scaffold helper, including lazy-fetch prevention.

Certification results on macOS Bash 3.2.57 / GNU Make 3.81:

- Scaffold suite: **58 passed, 0 failed, 0 skipped, 58 total**.
- Existing workspace regression suite: **19 passed, 0 failed, 0 skipped, 19 total**.
- Shell syntax checks, Make help, and `git diff --check`: passed.
- The real user service was not scaffolded. Its source/pin and all other child pins
  remain unchanged; TODO.md retains its recorded SHA-256.

Shared Git checks are extracted into scripts/git-safety.sh. Existing workspace
fixtures include that library and must retain all 19 passing setup/sync cases.
Runtime box/Compose files, .gitmodules, all pins, and child source stay unchanged.

Actual-template certification used disposable parent clones populated from locally
available child Git objects, with canonical child origins and the parent's exact
pins. No real child was fetched or updated. Source:
`backend/template-goalstats-service` at
`e89164842ca2c0f2954919a38da3ed4924d5f3ac`; destination baseline:
`backend/goalstats-user-service` at
`70c77c692993fc18e9f484bf22266a15288c0541`.

Both preview and installation passed with Docker absent and Git transports disabled
after setup. All **139 tracked files** matched the approved template's paths, bytes,
and modes; migrations, Item/Action, and template identities remained intact. Git
administration stayed destination-owned: pointer/resolution, origin/config, branch,
HEAD, refs/history, and index were unchanged. Parent HEAD, index, and gitlinks were
unchanged; parent status showed dirty child content with nothing staged.

Actual and dry-run repeats refused both before and after a disposable child commit,
without overwriting, deleting, or staging anything. Fixture tests additionally cover
missing offline objects, archive/extraction/temp failures, partial-install and final
verification failures, malformed approvals, hostile inputs, and simultaneous lock
contention. Recovery evidence survives partial writes and prevents blind retries.

The documented setup → feature branch → preview → install → child status/diff
sequence was exercised in two independent disposable workspaces. This is a scripted beginner
walkthrough, not a study with human participants. Output exposes exact identities,
file additions/replacements, and the expected unstaged child work; raw scripts,
approval metadata, and Git diffs remain directly inspectable.

All five real runtime guard checks (`build`, `run`, `migrate`, `test`, `smoke`)
refused the runtime-pending user service before partial execution, as required.
No full-stack or destination-service runtime certification is implied.

The real dry run was **NOT RUN**: untracked user-owned TODO.md and the destination's
detached HEAD block it. The uncommitted parent implementation also blocked it during
certification. These rules were not bypassed; no real feature branch was created.
Resolve prerequisites and perform the real preview before scaffolding in a separate
explicit task. Windows remains unverified. No production safety changes were needed
by certification; five fixture cases and documentation updates complete the release.
