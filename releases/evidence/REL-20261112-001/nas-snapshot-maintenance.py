#!/usr/bin/env python3
"""One-release, administrator-run maintenance. No sudoers or runner changes.

Run with --start after REL-20261112-001 has DEPLOY_PASS. The detached worker
holds the existing NAS release lock, backs up snapshots, stops only Dashboard
API, runs the deployed maintenance scripts, then restores the same container.
"""
import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import pwd
import subprocess
import sys
import time

RELEASE = 'REL-20261112-001'
ROOT = Path('/volume1/docker/.investment-platform-releases')
API = 'investment-research-dashboard-nas-api-1'
DOCKER = '/usr/local/bin/docker'
OUT = Path('/volume1/homes/freemumu/release-jobs') / RELEASE


def command(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def output(args):
    return subprocess.check_output(args, text=True).strip()


def sql(query):
    return output([DOCKER, 'exec', 'shared-postgres', 'sh', '-c',
        'exec psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d investment_dashboard -At -c "$1"',
        'psql', query])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', action='store_true')
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise SystemExit('Administrator execution is required for the existing release lock.')
    if not (args.start or args.worker):
        raise SystemExit('No changes: use --start only after reviewing this file.')
    if args.start:
        with (OUT / 'maintenance.log').open('x') as log:
            os.chmod(log.name, 0o600)
            owner = pwd.getpwnam('freemumu')
            os.chown(log.name, owner.pw_uid, owner.pw_gid)
            job = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker'],
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True)
        print('Maintenance PID:', job.pid, 'Log:', log.name)
        return
    with (ROOT / 'release.lock').open('r+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        now = datetime.now(timezone(timedelta(hours=8)))
        assert not (now.weekday() < 5 and 9 <= now.hour < 16), 'Outside the authorized off-hours window'
        state = json.loads((ROOT / RELEASE / 'state.json').read_text())
        assert state['last_operation'] == 'deploy' and state['last_result'] == 'PASS', 'Release not complete'
        identity = next(i for i in state['identity'] if i['repository'] == 'investment-research-dashboard')
        assert identity['tag'] == 'v2.12.4'
        info = json.loads(output([DOCKER, 'inspect', API]))[0]
        image = identity['images']['api']
        assert info['Image'] == output([DOCKER, 'image', 'inspect', image, '--format', '{{.Id}}'])
        assert info['State']['Running'], 'Dashboard must start healthy before maintenance'
        assert info['State'].get('Health', {}).get('Status') == 'healthy'
        assert os.statvfs('/volume1').f_bavail * os.statvfs('/volume1').f_frsize > 20 * 1024**3
        assert sql('SELECT count(*) FROM pg_replication_slots') == '0', 'Review replication retention first'
        vacuum = """SELECT coalesce(json_agg(json_build_object('pid',a.pid,'wraparound',
          position('to prevent wraparound' in a.query)>0)), '[]')
          FROM pg_stat_progress_vacuum v JOIN pg_stat_activity a USING(pid)
          WHERE v.datid=(SELECT oid FROM pg_database WHERE datname=current_database())
          AND v.relid IN ('public.snapshots'::regclass,
            (SELECT reltoastrelid FROM pg_class WHERE oid='public.snapshots'::regclass))"""
        workers = json.loads(sql(vacuum))
        assert not any(w['wraparound'] for w in workers), 'Do not interrupt wraparound protection'
        directory = ROOT / RELEASE / 'snapshot-maintenance'
        directory.mkdir(mode=0o700)
        envfile = directory / 'api.env'
        assert all('\n' not in value for value in info['Config']['Env'])
        envfile.write_text('\n'.join(info['Config']['Env']) + '\n')
        envfile.chmod(0o600)
        networks = list(info['NetworkSettings']['Networks'])
        assert len(networks) == 1, 'Review Dashboard network before maintenance'
        base = [DOCKER, 'run', '--rm', '--network', networks[0], '--env-file', str(envfile),
                '--entrypoint', '/app/.venv/bin/python', image]
        stopped = False
        try:
            command([DOCKER, 'stop', '--time', '60', API])
            stopped = True
            print('Dashboard API stopped; creating scoped snapshots backup.', flush=True)
            backup = directory / 'snapshots.dump'
            with backup.open('xb') as handle:
                backup.chmod(0o600)
                command([DOCKER, 'exec', 'shared-postgres', 'sh', '-c',
                    'exec pg_dump -U "$POSTGRES_USER" -d investment_dashboard -Fc --no-owner --no-acl --strict-names --table=public.snapshots'], stdout=handle)
            assert backup.stat().st_size > 0
            with backup.open('rb') as handle:
                command([DOCKER, 'exec', '-i', 'shared-postgres', 'pg_restore', '--list'],
                        stdin=handle, stdout=subprocess.DEVNULL)
            print(json.dumps({'backup_bytes': backup.stat().st_size, 'readability': 'PASS'}), flush=True)
            # Cancel only ordinary autovacuum on this exact table; never other backends.
            workers = json.loads(sql(vacuum))
            assert not any(w['wraparound'] for w in workers), 'Wraparound vacuum started; maintenance stopped'
            for worker in workers:
                sql("SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE pid=" + str(int(worker['pid'])) +
                    " AND backend_type='autovacuum worker' AND position('to prevent wraparound' in query)=0")
            while True:
                result = json.loads(output(base + ['scripts/snapshot_maintenance.py', '--apply']))
                (directory / 'cleanup.json').write_text(json.dumps(result, ensure_ascii=False, default=str))
                print(json.dumps({k: result.get(k) for k in ('deleted_rows', 'remaining_rows', 'error', 'status')}), flush=True)
                assert not result.get('error') and 'remaining_rows' in result, 'Cleanup did not complete'
                if result['remaining_rows'] == 0:
                    break
                assert result['deleted_rows'] > 0, 'Cleanup made no progress'
            result = json.loads(output(base + ['scripts/compact_snapshots.py', '--apply']))
            (directory / 'compaction.json').write_text(json.dumps(result, ensure_ascii=False, default=str))
            print(json.dumps(result, ensure_ascii=False, default=str), flush=True)
        finally:
            envfile.unlink()
            if stopped:
                command([DOCKER, 'start', API])
                for _ in range(60):
                    health = output([DOCKER, 'inspect', API, '--format', '{{.State.Health.Status}}'])
                    if health == 'healthy':
                        break
                    time.sleep(2)
                assert health == 'healthy', 'Dashboard restart needs attention'
                command(['/usr/bin/python3', '/usr/local/lib/investment-platform/nas_checks.py', 'smoke', 'investment-research-dashboard'])
                print('Dashboard restored and smoke PASS', flush=True)
        print('SNAPSHOT_MAINTENANCE_PASS', flush=True)


if __name__ == '__main__':
    main()
