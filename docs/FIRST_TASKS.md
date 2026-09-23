# First four task drafts

**DRAFTS ONLY — no GitHub Issues have been created by this handoff.** These are
assignment-ready definitions, not permission to implement them in the parent change.
When issue creation is authorized and access is verified, publish in each owning
repository, assign the developer and replace draft bodies here with issue links and
a short ownership table. Do not maintain duplicate backlogs. The parent roadmap item
remains unchecked pending Prompt 2's independent acceptance.

## Junior #1 — Honest GoalStats landing page

- **Owning repository:** `goal-stats-app`
- **Size:** Small
- **Outcome:** Replace create-next-app guidance with an honest project landing page.
- **Acceptance criteria:**
  - Identify GoalStats as a football analytics/prediction project and the current UI as a development foundation.
  - Remove starter deployment/tutorial calls to action without inventing login, backend connectivity or finished product features.
  - Preserve accessible headings/navigation and responsive presentation.
  - Update existing page tests for the new content.
  - Run unit tests, lint, typecheck and build; provide a screenshot.
- **Dependencies:** App access and successful standalone setup; agree brief product copy with the reviewer before editing.
- **Reviewer:** Mid-level.

## Junior #2 — Wiki navigation and onboarding observations

- **Owning repository:** `goal-stats-wiki`
- **Size:** Small
- **Outcome:** New contributors can navigate to accurate, authoritative instructions.
- **Acceptance criteria:**
  - Correct obsolete repository names and current technology descriptions.
  - Distinguish frozen Template, older User scaffold, App demo and legacy reference.
  - Link parent onboarding and child setup/testing guides instead of duplicating commands.
  - Label historical meeting plans; do not rewrite past decisions as current facts.
  - Follow the approved onboarding route and report reproducible friction in the owning repository using the shared bug format.
  - Do not publish or remove existing untracked contributor material without owner direction.
  - Verify links and include the onboarding observations in the PR.
- **Dependencies:** Published parent handoff guidance, Wiki access and the selected child prerequisites.
- **Reviewer:** Mid-level; senior verifies runtime claims.

## Mid-level — Baseline App pull-request checks

- **Owning repository:** `goal-stats-app`
- **Size:** Small
- **Outcome:** Frontend PRs receive automated feedback using existing commands.
- **Acceptance criteria:**
  - Install from `package-lock.json` with compatible Node tooling and `npm ci`.
  - Run existing lint, typecheck, unit-test and build commands on PRs and the default branch.
  - Require no backend, private credentials or full-stack runtime.
  - Report failures clearly and verify the workflow on its PR.
  - Leave full-stack/browser integration expansion outside this task.
- **Dependencies:** Workflow permissions and package/font download access; no User adoption or parent runtime dependency.
- **Reviewer:** Senior.

## Senior — Adopt the frozen User foundation

- **Owning repository:** `goalstats-user-service`
- **Size:** Standard; split before assignment if the reviewed scope exceeds three days.
- **Outcome:** User develops against the frozen foundation while preserving service state and public behavior.
- **Acceptance criteria:**
  - Use exactly Template `6600facf42ecf9a3431b44f5d19ff2ac2a3b0b07`.
  - Preserve repository identity/history, User service/database/cache identity, port configuration, private credentials, existing data and migration history.
  - Replace obsolete foundation files through a reviewed normal commit; do not reset volumes or replace migrations without demonstrated schema need.
  - Verify relevant setup, quality, unit/integration tests, migration parity and public API behavior with the adopted certification tooling.
  - Record provenance and publish through a reviewed User PR.
  - Do not modify Template or use the incompatible parent generator.
  - Keep parent classifier compatibility, gitlink adoption and runtime integration in separately owned follow-up work; do not change parent pins in the User PR.
- **Dependencies:** User access, exact frozen source and reviewed preservation/verification checklist. Establish data/configuration preservation requirements before file replacement.
- **Reviewer:** Mid-level for independent non-author review; resolve sensitive concerns before merge.
