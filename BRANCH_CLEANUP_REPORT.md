# Legacy Branch Cleanup Report

- Cleanup date: 2026-09-26
- Scope: `marketNewsFeed`, `stock-analyzer`, and a read-only protection check of
  `investment-research-dashboard`
- Remote state: refreshed successfully before cleanup; each deleted remote ref was pruned and
  verified separately
- PR evidence: authenticated GitHub Open PR filters returned zero matches for every deleted branch
- Protection evidence: no classic branch protection rules or repository rulesets are configured in
  `marketNewsFeed` or `stock-analyzer`

## Deleted

| Repository | Branch | Local | Remote | Evidence |
| --- | --- | --- | --- | --- |
| marketNewsFeed | `dev` | DELETED | DELETED | Tip `fe8bad0d7f3cbe5e17025d32db531b375c4cf889`; exact ancestor of `main`, 0 unique commits, 7 commits behind, no branch worktree, no Open PR, not protected. |
| marketNewsFeed | `codex/docs/codex-branch-policy` | DELETED | DELETED | Tip `a8d4c261e2ede54c9949369b4256d15e420f6c28`; sole unique commit changed only `AGENTS.md`; superseded governance archived before deletion; no worktree, Open PR, or protection. |
| stock-analyzer | `dev` | DELETED | DELETED | Tip `5a6017085572b17e52dacf36aae2d9065ff2bb51`; exact ancestor of `main`, 0 unique commits, 95 commits behind, no worktree, no Open PR, not protected. |

All local deletions used normal `git branch -d`. Remote branches were deleted one at a time; no
Force Push, merge, rebase, cherry-pick, Tag change, or business Commit was performed.

## Retained

| Repository | Branch | Classification | Reason |
| --- | --- | --- | --- |
| marketNewsFeed | `main` | PROTECTED | Persistent development baseline. |
| stock-analyzer | `main` | PROTECTED | Persistent development baseline. |
| investment-research-dashboard | `main` | PROTECTED | Persistent development baseline. |
| investment-research-dashboard | `codex/chore/local-sit-stack` | ACTIVE_CHANGE | Five unique commits and an active clean SIT worktree at `098ea1a9089560ec2455c358466a74f34f2daf31`; explicitly excluded from cleanup. |

## Review

No additional branch requires review. The detached `marketNewsFeed-sit` worktree remains a separate
`STALE_WORKTREE_REVIEW` item and was not removed.

## Worktrees

| Repository | Path | Branch / State | HEAD | Classification |
| --- | --- | --- | --- | --- |
| investment-platform | `/Users/mukun/work/workspace/stock/investment-platform` | `main` | Governance maintenance HEAD | PROTECTED |
| marketNewsFeed | `/Users/mukun/work/workspace/stock/marketNewsFeed` | `main` | `b7a7e982bb688b5f4818bee0a8e5b5cc3d8b8bdb` | PROTECTED |
| marketNewsFeed | `/Users/mukun/work/workspace/stock/marketNewsFeed-sit` | detached, clean | `fe8bad0d7f3cbe5e17025d32db531b375c4cf889` | STALE_WORKTREE_REVIEW |
| stock-analyzer | `/Users/mukun/work/workspace/stock/stock-analyzer` | `main` | `8c5387300dd3ee2fc584319f8147966355f83756` | PROTECTED |
| investment-research-dashboard | `/Users/mukun/work/workspace/stock/investment-research-dashboard` | `main` | `90ef7edd87fb2581a1ee904417d08ed2687b8b2e` | PROTECTED |
| investment-research-dashboard | `/Users/mukun/work/workspace/stock/investment-research-dashboard-sit` | `codex/chore/local-sit-stack`, clean | `098ea1a9089560ec2455c358466a74f34f2daf31` | ACTIVE_CHANGE |

## Safety Evidence

- `marketNewsFeed/test_discord.py` remained untracked with unchanged inode, size, mtime, and mode.
- The Dashboard SIT Branch, tip, worktree, and clean status remained unchanged.
- No new unexpected local or remote branch appeared during the refreshed inventory.
- Business repository tracked working trees remained clean; no business source was modified or
  committed.
