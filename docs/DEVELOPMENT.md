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
`backend/template-goalstats-service` at `07a75b4a8e6e83429c41c51527691870884d76e8`;
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

The selected template uses this testing philosophy:

UNIT TESTS FOLLOW LOGIC

INTEGRATION TESTS FOLLOW BOUNDARIES

SMOKE TESTS FOLLOW BUILT SYSTEM

MetaController owns `/health` and `/ready`, outside Swagger, with unrestricted
method compatibility. Readiness may be 200 `Degraded`; waits require 200 `Healthy`.
Controllers are integration-only. The certified baseline is 260 unit and 293
integration tests; DOMAIN transformation must preserve discovery. See the
[template testing guide](../backend/template-goalstats-service/docs/TESTING.md) for
placement rules. Generated services remain Item/Action skeletons, without User
business or authentication behavior.

The pinned template README still describes DOMAIN-aware scaffolding as planned.
That historical wording is copied unchanged apart from identity tokens; this parent
guide defines the available scaffold command.

The parent owns one bootstrap command:

```bash
make scaffold-service SERVICE=goalstats-user-service DOMAIN=User
make scaffold-service SERVICE=goalstats-user-service DOMAIN=User DRY_RUN=true
```

SERVICE and DOMAIN are required. DRY_RUN defaults to false and accepts exactly `true` or `false`;
an explicitly empty value is invalid. There are no force, confirmation, source, or
destination overrides. The helper exits 0 on success, 2 on validation/safety refusal,
and 1 on operational failure; GNU Make reports its own nonzero recipe-failure code.

The exactly three-column `config/scaffolds.tsv` approves service, full placeholder
commit SHA, and case-sensitive DOMAIN, separated by tabs. Legacy rows are refused. Committed component metadata supplies its active backend role, and committed
`.gitmodules` supplies the canonical URL. The source is always the current parent's
exact `backend/template-goalstats-service` gitlink. No latest branch selection, fetch,
setup, or sync is performed. Setup must already have initialized the repositories.

DOMAIN must match `^[A-Z][a-z0-9]+([A-Z][a-z0-9]+)*$`, contain 2–15 ASCII
characters, and cannot be Template. Invalid input is never normalized or inferred.
User, Match, Team and PlayerStats are valid forms; only User is currently approved.
PlayerStats derives `goalstats-playerstats` and `goalstats_playerstats`, without splitting.

Exactly four reserved families are transformed simultaneously and case-sensitively:
`GoalStats.Template` → `GoalStats.<DOMAIN>`, `TemplateDbContext` → `<DOMAIN>DbContext`,
`goalstats-template` → `goalstats-<lowercase-domain>`, and
`goalstats_template` → `goalstats_<lowercase-domain>`. Unexpected embeddings refuse.
Generic Template, Service, Api and GoalStats prose is unchanged. Swagger follows the
namespace identity and existing ` v1` label convention.

After exact export verification, Python checks required solution/project/context/
snapshot/test anchors, calculates every path and rejects duplicate, case-insensitive,
file/directory, traversal, device-name and trailing-dot collisions. It transforms into
a separate temporary tree and verifies a fresh manifest and zero reserved identities.
The source export and template child are never edited. Only UTF-8 `.cs`, `.csproj`,
`.sln`, `.json`, `.yml`, `.yaml`, `.md`, `.sh`, `.py`, and exact Dockerfile, Makefile,
.gitignore, .dockerignore, .env.example names are transformable. BOM, CRLF/LF,
final-newline state, executable mode and all non-token bytes are preserved. NUL or
invalid UTF-8 text refuses. Opaque files remain identical; identity in their bytes
or paths refuses. No exported code executes.

Only the parent, template, and destination receive relevant safety checks. Unrelated
child dirty/off-pin state is allowed, but parent staged gitlink changes are refused.
The source and destination must be clean and at their pins, with canonical origins
and no in-progress Git operations. Destination HEAD must also match its approved
placeholder SHA. HEAD, existing local master and local origin/master must all equal
that SHA and the parent pin. Only master or detached HEAD is accepted; another
worktree owning master refuses. No branch is created or reset.
Parent staged/unstaged/untracked work, including TODO.md, causes refusal. Preserve
and resolve that work deliberately; the command never moves/deletes/ignores it.

The destination must contain exactly approved regular README.md and .gitignore
files, matching committed blob bytes and modes, with no untracked or ignored files.
README is replaced by the template README. Ignore compatibility is conservative:
identical rule lists pass; otherwise destination positive rules must remain in
order, destination negations are refused, and new template negations are limited
to `!.env.example` when it does not undo a destination exclusion. Comments and empty
lines do not affect comparison. Custom rules requiring reconciliation cause refusal.
Compatibility is checked against the final transformed ignore file; there is no automatic merge.

The helper archives the exact local commit into private temporary storage, extracts
it there, and verifies paths, raw blob hashes, and executable bits against its Git
tree. Archive attributes that omit or substitute content cause refusal. Only regular
100644/100755 files and portable ASCII letter/digit/dot/underscore/hyphen/slash paths
are supported initially; unsafe paths, case collisions, symlinks, and nested gitlinks
are refused. Git metadata, real dotenv files, build/test outputs, local IDE state,
logs, database dumps/cache files, and Docker runtime data are forbidden even if
tracked. Root `.env.example`, Docker configuration, SQL source, and migrations are
allowed. Ignored source files never enter the tracked-file archive.

Dry run performs the same checks and temporary export verification, prints exact
SERVICE, DOMAIN, source/destination identities, four mappings, renames and additions/replacements, and changes no repository
files, refs, index, or configuration. It is a preview, not a reservation: actual
installation revalidates the repositories and branch state before writing.

A workspace-exclusive empty lock directory lives under `/tmp`, independent of TMPDIR.
If it exists, the command reports its exact path and refuses. Check that no scaffold
is running before manually removing a stale empty lock. No daemon is involved.

Before installing, the helper stores original placeholders and Git identity
snapshots in private temporary storage. It installs only manifest-listed files,
then verifies payload and preserved post-attachment Git identity. `.git`, origin, refs, HEAD, branch,
and indexes remain unchanged; no stage, commit, push, or parent pin update occurs.
The parent displays dirty child content; the child contains modified placeholders
and untracked new source files. This is expected. Do not run setup/sync to discard it.

Installation is not atomic. Preparation failures clean up owned temporary files
without changing the destination. A failure after attachment may leave master
attached, without payload writes; no automatic detach/reset occurs. Once payload
installation starts, a failure preserves a
recovery directory containing source SHA, DOMAIN, policy version, source manifest,
source-to-output mapping, transformed manifest, original placeholders, Git identity,
completed.txt and failed-phase.txt,
and records its path in the parent's Git directory under
`team-squared-scaffold-incomplete`. The error identifies the failed path/phase.
Inspect and preserve the resulting work; use explicit recovery verification below.
Do not manually remove the indicator, blindly rerun, reset, or clean. The command performs no automatic
rollback, and a repeat invocation refuses dirty or already-committed scaffolds.

Beginner workflow for an approved scaffolding task:

```bash
make setup

make scaffold-service \
  SERVICE=goalstats-user-service DOMAIN=User \
  DRY_RUN=true

make scaffold-service \
  SERVICE=goalstats-user-service DOMAIN=User

cd backend/goalstats-user-service
git status --short
git diff
```

Resolve parent safety blockers first. Review untracked files using `git status`;
`git diff` alone does not display them. Scaffolding transforms identity only.
Item/Action remain examples; business-domain generation is outside this command.
Migration IDs, Up/Down operations, routes, DTO names and SQL tables remain unchanged.
Do not delete migrations as part of identity adaptation.

Commit and publish reviewed implementation on child master. Only
later integrate an approved published commit through a deliberate parent gitlink
update. Scaffolding never stages that pointer. The reference template remains
excluded from normal active runtime/testing.

Runtime requirements are Git, Bash, tar, and ordinary shell utilities, with GNU Make
3.81+ for the public interface, plus Python 3.9+ (standard library only). Missing or
unsupported Python fails before destination writes. No packages, Docker, Compose, or
network are required by scaffolding. macOS Bash 3.2 is the validation target; WSL is a candidate
with the same tools. Git Bash requires verified Make, filenames, and executable-bit
behavior. Native PowerShell and Windows are not certified.

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

### Safe master attachment

Owned repos use master only; RoadToTheFinal keeps its main exception. Setup/sync
still materialize approved commits, normally detached. No manual child branch
command is needed for the bootstrap sequence above.

Preview validates safe attachment and reports the planned action without changing
repository files, HEAD, refs, reflogs or index. Actual scaffold prepares and validates
all transformed output first, then attaches only the approved destination to existing
master using symbolic-ref. HEAD commit, refs, config/origin, index bytes, placeholder
bytes and parent gitlink must remain unchanged. Only symbolic HEAD and its normal
HEAD reflog entry may change. Attachment also permits exactly one local config
addition: absent `branch.master.vscode-merge-base` becomes a single `origin/master`
value. Existing values and every other config entry must remain unchanged.
Installation uses a verified post-attachment identity, including HEAD reflog state.

Scaffold remains offline: local origin/master is a consistency check, not a claim
about the live remote. Missing/mismatched refs, unexpected branches, dirty files,
operations or another worktree owning master refuse without automatic repair.
Attachment and post-attachment failures write no scaffold payload and do not reset
or detach again; inspect the reported state and private temporary diagnostic path.
Failure evidence is retained outside repositories; successful runs remove it.
Treat raw config evidence as private. Errors identify keys/categories, not values. The external scaffold lock covers
preparation, attachment and installation, but cannot prevent manual Git changes.
All existing parent cleanliness, placeholder and repeat-run guards remain active.


## Explicit scaffold recovery

Final verification requires every transformed payload file at its exact path, bytes
and mode. It permits additional directories/files only beneath `bin/` or `obj/`
directly inside a project root identified by a manifest-listed `.csproj`. These
artifacts are counted separately from payload. Symlinks, special files, unknown
extras (including ignored `.env` files), and non-project `bin/obj` refuse.

For an incomplete operation that reached final verification with all writes complete:

```bash
make recover-scaffold SERVICE=<approved-service> DOMAIN=<approved-domain> \
  OPERATION_PARENT=<original-sha> RECOVERY_TOOLING_SHA=<certified-sha> DRY_RUN=true
make recover-scaffold SERVICE=<approved-service> DOMAIN=<approved-domain> \
  OPERATION_PARENT=<original-sha> RECOVERY_TOOLING_SHA=<certified-sha>
```

Preview leaves the marker and evidence intact. Actual recovery independently
reconstructs the exact pinned template transformation, checks retained manifests,
mapping, completed writes and original placeholders, and applies the same payload
verifier. Supply the original operation SHA from the retained evidence and the exact
tooling SHA approved by the separate certification/publication task. A supplied SHA
is a binding to that external approval, not proof of certification by itself.

The original parent defines the operation; the current parent supplies the recovery
engine. The engine reads the original committed transformer and invokes only its
pure planning logic in memory. Original/current transformer bytes and mode must
match. No old installer or template code is executed, and no branch is switched.

The approved tooling SHA must equal HEAD, master and origin/master. Every intervening
commit must form a complete linear descendant chain and touch only these exact paths:

- `Makefile`, `README.md`
- `docs/DEVELOPMENT.md`, `docs/READINESS.md`, `docs/VALIDATION.md`
- `scripts/scaffold-service.sh`, `scripts/scaffold-verify.py`, `scripts/recover-scaffold.py`
- `tests/scaffold_service_test.py`

All child gitlinks, complete `.gitmodules`, both registries and the transformer remain
unchanged throughout that history. A prohibited change followed by a revert refuses.
Merge/shallow/replaced/grafted histories refuse. Parent source must match the approved
commit and its index must match the committed tree, with no staged changes. Historical
index bytes may differ; the current execution baseline is preserved instead. The
original HEAD reflog prefix must remain intact, and appended transitions must match
the approved commit chain. Existing unrelated refs/config remain strict. Historical
additions, removals and retargeting are allowed only for direct Codex turn-diff tree snapshot refs matching
these complete forms (lowercase hexadecimal hashes, decimal timestamps, canonical
lowercase UUIDs):

- `refs/codex/turn-diffs/checkpoints/<64-hex>/<64-hex>/<milliseconds>/<UUID>`
- `refs/codex/turn-diffs/captures/<milliseconds>/<UUID>/base`
- `refs/codex/turn-diffs/captures/<milliseconds>/<UUID>/head`

Every present snapshot must target a readable local tree directly: commits, blobs,
annotated tags, symbolic/dangling refs and malformed paths refuse. Snapshot trees
may represent uncommitted work and need not be reachable from committed history.
Removed historical snapshot objects need not survive garbage collection; recovery
never uses these snapshots to define the operation or reconstruct payload. Original
operation/template/transformer objects remain independently mandatory.

This permits the editor's historical snapshot lifecycle without rewriting retained
evidence. The complete current ref inventory, including snapshot refs and symbolic
targets, stays frozen throughout both verification passes. Concurrent ref changes
still refuse. Other Codex namespaces receive no exception, and unknown ref changes
remain errors. Publication refs keep their existing certified transition rules.

Recovery prints both parent SHAs and the compatibility checks. It never rewrites
historical snapshots to claim the operation happened under the newer tooling. The
command uses local Git objects only; publication/real-recovery certification checks
the live remote separately before invoking it.

After two successful verification passes, recovery atomically moves the specific
marker into `finalized-marker` inside the retained recovery directory. If that
archive cannot be performed atomically, recovery refuses without deleting the marker.
Recovery never recopies, overwrites, deletes build output, stages, commits, pushes,
or changes branches/pins. Failure preserves the marker and evidence. The resulting
child remains on master at its approved placeholder commit, with modified
README/.gitignore and untracked scaffold files ready for review. Ordinary scaffold
refuses both an incomplete operation and an already-generated destination.
