# Contributing

This is the shared contribution policy. Child repositories own their commands,
architecture, tests and debugging. The parent owns workspace mechanics and pins;
the Wiki owns product context, decisions and learning references.

## Issues and branches

| Repository | Issues belong here for |
| --- | --- |
| Parent | Workspace, setup/sync, orchestration, integration and shared workflow |
| User | Backend foundation, domain/API, migrations and tests |
| App | UI, API adapter, frontend tooling and tests |
| Wiki | Project documentation, navigation and product context |
| RoadToTheFinal | Necessary legacy/reference work only |
| Template | Demonstrated canonical defects only, with separate authorization |

Default branches remain `master` in owned repositories; RoadToTheFinal uses `main`.
Contributors use branches inside the repository they change:

```text
feat/<issue>-<summary>
fix/<issue>-<summary>
docs/<issue>-<summary>
chore/<issue>-<summary>
```

Use the owning issue number and a lowercase hyphenated summary. Start at the
parent-approved child commit unless the issue explicitly identifies another agreed
baseline. After setup, inspect status and create the branch before editing:

```bash
# Inside the intended, clean child at its approved pin; replace the example issue.
git status
git switch -c docs/123-clarify-setup
# Edit, verify, then review and stage only intended paths.
git diff
git add README.md
git diff --cached
git commit -m "docs: clarify setup"
git push -u origin docs/123-clarify-setup
```

Use descriptive commits; no Git Flow or elaborate commit convention is required.
Open the PR in that child against its default branch. Do not push directly to shared
default branches. Squash merge is the recommended simple default.

## Child PR and parent integration

**A child merge does not automatically update the approved workspace.**

1. Owning child issue → child branch → child PR.
2. Run relevant checks, obtain non-author review, then merge the child PR.
3. In a clean integration checkout, create a separate parent branch.
4. Select the published, reviewed child merge commit, preserving any unrelated work.
   With squash merging, use the resulting merged commit, not the old branch SHA.
5. Stage only the intended gitlink, for example `git add frontend/goal-stats-app`.
6. Review `git diff --cached --submodule=log` and verify the selected child combination.
7. Open a parent pin PR linking the child PR and verification evidence.
8. Integration review → parent merge. Other developers adopt it with clean-workspace sync.

Do not include unrelated child pins. The parent integration reviewer must check that
its current contract/tooling supports the selected child. User foundation adoption
and parent classifier/pin compatibility are separate coordinated tasks.

Parent-only work follows parent issue → parent branch → parent PR → review → merge.
It does not require a child pin update. For multi-repository work, one parent tracking
issue describes the integrated outcome/dependencies and links owning child issues,
child PRs and the final integration PR. Keep implementation details in the owning repo.

## Reviews and PRs

Routine changes need one non-author reviewer. The mid-level can review junior UI/docs
work; the senior need not approve every small edit.

Sensitive changes require senior involvement: migrations, authentication/security,
environment handling, Docker ownership, destructive tooling, transaction/cache behavior
and architecture. If the senior authors the work, an independent non-author review
is still required. Unresolved concerns must be addressed before merge.

Use this short PR description:

```text
Linked issue:
What changed:
How verified:
Screenshot, if meaningful UI changed:
Migration / API / configuration impact, if applicable:
```

## Tasks

| Size | Planning guide |
| --- | --- |
| Quick | Usually under two hours |
| Small | Roughly half a day to one day |
| Standard | Roughly one to three days |

Split larger work before assignment. These are guides, not deadlines or story points.
GitHub Issues in owning repositories are the assignment system; [first task drafts](FIRST_TASKS.md)
await authorized publication. [TODO](../TODO.md) remains a high-level roadmap.

Minimal issue body:

```text
Outcome / why:
Target repository / area:
Acceptance criteria, including verification:
Size:
Dependencies: none, or linked prerequisites
```

**Ready:** intended outcome, owning repository, observable acceptance criteria and
verification, explicit dependencies (or none), and a scope that does not hide unresolved
design decisions. Use the issue assignee field for ownership.

**Done:** acceptance criteria met; relevant tests and lint/type checks pass;
behavior/configuration docs updated where needed; schema changes include reviewed
migrations; PR reviewed; available required CI checks green. A child issue can finish
at its stated child acceptance boundary. Cross-repo trackers remain open until their
integration criteria are satisfied.

## Bugs and safety

Report in the repository owning the failing command/content. Parent may triage when
ownership is unclear. Use:

```text
Type: setup / application / docs / tooling
Repository / commit:
Command or action:
Expected:
Actual:
Environment / relevant tool versions:
Short redacted error:
Blocks progress? Workaround?
```

Never attach credentials or complete env files. Commit intended source/docs/lockfiles,
not private env files, generated caches or machine-specific IDE state. Review status,
working diff and staged diff. Do not force-push shared default branches, use destructive
Git cleanup to recover setup, globally prune Docker resources or delete database
volumes to fix configuration. Do not delete operation journals to bypass safety.
Sync is not a dirty-work recovery command; preserve work and follow
[workspace troubleshooting](DEVELOPMENT.md#troubleshooting).

## GitHub settings: owner verification

Unverified settings remain **UNKNOWN**. During handoff implementation, GitHub reported
parent `master` as unprotected, no applicable branch rules/rulesets, and squash merging
available. These observations do not establish teammate permissions or child protection
and do not replace this PR policy. The owner should verify/configure parent and active
child default branches for:

- PR requirement and at least one non-author approval of the final changes.
- Required checks that actually exist; do not require nonexistent workflows.
- Force-push and branch-deletion restrictions, including bypass permissions.
- Team branch, issue and PR permissions.
- Squash merge availability.

No parent CI workflow is currently tracked. Run parent tooling checks manually as
[documented](DEVELOPMENT.md#parent-tooling-verification). App CI is a first task;
child workflows and runtime prerequisites remain child-owned.
