# Manifest and Release Gates

Apply these common controls in both Prepare and Formal Release. Use repository AGENTS, existing
scripts, and CI for concrete commands; do not copy every repository command into this Skill.

## Persistent identity

- Release ID format: `REL-YYYYMMDD-NNN`; inspect existing records before allocating the sequence.
- Freeze one execution plan before mutations; it holds scope, exact identities and rollback. Do not retype
  a second prepared Manifest. Generate `releases/<release_id>.yaml` from the actual deployment receipt;
  `RELEASE_MANIFEST.yaml` remains a manual-reference template.
- A Release may contain multiple READY Changes. Its repository scope is the union of their affected
  repositories, reduced to repositories with actual release changes.
- Persist state locally/NAS journal at material transitions; combine shared governance commit/PR at closeout.
  A separate commit, CI wait or PR per transition is not required. Chat is not the system of record.

At minimum record:

- `release_id`, `status`, `changes`, timestamps, environment, and release order;
- per repository: name, previous/new version, exact SHA, Tag, Artifact identity/digest,
  retained rollback identity and links to current CI/candidate/deployment evidence;
- result, backup/rollback point, actual changed-boundary checks and limitations, preferably by receipt link.

Omit inapplicable fields and duplicated top-level/per-repository versions or test detail. Do not create extra
identity, hash, configuration or test summary files when the candidate/deploy receipt already provides the
same evidence. Keep image-release-v1; new plans omit the optional legacy `gates` field. An unchanged
boundary needs one honest evidence reference, not another probe/report. No separate READY/preparation governance
PR before deployment; persist locally and archive once at closeout. Ordinary personal-use features do not
require a new flag, grey rollout or observation gate.

Use `image_release.py deploy ... --receipt ... --manifest releases/<release_id>.yaml` to summarize the real
receipt, or local `record` to regenerate that same generated record without contacting NAS. Hand-maintained
final/unrelated Manifests are never overwritten; matching prepared records are completed while preserving
existing PR links, notes and verification limitations. Generated deployment smoke evidence is not full functional/performance or
real-source acceptance; reference development evidence from the Change/CI and add actual limitations only.
Generated records are JSON (valid YAML 1.2); only matching JSON preparation records can be completed in place.
Keep historical hand-written YAML intact.

## Git and worktree preflight

For each affected repository check current branch, HEAD SHA, expected Change SHA, dirty/untracked
state, unfinished merge/rebase/cherry-pick, upstream/remote state, relevant Tags, and worktrees.
Normal findings may be summarized as `PASS`; explain anomalies.

Never reset, discard, clean, delete unknown files or branches, rewrite history, force-push, or hide
state through an automatic stash. Block or use a provably safe isolated worktree. A dirty checkout
does not authorize including unrelated changes.

## Checks performed by the existing deployment entry

Select affected READY Changes and their tested frozen main artifacts once. Formal authorization is still
required for mutations. The entry enforces exact Tag/SHA/image identity, CI/candidate provenance, actual
baseline/retained rollback image, configuration, dependency order and the reviewed backup decision, then
checks runtime identity, health and one smoke. Stop on actual failure and keep the partial receipt.

Do not turn these conditions into a twelve-item manual review or require six evidence strings. Development
functional/integration/performance validation is recorded once under `docs/development-validation.md`.
Only investigate missing or conflicting evidence. Legacy plans containing `gates` keep their original checks;
never delete a known failure to bypass it. Do not run restore/rollback/browser suites or baseline-refresh jobs
as routine preparation. See RELEASE_RULES.md for actual data/contract changes and backup scope.

Use `dashboard-contract-check` when a Dashboard/upstream contract change needs specialized
validation and that Skill is available. Do not duplicate all contract schemas here.

## Branch cleanup safety

Release success does not justify deleting every branch. Cleanup is allowed only for an exact
temporary branch when it is merged into the correct target, has no unique Commit, uncommitted or
unpublished work, active worktree, open/dependent PR, CI/automation consumer, protected status, or
unknown ownership. Squash/Rebase merges require platform merge evidence, not ancestry alone.

If any condition cannot be proven, retain the exact branch and record pending cleanup; this does not demote
an otherwise READY Change or RELEASED deployment. Never delete protected or
unknown historical branches.
