# Workspace development

## Ownership and standalone work

Children own application dependencies, Dockerfiles, runtime commands, migrations,
tests and debugging. Parent owns gitlinks, workspace setup/sync, parent configuration
and eventual full-stack composition. Wiki owns project context and learning material.

Today, follow the [App guide](../frontend/goal-stats-app/docs/DEVELOPMENT.md) or
[current User guide](../backend/goalstats-user-service/docs/service/development.md)
for standalone development. Open the intended child as the IDE root; opening only
the parent does not activate a child's repository-specific debug configuration.
Use [Contributing](CONTRIBUTING.md) for all branches, PRs, reviews and tasks.

## Initialization and synchronization

[README](../README.md#day-1-initialize-the-workspace) contains the clone sequence.
`make setup` prepares the current committed parent, including a feature branch or
detached commit, and initializes all five children at exact gitlink SHAs. It never
pulls/moves parent HEAD or runs child setup. It prepares private `infra/.env.local`.
Git/Make/Bash/SSH and access to all required repositories are needed; Docker is not.

`make sync` is for a **clean integration workspace on parent master**. It fetches
`origin/master`, refuses locally ahead/divergent history, fast-forwards only and adopts
that parent's exact approved pins. It does not modify env files, update child feature
branches or select latest child remote heads. A child feature branch clean at the pin
can pass checks; branch names alone are not the safety criterion. When a new pin is
selected, detached child HEAD is normal and existing branch refs remain.

Both operations inspect parent and initialized children recursively. Tracked changes,
nonignored untracked files, staged gitlinks, in-progress Git operations and clean
off-pin child commits cause refusal. Missing child directories must be empty; unsafe
paths and collisions are refused. Ignored files are permitted only when incoming
tracked content would not replace them. No automatic stash, reset, cleanup or staging
is performed. Do not run concurrent Git edits during setup/sync.

Canonical URLs come from committed `.gitmodules`. Successful SSH authentication alone
does not prove access to each child. Git's failing URL identifies the repository whose
access/download must be resolved. Already initialized offline setup need not probe GitHub.

Preserve dirty/off-pin work, continue/finish its branch and PR, or use a separate clean
integration checkout. Do not use sync to update a feature branch. Parent pin adoption
is the separate reviewed process in [Contributing](CONTRIBUTING.md#child-pr-and-parent-integration).

Sync is not atomic. If parent advances and a child download fails, a journal under
parent Git administration records the target/prior child SHAs. Resolve the reported
failure and retry `make sync`; it finishes the recorded target before fetching a later
one. Preserve the journal. `setup` asks you to finish an interrupted sync first.
Incoming removal/rename of an occupied submodule requires deliberate reconciliation.

Read-only pin inspection:

```bash
git submodule status --recursive
bash scripts/workspace.sh status
```

## Parent configuration and runtime boundary

Parent owns ignored `infra/.env.local`, with `LOCAL_FRONTEND_PORT` and
`DEV_FRONTEND_PORT`; defaults are in `scripts/infra-config.sh`. Setup preserves valid
existing configuration and backs up legacy port configuration during migration.
DEV is a runtime mode, not a second required env file. Parent does not copy or source
child dotenv files. Keep private configuration out of commits and browser-visible values.

| Parent mode | Frontend port | Compose project |
| --- | --- | --- |
| LOCAL | 33000 | team-squared-local |
| DEV | 33001 | team-squared-dev |

These are incomplete parent composition settings, not standalone child URLs. Child
ports/configuration are documented by each child. Parent backend/provider ports and
credentials remain unassigned pending a separate integration task.

**Parent full-stack runtime-pending:** root `make build`, `make migrate`, `make run`
and `make smoke` are blocked because the registry/backend Compose contract is incomplete.
Both Compose files currently define only frontend. Do not bypass completeness guards
with raw Compose and claim a working full stack. Standalone child work is available.

Parent `make stop` and `make logs` target only the selected parent project, even when
active contracts are unavailable. Stop preserves volumes. They do not stop/log standalone
child projects. `ENV` defaults to local; supported modes are local/dev. `PROJECT`
overrides must use the corresponding parent namespace. Interrupting logs does not stop it.

## Test boundaries

Root `make test` validates active Python service structure and the presence of all
active child Makefiles, then delegates App/User normal suites serially with App
`E2E=false`. It clears parent Make/environment overrides. A failure stops later suites
and remains nonzero. It needs child prerequisites but not a running parent box or
complete parent Compose definitions. References and docs are excluded.

It is **not** the parent tooling-test command. Child tests may create disposable
runtime resources; consult child docs. App browser tests remain App-owned.

The current backend classifier checks the older scaffold structure, not parity with
the frozen Template. Updating it alongside future User pin adoption is separate work.
The parent's prepared smoke probe checks internal transport/readiness, not a browser
feature flow; no connected-stack verification is claimed here.

## Scaffolding: deferred

Service scaffolding is not part of normal onboarding. The current generator targets
an older foundation and must be repaired before another service is generated. Do not
scaffold over the existing User service. No scaffolder/classifier repair is included
in this handoff. Old SHA constants, identity allowlists and frozen fixture patches are
historical tooling inputs, not today's canonical foundation declaration.

Template remains frozen at `6600facf42ecf9a3431b44f5d19ff2ac2a3b0b07`; product work
belongs in active children. Changes require a demonstrated canonical defect and
separate authorization. [Validation](VALIDATION.md) preserves historical evidence;
it is not an onboarding command sequence or current compatibility certification.

## Parent tooling verification

With Python 3.12 and the initialized repositories:

```bash
make help
bash -n scripts/workspace.sh scripts/git-safety.sh scripts/infra-config.sh scripts/box.sh scripts/scaffold-service.sh
PYTHONDONTWRITEBYTECODE=1 python3.12 -B -m unittest discover -s tests -p '*_test.py'
git diff --check
```

The tests create Git histories/files only in disposable fixtures and need no Docker.
Scaffold fixtures read historical Template objects (`720260c...`) and a frozen IDE
patch; passing them does not certify generation from `6600fac...`. Do not change
fixtures/old SHAs merely to clean up documentation. Parent CI is not currently tracked.

## Troubleshooting

| Symptom | Next step |
| --- | --- |
| SSH failure / inaccessible repository | Check account authentication, then access to the exact URL reported; references/docs also need access |
| Dirty parent or child refusal | Review status/diff, preserve work and continue its branch; no destructive cleanup |
| Clean off-pin child / feature work | Preserve commits on a named branch; finish its PR/integration or use a separate clean checkout |
| Interrupted sync | Resolve the reported failure and retry sync; preserve the recovery journal |
| Port occupied | Follow the owning child's documented override; do not kill unrelated processes or change parent ports expecting to affect standalone children |
| Existing DB volume but missing credentials | Restore the original private configuration; changing a password does not rotate stored DB credentials. Do not delete volumes |
| IDE launch missing or wrong interpreter | Open the child root and follow its own interpreter/setup guide; current User host dependencies need its documented installation |
| Parent runtime-pending | Use standalone App/User workflows; root runtime integration is a later task |

Report reproducible failures using the [bug format](CONTRIBUTING.md#bugs-and-safety).
Expand this section from actual onboarding questions, not hypothetical failures.
