import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import nas_source_release as source
import image_release as controller
import nas_image_release as nas


def plan():
    return {'schema_version': 'image-release-v1', 'artifact_model': 'SOURCE_TAG_BUILD',
            'release_id': 'REL-20261014-999', 'environment': 'Production',
            'status': 'READY_FOR_FORMAL_RELEASE', 'release_order': ['marketNewsFeed'],
            'repositories': [{'repository': 'marketNewsFeed', 'tag': 'v2.3.6', 'commit_sha': 'a' * 40,
                              'expected_production': {'tag': 'v2.3.5', 'commit_sha': 'b' * 40, 'image_id': 'sha256:' + '2' * 64},
                              'quality': {'status': 'PASS', 'commit_sha': 'a' * 40, 'evidence': 'affected tests'}}],
            'gates': {name: {'status': 'PASS', 'evidence': 'reviewed'} for name in
                      ('scope', 'compatibility', 'integration', 'real_data', 'configuration', 'rollback')},
            'authorization': {'status': 'FORMAL', 'evidence': 'user formal release'}}


class SourcePlanTest(unittest.TestCase):
    def test_existing_controller_accepts_source_plan_without_fabricated_ci_candidate(self):
        controller.validate_plan(plan(), formal=True)

    def test_rejects_unknown_scope_floating_tag_unknown_baseline_and_missing_auth(self):
        for field, value in [('repository', 'other'), ('tag', 'main'), ('commit_sha', 'a' * 7)]:
            p = plan(); p['repositories'][0][field] = value
            with self.assertRaises(ValueError): source.validate_source_plan(p, formal=True)
        p = plan(); p['repositories'][0]['expected_production']['image_id'] = 'latest'
        with self.assertRaises(ValueError): source.validate_source_plan(p)
        p = plan(); p.pop('authorization')
        with self.assertRaises(ValueError): source.validate_source_plan(p, formal=True)
        p = plan(); p['repositories'][0]['quality']['commit_sha'] = 'b' * 40
        with self.assertRaises(ValueError): source.validate_source_plan(p)

    def test_source_is_not_enabled_without_administrator_config(self):
        with self.assertRaisesRegex(ValueError, 'not enabled'):
            source.execute_source(plan(), {'source_repositories': {}}, 'deploy')

    def test_unsupported_image_modes_do_not_turn_into_source_commands(self):
        for mode in ('rollback', 'prefetch'):
            with self.assertRaisesRegex(ValueError, 'unsupported'):
                source.execute_source(plan(), {}, mode)

    def test_root_config_rejects_untrusted_source_paths_and_empty_checks(self):
        for section in ({'other': {'path': source.PATH}},
                        {'marketNewsFeed': {'path': '/tmp/unsafe'}},
                        {'marketNewsFeed': {'path': source.PATH, 'compose_file': 'docker-compose.yml'}}):
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / 'config.json'
                p.write_text(json.dumps({'state_root': '/volume1/docker/state', 'repositories': {}, 'source_repositories': section}))
                with mock.patch.object(Path, 'stat', return_value=SimpleNamespace(st_uid=0, st_mode=0o600)):
                    with self.assertRaises(ValueError): nas.load_config(p)


class SourceDeployTest(unittest.TestCase):
    def execute(self, mode='deploy', fail=None, drift=False):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        root.chmod(0o700)
        config = {'state_root': str(root), 'deploy_user': 'freemumu', 'git_bin': 'git',
                  'source_repositories': {'marketNewsFeed': {'backup_command': ['backup'], 'verify_backup_command': ['readable', '{backup}'], 'health_command': ['health'], 'smoke_command': ['smoke']}}}
        switched = False
        calls = []
        real_stat = Path.stat
        def stat(path, **kwargs):
            if path == root: return SimpleNamespace(st_uid=0, st_mode=0o40700)
            return real_stat(path, **kwargs)
        def run(command, output=None, timeout=300):
            nonlocal switched
            calls.append(command)
            if command[0] == fail: raise RuntimeError('operation failed')
            if command[0] == 'backup': output.write(b'custom-format-fixture'); return None
            if command[0] == '/usr/bin/sudo' and command[3] == 'git':
                args = command[6:]
                if args == ['status', '--porcelain', '--untracked-files=no']: return ''
                if args == ['rev-parse', 'HEAD']: return ('a' if switched else 'b') * 40
                if args[0] == 'rev-parse': return ('a' if args[1].startswith('v2.3.6') else 'b') * 40
                if args[0] == 'checkout': switched = True
                return ''
            if command[:2] == ['docker', 'compose']: return 'container-id'
            if command[:2] == ['docker', 'inspect']: return 'sha256:' + ('3' if switched else '9' if drift else '2') * 64
            return ''
        with mock.patch.object(Path, 'stat', stat), mock.patch.object(source, 'run', side_effect=run), mock.patch.object(Path, 'read_bytes', return_value=b'private-env'), mock.patch('builtins.print'):
            try: source.execute_source(plan(), config, mode)
            except (RuntimeError, ValueError):
                self.calls = calls
                self.root = root
                raise
        self.calls = calls
        self.root = root
        receipt = root / plan()['release_id'] / 'source-state.json'
        return json.loads(receipt.read_text()) if receipt.exists() else None

    def test_preflight_never_backs_up_builds_or_changes_checkout(self):
        self.assertIsNone(self.execute('preflight'))
        self.assertFalse(any(c[0] == 'backup' or '/bin/bash' in c or 'checkout' in c for c in self.calls))

    def test_deploy_retains_readable_backup_before_switch_and_records_actual_new_image(self):
        receipt = self.execute()
        self.assertEqual(receipt['status'], 'PASS')
        self.assertEqual(receipt['image_id'], 'sha256:' + '3' * 64)
        self.assertEqual(receipt['backup']['readability'], 'PASS')
        before = next(i for i,c in enumerate(self.calls) if c[0] == 'readable')
        deploy = next(i for i,c in enumerate(self.calls) if '/bin/bash' in c)
        self.assertLess(before, deploy)
        self.assertIn('PATH=/usr/local/bin:/usr/bin:/bin', self.calls[deploy])
        self.assertEqual((self.root / plan()['release_id'] / 'runtime.env').stat().st_mode & 0o777, 0o600)

    def test_baseline_drift_cannot_start_backup_or_build(self):
        with self.assertRaisesRegex(ValueError, 'image drift'): self.execute(drift=True)
        self.assertFalse(any(c[0] == 'backup' or '/bin/bash' in c for c in self.calls))

    def test_health_failure_records_actual_partial_identity_without_claiming_success(self):
        with mock.patch.object(source.time, 'sleep'):
            with self.assertRaises(RuntimeError): self.execute(fail='health')
        receipt = json.loads((self.root / plan()['release_id'] / 'source-state.json').read_text())
        self.assertEqual(receipt['status'], 'FAILED')
        self.assertEqual(receipt['stage'], 'verify')
        self.assertEqual(receipt['observed']['image_id'], 'sha256:' + '3' * 64)

    def test_bad_backup_blocks_build_and_saves_failure(self):
        with self.assertRaises(RuntimeError): self.execute(fail='readable')
        self.assertFalse(any('/bin/bash' in c for c in self.calls))
        self.assertEqual(json.loads((self.root / plan()['release_id'] / 'source-state.json').read_text())['status'], 'FAILED')
