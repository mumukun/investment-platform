import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('database_backup', Path(__file__).parents[1] / 'scripts/database_backup.py')
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class BackupTests(unittest.TestCase):
    def test_preflight_never_dumps_or_writes(self):
        config = [{'name': 'news', 'container': 'test-db', 'database': 'news', 'user': 'test'}]
        with patch.object(backup, 'run') as run:
            result = backup.backup(config, None)
        self.assertEqual(result['status'], 'preflight')
        self.assertEqual(run.call_count, 1)
        self.assertIn('pg_isready', run.call_args.args[0])

    def test_checksum_detects_damage_and_never_claims_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            dump = Path(folder) / 'news.dump'
            dump.write_bytes(b'fixture')
            (Path(folder) / 'manifest.json').write_text(json.dumps({
                'status': 'archive_readable', 'databases': [{'file': dump.name, 'bytes': 7,
                                                          'sha256': backup.digest(dump)}]}))
            self.assertFalse(backup.verify(folder)['restore_verified'])
            dump.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                backup.verify(folder)
