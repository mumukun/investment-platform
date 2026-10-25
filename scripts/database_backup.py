#!/usr/bin/env python3
"""Independent logical backups. Default preflight; --apply is explicit execution.

Use local Docker PostgreSQL tools. No network downloads, service restarts or retention
deletions. Credentials remain in the container's existing PostgreSQL environment.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid


def checked_config(config):
    if not isinstance(config, list) or not config:
        raise ValueError('nonempty database configuration required')
    names = set()
    for row in config:
        if set(row) != {'name', 'container', 'database', 'user'}:
            raise ValueError('only name/container/database/user permitted; no credentials')
        if not all(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', v) for v in row.values()):
            raise ValueError('invalid identifier')
        if row['name'] in names:
            raise ValueError('duplicate backup name')
        names.add(row['name'])
    return config


def run(args, **kwargs):
    try:
        return subprocess.run(args, check=True, stderr=subprocess.PIPE, timeout=1800, **kwargs)
    except subprocess.SubprocessError:
        raise RuntimeError('database backup command failed; inspect protected local logs') from None


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def backup(config, root, *, apply=False):
    checked_config(config)
    for row in config:
        run(['docker', 'exec', row['container'], 'pg_isready', '-U', row['user'], '-d', row['database']], stdout=subprocess.PIPE)
    if not apply:
        return {'status': 'preflight', 'databases': [r['name'] for r in config],
                'note': 'No dump, retention change, restore or schedule installation performed'}
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError('existing nonsymlink destination directory required')
    folder = root / ('backup-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:8])
    folder.mkdir(mode=0o700)
    manifest = {'version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
                'status': 'incomplete', 'databases': [], 'restore_verified': False}
    for row in config:
        partial = folder / (row['name'] + '.partial')
        with partial.open('xb') as handle:
            os.chmod(partial, 0o600)
            run(['docker', 'exec', row['container'], 'pg_dump', '-Fc', '--no-owner',
                 '--no-acl', '-U', row['user'], '-d', row['database']], stdout=handle)
            handle.flush()
            os.fsync(handle.fileno())
        if partial.stat().st_size == 0:
            raise ValueError('empty dump')
        with partial.open('rb') as handle:
            run(['docker', 'exec', '-i', row['container'], 'pg_restore', '--list'], stdin=handle, stdout=subprocess.PIPE)
        target = partial.with_suffix('.dump')
        partial.rename(target)
        manifest['databases'].append({'name': row['name'], 'file': target.name,
                                      'bytes': target.stat().st_size, 'sha256': digest(target)})
    manifest['status'] = 'archive_readable'
    with (folder / 'manifest.json').open('x') as handle:
        os.chmod(handle.name, 0o600)
        json.dump(manifest, handle, indent=2)
    return {'folder': str(folder), **manifest}


def verify(folder):
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text())
    if manifest.get('status') != 'archive_readable' or not manifest.get('databases'):
        raise ValueError('incomplete backup')
    for row in manifest['databases']:
        if Path(row['file']).name != row['file']:
            raise ValueError('unsafe file path')
        path = folder / row['file']
        if path.is_symlink() or path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError('backup integrity check failed')
    return {'status': 'checksum_verified', 'restore_verified': False}


def restore_check(folder, image):
    """Always restore to our own network-isolated disposable container."""
    verify(folder)
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', image or ''):
        raise ValueError('local immutable PostgreSQL image ID required')
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text())
    container = None
    try:
        output = run(['docker', 'run', '-d', '--pull', 'never', '--network', 'none',
                      '--restart', 'no', '--memory', '1g', '--name', 'backup-check-' + uuid.uuid4().hex,
                      '-e', 'POSTGRES_HOST_AUTH_METHOD=trust', image], stdout=subprocess.PIPE)
        container = output.stdout.decode().strip()
        if not re.fullmatch(r'[0-9a-f]{64}', container):
            container = None
            raise ValueError('invalid disposable container identity')
        for attempt in range(30):
            try:
                run(['docker', 'exec', container, 'pg_isready', '-h', '127.0.0.1', '-U', 'postgres'], stdout=subprocess.PIPE)
                break
            except RuntimeError:
                if attempt == 29:
                    raise
                time.sleep(1)
        checked = []
        for index, row in enumerate(manifest['databases']):
            database = f'restore_test_{index}'
            run(['docker', 'exec', container, 'createdb', '-U', 'postgres', database], stdout=subprocess.PIPE)
            with (folder / row['file']).open('rb') as handle:
                run(['docker', 'exec', '-i', container, 'pg_restore', '--exit-on-error',
                     '--no-owner', '--no-acl', '-U', 'postgres', '-d', database], stdin=handle, stdout=subprocess.PIPE)
            checked.append(row['name'])
        verify(folder)
    finally:
        if container:
            run(['docker', 'rm', '-f', '-v', container], stdout=subprocess.PIPE)
    receipt = {'status': 'isolated_restore_passed', 'databases': checked, 'image': image,
               'at': datetime.now(timezone.utc).isoformat(), 'temporary_container_removed': True,
               'note': 'Restores database archives; does not validate application behavior'}
    with (folder / ('restore-' + uuid.uuid4().hex + '.json')).open('x') as handle:
        os.chmod(handle.name, 0o600)
        json.dump(receipt, handle, indent=2)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--restore-check', type=Path)
    parser.add_argument('--image', help='local immutable sha256 image ID; never pulls')
    args = parser.parse_args()
    os.umask(0o077)
    if args.restore_check:
        result = restore_check(args.restore_check, args.image)
    elif args.verify:
        result = verify(args.verify)
    else:
        if not args.config or (args.apply and not args.destination):
            parser.error('--config required; --apply additionally requires --destination')
        result = backup(json.loads(args.config.read_text()), args.destination, apply=args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
