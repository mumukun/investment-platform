---
name: change-manager
description: Create and maintain Investment Platform Change records, determine affected repositories and dependencies, create Change-ID branches, and confirm readiness. Use for starting, planning, updating, or completing a governed feature or fix; do not use for production release execution.
---

# Change Manager

Manage one business requirement as one durable Change without scanning or modifying unrelated repositories.

## Authority and inputs

Read `AGENTS.md`, `SYSTEM_MAP.yaml`, and `changes/TEMPLATE.md`. If the Change already exists, read
`changes/<CHANGE_ID>.md` first and continue it instead of allocating another ID. Repository-specific build,
test, runtime, database, and deployment commands still come from the affected repository's `AGENTS.md`.

## Create or continue a Change

1. Confirm the request, outcome, non-goals, acceptance criteria, and whether an existing Change ID was supplied.
2. For a new Change, inspect only existing `changes/CHG-YYYYMMDD-*.md` names and allocate the next unused
   three-digit sequence for the current date. Create `changes/<CHANGE_ID>.md` from the template.
3. Read `SYSTEM_MAP.yaml`, then inspect only the likely affected repositories and relevant modules. Do not
   default to all repositories.
4. Use the compact template: scope, repository/branch/PR identity, required test links, release impact and
   rollback. Add dependency/API/database/contract or Feature Flag detail only when actually affected; omit
   unchanged None sections and copied logs. Mark uncertain relationships explicitly.
5. When development is authorized, create one branch per affected repository using the same Change ID:
   `feat/<CHANGE_ID>-description`, `fix/<CHANGE_ID>-description`, or `hotfix/<CHANGE_ID>-description`.
   Preserve unrelated work and use isolated worktrees when required.
6. Keep Branches, PRs, tests, commits, decisions, and evidence current as work progresses.

## Confirm READY

Only mark a Change `READY` when the requested implementation and documentation are complete, required repository
and affected cross-repository tests passed, PRs merged to `main`, and release and rollback impact is recorded.
Safe temporary branch cleanup may be deferred and recorded; it does not block READY or routine deployment.
After business PRs merge and required checks pass, record READY locally without a separate governance PR/CI
wait. Batch record commits at closeout; only committed records are shared facts. Include version/changelog
changes in the feature PR instead of creating another preparation PR. Do not start another full review or
test phase after submission unless conflicts, new changes or failed evidence require it.
“Development complete” has this same meaning.

Do not create release Tags, deploy Production, activate features, or mark a Release successful. Commit, push,
PR, merge, and branch deletion remain separately governed actions and require the user's current authorization.
