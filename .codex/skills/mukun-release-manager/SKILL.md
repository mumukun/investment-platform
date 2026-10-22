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

## Default: personal-use routine release

Follow the four-step routine in `RELEASE_RULES.md`. Reuse exact main CI/candidate and unchanged-boundary
evidence. Do not repeat full restore, old-image compatibility, runner recovery/rollback, both transport modes,
or a second verify for every release. Drills are disabled by default, including ordinary additive migrations
and deployment changes. Prefer focused local tests; explain a concrete unresolved data-loss risk before
considering a minimal extra validation. Do not automatically run clone/restore/old-image/rollback tools.
Use the existing deploy entry once; it includes baseline, the reviewed backup decision, identity, health and smoke.
New plans use per-repository database_backup per RELEASE_RULES: skip reviewed non-destructive,
rollback-compatible changes; table/full backup for data risk. Record SKIPPED honestly. Legacy plans without
the field retain full backup. Independent scheduled backup coverage must not be assumed.
Start elapsed timing at the user’s submit/merge/prepare request, or formal request when direct; target about
five minutes for routine handling. Include commits/merges/CI waiting/assistant preparation, not only deployment.
For separate prepare/formal authorization report both phases and actual handling total; label user approval
waiting separately, never deploy on prepare-only wording. Assistant evidence review targets 30–60 seconds;
move required development verification before development completion, reuse it during release, and report
missing evidence immediately. One chat owns release; exchange final evidence once, not repeated coordination.
No separate version, READY, preparation or baseline-refresh PR for routine releases. Keep version updates
in the business PR; record READY locally after its merge/checks, then batch governance closeout once.
Use compact Change/Manifest records and link existing CI/candidate/receipt detail instead of duplicating it.
Do not add a second full code review, a rollout observation period or a new flag for ordinary personal-use
features. Cleanup/archive follows deployment. Freeze once; later unrelated main changes belong to another release.
Never claim an unready/failed release succeeded or hide waiting outside the reported elapsed time.

## Select exactly one authorization mode

- **PREPARE RELEASE** — selected by “准备发版”, “准备发布”, “封板”, “检查是否可以发布”,
  `release readiness`, or `prepare release`. Read
  [references/prepare-release.md](references/prepare-release.md). This mode never creates or pushes
  a formal Tag, deploys Production, activates a feature, or marks a Release `RELEASED`.
- **FORMAL RELEASE** — selected only when the user explicitly authorizes “正式发布” or an
  unambiguous equivalent for the current Release and Production environment. Read
  [references/formal-release.md](references/formal-release.md). An explicit formal request may include
  concise preparation in the same turn; a separate prepare request/approval is not required.

An action-specific request such as “打 Tag” or “部署某环境” authorizes only that named action; do
not silently upgrade it to a complete Formal Release. If the requested action would break platform
governance, stop and report the conflict.

For either mode, read [references/manifest-and-gates.md](references/manifest-and-gates.md) before
release mutations.

## Read persisted state before code

Read missing or changed context in this order; reuse already-read unchanged rules:

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
- Prefer the verified `CI_BUILD_ONCE` candidate entry for stock-analyzer and Dashboard. Legacy exact-Tag
  capability uses `SOURCE_TAG_BUILD` on the NAS. It does not prove Build Once /
  Promote Same Artifact, Registry availability, or an image digest; persist the actual Image ID or
  `ARTIFACT_DIGEST_UNAVAILABLE` honestly and keep the Artifact gate fail-closed when the current
  Release risk requires stronger identity.
- A candidate_image_entry marked NEEDS_TARGET_VERIFICATION is not an approved production entry.
  For CI_BUILD_ONCE follow docs/image-release.md and RELEASE_RULES sections 4–5: verify frozen-SHA CI,
  exact candidate artifact, digest/config IDs and target evidence. Formal Tag creation must reuse
  that image without rebuilding. Persist the executable plan and receipts alongside the Manifest.
  Missing target or offline identity evidence blocks switching models; never silently fall back.

## Production baseline and drift gate

- For every affected repository, require a verified `PRODUCTION_BASELINE.yaml` entry before release
  preparation. Copy its current Production Tag to both `previous_version` and `rollback_version`, and
  its exact Commit and available Artifact identity into the Release Manifest. `UNKNOWN` or `BLOCKED`
  rollback state blocks Formal Release.
- During routine Prepare, reuse the latest verified Production release receipt/baseline. The NAS deployer
  validates real image/version/checkout drift at the actual switch. Do not run a separate baseline refresh
  task or repeated remote probes for an unchanged, already verified deployment implementation.
- Unexplained drift or unknown rollback identity still blocks. Investigate only the affected repository;
  do not silently overwrite the baseline to continue.
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
