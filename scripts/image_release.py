#!/usr/bin/env python3
"""Validate frozen image plans and invoke the restricted NAS entrypoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

COMPONENTS = {
    "stock-analyzer": {"app": ("stock-api", "stock-watch")},
    "investment-research-dashboard": {"api": ("api",), "web": ("web",)},
}
FLAGS = {"VITE_LIMIT_UP_LADDER_ENABLED", "VITE_PRO_KLINE_ENABLED", "VITE_MARKET_STRUCTURE_ENABLED"}
SHA = re.compile(r"[0-9a-f]{40}")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
IMAGE_ID = re.compile(r"sha256:[0-9a-f]{64}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frozen_plan_hash(plan):
    identity = {key: value for key, value in plan.items()
                if key not in {"authorization", "transport"}}
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()


def service_components(repository, metadata):
    """Freeze runtime membership per artifact; old manifests retain two stock services."""
    default = COMPONENTS[repository]
    selected = metadata.get("runtime_services", default)
    require(isinstance(selected, dict) and set(selected) == set(default), "invalid runtime service components")
    result = {}
    for component, required in default.items():
        values = selected[component]
        allowed = set(required) | ({"stock-data"} if repository == "stock-analyzer" else set())
        require(isinstance(values, (list, tuple)) and all(isinstance(v, str) for v in values)
                and len(values) == len(set(values))
                and set(required) <= set(values) <= allowed, "invalid runtime service membership")
        result[component] = tuple(values)
    return result


def database_backup_policy(entry):
    # Historical frozen plans retain their original full-backup behavior.
    if "database_backup" not in entry:
        return {"mode": "full"}
    policy = entry["database_backup"]
    require(isinstance(policy, dict), "database_backup must be an object")
    require(set(policy) <= {"mode", "data_impact", "rollback_compatible", "reason", "evidence", "tables"},
            "unknown database backup policy field")
    mode, impact = policy.get("mode"), policy.get("data_impact")
    require(isinstance(mode, str) and mode in {"skip", "tables", "full"}, "invalid database backup mode")
    require(isinstance(impact, str) and impact in {"none", "additive", "destructive", "unknown"},
            "database data impact review required")
    require(isinstance(policy.get("rollback_compatible"), bool), "database rollback compatibility review required")
    for key in ("reason", "evidence"):
        require(isinstance(policy.get(key), str) and bool(policy[key].strip()), "database backup " + key + " required")
    tables = policy.get("tables", [])
    require(isinstance(tables, list), "backup tables must be a list")
    if mode == "skip":
        require(impact in {"none", "additive"} and policy["rollback_compatible"],
                "skip requires reviewed non-destructive changes and compatible code rollback")
    if mode == "tables":
        require(impact != "unknown" and bool(tables), "table backup requires a known scope")
        require(all(isinstance(table, str) and re.fullmatch(r"[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*", table)
                    for table in tables), "exact schema-qualified backup table names required")
        require(len(tables) == len(set(tables)), "duplicate backup table")
    else:
        require(not tables, "tables only apply to table backup mode")
    return dict(policy)


def image_pattern(repository, component):
    suffix = "" if repository == "stock-analyzer" else "-" + component
    return rf"ghcr\.io/mumukun/{repository}{suffix}@sha256:[0-9a-f]{{64}}"


def validate_candidate(candidate):
    repo = candidate.get("repository")
    require(
        candidate.get("schema_version") in {"candidate-v1", "candidate-v2"},
        "unsupported candidate schema",
    )
    require(repo in COMPONENTS, "unsupported repository")
    if candidate["schema_version"] == "candidate-v2":
        require("runtime_services" in candidate, "candidate-v2 requires frozen runtime services")
    else:
        require("runtime_services" not in candidate, "runtime membership requires candidate-v2")
    require(
        bool(SHA.fullmatch(candidate.get("commit_sha", ""))), "full source SHA required"
    )
    require(bool(VERSION.fullmatch(candidate.get("version", ""))), "SemVer required")
    require(
        candidate.get("platform") == "linux/amd64", "NAS platform must be linux/amd64"
    )
    service_components(repo, candidate)
    images = candidate.get("images", {})
    require(set(images) == set(COMPONENTS[repo]), "all repository images are required")
    for component, ref in images.items():
        require(
            bool(re.fullmatch(image_pattern(repo, component), ref)),
            "pinned GHCR digest required",
        )
    require(
        set(candidate.get("image_ids", {})) == set(images)
        and all(IMAGE_ID.fullmatch(value) for value in candidate["image_ids"].values()),
        "CI must certify each config Image ID for archive transport",
    )
    flags = candidate.get("build_args", {})
    expected_flags = FLAGS if repo == "investment-research-dashboard" else set()
    legacy_dashboard = (
        repo == "investment-research-dashboard"
        and tuple(int(v) for v in candidate["version"].split(".")) < (0, 19, 0)
    )
    require(
        set(flags) == expected_flags or (
            legacy_dashboard and set(flags) == FLAGS - {"VITE_MARKET_STRUCTURE_ENABLED"}
        ),
        "unexpected or missing build arguments",
    )
    require(
        all(value in {"true", "false"} for value in flags.values()),
        "boolean flags required",
    )
    evidence = candidate.get("evidence", {})
    quality = evidence.get("quality", {})
    smoke = evidence.get("image_smoke", {})
    require(
        quality.get("status") == "PASS"
        and quality.get("commit_sha") == candidate["commit_sha"],
        "quality evidence must certify the frozen source",
    )
    require(
        smoke.get("status") == "PASS"
        and smoke.get("images") == images
        and smoke.get("scope") == "isolated-fixture",
        "exact image smoke evidence required",
    )
    for run_id in (quality.get("run_id"), evidence.get("candidate_run_id")):
        require(
            str(run_id).isdigit() and int(run_id) > 0, "GitHub run identity required"
        )


def validate_legacy_gates(plan, preparation=False):
    """New plans omit this manual checklist; preserve existing frozen plans."""
    if "gates" not in plan:
        return
    for name in ("scope", "compatibility", "integration", "real_data", "configuration", "rollback"):
        gate = plan["gates"].get(name, {})
        if preparation and name not in {"scope", "compatibility"}:
            require(gate.get("status") in {"PASS", "NOT_RUN", "PENDING"},
                    f"preparation gate missing or failed: {name}")
            require(gate["status"] != "PASS" or bool(gate.get("evidence")),
                    f"preparation PASS evidence missing: {name}")
        else:
            require(gate.get("status") == "PASS" and bool(gate.get("evidence")),
                    f"release gate missing: {name}")


def validate_plan(plan, formal=False, preparation=False):
    require(not (formal and preparation), "formal operations cannot use preparation gates")
    if plan.get("artifact_model") == "SOURCE_TAG_BUILD":
        from nas_source_release import validate_source_plan
        return validate_source_plan(plan, formal=formal, preparation=preparation)
    require(
        plan.get("schema_version") == "image-release-v1",
        "unsupported release plan schema",
    )
    require(
        bool(re.fullmatch(r"REL-[0-9]{8}-[0-9]{3}", plan.get("release_id", ""))),
        "invalid Release ID",
    )
    require(
        plan.get("environment") == "Production", "explicit Production target required"
    )
    allowed_status = {"READY_FOR_FORMAL_RELEASE"}
    if preparation:
        allowed_status.add("NEEDS_TARGET_VERIFICATION")
    require(plan.get("status") in allowed_status, "prepared plan required")
    entries = plan.get("repositories", [])
    require(bool(entries), "empty release scope")
    names = [entry["candidate"]["repository"] for entry in entries]
    require(len(set(names)) == len(names), "duplicate repository")
    require(
        plan.get("release_order") == names,
        "repository list must match explicit release order",
    )
    for entry in entries:
        database_backup_policy(entry)
        candidate = entry["candidate"]
        validate_candidate(candidate)
        repo = candidate["repository"]
        require(entry.get("tag") == "v" + candidate["version"], "Tag/version mismatch")
        baseline = entry.get("expected_production", {})
        require(
            bool(SHA.fullmatch(baseline.get("commit_sha", ""))),
            "verified baseline SHA required",
        )
        require(
            bool(re.fullmatch(r"v" + VERSION.pattern, baseline.get("tag", ""))),
            "verified baseline Tag required",
        )
        rollback = entry.get("rollback", {})
        services = {service for group in service_components(repo, rollback).values() for service in group}
        target_services = {service for group in service_components(repo, candidate).values() for service in group}
        require(services <= target_services, "runtime service removal requires the explicit rollback flow")
        require(
            set(baseline.get("image_ids", {})) == services,
            "all baseline service Image IDs required",
        )
        require(
            all(IMAGE_ID.fullmatch(value) for value in baseline["image_ids"].values()),
            "full baseline Image IDs required",
        )
        rollback = entry.get("rollback", {})
        require(
            rollback.get("commit_sha") == baseline["commit_sha"]
            and rollback.get("tag") == baseline["tag"],
            "rollback must equal verified baseline",
        )
        require(
            rollback.get("version") == baseline["tag"][1:], "rollback version mismatch"
        )
        require(
            set(rollback.get("images", {})) == set(COMPONENTS[repo]),
            "rollback images missing",
        )
        for component, ref in rollback["images"].items():
            require(
                bool(
                    IMAGE_ID.fullmatch(ref)
                    or re.fullmatch(image_pattern(repo, component), ref)
                ),
                "rollback must use pinned digest or retained local Image ID",
            )
            for service in service_components(repo, rollback)[component]:
                if IMAGE_ID.fullmatch(ref):
                    require(
                        ref == baseline["image_ids"][service],
                        "rollback Image ID mismatch",
                    )
        dependencies = entry.get("dependencies", [])
        require(len(dependencies) == len(set(dependencies)), "duplicate dependency")
        require(
            all(dep in names[: names.index(repo)] for dep in dependencies),
            "required provider must precede consumer",
        )
    validate_legacy_gates(plan, preparation)
    if formal:
        auth = plan.get("authorization", {})
        require(
            auth.get("status") == "FORMAL" and bool(auth.get("evidence")),
            "explicit formal-release authorization evidence required",
        )
    transport = plan.get("transport", {"mode": "registry"})
    require(
        transport.get("mode") in {"registry", "archive"}, "unsupported image transport"
    )
    if transport["mode"] == "archive":
        require(
            set(transport.get("archives", {})) == set(names),
            "one archive per affected repository required",
        )
        for repo, archive in transport["archives"].items():
            expected = (
                "/volume1/docker/image-transfer/"
                + plan["release_id"]
                + "/"
                + repo
                + ".tar"
            )
            require(
                archive.get("path") == expected,
                "archive path must be fixed for this Release ID",
            )
            require(
                bool(re.fullmatch(r"[0-9a-f]{64}", archive.get("sha256", ""))),
                "archive hash required",
            )


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def export_bundle(plan, directory):
    directory.mkdir(parents=True, exist_ok=True)
    transport = {"mode": "archive", "archives": {}}
    for entry in plan["repositories"]:
        candidate = entry["candidate"]
        for component, ref in candidate["images"].items():
            info = json.loads(
                subprocess.check_output(["docker", "image", "inspect", ref], text=True)
            )[0]
            require(
                ref in info.get("RepoDigests", [])
                and info["Id"] == candidate["image_ids"][component],
                "local image differs from CI artifact",
            )
        repo = candidate["repository"]
        archive = directory / (repo + ".tar")
        require(
            not archive.exists(),
            "archive already exists; do not overwrite unknown files",
        )
        subprocess.run(
            ["docker", "save", "-o", str(archive), *candidate["image_ids"].values()],
            check=True,
        )
        transport["archives"][repo] = {
            "path": "/volume1/docker/image-transfer/"
            + plan["release_id"]
            + "/"
            + repo
            + ".tar",
            "sha256": file_hash(archive),
        }
    output = directory / "transport.json"
    require(not output.exists(), "transport record already exists")
    output.write_text(json.dumps(transport, indent=2) + "\n")
    print(
        "Archives exported; attach transport.json and transfer archives to its fixed NAS paths"
    )


def verify_ci(plan):
    """Query GitHub and compare the downloaded candidate, not just an operator PASS flag."""
    for entry in plan["repositories"]:
        candidate = entry["candidate"]
        repo = "mumukun/" + candidate["repository"]
        evidence = candidate["evidence"]
        for run_id, workflow in (
            (evidence["quality"]["run_id"], "ci.yml"),
            (evidence["candidate_run_id"], "candidate.yml"),
        ):
            run = json.loads(
                subprocess.check_output(
                    ["gh", "api", f"repos/{repo}/actions/runs/{run_id}"], text=True
                )
            )
            require(
                run["conclusion"] == "success" and run["status"] == "completed",
                "GitHub run has not succeeded",
            )
            require(
                run["repository"]["full_name"] == repo
                and run["path"] == ".github/workflows/" + workflow,
                "wrong CI provenance",
            )
            if workflow == "ci.yml":
                require(
                    run["event"] == "push"
                    and run["head_branch"] == "main"
                    and run["head_sha"] == candidate["commit_sha"],
                    "CI did not certify frozen main SHA",
                )
            else:
                require(run["event"] == "workflow_run", "unexpected candidate trigger")
        with tempfile.TemporaryDirectory(prefix="candidate-evidence-") as directory:
            subprocess.run(
                [
                    "gh",
                    "run",
                    "download",
                    str(evidence["candidate_run_id"]),
                    "--repo",
                    repo,
                    "--name",
                    "candidate-" + candidate["commit_sha"],
                    "--dir",
                    directory,
                ],
                check=True,
            )
            downloaded = json.loads((Path(directory) / "candidate.json").read_text())
            require(
                downloaded == candidate,
                "plan differs from successful CI candidate artifact",
            )
    print("GitHub quality and candidate evidence verified for exact source and digests")


def write_manifest(path, plan, receipt, receipt_path):
    """Summarize the actual receipt once, without new tests or Production probes."""
    receipt = receipt.get("receipt", receipt)
    require(receipt.get("release_id") == plan["release_id"], "receipt Release ID mismatch")
    source = plan.get("artifact_model") == "SOURCE_TAG_BUILD"
    rows = []
    if source:
        entry = plan["repositories"][0]
        require(receipt.get("tag") == entry["tag"] and receipt.get("commit_sha") == entry["commit_sha"],
                "source receipt identity mismatch")
        require(receipt.get("previous") == entry["expected_production"], "source receipt baseline mismatch")
        success = receipt.get("status") == "PASS" and bool(IMAGE_ID.fullmatch(receipt.get("image_id", "")))
        status = "RELEASED" if success else "FAILED"
        rows.append({"repository": entry["repository"], "tag": entry["tag"],
                     "commit_sha": entry["commit_sha"], "artifact_model": "SOURCE_TAG_BUILD",
                     "artifact_id": receipt.get("image_id", "UNKNOWN"),
                     "rollback": entry["expected_production"], "quality": entry["quality"]})
    else:
        require(receipt.get("plan_hash") == frozen_plan_hash(plan), "receipt frozen plan mismatch")
        operation = receipt.get("last_operation")
        require(operation in {"deploy", "rollback", "verify"}, "deployment receipt required")
        states = receipt.get("repositories", {})
        complete = True
        for entry in plan["repositories"]:
            candidate = entry["candidate"]
            repo = candidate["repository"]
            state = states.get(repo, {})
            expected = {service: candidate["image_ids"][component]
                        for component, services in service_components(repo, candidate).items()
                        for service in services}
            complete = complete and state.get("completed", False) and state.get("image_ids") == expected
            rows.append({"repository": repo, "tag": entry["tag"],
                         "commit_sha": candidate["commit_sha"], "planned_version": candidate["version"],
                         "artifact_model": "CI_BUILD_ONCE", "artifact": candidate["images"],
                         "artifact_id": candidate["image_ids"], "rollback": entry["rollback"],
                         "ci_evidence": candidate["evidence"]})
        if receipt.get("last_result") == "PASS" and operation == "rollback":
            status = "ROLLED_BACK"
        elif receipt.get("last_result") == "PASS" and complete:
            status = "RELEASED"
        else:
            status = "PARTIAL" if any(s.get("deployment_started") for s in states.values()) else "FAILED"
    document = {"schema_version": "1.0", "template": False, "generated_by": "image_release.py",
                "release_id": plan["release_id"], "status": status,
                "changes": plan.get("changes", []), "release_order": plan["release_order"],
                "repositories": rows, "deployment_receipts": [str(receipt_path)],
                "deployment": {"environment": plan["environment"], "status": status,
                               "completed_at": receipt.get("last_operation_at", receipt.get("completed_at"))},
                "verification": {"status": "DEPLOYMENT_SMOKE_PASS" if status == "RELEASED" else "NOT_PASSED"}}
    if path.exists():
        previous = json.loads(path.read_text())
        same_identity = [(r.get("repository"), r.get("tag"), r.get("commit_sha"))
                         for r in previous.get("repositories", [])] == [
                             (r["repository"], r["tag"], r["commit_sha"]) for r in rows]
        prepared = previous.get("status") in {"DRAFT", "READY_FOR_FORMAL_RELEASE", "IN_PROGRESS"} and same_identity
        require(previous.get("release_id") == plan["release_id"]
                and (previous.get("generated_by") == "image_release.py" or prepared),
                "refusing to replace a manually maintained or unrelated Manifest")
        previous_rows = {r["repository"]: r for r in previous.get("repositories", [])}
        document["repositories"] = [{**previous_rows.get(r["repository"], {}), **r} for r in rows]
        document["changes"] = plan.get("changes", previous.get("changes", []))
        document = {**previous, **document,
                    "verification": {**previous.get("verification", {}), **document["verification"]}}
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=[
            "check",
            "verify-ci",
            "export-bundle",
            "preflight",
            "prefetch",
            "deploy",
            "verify",
            "rollback",
            "record",
        ],
    )
    parser.add_argument("plan", type=Path)
    parser.add_argument("--host")
    parser.add_argument("--port", type=int, default=9352)
    parser.add_argument("--key", type=Path)
    parser.add_argument(
        "--receipt",
        type=Path,
        help="Save NAS evidence including partial failure; no secrets included",
    )
    parser.add_argument("--bundle-dir", type=Path)
    parser.add_argument("--manifest", type=Path, help="Generate a compact Manifest from the deployment receipt")
    args = parser.parse_args()
    if args.manifest:
        require(args.manifest.resolve() not in {args.plan.resolve(), args.receipt.resolve() if args.receipt else None},
                "Manifest must not replace the plan or receipt")
    plan = json.loads(args.plan.read_text())
    validate_plan(
        plan, formal=args.mode in {"deploy", "rollback"},
        preparation=args.mode in {"preflight", "prefetch"},
    )
    if args.mode == "record":
        require(args.receipt is not None and args.manifest is not None, "record requires --receipt and --manifest")
        write_manifest(args.manifest, plan, json.loads(args.receipt.read_text()), args.receipt)
        return
    require(args.manifest is None or (args.receipt is not None and args.mode in {"deploy", "rollback", "verify"}),
            "automatic Manifest requires a deployment receipt")
    if args.mode == "check":
        print(
            "plan valid; deploy verifies CI, live NAS identity and the backup decision"
        )
        return
    source_build = plan.get("artifact_model") == "SOURCE_TAG_BUILD"
    if source_build:
        require(args.mode in {"check", "preflight", "deploy", "verify"}, "unsupported SOURCE_TAG_BUILD operation")
    if not source_build and args.mode in {"verify-ci", "export-bundle", "prefetch", "deploy"}:
        verify_ci(plan)
    if args.mode == "verify-ci":
        return
    if args.mode == "export-bundle":
        require(args.bundle_dir is not None, "bundle directory required")
        export_bundle(plan, args.bundle_dir)
        return
    require(
        bool(args.host)
        and not args.host.startswith("-")
        and not any(char.isspace() for char in args.host),
        "explicit SSH host required",
    )
    require(0 < args.port < 65536, "invalid SSH port")
    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=8",
        "-o",
        "StrictHostKeyChecking=yes",
        "-p",
        str(args.port),
    ]
    if args.key:
        command += ["-i", str(args.key)]
    command += [args.host, "sudo", "-n", "/usr/local/sbin/nas-image-release", args.mode]
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
    process.stdin.write(json.dumps(plan))
    process.stdin.close()
    receipt = None
    for line in process.stdout:
        print(line, end="", flush=True)
        try:
            output = json.loads(line)
            if "receipt" in output:
                receipt = output["receipt"]
        except (ValueError, TypeError):
            pass
    returncode = process.wait()
    if args.receipt and receipt is not None:
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
        if args.manifest:
            write_manifest(args.manifest, plan, receipt, args.receipt)
    if returncode:
        raise ValueError(
            "NAS operation failed; protected partial state remains available for recovery"
        )
    if args.receipt:
        require(receipt is not None, "NAS did not return a release receipt")


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.CalledProcessError,
    ) as error:
        raise SystemExit(f"image release stopped: {error}") from None
