"""One administrator step for the approved CHG007 runner; no app/DB restart."""
import fcntl
import hashlib
import json
import os
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def main():
    if os.geteuid() != 0:
        raise RuntimeError('Run with sudo in an administrator terminal')
    os.umask(0o077)
    task = Path(__file__).resolve().parent
    manifest = json.loads((task / 'package.json').read_text())
    config_path = Path('/usr/local/etc/investment-platform-deploy.json')
    if config_path.is_symlink() or config_path.stat().st_uid != 0 or stat.S_IMODE(config_path.stat().st_mode) & 0o022:
        raise RuntimeError('Existing administrator config ownership is invalid')
    config = json.loads(config_path.read_text())
    state_root = Path(config['state_root'])
    if str(state_root) != '/volume1/docker/.investment-platform-releases':
        raise RuntimeError('Unexpected release state path')
    with (state_root / 'release.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        contents = {}
        for relative, expected in manifest['files'].items():
            path = task / 'payload' / relative
            if path.is_symlink():
                raise RuntimeError('Payload symlink rejected')
            body = path.read_bytes()
            if hashlib.sha256(body).hexdigest() != expected:
                raise RuntimeError('Payload hash mismatch: ' + relative)
            contents[relative] = body
        for target, expected in manifest['expected_installed'].items():
            if hashlib.sha256(Path(target).read_bytes()).hexdigest() != expected:
                raise RuntimeError('Installed runner drift: ' + target)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup = state_root / ('runner-CHG-20261022-007-' + stamp)
        backup.mkdir(mode=0o700)
        shutil.copy2(str(config_path), str(backup / 'previous-config.json'))
        for target in manifest['expected_installed']:
            shutil.copy2(target, str(backup / Path(target).name))
        # Stage verified bytes as root-owned files before invoking the installer.
        stage = backup / 'approved-payload'
        for relative, body in contents.items():
            output = stage / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(body)
        reviewed = json.loads(contents['deploy/nas-config.DS920plus.json'].decode())
        changed = []
        for section in ('repositories', 'source_repositories'):
            for name, template in reviewed[section].items():
                current = config[section][name]
                if current['path'] != template['path']:
                    raise RuntimeError('Repository path drift: ' + name)
                current['table_backup_command'] = template['table_backup_command']
                changed.append(name)
        merged = backup / 'merged-config.json'
        merged.write_text(json.dumps(config, indent=2) + '\n')
        os.chmod(str(merged), 0o600)
        subprocess.run(['/bin/bash', str(stage / 'deploy/install-nas-image-release.sh'), str(merged)], check=True)
        installed = {}
        for relative, target in manifest['runtime_targets'].items():
            actual = hashlib.sha256(Path(target).read_bytes()).hexdigest()
            if actual != manifest['files'][relative]:
                raise RuntimeError('Installed payload mismatch: ' + target)
            installed[target] = actual
        receipt = {'change_id': 'CHG-20261022-007', 'status': 'INSTALLED',
                   'governance_commit': manifest['governance_commit'], 'installed_hashes': installed,
                   'mechanism_rollback_directory': str(backup), 'table_commands_updated': changed,
                   'apps_restarted': False, 'database_touched': False,
                   'completed_at': datetime.now(timezone.utc).isoformat()}
        (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        public = task / 'installed-receipt.json'
        public.write_text(json.dumps(receipt, indent=2) + '\n')
        os.chmod(str(public), 0o644)
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
