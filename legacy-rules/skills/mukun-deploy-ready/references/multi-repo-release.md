# Coordinated Multi-Repository Release

Use this workflow only for repositories the user placed in one release unit. Coordination grants
permission to operate across that unit, not to include every Git repository found on the machine.

## Build one release manifest before writes

Perform a read-only preflight across all in-scope repositories and record:

- exact repository path, effective `AGENTS.md`, remote, production branch, and current worktree;
- intended source branches and immutable tip SHAs;
- dirty, untracked, unpublished, merge/rebase, and worktree state;
- current version, proposed next version, tag format, and whether the repositories share a release
  train or version independently;
- required local gates, remote CI, migration requirements, deployment entrypoint, and rollback;
- dependency edges, minimum compatible contract versions, and upstream-to-downstream release order.

Infer scope from repositories explicitly named by the user, established workspace/project
configuration, dependency manifests, and maintained architecture or release documentation. Do not
scan broad home-directory trees or include a nearby repository merely because it exists. If an
essential repository or dependency boundary cannot be resolved safely, stop before cross-repository
writes and ask one focused question.

Do not move, stash, clean, reset, or absorb unrelated changes. Use separate clean worktrees when an
in-scope checkout is dirty or another task is active. A repository excluded from the release unit
must remain untouched and be listed as excluded.

## Unified freeze

1. Finish the read-only preflight for the whole release unit before mutating the first repository.
2. Lock source SHAs and verify that required changes are committed and available to integrate.
3. Integrate and resolve conflicts using each repository's required PR or merge flow. Update
   cross-repository contract declarations and compatibility documentation where the actual change
   requires it.
4. Derive each repository's version independently unless a documented shared release train applies.
   Update its canonical version source, generated metadata, release notes, and tests as required.
5. Run each repository's release gate on the final integrated tree. Reuse earlier evidence only
   under the unchanged-evidence rules in `SKILL.md`.
6. Recheck all planned production-branch tips and versions before the first final push. Push the
   exact production branches, then create and push only the planned immutable tags. Stop on the
   first failure and report the repositories already changed; never pretend cross-repository Git
   operations are atomic.
7. Return one consolidated manifest mapping repository to commit, version, tag, CI evidence, and
   compatibility constraints. Do not deploy during a freeze.

Prefer completing all validation before any final production-branch push or tag so failures remain
recoverable. Never move or overwrite a published release tag; correct a released mistake with a new
version according to repository policy.

## Unified production

Use the frozen manifest rather than rediscovering floating branches. Before deployment, verify that
every tag still resolves to the recorded commit and satisfies repository ancestry and CI rules.

Deploy in dependency order: data/schema and upstream contract providers first, then adapters or
workers, then downstream APIs and user-facing applications. After each step, run that repository's
health, version, migration, contract, and critical-path checks. Do not continue to a dependent
service when an upstream deployment or compatibility check fails.

On failure, preserve evidence and follow the affected repository's rollback procedure. Report the
release as partial with exact deployed and undeployed tags; do not create replacement tags or roll
back databases unless the applicable repository instructions and user authorization permit it.

## Useful invocation vocabulary

- `统一准备发版` / `统一封板` / `统一发版`: freeze all explicitly in-scope repositories, merge
  their production branches, version and tag them, but do not deploy.
- `统一正式发布` / `统一生产上线`: deploy the exact frozen tags across the release unit in
  dependency order and verify the integrated system.
- `统一封板：合并全部相关仓库 main，打 Tag，不部署`: action-explicit form when the user wants
  the requested boundary repeated in the command; it has the same authorization as “统一封板”.
