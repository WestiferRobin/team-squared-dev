# Current workspace readiness

This is the current capability snapshot, not a runtime certification report.
Gitlinks are the authoritative approved commits; inspect them with `git submodule status`.

| Component | Approved pin | State |
| --- | --- | --- |
| Template | `6600facf42ecf9a3431b44f5d19ff2ac2a3b0b07` | Frozen canonical reference; no product work |
| User | `a4dc2f5e2bae6f1e7634dccce6a828e8a4c10d19` | Older Item/Action scaffold with standalone guides; frozen-foundation adoption upcoming; no User/auth domain |
| App | `d7e77e711b4286481a35ffb3a98c8b2892ffe8cf` | Next.js demo/development foundation; standalone UI work available |
| Wiki | `1f7ce88c2dce44548b321707e138c1be8ecbf111` | Project context/learning documentation; navigation corrections are a first task |
| RoadToTheFinal | `4c77197e209292f70ae788e6d4539bb89189e963` | Legacy football/product reference, excluded from active runtime |

## Available now

- Parent setup initializes exact pins and parent configuration without Docker.
- Clean parent-master sync adopts approved integration commits; it is not feature-branch maintenance.
- App and current User have independent setup/run/test guides linked from [README](../README.md).
- Root `make test` structurally checks backends and delegates active child suites, with App E2E off.
  It requires child prerequisites and is not the parent tooling suite.

## Explicit limitations

- Parent full-stack composition is **runtime-pending**: User registry migration/readiness/health/smoke
  fields are pending and Compose contains only frontend. Root build/migrate/run/smoke remain blocked.
- Generator and structural classifier retain older foundation assumptions. Do not generate another
  service before generator repair or adopt a new User pin without compatible parent checks.
- Scaffolding existing User is not onboarding. Foundation adoption is separate User work.
- No tracked parent CI; App CI is a first task. Parent master was reported unprotected during handoff verification; child protection and team permissions remain UNKNOWN.
- Windows and fresh-team-machine runtime success are not certified by this handoff.
- [Historical validation](VALIDATION.md) is evidence for its recorded commits only.

## Next work and acceptance

The parent handoff defines workflow and [four task drafts](FIRST_TASKS.md), not created
GitHub Issues. User adoption, classifier/pin coordination, runtime integration and
scaffold repair remain separate tasks. No child commit is changed by this handoff.
The parent roadmap item remains unchecked: Prompt 2 owns independent final acceptance.
