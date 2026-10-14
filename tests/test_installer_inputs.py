import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class InstallerInputsTest(unittest.TestCase):
    def test_incomplete_package_stops_before_validation_or_protected_file_copy(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            (package / 'deploy').mkdir()
            (package / 'scripts').mkdir()
            (package / 'bin').mkdir()
            shutil.copy(root / 'deploy/install-nas-image-release.sh', package / 'deploy/install.sh')
            for name in ('image_release.py', 'nas_image_release.py', 'nas_source_release.py', 'nas_checks.py'):
                (package / 'scripts' / name).touch()
            (package / 'config.json').write_text('{}')
            marker = package / 'invoked'
            for command, body in [('id', 'echo 0'), ('install', f'touch "{marker}"'), ('python3', f'touch "{marker}"')]:
                executable = package / 'bin' / command
                executable.write_text('#!/bin/sh\n' + body + '\n')
                executable.chmod(0o755)
            environment = dict(os.environ, PATH=str(package / 'bin') + ':' + os.environ['PATH'])
            result = subprocess.run(['/bin/bash', str(package / 'deploy/install.sh'), str(package / 'config.json')], env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Missing installation file: deploy/nas-image-release', result.stderr)
            self.assertFalse(marker.exists())
