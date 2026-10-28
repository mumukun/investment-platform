"""Post-release GET checks; comprehensive consumer GET archives a business snapshot.

Use production-short-readback.py for a strictly provider-only comprehensive retry.
No manual refresh jobs are triggered here.
"""
import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, 'backend')
from app.auth import SESSION_COOKIE, AuthUser, issue_session
from app.config import get_settings
from app.integrations.stock_analyzer import StockAnalyzerClient

settings = get_settings()
assert not settings.seed_demo_data
cookie = issue_session(settings, AuthUser(open_id='production-smoke', name='Production smoke', role='admin', auth_type='password'))
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
client = StockAnalyzerClient(settings.stock_analyzer_base_url, settings.stock_analyzer_token, settings.stock_analyzer_timeout_seconds)
parser = argparse.ArgumentParser()
parser.add_argument('--only-failed', action='store_true')
parser.add_argument('--include-general-short', action='store_true')
args = parser.parse_args()
now = datetime.now(ZoneInfo('Asia/Shanghai'))
paths = [
    '/api/v1/watchlist',
    '/api/v1/watchlist/strategy-profiles?contract_version=investment-dashboard-watchlist-strategy-v3',
    '/api/v1/short-selection/tail?contract_version=investment-dashboard-short-tail-selection-v2',
    '/api/v1/swing-selection/list?page=1&page_size=2&scope=all&contract_version=investment-dashboard-swing-selection-v4',
    '/api/v1/sector-workbench',
]
if args.only_failed:
    paths = ['/api/v1/sector-workbench']
if args.include_general_short:
    paths.insert(0, '/api/v1/short-selection')
results = []
for path in paths:
    started = time.monotonic()
    row = {'path':path}
    try:
        request = urllib.request.Request('http://127.0.0.1:8000'+path, headers={'Cookie':SESSION_COOKIE+'='+cookie})
        with opener.open(request, timeout=45) as response:
            assert response.status==200
            payload = json.load(response)
        row.update(status='PASS_READ_CONTRACT', seconds=round(time.monotonic()-started,3))
        if isinstance(payload,list):
            row['items']=len(payload)
        else:
            for key in ('trade_date','data_time','generated_at','freshness_status','quality','display_basis'):
                if key in payload: row[key]=payload[key]
            meta=payload.get('meta') or {}
            assert not meta.get('isMock') and not meta.get('is_mock')
            row['meta']={k:meta.get(k) for k in ('trade_date','updated_at','quality','freshness_status','businessDate','latestSnapshotDate') if k in meta}
            current=payload.get('current') or {}
            row['current']={k:current.get(k) for k in ('evaluated_at','last_progress_at','generation_id','quality','coverage') if k in current}
            row['page_items']=len(payload.get('items',[]))
            if 'summaries' in payload: row['summaries']=len(payload['summaries'])
            if 'swing-selection/list?' in path:
                direct=client.fetch_swing_selection(contract_version='investment-dashboard-swing-selection-v4',limit=2).model_dump(mode='json')
                dc=direct.get('current') or {}
                row['provider']={k:direct.get(k) for k in ('trade_date','data_time','generated_at','freshness_status')}
                row['provider']['current']={k:dc.get(k) for k in ('evaluated_at','last_progress_at','generation_id','quality')}
                row['same_generation']=current.get('generation_id')==dc.get('generation_id') if current and dc else None
                assert payload['trade_date']==direct['trade_date']
                assert payload['rules_version']==direct['rules_version']
    except Exception as exc:
        row.update(status='FAIL',kind=type(exc).__name__,seconds=round(time.monotonic()-started,3))
        if hasattr(exc,'code'): row['http_status']=exc.code
    results.append(row)
    print(json.dumps(row,ensure_ascii=False),flush=True)
started=time.monotonic()
try:
    tech=client.fetch_tech_board()
    assert tech.get('is_mock') is False
    row={'path':'provider:/tech-board','status':'PASS_PROVIDER_READ_CONTRACT',
        'seconds':round(time.monotonic()-started,3),'boards':len(tech.get('boards',[])),
        'securities':len(tech.get('securities',[])),'generated_at':tech.get('generated_at'),
        'last_collection_at':tech.get('last_collection_at')}
except Exception as exc:
    row={'path':'provider:/tech-board','status':'FAIL','kind':type(exc).__name__,
        'seconds':round(time.monotonic()-started,3)}
results.append(row)
print(json.dumps(row,ensure_ascii=False),flush=True)
if args.include_general_short:
    started=time.monotonic()
    try:
        short=client.fetch_short_selection()
        row={'path':'provider:/short-selection','status':'PASS_PROVIDER_READ_CONTRACT',
            'seconds':round(time.monotonic()-started,3),
            'trade_date':short.trade_date,'data_time':short.data_time,
            'generated_at':short.generated_at,'degraded':short.degraded,
            'candidates':len(short.candidates),'excluded':len(short.excluded)}
    except Exception as exc:
        row={'path':'provider:/short-selection','status':'FAIL','kind':type(exc).__name__,
            'seconds':round(time.monotonic()-started,3)}
    results.append(row)
    print(json.dumps(row,ensure_ascii=False),flush=True)
print(json.dumps({'read_at':now.isoformat(),'scope':'READ_CONTRACT_ONLY_AFTER_MARKET_CLOSE; not intraday freshness acceptance','ok':all(r['status']!='FAIL' for r in results),'checks':results},ensure_ascii=False))
if any(r['status']=='FAIL' for r in results): sys.exit(1)
