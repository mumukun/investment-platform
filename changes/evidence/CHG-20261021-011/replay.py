"""Offline replay of public industry amounts; no source API or production writes."""
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'stock-analyzer'))
from stock_analyzer import sector_fund_sina_intraday as source

folder = Path(__file__).resolve().parent
raw = (folder / 'observed-20261021.json').read_bytes()
samples = json.loads(raw)
original = json.dumps(samples, sort_keys=True)
conn = MagicMock()
conn.__enter__.return_value = conn
conn.execute.return_value.fetchall.return_value = [{'payload': p} for p in samples]
with patch.object(source.local_db, 'connect', return_value=conn):
    trend = source.trend('offline-only', datetime.fromisoformat('2026-10-21T15:01:00+08:00'), '2026-10-21')
assert json.dumps(samples, sort_keys=True) == original
assert len(trend['series']) == 12
assert all(len(row['values']) == len(trend['times']) for row in trend['series'])
for row in trend['series']:
    for minute, value in zip(trend['times'], row['values']):
        archived = next((p for p in samples if p['minute'] == minute), None)
        assert value == (round(archived['values'][row['code']], 4) if archived else None)
report = {
    'fixture_sha256': hashlib.sha256(raw).hexdigest(),
    'stored_samples': len(samples), 'timeline_minutes':len(trend['times']),
    'missing_minutes':len(trend['times'])-len(samples),
    'warning_minutes':len(trend['sampleWarnings']),
    'warning_examples':trend['sampleWarnings'][:8],
    'raw_values_unchanged':True, 'network_requests':0,
    'scope':'Public archived industry values, read-only exported earlier; replay uses mocked local storage, no production calls.',
}
(folder / 'replay-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(folder / 'trend-replay.json').write_text(json.dumps(trend,ensure_ascii=False)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
