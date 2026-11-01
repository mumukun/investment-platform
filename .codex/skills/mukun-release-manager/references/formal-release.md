# Formal Release

Requires explicit Production authorization. If no frozen execution plan exists, do the concise preparation in
prepare-release.md in the same turn. Follow RELEASE_RULES.md's personal-use routine by default.

## Execute the frozen plan

1. Freeze the selected merged-main SHA/version/candidate and retained Production rollback identity. Confirm
   applicable evidence and authorization; record READY_FOR_FORMAL_RELEASE then IN_PROGRESS locally.
2. Create/push immutable Tags at those SHAs. Fetch precise Tags/main as the NAS deploy user. Select the same
   CI artifacts; Tags do not rebuild. Never include unrelated repositories or a newer floating main.
3. Run the same restricted deployment entry, preferably as an independent NAS-local task using
   [docs/image-release.md: NAS独立运行与回执恢复](../../../../docs/image-release.md#nas独立运行与回执恢复).
   The synchronous image_release.py deploy --receipt/--manifest path remains available; it is not asynchronous.
   Detached execution must first use the existing local verify-ci check once; synchronous deploy includes
   that check itself. Both paths retain pinned images, live baseline, the reviewed backup decision,
   exact checkout, dependency order, running identity, health/version and production smoke.
   Do not routinely prepend preflight/prefetch or append verify, a full production acceptance script, clone
   restore, runner rollback drill or browser suite. A targeted extra check is required only for an affected
   boundary not covered by existing smoke; use the risk table, not a blanket test list.
4. Collect the actual receipt and generate the Manifest with the existing record entry when detached; reference its actual identity, time and backup details from the baseline,
   recording only rollback context and limitations not already captured there;
   mark RELEASED only on real success. Combine governance changes into one closeout commit/PR with authorization.
   Safe branch cleanup and optional page inspection follow without delaying successful deployment reporting.

Once the candidate is ready and formal authorization exists, continue the frozen Tag/fetch/deploy chain
without another evidence-review phase. Prepare target/baseline details during CI waiting. Record a concrete
blocking command if candidate-to-launch exceeds the roughly two-minute target.

## Failure and timing

Stop at critical failure, preserve the real partial receipt/journal, do not deploy downstream or claim success.
A lost SSH channel alone means execution status unknown. Inspect the existing task and journal before
relaunching; collect finished receipts, keep observing active work, and resume a stopped incomplete task
only with the same frozen plan. Unknown drift blocks. Roll back to the retained stable artifact under the
recorded plan, never invent database downgrade or move Tags. A network/migration timeout may exceed the target;
do not kill a live migration merely to meet five minutes.

Target ~300 seconds for routine handling, timed from the user’s submit/merge/prepare request when that
preceded formal authorization, or from the direct formal request. Include commit/merge/CI waiting, assistant
preparation, Tags and deployment. Report prepare/formal phase durations and handling total, with user approval
waiting separate; prepare-only authorization never permits deployment. Review existing evidence once in ~30–60
seconds; investigate only missing/conflicting evidence. Report the total user wait as well as its breakdown.
Keep archival/cleanup asynchronous and explicitly report any unfinished closeout. Use one compact result: Release, versions,
verification result, access link, rollback availability and any actual limitation.

Report first verified service availability separately from late receipt recovery and optional closeout.
Do not present accumulated command seconds as total user wait, or attribute unrecorded gaps to CI/network.
