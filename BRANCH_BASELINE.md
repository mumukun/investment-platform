# Git Branch Baseline

- Audit date: 2026-09-25
- Scope: `marketNewsFeed`, `stock-analyzer`, `investment-research-dashboard`, plus a lightweight
  `investment-platform` working-tree check
- Mode: audit only; no branch switch, creation, merge, rebase, deletion, Commit, Push, or Tag change
- Remote tracking refs and Tags: refreshed successfully with `git fetch --prune --tags origin`
- PR evidence: `PR_STATUS_UNKNOWN` for all three repositories. GitHub CLI is unavailable and the
  unauthenticated GitHub API returned 404, so no branch is treated as deletion-safe based on PR state.

## 1. Repository Baseline

| Repository | Current branch | HEAD | `main` SHA / upstream | Latest formal Tag | Working tree | Active worktrees | Remote refreshed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| marketNewsFeed | `dev` | `fe8bad0d7f3cbe5e17025d32db531b375c4cf889` | `deb075480b57f448b10d6de6880401a7a23fdc47` / `origin/main` | `v2.3.3` → `deb075480b57f448b10d6de6880401a7a23fdc47` | DIRTY: `AGENTS.md` and Trae rule modified; `test_discord.py` untracked and not inspected | primary checkout on `dev`; detached SIT checkout at `fe8bad0` | YES |
| stock-analyzer | `main` | `7e8b8aee55571665a4a1aa00b037a0486b97ea55` | same / `origin/main` | `v3.19.3` → `5571647bb826f1397fbae96b9c6a502425c02cda` | DIRTY: `AGENTS.md` modified | primary checkout on `main` | YES |
| investment-research-dashboard | `main` | `8ee167fb63870696b79d18f0667c00a61d4d1d62` | same / `origin/main` | `v0.13.1` → `8ee167fb63870696b79d18f0667c00a61d4d1d62` | DIRTY: `AGENTS.md`, `CONTRIBUTING.md`, and `docs/development/process.md` modified | primary checkout on `main`; SIT checkout on `codex/chore/local-sit-stack` | YES |

Origins:

- marketNewsFeed: `git@github.com:mumukun/marketNewsFeed.git`
- stock-analyzer: `git@github.com:mumukun/stock-analyzer.git`
- investment-research-dashboard: `git@github.com:mumukun/investment-research-dashboard.git`

## 2. Branch Inventory

Ahead/behind values are relative to local `main` after the successful refresh. `Patch unique` and
`patch equivalent` are from `git cherry main <ref>`. Remote tracking refs are listed separately from
local branches. Summary counts later in this file count logical branch names rather than duplicate
local/remote refs.

| Repository | Ref | Location | Tip | Upstream | Last commit | Ahead / behind | Patch unique / equivalent | Merged into `main` | Active worktree | Classification | Reason / recommendation |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| marketNewsFeed | `main` | Local | `deb075480b57` | `origin/main` | 2026-09-19 | 0 / 0 | 0 / 0 | YES | NO | PROTECTED | Persistent trunk; retain. |
| marketNewsFeed | `origin/main` | Remote | `deb075480b57` | — | 2026-09-19 | 0 / 0 | 0 / 0 | YES | N/A | PROTECTED | Remote persistent trunk; retain. |
| marketNewsFeed | `dev` | Local | `fe8bad0d7f3c` | `origin/dev` | 2026-09-19 | 0 / 6 | 0 / 0 | YES | YES | LEGACY_DEV_REVIEW | Exact ancestor of `main`, but it is the current dirty checkout. Keep temporarily; do not merge `dev` into `main`. |
| marketNewsFeed | `origin/dev` | Remote | `fe8bad0d7f3c` | — | 2026-09-19 | 0 / 6 | 0 / 0 | YES | via local `dev` | LEGACY_DEV_REVIEW | History is absorbed, but local user work and PR status must be resolved before retirement. |
| marketNewsFeed | `codex/docs/codex-branch-policy` | Local | `a8d4c261e2ed` | `origin/codex/docs/codex-branch-policy` | 2026-09-16 | 1 / 8 | 1 / 0 | NO | NO | UNMERGED_REVIEW | One unique AGENTS documentation commit. Decide whether it is obsolete or migrate required intent under a Change ID; do not merge wholesale. |
| marketNewsFeed | `origin/codex/docs/codex-branch-policy` | Remote | `a8d4c261e2ed` | — | 2026-09-16 | 1 / 8 | 1 / 0 | NO | NO | UNMERGED_REVIEW | Remote counterpart has the same unique commit; retain pending decision and PR evidence. |
| stock-analyzer | `main` | Local | `7e8b8aee5557` | `origin/main` | 2026-09-25 | 0 / 0 | 0 / 0 | YES | YES | PROTECTED | Persistent trunk; retain. |
| stock-analyzer | `origin/main` | Remote | `7e8b8aee5557` | — | 2026-09-25 | 0 / 0 | 0 / 0 | YES | N/A | PROTECTED | Remote persistent trunk; retain. |
| stock-analyzer | `dev` | Local | `5a6017085572` | `origin/dev` | 2026-08-21 | 0 / 94 | 0 / 0 | YES | NO | STALE_REMOTE_REVIEW | Exact ancestor with no unique commit, but a remote counterpart exists and PR status is unknown. Verify ownership/PR state before later deletion. |
| stock-analyzer | `origin/dev` | Remote | `5a6017085572` | — | 2026-08-21 | 0 / 94 | 0 / 0 | YES | NO | STALE_REMOTE_REVIEW | Fully merged remote history, but remote deletion safety is not proven without PR/owner evidence. |
| investment-research-dashboard | `main` | Local | `8ee167fb6387` | `origin/main` | 2026-09-25 | 0 / 0 | 0 / 0 | YES | YES | PROTECTED | Persistent trunk; retain. |
| investment-research-dashboard | `origin/main` | Remote | `8ee167fb6387` | — | 2026-09-25 | 0 / 0 | 0 / 0 | YES | N/A | PROTECTED | Remote persistent trunk; retain. |
| investment-research-dashboard | `codex/chore/local-sit-stack` | Local | `098ea1a90895` | `origin/main` | 2026-09-20 | 5 / 8 | 5 / 0 | NO | YES | ACTIVE_CHANGE | Five unique SIT/swing commits and an active worktree. Preserve; map required work to Change ID(s) before any future migration. No same-name remote ref exists. |

No `release/*`, `codex/release-*`, `release-v*`, or `hotfix/*` branches were found after refresh.

## 3. Logical Branch Summary

| Repository | Protected | Active change | Delete candidate | Review | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: |
| marketNewsFeed | 1 | 0 | 0 | 2 | 0 |
| stock-analyzer | 1 | 0 | 0 | 1 | 0 |
| investment-research-dashboard | 1 | 1 | 0 | 0 | 0 |

`Review` combines `UNMERGED_REVIEW`, `LEGACY_DEV_REVIEW`, and `STALE_REMOTE_REVIEW`. No branch is
currently classified `MERGED_DELETE_CANDIDATE` because reliable PR state is unavailable and the
otherwise-merged legacy branches still need ownership/worktree resolution.

## 4. marketNewsFeed `dev` Analysis

- Merge base: `fe8bad0d7f3cbe5e17025d32db531b375c4cf889` (the `dev` tip).
- `dev` ahead of `main`: 0.
- `dev` behind `main`: 6.
- Unique or patch-only commits on `dev`: 0.
- Does `dev` contain commits absent from `main`? **NO**.
- Does `main` contain commits absent from `dev`? **YES**.
- Absorbed by `main`? **YES**; exact ancestor, not merely patch-equivalent.
- Business modifications that still require preservation? **REVIEW**. The branch has no unique
  committed business change, but its active checkout contains uncommitted governance files and the
  untracked `test_discord.py`, whose contents were intentionally not read.
- Recommended strategy: **KEEP_TEMPORARILY**.

Retirement requires first preserving authorized governance changes through the new Change workflow,
resolving ownership/disposition of the untracked user file, moving active work away from `dev`, and
checking PR/automation dependencies. Once those blockers are cleared, the branch history itself can
be retired directly; there is no reason to merge `dev` into `main`.

## 5. Tag Lineage

| Repository | Latest Tag | Tag commit | Reachable from `main` | `main` commits after Tag | Finding |
| --- | --- | --- | --- | ---: | --- |
| marketNewsFeed | `v2.3.3` | `deb075480b57f448b10d6de6880401a7a23fdc47` | YES | 0 | No lineage anomaly. |
| stock-analyzer | `v3.19.3` | `5571647bb826f1397fbae96b9c6a502425c02cda` | YES | 7 | `main` legitimately leads the latest Tag; no lineage anomaly. |
| investment-research-dashboard | `v0.13.1` | `8ee167fb63870696b79d18f0667c00a61d4d1d62` | YES | 0 | No lineage anomaly. |

No `TAG_LINEAGE_REVIEW` finding was produced. This is Git lineage evidence only and does not claim
that any Tag is the real current Production identity.

## 6. Active Worktrees

| Repository | Path | Branch / state | HEAD | Impact |
| --- | --- | --- | --- | --- |
| marketNewsFeed | `/Users/mukun/work/workspace/stock/marketNewsFeed` | `dev` | `fe8bad0d7f3c` | Blocks `dev` retirement; working tree is dirty. |
| marketNewsFeed | `/Users/mukun/work/workspace/stock/marketNewsFeed-sit` | detached, clean | `fe8bad0d7f3c` | Preserve until ownership/use is confirmed; it does not directly lock a branch ref. |
| stock-analyzer | `/Users/mukun/work/workspace/stock/stock-analyzer` | `main` | `7e8b8aee5557` | Protected trunk checkout. |
| investment-research-dashboard | `/Users/mukun/work/workspace/stock/investment-research-dashboard` | `main` | `8ee167fb6387` | Protected trunk checkout; governance files are dirty. |
| investment-research-dashboard | `/Users/mukun/work/workspace/stock/investment-research-dashboard-sit` | `codex/chore/local-sit-stack`, clean | `098ea1a90895` | Proves active branch use; branch cannot be a deletion candidate. |

## 7. Governance Working Trees

`GOVERNANCE_CHANGES_UNCOMMITTED` applies to all three business repositories:

- marketNewsFeed: `AGENTS.md` (STEP 3) and `.trae/rules/代码开发规则.md` (STEP 5) are modified and
  unstaged. `test_discord.py` remains an unrelated untracked user file.
- stock-analyzer: `AGENTS.md` (STEP 3) is modified and unstaged.
- investment-research-dashboard: `AGENTS.md` (STEP 3), `CONTRIBUTING.md`, and
  `docs/development/process.md` (STEP 5) are modified and unstaged.

No governance file was committed in this audit.

## 8. investment-platform State

- Current branch: `main`.
- HEAD: `NO_COMMIT` (unborn branch).
- Upstream display: `origin/main [gone]`.
- Working tree: all current governance files, Skills, templates, reports, Changes, and archives are
  untracked; this file is part of that uncommitted governance baseline.
- Origin: `git@github.com:mumukun/investment-platform.git`.

A separate, explicitly authorized Governance Baseline Commit is required later; this audit does not
create it.

## 9. Future Branch Lifecycle Policy

- Branch is a temporary workspace. The default persistent branch is `main`.
- Temporary names are `feat/CHG-YYYYMMDD-NNN-description`,
  `fix/CHG-YYYYMMDD-NNN-description`, and `hotfix/CHG-YYYYMMDD-NNN-description`.
- A temporary branch is deletion-eligible only after it is merged, has no unique commit, has no
  active worktree, has no active PR/dependency, and no user work depends on it.
- Future automation may delete only `MERGED_DELETE_CANDIDATE` branches.
- `UNMERGED_REVIEW`, `LEGACY_DEV_REVIEW`, `STALE_REMOTE_REVIEW`, and `UNKNOWN` always require review.
- Age alone is never deletion evidence. Local and remote refs require separate verification.

## 10. Recommended STEP 7 Plan

1. Establish an authorized Governance Baseline Change/commit so current STEP 3/5 documents are not
   stranded in dirty business working trees or an unborn platform repository.
2. For marketNewsFeed, preserve authorized governance edits, decide the untouched `test_discord.py`
   ownership/disposition, move active work off `dev`, verify PR/automation state, then retire `dev`
   directly without `dev → main`.
3. Review marketNewsFeed `codex/docs/codex-branch-policy`; mark its unique AGENTS change obsolete or
   migrate only still-required intent under a new Change ID.
4. Obtain reliable PR/ownership evidence for stock-analyzer `dev`; if no dependency remains, promote
   it to `MERGED_DELETE_CANDIDATE` before any local or remote deletion.
5. Preserve Dashboard `codex/chore/local-sit-stack`; map its five unique commits to one or more
   Change IDs and migrate only approved work to compliant Change branches.
6. Re-run branch/ref/worktree/PR checks immediately before any STEP 7 cleanup; do not rely on this
   snapshot alone.

## 11. STEP 7 Main Alignment Update

This update records the authorized local Governance Baseline operation; the earlier STEP 6 snapshot
above remains intact as historical audit evidence.

| Repository / branch | STEP 7 result | Current classification |
| --- | --- | --- |
| marketNewsFeed primary checkout | Switched from `dev` to local `main` at `b7a7e982bb688b5f4818bee0a8e5b5cc3d8b8bdb`; `test_discord.py` remains untouched and untracked | `main` is PROTECTED |
| marketNewsFeed `dev` / `origin/dev` | 0 ahead, 7 behind local `main`, exact ancestor, no active branch worktree; PR status remains unknown | STALE_REMOTE_REVIEW |
| marketNewsFeed `codex/docs/codex-branch-policy` | 1 ahead, 9 behind local `main`; its sole commit changes only `AGENTS.md` and reinstates the old `dev`, global `codex/*`, candidate-branch, and dev-to-main model | SUPERSEDED_LEGACY_BRANCH |
| stock-analyzer `dev` / `origin/dev` | 0 ahead, 95 behind local `main`, exact ancestor; PR/ownership remains unknown | STALE_REMOTE_REVIEW |
| Dashboard `codex/chore/local-sit-stack` | 5 ahead, 9 behind local `main`; clean active SIT worktree remains unchanged | ACTIVE_CHANGE |

The superseded marketNewsFeed branch contains no governance capability that still needs migration:
the valid repository technical constraints and user-work safety rules are present in the current
Repository AGENTS or higher-level governance. The branch was not merged, rewritten, or deleted.

Local governance baseline commits now reachable from business `main`:

- marketNewsFeed: `b7a7e982bb688b5f4818bee0a8e5b5cc3d8b8bdb`;
- stock-analyzer: `8c5387300dd3ee2fc584319f8147966355f83756`;
- investment-research-dashboard: `90ef7edd87fb2581a1ee904417d08ed2687b8b2e`.

All three one-time governance branches and their temporary worktrees were removed after Fast Forward.
No legacy local or remote branch was deleted. All three business `main` branches are one local Commit
ahead of `origin/main` and require explicit remote synchronization later.

The `investment-platform` bootstrap exception produced initial Governance Baseline Commit
`c5684b87e6e462982f1e1f15ac6c6284fb1224e2` directly on its previously unborn local `main`.
