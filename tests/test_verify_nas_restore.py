import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import verify_nas_restore as restore


class RestoreTests(unittest.TestCase):
    def test_non_admin_rejected_before_docker(self):
        with patch.object(restore.os, "geteuid", return_value=501):
            with self.assertRaises(ValueError):
                restore.checked_files(Path("/volume1/docker/CHG-20261010-001-backup-abcd1234"))

    def test_restore_and_failed_restore_only_target_own_container(self):
        for fails in (False, True):
            with self.subTest(fails=fails), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                files = [folder / (db + ".dump") for db in restore.DATABASES]
                for file in files:
                    file.write_bytes(b"fixture dump")
                calls = []
                cid = "a" * 64

                def docker(*args, **kwargs):
                    calls.append(args)
                    if args[0] == "run":
                        self.assertIn("none", args)
                        self.assertNotIn("-v", args)
                        self.assertNotIn("--mount", args)
                        self.assertNotIn("-p", args)
                        self.assertNotIn("--cpus", args)
                        self.assertIn(restore.IMAGE, args)
                        return cid
                    self.assertIn(cid, args)
                    self.assertNotIn("shared-postgres", args)
                    if "pg_isready" in args:
                        self.assertIn("-h", args)
                        self.assertIn("127.0.0.1", args)
                    if fails and "pg_restore" in args:
                        raise subprocess.CalledProcessError(1, "hidden", stderr=b"private data")
                    if "psql" in args:
                        return "1"
                    return ""

                with patch.object(restore, "checked_files", return_value=files), patch.object(
                    restore, "docker", side_effect=docker
                ):
                    if fails:
                        with self.assertRaisesRegex(RuntimeError, "restore stock_analyzer") as caught:
                            restore.restore(folder)
                        self.assertNotIn("private data", str(caught.exception))
                    else:
                        restore.restore(folder)
                self.assertEqual(calls[-1], ("rm", "-f", "-v", cid))
                self.assertEqual(bool(list(folder.glob("restore-receipt-*"))), not fails)

    def test_failed_creation_reports_safe_stage_without_running_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            file = folder / "fixture.dump"
            file.write_bytes(b"fixture")
            error = subprocess.CalledProcessError(125, "hidden", stderr=b"sensitive details")
            with patch.object(restore, "checked_files", return_value=[file, file]), patch.object(
                restore, "docker", side_effect=error
            ) as docker:
                with self.assertRaises(restore.RestoreFailure) as caught:
                    restore.restore(folder)
            self.assertEqual(docker.call_count, 1)
            self.assertIn("create isolated container", str(caught.exception))
            self.assertIn("exit=125", str(caught.exception))
            self.assertNotIn("sensitive details", str(caught.exception))
            self.assertFalse(list(folder.glob("restore-receipt-*")))


if __name__ == "__main__":
    unittest.main()
