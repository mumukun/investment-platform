#!/usr/bin/env python3
"""Restore reviewed DS920plus backups into an isolated, disposable PostgreSQL."""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

DOCKER = "/usr/local/bin/docker"
IMAGE = "sha256:e684c11a6c7c127c1b7602063cc6a13db0a12b62dfd770d83936c089751d498d"
DATABASES = ("stock_analyzer", "investment_dashboard")


class RestoreFailure(RuntimeError):
    """Only fixed stage names and error types; never captured database output."""


def checked_files(folder):
    if os.geteuid() != 0:
        raise ValueError("administrator required")
    if (
        folder.parent != Path("/volume1/docker")
        or not re.fullmatch(r"CHG-20261010-001-backup-[a-z0-9_]{8}", folder.name)
        or folder.is_symlink()
        or folder.stat().st_uid != 0
        or folder.stat().st_mode & 0o077
    ):
        raise ValueError("protected backup directory required")
    files = [folder / (db + ".dump") for db in DATABASES]
    for path in files:
        if (
            path.is_symlink()
            or not path.is_file()
            or path.stat().st_uid != 0
            or path.stat().st_mode & 0o077
            or not path.stat().st_size
        ):
            raise ValueError("protected nonempty backup required")
    return files


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def docker(*args, **kwargs):
    return subprocess.run(
        [DOCKER, *args], check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=600, **kwargs
    ).stdout.decode().strip()


def restore(folder, after_restore=None):
    files = checked_files(folder)
    hashes = {path.name: digest(path) for path in files}
    name = "chg-20261010-001-restore-" + uuid.uuid4().hex
    container = None
    stage = "create isolated container"
    try:
        # No host mounts, published ports, production credentials or shared volumes.
        container = docker(
            "run", "-d", "--pull", "never", "--network", "none",
            # DS920plus has memory limits but no CPU CFS quota support.
            "--restart", "no", "--memory", "1g",
            "--name", name, "--label", "investment-platform.change=CHG-20261010-001",
            "-e", "POSTGRES_USER=postgres", "-e", "POSTGRES_DB=postgres",
            "-e", "POSTGRES_HOST_AUTH_METHOD=trust", IMAGE,
        )
        if not re.fullmatch(r"[a-f0-9]{64}", container):
            container = None
            raise ValueError("unexpected container identity")
        stage = "wait for isolated PostgreSQL"
        for attempt in range(60):
            try:
                # Entry-point initialization uses a temporary Unix-only server.
                docker("exec", container, "pg_isready", "-h", "127.0.0.1", "-U", "postgres", "-d", "postgres")
                break
            except subprocess.CalledProcessError:
                if attempt == 59:
                    raise
                time.sleep(1)
        results = {}
        for db, path in zip(DATABASES, files):
            stage = "restore " + db
            docker("exec", container, "createdb", "-U", "postgres", db)
            with path.open("rb") as f:
                docker(
                    "exec", "-i", container, "pg_restore", "--exit-on-error",
                    "--no-owner", "--no-acl", "-U", "postgres", "-d", db, stdin=f,
                )
            if digest(path) != hashes[path.name]:
                raise ValueError("backup changed during restore")
            table_count = int(docker(
                "exec", container, "psql", "-U", "postgres", "-d", db, "-Atc",
                "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                "WHERE c.relkind IN ('r','p') AND n.nspname NOT IN ('pg_catalog','information_schema') "
                "AND n.nspname NOT LIKE 'pg_toast%';",
            ))
            if table_count < 1:
                raise ValueError("restored application tables missing")
            results[db] = {
                "status": "PASS", "backup_sha256": hashes[path.name],
                "application_tables": table_count,
            }
            print(db + ": isolated restore PASS", flush=True)
        acceptance = None
        if after_restore is not None:
            stage = "isolated candidate acceptance"
            acceptance = after_restore(container)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        # Database errors can contain application data; never print captured output.
        code = " exit=" + str(error.returncode) if isinstance(error, subprocess.CalledProcessError) else ""
        raise RestoreFailure(
            "restore verification failed at " + stage + "; " + type(error).__name__ + code
        ) from None
    finally:
        if container:
            # Only the exact ID returned by our own successful create; removes anonymous volume.
            try:
                docker("rm", "-f", "-v", container)
            except (OSError, subprocess.SubprocessError):
                raise RestoreFailure("temporary container cleanup failed") from None
    receipt = {
        "scope": "isolated-database-restore", "result": "PASS",
        "at": datetime.now(timezone.utc).isoformat(), "postgres_image_id": IMAGE,
        "databases": results, "temporary_container_removed": True,
        "note": "Does not verify application rollback or migration compatibility",
    }
    if acceptance is not None:
        receipt["candidate_acceptance"] = acceptance
    path = folder / ("restore-receipt-" + uuid.uuid4().hex + ".json")
    with path.open("x") as f:
        os.chmod(path, 0o600)
        json.dump(receipt, f, indent=2)
    print("receipt: " + str(path))


if __name__ == "__main__":
    os.umask(0o077)
    try:
        if len(sys.argv) != 2:
            raise ValueError("one reviewed backup directory required")
        restore(Path(sys.argv[1]))
    except (ValueError, RestoreFailure) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit("Restore check stopped; no production database was targeted.") from None
    except (OSError, subprocess.SubprocessError):
        raise SystemExit("Restore check stopped; no production database was targeted.") from None
