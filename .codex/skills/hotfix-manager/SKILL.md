---
name: hotfix-manager
description: Govern urgent Investment Platform production fixes from the verified deployed tag and commit through a minimal hotfix Change, PATCH release, fix-forward and safe cleanup. Use for production incidents or hotfix requests; do not deploy floating main or proceed when production identity is unknown.
---

# Hotfix Manager

Restore production with the smallest verified change while keeping the normal governance record intact.

## Establish the baseline

Read `AGENTS.md`, `SYSTEM_MAP.yaml`, `RELEASE_RULES.md`, and the affected repository instructions. Obtain the actual
Production Tag, Commit SHA, Artifact identity/digest, affected environment and last stable rollback point from the
running environment or authoritative deployment record. If identity is `UNKNOWN` or inconsistent, stop before
creating or releasing the hotfix.

## Create and validate the hotfix

1. Create a Hotfix Change with a new `CHG-YYYYMMDD-NNN` and record impact, incident evidence, rollback and
   fix-forward requirements.
2. Create `hotfix/<CHANGE_ID>-description` from the verified Production Tag/Commit. Use `main` only when its exact
   Commit equals the production baseline.
3. Make only the minimal recovery change. Do not absorb unreleased `main` features or unrelated work.
4. Run the affected repository's full relevant tests plus contract, migration, integration and critical-path smoke
   checks proportional to the incident.
5. Select a PATCH version unless the actual compatibility impact requires a different explicit decision.

## Release and fix forward

Use `mukun-release-manager` semantics: preparation creates a persisted Manifest but no Tag or deployment; only explicit
“正式发布” authorizes the immutable hotfix Tag, exact Artifact deployment and production verification. Never deploy
the whole of `main` merely because it contains the fix.

After production is stable, fix-forward the hotfix into `main` and any maintained line through their required PR
flows, rerun affected checks, and update Change/Release evidence. Clean up the hotfix branch only with separate
authorization and complete merge/worktree/PR/CI evidence. Never move an existing Tag.
