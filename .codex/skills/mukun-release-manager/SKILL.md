---
name: mukun-release-manager
description: >
  Prepare and execute governed releases for the Investment Platform
  across affected repositories. Manage release scope, independent
  semantic versions, dependency and contract validation, immutable
  tags, exact production artifacts, rollback points, verification,
  and release closeout.
---

# Mukun Release Manager

This is the single authoritative Release Governance Skill for the Investment Platform. It prepares
or formally releases only the Changes, repositories, and environment authorized by the user. It
does not replace repository-specific build, test, deployment, health, or rollback implementation.

## Select exactly one authorization mode

- **PREPARE RELEASE** — selected by “准备发版”, “准备发布”, “封板”, “检查是否可以发布”,
  `release readiness`, or `prepare release`. Read
  [references/prepare-release.md](references/prepare-release.md). This mode never creates or pushes
  a formal Tag, deploys Production, activates a feature, or marks a Release `RELEASED`.
- **FORMAL RELEASE** — selected only when the user explicitly authorizes “正式发布” or an
  unambiguous equivalent for the current Release and Production environment. Read
  [references/formal-release.md](references/formal-release.md).

An action-specific request such as “打 Tag” or “部署某环境” authorizes only that named action; do
not silently upgrade it to a complete Formal Release. If the requested action would break platform
governance, stop and report the conflict.

For either mode, read [references/manifest-and-gates.md](references/manifest-and-gates.md) before
release mutations.

## Read persisted state before code

Read, in order:

1. `AGENTS.md` and `RELEASE_RULES.md`;
2. `PRODUCTION_BASELINE.yaml` and the selected `releases/<release_id>.yaml` or
   `RELEASE_MANIFEST.yaml` template;
3. included `changes/<CHANGE_ID>.md` files;
4. `SYSTEM_MAP.yaml`;
5. affected Repository AGENTS and recorded Git/CI/test/contract evidence.

Do not rescan complete source trees during a normal release. Inspect affected modules only when a
gate fails, required evidence is missing, compatibility is unknown, or a dependency is unresolved.

## Scope, order, and versions

- Exclude Changes marked governance-only, `NON_RELEASE_CHANGE`, or `Release Impact: NONE`, even when
  their status is `READY`. They do not receive a Release ID, version bump, Tag, Artifact, or deployment.
- Include only selected `READY` Changes and the union of their actually affected repositories.
- Never publish every governed repository merely because it exists in `SYSTEM_MAP.yaml`.
- Calculate order from current Change dependencies and verified `required` edges. `optional` edges
  inform compatibility checks but do not force atomic release; `none` adds no order.
- Do not hardcode a three-repository chain. In the verified baseline, marketNewsFeed and
  stock-analyzer are parallel Dashboard providers, and stock-analyzer also provides an optional
  lookup to marketNewsFeed.
- Version each changed repository independently. Unchanged repositories receive no version bump,
  Tag, Artifact, or deployment.

## Preserve work and identity

- Preflight current branch, HEAD SHA, working tree, untracked files, upstream/remote state, relevant
  Tags, unfinished Git operations, and worktree conflicts.
- Never reset, discard, clean, secretly stash, rewrite, force-push, or absorb unrelated user work.
  Block on dirty or ambiguous state unless a provably isolated worktree is safe and authorized.
- Production identity is immutable Git Tag + exact Commit SHA + exact Artifact identity. Record an
  image digest when Docker is used. Never use `main`, `HEAD`, or `latest` as production identity.
- Read each target's current `SYSTEM_MAP.yaml` deployment status. An `exact_tag_capable` entry may be
  used for Formal Release only when the persisted Release Manifest already contains the repository's
  immutable Tag, exact SHA, and explicit rollback Tag, and the entry's dry-run resolves the same Tag
  to the same SHA on `origin/main`. Any non-compliant, floating-ref, mismatched, or unverifiable entry
  blocks Formal Release before deployment.
- Exact-Tag capability currently uses `SOURCE_TAG_BUILD` on the NAS. It does not prove Build Once /
  Promote Same Artifact, Registry availability, or an image digest; persist the actual Image ID or
  `ARTIFACT_DIGEST_UNAVAILABLE` honestly and keep the Artifact gate fail-closed when the current
  Release risk requires stronger identity.

## Production baseline and drift gate

- For every affected repository, require a verified `PRODUCTION_BASELINE.yaml` entry before release
  preparation. Copy its current Production Tag to both `previous_version` and `rollback_version`, and
  its exact Commit and available Artifact identity into the Release Manifest. `UNKNOWN` or `BLOCKED`
  rollback state blocks Formal Release.
- During Prepare Release, re-query the actual Production Tag and Commit through the repository's safe,
  read-only runtime/checkout evidence. Do not accept baseline age, local `main`, or the latest Tag as
  proof that Production is unchanged.
- If actual Production Tag or Commit differs from the persisted baseline, record `BASELINE_DRIFT`, stop
  release preparation, and require a separate read-only Production baseline refresh. Never overwrite the
  baseline or infer a new rollback point merely to continue a Release.
- Treat each repository independently: a fresh verified baseline for one repository does not validate another.

## Fail closed

Stop on the first critical gate failure. Persist the real partial state and set `BLOCKED`, `FAILED`,
or `PARTIAL` as appropriate; do not continue downstream, bypass checks, invent a production
baseline, create replacement Tags, or activate features.

Rollback must target a previously confirmed stable Production Tag/Artifact. Record `UNKNOWN` rather
than guessing. For a high-risk Production release, an unknown rollback point is blocking.

## Keep output compact

Successful preparation reports only Release ID, Changes, affected repositories, versions, SHAs,
order, rollback versions, gate result, and `READY_FOR_FORMAL_RELEASE`.

Successful Formal Release reports only Release ID, repository versions, production Tags, deployment
order, smoke/E2E results, production identities, rollback points, and `RELEASED`.

On failure, report `BLOCKED` and the blocking conditions. The persisted Manifest is the detailed
record; chat is never the sole release record.
