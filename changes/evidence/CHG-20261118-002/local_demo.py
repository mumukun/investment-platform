"""Local synthetic replay using the real provider selector and consumer validator."""
import json
import math
import sys
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / 'stock-analyzer'), str(ROOT / 'investment-research-dashboard/backend')]
from stock_analyzer import sector_fund_sina_intraday as provider
from stock_analyzer.capital_flow import BEIJING
from app.integrations.stock_analyzer import StockAnalyzerClient

DATE = '2026-11-18'
NOW = datetime.fromisoformat(DATE + 'T15:00:00+08:00')
CATALOG = list(provider.sina.INDUSTRIES.values())
rows = []
for minute in range(330):
    stamp = NOW.replace(hour=9, minute=31) + timedelta(minutes=minute)
    if not provider.trading_minute(stamp) or stamp > NOW:
        continue
    values = {row['code']: round((index - 23.5) * 1.9 * (0.3 + minute / 470)
              + math.sin(minute / 18 + index) * 1.3, 4)
              for index, row in enumerate(CATALOG)}
    rows.append({'payload': {'minute': stamp.strftime('%H:%M'),
                            'sourceTime': stamp.isoformat(), 'values': values}})


def flow(codes=None):
    with patch('stock_analyzer.market_data.reader.industry_flow_samples', return_value=rows):
        trend = provider.trend('synthetic-read-only', NOW, DATE, codes)
    return {
        'summary': {'netInflow': 12.4, 'speed': 0.8, 'duration': 30, 'state': '本地合成演示'},
        'levels': [], 'timeline': [{'time': '15:00', 'market': 12.4, 'star': None, 'chinext': None}],
        'sectorTrend': trend, 'sectorEvents': [], 'availableDates': [DATE],
        'meta': {'contractVersion': provider.CONTRACT, 'isMock': False,
                 'marketFlowAvailable': True, 'tradeDate': DATE,
                 'updatedAt': NOW.isoformat(), 'businessTime': NOW.isoformat(),
                 'marketStatus': '已收盘', 'quality': 'healthy', 'source': '本地合成演示 · 非真实行情',
                 'calculation': '行业全部单净流入（亿）；仅用于界面验收',
                 'delayLabel': '本地合成数据，不连接生产或外部行情'},
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path
        status = 200
        if path.endswith('/capital-flow'):
            raw = parse_qs(url.query).get('sector_codes', [None])[0]
            body = flow(raw.split(',') if raw else None)
            if path.startswith('/api/v1/'):
                body['meta']['isMock'] = True
                body['sectorTrend']['source'] = '本地合成演示 · 非真实行情'
        elif path.endswith('/capital-flow/research'):
            window = {'netFlowYi': None, 'returnPct': None, 'strengthPct': None,
                      'inflowDays': 0, 'state': '数据不足'}
            body = {'asOf': DATE, 'rows': [{**row, 'dataDate': DATE, 'windows': {
                str(days): window for days in (3, 5, 10)}} for row in CATALOG],
                'meta': {'total': 48, 'processed': 48, 'coverage': 0, 'failed': 48,
                         'collecting': False, 'source': '合成目录 · 仅演示盘中比较',
                         'quality': 'partial', 'generatedAt': NOW.isoformat()}}
        elif path.endswith('/auth/me'):
            body = {'enabled': False, 'authenticated': True, 'role': 'viewer',
                    'user': {'open_id': 'local-demo', 'name': '本地合成演示', 'role': 'viewer'}}
        elif path.endswith('/auth/config'):
            body = {'enabled': False, 'provider': None, 'password_enabled': False, 'captcha_enabled': False}
        elif path.endswith('/system/version'):
            body = {'version': '本地 Top12 演示', 'environment': 'development'}
        else:
            status, body = 404, {'detail': '本地演示仅提供资金流向数据'}
        output = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(output)))
        self.end_headers()
        self.wfile.write(output)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8124), Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    client = StockAnalyzerClient('http://127.0.0.1:8124', 'local-fixture')
    default = client.fetch_capital_flow(sina_only=True)
    assert len(default.sectorTrend['series']) == 24
    codes = [row['code'] for row in CATALOG[12:36]]
    selected = client.fetch_capital_flow(','.join(codes), sina_only=True)
    assert [row['code'] for row in selected.sectorTrend['series']] == codes
    print('PASS: actual provider selection -> local HTTP -> actual consumer validation; default 24, explicit 24, universe 48', flush=True)
    print('Synthetic API listening on http://127.0.0.1:8124', flush=True)
    try:
        from threading import Event
        Event().wait()
    except KeyboardInterrupt:
        server.shutdown()
