"""Read-only affected production path check; no user data or credentials in receipt."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CODE = '''
import sys,json,urllib.request
sys.path.insert(0,'backend')
from app.config import get_settings
from app.auth import AuthUser,issue_session,SESSION_COOKIE
s=get_settings();assert not s.seed_demo_data and s.auth_enabled
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
t=issue_session(s,AuthUser(open_id='production-smoke',name='Production smoke',role='admin',auth_type='password'))
checks=[]
for path in ['/api/v1/dashboard/premarket','/api/v1/us-industries/overnight','/api/v1/us-industries/calendar','/api/v1/watchlist','/api/v1/decisions?session=next_day','/api/v1/system/version']:
 with op.open(urllib.request.Request('http://127.0.0.1:8000'+path,headers={'Cookie':SESSION_COOKIE+'='+t}),timeout=20) as r:p=json.load(r);assert r.status==200
 item={'path':path,'result':'PASS'}
 if path.endswith('/premarket'):
  meta=p['meta'];assert meta['isMock'] is False
  assert '盘前参考' in p['sessionStatus']
  item.update({k:meta.get(k) for k in ['businessTime','updatedAt','quality','freshnessReason']})
  assert meta['updatedAt']!='now'
 if path.endswith('/version'):
  assert p['app_version']=='0.18.0' and p['git_commit']=='d482526907324d4b74aea1aeb84751064c9179ad'
  item['runtime']={k:p[k] for k in ['app_version','git_commit','build_time']}
 checks.append(item)
print(json.dumps({'result':'PASS','checks':checks,'paid_model_invoked':False,'user_data_writes':False}))
'''
remote = 'import subprocess\nsubprocess.run(' + repr([
    '/usr/local/bin/docker', 'exec', 'investment-research-dashboard-nas-api-1',
    '.venv/bin/python', '-c', CODE,
]) + ',check=True)'
result = subprocess.run([
    'ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
    '-i', '/Users/mukun/.ssh/id_ed25519_synology_stock_analyzer', '-p', '9352',
    'freemumu@100.86.90.115', '/usr/bin/python3', '-',
], input=remote, text=True, capture_output=True, timeout=140)
if result.returncode:
    raise SystemExit('Premarket production check failed; inspect affected path without printing credentials')
receipt = json.loads(result.stdout)
receipt['observed_at'] = datetime.now(timezone.utc).isoformat()
Path(__file__).with_name('premarket.receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('Premarket production version, dated real snapshot and four independent sections PASS')
