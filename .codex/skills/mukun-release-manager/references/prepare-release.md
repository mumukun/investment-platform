# Prepare Release

Use this workflow for preparation, freeze, readiness, or “can this release?” requests. Preparation
is read-mostly release governance and does not authorize formal Tag creation or Production changes.

## Workflow

1. Resolve the selected `READY` business-release Change files. Exclude governance-only,
   `NON_RELEASE_CHANGE`, and `Release Impact: NONE` Changes before allocating any Release ID; reject
   non-READY or ambiguous business-release Changes.
2. Build the Release scope from their affected repositories; exclude every unchanged repository.
3. Read `SYSTEM_MAP.yaml` and Change-specific dependencies. Classify relevant edges as `required`,
   `optional`, or `none`.
4. Allocate the next unused `REL-YYYYMMDD-NNN` after checking existing Manifests and release records.
5. Create or update `releases/<release_id>.yaml` from `RELEASE_MANIFEST.yaml`; do not keep state only
   in chat.
6. Run concise Git preflight for every affected repository: branch, HEAD, dirty/untracked state,
   unfinished operations, upstream/remote, worktrees, relevant Tags, and expected Change SHA.
7. Confirm the Change evidence, PR/merge result, tests, CI, contracts, integration checks, migration
   state, configuration changes, and feature activation plan.
8. Lock the exact release Commit SHA for each repository. Evidence must correspond to that SHA.
9. Determine an independent SemVer bump for each changed repository from actual compatibility impact.
10. Determine previous Production version and rollback version from an authoritative environment or
    release record. Use `UNKNOWN`, never inference from local `main` or latest Tag.
11. Validate API, `contract_version`, webhook, maintenance command, stock lookup, database migration,
    and environment/config compatibility where affected.
12. For a breaking change require explicit approval, MAJOR version, migration plan, and Consumer
    migration strategy; otherwise set `BLOCKED`.
13. Calculate release order dynamically. A Consumer that needs a new Provider capability makes the
    edge required; a backward-compatible Provider change may release independently.
14. Plan exact Tag, Artifact identity/digest, deployment implementation, repository smoke,
    integration checks, critical-path E2E, feature activation, and rollback.
15. Run every applicable release gate from `manifest-and-gates.md` and Repository AGENTS/CI.
16. Persist all results. Mark the Manifest `READY_FOR_FORMAL_RELEASE` only when every critical gate
    passes.

## Prohibited in this mode

- Creating or pushing a formal Git Tag.
- Production deployment or Production database changes.
- Production Feature Flag activation.
- Marking the Release or included Changes `RELEASED`.
- Creating a release/release-candidate branch by default.
- Merging or pushing code merely because the user said “准备发版” or “封板”.

## Compact result

Return:

- Release ID
- Included Changes
- Affected repositories
- Previous/new versions
- Exact Commit SHAs
- Dynamic release order
- Rollback versions
- Release gate result
- `READY_FOR_FORMAL_RELEASE`
