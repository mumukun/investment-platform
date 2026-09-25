# Investment Platform Governance Baseline

## Identity

- Baseline date: 2026-09-25
- Governance Change ID: `CHG-20260925-000`
- Change type: `NON_RELEASE_CHANGE`
- Platform governance version: `1.0`
- investment-platform initial Governance Commit: `c5684b87e6e462982f1e1f15ac6c6284fb1224e2`
- STEP 7 Governance Baseline Closeout Commit: `6d6399753a63d177eaae6a74c6e7b0c2bdb9334d`
- Active Release Governance Skill: `mukun-release-manager`
- Release impact: `NONE`
- Business release / Production deployment required: `NO` / `NO`
- Remote sync status: `COMPLETE`

## Repository Baseline Commits

| Repository | Local `main` at baseline sync | `origin/main` after sync | Sync date | Status |
| --- | --- | --- | --- | --- |
| investment-platform | `6d6399753a63d177eaae6a74c6e7b0c2bdb9334d` | `6d6399753a63d177eaae6a74c6e7b0c2bdb9334d` | 2026-09-26 | SYNCED |
| marketNewsFeed | `b7a7e982bb688b5f4818bee0a8e5b5cc3d8b8bdb` | `b7a7e982bb688b5f4818bee0a8e5b5cc3d8b8bdb` | 2026-09-26 | SYNCED |
| stock-analyzer | `8c5387300dd3ee2fc584319f8147966355f83756` | `8c5387300dd3ee2fc584319f8147966355f83756` | 2026-09-26 | SYNCED |
| investment-research-dashboard | `90ef7edd87fb2581a1ee904417d08ed2687b8b2e` | `90ef7edd87fb2581a1ee904417d08ed2687b8b2e` | 2026-09-26 | SYNCED |

The investment-platform commit that records this table is a documentation-only closeout commit on
top of the synchronized STEP 7 baseline and is also pushed to `origin/main` by STEP 8A.

## Current Branch Model

- Persistent branch: `main`.
- Temporary branches:
  - `feat/CHG-YYYYMMDD-NNN-description`
  - `fix/CHG-YYYYMMDD-NNN-description`
  - `hotfix/CHG-YYYYMMDD-NNN-description`
- Temporary lifecycle: Create → Commit/Review → Merge `main` → verify → delete when safe.
- Release branches are exceptional and temporary, only for an explicitly approved long Freeze/UAT.

## Known Legacy Branches

| Repository | Branch | Classification | Current action |
| --- | --- | --- | --- |
| marketNewsFeed | `dev` / `origin/dev` | STALE_REMOTE_REVIEW | Retain pending reliable PR/ownership evidence. |
| marketNewsFeed | `codex/docs/codex-branch-policy` and remote counterpart | SUPERSEDED_LEGACY_BRANCH | Retain for later cleanup authorization; do not merge. |
| stock-analyzer | `dev` / `origin/dev` | STALE_REMOTE_REVIEW | Retain pending reliable PR/ownership evidence. |
| investment-research-dashboard | `codex/chore/local-sit-stack` | ACTIVE_CHANGE | Preserve active SIT worktree and five unique commits. |

## Operational Baselines

- Deployment governance: `NON_COMPLIANT` / `DEPLOYMENT_GOVERNANCE_PENDING` for all three business
  repositories because an exact Tag/Artifact deployment is not yet guaranteed.
- Production baseline: `UNKNOWN`; real Production Tag, Commit SHA, Artifact identity/digest, and
  rollback baseline must be read from the running environments in a later step.
- marketNewsFeed application version source: current `UNKNOWN`; target root `VERSION` remains a later
  governed Change.
- Governance baseline commits are synchronized to each repository's `origin/main`. No business Tag,
  Release Manifest, or Production action is part of this baseline.

## Verification

- Governance file scope and cached diffs: PASS.
- High-confidence Secret scan across platform, archives, and committed repository governance files:
  PASS; no credential-bearing archive was detected.
- Business source changes: NONE.
- Temporary governance branches/worktrees: merged by Fast Forward and removed.
- User work: marketNewsFeed `test_discord.py` preserved untouched and untracked.
- Remote synchronization: PASS; each Push was Fast Forward only, and every Governance Commit is
  reachable from the corresponding `origin/main`.
