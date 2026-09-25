---
name: mukun-deploy-ready
description: >-
  Commit, push, freeze, tag, or deploy one repository or a coordinated set of
  dependent repositories. Use for release preparation, sealing a release,
  merging production branches, unified multi-repository releases, tags,
  production rollout, or release-readiness checks. Follow each repository's
  effective AGENTS.md and require explicit production wording before deployment.
---

# Deploy Ready

Deliver repository changes with the shortest safe path allowed by the user's requested
scope and each repository's effective `AGENTS.md`. This skill defines the user's release
vocabulary, coordinates related repositories, and avoids duplicate validation; it does not
replace repository-specific versioning, testing, deployment, or rollback rules.

## Interpret authorization literally

- **Commit** — “提交代码”: validate and commit the requested repository changes. Do not push.
- **Push** — “推送”: validate, commit if needed, and push the task branch. Do not merge the
  production branch, tag, or deploy.
- **Freeze** — “准备发版”, “封板”, or `release freeze`: complete the release gate, integrate
  the intended changes into the repository's production branch through its required PR or
  merge flow, synchronize release metadata, push the production branch, and create and push
  the immutable release tag. Do not deploy.
- **Production** — “正式发布”, “正式上线”, or “生产上线”: freeze first if necessary, then deploy
  the exact immutable tag and complete production verification and required release records.

An action-specific request authorizes only that action. In particular, “合并 main” authorizes
the named merge but does not by itself authorize a tag or deployment; “打 Tag” does not authorize
deployment. Never reinterpret a merge as a full production rollout.

Treat the Freeze vocabulary above as the user's explicit authorization for its listed Git
operations. An older `AGENTS.md` mapping the same phrase to a lower authorization level does not
silently downgrade this vocabulary. Still obey the repository's required PR, review, CI,
protected-branch, version, and tagging process. If the repository expressly forbids an operation
or an unresolved choice makes it unsafe, report the exact conflict and the smallest resolution.

## Select repository scope

The current repository is the default scope. Use coordinated multi-repository mode only when the
user says “统一准备发版”, “统一封板”, “统一发版”, “全部相关仓库”, “统一正式发布”, lists multiple
repositories, or otherwise explicitly requests one release unit across repositories.

- **Unified freeze** — validate and freeze every in-scope repository as one release unit, merging
  and tagging each repository according to its own rules; do not deploy.
- **Unified production** — deploy the exact frozen tags in dependency order and verify contracts
  between services before continuing downstream.

For coordinated work, read [references/multi-repo-release.md](references/multi-repo-release.md)
before mutating any repository.

## Use repository instructions as the implementation source

Read the effective `AGENTS.md` for every in-scope repository. Use it for the real default and
production branches, required checks, version source, release notes, merge strategy, migration
handling, deployment entrypoint, production verification, and rollback. Do not impose a shared
version number, branch name, language workflow, or deployment mechanism unless the repositories
actually use a shared release train.

## Minimize repeated work without weakening gates

- Start with repository status, relevant diff, and `git diff --check`; inspect broader history,
  tags, worktrees, remotes, and CI only when the requested operation needs them.
- Reuse passing evidence from the same task only while tested files, dependency manifests,
  configuration, generated artifacts, merge resolution, and target base remain unchanged.
- Run the integrated release gate after all in-repository merges and conflict resolutions instead
  of repeating the same full suite around every merge.
- Check remote CI once when accessible. Do not repeatedly poll unchanged state; report when CI
  cannot be verified.

A required failing check must be fixed or reported. Speed never justifies skipping a gate.

## Preserve work and release identity

- Preserve unrelated changes and stage explicit files. Reuse the active task branch when valid;
  use a clean worktree when required by repository policy or existing work.
- Confirm exact source tips and committed state before integration. Preserve both valid sides when
  resolving conflicts.
- Derive versions from each repository's policy and actual change. Tags are immutable and must
  identify the exact pushed production-branch commit intended for deployment.
- Never deploy a task branch, dirty worktree, floating branch, or tag that is not reachable from
  the repository's pushed production branch when the repository requires that ancestry.
- Do not delete branches unless the user separately authorizes cleanup and merge evidence is
  sufficient.

## Report the release unit

Report the authorization mode, every repository in scope, dependency order, branch and commit,
version and tag, push/merge/tag/deploy state, validations run or reused, dirty or excluded
repositories, blockers, and the one next step requiring more authority. For a freeze, explicitly
say that production deployment has not run. For unified work, provide one consolidated result
rather than requiring a separate user instruction per service.
