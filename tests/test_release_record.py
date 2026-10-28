"""Local end-to-end recording from actual runner state; never connects to a NAS."""
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from test_image_release import plan
from test_nas_source_release import plan as source_plan

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import image_release as release
import nas_image_release as nas


class ReleaseRecordTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.plan = plan()
        self.plan.pop("gates")
        self.plan["changes"] = ["CHG-20261028-001"]
        deployer = nas.Deployer(self.plan, {}, self.root / "state.json")
        self.receipt = deployer.state
        self.receipt.update(last_operation="deploy", last_result="PASS",
                            last_operation_at="2026-10-28T08:00:00+00:00")
        self.receipt["repositories"]["stock-analyzer"] = {
            "deployment_started": True, "completed": True,
            "image_ids": {"stock-api": "sha256:" + "1" * 64, "stock-watch": "sha256:" + "1" * 64}}
        self.output = self.root / "release.yaml"
        self.receipt_path = self.root / "receipt.json"

    def record(self):
        release.write_manifest(self.output, self.plan, self.receipt, self.receipt_path)
        return json.loads(self.output.read_text())

    def test_record_cli_reuses_receipt_without_network_and_preserves_known_limitations(self):
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(self.plan))
        self.receipt_path.write_text(json.dumps(self.receipt))
        command = [sys.executable, str(Path(release.__file__)), "record", str(plan_path),
                   "--receipt", str(self.receipt_path), "--manifest", str(self.output)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        document = json.loads(self.output.read_text())
        self.assertEqual(document["status"], "RELEASED")
        self.assertEqual(document["changes"], self.plan["changes"])
        self.assertEqual(document["repositories"][0]["artifact"], self.plan["repositories"][0]["candidate"]["images"])
        self.assertEqual(document["deployment_receipts"], [str(self.receipt_path)])
        self.assertEqual(document["verification"]["status"], "DEPLOYMENT_SMOKE_PASS")
        document["verification"]["known_limitations"] = ["Unchanged source observation retains its original date"]
        self.output.write_text(json.dumps(document))
        subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(self.output.read_text())["verification"]["known_limitations"],
                         document["verification"]["known_limitations"])

    def test_failed_partial_and_incomplete_receipts_never_become_released(self):
        self.receipt["last_result"] = "FAILED"
        self.assertEqual(self.record()["status"], "PARTIAL")
        self.receipt["repositories"] = {}
        self.assertEqual(self.record()["status"], "FAILED")
        self.receipt["last_result"] = "PASS"
        self.assertNotEqual(self.record()["status"], "RELEASED")

    def test_deploy_generates_receipt_and_manifest_on_success_and_partial_failure(self):
        self.plan["authorization"] = {"status": "FORMAL", "evidence": "test-only authorization"}
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(self.plan))
        for code, expected in ((0, "RELEASED"), (1, "PARTIAL")):
            with self.subTest(code=code):
                self.receipt["last_result"] = "PASS" if code == 0 else "FAILED"
                process = SimpleNamespace(stdin=io.StringIO(),
                                          stdout=io.StringIO(json.dumps({"receipt": self.receipt}) + "\n"),
                                          wait=lambda: code)
                args = ["runner", "deploy", str(plan_path), "--host", "fixture-nas",
                        "--receipt", str(self.receipt_path), "--manifest", str(self.output)]
                with patch.object(sys, "argv", args), patch.object(release, "verify_ci") as ci, \
                        patch.object(release.subprocess, "Popen", return_value=process), redirect_stdout(io.StringIO()):
                    if code:
                        with self.assertRaisesRegex(ValueError, "NAS operation failed"):
                            release.main()
                    else:
                        release.main()
                    ci.assert_called_once_with(self.plan)
                self.assertEqual(json.loads(self.output.read_text())["status"], expected)
                self.assertEqual(json.loads(self.receipt_path.read_text())["last_result"], self.receipt["last_result"])

    def test_wrong_release_hash_or_running_image_cannot_certify_release(self):
        self.receipt["repositories"]["stock-analyzer"]["image_ids"]["stock-api"] = "sha256:" + "9" * 64
        self.assertEqual(self.record()["status"], "PARTIAL")
        self.receipt["plan_hash"] = "foreign"
        with self.assertRaisesRegex(ValueError, "frozen plan"):
            self.record()
        self.receipt["release_id"] = "REL-20261028-999"
        with self.assertRaisesRegex(ValueError, "Release ID"):
            self.record()

    def test_read_only_recording_does_not_overwrite_manually_maintained_manifest(self):
        content = '{"release_id":"REL-20261010-999","notes":["user work"]}'
        self.output.write_text(content)
        with self.assertRaisesRegex(ValueError, "manually maintained"):
            self.record()
        self.assertEqual(self.output.read_text(), content)

    def test_prepared_matching_manifest_is_completed_without_losing_development_evidence(self):
        prepared = {"release_id": self.plan["release_id"], "status": "READY_FOR_FORMAL_RELEASE",
                    "changes": self.plan["changes"], "notes": ["development tests passed"],
                    "repositories": [{"repository": "stock-analyzer", "tag": "v3.23.0",
                                      "commit_sha": "a" * 40, "pr": "existing PR evidence"}]}
        self.output.write_text(json.dumps(prepared))
        result = self.record()
        self.assertEqual(result["status"], "RELEASED")
        self.assertEqual(result["notes"], prepared["notes"])
        self.assertEqual(result["repositories"][0]["pr"], "existing PR evidence")

    def test_source_receipt_records_actual_image_and_failure_honestly(self):
        value = source_plan()
        entry = value["repositories"][0]
        receipt = {"release_id": value["release_id"], "tag": entry["tag"],
                   "commit_sha": entry["commit_sha"], "previous": entry["expected_production"],
                   "status": "PASS", "image_id": "sha256:" + "3" * 64}
        release.write_manifest(self.output, value, receipt, self.receipt_path)
        self.assertEqual(json.loads(self.output.read_text())["repositories"][0]["artifact_id"], receipt["image_id"])
        receipt["status"] = "FAILED"
        release.write_manifest(self.output, value, receipt, self.receipt_path)
        self.assertEqual(json.loads(self.output.read_text())["status"], "FAILED")
        receipt["commit_sha"] = "f" * 40
        with self.assertRaisesRegex(ValueError, "identity"):
            release.write_manifest(self.output, value, receipt, self.receipt_path)


if __name__ == "__main__":
    unittest.main()
