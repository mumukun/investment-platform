---
name: change-manager
description: Group feedback within one Investment Platform conversation and delivery round into one default Change, maintain scope and acceptance items, determine affected repositories and dependencies, reuse Change-ID branches, and report implementation versus release readiness. Use for starting, planning, updating, or completing governed work; do not use for production release execution.
---

# Change Manager

Default to one requirement and one active Change per conversation and delivery round. Keep additional
feedback as scope and acceptance items without scanning or modifying unrelated repositories.

## Authority and inputs

Read `AGENTS.md`, `SYSTEM_MAP.yaml`, and `changes/TEMPLATE.md`. If the Change already exists, read
`changes/<CHANGE_ID>.md` first and continue it instead of allocating another ID. Repository-specific build,
test, runtime, database, and deployment commands still come from the affected repository's `AGENTS.md`.

## Create or continue a Change

1. Identify the conversation's existing Change first. Fold subsequent page/module adjustments and fixes
   into its scope and acceptance items; different pages, feedback turns, commits or delivery stages alone
   do not justify new Changes, branches or PRs. State the combined scope briefly without adding approval steps.
2. Split only for an explicit independent-delivery request or a concrete boundary that cannot be delivered
   safely together, including data-risk handling. Separate acceptance items/tests alone do not justify a split.
   Record the reason briefly in the existing Change. Grouping never expands authorization.
   After release, group additional changes into the next delivery round: when development starts, create
   one new Change linked to the prior round, preserving released records/Tags. Start ordinary work from
   current main; route urgent production fixes to hotfix-manager. Subsequent feedback belongs to that new
   round. Questions, discussion, retrospectives and read-only investigation alone create no Change.
3. Only when a new Change is warranted, inspect existing `changes/CHG-YYYYMMDD-*.md` names and allocate
   the next unused three-digit sequence for the current date. Create it from `changes/TEMPLATE.md`.
4. Read `SYSTEM_MAP.yaml`, then inspect only the likely affected repositories and relevant modules. Do not
   default to all repositories.
5. Use the compact template: scope and acceptance items, repository/branch/PR identity, required test
   links, release impact and rollback. Add dependency/API/database/contract or Feature Flag detail only when affected; omit
   unchanged None sections and copied logs. Mark uncertain relationships explicitly.
6. When development is authorized, use one task branch per actually affected repository with the same Change ID:
   `feat/<CHANGE_ID>-description`, `fix/<CHANGE_ID>-description`, or `hotfix/<CHANGE_ID>-description`.
   Reuse that Change's existing safe branch/worktree first. Do not create extra branches for versions,
   READY, release preparation or archival. Preserve unrelated work and use isolated worktrees when required.
7. Keep Branches, PRs, tests, commits, decisions, and evidence current as work progresses. Multiple logical
   commits may belong to one Change and PR; they do not require separate requirement records.

## Report completion and READY separately

Before completion, apply the repository's existing checks and platform `docs/development-validation.md`:
verify functional outcomes, affected integration boundaries, and performance when queries, batch size,
collection, scheduling, concurrency or an explicit performance goal changes. Record commands/CI links,
actual workload and results in the existing Change/PR. A green CI or test count alone does not establish
acceptance. Report required skipped/unrun checks honestly. Do not create another report, approval or
release-time testing phase; simple copy/style/docs changes stay proportionate.

Only mark a Change `READY` when the requested implementation and documentation are complete, required repository
and affected cross-repository tests passed, PRs merged to `main`, and release and rollback impact is recorded.
Safe temporary branch cleanup may be deferred and recorded; it does not block READY or routine deployment.
After business PRs merge and required checks pass, record READY locally without a separate governance PR/CI
wait. Batch record commits at closeout; only committed records are shared facts. Include version/changelog
changes in the feature PR instead of creating another preparation PR. Do not start another full review or
test phase after submission unless conflicts, new changes or failed evidence require it.
Report implementation and required validation complete as REVIEW even when not submitted/merged yet.
Always distinguish local changes, committed, merged/READY, and actually RELEASED; do not call an unmerged
change READY. Reuse already granted authorization; do not ask again just because the phase changed.

Do not create release Tags, deploy Production, activate features, or mark a Release successful. Commit, push,
PR, merge, and branch deletion remain separately governed actions and require the user's current authorization.
