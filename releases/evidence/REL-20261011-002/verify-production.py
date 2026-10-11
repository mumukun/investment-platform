"""Read-only checks for the frozen release; never print data or credentials."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLAN = json.loads((ROOT / "changes/evidence/CHG-20261011-002/final-image-release.plan.json").read_text())
SEAT_CHECK = '''
import json,sys,urllib.request,urllib.error
from datetime import date
sys.path.insert(0,'backend')
from app.config import get_settings
from app.auth import SESSION_COOKIE,AuthUser,issue_session
from app.version import build_metadata
from app.integrations.stock_analyzer import StockAnalyzerClient
from app.integrations.seat_tracking import fetch_directory,fetch_tracking,fetch_case
s=get_settings()
assert not s.seed_demo_data and s.auth_enabled
metadata=build_metadata()
assert metadata['app_version']=='0.17.0'
assert metadata['git_commit']=='054802065d60d2460e6098542da59fa785652ced'
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
base='http://127.0.0.1:8000'
token=issue_session(s,AuthUser(open_id='production-smoke',name='Production smoke',role='admin',auth_type='password'))
checks=[]
for path in ['/api/v1/seat-tracking/subscriptions','/api/v1/seat-tracking/reports?observation_date=2026-10-09&window=5','/api/v1/seat-tracking/reviews','/api/v1/system/version']:
 try:
  opener.open(base+path,timeout=10)
  raise AssertionError('authentication missing')
 except urllib.error.HTTPError as e:
  assert e.code==401
 with opener.open(urllib.request.Request(base+path,headers={'Cookie':SESSION_COOKIE+'='+token}),timeout=15) as response:
  p=json.load(response)
  assert response.status==200
 if path.endswith('/reviews'):assert isinstance(p,list)
 elif '/system/version' not in path:assert isinstance(p['items'],list)
 checks.append({'check':path.split('?')[0]+' authenticated read','result':'PASS'})
client=StockAnalyzerClient(s.stock_analyzer_base_url,s.stock_analyzer_token,s.stock_analyzer_timeout_seconds)
observed=date(2026,10,9)
directory=fetch_directory(client,'紫阳东路',observed)
assert any(x['code']=='10026937' for x in directory['items'])
tracking=fetch_tracking(client,'10026937',observed,5)
assert tracking['seat']['code']=='10026937'
case=fetch_case(client,'000980',date(2026,9,28),observed)
checks.extend([{'check':'live seat directory through strict Consumer','result':'PASS'}, {'check':'live five-market-day tracking through strict Consumer','result':'PASS'}, {'check':'live case outcomes through strict Consumer','result':'PASS'}])
from sqlalchemy import text
from app.database import engine
with engine.connect() as connection:
 assert connection.scalar(text('select version_num from alembic_version'))=='a8d6210f1101'
 for table in ['seat_subscriptions','seat_reviews']:
  assert connection.scalar(text("select to_regclass(:table)"),{'table':table})
checks.append({'check':'production migration a8d6210f1101 and seat tables','result':'PASS'})
print(json.dumps({'result':'PASS','checks':checks,'runtime':metadata,'paid_model_invoked':False,'subscription_or_review_writes':False}))
'''

REMOTE = '''
import json,subprocess
entries=ENTRIES
seat_code=SEAT_CODE
checks=[]
mapping={'stock-api':'stock-api','stock-watch':'stock-watch','api':'investment-research-dashboard-nas-api-1','web':'investment-research-dashboard-nas-web-1'}
for e in entries:
 c=e['candidate'];repo=c['repository'];path='/volume1/docker/'+repo
 def run(args):return subprocess.check_output(args,stderr=subprocess.DEVNULL,timeout=180).decode().strip()
 sha=run(['/usr/local/bin/git','-C',path,'rev-parse','HEAD']);tag=run(['/usr/local/bin/git','-C',path,'describe','--tags','--exact-match','HEAD'])
 assert sha==c['commit_sha'] and tag==e['tag']
 assert not run(['/usr/local/bin/git','-C',path,'status','--porcelain','--untracked-files=no'])
 containers={}
 for component,services in ({'app':['stock-api','stock-watch']} if repo=='stock-analyzer' else {'api':['api'],'web':['web']}).items():
  for service in services:
   d=json.loads(run(['/usr/local/bin/docker','inspect',mapping[service]]))[0]
   assert d['Image']==c['image_ids'][component] and d['State']['Running']
   containers[service]={'container_id':d['Id'],'image_id':d['Image'],'started_at':d['State']['StartedAt']}
 version=run(['/usr/bin/python3','/usr/local/lib/investment-platform/nas_checks.py','version',repo]);assert version==c['version']
 checks.append({'repository':repo,'tag':tag,'commit_sha':sha,'version':version,'images':c['images'],'containers':containers,'result':'PASS'})
seat=json.loads(run(['/usr/local/bin/docker','exec','investment-research-dashboard-nas-api-1','.venv/bin/python','-c',seat_code]))
assert seat['result']=='PASS'
print(json.dumps({'result':'PASS','repositories':checks,'seat_and_auth':seat}))
'''.replace("ENTRIES", repr(PLAN["repositories"])).replace("SEAT_CODE", repr(SEAT_CHECK))

result = subprocess.run([
    'ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
    '-i', '/Users/mukun/.ssh/id_ed25519_synology_stock_analyzer',
    '-p', '9352', 'freemumu@100.86.90.115', '/usr/bin/python3', '-'
], input=REMOTE, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=220)
if result.returncode:
    print('Production acceptance FAILED; inspect exact stage without printing credentials', file=sys.stderr)
    raise SystemExit(1)
receipt = json.loads(result.stdout)
receipt['observed_at'] = datetime.now(timezone.utc).isoformat()
(Path(__file__).parent / 'production-acceptance.receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('Production identity, authenticated seat APIs, live Consumer contracts and migration PASS')
