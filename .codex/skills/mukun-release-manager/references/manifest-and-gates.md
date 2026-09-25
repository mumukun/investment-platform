# Manifest and Release Gates

Apply these common controls in both Prepare and Formal Release. Use repository AGENTS, existing
scripts, and CI for concrete commands; do not copy every repository command into this Skill.

## Persistent identity

- Release ID format: `REL-YYYYMMDD-NNN`; inspect existing records before allocating the sequence.
- Manifest path: `releases/<release_id>.yaml`, initialized from `RELEASE_MANIFEST.yaml`.
- A Release may contain multiple READY Changes. Its repository scope is the union of their affected
  repositories, reduced to repositories with actual release changes.
- Persist after every material state transition. Chat output is a summary, not the system of record.

At minimum record:

- `release_id`, `status`, `changes`, timestamps, environment, and release order;
- per repository: name, previous/new version, exact SHA, Tag, Artifact identity/digest,
  dependencies, rollback version, tests, deployment, and verification;
- Repository, Contract, Integration, Smoke, Critical-path E2E, Feature Flag, Production identity,
  limitations, and rollback evidence.

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

Use `dashboard-contract-check` when a Dashboard/upstream contract change needs specialized
validation and that Skill is available. Do not duplicate all contract schemas here.

## Branch cleanup safety

Release success does not justify deleting every branch. Cleanup is allowed only for an exact
temporary branch when it is merged into the correct target, has no unique Commit, uncommitted or
unpublished work, active worktree, open/dependent PR, CI/automation consumer, protected status, or
unknown ownership. Squash/Rebase merges require platform merge evidence, not ancestry alone.

If any condition cannot be proven, record `REVIEW` and retain the branch. Never delete protected or
unknown historical branches.
