# Formal Release

Use this workflow only after explicit Production authorization for a specific prepared Release.

## Revalidation

1. Read the persisted Manifest; require status `READY_FOR_FORMAL_RELEASE`.
2. Reconfirm Release ID, included Changes, affected repositories, environment, versions, exact SHAs,
   Tags, Artifacts, dependencies, release order, and rollback points.
3. Re-run concise Git preflight and verify frozen SHAs, relevant remote state, CI/test evidence, and
   critical gates are unchanged and current.
4. Require every target deployment implementation to prove it deploys the exact recorded Tag or
   Artifact. If it falls back to floating `main`/`latest`, set `BLOCKED` before creating release
   side effects.

## Execution

1. Set the Manifest to `IN_PROGRESS` and persist the start time.
2. Create an immutable `vMAJOR.MINOR.PATCH` Tag for each affected repository at its recorded SHA;
   never move or overwrite an existing Tag.
3. Push only the explicitly planned Tag when push is part of the current authorization.
4. Build or select the exact Tag/SHA-derived Artifact and record identity plus digest before deploy.
5. Deploy in the dynamic dependency order. After each repository, run its version check, health,
   migration verification, and smoke test before continuing.
6. Stop downstream deployment when an upstream required edge or compatibility gate fails.
7. Run affected Contract and Integration verification, plus a small stable critical-path E2E when
   required by the Change risk.
8. Activate a Feature Flag only when recorded in the Manifest and only after deployment and
   end-to-end verification; record its disable path.
9. Record the actual Production Tag, SHA, Artifact identity/digest, deployment time, verification,
   known limitations, and rollback point for every released repository.
10. Mark the Release and included Changes `RELEASED` only after all required production evidence is
    persisted.
11. During closeout, clean up only temporary branches explicitly associated with this Release and
    only when every safety condition in `manifest-and-gates.md` is proven.

## Failure handling

At the first critical failure:

- stop immediately and do not continue to dependent repositories;
- preserve logs and evidence without exposing secrets;
- record exactly which Tags were created/pushed and which Artifacts were deployed;
- set the honest Manifest state (`BLOCKED`, `FAILED`, `PARTIAL`, or `ROLLED_BACK`);
- follow the recorded repository rollback/fix-forward plan without inventing database downgrade;
- do not create replacement Tags or deploy floating branches to make the run appear complete.

## Compact result

Return:

- Release ID
- Repository versions and Production Tags
- Deployment order
- Smoke and critical-path E2E results
- Exact Production identities
- Rollback points
- `RELEASED`

If unsuccessful, return `BLOCKED` and only the blocking conditions plus the persisted partial state.
