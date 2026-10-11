# Prepare Release

Preparation does not authorize Tag creation or Production changes. For a formal release request, run this
concise preparation inside the formal turn; do not require another user prompt or a separate preparation PR.
Begin elapsed timing at the user’s submit/merge/prepare request; report time to READY including commit/merge
and CI/build waiting, not just the final check. Target 30–60 seconds for assistant review of existing evidence. Required development/contract/migration checks
belong before declaring development complete. During release investigate only missing or conflicting evidence,
not another blanket validation phase. Keep one release owner and exchange final evidence once.
Business versions/changelog belong in the feature PR. Merged business PRs and passed required checks allow
local READY; no extra version, READY, preparation or baseline governance PR/CI wait. Compact records link
the existing evidence, omitting unchanged impact sections. Freeze once rather than restart for unrelated main commits.

1. Read selected READY Changes, current baseline and existing candidate evidence. Include only changed
   business repositories; governance-only Changes do not receive business versions or a deployment.
2. Check relevant Git state and freeze the committed main SHA/version and corresponding successful CI
   candidate. Compute only required upstream order. Preserve unrelated changes and worktrees.
3. Reuse current tests for that SHA and verified evidence for unchanged boundaries. Apply the risk table in
   RELEASE_RULES.md to changed migrations, contracts or deployment mechanisms. No routine clone/restore,
   old-image test, runner rollback test or second real-source probe. Do not call verify-ci separately just
   to repeat the same check inside deploy.
4. Reuse the verified previous Production Tag/SHA/image and configuration. Record them in a single Manifest
   and image-release-v1 plan, with honest evidence reuse notes. The deployer checks live drift before switching.
5. Mark READY_FOR_FORMAL_RELEASE when applicable checks pass. A prepare-only request ends here; a formally
   authorized turn continues immediately. Persist local state; combine governance commits at closeout.

Unexplained drift, missing CI/artifact evidence, unknown rollback, or a failing applicable test blocks.
For breaking schema/data changes, explain concrete risk and prefer focused tests/fix-forward evidence.
Drills remain disabled by default; do not automatically invoke clone/restore/old-image/rollback tools.
Unresolved actual data-loss risk blocks the mutation. Do not stretch
the routine five-minute objective to hide unverified migrations. No default release branch or per-stage PR.
