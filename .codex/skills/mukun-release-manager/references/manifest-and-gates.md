# Manifest and Release Gates

Apply these common controls in both Prepare and Formal Release. Use repository AGENTS, existing
scripts, and CI for concrete commands; do not copy every repository command into this Skill.

## Persistent identity

- Release ID format: `REL-YYYYMMDD-NNN`; inspect existing records before allocating the sequence.
- Manifest path: `releases/<release_id>.yaml`, initialized from `RELEASE_MANIFEST.yaml`.
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
same evidence. Keep the existing image-release-v1 executable plan and required fields unchanged. An unchanged
boundary needs one honest evidence reference, not another probe/report. No separate READY/preparation governance
PR before deployment; persist locally and archive once at closeout. Ordinary personal-use features do not
require a new flag, grey rollout or observation gate.

## Git and worktree preflight

For each affected repository check current branch, HEAD SHA, expected Change SHA, dirty/untracked
state, unfinished merge/rebase/cherry-pick, upstream/remote state, relevant Tags, and worktrees.
Normal findings may be summarized as `PASS`; explain anomalies.

Never reset, discard, clean, delete unknown files or branches, rewrite history, force-push, or hide
state through an automatic stash. Block or use a provably safe isolated worktree. A dirty checkout
does not authorize including unrelated changes.

## Required gates

1. **Scope** — every Change is READY; every repository is affected; nothing extra is included.
2. **Git identity** — frozen SHAs are committed, reachable as required, and match evidence.
3. **Version** — application versions are independent; planned Tags are unused and immutable.
4. **Compatibility** — API, contract, webhook, command, lookup, database, and config changes are
   backward compatible or have explicitly approved breaking-change plans.
5. **Dependency** — required/optional/none classification and dynamic order are evidence-based.
6. **Tests** — repository, contract, integration, migration, build, and risk-based E2E evidence is
   current for the frozen SHA.
7. **Artifact** — exact identity and digest can be tied to the frozen Tag/SHA; `latest` is invalid.
8. **Deployment** — the entrypoint can deploy that exact Artifact. A floating-main fallback blocks.
9. **Production baseline** — current Tag, SHA, Artifact, and previous stable rollback identity are
   authoritative, not inferred.
10. **Rollback** — rollback version and implementation are executable; high-risk `UNKNOWN` blocks.
11. **Security/config** — required configuration is present without exposing values; backup and
    migration evidence is readable where applicable.
12. **Authorization** — current user wording authorizes the exact next mutation and environment.

For routine releases, these are review gates, not twelve fresh test runs. Reuse successful frozen-main CI
and verified unchanged-boundary evidence with its source/reason/limitations. Existing PASS in image-release-v1
may represent evidence review; do not describe skipped execution as a newly run test. Live baseline, readable
backup, image identity, health and smoke remain enforced by deploy. Apply RELEASE_RULES.md's risk table for
changed boundaries; no blanket restore/rollback/browser rerun or separate production-baseline refresh.

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
