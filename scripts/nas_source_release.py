"""Restricted marketNewsFeed SOURCE_TAG_BUILD support for the existing NAS runner."""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from image_release import IMAGE_ID, SHA, VERSION, require, file_hash
from nas_image_release import atomic_json, release_lock, run

REPOSITORY = 'marketNewsFeed'
SERVICE = 'market-news-feed'
PATH = '/volume1/docker/marketNewsFeed'


def validate_source_plan(plan, formal=False, preparation=False):
    require(not (formal and preparation), "formal operations cannot use preparation gates")
    require(plan.get('schema_version') == 'image-release-v1', 'unsupported schema')
    require(plan.get('artifact_model') == 'SOURCE_TAG_BUILD', 'source artifact required')
    require(re.fullmatch(r'REL-[0-9]{8}-[0-9]{3}', plan.get('release_id', '')), 'invalid Release ID')
    statuses = {'READY_FOR_FORMAL_RELEASE', 'NEEDS_TARGET_VERIFICATION'} if preparation else {'READY_FOR_FORMAL_RELEASE'}
    require(plan.get('environment') == 'Production' and plan.get('status') in statuses, 'prepared Production plan required')
    entries = plan.get('repositories', [])
    require(len(entries) == 1 and entries[0].get('repository') == REPOSITORY, 'source scope is marketNewsFeed only')
    require(plan.get('release_order') == [REPOSITORY], 'explicit source order required')
    entry = entries[0]
    for identity in (entry, entry.get('expected_production', {})):
        require(re.fullmatch('v' + VERSION.pattern, identity.get('tag', '')), 'immutable semver Tag required')
        require(SHA.fullmatch(identity.get('commit_sha', '')), 'exact Commit required')
    require(IMAGE_ID.fullmatch(entry['expected_production'].get('image_id', '')), 'verified baseline image required')
    quality = entry.get('quality', {})
    require(quality.get('status') == 'PASS' and quality.get('commit_sha') == entry['commit_sha'] and quality.get('evidence'), 'frozen source quality evidence required')
    for name in ('scope', 'compatibility', 'integration', 'real_data', 'configuration', 'rollback'):
        gate = plan.get('gates', {}).get(name, {})
        if preparation and name not in {'scope', 'compatibility'}:
            require(gate.get('status') in {'PASS', 'NOT_RUN', 'PENDING'}, 'preparation gate missing: ' + name)
            require(gate['status'] != 'PASS' or bool(gate.get('evidence')), 'PASS evidence missing: ' + name)
        else:
            require(gate.get('status') == 'PASS' and gate.get('evidence'), 'release gate missing: ' + name)
    if formal:
        auth = plan.get('authorization', {})
        require(auth.get('status') == 'FORMAL' and auth.get('evidence'), 'formal authorization required')


def execute_source(plan, config, mode):
    require(mode in {'preflight', 'deploy', 'verify'}, 'unsupported source operation')
    validate_source_plan(plan, formal=mode == 'deploy', preparation=mode == 'preflight')
    item = config.get('source_repositories', {}).get(REPOSITORY)
    require(item is not None, 'marketNewsFeed source runner is not enabled by administrator')
    entry = plan['repositories'][0]
    root = Path(config['state_root'])
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    require(not root.is_symlink() and root.stat().st_uid == 0 and not root.stat().st_mode & 0o077, 'state root must be root-owned mode 700')
    with release_lock(root / 'release.lock'):
        directory = root / plan['release_id']
        require(not directory.is_symlink(), 'invalid source state directory')
        state_file = directory / 'source-state.json'
        if mode == 'verify':
            require(state_file.exists(), 'source deployment receipt required')
            state = json.loads(state_file.read_text())
            require(state.get('status') == 'PASS' and state['tag'] == entry['tag'] and state['commit_sha'] == entry['commit_sha'], 'successful matching source receipt required')
            check_identity(config, entry, state['image_id'])
            verify(item)
            print(json.dumps({'receipt': state}), flush=True)
            return
        # Never silently replay a failed or completed build from the same Release ID.
        require(not state_file.exists(), 'source Release ID already used; inspect saved receipt')
        check_baseline(config, entry)
        git(config, 'fetch', 'origin', '--tags', '--prune')
        require(git(config, 'rev-parse', entry['tag'] + '^{commit}') == entry['commit_sha'], 'Tag SHA mismatch')
        git(config, 'merge-base', '--is-ancestor', entry['commit_sha'], 'origin/main')
        if mode == 'preflight':
            print(json.dumps({'source_preflight': 'PASS', 'repository': REPOSITORY, 'tag': entry['tag'], 'commit_sha': entry['commit_sha']}), flush=True)
            return
        directory.mkdir(mode=0o700)
        directory.chmod(0o700)
        state = {'release_id': plan['release_id'], 'repository': REPOSITORY, 'artifact_model': 'SOURCE_TAG_BUILD', 'tag': entry['tag'], 'commit_sha': entry['commit_sha'], 'status': 'IN_PROGRESS', 'stage': 'backup', 'previous': entry['expected_production'], 'started_at': datetime.now(timezone.utc).isoformat()}
        atomic_json(state_file, state)
        try:
            backup = directory / 'market_news.dump'
            with backup.open('wb') as handle:
                backup.chmod(0o600)
                run(item['backup_command'], output=handle, timeout=600)
            require(backup.stat().st_size > 0, 'empty source database backup')
            run([arg.replace('{backup}', str(backup)) for arg in item['verify_backup_command']])
            state['backup'] = {'path': str(backup), 'sha256': file_hash(backup), 'size': backup.stat().st_size, 'readability': 'PASS'}
            # Retain the verified old image and config; never automatically downgrade the DB.
            previous = entry['expected_production']
            run(['docker', 'image', 'tag', previous['image_id'], 'marketnewsfeed-market-news-feed:rollback-' + previous['tag']])
            env = directory / 'runtime.env'
            env.write_bytes((Path(PATH) / '.env').read_bytes())
            env.chmod(0o600)
            state['stage'] = 'deploy'
            atomic_json(state_file, state)
            check_baseline(config, entry)
            git(config, 'checkout', '--detach', entry['commit_sha'])
            with (directory / 'deployment.log').open('wb') as handle:
                (directory / 'deployment.log').chmod(0o600)
                run(['/usr/bin/sudo', '-u', config['deploy_user'], '/usr/bin/env', 'PATH=/usr/local/bin:/usr/bin:/bin', '/bin/bash', PATH + '/deploy.sh', entry['tag']], output=handle, timeout=1800)
            state['image_id'] = current_image()
            state['stage'] = 'verify'
            atomic_json(state_file, state)
            check_identity(config, entry, state['image_id'])
            verify(item)
            state['status'] = 'PASS'
        except Exception:
            state['status'] = 'FAILED'
            try:
                state['observed'] = {'commit_sha': git(config, 'rev-parse', 'HEAD'), 'image_id': current_image()}
            except Exception:
                state['observed'] = {'status': 'UNAVAILABLE'}
            raise
        finally:
            state['completed_at'] = datetime.now(timezone.utc).isoformat()
            atomic_json(state_file, state)
            print(json.dumps({'receipt': state}), flush=True)


def git(config, *args):
    return run(['/usr/bin/sudo', '-u', config['deploy_user'], config['git_bin'], '-C', PATH, *args])


def current_image():
    container = run(['docker', 'compose', '-f', PATH + '/docker-compose.yml', 'ps', '-q', SERVICE])
    require(bool(container) and '\n' not in container, 'one running marketNewsFeed container required')
    return run(['docker', 'inspect', container, '--format', '{{.Image}}'])


def check_identity(config, entry, image):
    require(not git(config, 'status', '--porcelain', '--untracked-files=no'), 'tracked source worktree changes block release')
    require(git(config, 'rev-parse', 'HEAD') == entry['commit_sha'], 'production Commit drift')
    require(git(config, 'rev-parse', entry['tag'] + '^{commit}') == entry['commit_sha'], 'production Tag drift')
    require(current_image() == image, 'production image drift')


def check_baseline(config, entry):
    previous = entry['expected_production']
    check_identity(config, previous, previous['image_id'])


def verify(item):
    for attempt in range(20):
        try:
            run(item['health_command'], timeout=10)
            break
        except RuntimeError:
            if attempt == 19:
                raise
            time.sleep(3)
    run(item['smoke_command'], timeout=60)
