# Release Skill Migration Report

- Migration date: 2026-09-25
- Old Skill: `mukun-deploy-ready`
- New Skill: `mukun-release-manager`
- Old Skill archive: `legacy-rules/skills/mukun-deploy-ready/`
- STEP 1 Skill archive: `legacy-rules/skills/release-manager-step1/`

## Active Skill Status

| Skill | Status | Location |
| --- | --- | --- |
| `mukun-release-manager` | ACTIVE, authoritative Release Governance Skill | `.codex/skills/mukun-release-manager/` |
| `mukun-deploy-ready` | `ARCHIVED_INACTIVE` | archive above; inactive copy at `~/.codex/inactive-skills/mukun-deploy-ready/` |
| `release-manager` | `REMOVED_FROM_ACTIVE` | archived as the STEP 1 baseline above |
| `dashboard-contract-check` | ACTIVE specialized contract Skill; not a Release Governance Skill | `~/.codex/skills/dashboard-contract-check/` |

## Capabilities Kept

- Git preflight, dirty/untracked state detection, exact HEAD and remote/Tag checks.
- Protection of user changes, worktree safety, and prohibition on reset, discard, hidden stash, history rewrite, and force-push.
- Affected-repository scope detection and multi-repository coordination.
- Independent repository SemVer, immutable Tags, and exact Commit SHA.
- Dependency-aware ordering, health/contract verification, fail-closed behavior, and evidence-based safe branch cleanup.

## Capabilities Migrated

| Capability | New behavior |
| --- | --- |
| Prepare / freeze | Persists an exact scope, version, SHA, dependency order, evidence, and rollback plan without Tag or deployment. |
| Authorization | Separates `PREPARE RELEASE` from explicitly authorized `FORMAL RELEASE`. |
| Manifest and state | Uses a persisted `releases/<release_id>.yaml`; chat is only a compact summary. |
| Artifact / Production identity | Requires immutable Tag + exact SHA + exact Artifact identity, plus digest when applicable. |
| Rollback | Records the previous confirmed stable version/Artifact; unknown high-risk rollback baselines block. |
| Multi-repository release | Includes only repositories changed by selected READY Changes and orders them from verified dependency edges. |
| Closeout | Persists production verification and marks Releases and included Changes `RELEASED` only after success. |

## Capabilities Rejected

- Default release-candidate or release branches.
- Creating a formal Tag for “准备发版”, “准备发布”, or “封板”.
- Deploying Production or activating features during preparation.
- Keeping the Release Manifest only in chat.
- Inferring Production from current `main`, or using floating `main`, `HEAD`, or `latest` as Production identity.
- Rescanning complete source repositories during a normal release.

## Prepare Release Semantics

Preparation collects selected READY Changes, derives the affected-repository union, performs Git,
test, contract, integration, compatibility, deployment, and rollback gates, independently determines
versions and exact SHAs, dynamically calculates release order, allocates a unique Release ID, and
persists the Manifest. Success ends at `READY_FOR_FORMAL_RELEASE`; it cannot create/push a formal Tag,
deploy Production, activate a feature, or mark the Release `RELEASED`.

## Formal Release Semantics

Only explicit “正式发布” or an unambiguous equivalent authorizes Formal Release. It revalidates the
prepared Manifest and every critical gate, then may create/push immutable Tags, deploy exact
Tag-derived Artifacts in dynamic dependency order, run smoke/integration/critical-path E2E, activate
an approved Feature Flag, persist actual Production identities, mark included Changes and the Release
`RELEASED`, and clean only branches proven safe. A critical failure stops immediately and records the
honest partial or blocked state.

## Known Deployment Blockers

All three current business-repository deployment entries are `NON_COMPLIANT` with the exact
Tag/Artifact Production policy because a floating-`main` path remains possible. Until a later
Deployment Governance Change guarantees exact identity, Formal Release must be `BLOCKED`; this
migration did not modify any deployment script.

## Global Rule Convergence

STEP 5 replaced the global project-specific branch namespace and candidate-branch release sequence
with generic safety defaults. Global rules now defer branch, version, and release governance to the
Workspace/Project and Repository. The original Global AGENTS remains preserved in the STEP 5
archive for historical audit.

## Remaining Risks

- Production Tag, SHA, Artifact/digest, and stable rollback baselines remain `UNKNOWN` until the
  Production Baseline step.
- Deployment implementations remain non-compliant until exact Tag/Artifact deployment is enforced.
- Claude command allow-lists still require a separate least-privilege security review.
- Release Manifest storage is governed, but no real Release was created or exercised in this step.
