#!/usr/bin/env python3
"""CHG-20261010-001: exercise the real Deployer on disposable Compose fixtures.

Git is a fixture; applications sleep without databases, credentials, ports or mounts.
This is lifecycle evidence, not production Git/configuration/application acceptance.
"""

import copy
import json
import os
import re
import sys
import uuid
from pathlib import Path

import nas_image_release as nas
from image_release import COMPONENTS, file_hash, require, validate_plan

SCRIPT = Path(__file__).resolve()
PRODUCTION = (
    "stock-api", "stock-watch", "investment-research-dashboard-nas-api-1",
    "investment-research-dashboard-nas-web-1",
)


def snapshot():
    return {
        name: nas.run(["docker", "inspect", "--format", "{{.Id}} {{.Image}} {{.State.StartedAt}}", name])
        for name in PRODUCTION
    }


def compose_command(spec, *args):
    path = Path(spec["path"])
    require(path.parent.name.startswith("CHG-20261010-001-runner-"), "fixture path required")
    require(re.fullmatch(r"chg20261010001[a-f0-9]+", spec["project"]), "fixture project required")
    return ["docker", "compose", "--project-directory", str(path), "--env-file",
            str(path / ".env"), "-f", str(path / "compose.json"), *args]


def probe(spec_path, mode):
    spec = json.loads(Path(spec_path).read_text())
    ids = {}
    for service in spec["services"]:
        cid = nas.run(compose_command(spec, "ps", "-q", service))
        require(re.fullmatch(r"[a-f0-9]{64}", cid), "fixture container missing")
        info = json.loads(nas.run(["docker", "inspect", cid]))[0]
        require(info["Config"]["Labels"].get("com.docker.compose.project") == spec["project"], "foreign container")
        require(info["State"]["Running"], "fixture not running")
        require(info["HostConfig"]["NetworkMode"] == "none", "fixture network must be none")
        require(not info["Mounts"] and not info["HostConfig"].get("PortBindings")
                and not info["HostConfig"]["Privileged"], "fixture isolation changed")
        ids[service] = cid
    if mode == "version":
        if spec["repository"] == "stock-analyzer":
            command = ["python", "-c", "from stock_analyzer.version import APP_VERSION; print(APP_VERSION)"]
            service = "stock-api"
        else:
            command = [".venv/bin/python", "-c", "import sys;sys.path.insert(0,'backend');from app.version import app_version;print(app_version())"]
            service = "api"
        print(nas.run(["docker", "exec", ids[service], *command]))
    else:
        require(mode in {"health", "smoke"}, "unknown fixture probe")


class Interrupted(Exception):
    pass


class FixtureDeployer(nas.Deployer):
    """Only Git and interruption are fixtures; Docker/state/backup/verify stay real."""

    def git(self, entry, *args):
        checkout = self.state_path.parent / (entry["candidate"]["repository"] + "-checkout")
        if args[:2] == ("rev-parse", "--verify"):
            require(args[2].endswith("^{commit}"), "unexpected fixture tag query")
            tag = args[2][:-9]
            require(tag in {entry["tag"], entry["rollback"]["tag"]}, "unknown fixture tag")
            return entry["candidate"]["commit_sha"] if tag == entry["tag"] else entry["rollback"]["commit_sha"]
        if args == ("merge-base", "--is-ancestor", entry["candidate"]["commit_sha"], "origin/main") or args == ("merge-base", "--is-ancestor", entry["rollback"]["commit_sha"], "origin/main"):
            return ""
        if args == ("status", "--porcelain", "--untracked-files=no"):
            return ""
        if args == ("rev-parse", "HEAD"):
            return checkout.read_text() if checkout.exists() else entry["expected_production"]["commit_sha"]
        if args[:2] == ("checkout", "--detach"):
            checkout.write_text(args[2])
            return ""
        raise ValueError("unexpected fixture Git operation")

    def step(self, repo, name, operation):
        if name == "verify" and getattr(self, "interrupt", False):
            self.interrupt = False
            def stop():
                raise Interrupted("simulated controller loss after Compose recreation")
            return super().step(repo, name, stop)
        return super().step(repo, name, operation)


class ArchiveMissDeployer(FixtureDeployer):
    def inspect_images(self, entry, rollback=False):
        if not rollback and not getattr(self, "cache_miss_injected", False):
            self.cache_miss_injected = True
            raise RuntimeError("injected missing-cache branch")
        return super().inspect_images(entry, rollback=rollback)


def fixture(entry, folder, project):
    repo = entry["candidate"]["repository"]
    path = folder / repo
    path.mkdir(mode=0o700)
    (path / ".env").write_text("")
    services = {}
    for component, names in COMPONENTS[repo].items():
        command = ["sh", "-c", "sleep 86400"] if component == "web" else [
            ".venv/bin/python" if repo != "stock-analyzer" else "python", "-c",
            "import time;time.sleep(86400)",
        ]
        for service in names:
            services[service] = {
                "image": entry["rollback"]["images"][component], "pull_policy": "never",
                "network_mode": "none", "restart": "no", "mem_limit": "128m",
                "entrypoint": command, "command": [],
            }
    compose = {"name": project, "services": services}
    if repo != "stock-analyzer":
        compose["services"]["web"]["build"] = {"context": ".", "args": entry["candidate"]["build_args"]}
    nas.atomic_json(path / "compose.json", compose)
    spec = {"path": str(path), "project": project, "repository": repo, "services": list(services)}
    spec_path = path / "fixture.json"
    nas.atomic_json(spec_path, spec)
    item = {
        "path": str(path), "compose_file": "compose.json",
        "backup_command": [sys.executable, "-c", "print('isolated-backup-fixture-v1')"],
        "verify_backup_command": [sys.executable, "-c", "import sys;from pathlib import Path;assert Path(sys.argv[1]).read_text()=='isolated-backup-fixture-v1\\n'", "{backup}"],
    }
    for mode in ("health", "version", "smoke"):
        item[mode + "_command"] = [sys.executable, str(SCRIPT), "--probe", str(spec_path), mode]
    return item, spec


def acceptance(plan, folder):
    plan = copy.deepcopy(plan)
    validate_plan(plan, preparation=True)
    # These fixture tags never enter the installed CLI or a production release plan.
    for entry in plan["repositories"]:
        entry["tag"] += "-isolated-fixture"
    config = {"repositories": {}}
    specs = []
    state = folder / "state.json"
    checks = []
    before = snapshot()
    try:
        for index, entry in enumerate(plan["repositories"]):
            repo = entry["candidate"]["repository"]
            item, spec = fixture(entry, folder, "chg20261010001" + folder.name.rsplit("-", 1)[-1] + str(index))
            config["repositories"][repo] = item
            specs.append(spec)
        for entry, spec in zip(plan["repositories"], specs):
            repo = entry["candidate"]["repository"]
            nas.run(compose_command(spec, "up", "-d", "--no-build", "--pull", "never"))
            deployer = ArchiveMissDeployer(plan, config, state)
            deployer.prefetch(entry)
            checks.append(repo + " archive hash/load/identity (injected cache miss, warm layers)")
            deployer.interrupt = True
            try:
                deployer.deploy(entry)
            except Interrupted:
                pass
            else:
                raise ValueError("expected interruption missing")
            backup = copy.deepcopy(deployer.state["repositories"][repo]["backup"])
            def starts():
                return {service: nas.run(["docker", "inspect", "--format", "{{.State.StartedAt}}", nas.run(compose_command(spec, "ps", "-q", service))]) for service in spec["services"]}
            started = starts()
            deployer = FixtureDeployer(plan, config, state)
            deployer.deploy(entry)
            require(starts() == started, "resume unexpectedly recreated completed containers")
            require(deployer.state["repositories"][repo]["backup"] == backup, "resume replaced restore point")
            require(file_hash(Path(backup["path"])) == backup["sha256"], "restore point changed")
            checks.append(repo + " interrupted deployment resume without recreation")
            # An incomplete recreation must also resume from its original restore point.
            service = spec["services"][0]
            cid = nas.run(compose_command(spec, "ps", "-q", service))
            nas.run(["docker", "rm", "-f", cid])
            deployer = FixtureDeployer(plan, config, state)
            deployer.deploy(entry)
            require(deployer.state["repositories"][repo]["backup"] == backup, "partial resume replaced restore point")
            checks.append(repo + " partial recreation resume")
            deployer.rollback(entry)
            require(deployer.current_images(entry) == entry["expected_production"]["image_ids"], "rollback identity mismatch")
            checks.append(repo + " retained image rollback")
            try:
                deployer.deploy(entry)
            except RuntimeError:
                pass
            else:
                raise ValueError("rolled-back journal allowed reuse")
            for label in checks[-4:]:
                print(label + " PASS", flush=True)
    finally:
        failures = []
        for spec in reversed(specs):
            try:
                nas.run(compose_command(spec, "down", "--volumes", "--remove-orphans"))
                require(not nas.run(["docker", "ps", "-aq", "--filter", "label=com.docker.compose.project=" + spec["project"]]), "fixture cleanup incomplete")
            except Exception:
                failures.append(spec["project"])
        require(snapshot() == before, "production identity/start time changed during acceptance")
        require(not failures, "fixture cleanup failed")
    receipt = {"result": "PASS", "scope": "isolated Compose lifecycle; fixture Git/backup/health/smoke; no production deployment",
               "checks": checks, "temporary_containers_removed": True, "production_unchanged": True,
               "archive_scope": "real hash and docker load; injected cache miss; existing layers retained"}
    nas.atomic_json(folder / "receipt.json", receipt)
    print("runner receipt: " + str(folder / "receipt.json"), flush=True)


def main():
    os.environ["PATH"] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    if len(sys.argv) == 4 and sys.argv[1] == "--probe":
        probe(sys.argv[2], sys.argv[3])
        return
    require(len(sys.argv) == 1 and os.geteuid() == 0, "run the reviewed fixed tool as root without arguments")
    os.umask(0o077)
    plan = json.loads((SCRIPT.parent.parent / "changes/evidence/CHG-20261010-001/nas-preparation.plan.json").read_text())
    hashes = {
        "stock-analyzer": "3314c39b38792416b60aa011ed8a48b34f693501d0f2462b0d3a654bd1bd62a5",
        "investment-research-dashboard": "550ae0f04dbce43580745ff36f0f526de5b44793a3f98b40aa9f405d04ac96b1",
    }
    plan["transport"] = {"mode": "archive", "archives": {repo: {
        "path": "/volume1/docker/image-transfer/REL-20261010-900/" + repo + ".tar", "sha256": digest,
    } for repo, digest in hashes.items()}}
    folder = Path('/root') / ('CHG-20261010-001-runner-' + uuid.uuid4().hex)
    folder.mkdir(mode=0o700)
    acceptance(plan, folder)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("runner acceptance stopped: " + type(error).__name__, file=sys.stderr)
        raise SystemExit(1)
