---
name: release-manager
description: Prepare or formally release selected READY Investment Platform Changes across affected repositories using persisted manifests, independent versions, dependency-aware ordering, exact tags and fail-closed gates. Use for prepare-release, freeze, formal-release, or release-status requests; preparation never deploys Production.
---

# Release Manager

Coordinate the smallest release unit permitted by the user's current authorization. Read `AGENTS.md`,
`RELEASE_RULES.md`, `SYSTEM_MAP.yaml`, the selected Change files, and the active Release Manifest before acting.

## Prepare Release

“准备发版”“准备发布”“封板” select this mode. Collect only selected `READY` Changes and their actually affected
repositories. Use Git status/diff, version sources, Tags, CI and test evidence; do not rescan complete source trees
unless a gate fails or evidence is insufficient.

Perform repository preflight, lock exact Commit SHAs, calculate independent versions, validate dependencies and
contracts, determine dynamic release order and rollback versions, and run required gates. Create a persisted
`releases/<release_id>.yaml` from `RELEASE_MANIFEST.yaml` and mark it `PREPARED` only when all critical gates pass.

Preparation must not create or push formal Tags, deploy Production, or activate Feature Flags.

## Formal Release

Enter this mode only when the user explicitly authorizes “正式发布” or an unambiguous equivalent for the current
Release. Revalidate the prepared Manifest, then create immutable Tags on the frozen SHAs, record exact Artifact
identities and digests, and deploy Provider/Upstream before Consumer/Downstream. After each deployment verify
version, health, migration and smoke; then run contract, integration and necessary critical-path E2E checks.
Activate a Feature Flag only when recorded and only after deployment verification.

## Fail closed and closeout

Stop at the first critical failure, preserve evidence, do not continue downstream, and record exact partial state.
Unknown production baseline, rollback version, dependency, required test, Tag/SHA mismatch, unreadable backup, or
failed health/contract gate blocks formal release. Follow the Manifest rollback plan without inventing database
downgrades or replacement Tags.

Mark `RELEASED` only after production identity, deployment, verification, limitations and rollback point are
persisted. Do not delete branches without separate authorization and sufficient merge/worktree/PR/CI evidence.
