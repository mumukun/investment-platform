#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <repository> <repository-path> <existing-tag> [...]"
}

if [ "$#" -eq 0 ] || [ $(( $# % 3 )) -ne 0 ]; then
  usage >&2
  exit 2
fi

run_expect_failure() {
  local expected_code="$1"
  shift
  local output
  local status
  set +e
  output="$("$@" 2>&1)"
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    echo "Expected failure but command succeeded: $*" >&2
    exit 1
  fi
  if ! grep -Fq "ERROR_CODE=${expected_code}" <<<"$output"; then
    echo "Expected ERROR_CODE=${expected_code}, got:" >&2
    printf '%s\n' "$output" >&2
    exit 1
  fi
}

while [ "$#" -gt 0 ]; do
  repository="$1"
  repository_path="$2"
  existing_tag="$3"
  shift 3

  deploy_script="${repository_path}/deploy.sh"
  if [ ! -x "$deploy_script" ]; then
    echo "${repository}: deploy.sh is missing or not executable" >&2
    exit 1
  fi

  branch_before="$(git -C "$repository_path" branch --show-current)"
  head_before="$(git -C "$repository_path" rev-parse HEAD)"
  status_before="$(git -C "$repository_path" status --porcelain=v1)"

  bash -n "$deploy_script"
  help_output="$($deploy_script --help)"
  grep -Fq 'Usage:' <<<"$help_output"
  grep -Fq '<release-tag>' <<<"$help_output"

  run_expect_failure RELEASE_TAG_REQUIRED "$deploy_script"
  for floating_ref in main HEAD latest origin/main; do
    run_expect_failure INVALID_RELEASE_TAG "$deploy_script" "$floating_ref" --dry-run
  done
  run_expect_failure INVALID_RELEASE_TAG "$deploy_script" v999.999.999-does-not-exist --dry-run
  run_expect_failure TAG_NOT_FOUND "$deploy_script" v999.999.999 --dry-run

  expected_commit="$(git -C "$repository_path" rev-parse --verify "${existing_tag}^{commit}")"
  dry_run_output="$($deploy_script "$existing_tag" --dry-run)"
  grep -Fq "RELEASE_TAG=${existing_tag}" <<<"$dry_run_output"
  grep -Fq "RELEASE_COMMIT_SHA=${expected_commit}" <<<"$dry_run_output"
  grep -Fq 'DEPLOYMENT_RESULT=DRY_RUN' <<<"$dry_run_output"
  grep -Fq 'HEALTH_RESULT=NOT_RUN' <<<"$dry_run_output"

  if [ "$(git -C "$repository_path" branch --show-current)" != "$branch_before" ] ||
     [ "$(git -C "$repository_path" rev-parse HEAD)" != "$head_before" ] ||
     [ "$(git -C "$repository_path" status --porcelain=v1)" != "$status_before" ]; then
    echo "${repository}: validation changed branch, HEAD, or working tree" >&2
    exit 1
  fi

  echo "${repository}: PASS tag=${existing_tag} commit=${expected_commit}"
done
