# Formal Release

Requires explicit Production authorization. If no prepared Manifest exists, do the concise preparation in
prepare-release.md in the same turn. Follow RELEASE_RULES.md's personal-use routine by default.

## Execute once

1. Freeze the selected merged-main SHA/version/candidate and retained Production rollback identity. Confirm
   applicable evidence and authorization; record READY_FOR_FORMAL_RELEASE then IN_PROGRESS locally.
2. Create/push immutable Tags at those SHAs. Fetch precise Tags/main as the NAS deploy user. Select the same
   CI artifacts; Tags do not rebuild. Never include unrelated repositories or a newer floating main.
3. Call image_release.py deploy once. It already verifies CI, cached/pinned images, live baseline, protected
   readable backup, exact checkout, dependency order, running identity, health/version and production smoke.
   Do not routinely prepend preflight/prefetch or append verify, a full production acceptance script, clone
   restore, runner rollback drill or browser suite. A targeted extra check is required only for an affected
   boundary not covered by existing smoke; use the risk table, not a blanket test list.
4. Save the returned receipt; reference its actual identity, time and backup details from the Manifest/baseline,
   recording only rollback context and limitations not already captured there;
   mark RELEASED only on real success. Combine governance changes into one closeout commit/PR with authorization.
   Safe branch cleanup and optional page inspection follow without delaying successful deployment reporting.

## Failure and timing

Stop at critical failure, preserve the real partial receipt/journal, do not deploy downstream or claim success.
Resume only the same frozen plan; unknown drift blocks. Roll back to the retained stable artifact under the
recorded plan, never invent database downgrade or move Tags. A network/migration timeout may exceed the target;
do not kill a live migration merely to meet five minutes.

Target ~300 seconds for routine handling, timed from the user’s submit/merge/prepare request when that
preceded formal authorization, or from the direct formal request. Include commit/merge/CI waiting, assistant
preparation, Tags and deployment. Report prepare/formal phase durations and handling total, with user approval
waiting separate; prepare-only authorization never permits deployment. Review existing evidence once in ~30–60
seconds; investigate only missing/conflicting evidence. Report the total user wait as well as its breakdown.
Keep archival/cleanup asynchronous and explicitly report any unfinished closeout. Use one compact result: Release, versions,
verification result, access link, rollback availability and any actual limitation.
