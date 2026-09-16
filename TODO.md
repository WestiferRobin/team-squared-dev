# Team Squared TODO

NOTE: Wes is using to keep track.

WE NEED TO REPLACE .NET!
  - We need to extract logic into python

## OLD WORK BEFORE FLASK REFACTOR
- [x] **template-goalstats-service**
  - [x] establish `GoalStats.Template.*` naming
  - [x] use `TemplateDbContext`
  - [x] preserve Item / Action example domains
  - [x] align test architecture
    - [x] unit tests follow logic
    - [x] integration tests follow boundaries
    - [x] controllers are integration-tested
    - [x] smoke tests follow built system
  - [x] certify LOCAL / DEV / EF / smoke / workflows
  - [x] publish certified template

- [x] **team-squared-dev scaffolding**
  - [x] canonical submodule workspace
  - [x] safe `make scaffold-service`
  - [x] DOMAIN-aware scaffolding
  - [x] interface:
    - [x] `make scaffold-service SERVICE=goalstats-user-service DOMAIN=User`
  - [x] transform:
    - [x] `GoalStats.Template.* -> GoalStats.User.*`
    - [x] `TemplateDbContext -> UserDbContext`
    - [x] `goalstats-template -> goalstats-user`
    - [x] `goalstats_template -> goalstats_user`
  - [x] preserve destination Git identity
  - [x] dry-run support
  - [x] scaffold safety tests
  - [x] test-aligned template pin adopted
  - [x] disposable `GoalStats.User` scaffold certified
  - [x] generated User skeleton passes build / EF / tests / LOCAL / DEV / smoke


## TODOS AFTER FLASK REFACTOR

- [ ] **goalstats-user-service**
  - [ ] create `feat/architecture-prototype`
  - [ ] run real scaffold dry run
  - [ ] scaffold real service with:
        `make scaffold-service SERVICE=goalstats-user-service DOMAIN=User`
  - [ ] inspect generated `GoalStats.User.*` skeleton

  - [ ] implement User domain
    - [ ] User model
    - [ ] register
    - [ ] login
    - [ ] get user by ID
    - [ ] password hashing
    - [ ] duplicate username -> 409
    - [ ] invalid credentials -> 401

  - [ ] establish `User -> Items -> Actions`
    - [ ] User owns Items
    - [ ] Item owns Actions
    - [ ] Item CRUD
    - [ ] Action CRUD

  - [ ] PostgreSQL persistence
  - [ ] Redis cache behavior for Item / Action
  - [ ] replace template/example migration with fresh concrete migration if required by User-domain schema work
  - [ ] Swagger / OpenAPI
  - [ ] `/health`
  - [ ] `/ready`

  - [ ] testing
    - [ ] unit tests for logic
    - [ ] integration tests for boundaries
    - [ ] controllers integration-only
    - [ ] smoke / workflow validation

  - [ ] validate:
    - [ ] `make setup`
    - [ ] `make build`
    - [ ] `make migrate`
    - [ ] `make run`
    - [ ] `make stop`
    - [ ] `make logs`
    - [ ] `make unit`
    - [ ] `make integration`
    - [ ] `make test`
    - [ ] LOCAL
    - [ ] DEV

  - [ ] commit / push

- [ ] **goal-stats-app**
  - [ ] establish frontend architecture and lock it
  - [ ] define API client / proxy architecture
  - [ ] define demo login state

  - [ ] testing
    - [ ] unit/component tests: `*.test.ts | *.test.tsx`
    - [ ] E2E tests: `tests/e2e`
    - [ ] `make test E2E=false`
    - [ ] `make test E2E=true`

  - [ ] implement `feature/<domain>/views`
    - [ ] auth
      - [ ] register
      - [ ] login
    - [ ] home
      - [ ] list Items
      - [ ] create Item
      - [ ] select/open Item
      - [ ] add Actions to Item
      - [ ] edit/delete Item
      - [ ] edit/delete Action
    - [ ] loading / empty / error states

  - [ ] configure `USER_SERVICE_BASE_URL`
  - [ ] LOCAL container validation
  - [ ] DEV container validation

- [ ] **team-squared-dev finalization**
  - [ ] update active submodule pins
    - [ ] goalstats-user-service
    - [ ] goal-stats-app

  - [ ] add real user-service runtime contract
    - [ ] user-service Compose definition
    - [ ] PostgreSQL wiring
    - [ ] Redis wiring
    - [ ] frontend -> user-service networking
    - [ ] migration delegation
    - [ ] readiness / health checks

  - [ ] full-stack validation
    - [ ] all services run on LOCAL
    - [ ] all services run on DEV
    - [ ] app runs on LOCAL
    - [ ] app runs on DEV
    - [ ] all child tests from one dev command
    - [ ] full-stack smoke command

  - [ ] Docker validation
    - [ ] backend accessible from Swagger
    - [ ] backend accessible from Postman
    - [ ] frontend talks to backend
    - [ ] persistence survives restart
    - [ ] logs usable
    - [ ] stop preserves data

  - [ ] fresh clone validation
    - [ ] `make setup`
    - [ ] `make migrate`
    - [ ] `make run`
    - [ ] `make test`
    - [ ] `make smoke`
    - [ ] `make stop`

- [ ] **documentation / goal-stats-wiki**
  - [ ] architecture diagram
  - [ ] repo responsibilities
  - [ ] LOCAL vs DEV
  - [ ] beginner setup walkthrough
  - [ ] scaffolding workflow
  - [ ] test architecture
  - [ ] register/login demo walkthrough
  - [ ] Item/Action demo walkthrough
  - [ ] known prototype limitations
  - [ ] explicitly state auth is demo-only
  - [ ] record template provenance