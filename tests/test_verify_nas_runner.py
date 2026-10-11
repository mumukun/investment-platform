import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import verify_nas_runner as tool
import nas_image_release as nas
from test_image_release import entry, plan


class RunnerAcceptanceTests(unittest.TestCase):
    def test_fixture_configuration_has_no_production_access(self):
        with tempfile.TemporaryDirectory(prefix='CHG-20261010-001-runner-') as name:
            for repo in ('stock-analyzer', 'investment-research-dashboard'):
                item, spec = tool.fixture(entry(repo), Path(name), 'chg20261010001abcdef')
                config = json.loads((Path(item['path']) / 'compose.json').read_text())
                for service in config['services'].values():
                    self.assertEqual(service['network_mode'], 'none')
                    self.assertEqual(service['restart'], 'no')
                    for key in ('volumes', 'ports', 'env_file', 'environment', 'container_name', 'privileged'):
                        self.assertNotIn(key, service)
                self.assertNotIn('shared-postgres', str(item))
                self.assertNotIn('/volume1/docker/stock-analyzer', str(item))
                self.assertNotIn('/volume1/docker/investment-research-dashboard', str(item))
                self.assertEqual(spec['repository'], repo)

    def test_compose_guard_rejects_production_paths_or_project_names(self):
        for spec in (
            {'path': '/volume1/docker/stock-analyzer', 'project': 'chg20261010001abc'},
            {'path': '/root/CHG-20261010-001-runner-abc/stock-analyzer', 'project': 'stock-analyzer'},
        ):
            with self.assertRaises(ValueError):
                tool.compose_command(spec, 'down')

    def test_interruption_persists_failed_stage_and_can_reload(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / 'state.json'
            deployer = tool.FixtureDeployer(plan(), {}, path)
            deployer.interrupt = True
            with self.assertRaises(tool.Interrupted):
                deployer.step('stock-analyzer', 'verify', lambda: self.fail('must interrupt before verification'))
            restarted = tool.FixtureDeployer(plan(), {}, path)
            self.assertEqual(restarted.state['events'][-1]['status'], 'FAILED')

    def test_cache_miss_is_injected_once_then_real_image_checks_run(self):
        with tempfile.TemporaryDirectory() as name:
            deployer = tool.ArchiveMissDeployer(plan(), {}, Path(name) / 'state.json')
            with self.assertRaises(RuntimeError):
                deployer.inspect_images(entry())
            with patch.object(nas.Deployer, 'inspect_images', return_value={'stock-api': 'verified'}) as inspect:
                self.assertEqual(deployer.inspect_images(entry()), {'stock-api': 'verified'})
                inspect.assert_called_once()

    def test_cleanup_continues_after_failure_and_never_writes_success_receipt(self):
        with tempfile.TemporaryDirectory(prefix='CHG-20261010-001-runner-') as name:
            folder = Path(name) / 'CHG-20261010-001-runner-abcdef'
            folder.mkdir()
            value = plan()
            value['repositories'].append(entry('investment-research-dashboard'))
            value['release_order'].append('investment-research-dashboard')
            with patch.object(tool, 'snapshot', return_value={'production': 'unchanged'}), \
                 patch.object(tool, 'ArchiveMissDeployer') as first, \
                 patch.object(nas, 'run', return_value='') as run:
                first.return_value.deploy.side_effect = ValueError('injected early failure')
                with self.assertRaises(ValueError):
                    tool.acceptance(value, folder)
                self.assertEqual(sum('down' in call.args[0] for call in run.call_args_list), 2)
                self.assertFalse((folder / 'receipt.json').exists())


if __name__ == '__main__':
    unittest.main()
