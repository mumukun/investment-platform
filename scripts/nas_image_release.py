#!/usr/bin/env python3
"""Restricted NAS image deployment. The operator's plan never contains commands or secrets."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from image_release import COMPONENTS, file_hash, require, validate_plan

CONFIG = Path("/usr/local/etc/investment-platform-deploy.json")


def run(command, *, output=None, timeout=300):
    # Do not print command arguments, container logs or Compose config: they can contain secrets.
    result = subprocess.run(
        command,
        check=False,
        stdout=output or subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=output is None,
        timeout=timeout,
    )
    if result.returncode:
        raise RuntimeError(
            f"operation failed (exit {result.returncode}); inspect NAS journal and service status"
        )
    return result.stdout.strip() if output is None else None


def atomic_json(path, value):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w") as handle:
        os.chmod(temporary, 0o600)
        json.dump(value, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


@contextmanager
def release_lock(path):
    with path.open("a") as handle:
        os.chmod(path, 0o600)
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("another NAS image release is running") from None
        yield


def load_config(path=CONFIG):
    info = path.stat()
    require(
        info.st_uid == 0 and not info.st_mode & 0o022,
        "NAS config must be root-owned and not writable by others",
    )
    config = json.loads(path.read_text())
    root = Path(config["state_root"])
    require(
        root.is_absolute() and str(root).startswith("/volume1/docker/"),
        "invalid state root",
    )
    for repo, item in config["repositories"].items():
        require(repo in COMPONENTS, "unknown configured repository")
        require(
            item["path"] == "/volume1/docker/" + repo, "deployment path must be fixed"
        )
        require(
            item["compose_file"]
            == (
                "compose.yaml"
                if repo == "investment-research-dashboard"
                else "docker-compose.yml"
            ),
            "unexpected Compose entrypoint",
        )
        for key in (
            "backup_command",
            "verify_backup_command",
            "smoke_command",
            "health_command",
            "version_command",
        ):
            require(
                isinstance(item.get(key), list)
                and bool(item[key])
                and all(isinstance(arg, str) for arg in item[key]),
                "administrator command missing: " + key,
            )
        require(
            "{backup}" in item["verify_backup_command"],
            "backup readability command required",
        )
    return config


class Deployer:
    def __init__(self, plan, config, state_path):
        self.plan, self.config, self.state_path = plan, config, state_path
        # Authorization may be added after preparation, without changing frozen deployment inputs.
        identity = {
            key: value
            for key, value in plan.items()
            if key not in {"authorization", "transport"}
        }
        self.plan_hash = hashlib.sha256(
            json.dumps(identity, sort_keys=True).encode()
        ).hexdigest()
        self.state = (
            json.loads(state_path.read_text())
            if state_path.exists()
            else {
                "release_id": plan["release_id"],
                "plan_hash": self.plan_hash,
                "repositories": {},
                "events": [],
                "identity": [
                    {
                        "repository": entry["candidate"]["repository"],
                        "tag": entry["tag"],
                        "commit_sha": entry["candidate"]["commit_sha"],
                        "images": entry["candidate"]["images"],
                    }
                    for entry in plan["repositories"]
                ],
            }
        )
        require(
            self.state["plan_hash"] == self.plan_hash,
            "Release ID already belongs to a different frozen plan",
        )

    def save(self):
        atomic_json(self.state_path, self.state)

    def step(self, repo, name, operation):
        started = time.monotonic()
        event = {
            "repository": repo,
            "stage": name,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "IN_PROGRESS",
        }
        self.state["events"].append(event)
        self.save()
        try:
            result = operation()
            event["status"] = "PASS"
            return result
        except Exception:
            event["status"] = "FAILED"
            raise
        finally:
            event["elapsed_seconds"] = round(time.monotonic() - started, 3)
            self.save()
            print(json.dumps(event), flush=True)

    def item(self, entry):
        return self.config["repositories"][entry["candidate"]["repository"]]

    def git(self, entry, *args):
        item = self.item(entry)
        return run(
            [
                "sudo",
                "-n",
                "-u",
                self.config["deploy_user"],
                self.config["git_bin"],
                "-C",
                item["path"],
                *args,
            ]
        )

    def tag_check(self, entry, rollback=False):
        target = entry["rollback"] if rollback else entry["candidate"]
        tag = entry["rollback"]["tag"] if rollback else entry["tag"]
        actual = self.git(entry, "rev-parse", "--verify", tag + "^{commit}")
        require(
            actual == target["commit_sha"],
            "local Tag does not match frozen SHA; fetch as deploy user first",
        )
        self.git(entry, "merge-base", "--is-ancestor", actual, "origin/main")
        dirty = self.git(entry, "status", "--porcelain", "--untracked-files=no")
        require(not dirty, "tracked NAS worktree changes block deployment")

    def compose(self, entry, overlay=None, *args):
        item = self.item(entry)
        command = [
            "docker",
            "compose",
            "--project-directory",
            item["path"],
            "--env-file",
            item["path"] + "/.env",
            "-f",
            item["path"] + "/" + item["compose_file"],
        ]
        if overlay:
            command += ["-f", str(overlay)]
        return run([*command, *args])

    def current_images(self, entry, allow_missing=False):
        services = {
            service
            for group in COMPONENTS[entry["candidate"]["repository"]].values()
            for service in group
        }
        result = {}
        for service in sorted(services):
            container = self.compose(entry, None, "ps", "-q", service)
            require(
                (bool(container) or allow_missing) and "\n" not in container,
                "expected one running container per service",
            )
            result[service] = (
                run(["docker", "inspect", "--format", "{{.Image}}", container])
                if container
                else None
            )
        return result

    def inspect_images(self, entry, rollback=False):
        candidate = entry["candidate"]
        ids = {}
        for component, ref in self.image_refs(entry, rollback).items():
            info = json.loads(run(["docker", "image", "inspect", ref]))[0]
            require(
                info["Os"] == "linux" and info["Architecture"] == "amd64",
                "image platform mismatch",
            )
            if not rollback:
                labels = info.get("Config", {}).get("Labels", {}) or {}
                required = {
                    "org.opencontainers.image.revision": candidate["commit_sha"],
                    "org.opencontainers.image.version": candidate["version"],
                    "org.opencontainers.image.source": "https://github.com/mumukun/"
                    + candidate["repository"],
                    "investment-platform.component": component,
                }
                if component == "web":
                    required.update(
                        {
                            "investment-platform.limit-up-ladder": candidate[
                                "build_args"
                            ]["VITE_LIMIT_UP_LADDER_ENABLED"],
                            "investment-platform.pro-kline": candidate["build_args"][
                                "VITE_PRO_KLINE_ENABLED"
                            ],
                        }
                    )
                require(
                    all(labels.get(key) == value for key, value in required.items()),
                    "image label/source mismatch",
                )
                require(
                    info["Id"] == candidate["image_ids"][component],
                    "image config differs from CI evidence",
                )
                if self.plan.get("transport", {}).get("mode", "registry") == "registry":
                    require(
                        ref in info.get("RepoDigests", []),
                        "local image does not prove registry digest",
                    )
            else:
                for service in COMPONENTS[candidate["repository"]][component]:
                    require(
                        info["Id"]
                        == entry["expected_production"]["image_ids"][service],
                        "rollback image differs from verified baseline",
                    )
            for service in COMPONENTS[candidate["repository"]][component]:
                ids[service] = info["Id"]
        return ids

    def prefetch(self, entry):
        try:
            self.inspect_images(entry)
        except RuntimeError:
            pass  # Missing local images require transfer; invalid identity must still fail.
        else:
            self.inspect_images(entry, rollback=True)
            return
        if self.plan.get("transport", {}).get("mode", "registry") == "archive":
            archive = self.plan["transport"]["archives"][
                entry["candidate"]["repository"]
            ]
            path = Path(archive["path"])
            require(
                path.is_file() and not path.is_symlink(),
                "archive must be a regular file",
            )
            require(path.resolve() == path, "archive cannot traverse a symlink")
            require(file_hash(path) == archive["sha256"], "image archive hash mismatch")
            run(["docker", "load", "-i", str(path)], timeout=900)
        else:
            for ref in entry["candidate"]["images"].values():
                run(["docker", "pull", ref], timeout=900)
        self.inspect_images(entry)
        self.inspect_images(entry, rollback=True)

    def backup(self, entry):
        repo = entry["candidate"]["repository"]
        record = self.state["repositories"].setdefault(repo, {})
        item = self.item(entry)
        if record.get("deployment_started"):
            # A retry must never replace the pre-migration restore point with a post-migration dump.
            backup = Path(record["backup"]["path"])
            require(
                backup.exists() and file_hash(backup) == record["backup"]["sha256"],
                "original restore point missing or changed",
            )
            run(
                [
                    arg.replace("{backup}", str(backup))
                    for arg in item["verify_backup_command"]
                ]
            )
            return
        backup = self.state_path.parent / (repo + ".dump")
        temporary = backup.with_suffix(".dump.tmp")
        with temporary.open("wb") as handle:
            os.chmod(temporary, 0o600)
            run(item["backup_command"], output=handle, timeout=600)
        require(temporary.stat().st_size > 0, "empty database backup")
        run(
            [
                arg.replace("{backup}", str(temporary))
                for arg in item["verify_backup_command"]
            ]
        )
        os.replace(temporary, backup)
        record["backup"] = {
            "path": str(backup),
            "sha256": file_hash(backup),
            "size": backup.stat().st_size,
        }
        self.save()

    def image_refs(self, entry, rollback=False):
        if rollback:
            return entry["rollback"]["images"]
        if self.plan.get("transport", {}).get("mode", "registry") == "archive":
            return entry["candidate"]["image_ids"]
        return entry["candidate"]["images"]

    def overlay(self, entry, rollback=False):
        repo = entry["candidate"]["repository"]
        target = entry["rollback"] if rollback else entry["candidate"]
        overlay = {"services": {}}
        for component, ref in self.image_refs(entry, rollback).items():
            for service in COMPONENTS[repo][component]:
                service_config = {"image": ref, "pull_policy": "never"}
                if repo == "investment-research-dashboard" and component == "api":
                    info = json.loads(run(["docker", "image", "inspect", ref]))[0]
                    labels = info.get("Config", {}).get("Labels", {}) or {}
                    # Preserve observed build metadata for legacy rollback images without labels.
                    built_at = labels.get("org.opencontainers.image.created") or entry[
                        "expected_production"
                    ].get("build_time")
                    require(bool(built_at), "Dashboard build time required")
                    service_config["environment"] = {
                        "APP_GIT_COMMIT": target["commit_sha"],
                        "APP_BUILD_TIME": built_at,
                    }
                overlay["services"][service] = service_config
        path = self.state_path.parent / (
            repo + ("-rollback.json" if rollback else "-images.json")
        )
        atomic_json(path, overlay)
        return path

    def verify(self, entry, rollback=False):
        target = entry["rollback"] if rollback else entry["candidate"]
        require(
            self.current_images(entry) == self.inspect_images(entry, rollback=rollback),
            "running image identity mismatch",
        )
        item = self.item(entry)
        for _ in range(60):
            try:
                run(item["health_command"], timeout=10)
                version = run(item["version_command"], timeout=10)
                require(
                    version == target["version"], "runtime application version mismatch"
                )
                break
            except (RuntimeError, ValueError):
                time.sleep(2)
        else:
            raise RuntimeError("production health/version failed; downstream stopped")
        run(item["smoke_command"], timeout=180)

    def deploy(self, entry):
        repo = entry["candidate"]["repository"]
        record = self.state["repositories"].setdefault(repo, {})
        if record.get("rolled_back"):
            raise RuntimeError("this release was rolled back; prepare a new Release ID")
        self.tag_check(entry)
        current = self.current_images(
            entry, allow_missing=bool(record.get("deployment_started"))
        )
        expected = self.inspect_images(entry)
        if record.get("deployment_started") and current == expected:
            self.backup(entry)
            self.step(repo, "resume_verify", lambda: self.verify(entry))
            record["completed"] = True
            self.save()
            return
        baseline = entry["expected_production"]["image_ids"]
        # Allow partial recreation only when this exact plan started deployment.
        require(
            current == baseline
            or (
                record.get("deployment_started")
                and all(
                    value in {baseline[key], expected[key], None}
                    for key, value in current.items()
                )
            ),
            "production baseline drift; do not overwrite an unrelated deployment",
        )
        if not record.get("deployment_started"):
            version = run(self.item(entry)["version_command"], timeout=10)
            require(
                version == entry["expected_production"]["tag"][1:],
                "baseline runtime version drift",
            )
        self.step(repo, "backup", lambda: self.backup(entry))
        if repo == "investment-research-dashboard":
            configured = json.loads(
                self.compose(entry, None, "config", "--format", "json")
            )
            actual = configured["services"]["web"].get("build", {}).get("args", {})
            require(
                all(
                    str(actual.get(key)).lower() == value
                    for key, value in entry["candidate"]["build_args"].items()
                ),
                "NAS build flag drift; explicitly reconcile configuration before deployment",
            )
        require(
            self.git(entry, "rev-parse", "HEAD")
            in {
                entry["expected_production"]["commit_sha"],
                entry["candidate"]["commit_sha"],
            },
            "NAS source checkout drift",
        )
        record["deployment_started"] = True
        self.save()
        self.step(
            repo,
            "checkout",
            lambda: self.git(
                entry, "checkout", "--detach", entry["candidate"]["commit_sha"]
            ),
        )
        overlay = self.overlay(entry)
        self.step(
            repo,
            "start",
            lambda: self.compose(
                entry, overlay, "up", "-d", "--no-build", "--pull", "never"
            ),
        )
        self.step(repo, "verify", lambda: self.verify(entry))
        record["completed"] = True
        record["image_ids"] = expected
        self.save()

    def rollback(self, entry):
        repo = entry["candidate"]["repository"]
        record = self.state["repositories"].get(repo, {})
        require(
            record.get("deployment_started"),
            "repository was never deployed by this plan",
        )
        require(record.get("backup"), "pre-deployment restore point missing")
        self.inspect_images(entry, rollback=True)
        self.backup(
            entry
        )  # Verify the original restore point before touching running apps.
        current = self.current_images(entry, allow_missing=True)
        old = entry["expected_production"]["image_ids"]
        new = self.inspect_images(entry)
        require(
            all(value in {old[key], new[key], None} for key, value in current.items()),
            "unrelated production drift blocks rollback",
        )
        self.tag_check(entry, rollback=True)
        self.step(
            repo,
            "rollback_checkout",
            lambda: self.git(
                entry, "checkout", "--detach", entry["rollback"]["commit_sha"]
            ),
        )
        overlay = self.overlay(entry, rollback=True)
        self.step(
            repo,
            "rollback_start",
            lambda: self.compose(
                entry, overlay, "up", "-d", "--no-build", "--pull", "never"
            ),
        )
        self.step(repo, "rollback_verify", lambda: self.verify(entry, rollback=True))
        record.update({"completed": False, "rolled_back": True})
        self.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", choices=["preflight", "prefetch", "deploy", "verify", "rollback"]
    )
    args = parser.parse_args()
    require(
        os.geteuid() == 0, "use the administrator-installed restricted sudo wrapper"
    )
    raw = sys.stdin.read(1024 * 1024 + 1)
    require(len(raw) <= 1024 * 1024, "plan exceeds size limit")
    plan = json.loads(raw)
    validate_plan(
        plan, formal=args.mode in {"deploy", "rollback"},
        preparation=args.mode in {"preflight", "prefetch"},
    )
    config = load_config()
    require(
        all(
            entry["candidate"]["repository"] in config["repositories"]
            for entry in plan["repositories"]
        ),
        "repository is not enabled by administrator",
    )
    if args.mode == "preflight":
        info = json.loads(run(["docker", "info", "--format", "{{json .}}"]))
        require(
            info.get("Architecture") in {"x86_64", "amd64"},
            "unexpected NAS architecture",
        )
        for entry in plan["repositories"]:
            item = config["repositories"][entry["candidate"]["repository"]]
            require(Path(item["path"], ".env").is_file(), "NAS environment missing")
            require(bool(item.get("version_command")), "runtime version check missing")
        print(
            json.dumps(
                {
                    "preflight": "PASS",
                    "http_proxy_configured": bool(info.get("HttpProxy")),
                    "https_proxy_configured": bool(info.get("HttpsProxy")),
                    "note": "private registry pull and live smoke are separate gates",
                }
            )
        )
        return
    root = Path(config["state_root"])
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    require(
        root.stat().st_uid == 0 and not root.stat().st_mode & 0o077,
        "state root must be root-owned mode 700",
    )
    with release_lock(root / "release.lock"):
        directory = root / plan["release_id"]
        directory.mkdir(mode=0o700, exist_ok=True)
        require(not directory.is_symlink(), "invalid release state directory")
        deployer = Deployer(plan, config, directory / "state.json")
        try:
            execute(deployer, plan, args.mode)
        except (
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
            subprocess.TimeoutExpired,
        ):
            emit_receipt(deployer, plan, args.mode, "FAILED")
            raise
        emit_receipt(deployer, plan, args.mode, "PASS")


def execute(deployer, plan, mode):
    if mode == "rollback":
        entries = list(reversed(plan["repositories"]))
        for entry in entries:
            if (
                deployer.state["repositories"]
                .get(entry["candidate"]["repository"], {})
                .get("deployment_started")
            ):
                deployer.rollback(entry)
    else:
        for entry in plan["repositories"]:
            repo = entry["candidate"]["repository"]
            if mode in {"prefetch", "deploy"}:
                deployer.step(
                    repo, "pull", lambda entry=entry: deployer.prefetch(entry)
                )
            if mode == "deploy":
                deployer.deploy(entry)
            elif mode == "verify":
                deployer.step(
                    repo, "verify", lambda entry=entry: deployer.verify(entry)
                )


def emit_receipt(deployer, plan, mode, result):
    deployer.state["last_operation"] = mode
    deployer.state["last_result"] = result
    deployer.state["last_operation_at"] = datetime.now(timezone.utc).isoformat()
    deployer.save()
    print(
        json.dumps(
            {
                "release_id": plan["release_id"],
                "result": mode.upper() + "_" + result,
                "state": str(deployer.state_path),
                "receipt": deployer.state,
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        KeyError,
        TypeError,
        RuntimeError,
        OSError,
        subprocess.TimeoutExpired,
    ):
        # Never expose arbitrary command/config/secret data through an exception message.
        raise SystemExit(
            "image release stopped; inspect the protected state and failed stage on NAS"
        ) from None
