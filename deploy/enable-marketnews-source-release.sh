#!/usr/bin/env bash
# One administrator upgrade; preserve current root config and existing sudo rules.
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo 'Administrator installation required' >&2; exit 2; }
repo_dir=$(cd "$(dirname "$0")/.." && pwd)
/usr/bin/python3 - "$repo_dir" <<'PY'
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
repo = Path(sys.argv[1])
sys.path.insert(0, str(repo / 'scripts'))
from nas_image_release import load_config, release_lock
from image_release import require
config_path = Path('/usr/local/etc/investment-platform-deploy.json')
config = load_config(config_path)
root = Path(config['state_root'])
require(root.stat().st_uid == 0 and not root.stat().st_mode & 0o077, "protected root state directory required")
with release_lock(root / 'release.lock'):
    backup = Path(tempfile.mkdtemp(prefix='runner-source-upgrade-', dir=str(root)))
    backup.chmod(0o700)
    # Preserve the active root-reviewed commands; don't overwrite other repositories from an example.
    for path in [config_path, Path('/usr/local/sbin/nas-image-release')] + list(Path('/usr/local/lib/investment-platform').glob('*.py')):
        shutil.copy2(path, backup / path.name)
        (backup / path.name).chmod(0o600)
    section = json.loads((repo / 'deploy/nas-config.DS920plus.json').read_text())['source_repositories']['marketNewsFeed']
    existing = config.setdefault('source_repositories', {}).get('marketNewsFeed')
    if existing is not None and existing != section:
        raise SystemExit('Existing source configuration differs; preserve it for administrator review')
    config['source_repositories']['marketNewsFeed'] = section
    reviewed = backup / 'updated-config.json'
    reviewed.write_text(json.dumps(config, indent=2) + '\n')
    reviewed.chmod(0o600)
    load_config(reviewed)
    subprocess.run(['/bin/bash', str(repo / 'deploy/install-nas-image-release.sh'), str(reviewed)], check=True)
    print('MARKETNEWS_SOURCE_RUNNER=ENABLED')
    print('PROTECTED_RUNNER_BACKUP=' + str(backup))
    print('Existing sudoers, Docker configuration and running services were preserved.')
PY
