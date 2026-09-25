# Production Baseline Verification Report

- Governance Change: `CHG-20260926-001`
- Verified at: `2026-09-26T01:11:11+08:00`
- Access: existing configured SSH alias; no new credential created
- Artifact model: `SOURCE_TAG_BUILD`
- Production mutations: none

## marketNewsFeed

- Runtime evidence: `/api/health` returned HTTP 200 with `ok=true`, service enabled and authentication
  configured. Its reported `version=1.0` is the Admin API version, not a canonical application version.
- Git evidence: the clean Production checkout HEAD is
  `deb075480b57f448b10d6de6880401a7a23fdc47`; annotated Tag `v2.3.3^{commit}` resolves to the same SHA.
- Application version: `2.3.3`, derived from the verified exact Tag because no canonical root `VERSION` exists.
- Artifact evidence: running container `marketnewsfeed-market-news-feed-1`; Image ID
  `sha256:517b71ef8f501f9a64a22d878653178c5b6550449709080583eb3edf6ced1c05`; image labels contain the
  same app Tag and Commit. No registry digest is available.
- Health: `HEALTHY` for the available service-level evidence; no separate business-readiness endpoint exists.
- Rollback eligibility: `VERIFIED`; the exact Tag passed the current deploy entry dry-run and main-lineage gate.
- Confidence: `HIGH`.

## stock-analyzer

- Runtime evidence: `/api/health` returned HTTP 200 with `ok=true` and version `3.19.3`; the running API
  module also reports `APP_VERSION=3.19.3`.
- Git evidence: the clean Production checkout HEAD is
  `5571647bb826f1397fbae96b9c6a502425c02cda`; annotated Tag `v3.19.3^{commit}` resolves to the same SHA.
- Artifact evidence: `stock-watch` and `stock-api` share Image ID
  `sha256:575d5193c39359181190e5f7784ecc92a84b1e320a45e6c077368d675729db0d`. The current image reference
  remains legacy `stock-analyzer:latest`, with no app Commit label or registry digest.
- Health: `HEALTHY`; both containers are running, the API health check passes, the scheduler startup marker
  exists, and the last 100 scheduler log lines contain no error marker. One older marker exists within the
  last 500 lines and remains operational evidence for later review, not a current failed gate.
- Rollback eligibility: `VERIFIED`; the exact Tag passed the current deploy entry dry-run and main-lineage gate.
- Confidence: `MEDIUM` because the running Image ID is not labeled with the app Commit.

## investment-research-dashboard

- Runtime evidence: `/api/v1/health` returned HTTP 200 with PostgreSQL healthy; `/api/v1/readiness` returned
  `ready=true` with required `market-dashboard` and `us-market` checks ready. Authenticated `/data-status`
  and `/system/version` returned 401 without credentials, so no credential was requested or exposed.
- Runtime version evidence: safe in-container `build_metadata()` returned application version `0.13.1`,
  Commit `8ee167fb63870696b79d18f0667c00a61d4d1d62`, build time `2026-09-25T10:16:11+08:00`, and
  environment `production`.
- Git evidence: the clean Production checkout HEAD is the same Commit; annotated Tag `v0.13.1^{commit}`
  resolves to that SHA. This verifies the restricted launcher requested Tag → runtime SHA path.
- Artifact evidence: web Image ID
  `sha256:c9102b716b343c546f2bf29eefc174c283d36b752d7ae4a87dabe01840621d88`; API Image ID
  `sha256:692924aa3529e346557457598407d802464c1af103d7a3881a84ab07718bcf5f`. Both local image refs remain
  `latest`-style Compose names and have no registry digest. OCI revision/version labels on the API image are
  inherited base-image metadata and are not treated as application identity.
- Health: `HEALTHY`; both containers also report Docker health status `healthy`.
- Rollback eligibility: `VERIFIED`; the exact Tag passed the current deploy entry dry-run and main-lineage gate.
- Confidence: `HIGH` for Tag/SHA/runtime identity; artifact identity remains Image-ID-only.

## Reconciliation and Drift

- No prior persisted Production baseline existed, so this record establishes the first drift comparison point.
- Local `main` being ahead of Production is expected platform behavior and is not baseline drift.
- No Tag/SHA conflict was found across runtime, Production checkout, or Tag resolution.
- Future Prepare Release must re-read actual Production Tag and Commit. Any mismatch with
  `PRODUCTION_BASELINE.yaml` is `BASELINE_DRIFT` and blocks release preparation until the baseline is refreshed.

## Known Gaps

- No registry digest or build-once/promote artifact chain exists.
- stock-analyzer and Dashboard currently use legacy/latest-style local image references.
- stock-analyzer's running Image ID lacks an application Commit label.
- marketNewsFeed still lacks a canonical root `VERSION` and runtime application-version endpoint.
- Dashboard authenticated version/data-status endpoints could not be queried without credentials; the baseline
  used safe in-container version metadata and unauthenticated readiness instead.
