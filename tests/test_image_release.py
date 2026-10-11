import io
import json
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import image_release as release
import nas_image_release as nas
import check_docker_proxy as proxy


def candidate(repo="stock-analyzer"):
    components = release.COMPONENTS[repo]
    images = {
        component: "ghcr.io/mumukun/"
        + repo
        + ("" if repo == "stock-analyzer" else "-" + component)
        + "@sha256:"
        + "1" * 64
        for component in components
    }
    return {
        "schema_version": "candidate-v1",
        "repository": repo,
        "commit_sha": "a" * 40,
        "version": "3.23.0" if repo == "stock-analyzer" else "0.17.0",
        "platform": "linux/amd64",
        "images": images,
        "image_ids": {component: "sha256:" + "1" * 64 for component in components},
        "build_args": {key: "false" for key in release.FLAGS}
        if repo != "stock-analyzer"
        else {},
        "evidence": {
            "quality": {"status": "PASS", "commit_sha": "a" * 40, "run_id": "12"},
            "image_smoke": {
                "status": "PASS",
                "scope": "isolated-fixture",
                "images": dict(images),
            },
            "candidate_run_id": "13",
        },
    }


def entry(repo="stock-analyzer"):
    previous = "3.22.0" if repo == "stock-analyzer" else "0.16.0"
    return {
        "candidate": candidate(repo),
        "tag": "v" + candidate(repo)["version"],
        "dependencies": [],
        "expected_production": {
            "tag": "v" + previous,
            "commit_sha": "b" * 40,
            "image_ids": {
                service: "sha256:" + "2" * 64
                for group in release.COMPONENTS[repo].values()
                for service in group
            },
            "build_time": "2026-10-09T10:00:00Z",
        },
        "rollback": {
            "tag": "v" + previous,
            "commit_sha": "b" * 40,
            "version": previous,
            "images": {
                component: "sha256:" + "2" * 64
                for component in release.COMPONENTS[repo]
            },
        },
    }


def plan():
    return {
        "schema_version": "image-release-v1",
        "release_id": "REL-20261010-999",
        "environment": "Production",
        "status": "READY_FOR_FORMAL_RELEASE",
        "release_order": ["stock-analyzer"],
        "repositories": [entry()],
        "gates": {
            name: {"status": "PASS", "evidence": "test-only"}
            for name in (
                "scope",
                "compatibility",
                "integration",
                "real_data",
                "configuration",
                "rollback",
            )
        },
    }


class PlanTests(unittest.TestCase):
    def test_actual_docker_info_proxy_keys_are_reported_by_both_tools(self):
        for enabled in (False, True):
            info = {"Architecture": "x86_64", "HttpProxy": "http://127.0.0.1:7890" if enabled else "", "HttpsProxy": "http://127.0.0.1:7890" if enabled else ""}
            for module in (nas, proxy):
                with self.subTest(enabled=enabled, module=module.__name__), ExitStack() as stack:
                    output = stack.enter_context(redirect_stdout(io.StringIO()))
                    argv = ["tool", "preflight"] if module is nas else ["tool", "--proxy", "http://127.0.0.1:7890"]
                    stack.enter_context(patch.object(sys, "argv", argv))
                    if module is nas:
                        stack.enter_context(patch.object(sys, "stdin", io.StringIO(json.dumps(plan()))))
                        stack.enter_context(patch.object(nas.os, "geteuid", return_value=0))
                        stack.enter_context(patch.object(nas, "load_config", return_value={"repositories": {"stock-analyzer": {"path": "/fixture", "version_command": ["fixture"]}}}))
                        stack.enter_context(patch.object(Path, "is_file", return_value=True))
                        stack.enter_context(patch.object(nas, "run", return_value=json.dumps(info)))
                    else:
                        stack.enter_context(patch.object(proxy.subprocess, "check_output", return_value=json.dumps(info)))
                        stack.enter_context(patch.object(proxy, "probe", return_value={"reachable": True}))
                    module.main()
                    result = json.loads(output.getvalue())
                    prefix = "" if module is nas else "daemon_"
                    self.assertEqual(result[prefix + "http_proxy_configured"], enabled)
                    self.assertEqual(result[prefix + "https_proxy_configured"], enabled)

    def test_preparation_allows_pending_target_acceptance_but_never_deployment(self):
        value = plan()
        value["status"] = "NEEDS_TARGET_VERIFICATION"
        for name in ("integration", "real_data", "configuration", "rollback"):
            value["gates"][name] = {"status": "NOT_RUN", "evidence": ""}
        release.validate_plan(value, preparation=True)
        for kwargs in ({}, {"formal": True}, {"formal": True, "preparation": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                release.validate_plan(value, **kwargs)

    def test_preparation_still_rejects_failed_gates_and_invalid_identity(self):
        for change in (
            lambda p: p["gates"]["scope"].update(status="NOT_RUN"),
            lambda p: p["gates"]["compatibility"].update(evidence=""),
            lambda p: p["gates"]["rollback"].update(status="FAIL"),
            lambda p: p["gates"]["real_data"].update(evidence=""),
            lambda p: p["gates"].pop("configuration"),
            lambda p: p["repositories"][0]["candidate"]["images"].update(
                app="ghcr.io/mumukun/stock-analyzer:latest"
            ),
        ):
            value = plan()
            change(value)
            with self.subTest(change=change), self.assertRaises(ValueError):
                release.validate_plan(value, preparation=True)

    def test_both_entrypoints_only_use_preparation_gates_for_safe_modes(self):
        for module in (release, nas):
            for mode in ("preflight", "prefetch", "deploy", "verify", "rollback"):
                with self.subTest(module=module.__name__, mode=mode), tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "plan.json"
                    path.write_text(json.dumps(plan()))
                    argv = ["runner", mode] + ([str(path)] if module is release else [])
                    with ExitStack() as stack:
                        stack.enter_context(patch.object(sys, "argv", argv))
                        stack.enter_context(patch.object(sys, "stdin", io.StringIO(path.read_text())))
                        stack.enter_context(patch.object(nas.os, "geteuid", return_value=0))
                        validate = stack.enter_context(patch.object(module, "validate_plan", side_effect=ValueError("stop before execution")))
                        with self.assertRaisesRegex(ValueError, "stop before execution"):
                            module.main()
                        validate.assert_called_once_with(
                            plan(), formal=mode in {"deploy", "rollback"},
                            preparation=mode in {"preflight", "prefetch"},
                        )

    def test_archive_transport_rejects_foreign_path_or_missing_hash(self):
        value = plan()
        value["transport"] = {
            "mode": "archive",
            "archives": {
                "stock-analyzer": {
                    "path": "/volume1/docker/image-transfer/REL-20261010-999/stock-analyzer.tar",
                    "sha256": "f" * 64,
                }
            },
        }
        release.validate_plan(value)
        value["transport"]["archives"]["stock-analyzer"]["path"] = "/tmp/foreign.tar"
        with self.assertRaises(ValueError):
            release.validate_plan(value)

    def test_archive_export_rejects_config_different_from_ci(self):
        value = plan()
        ref = value["repositories"][0]["candidate"]["images"]["app"]
        with ExitStack() as stack:
            directory = stack.enter_context(tempfile.TemporaryDirectory())
            stack.enter_context(
                patch.object(
                    release.subprocess,
                    "check_output",
                    return_value=json.dumps(
                        [{"RepoDigests": [ref], "Id": "sha256:" + "f" * 64}]
                    ),
                )
            )
            save = stack.enter_context(patch.object(release.subprocess, "run"))
            with self.assertRaises(ValueError):
                release.export_bundle(value, Path(directory))
            save.assert_not_called()

    def test_valid_prepared_plan_is_not_formal_authorization(self):
        release.validate_plan(plan())
        with self.assertRaises(ValueError):
            release.validate_plan(plan(), formal=True)

    def test_rejects_floating_images_architecture_and_missing_real_acceptance(self):
        for change in (
            lambda p: p["repositories"][0]["candidate"]["images"].update(
                app="ghcr.io/mumukun/stock-analyzer:latest"
            ),
            lambda p: p["repositories"][0]["candidate"].update(platform="linux/arm64"),
            lambda p: p["gates"]["real_data"].update(status="NOT_RUN"),
            lambda p: p["repositories"][0]["candidate"]["evidence"]["quality"].update(
                commit_sha="c" * 40
            ),
        ):
            value = plan()
            change(value)
            with self.assertRaises(ValueError):
                release.validate_plan(value)

    def test_digest_smoke_and_rollback_identity_must_match(self):
        value = plan()
        value["repositories"][0]["candidate"]["evidence"]["image_smoke"]["images"][
            "app"
        ] = "another"
        with self.assertRaises(ValueError):
            release.validate_plan(value)
        value = plan()
        value["repositories"][0]["rollback"]["images"]["app"] = "sha256:" + "3" * 64
        with self.assertRaises(ValueError):
            release.validate_plan(value)

    def test_required_dependency_cannot_be_deployed_first(self):
        value = plan()
        downstream = entry("investment-research-dashboard")
        downstream["dependencies"] = ["stock-analyzer"]
        value["repositories"] += [downstream]
        value["release_order"] += ["investment-research-dashboard"]
        release.validate_plan(value)
        value["repositories"].reverse()
        value["release_order"].reverse()
        with self.assertRaises(ValueError):
            release.validate_plan(value)


class DeploymentTests(unittest.TestCase):
    def test_cached_prefetch_never_pulls_or_loads(self):
        with ExitStack() as stack:
            inspect = stack.enter_context(patch.object(self.deployer, "inspect_images"))
            run = stack.enter_context(patch.object(nas, "run"))
            self.deployer.prefetch(entry())
            self.assertEqual(inspect.call_count, 2)
            run.assert_not_called()

    def test_invalid_cached_identity_cannot_trigger_transfer(self):
        with ExitStack() as stack:
            stack.enter_context(
                patch.object(
                    self.deployer,
                    "inspect_images",
                    side_effect=ValueError("wrong identity"),
                )
            )
            run = stack.enter_context(patch.object(nas, "run"))
            with self.assertRaises(ValueError):
                self.deployer.prefetch(entry())
            run.assert_not_called()

    def test_failure_receipt_records_partial_state(self):
        self.deployer.state["repositories"]["stock-analyzer"] = {
            "deployment_started": True
        }
        output = io.StringIO()
        with redirect_stdout(output):
            nas.emit_receipt(self.deployer, plan(), "deploy", "FAILED")
        receipt = json.loads(output.getvalue())
        self.assertEqual(receipt["result"], "DEPLOY_FAILED")
        self.assertTrue(
            receipt["receipt"]["repositories"]["stock-analyzer"]["deployment_started"]
        )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "state.json"
        self.config = {
            "repositories": {
                "stock-analyzer": {
                    "backup_command": [
                        sys.executable,
                        "-c",
                        "import sys; sys.stdout.buffer.write(b'backup')",
                    ],
                    "version_command": ["test-version-command"],
                    "verify_backup_command": [
                        sys.executable,
                        "-c",
                        "import pathlib,sys; "
                        "assert pathlib.Path(sys.argv[1]).read_bytes()==b'backup'",
                        "{backup}",
                    ],
                }
            }
        }
        self.deployer = nas.Deployer(plan(), self.config, self.path)

    def test_plan_identity_survives_authorization_but_rejects_changed_inputs(self):
        self.deployer.save()
        value = plan()
        value["authorization"] = {"status": "FORMAL", "evidence": "human"}
        nas.Deployer(value, self.config, self.path)
        value["repositories"][0]["candidate"]["commit_sha"] = "c" * 40
        with self.assertRaises(ValueError):
            nas.Deployer(value, self.config, self.path)

    def test_backup_is_readable_and_never_replaced_after_deployment_started(self):
        value = entry()
        self.deployer.backup(value)
        record = self.deployer.state["repositories"]["stock-analyzer"]
        record["deployment_started"] = True
        self.config["repositories"]["stock-analyzer"]["backup_command"] = [
            "must-not-run"
        ]
        self.deployer.backup(value)
        Path(record["backup"]["path"]).write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            self.deployer.backup(value)

    def test_failed_stage_is_persisted_with_timing(self):
        def fail():
            raise RuntimeError("test failure")

        with self.assertRaises(RuntimeError):
            self.deployer.step("stock-analyzer", "start", fail)
        event = json.loads(self.path.read_text())["events"][-1]
        self.assertEqual(event["status"], "FAILED")
        self.assertGreaterEqual(event["elapsed_seconds"], 0)

    def test_release_lock_blocks_concurrent_release(self):
        lock = self.path.parent / "release.lock"
        with nas.release_lock(lock):
            with self.assertRaises(RuntimeError):
                with nas.release_lock(lock):
                    pass

    def test_baseline_drift_stops_before_backup_or_start(self):
        with ExitStack() as stack:
            stack.enter_context(patch.object(self.deployer, "tag_check"))
            stack.enter_context(
                patch.object(
                    self.deployer,
                    "current_images",
                    return_value={"stock-api": "foreign", "stock-watch": "foreign"},
                )
            )
            stack.enter_context(
                patch.object(
                    self.deployer,
                    "inspect_images",
                    return_value={"stock-api": "target", "stock-watch": "target"},
                )
            )
            backup = stack.enter_context(patch.object(self.deployer, "backup"))
            with self.assertRaises(ValueError):
                self.deployer.deploy(entry())
            backup.assert_not_called()

    def test_resume_reverifies_running_images_without_restarting(self):
        self.deployer.state["repositories"]["stock-analyzer"] = {
            "deployment_started": True
        }
        ids = {"stock-api": "target", "stock-watch": "target"}
        with ExitStack() as stack:
            stack.enter_context(patch.object(self.deployer, "tag_check"))
            stack.enter_context(
                patch.object(self.deployer, "current_images", return_value=ids)
            )
            stack.enter_context(
                patch.object(self.deployer, "inspect_images", return_value=ids)
            )
            stack.enter_context(patch.object(self.deployer, "backup"))
            verify = stack.enter_context(patch.object(self.deployer, "verify"))
            compose = stack.enter_context(patch.object(self.deployer, "compose"))
            self.deployer.deploy(entry())
            verify.assert_called_once()
            compose.assert_not_called()
            self.assertTrue(
                self.deployer.state["repositories"]["stock-analyzer"]["completed"]
            )

    def test_image_labels_and_registry_digest_are_checked(self):
        value = entry()
        ref = value["candidate"]["images"]["app"]
        info = {
            "Id": "sha256:" + "1" * 64,
            "Os": "linux",
            "Architecture": "amd64",
            "RepoDigests": [ref],
            "Config": {
                "Labels": {
                    "org.opencontainers.image.revision": "a" * 40,
                    "org.opencontainers.image.version": "3.23.0",
                    "org.opencontainers.image.source": "https://github.com/mumukun/stock-analyzer",
                    "investment-platform.component": "app",
                }
            },
        }
        with patch.object(nas, "run", return_value=json.dumps([info])):
            self.assertEqual(
                set(self.deployer.inspect_images(value)), {"stock-api", "stock-watch"}
            )
        info["RepoDigests"] = []
        with patch.object(nas, "run", return_value=json.dumps([info])):
            with self.assertRaises(ValueError):
                self.deployer.inspect_images(value)

    def test_failed_backup_blocks_checkout_and_start(self):
        value = entry()
        baseline = value["expected_production"]["image_ids"]
        with ExitStack() as stack:
            stack.enter_context(patch.object(self.deployer, "tag_check"))
            stack.enter_context(
                patch.object(self.deployer, "current_images", return_value=baseline)
            )
            stack.enter_context(
                patch.object(
                    self.deployer,
                    "inspect_images",
                    return_value={key: "target" for key in baseline},
                )
            )
            stack.enter_context(patch.object(nas, "run", return_value="3.22.0"))
            stack.enter_context(
                patch.object(
                    self.deployer,
                    "backup",
                    side_effect=RuntimeError("unreadable backup"),
                )
            )
            git = stack.enter_context(patch.object(self.deployer, "git"))
            with self.assertRaises(RuntimeError):
                self.deployer.deploy(value)
            git.assert_not_called()


if __name__ == "__main__":
    unittest.main()
