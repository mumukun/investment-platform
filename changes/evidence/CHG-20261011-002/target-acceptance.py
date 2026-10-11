"""Release-only NAS acceptance; never targets live DB for writes or publishes ports."""
import json, subprocess, sys, time, uuid
from datetime import datetime, timezone
D = "/usr/local/bin/docker"
PG = "sha256:e684c11a6c7c127c1b7602063cc6a13db0a12b62dfd770d83936c089751d498d"
containers = []
checks = []

def run(*args, **kwargs):
    return subprocess.run([D, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True, timeout=600, **kwargs).stdout.decode().strip()

def create(image, env, command=(), network="none"):
    cid = run("run", "-d", "--pull", "never", "--restart", "no", "--memory", "1g",
              "--name", "rel-20261011-001-check-" + uuid.uuid4().hex,
              "--label", "investment-platform.release=REL-20261011-001",
              "--network", network, *[a for e in env for a in ("-e", e)], image, *command)
    assert len(cid) == 64 and all(c in "0123456789abcdef" for c in cid)
    containers.append(cid)
    return cid

def stop(cid):
    run("rm", "-f", "-v", cid)
    containers.remove(cid)

def check(cid, command, name):
    for i in range(60):
        try:
            result = run("exec", cid, *command)
            checks.append({"check": name, "result": "PASS", "summary": result if name in ("frozen Provider historical real-data contract", "frozen Consumer to Provider concept metadata", "retained Provider rollback compatibility") else "command passed"})
            print(name + " PASS", flush=True)
            return
        except subprocess.CalledProcessError:
            if i == 59: raise RuntimeError(name + " failed") from None
            time.sleep(1)

STOCK_CHECK = """
import json, urllib.request
base='http://127.0.0.1:8808'
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
with opener.open(base+'/api/health', timeout=5) as r: assert json.load(r)['ok']
url=base+'/api/integrations/investment-dashboard/swing-selection?trade_date=2026-10-09&limit=100&contract_version=investment-dashboard-swing-selection-v3'
req=urllib.request.Request(url,headers={'Authorization':'Bearer isolated-fixture-only'})
with opener.open(req, timeout=45) as r: p=json.load(r)
assert p['ok'] and p['contract_version']=='investment-dashboard-swing-selection-v3' and p['items']
assert not p.get('is_mock', False)
covered=sum(bool(x.get('concept_tags')) for x in p['items'])
for x in p['items']:
 m=x.get('classification_meta') or {}
 assert not m.get('concept_snapshot_date') or m['concept_snapshot_date'] <= '2026-10-09'
 if x.get('concept_tags'): assert m.get('concept_source') and m.get('concept_quality') in ('healthy','stale','partial')
print(json.dumps({'items':len(p['items']),'concept_covered':covered,'qualities':sorted({(x.get('classification_meta') or {}).get('concept_quality','unknown') for x in p['items']})}))
"""
CROSS_CHECK = """
import json,sys,urllib.request
sys.path.insert(0,'backend')
import app.integrations.stock_analyzer as adapter
from app.integrations.stock_analyzer import StockAnalyzerClient
def historical_request(req, timeout):
 req.full_url += '&trade_date=2026-10-09'
 return urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=timeout)
adapter.urlopen=historical_request
p=StockAnalyzerClient(base_url='http://127.0.0.1:8808', token='isolated-fixture-only',timeout_seconds=45).fetch_swing_selection(limit=100)
assert p.items
assert any(x.concept_tags for x in p.items), 'no real concept memberships available'
for x in p.items:
 m=x.classification_meta
 assert not m.get('concept_snapshot_date') or m['concept_snapshot_date'] <= '2026-10-09'
print(json.dumps({'items':len(p.items),'concept_covered':sum(bool(x.concept_tags) for x in p.items)}))
"""

def main(plan):
    from pathlib import Path
    entries=plan['repositories']
    images={e['candidate']['repository']:e['candidate'] for e in entries}
    for c in images.values():
        for component,ref in c['images'].items():
            info=json.loads(run('image','inspect',ref))[0]
            assert info['Id']==c['image_ids'][component]
            assert info['Config']['Labels']['org.opencontainers.image.revision']==c['commit_sha']
            assert info['Config']['Labels']['org.opencontainers.image.version']==c['version']
    before={n:run('inspect','--format','{{.Id}} {{.Image}} {{.State.StartedAt}}',n) for n in ['stock-api','stock-watch','investment-research-dashboard-nas-api-1','investment-research-dashboard-nas-web-1']}
    db=create(PG,['POSTGRES_USER=postgres','POSTGRES_DB=postgres','POSTGRES_HOST_AUTH_METHOD=trust'])
    check(db,['pg_isready','-h','127.0.0.1','-U','postgres'], 'isolated PostgreSQL readiness')
    for name in ['stock_analyzer','investment_dashboard']:
        run('exec',db,'createdb','-U','postgres',name)
        dump=subprocess.Popen([D,'exec','shared-postgres','sh','-c','exec pg_dump -U "$POSTGRES_USER" -d '+name+' -Fc --no-owner --no-acl'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        try:
            subprocess.run([D,'exec','-i',db,'pg_restore','--exit-on-error','--no-owner','--no-acl','-U','postgres','-d',name],stdin=dump.stdout,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=600,check=True)
        finally:
            dump.stdout.close()
        assert dump.wait(timeout=30)==0
        checks.append({'check':'stream real-data clone '+name,'result':'PASS'})
        print('isolated clone '+name+' PASS',flush=True)
    stock_env=['STOCK_API_TOKEN=isolated-fixture-only','STOCK_ANALYZER_DATABASE_URL=postgresql://postgres@127.0.0.1:5432/stock_analyzer']
    api_env=['DATABASE_URL=postgresql+psycopg://postgres@127.0.0.1:5432/investment_dashboard','SEED_DEMO_DATA=false','AUTH_ENABLED=false','AUTH_FEISHU_ENABLED=false','AUTH_SESSION_SECRET=isolated-fixture-only-secret-32-chars','APP_ENVIRONMENT=staging','STOCK_ANALYZER_BASE_URL=http://127.0.0.1:8808','STOCK_ANALYZER_TOKEN=isolated-fixture-only']
    stock=create(images['stock-analyzer']['images']['app'],stock_env,['python','scripts/api.py'],'container:'+db)
    check(stock,['python','-c',STOCK_CHECK],'frozen Provider historical real-data contract')
    api=create(images['investment-research-dashboard']['images']['api'],api_env,network='container:'+db)
    check(api,['.venv/bin/python','scripts/production_smoke.py'],'frozen Dashboard real-data smoke')
    check(api,['.venv/bin/python','-c',CROSS_CHECK],'frozen Consumer to Provider concept metadata')
    check(api,['.venv/bin/alembic','check'],'frozen Dashboard migration compatibility')
    stop(api)
    web=create(images['investment-research-dashboard']['images']['web'],[],network='container:'+db)
    check(web,['sh','-c','wget -q -O /dev/null http://127.0.0.1:9360/'],'frozen Web serves application')
    stop(web);stop(stock)
    for e in entries:
        if e['candidate']['repository']=='stock-analyzer':
            old=create(e['rollback']['images']['app'],stock_env,['python','scripts/api.py'],'container:'+db)
            check(old,['python','-c',STOCK_CHECK],'retained Provider rollback compatibility')
            stop(old)
        else:
            old=create(e['rollback']['images']['api'],api_env,['.venv/bin/uvicorn','app.main:app','--app-dir','backend','--host','127.0.0.1','--port','8000'],'container:'+db)
            check(old,['.venv/bin/python','scripts/production_smoke.py'],'retained Dashboard rollback compatibility')
            stop(old)
            old=create(e['rollback']['images']['web'],[],network='container:'+db)
            check(old,['sh','-c','wget -q -O /dev/null http://127.0.0.1:9360/'],'retained Web rollback compatibility')
            stop(old)
    stop(db)
    after={n:run('inspect','--format','{{.Id}} {{.Image}} {{.State.StartedAt}}',n) for n in before}
    assert before==after, 'production runtime changed during isolated acceptance'
    print(json.dumps({'target_acceptance':{'result':'PASS','at':datetime.now(timezone.utc).isoformat(),'scope':'exact frozen images on isolated live-data clone; no production credential copied, ports, mounts, scheduler, refresh or production mutation','checks':checks,'production_runtime_unchanged':True,'cleanup':'PASS'}}))

if __name__=='__main__':
    try:
        main(json.loads(PLAN_JSON))
    except Exception as exc:
        print(json.dumps({'target_acceptance':{'result':'FAILED','error_type':type(exc).__name__,'checks':checks}}))
        raise SystemExit(1) from None
    finally:
        for cid in reversed(containers[:]):
            try: stop(cid)
            except Exception: print('isolated fixture cleanup FAILED', file=sys.stderr)
