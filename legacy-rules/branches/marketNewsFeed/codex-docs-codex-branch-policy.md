# Archived Legacy Branch: `codex/docs/codex-branch-policy`

- Repository: `marketNewsFeed`
- Branch: `codex/docs/codex-branch-policy`
- Tip SHA: `a8d4c261e2ede54c9949369b4256d15e420f6c28`
- Commit message: `docs: align Codex branch policy`
- Changed files: `AGENTS.md` only
- Branch classification: `SUPERSEDED_LEGACY_BRANCH`
- Superseded verification: `VERIFIED`
- Deletion date: 2026-09-26
- Local deletion status: `DELETED`
- Remote deletion status: `DELETED`

## Diff Summary

The sole unique commit changes governance documentation only. It defines the superseded long-lived
`dev` integration line, global `codex/<type>/<short-name>` branches, a default
`codex/release-vX.Y.Z` candidate branch, and `dev`-to-`main` release flow. It contains no business
source, script, runtime configuration, deployment implementation, test implementation, or database
change.

## Why Superseded

The branch conflicts with the active trunk-based Investment Platform governance. Its reusable user
work protections and repository-specific technical constraints are already retained in the current
global and repository instructions. Merging this branch would restore an obsolete Git and release
model.

## Replacement Governance

- `investment-platform/AGENTS.md`
- `investment-platform/RELEASE_RULES.md`
- `investment-platform/SYSTEM_MAP.yaml`
- `marketNewsFeed/AGENTS.md`

## Deletion Evidence

- Local and remote tips both equal `a8d4c261e2ede54c9949369b4256d15e420f6c28`.
- The branch has one unique commit relative to `main`; that commit changes only `AGENTS.md`.
- No active worktree uses the branch.
- GitHub's authenticated Open PR filter returned zero matching PRs.
- The repository has no configured classic branch protection rule or ruleset.
- The archive was created before branch deletion; final deletion results are recorded in this file
  and `BRANCH_CLEANUP_REPORT.md`.
- The local branch was deleted with normal `git branch -d`; no force-delete was used.
- The remote branch was deleted individually and a subsequent fetch/prune confirmed that the
  tracking ref no longer exists.
