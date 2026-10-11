#!/usr/bin/env python3
"""Fixed CHG-20261010-001 candidate checks on disposable restored databases."""

import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

import nas_checks
import verify_nas_restore as restore

STOCK = "ghcr.io/mumukun/stock-analyzer@sha256:f4c7713f1515c51877a89b3bdc4980ab1a373ce5b0ed284f0fc6ef88ee872022"
API = "ghcr.io/mumukun/investment-research-dashboard-api@sha256:1915f2639ff2e27d4a059b5a581dcceacaebabda35aadf71195578e338e0239f"
WEB = "ghcr.io/mumukun/investment-research-dashboard-web@sha256:f48a88b3e27ee5ca14cff07edd6b0718243e7a47547de964c6ac131d300953dc"
OLD_STOCK = "sha256:312c96d54c7ed9e826a67c5a1c43ff2928007d2e5c52d2ac1709345a778feb95"
OLD_API = "sha256:6c41c692d494d1c1f7084df6c768c5eac62410c40d6315e1c3b1acee026ad0ac"
OLD_WEB = "sha256:fd7be7f1a46eed1ea316384a658889e48ae959ac398b2788a973dcc5a4b753cb"


def acceptance(db):
    if not re.fullmatch(r"[a-f0-9]{64}", db):
        raise ValueError("invalid isolated database identity")
    # The database's network=none namespace only permits shared loopback traffic.
    info = json.loads(restore.docker("inspect", db))[0]
    if info["HostConfig"]["NetworkMode"] != "none" or info["HostConfig"].get("Binds"):
        raise ValueError("database must remain isolated")
    containers = []
    checks = []

    def start(image, env, command=()):
        cid = restore.docker(
            "run", "-d", "--pull", "never", "--restart", "no", "--memory", "512m",
            "--name", "chg-20261010-001-accept-" + uuid.uuid4().hex,
            "--label", "investment-platform.change=CHG-20261010-001",
            "--network", "container:" + db,
            *[arg for value in env for arg in ("-e", value)], image, *command,
        )
        if not re.fullmatch(r"[a-f0-9]{64}", cid):
            raise ValueError("invalid isolated application identity")
        containers.append(cid)
        return cid

    def check(cid, command, label):
        for attempt in range(90):
            try:
                restore.docker("exec", cid, *command)
                break
            except subprocess.CalledProcessError:
                if attempt == 89:
                    raise restore.RestoreFailure(label + " failed") from None
                time.sleep(1)
        checks.append(label)
        print(label + " PASS", flush=True)

    def stop(cid):
        restore.docker("rm", "-f", "-v", cid)
        containers.remove(cid)

    stock_env = [
        "STOCK_API_TOKEN=isolated-fixture-only",
        "STOCK_ANALYZER_DATABASE_URL=postgresql://postgres@127.0.0.1:5432/stock_analyzer",
    ]
    api_env = [
        "DATABASE_URL=postgresql+psycopg://postgres@127.0.0.1:5432/investment_dashboard",
        "SEED_DEMO_DATA=false", "AUTH_ENABLED=true", "AUTH_FEISHU_ENABLED=false",
        "AUTH_PASSWORD_ENABLED=true", "AUTH_ADMIN_USERNAME=isolated-acceptance",
        "AUTH_ADMIN_PASSWORD=isolated-fixture-only",
        "AUTH_SESSION_SECRET=isolated-fixture-only-secret-32-chars",
        "APP_ENVIRONMENT=staging", "STOCK_ANALYZER_BASE_URL=",
    ]
    stock_check = ["python", "-c", nas_checks.STOCK_SMOKE]
    api_check = [".venv/bin/python", "scripts/production_smoke.py"]
    cross_check = [".venv/bin/python", "-c", """
import json, urllib.request, urllib.error
url='http://127.0.0.1:8808/api/integrations/investment-dashboard/watchlist?refresh_quotes=false&limit=1'
try:
    urllib.request.urlopen(url,timeout=5)
    raise AssertionError('authentication missing')
except urllib.error.HTTPError as e:
    assert e.code==401
request=urllib.request.Request(url,headers={'Authorization':'Bearer isolated-fixture-only'})
with urllib.request.urlopen(request,timeout=10) as response:
    p=json.load(response)
assert p['ok'] and p['contract_version']=='investment-dashboard-watchlist-v1'
assert p['count']==len(p['items']) and p['quote_refresh']['status']=='not_requested'
"""
    ]
    web_check = ["sh", "-c", "wget -q -O - http://127.0.0.1:9360/ | grep -q 'id=\"app\"'"]
    try:
        stock = start(STOCK, stock_env, ("python", "scripts/api.py"))
        check(stock, stock_check, "candidate stock database/auth contract")
        api = start(API, api_env)
        check(api, api_check, "candidate dashboard restored-data smoke")
        check(api, cross_check, "dashboard-container to stock HTTP/auth contract")
        # Do not run projections or external data refresh. Verify migration state on the clone.
        restore.docker("exec", api, ".venv/bin/alembic", "check")
        checks.append("candidate dashboard migration state")
        stop(api)
        web = start(WEB, [])
        check(web, web_check, "candidate Web serves application")
        stop(web)
        stop(stock)
        stock = start(OLD_STOCK, stock_env, ("python", "scripts/api.py"))
        check(stock, stock_check, "old stock retained-image compatibility")
        # Old app is tested against the clone after the candidate migration; no downgrade.
        api = start(OLD_API, api_env, (
            ".venv/bin/uvicorn", "app.main:app", "--app-dir", "backend",
            "--host", "127.0.0.1", "--port", "8000",
        ))
        check(api, api_check, "old dashboard retained-image compatibility")
        check(api, cross_check, "old dashboard-container to stock HTTP/auth contract")
        stop(api)
        web = start(OLD_WEB, [])
        check(web, web_check, "old Web retained-image compatibility")
    finally:
        cleanup_failed = False
        for cid in reversed(containers[:]):
            try:
                stop(cid)
            except (OSError, subprocess.SubprocessError):
                cleanup_failed = True
        if cleanup_failed:
            raise restore.RestoreFailure("isolated application cleanup failed")
    return {
        "scope": "isolated-restored-data-and-retained-image-compatibility", "result": "PASS",
        "checks": checks, "images": [STOCK, API, WEB, OLD_STOCK, OLD_API, OLD_WEB],
        "note": "Does not certify production configuration, new-runner rollback/resume, external data refresh or browser E2E",
    }


if __name__ == "__main__":
    os.umask(0o077)
    try:
        if len(sys.argv) != 2:
            raise ValueError("one reviewed backup directory required")
        restore.restore(Path(sys.argv[1]), after_restore=acceptance)
    except (ValueError, restore.RestoreFailure) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit("Isolated acceptance stopped; production databases were not targeted.") from None
    except (OSError, subprocess.SubprocessError):
        raise SystemExit("Isolated acceptance stopped; inspect protected local log.") from None
