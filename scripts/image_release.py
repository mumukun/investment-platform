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
FLAGS = {"VITE_LIMIT_UP_LADDER_ENABLED", "VITE_PRO_KLINE_ENABLED"}
SHA = re.compile(r"[0-9a-f]{40}")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
IMAGE_ID = re.compile(r"sha256:[0-9a-f]{64}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def image_pattern(repository, component):
    suffix = "" if repository == "stock-analyzer" else "-" + component
    return rf"ghcr\.io/mumukun/{repository}{suffix}@sha256:[0-9a-f]{{64}}"


def validate_candidate(candidate):
    repo = candidate.get("repository")
    require(
        candidate.get("schema_version") == "candidate-v1",
        "unsupported candidate schema",
    )
    require(repo in COMPONENTS, "unsupported repository")
    require(
        bool(SHA.fullmatch(candidate.get("commit_sha", ""))), "full source SHA required"
    )
    require(bool(VERSION.fullmatch(candidate.get("version", ""))), "SemVer required")
    require(
        candidate.get("platform") == "linux/amd64", "NAS platform must be linux/amd64"
    )
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
    require(
        set(flags) == (FLAGS if repo == "investment-research-dashboard" else set()),
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


def validate_plan(plan, formal=False):
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
    require(plan.get("status") == "READY_FOR_FORMAL_RELEASE", "prepared plan required")
    entries = plan.get("repositories", [])
    require(bool(entries), "empty release scope")
    names = [entry["candidate"]["repository"] for entry in entries]
    require(len(set(names)) == len(names), "duplicate repository")
    require(
        plan.get("release_order") == names,
        "repository list must match explicit release order",
    )
    for entry in entries:
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
        services = {service for group in COMPONENTS[repo].values() for service in group}
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
            for service in COMPONENTS[repo][component]:
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
    for name in (
        "scope",
        "compatibility",
        "integration",
        "real_data",
        "configuration",
        "rollback",
    ):
        gate = plan.get("gates", {}).get(name, {})
        require(
            gate.get("status") == "PASS" and bool(gate.get("evidence")),
            f"release gate missing: {name}",
        )
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
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    validate_plan(plan, formal=args.mode in {"deploy", "rollback"})
    if args.mode == "check":
        print(
            "plan structural gates PASS; GitHub, live NAS and backup checks remain separate"
        )
        return
    if args.mode in {"verify-ci", "export-bundle", "deploy"}:
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
