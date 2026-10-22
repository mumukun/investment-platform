"""Replay with synthetic data in an isolated localhost PostgreSQL database.

Run using the Dashboard development Python. PERF_DATABASE_URL must point to a
throwaway database named *_benchmark; DATABASE_URL must name that same DB.
No production, vendor, message or LLM calls are made.
"""
import ast
import copy
import json
import os
import statistics
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[4]
for entry in (ROOT / 'stock-analyzer', ROOT / 'investment-research-dashboard/backend',
              ROOT / 'investment-research-dashboard/backend/tests', ROOT / 'marketNewsFeed/src'):
    sys.path.insert(0, str(entry))
BASES = {'stock-analyzer': '5646ce7f210ecba99f2b6486eb789a61744ae58b',
         'investment-research-dashboard': '868f871148174a2e84f3d38be48c53d3d7087249'}
DSN = os.environ['PERF_DATABASE_URL']
identity = psycopg.conninfo.conninfo_to_dict(DSN)
assert identity['host'] in {'127.0.0.1', 'localhost'} and identity['dbname'].endswith('_benchmark')
dashboard_identity = psycopg.conninfo.conninfo_to_dict(os.environ['DATABASE_URL'].replace('postgresql+psycopg://', 'postgresql://', 1))
assert all(dashboard_identity.get(key) == identity.get(key) for key in ('host', 'port', 'dbname', 'user')), 'Both database URLs must refer to the same isolated database'

from stock_analyzer import local_db, swing_features as features, swing_store
from stock_analyzer.swing_intraday_cache import BaselineCache
from stock_analyzer import api_projection
from app import market_structure as structure, swing_list
from app.database import SessionLocal
from test_market_structure import fixture_envelope
from threading import Lock
usage_scope = {'time': time, '_usage_totals_lock': Lock(), '_usage_totals_cache': None}
usage_source = (ROOT / 'marketNewsFeed/src/admin_api.py').read_text()
usage_node = next(node for node in ast.parse(usage_source).body if isinstance(node, ast.FunctionDef) and node.name == '_usage_totals')
exec(compile(ast.fix_missing_locations(ast.Module(body=[usage_node], type_ignores=[])), 'admin_api_usage.py', 'exec'), usage_scope)
usage_totals = usage_scope['_usage_totals']

result = {'data': 'synthetic localhost fixtures; timings are stage measurements, not NAS end-to-end results'}
def measure(fn, n=3):
    values = []
    for _ in range(n):
        started = time.perf_counter()
        fn()
        values.append((time.perf_counter() - started) * 1000)
    return round(statistics.median(values), 3)

def old_function(repo, file, name, namespace):
    source = subprocess.check_output(['git', 'show', f'{BASES[repo]}:{file}'], cwd=ROOT / repo, text=True)
    node = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == name)
    scope = dict(namespace)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), file, 'exec'), scope)
    return scope[name]

bars = [{'trade_date': (date(2025, 1, 1)+timedelta(days=i)).isoformat(), 'adjusted_open': 10+i*.01,
         'adjusted_high': 10.2+i*.01, 'adjusted_low': 9.8+i*.01, 'adjusted_close': 10+i*.01,
         'amount': 1e8+i*10000} for i in range(120)]
quote = {'prev_close': 11.19, 'price': 11.4, 'open': 11.2, 'high_today': 11.5, 'low_today': 11.1, 'amount': 2e8}
baseline = bars[-1]['trade_date']
benchmarks = dict(index_pct10=1., index_pct20=2., sector_pct10=3.)
count = 400
cache = BaselineCache(DSN, 'benchmark')
for i in range(count):
    cache.get(str(i), bars, quote, baseline, candidate=True, **benchmarks)
cache.save()
def compute_old():
    for i in range(count):
        features.build_intraday_features(bars, quote, trade_date='2026-10-22', baseline_date=baseline, **benchmarks)
        features.candidate_intraday_reference(bars, quote, baseline_date=baseline, **benchmarks)
def compute_new():
    cache = BaselineCache(DSN, 'benchmark')
    for i in range(count):
        frozen, _ = cache.get(str(i), bars, quote, baseline, candidate=True, **benchmarks)
        features.build_intraday_features(bars, quote, trade_date='2026-10-22', baseline_date=baseline,
                                         baseline_features=frozen, **benchmarks)
    assert cache.hits == count
    cache.save()
result['1_intraday_features'] = {'securities': count, 'old_ms': measure(compute_old), 'cached_ms_including_cache_io': measure(compute_new)}

context = {'conditions': [{'group': 'structure', 'key': str(i), 'detail': 'synthetic evidence' * 15, 'value': i} for i in range(12)],
           'observation_event': {'expiry_date': '2026-10-29'}}
items = [{'code': f'{i:06}', 'name': 'synthetic', 'decision_context': context,
          'path_assessments': [{'strategy_path': path, 'path_role': '主导路径' if j == 0 else '辅助路径',
                                'decision_context': context, 'evidence': [{'detail': 'synthetic evidence', 'status': '满足'}]*12}
                               for j, path in enumerate(('趋势通道', '低位蓄势', '突破回踩'))]}
         for i in range(845)]
payload = {'ok': True, 'trade_date': '2026-10-22', 'rules_version': 'benchmark', 'items': items,
           'summary': {'total_count': len(items)}, 'data_health': {'status': 'healthy'}}
old_source = subprocess.check_output(['git', 'show', BASES['stock-analyzer']+':stock_analyzer/api_projection.py'], cwd=ROOT/'stock-analyzer', text=True)
old_scope = {'__name__': 'baseline_projection'}
exec(compile(old_source, 'baseline_projection.py', 'exec'), old_scope)
old_scope['source_revision'] = lambda *a, **kw: 'unchanged'
build_old, build_new = Mock(return_value=payload), Mock(return_value=payload)
old_pub = old_scope['Publisher'](DSN, 'benchmark-old', {'swing-selection': build_old}, revisions=True)
new_pub = api_projection.Publisher(DSN, 'benchmark-new', {'swing-selection': build_new}, revisions=True)
with local_db.connect(DSN) as conn:
    conn.execute("DELETE FROM api_read_projection WHERE cache_key=ANY(%s)", ([old_pub.key('swing-selection'),new_pub.key('swing-selection')],))
with patch.object(api_projection, 'source_revision', return_value='unchanged'):
    for pub in (old_pub, new_pub):
        pub.publish('swing-selection')
        with local_db.connect(DSN) as conn:
            conn.execute("UPDATE api_read_projection SET built_at=now()-interval '15 minutes' WHERE cache_key=%s", (pub.key('swing-selection'),))
    before = measure(lambda: old_pub.publish('swing-selection'), n=1)
    after = measure(lambda: new_pub.publish('swing-selection'), n=1)
result['2_unchanged_projection'] = {'after_minutes': 15, 'old_ms': before, 'new_ms': after,
                                    'old_builds': build_old.call_count, 'new_builds': build_new.call_count,
                                    'full_rebuild_safety_seconds': api_projection.REBUILD_SECONDS}

with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute('CREATE TEMP TABLE perf_history(id integer, key text, created_at timestamptz, payload jsonb)')
    conn.execute("""INSERT INTO perf_history SELECT i, (date '2026-10-22'-(i%150))::text||':'||i,
        timestamptz '2026-10-22 00:00:00+08'+make_interval(secs=>i),
        jsonb_build_object('trade_date',(date '2026-10-22'-(i%150))::text,'audit',repeat(md5(i::text),2000))
        FROM generate_series(1,1352) i""")
    old_sql = "SELECT DISTINCT ON(payload->>'trade_date') id FROM perf_history ORDER BY payload->>'trade_date' DESC,created_at DESC,id DESC LIMIT 121"
    new_sql = "SELECT DISTINCT ON(split_part(key,':',1)) id FROM perf_history ORDER BY split_part(key,':',1) DESC,created_at DESC,id DESC LIMIT 121"
    assert conn.execute(old_sql).fetchall() == conn.execute(new_sql).fetchall()
    result['3_history_metadata'] = {'generations': 1352, 'old_ms': measure(lambda: conn.execute(old_sql).fetchall()),
                                    'new_ms': measure(lambda: conn.execute(new_sql).fetchall()), 'same_121_ids': True}

summary = swing_list.list_payload(payload)
assert summary['summary'] == payload['summary']
assert swing_list.detail('000001', summary['snapshot_id'])['item'] == items[1]
result['4_swing_response'] = {'items': len(items), 'full_bytes': len(json.dumps(payload).encode()),
                             'summary_bytes': len(json.dumps(summary).encode()), 'complete_detail_equal': True}

raw = fixture_envelope()
day = raw['days'][0]
fund = {'code': '510300', 'exchange': 'SH', 'name': 'synthetic', 'group_id': 'E001',
        'tracking_index_name': 'synthetic index', 'total_shares': 1e8, 'unit_nav': 1.2,
        'share_delta': None, 'flow_est_cny': None, 'share_date': day['trade_date'], 'nav_date': None,
        'reason_codes': ['NAV_DATE_MISMATCH'], 'quality': 'unavailable', 'source_endpoint': 'https://fixture.invalid'}
for n in (1,5,20):
    fund[f'window_{n}d'] = {'value': None, 'covered_subtotal_cny': None, 'missing_days': n,
                          'missing_dates': ['2026-10-01']*n, 'reason_codes': ['FLOW_WINDOW_INCOMPLETE']}
    fund[f'flow_est_{n}d_cny'] = None
    fund[f'aum_start_{n}d_cny'] = 1.2e8
    fund[f'flow_strength_{n}d_pct'] = None
funds = [{**fund, 'code': f'{i:06}'} for i in range(64)]
days = []
for i in range(121):
    value = copy.deepcopy(day)
    value['trade_date'] = (date(2026,10,9)-timedelta(days=120-i)).isoformat()
    value['first_available_at'] = value['trade_date']+'T16:00:00+08:00'
    value['input_hash'] = f'{i:064x}'
    value['funds'] = funds
    days.append(value)
data = {**raw, 'overview': days[-1], 'etf_overview': days[-1], 'days': days}
old_compact = {**data, 'history_detail': 'series', 'days': structure.compact_history(data['days'])}
new_compact = structure.overview(data, compact=True)
assert [d['funds'][0]['flow_est_cny'] for d in old_compact['days']] == [d['funds'][0]['flow_est_cny'] for d in new_compact['days']]
result['5_structure_series'] = {'days': 121, 'funds': 64, 'old_compact_bytes': len(json.dumps(old_compact).encode()),
                                'new_compact_bytes': len(json.dumps(new_compact).encode()), 'null_gaps_equal': True}

# Empty-fund days isolate sync overhead; the body itself is already validated.
sync_days = [{**d, 'funds': []} for d in days]
envelope = structure.Envelope.model_validate({**raw, 'days': sync_days, 'overview': sync_days[-1]})
old_sync = old_function('investment-research-dashboard', 'backend/app/market_structure.py', 'sync_projection', vars(structure))
with SessionLocal() as db:
    structure.sync_projection(db, envelope)
    result['6_unchanged_sync'] = {'days': 121, 'old_ms': measure(lambda: old_sync(db,envelope)),
                                 'new_ms': measure(lambda: structure.sync_projection(db,envelope)),
                                 'old_insert_attempts': 121, 'new_metadata_queries': 1, 'conditional_304_body_bytes': 0}

with psycopg.connect(DSN, autocommit=True, row_factory=dict_row) as conn:
    conn.execute('CREATE TEMP TABLE x_watch_api_usage(id integer PRIMARY KEY, resource_type text, resource_count integer, estimated_cost numeric)')
    conn.execute("INSERT INTO x_watch_api_usage SELECT i,'post',1,.005 FROM generate_series(1,301404) i")
    owner = object()
    aggregate = 'SELECT resource_type, SUM(resource_count) AS resource_count, SUM(estimated_cost) AS estimated_cost FROM x_watch_api_usage GROUP BY resource_type'
    expected = conn.execute(aggregate).fetchall()
    assert usage_totals(conn,owner) == expected
    result['7_x_usage_totals'] = {'rows': 301404, 'old_ms': measure(lambda: conn.execute(aggregate).fetchall()),
                                 'cached_ms': measure(lambda: usage_totals(conn,owner)), 'exact_totals_equal': True}

import gzip
from urllib.request import Request, urlopen
base = os.environ.get('PERF_NGINX_URL')
if base:
    assert base.startswith('http://127.0.0.1:')
    asset = max((ROOT/'investment-research-dashboard/dist/assets').glob('*.js'), key=lambda p:p.stat().st_size)
    with urlopen(Request(base+'/assets/'+asset.name, headers={'Accept-Encoding': 'gzip'})) as response:
        encoded = response.read()
        assert response.headers['Content-Encoding'] == 'gzip'
        assert 'Accept-Encoding' in response.headers['Vary']
        assert gzip.decompress(encoded) == asset.read_bytes()
        assert any('immutable' in value for value in response.headers.get_all('Cache-Control'))
        result['8_static_gzip'] = {'raw_bytes': asset.stat().st_size, 'gzip_bytes': len(encoded), 'decoded_equal': True,
                                   'vary': response.headers['Vary'], 'cache_control': response.headers.get_all('Cache-Control')}
    css = max((ROOT/'investment-research-dashboard/dist/assets').glob('*.css'), key=lambda p:p.stat().st_size)
    with urlopen(Request(base+'/assets/'+css.name, headers={'Accept-Encoding': 'gzip'})) as response:
        encoded = response.read()
        assert response.headers['Content-Encoding'] == 'gzip'
        assert gzip.decompress(encoded) == css.read_bytes()
        result['8_static_gzip']['css'] = {'raw_bytes': css.stat().st_size, 'gzip_bytes': len(encoded), 'decoded_equal': True}
output = Path(__file__).with_name('performance-results.json')
output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
print(output.read_text())
