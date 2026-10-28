import io
import json
import os
import subprocess
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
    def test_new_plans_need_no_manual_gates_but_keep_ci_identity_and_authorization(self):
        value = plan()
        del value["gates"]
        release.validate_plan(value)
        release.validate_plan(value, preparation=True)
        with self.assertRaisesRegex(ValueError, "authorization"):
            release.validate_plan(value, formal=True)
        value["authorization"] = {"status": "FORMAL", "evidence": "user formal release"}
        release.validate_plan(value, formal=True)
        value["repositories"][0]["candidate"]["evidence"]["quality"]["status"] = "FAIL"
        with self.assertRaises(ValueError):
            release.validate_plan(value, formal=True)

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


def backup_policy(mode="skip", impact="none", compatible=True):
    value = {"mode": mode, "data_impact": impact, "rollback_compatible": compatible,
             "reason": "Reviewed startup, jobs and migration writes", "evidence": "change review"}
    if mode == "tables":
        value["tables"] = ["public.swing_setup_snapshot", "public.swing_state_event"]
    return value


class RuntimeServiceExpansionTests(unittest.TestCase):
    setUp = DeploymentTests.setUp

    def expanded(self):
        value = plan()
        target = value["repositories"][0]
        target["candidate"]["schema_version"] = "candidate-v2"
        target["candidate"]["runtime_services"] = {"app": ["stock-api", "stock-watch", "stock-data"]}
        release.validate_plan(value)
        return value, target

    def test_old_manifest_membership_is_immutable_and_only_known_extension_allowed(self):
        old = candidate()
        self.assertEqual(release.service_components("stock-analyzer", old)["app"], ("stock-api", "stock-watch"))
        new, target = self.expanded()
        self.assertIn("stock-data", release.service_components("stock-analyzer", target["candidate"])["app"])
        target["candidate"]["schema_version"] = "candidate-v1"
        with self.assertRaisesRegex(ValueError, "requires candidate-v2"):
            release.validate_candidate(target["candidate"])
        target["candidate"]["schema_version"] = "candidate-v2"
        target["candidate"]["runtime_services"]["app"].append("unrelated-container")
        with self.assertRaisesRegex(ValueError, "membership"):
            release.validate_plan(new)

    def test_old_compose_can_report_absent_new_service_without_querying_unknown_service(self):
        value, target = self.expanded()
        deployer = nas.Deployer(value, self.config, self.path)
        def compose(_entry, _overlay, *arguments):
            if arguments == ("config", "--services"):
                return "stock-api\nstock-watch"
            self.assertNotIn("stock-data", arguments)
            return "fixture-container"
        def run(arguments, **kwargs):
            return "" if arguments[:3] == ["docker", "ps", "-aq"] else "sha256:"+"2"*64
        with patch.object(deployer, "compose", side_effect=compose), patch.object(nas, "run", side_effect=run):
            observed = deployer.current_images(target, allow_missing=True)
        self.assertEqual(observed, {**target["expected_production"]["image_ids"], "stock-data": None})

    def test_first_expansion_stops_legacy_collectors_before_start(self):
        value, target = self.expanded()
        deployer = nas.Deployer(value, self.config, self.path)
        old = target["expected_production"]["image_ids"]
        new = {service: "sha256:"+"1"*64 for service in ("stock-api", "stock-watch", "stock-data")}
        with ExitStack() as stack:
            for name in ("tag_check", "backup", "overlay", "verify"):
                stack.enter_context(patch.object(deployer, name))
            stack.enter_context(patch.object(deployer, "git", return_value=target["expected_production"]["commit_sha"]))
            stack.enter_context(patch.object(deployer, "current_images", return_value={**old, "stock-data": None}))
            stack.enter_context(patch.object(deployer, "inspect_images", return_value=new))
            stack.enter_context(patch.object(nas, "run", return_value=target["expected_production"]["tag"][1:]))
            compose = stack.enter_context(patch.object(deployer, "compose"))
            deployer.deploy(target)
            actions = [call.args[2:] for call in compose.call_args_list]
            self.assertEqual(actions[0], ("stop", "stock-api", "stock-watch"))
            self.assertEqual(actions[1][0], "up")

    def test_rollback_removes_only_the_added_collector_before_old_start(self):
        value, target = self.expanded()
        deployer = nas.Deployer(value, self.config, self.path)
        deployer.state["repositories"]["stock-analyzer"] = {"deployment_started": True}
        old = target["expected_production"]["image_ids"]
        new = {service: "sha256:"+"1"*64 for service in ("stock-api", "stock-watch", "stock-data")}
        with ExitStack() as stack:
            for name in ("tag_check", "backup", "git", "overlay", "verify"):
                stack.enter_context(patch.object(deployer, name))
            stack.enter_context(patch.object(deployer, "inspect_images", side_effect=lambda _, rollback=False: old if rollback else new))
            stack.enter_context(patch.object(deployer, "current_images", return_value=new))
            compose = stack.enter_context(patch.object(deployer, "compose"))
            deployer.rollback(target)
            actions = [call.args[2:] for call in compose.call_args_list]
            self.assertEqual(actions[:2], [("stop", "stock-data"), ("rm", "-f", "stock-data")])
            self.assertEqual(actions[2][0], "up")


class BackupPolicyTests(unittest.TestCase):
    def setUp(self):
        DeploymentTests.setUp(self)

    def test_legacy_plans_keep_full_backup_and_new_decisions_are_validated(self):
        self.assertEqual(release.database_backup_policy(entry()), {"mode": "full"})
        for mode, impact in (("skip", "none"), ("skip", "additive"), ("tables", "destructive"), ("full", "unknown")):
            value = plan()
            value["repositories"][0]["database_backup"] = backup_policy(mode, impact)
            release.validate_plan(value)
        for change in (
            {"mode": "incremental"}, {"mode": []}, {"data_impact": "unknown"},
            {"data_impact": "destructive"}, {"rollback_compatible": False},
            {"reason": " "}, {"evidence": ""}, {"tables": ["public.foo"]},
            {"typo": True},
        ):
            value = plan()
            value["repositories"][0]["database_backup"] = dict(backup_policy(), **change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                release.validate_plan(value)

    def test_table_scope_rejects_globs_options_injection_duplicates_and_unknown_impact(self):
        for tables in ([], ["foo"], ["public.*"], ["--file=/tmp/out"], ["public.foo;drop"],
                       ["public.foo", "public.foo"], [{}], "public.foo"):
            value = entry()
            value["database_backup"] = dict(backup_policy("tables"), tables=tables)
            with self.subTest(tables=tables), self.assertRaises(ValueError):
                release.database_backup_policy(value)
        value["database_backup"] = backup_policy("tables", "unknown")
        with self.assertRaises(ValueError):
            release.database_backup_policy(value)

    def test_skip_records_honest_receipt_and_never_runs_dump_or_readability(self):
        value = entry()
        value["database_backup"] = backup_policy()
        with patch.object(nas, "run") as run:
            self.deployer.step("stock-analyzer", "backup", lambda: self.deployer.backup(value))
            run.assert_not_called()
        state = json.loads(self.path.read_text())
        self.assertEqual(state["events"][-1]["status"], "SKIPPED")
        saved = state["repositories"]["stock-analyzer"]["backup"]
        self.assertEqual(saved["status"], "SKIPPED")
        self.assertNotIn("path", saved)
        self.assertFalse((self.path.parent / "stock-analyzer.dump").exists())
        self.deployer.state["repositories"]["stock-analyzer"]["deployment_started"] = True
        with patch.object(nas, "run") as run:
            self.deployer.backup(value)
            run.assert_not_called()
        self.deployer.state["repositories"]["stock-analyzer"]["backup"]["policy"]["reason"] = "tampered"
        with self.assertRaisesRegex(ValueError, "decision missing or changed"):
            self.deployer.backup(value)

    def test_selected_tables_are_separate_strict_arguments_and_restore_point_survives_resume(self):
        value = entry()
        value["database_backup"] = backup_policy("tables", "destructive")
        item = self.config["repositories"]["stock-analyzer"]
        item["table_backup_command"] = [sys.executable, "-c",
            "import sys; assert sys.argv[1:]==['--strict-names','--table=public.swing_setup_snapshot','--table=public.swing_state_event']; sys.stdout.buffer.write(b'backup')", "{tables}"]
        self.deployer.backup(value)
        record = self.deployer.state["repositories"]["stock-analyzer"]
        self.assertEqual(record["backup"]["policy"]["tables"], value["database_backup"]["tables"])
        record["deployment_started"] = True
        item["table_backup_command"] = ["must-not-run", "{tables}"]
        self.deployer.backup(value)
        Path(record["backup"]["path"]).write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.deployer.backup(value)

    def test_missing_table_command_cannot_fall_back_to_full_backup(self):
        value = entry()
        value["database_backup"] = backup_policy("tables")
        with patch.object(nas, "run") as run, self.assertRaisesRegex(ValueError, "table_backup_command"):
            self.deployer.backup(value)
        run.assert_not_called()
        self.assertFalse((self.path.parent / "stock-analyzer.dump").exists())

    def test_ds920plus_shell_commands_forward_all_table_filters_to_pg_dump(self):
        config = json.loads((Path(__file__).parents[1] / "deploy/nas-config.DS920plus.json").read_text())
        fake = self.path.parent / "pg_dump"
        fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\"\n")
        fake.chmod(0o700)
        env = dict(os.environ, PATH=str(fake.parent) + os.pathsep + os.environ.get("PATH", ""), POSTGRES_USER="fixture")
        for item in list(config["repositories"].values()) + list(config["source_repositories"].values()):
            command = nas.backup_command(item, backup_policy("tables"))
            result = subprocess.check_output(command[3:], env=env, text=True).splitlines()
            self.assertEqual(result[-3:], ["--strict-names", "--table=public.swing_setup_snapshot", "--table=public.swing_state_event"])

    def test_skip_decision_is_frozen_with_plan_identity(self):
        value = plan()
        value["repositories"][0]["database_backup"] = backup_policy()
        deployer = nas.Deployer(value, self.config, self.path)
        deployer.save()
        value["repositories"][0]["database_backup"] = backup_policy("full")
        with self.assertRaisesRegex(ValueError, "different frozen plan"):
            nas.Deployer(value, self.config, self.path)

    def test_skip_deploy_and_resume_preserve_identity_health_and_no_restart_on_resume(self):
        value = plan()
        target = value["repositories"][0]
        target["database_backup"] = backup_policy()
        deployer = nas.Deployer(value, self.config, self.path)
        old = target["expected_production"]["image_ids"]
        new = {key: "target" for key in old}
        with ExitStack() as stack:
            stack.enter_context(patch.object(deployer, "tag_check"))
            stack.enter_context(patch.object(deployer, "current_images", return_value=old))
            stack.enter_context(patch.object(deployer, "inspect_images", return_value=new))
            stack.enter_context(patch.object(deployer, "git", return_value=target["expected_production"]["commit_sha"]))
            stack.enter_context(patch.object(deployer, "overlay"))
            run = stack.enter_context(patch.object(nas, "run", return_value="3.22.0"))
            compose = stack.enter_context(patch.object(deployer, "compose"))
            verify = stack.enter_context(patch.object(deployer, "verify"))
            deployer.deploy(target)
            run.assert_called_once_with(self.config["repositories"]["stock-analyzer"]["version_command"], timeout=10)
            compose.assert_called_once()
            verify.assert_called_once()
        resumed = nas.Deployer(value, self.config, self.path)
        with ExitStack() as stack:
            stack.enter_context(patch.object(resumed, "tag_check"))
            stack.enter_context(patch.object(resumed, "current_images", return_value=new))
            stack.enter_context(patch.object(resumed, "inspect_images", return_value=new))
            compose = stack.enter_context(patch.object(resumed, "compose"))
            verify = stack.enter_context(patch.object(resumed, "verify"))
            run = stack.enter_context(patch.object(nas, "run"))
            resumed.deploy(target)
            compose.assert_not_called()
            run.assert_not_called()
            verify.assert_called_once()
        self.assertEqual(resumed.state["repositories"]["stock-analyzer"]["backup"]["status"], "SKIPPED")

    def test_compatible_code_rollback_works_without_a_dump(self):
        value = entry()
        value["database_backup"] = backup_policy()
        self.deployer.backup(value)
        self.deployer.state["repositories"]["stock-analyzer"]["deployment_started"] = True
        with ExitStack() as stack:
            for name in ("inspect_images", "tag_check", "git", "overlay", "verify"):
                stack.enter_context(patch.object(self.deployer, name))
            stack.enter_context(patch.object(self.deployer, "current_images", return_value=value["expected_production"]["image_ids"]))
            compose = stack.enter_context(patch.object(self.deployer, "compose"))
            run = stack.enter_context(patch.object(nas, "run"))
            self.deployer.rollback(value)
            run.assert_not_called()
            compose.assert_called_once()
        self.assertTrue(self.deployer.state["repositories"]["stock-analyzer"]["rolled_back"])
        self.assertFalse((self.path.parent / "stock-analyzer.dump").exists())

    def test_missing_skip_receipt_and_incompatible_database_block_rollback_before_switch(self):
        value = entry()
        value["database_backup"] = backup_policy()
        self.deployer.state["repositories"]["stock-analyzer"] = {"deployment_started": True}
        with patch.object(self.deployer, "inspect_images"), patch.object(self.deployer, "compose") as compose:
            with self.assertRaisesRegex(ValueError, "decision missing"):
                self.deployer.rollback(value)
            compose.assert_not_called()
        value["database_backup"] = backup_policy("full", "destructive", False)
        with patch.object(self.deployer, "inspect_images") as inspect:
            with self.assertRaisesRegex(ValueError, "incompatible with code rollback"):
                self.deployer.rollback(value)
            inspect.assert_not_called()


class MarketStructureBuildIdentityTests(unittest.TestCase):
    def test_new_flags_are_checked_on_target_checkout_before_start(self):
        with tempfile.TemporaryDirectory() as directory:
            value = entry("investment-research-dashboard")
            release_plan = plan()
            release_plan["repositories"] = [value]
            release_plan["release_order"] = ["investment-research-dashboard"]
            config = {"repositories": {"investment-research-dashboard": {"version_command": ["version"]}}}
            deployer = nas.Deployer(release_plan, config, Path(directory) / "state.json")
            switched, started = [], []

            def git(_, *args):
                if args[0] == "checkout":
                    switched.append(args[-1])
                return value["expected_production"]["commit_sha"]

            def compose(_, overlay, *args):
                if args[0] == "config":
                    self.assertEqual(switched, [value["candidate"]["commit_sha"]])
                    return json.dumps({"services": {"web": {"build": {"args": value["candidate"]["build_args"]}}}})
                started.append(args[0])

            with ExitStack() as stack:
                for name in ("tag_check", "backup", "verify", "overlay"):
                    stack.enter_context(patch.object(deployer, name))
                stack.enter_context(patch.object(deployer, "git", side_effect=git))
                stack.enter_context(patch.object(deployer, "compose", side_effect=compose))
                stack.enter_context(patch.object(deployer, "current_images", return_value=value["expected_production"]["image_ids"]))
                stack.enter_context(patch.object(deployer, "inspect_images", return_value={"api": "new", "web": "new"}))
                stack.enter_context(patch("nas_image_release.run", return_value=value["expected_production"]["tag"][1:]))
                deployer.deploy(value)
            self.assertEqual(started, ["up"])

    def test_new_dashboard_requires_module_build_identity_and_legacy_survives(self):
        value = candidate("investment-research-dashboard")
        value["version"] = "0.18.1"
        value["build_args"].pop("VITE_MARKET_STRUCTURE_ENABLED")
        release.validate_candidate(value)
        value["version"] = "0.19.0"
        with self.assertRaisesRegex(ValueError, "build arguments"):
            release.validate_candidate(value)
        value["build_args"]["VITE_MARKET_STRUCTURE_ENABLED"] = "true"
        release.validate_candidate(value)


if __name__ == "__main__":
    unittest.main()
