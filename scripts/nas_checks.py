#!/usr/bin/env python3
"""Fixed DS920plus checks. Never print application data, tokens or connection strings."""

import argparse
import subprocess
import sys
from pathlib import Path

DOCKER = "/usr/local/bin/docker"
REPOSITORIES = ("stock-analyzer", "investment-research-dashboard")
STOCK_HEALTH = """
import json, urllib.request
from stock_analyzer.settings import load_settings
s = load_settings()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
base = 'http://127.0.0.1:' + str(s.api.port)
def get(path, headers=None):
    with opener.open(urllib.request.Request(base + path, headers=headers or {}), timeout=5) as r:
        return json.load(r)
h = get('/api/health')
assert h['ok'] and h['auth_configured']
"""
STOCK_SMOKE = (
    STOCK_HEALTH
    + """
import urllib.error
path = '/api/integrations/investment-dashboard/watchlist?refresh_quotes=false&limit=1'
try:
    get(path)
    raise AssertionError('authentication missing')
except urllib.error.HTTPError as e:
    assert e.code == 401
p = get(path, {'Authorization': 'Bearer ' + s.api.token})
assert p['ok'] and p['contract_version'] == 'investment-dashboard-watchlist-v1'
assert p['count'] == len(p['items'])
assert p['quote_refresh']['status'] == 'not_requested'
assert not p['quote_refresh']['persisted']
print('authenticated database/watchlist smoke PASS')
"""
)
DASHBOARD_HEALTH = """
import json, urllib.request
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
with opener.open('http://127.0.0.1:8000/api/v1/health', timeout=5) as r:
    assert json.load(r)['status'] == 'ok'
"""


def commands(repository, mode):
    """Only administrator-reviewed fixed commands, independent of a release plan."""
    if repository not in REPOSITORIES or mode not in {"health", "version", "smoke"}:
        raise ValueError("unknown check")
    if repository == "stock-analyzer":
        code = {
            "health": STOCK_HEALTH,
            "version": "from stock_analyzer.version import APP_VERSION; print(APP_VERSION)",
            "smoke": STOCK_SMOKE,
        }[mode]
        return [[DOCKER, "exec", "stock-api", "python", "-c", code]]
    container = "investment-research-dashboard-nas-api-1"
    if mode == "version":
        code = (
            "import sys;sys.path.insert(0,'backend');"
            "from app.version import app_version;print(app_version())"
        )
        return [[DOCKER, "exec", container, ".venv/bin/python", "-c", code]]
    if mode == "smoke":
        return [
            [
                DOCKER,
                "exec",
                container,
                ".venv/bin/python",
                "scripts/production_smoke.py",
            ]
        ]
    return [
        [DOCKER, "exec", container, ".venv/bin/python", "-c", DASHBOARD_HEALTH],
        [
            DOCKER,
            "exec",
            "investment-research-dashboard-nas-web-1",
            "wget",
            "-q",
            "-O",
            "/dev/null",
            "http://127.0.0.1:9360/",
        ],
    ]


def verify_backup(path):
    # pg_restore reads a local protected file via stdin, never a remote URI or shell interpolation.
    with Path(path).open("rb") as handle:
        result = subprocess.run(
            [DOCKER, "exec", "-i", "shared-postgres", "pg_restore", "--list"],
            stdin=handle,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120,
        )
    if result.returncode:
        raise RuntimeError("backup readability failed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("verify-backup", "health", "version", "smoke"))
    parser.add_argument("target")
    args = parser.parse_args()
    try:
        if args.mode == "verify-backup":
            verify_backup(args.target)
        else:
            for command in commands(args.target, args.mode):
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=240 if args.mode == "smoke" else 8,
                )
                if result.returncode:
                    raise RuntimeError("application check failed")
                if args.mode == "version":
                    print(result.stdout.strip())
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        print("NAS check failed; inspect service status locally", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
