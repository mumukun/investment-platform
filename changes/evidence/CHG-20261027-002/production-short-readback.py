"""Targeted retry after correcting a field absent from the consumer model."""
import json
import sys
import time
from datetime import datetime
from urllib.parse import urlparse
sys.path.insert(0, 'backend')
from app.config import get_settings
from app.integrations.stock_analyzer import StockAnalyzerClient

settings = get_settings()
assert not settings.seed_demo_data
# Stock provider only (8808); never call the Dashboard API (8000), which archives reads.
assert urlparse(settings.stock_analyzer_base_url).port == 8808
client = StockAnalyzerClient(settings.stock_analyzer_base_url,
                            settings.stock_analyzer_token,
                            settings.stock_analyzer_timeout_seconds)
started = time.monotonic()
short = client.fetch_short_selection()
assert datetime.fromisoformat(short.generated_at) > datetime.fromisoformat('2026-10-28T14:28:52+00:00')
assert short.data_time[:10] == short.trade_date
print(json.dumps({'path':'provider:/short-selection', 'status':'PASS_PROVIDER_READ_CONTRACT',
                  'seconds':round(time.monotonic()-started,3),
                  'trade_date':short.trade_date, 'data_time':short.data_time,
                  'generated_at':short.generated_at, 'degraded':short.degraded,
                  'candidates':len(short.candidates), 'excluded':len(short.excluded)}))
