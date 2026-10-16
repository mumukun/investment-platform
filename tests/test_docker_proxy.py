import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("docker_proxy", Path(__file__).resolve().parents[1] / "scripts/check_docker_proxy.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DockerProxyStatusTests(unittest.TestCase):
    def test_actual_case_sensitive_fields_and_different_proxy(self):
        value = "http://127.0.0.1:7890"
        info = {"HttpProxy": value, "HttpsProxy": value}
        self.assertTrue(module.daemon_proxy_status(info, value)["daemon_uses_expected_mihomo"])
        self.assertFalse(module.daemon_proxy_status(info, "http://127.0.0.1:7891")["daemon_uses_expected_mihomo"])
        self.assertFalse(module.daemon_proxy_status({"HttpProxy": "", "HttpsProxy": ""}, value)["daemon_http_proxy_configured"])

    def test_missing_or_wrong_case_is_unknown(self):
        for info in [{}, {"HTTPProxy": "http://127.0.0.1:7890", "HTTPSProxy": "http://127.0.0.1:7890"}]:
            with self.assertRaises(ValueError):
                module.daemon_proxy_status(info, "http://127.0.0.1:7890")
