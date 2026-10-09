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

## REL-20260926-001 refresh (2026-09-27)

- `stock-analyzer` Production is now immutable Tag `v3.20.0` at
  `0626c1704569550cc6381b1ff3079df250f30865`. Both API and scheduler containers run the exact-SHA image
  `sha256:c722c8db7e4100560642494f1cd35de5fe4597275f41619785c1d1467f1d96c3`; health reports application
  version `3.20.0`, the scheduler startup marker is present, and the new limit-up/swing contracts passed
  authenticated read-only smoke checks.
- `investment-research-dashboard` Production is now immutable Tag `v0.14.0` at
  `ca6f06de90dfa284cf359a13cf83afa92fb48fac`. In-container build metadata matches the version and Commit;
  API and Web containers are healthy, `/api/v1/health` passes, and `/api/v1/readiness` remains ready.
- Before Provider deployment, the real `stock_analyzer` database was backed up in PostgreSQL custom format at
  `/volume1/docker/stock-analyzer/backups/REL-20260926-001/stock-analyzer-db-pre-v3.20.0.dump`; the 278,685,490-byte
  dump produced a readable 122-line catalog. The prior `.env` was also retained as
  `/volume1/docker/stock-analyzer/.env.pre-REL-20260926-001`.
- Registry digests remain unavailable. The baseline therefore records exact source Tags/SHAs and local Docker
  Image IDs. The limit-up UI remains disabled pending five real trading-day snapshots, and the next scheduled
  trading-day scan will create the first V5.1 swing candidate snapshot; no weekend backfill was performed.

## Read-only Tailscale refresh (2026-10-09)

- Scope: `stock-analyzer` and `investment-research-dashboard` only. `marketNewsFeed` was not reverified.
  The Tailscale NAS peer was online; port 9352 and SSH succeeded using the previously trusted host key.
- `stock-analyzer` Production checkout has no tracked changes at exact Tag `v3.20.0`, Commit
  `0626c1704569550cc6381b1ff3079df250f30865`. Both running containers use Image ID
  `sha256:c722c8db7e4100560642494f1cd35de5fe4597275f41619785c1d1467f1d96c3`;
  `/api/health` returned HTTP 200 and application version `3.20.0`. Its pre-existing untracked `backups/`
  directory was preserved.
- Dashboard Production checkout is clean at exact Tag `v0.14.1`, Commit
  `b7e005c2613c3e9e23fe154327cb5e608caa1a40`. In-container build metadata reports that version and
  Commit, build time `2026-09-27T16:33:22+0800`, and `production` environment. API and Web are running and
  Docker-healthy at Image IDs `sha256:25a4592c53809ded583e57b77031490cd11a773616471425c5bbf9f61831e058`
  and `sha256:1fbcd36cdc75c5dc4e94d4333736fd26f4d00513932bd6009ed8c1b8a3a3fb3d` respectively.
  `/api/v1/health` and `/api/v1/readiness` returned HTTP 200; unauthenticated `/api/v1/system/version`
  returned 401, so no credential was used.
- The previous baseline's Dashboard `v0.14.0` was stale after `REL-20260927-001`; it is now the rollback Tag.
  `v0.14.0^{commit}` resolves to `ca6f06de90dfa284cf359a13cf83afa92fb48fac`, and both previously
  recorded API/Web rollback Image IDs remain present locally. The current Image IDs match the prior Release
  Manifest. No registry digest is available.
- No Production configuration, code, Tag, container, database, or Feature Flag was changed during this refresh.

## REL-20261009-001 release refresh (2026-10-09)

- Scope: `stock-analyzer` and `investment-research-dashboard` only; `marketNewsFeed` was not deployed.
- `stock-analyzer` is at exact annotated Tag `v3.21.0`, Commit
  `910befbc62ee4c6a3284e7e750acab7661a3e4b6`. Both API and scheduler run Image ID
  `sha256:49748c11b9a441f17f7de00f65a9ced9ea0602158e1c0a7ce17b29e94e50d7dc`.
  API health reports version `3.21.0`. Authenticated production v2 day/week/month and exclusive
  history-cursor checks passed. The deployment SSH session dropped during optional stock-sync
  dry-run; the exact Tag, runtime, scheduler, health and contract were independently verified.
- Dashboard is at exact annotated Tag `v0.15.0`, Commit
  `7b23ff0ea16af8372bb48db4a24cec225200a374`. Runtime metadata reports version `0.15.0`,
  build time `2026-10-09T13:09:21+0800`, and production environment. API Image ID is
  `sha256:aa83631d0b637b701aaa692883a5979e8201857dc63635c7ec68c744b247d359`;
  activated Web Image ID is
  `sha256:e33dde272efc165fb9297d49aa7302b706070a572bb78f7a33321d822e4fb4ec`.
  Both containers are Docker-healthy; API health and readiness are HTTP 200. The server-side
  Dashboard client validated the live Provider's v2 contract, including older-page cursor.
- `VITE_PRO_KLINE_ENABLED=true` appears once in the production `.env`; the pre-activation copy is
  `/volume1/docker/investment-research-dashboard/.env.bak.REL-20261009-001-pre-activation`.
  The public HTTPS endpoint `https://invest.freemumu.top:9527` serves the activated
  `ProfessionalStockChart-CjmuMruT.js` chunk with valid TLS and HTTP 200. Staging visually
  exercised the same frozen code with live sourced candles, MA, amount and MACD. Authenticated
  production detail rendering was not inspected because the browser session redirected to login;
  no credential or CAPTCHA bypass was attempted.
- Fresh pre-deployment custom-format PostgreSQL backups and SHA-256 values are recorded in
  `releases/REL-20261009-001.yaml`. Registry digests remain unavailable; exact Tags, SHAs and
  observed local Image IDs identify the deployed artifacts. A background capital-flow sync
  returned one stock-analyzer HTTP 502 during activation, while the chart path and readiness
  passed; monitor that unrelated integration separately.
