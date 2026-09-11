# Development-box contract

## Ownership

Children own Dockerfiles, development/build/runtime commands, migration logic, and
normal tests. The box owns the active registry, Compose project/network, host ports,
combined configuration, lifecycle, aggregate logs, and stack-level smoke.

No child standalone make run is called by the box. Each ENV has one project:
team-squared-local or team-squared-dev. Optional PROJECT overrides must begin with
the corresponding name plus a dash. Stop/logs can still operate on that owned
project when a child contract becomes unavailable, so diagnosis/cleanup stays possible.

## Setup and submodules

Setup checks Git/Docker/Compose/GNU Make and creates only missing parent env files.
It starts no stack. It then inspects ALL configured submodules before any checkout
operation, including references and dirty nested submodules visible through status.

- HEAD must contain .gitmodules and a committed gitlink for every configured child.
- Working .gitmodules and index pins must agree with HEAD; staged-only replacements
  fail rather than becoming hidden new defaults.
- Dirty initialized children produce an explicit warning and nonzero result. No
  child is checked out or overwritten; commit/stash intentionally outside setup.
- Clean initialized children and missing children are synchronized/initialized at
  the pinned commits with git submodule update --init --recursive --checkout.
- Detached HEAD at a pin is normal. A clean checkout may move back to its recorded
  pin; existing branch references are not deleted. Create a branch before editing.
- Setup never pulls latest branches, forces checkout, stages, commits, or advances
  parent gitlinks. Publish child commits before recording them in the parent.

The existing parent has no committed gitlinks, so successful initialization at
committed pins cannot yet be demonstrated. See READINESS.md.

Child setup is not delegated: the established container contracts prepare tooling
while building, and standalone child env files are unnecessary for this box.
Once real active contracts exist, setup validates them instead of creating unused
standalone configuration. Child files and independent workflows remain untouched.

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
References are excluded, and no successful partial test suite is reported.

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
