# GoalStats development workspace

GoalStats is a football analytics and prediction project. `team-squared-dev` is its
workspace/integration repository: clone once, work in independent child repositories,
and integrate reviewed changes through approved child commit pins.

## Repository map

| Repository | Role |
| --- | --- |
| This parent | Workspace setup/sync, approved pins, shared workflow and orchestration |
| [Template](backend/template-goalstats-service/README.md) | Frozen canonical backend reference; no product features |
| [User](backend/goalstats-user-service/README.md) | Active backend repository on an older Item/Action scaffold; frozen-foundation adoption is upcoming. User/auth is not yet implemented |
| [App](frontend/goal-stats-app/README.md) | Next.js development/demo foundation; standalone UI work can begin before full-stack integration |
| [Wiki](docs/goal-stats-wiki/README.md) | Project context, decisions and learning material; operational instructions belong to the owning repository |
| [RoadToTheFinal](frontend/RoadToTheFinal/README.txt) | Legacy football/product behavior and data reference; neither active runtime nor canonical architecture |

Template is frozen at `6600facf42ecf9a3431b44f5d19ff2ac2a3b0b07`.
Product features do not go there. Template changes require a demonstrated canonical
defect and separate authorization.

## Day 1: initialize the workspace

Install Git, GNU Make 3.81+, Bash (3.2+ supported), OpenSSH and normal shell utilities.
Configure GitHub SSH authentication and access to the parent and **all five** children
in [.gitmodules](.gitmodules), including Wiki and RoadToTheFinal. Successful SSH
account authentication does not prove access to each repository. If initialization
fails, identify the specific inaccessible child and ask its owner to verify access.

```bash
git clone git@github.com:WestiferRobin/team-squared-dev.git
cd team-squared-dev
make setup
git submodule status
```

Parent setup initializes approved repository pins and private parent configuration.
It does **not** install every child's dependencies, start providers, migrate databases
or run applications. It needs no Docker or host Node. Detached child HEADs at approved
pins are normal; create a child feature branch before editing.

## Choose your child

- **Frontend:** open `frontend/goal-stats-app` and follow its [setup](frontend/goal-stats-app/README.md),
  [development](frontend/goal-stats-app/docs/DEVELOPMENT.md) and
  [testing](frontend/goal-stats-app/docs/TESTING.md) guides. It runs independently of User.
- **Backend:** open `backend/goalstats-user-service` and follow its current
  [setup](backend/goalstats-user-service/README.md),
  [development](backend/goalstats-user-service/docs/service/development.md) and
  [testing](backend/goalstats-user-service/docs/testing/overview.md) guides.
  Do not substitute Template instructions: User has not adopted the frozen foundation.

Use the child as the IDE root for its repository-specific launch settings. Child
setup/checks require the prerequisites in that child's guide. LOCAL and DEV are local
runtime modes, not remote deployment. Windows is not certified; WSL is a candidate
requiring team verification, not a promised supported path.

## Parent command status

| Command | Today |
| --- | --- |
| `make help` | Show workspace scope and command limitations |
| `make setup` | Prepare the current checkout; preserve work by refusing unsafe state |
| `make sync` | Fast-forward clean parent `master` and adopt approved pins; not a feature-branch update command |
| `make test` | Validate active backend structure, then delegate App/User normal suites with App E2E disabled; requires child prerequisites |
| `make build`, `make migrate`, `make run`, `make smoke` | **Blocked:** parent backend runtime composition is incomplete |
| `make stop`, `make logs` | Selected parent Compose project only; do not control standalone child projects |
| `make scaffold-service ...` | **Not onboarding:** generator targets an older foundation; repair before generating another service |

Do not scaffold over existing User or bypass full-stack guards. Root `make test`
is not the parent tooling-test command. See [current readiness](docs/READINESS.md).

## Contribute

Read [Contributing](docs/CONTRIBUTING.md) for branches, PRs, reviews, task ownership,
Ready/Done and bug reports. Start with [four task drafts](docs/FIRST_TASKS.md);
these are not yet GitHub Issues. [TODO](TODO.md) is a high-level roadmap only.

**A child merge does not automatically update the approved workspace.** A separate
reviewed parent pin PR adopts its published commit.

Use `make sync` only from a clean integration workspace. Preserve dirty/off-pin work;
finish its branch/PR or use a separate clean integration checkout. Read
[Development](docs/DEVELOPMENT.md) for sync mechanics and troubleshooting.
[Validation](docs/VALIDATION.md) contains historical evidence, not current runtime certification.
