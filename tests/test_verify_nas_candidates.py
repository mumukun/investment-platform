import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import verify_nas_candidates as candidates


class CandidateAcceptanceTests(unittest.TestCase):
    def test_checks_and_failure_cleanup_only_target_own_isolated_containers(self):
        for fails in (False, True):
            with self.subTest(fails=fails):
                db = "d" * 64
                created = []
                removed = []
                executions = []

                def docker(*args, **kwargs):
                    if args[0] == "inspect":
                        self.assertEqual(args[1], db)
                        return json.dumps([{"HostConfig": {"NetworkMode": "none", "Binds": None}}])
                    if args[0] == "run":
                        self.assertIn("container:" + db, args)
                        for forbidden in ("host", "-v", "--mount", "-p", "--privileged", "--env-file"):
                            self.assertNotIn(forbidden, args)
                        self.assertIn("never", args)
                        cid = format(len(created) + 1, "064x")
                        created.append(cid)
                        return cid
                    if args[0] == "exec":
                        self.assertIn(args[1], created)
                        executions.append(args)
                        if fails and len(created) == 2:
                            raise subprocess.CalledProcessError(1, "hidden", stderr=b"private data")
                    elif args[0] == "rm":
                        self.assertIn(args[-1], created)
                        removed.append(args[-1])
                    else:
                        self.fail("unexpected Docker operation")
                    return ""

                with patch.object(candidates.restore, "docker", side_effect=docker), patch.object(candidates.time, "sleep"):
                    if fails:
                        with self.assertRaises(candidates.restore.RestoreFailure) as error:
                            candidates.acceptance(db)
                        self.assertNotIn("private data", str(error.exception))
                    else:
                        result = candidates.acceptance(db)
                        self.assertEqual(result["result"], "PASS")
                        self.assertEqual(len(result["checks"]), 9)
                        self.assertEqual(len(created), 6)
                        self.assertTrue(any("check" in call for call in executions))
                self.assertCountEqual(removed, created)

    def test_host_network_database_is_rejected_before_any_app_creation(self):
        with patch.object(candidates.restore, "docker", return_value=json.dumps([
            {"HostConfig": {"NetworkMode": "host", "Binds": None}}
        ])) as docker:
            with self.assertRaisesRegex(ValueError, "isolated"):
                candidates.acceptance("d" * 64)
            self.assertEqual(docker.call_count, 1)
