"""Focused authenticated read check for the released swing history boundary."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODE = r'''
import json,sys,urllib.request,urllib.parse
sys.path.insert(0,'backend')
from app.config import get_settings
from app.auth import AuthUser,issue_session,SESSION_COOKIE
s=get_settings();assert s.auth_enabled and not s.seed_demo_data
t=issue_session(s,AuthUser(open_id='production-smoke',name='Production smoke',role='admin',auth_type='password'))
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(path):
 with op.open(urllib.request.Request('http://127.0.0.1:8000'+path,headers={'Cookie':SESSION_COOKIE+'='+t}),timeout=45) as r:
  assert r.status==200
  return json.load(r)
stats=get('/api/v1/swing-selection/stats')
assert stats['contract_version']=='investment-dashboard-swing-stats-v2'
runtime=get('/api/v1/system/version')
assert runtime['app_version']=='0.18.1' and runtime['git_commit']=='ceb1b03d15c18973f3d3c6d9574384e680293d74'
version=stats['rules_version']
checks=[]
for pattern,expected in [(None,int(stats['overall']['formal_signals']))]+[(p,int(m['triggers'])) for p,m in stats['by_pattern'].items()]:
 q={'rules_version':version,'limit':2000}
 if pattern:q['pattern']=pattern
 h=get('/api/v1/swing-selection/history?'+urllib.parse.urlencode(q))
 assert h['contract_version']=='investment-dashboard-swing-history-v2' and h['rules_version']==version
 rows=h['samples'];assert len(rows)==min(expected,2000),(pattern,expected,len(rows))
 assert len({r['event_id'] for r in rows})==len(rows)
 assert all(r['participation_decision']=='可计划参与' for r in rows)
 if pattern:assert all(r['pattern']==pattern for r in rows)
 checks.append({'pattern':pattern or '全部','summary_formal_signals':expected,'returned_samples':len(rows),'with_outcome':sum(r['pct_5'] is not None for r in rows),'result':'PASS'})
assert int(stats['overall']['formal_signals'])>0,'No production formal signals to validate'
print(json.dumps({'result':'PASS','rules_version':version,'runtime':{k:runtime[k] for k in ['app_version','git_commit','build_time']},'checks':checks,'paid_model_invoked':False,'user_data_writes':False}))
'''
remote = 'import subprocess\nsubprocess.run(' + repr([
    '/usr/local/bin/docker', 'exec', 'investment-research-dashboard-nas-api-1',
    '.venv/bin/python', '-c', CODE,
]) + ',check=True)'
result = subprocess.run([
    'ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
    '-o', 'StrictHostKeyChecking=yes',
    '-i', '/Users/mukun/.ssh/id_ed25519_synology_stock_analyzer', '-p', '9352',
    'freemumu@100.86.90.115', '/usr/bin/python3', '-',
], input=remote, text=True, capture_output=True, timeout=230)
if result.returncode:
    raise SystemExit('Affected swing history production check FAILED; inspect without printing credentials')
receipt = json.loads(result.stdout)
receipt['observed_at'] = datetime.now(timezone.utc).isoformat()
(ROOT / 'swing-history.receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
