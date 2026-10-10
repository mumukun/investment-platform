#!/usr/bin/env bash
# One-time administrator installation; does not deploy apps or restart Docker.
set -euo pipefail
if [ "$#" -ne 1 ] || [ ! -f "$1" ]; then
  echo "Usage: sudo bash deploy/install-nas-image-release.sh <reviewed-root-config.json>" >&2
  exit 2
fi
if [ "$(id -u)" -ne 0 ]; then
  echo "Administrator installation required" >&2
  exit 2
fi
repo_dir=$(cd "$(dirname "$0")/.." && pwd)
# Validate before installing; the supplied config must already be root-owned.
python3 -c 'import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from nas_image_release import load_config; load_config(Path(sys.argv[2]))' "$repo_dir/scripts" "$1"
install -d -o root -m 755 /usr/local/lib/investment-platform
install -o root -m 644 "$repo_dir/scripts/image_release.py" /usr/local/lib/investment-platform/image_release.py
install -o root -m 644 "$repo_dir/scripts/nas_image_release.py" /usr/local/lib/investment-platform/nas_image_release.py
install -o root -m 644 "$repo_dir/scripts/nas_checks.py" /usr/local/lib/investment-platform/nas_checks.py
install -o root -m 755 "$repo_dir/deploy/nas-image-release" /usr/local/sbin/nas-image-release
install -o root -m 600 "$1" /usr/local/etc/investment-platform-deploy.json
echo "Installed image runner. Existing nas-deploy, sudoers and Docker configuration were not changed."
