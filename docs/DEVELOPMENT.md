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
reset, cleaned, staged, or discarded. The existing untracked parent `TODO.md` is
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
git switch -c feat/architecture-prototype
# edit/test using the child's available tools
# review changes before staging
git add .
git commit -m "Implement architecture prototype"
git push -u origin feat/architecture-prototype
```

The same independent-repository workflow applies to `frontend/goal-stats-app` and
`docs/goal-stats-wiki`: enter the child, create a feature branch, edit/test, and
commit/publish there. App standalone manual runtime verification remains pending.
Wiki edits do not change the parent pin until an approved wiki commit is integrated.

For the upcoming user-service bootstrap, the tracked template source is
`backend/template-goalstats-service` at `e89164842ca2c0f2954919a38da3ed4924d5f3ac`;
the destination remains `backend/goalstats-user-service` at
`70c77c692993fc18e9f484bf22266a15288c0541`. Create the destination feature branch
before a later tracked export and implementation. Pin adoption performs neither.
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

The parent owns one bootstrap command:

```bash
make scaffold-service SERVICE=goalstats-user-service
make scaffold-service SERVICE=goalstats-user-service DRY_RUN=true
```

SERVICE is required. DRY_RUN defaults to false and accepts exactly `true` or `false`;
an explicitly empty value is invalid. There are no force, confirmation, source, or
destination overrides. The helper exits 0 on success, 2 on validation/safety refusal,
and 1 on operational failure; GNU Make reports its own nonzero recipe-failure code.

The two-column `config/scaffolds.tsv` explicitly approves a service and placeholder
commit. Committed component metadata supplies its active backend role, and committed
`.gitmodules` supplies the canonical URL. The source is always the current parent's
exact `backend/template-goalstats-service` gitlink. No latest branch selection, fetch,
setup, or sync is performed. Setup must already have initialized the repositories.

Only the parent, template, and destination receive relevant safety checks. Unrelated
child dirty/off-pin state is allowed, but parent staged gitlink changes are refused.
The source and destination must be clean and at their pins, with canonical origins
and no in-progress Git operations. Destination HEAD must also match its approved
placeholder SHA and an existing `feat/<nonempty-name>` branch. No branch is created.
Parent staged/unstaged/untracked work, including TODO.md, causes refusal. Preserve
and resolve that work deliberately; the command never moves/deletes/ignores it.

The destination must contain exactly approved regular README.md and .gitignore
files, matching committed blob bytes and modes, with no untracked or ignored files.
README is replaced by the template README. Ignore compatibility is conservative:
identical rule lists pass; otherwise destination positive rules must remain in
order, destination negations are refused, and new template negations are limited
to `!.env.example` when it does not undo a destination exclusion. Comments and empty
lines do not affect comparison. Custom rules requiring reconciliation cause refusal.
The template ignore file is copied byte-for-byte; there is no automatic merge.

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
source/destination identities and additions/replacements, and changes no repository
files, refs, index, or configuration. It is a preview, not a reservation: actual
installation revalidates the repositories and feature branch before writing.

A workspace-exclusive empty lock directory lives under `/tmp`, independent of TMPDIR.
If it exists, the command reports its exact path and refuses. Check that no scaffold
is running before manually removing a stale empty lock. No daemon is involved.

Before installing, the helper stores original placeholders and Git identity
snapshots in private temporary storage. It installs only manifest-listed files,
then verifies payload and preserved Git identity. `.git`, origin, refs, HEAD, branch,
and indexes remain unchanged; no stage, commit, push, or parent pin update occurs.
The parent displays dirty child content; the child contains modified placeholders
and untracked new source files. This is expected. Do not run setup/sync to discard it.

Installation is not atomic. Pre-install failures clean up owned temporary files
without changing the destination. Once installation starts, a failure preserves a
recovery directory containing original placeholders, manifest, and completed.txt,
and records its path in the parent's Git directory under
`team-squared-scaffold-incomplete`. The error identifies the failed path/phase.
Inspect and preserve the resulting work; reconcile deliberately before removing the
indicator. Do not blindly rerun, reset, or clean. The command performs no automatic
rollback, and a repeat invocation refuses dirty or already-committed scaffolds.

Beginner workflow for an approved scaffolding task:

```bash
make setup

git -C backend/goalstats-user-service \
  switch -c feat/architecture-prototype

make scaffold-service \
  SERVICE=goalstats-user-service \
  DRY_RUN=true

make scaffold-service \
  SERVICE=goalstats-user-service

cd backend/goalstats-user-service
git status --short
git diff
```

Resolve parent safety blockers first. Review untracked files using `git status`;
`git diff` alone does not display them. Subsequent implementation renames/adapts the
template to GoalStats.UserService, removes copied migration artifacts, and preserves
Item/Action until later domain prompts. Scaffolding itself leaves all template
identity, migrations, Item/Action, source, and tests unchanged.

Commit and publish reviewed implementation inside the child feature branch. Only
later integrate an approved published commit through a deliberate parent gitlink
update. Scaffolding never stages that pointer. The reference template remains
excluded from normal active runtime/testing.

Runtime requirements are Git, Bash, tar, and ordinary shell utilities, with GNU Make
3.81+ for the public interface. No Python, rsync, Docker, Compose, or network is
required by scaffolding. macOS Bash 3.2 is the validation target; WSL is a candidate
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
