# Exact Tag Deployment Governance Report

- Change: `CHG-20260926-000`
- Validation date: 2026-09-26
- Scope: implementation, validation, reviewed merge, remote sync, and branch cleanup
- Production deployment: not performed
- Main status: `EXACT_TAG_CAPABLE` is merged and remotely synchronized for all three business repositories.

| Repository | Before behavior | After behavior | Exact Tag | Main fallback removed | Lineage | Dry-run | Health behavior | Artifact identity | Remaining gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| marketNewsFeed | No argument; checkout/pull floating `main` | Requires SemVer Tag, resolves `Tag^{commit}`, validates `origin/main`, detached exact checkout | YES | YES | PASS | PASS | Existing Compose status retained; `/api/health` remains release smoke evidence | Local Docker Image ID when available; digest unavailable | No canonical app `VERSION`; no Registry promotion/digest |
| stock-analyzer | No release ref; checkout/pull floating `main`; Compose image named `latest` | Requires SemVer Tag, resolves `Tag^{commit}`, validates `origin/main`, detached exact checkout, SHA-named local image | YES | YES | PASS | PASS | Scheduler and `/api/health` waits preserved; config/backfill unchanged | SHA-named local image plus Docker Image ID when available; digest unavailable | No Registry promotion/digest |
| investment-research-dashboard | Optional arbitrary ref defaulting to `main` | Requires SemVer Tag, resolves `Tag^{commit}`, validates `origin/main`, passes exact SHA to restricted launcher | YES | YES | PASS | PASS | Existing Compose health and Production smoke contract retained; launcher completion reported | Restricted launcher does not return Image ID/digest | Exact-SHA launcher behavior and Artifact identity require NAS verification |

## Validation Evidence

- `bash -n deploy.sh`: PASS for all three repositories.
- `./deploy.sh --help`: PASS with no deployment side effects.
- `./deploy.sh` without a Tag: non-zero `RELEASE_TAG_REQUIRED` before fetch/build/deploy.
- `main`, `HEAD`, `latest`, and `origin/main`: non-zero `INVALID_RELEASE_TAG`.
- `v999.999.999-does-not-exist`: non-zero `INVALID_RELEASE_TAG`.
- nonexistent well-formed `v999.999.999`: non-zero `TAG_NOT_FOUND`, with no fallback.
- Existing annotated Tags resolved through `^{commit}`, passed `origin/main` lineage, and completed
  dry-run without changing Branch, HEAD, or working tree:
  - marketNewsFeed `v2.3.3` → `deb075480b57f448b10d6de6880401a7a23fdc47`;
  - stock-analyzer `v3.19.3` → `5571647bb826f1397fbae96b9c6a502425c02cda`;
  - investment-research-dashboard `v0.13.1` → `8ee167fb63870696b79d18f0667c00a61d4d1d62`.
- No Docker command, checkout, configuration write, migration, restart, NAS launcher, or Production
  action was executed by validation.
- Final business `main` identities: marketNewsFeed `138ea7cbebfa17df0b27f52b7b15e2907a8eec65`,
  stock-analyzer `6feda48e3803bbbf9b9836c8a27712f6bb746f83`, and investment-research-dashboard
  `8625a61d9841e5df94588e5781098d2980d4ac25`.
- GitHub Actions is not configured for marketNewsFeed or stock-analyzer. Dashboard CI #115 passed on
  the Change Branch and CI #116 passed on `main`; no CI result is inferred for repositories without CI.

## Artifact Model

Current model: `SOURCE_TAG_BUILD`.

marketNewsFeed and stock-analyzer can report local Image IDs after an actual build. Dashboard's
restricted launcher does not currently return a reliable Image ID or digest. This Change does not
claim Build Once / Promote Same Artifact, Registry promotion, or digest-pinned deployment.
