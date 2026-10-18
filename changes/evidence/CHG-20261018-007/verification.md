# CHG-20261018-007 next-session verification

Final scope: short-nextday-tp-close-v1, preset +3% single upper barrier theoretical limit-touch fill, otherwise next-session close; no fixed stop or 3/5-day outcomes. Selection rules and swing remain unchanged. Prior local five-day implementation evidence is superseded.

- Provider unittest: 426 passed with 5 existing skips; configuration and compile PASS.
- Provider isolated PostgreSQL: 19 short ledger tests PASS, including losses, flat, missing next session without substitution, corporate-action vintage, frozen raw entry, final empty run, same-day reentry and pagination-independent statistics. Source-format replay test uses raw closes from quote archive when adjusted bars omit them.
- Consumer pytest: 211 PASS on fresh owned PostgreSQL, excluding existing seat_tracking module that targets a separate DB. New strict contract tests: 21 PASS.
- Frontend: 183 PASS, production typecheck/build PASS; Ruff PASS; Alembic upgrade/check PASS (no Dashboard migration).
- boundary.json: real Provider TestClient HTTP/auth → Consumer urllib/parser → Dashboard read routes, isolated synthetic PostgreSQL, 2 entries / 1 settled at +3% and 1 pending. Date cutoff, dry-run and read-only behavior PASS. This is synthetic integration, not live profitability.
- Read-only live source check: Friday 2026-10-16 latest same-day closing short batch has 1 research candidate / 0 actionable; noon actionable status is not eligible as a closing purchase. Full daily raw quote archive contains 5577 rows. Historical coverage may legitimately have zero eligible entries; never fabricate them.

Existing daily source and NAS proxy boundary unchanged; use existing Sina qfq fetch/save and shared daily maintenance lock. No new fees model or external dependency. Full production browser/mobile/keyboard manual inspection not performed; price target is theoretical, before costs and no guarantee of queue fill. Post-deployment verification belongs in the release receipt/business evidence.
