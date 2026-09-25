# Legacy Rule Convergence Report

- Date: 2026-09-25
- Scope: active Global, Trae, Dashboard development-process, Claude permission, and Release Skill
  governance surfaces only

## Global Rules

### Before

- 223 lines; SHA-256:
  `1a27a6d9fb17cf4863ff29e41e3b5a80ca533d98df70ab1770edf603217c4f5d`.
- Imposed a default `codex/<type>/<short-name>` namespace.
- Defined `codex/release-vX.Y.Z` and a candidate-branch-centered formal release sequence.
- Included detailed branch, merge, release, hotfix, and initialization workflows that could compete
  with project governance.

The complete original is archived at
`legacy-rules/global/AGENTS.pre-investment-platform-governance.md` with the same SHA-256.

### After

- 89 lines of generic, reusable safety defaults.
- Explicit priority: user instruction → workspace/project governance → repository instructions →
  Skill → global defaults.
- No global branch prefix, integration-branch model, release-branch model, or fixed merge sequence.
- Project-specific build, test, version, release, and production rules are delegated to the project.

### Removed Conflicts

- Global `codex/*` branch naming.
- Global release-candidate branch naming and candidate → main → Tag assumption.
- Global hotfix branch naming and project-independent release sequence.

### Preserved Safety Rules

- Protect user changes and worktrees; do not silently discard, stash, overwrite, or clean.
- Avoid destructive Git, history rewriting, unsafe force-push, and ambiguous cleanup.
- Respect local instructions, use small reviewable changes, and verify before reporting success.
- Require explicit authorization for Commit/Push/Merge/Tag/Production actions as applicable.
- Preserve immutable published Tags and do not infer Production from a floating branch or image.

## Trae Rules

### Before

- 39 lines; SHA-256:
  `88d0b7063563aad3f21d4668efafb0f52f2bf17322c6529caaf9a2c957d14c9c`.
- Declared `dev` as the daily integration branch and required feature → dev → main → Tag → deploy.

The complete original is archived at
`legacy-rules/trae/marketNewsFeed-代码开发规则.pre-governance.md` with the same SHA-256.

### After

- 30 lines focused on marketNewsFeed technical constraints.
- Delegates Change, Branch, main, Version, Release, and Hotfix to Investment Platform governance.
- Delegates repository build, test, runtime, database, contract, and deployment implementation to
  `marketNewsFeed/AGENTS.md`.

### Removed Conflicts

- Long-lived `dev` integration-line requirement.
- Feature → dev and dev → main release workflow.
- Trae-owned branch, Tag, and release governance.

## Dashboard Docs

### Updated References

- `CONTRIBUTING.md` no longer assigns a `codex/` branch prefix and now references Platform Branch
  Governance.
- `docs/development/process.md` retains the short-lived-branch principle but delegates Change and
  branch naming to `investment-platform/AGENTS.md`.
- No mandatory release branch, release candidate, or Production = main rule was found in these two
  documents.

## Claude Settings

### Permission-only Findings

- `stock-analyzer/.claude/settings.json` allows `git tag`, `git checkout`, `git merge dev`, and
  general `git merge` commands. These are permissions, not workflow authorization; Repository and
  Platform governance remain controlling.
- `stock-analyzer/.claude/settings.local.json` contains Python/Lark command permissions and no Git
  workflow declaration.

### Security Review Findings

- `marketNewsFeed/.claude/settings.local.json` contains broad `Bash(git *)` permission, which can
  encompass destructive or force operations even though none is written explicitly. Classify as
  `SECURITY_REVIEW_REQUIRED`; no settings were changed in this step.

## Remaining Governance Drift

- `DEPLOYMENT_GOVERNANCE_PENDING`: all three business repositories still have a floating-`main`
  deployment risk recorded by their Repository AGENTS; deployment scripts were out of scope.
- Claude command allow-lists require a later least-privilege security review, especially the broad
  marketNewsFeed Git wildcard.
- Historical archives retain old terms intentionally and are classified `HISTORICAL`, not active
  governance.
