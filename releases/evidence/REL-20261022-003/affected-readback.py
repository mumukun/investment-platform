"""Inside the released Dashboard API: real read-only Provider/Consumer boundary."""
import gzip
import json
import re
import sys
import time
from datetime import datetime
from urllib.request import ProxyHandler, Request, build_opener
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, 'backend')
from app.config import get_settings
from app.integrations.stock_analyzer import StockAnalyzerClient
from app import market_structure, swing_list

settings = get_settings()
opener = build_opener(ProxyHandler({}))
client = StockAnalyzerClient(settings.stock_analyzer_base_url, settings.stock_analyzer_token, settings.stock_analyzer_timeout_seconds)
result = {'time': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()}
with patch('app.integrations.stock_analyzer.urlopen', opener.open):
    selection = client.fetch_swing_selection()
    payload = selection.model_dump(mode='json')
    summary = swing_list.list_payload(payload)
    assert summary['summary'] == payload['summary'] and len(summary['items']) == len(payload['items'])
    if payload['items']:
        original = payload['items'][0]
        full = swing_list.detail(original['code'], summary['snapshot_id'])
        assert full['item'] == original
    result['swing'] = {'contract': selection.contract_version, 'rules_version': selection.rules_version,
                       'items': len(selection.items), 'freshness': selection.freshness_status,
                       'input_status': selection.data_health.get('status'), 'complete_detail_equal': True,
                       'full_json_bytes': len(json.dumps(payload).encode()),
                       'summary_json_bytes': len(json.dumps(summary).encode())}
    today = datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    basics = {}
    for code in ('300188', '301291'):
        attempts = 0
        while True:
            value = client.fetch_stock_candles(code, end_date=today, days=60)
            attempts += 1
            if not value.basic.get('refresh_pending') or attempts >= 16:
                break
            time.sleep(2)
        keys = ('quote_date', 'source', 'total_market_cap_yi', 'circulating_market_cap_yi',
                'pe_ttm', 'pb', 'amplitude_pct', 'volume_ratio', 'refresh_pending')
        basics[code] = {'actual_date': value.trade_date, 'bar_count': len(value.bars), 'attempts': attempts,
                        'basic': {key: value.basic.get(key) for key in keys}}
        assert value.bars and value.trade_date <= today
    result['basics'] = basics
with patch('app.market_structure.urlopen', opener.open):
    headers = {}
    history = market_structure.fetch_envelope(client, response_headers=headers)
    assert history is not None and history.days
    if headers.get('etag'):
        assert market_structure.fetch_envelope(client, etag=headers['etag']) is None
    compact = market_structure.overview(history.model_dump(mode='json'), compact=True)
    assert len(compact['days']) == len(history.days)
    result['market_structure'] = {'days': len(history.days), 'etag_304': bool(headers.get('etag')),
                                  'quality': history.quality.status}
base = 'http://127.0.0.1:9360'
with opener.open(base + '/', timeout=10) as response:
    html = response.read().decode()
assets = re.findall(r'(?:src|href)="(/assets/[^\"]+\.(?:js|css))"', html)
assert assets
result['static_assets'] = []
for asset in assets[:2]:
    with opener.open(base + asset, timeout=10) as response:
        original = response.read()
    with opener.open(Request(base + asset, headers={'Accept-Encoding': 'gzip'}), timeout=10) as response:
        body = response.read()
        assert response.headers.get('Content-Encoding') == 'gzip'
        assert gzip.decompress(body) == original
        assert 'Accept-Encoding' in response.headers.get('Vary', '')
        result['static_assets'].append({'path': asset, 'bytes': len(original), 'gzip_bytes': len(body), 'decoded_equal': True})
print(json.dumps(result, indent=2, ensure_ascii=False))
