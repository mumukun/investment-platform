"""Synthetic collector -> generation -> Consumer -> isolated PostgreSQL. No network."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

root = Path(__file__).resolve().parents[4]
provider = root / 'stock-analyzer'
consumer = root / 'investment-research-dashboard'
sys.path[:0] = [str(provider), str(consumer / 'backend')]
# Reuse existing local test runtimes without adding application dependencies.
sys.path.append('/Users/mukun/work/workspace/stock/stock-analyzer/.venv/lib/python3.13/site-packages')
assert '127.0.0.1:55466/investment_dashboard' in os.environ['DATABASE_URL']
from stock_analyzer import market_structure_sync as upstream
from stock_analyzer.market_structure_store import empty_envelope
from app.market_structure import DOMAIN, Envelope, read_projection, sync_projection
from app.database import SessionLocal
from app.models import Snapshot
from sqlalchemy import delete

end = '2026-10-15'
facts, generations = {}, []
def save(_db, kind, rows):
    for row in rows:
        key = row.get('entity_id') or f"{row.get('exchange', '')}:{row.get('code', '')}"
        facts.setdefault(kind, {}).setdefault(key, {})[row['trade_date']] = row
    return len(rows)
def source(name, **params):
    if name == 'tool_trade_date_hist_sina': return [{'trade_date': end}]
    if name == 'fetch_tencent_price': return [{'date': end, 'close': 100, 'source_name': 'synthetic fixture', 'source_endpoint': 'https://fixture.invalid'}]
    if name == 'fetch_microcap_index': raise upstream.SourceFailure(name, 'CONNECTION_ERROR', 2)
    return []
with patch.object(upstream, 'public_call', side_effect=source), patch.object(upstream, 'load_facts', return_value=facts), patch.object(upstream, 'save_facts', side_effect=save), patch.object(upstream, 'capture', return_value={'dates': 0}), patch.object(upstream.time, 'sleep'), patch.object(upstream, 'generations', return_value=[]), patch.object(upstream, 'save_generation', side_effect=lambda db, value: generations.append(value) or True):
    report = upstream.collect('fixture-only', end)
    upstream.compute('fixture-only', end, days=1)
assert len(generations) == 1
raw = empty_envelope(end, 'rebuilt')
raw.update(days=generations, overview=generations[-1], actual_market_trade_date=end, quality=generations[-1]['quality'])
envelope = Envelope.model_validate(raw)
assert envelope.days[0].collection_health.failures[0].code == 'CONNECTION_ERROR'
with SessionLocal() as db:
    db.execute(delete(Snapshot).where(Snapshot.domain == DOMAIN)); db.commit()
    inserted = sync_projection(db, envelope)
    projected = read_projection(db, end, 5, 'rebuilt')
    assert projected['overview']['collection_health']['failure_count'] == 1
    assert projected['overview']['collection_health']['checks']
    assert read_projection(db, end, 5, 'known')['overview'] is None
print(json.dumps({'status': 'PASS', 'evidence_type': 'synthetic isolated PostgreSQL; not production', 'inserted_generations': inserted, 'contract_version': raw['contract_version'], 'rules_version': raw['rules_version'], 'source_failure': projected['overview']['collection_health']['failures'][0], 'collection_status': projected['overview']['collection_health']['status'], 'collection_health': projected['overview']['collection_health'], 'known_mode_rejects_future_availability': True, 'external_requests': 0}, ensure_ascii=False))
