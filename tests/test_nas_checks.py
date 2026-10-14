import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "nas_checks", Path(__file__).resolve().parents[1] / "scripts/nas_checks.py"
)
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class NASChecksTest(unittest.TestCase):
    def test_rejects_arbitrary_repository_and_command(self):
        for repo, mode in [("other", "health"), ("stock-analyzer", "deploy")]:
            with self.assertRaises(ValueError):
                checks.commands(repo, mode)

    def test_marketnews_checks_use_host_admin_api_without_entering_business_container(self):
        for mode in ("health", "smoke"):
            commands = checks.commands("marketNewsFeed", mode)
            self.assertEqual(commands[0][:2], ["/usr/bin/python3", "-c"])
            self.assertNotIn("exec", commands[0])
        self.assertIn("Authorization", checks.MARKET_SMOKE)
        self.assertNotIn("POST", checks.MARKET_SMOKE)
        with self.assertRaises(ValueError):
            checks.commands("marketNewsFeed", "version")

    def test_backup_is_streamed_and_invalid_archive_fails(self):
        with patch.object(Path, "open") as opened, patch.object(
            checks.subprocess, "run"
        ) as run:
            run.return_value = subprocess.CompletedProcess([], 1)
            with self.assertRaisesRegex(RuntimeError, "readability"):
                checks.verify_backup("protected.dump")
            call = run.call_args
            self.assertEqual(call.args[0][-2:], ["pg_restore", "--list"])
            self.assertIs(
                call.kwargs["stdin"], opened.return_value.__enter__.return_value
            )
            self.assertEqual(call.kwargs["stdout"], subprocess.DEVNULL)


if __name__ == "__main__":
    unittest.main()
