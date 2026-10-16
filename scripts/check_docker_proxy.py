#!/usr/bin/env python3
"""Read-only GHCR connection comparison; never edits/restarts Docker."""

import argparse
import json
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit


def probe(proxy):
    handler = urllib.request.ProxyHandler({"https": proxy} if proxy else {})
    opener = urllib.request.build_opener(handler)
    started = time.monotonic()
    try:
        response = opener.open("https://ghcr.io/v2/", timeout=10)
        code = response.status
        response.close()
    except urllib.error.HTTPError as error:
        code = error.code
        error.close()
    except (OSError, urllib.error.URLError):
        return {
            "reachable": False,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
    return {
        "reachable": code in {200, 401},
        "http_status": code,
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }


def daemon_proxy_status(info, expected):
    # Docker JSON keys are case-sensitive; missing keys are unknown, never false.
    if not all(key in info for key in ("HttpProxy", "HttpsProxy")):
        raise ValueError("Docker proxy fields unavailable; do not infer direct access")
    return {
        "daemon_http_proxy_configured": bool(info["HttpProxy"]),
        "daemon_https_proxy_configured": bool(info["HttpsProxy"]),
        "daemon_uses_expected_mihomo": all(
            info[key] == expected for key in ("HttpProxy", "HttpsProxy")
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--proxy", default="http://127.0.0.1:7890", help="NAS mihomo HTTP/mixed proxy URL"
    )
    parser.add_argument("--compare-direct", action="store_true", help="Explicit diagnostic only")
    args = parser.parse_args()
    url = urlsplit(args.proxy)
    if (
        url.scheme not in {"http", "https"}
        or not url.hostname
        or url.username
        or url.password
    ):
        parser.error("HTTP proxy URL without embedded credentials required")
    info = json.loads(
        subprocess.check_output(["docker", "info", "--format", "{{json .}}"], text=True)
    )
    print(
        json.dumps(
            {
                "docker_version": info.get("ServerVersion"),
                **daemon_proxy_status(info, args.proxy),
                **({"direct_registry_connection": probe(None)} if args.compare_direct else {}),
                "mihomo_registry_connection": probe(args.proxy),
                "note": "connection timing only; measure private image pull throughput separately",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
