# Exact Tag Deployment Contract

Production deployment across the Investment Platform uses one interface:

- Input: an explicit immutable `vMAJOR.MINOR.PATCH` Git Tag.
- Identity: the Tag resolved through `<tag>^{commit}` plus that exact Commit SHA.
- Lineage: the resolved Commit must be reachable from refreshed `origin/main`.
- Source: detached checkout of the resolved Commit; unexpected tracked modifications block deployment.
- Deployment: build and run only the validated exact source. Current artifact model is
  `SOURCE_TAG_BUILD` on the NAS.
- Rollback: invoke the same entry with the explicit previous stable Tag supplied by the Release
  Manifest; the script never guesses a previous version.
- Verification: repository health/status checks and release smoke evidence are recorded by the
  release workflow.

Forbidden production inputs and identities include omitted refs, `main`, `master`, `HEAD`, `latest`,
and `origin/main`. There is no fallback to a branch when Tag validation fails.

Every repository deployment entry must provide safe `--help` and `--dry-run`. Dry-run may fetch and
validate Git metadata, but must not checkout source, write configuration, build, restart, migrate, or
deploy. Image ID/digest must be recorded when reliably available; otherwise record
`ARTIFACT_DIGEST_UNAVAILABLE` rather than infer it.
