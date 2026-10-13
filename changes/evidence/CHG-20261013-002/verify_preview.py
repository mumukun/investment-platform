"""Read-only localhost integration checks; no external requests or writes."""
import json
import urllib.request
import urllib.error
from pathlib import Path

def get(url, token=False):
    headers = {'Authorization': 'Bearer market-structure-local-test'} if token else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)

provider = 'http://127.0.0.1:18829/api/integrations/investment-dashboard/market-structure'
consumer = 'http://127.0.0.1:18029/api/v1/market-structure/overview'
checks = {}
for label, url, token, expected in [
    ('provider_authenticated', provider+'?lookback=120', True, 200),
    ('provider_no_token', provider, False, 401),
    ('consumer_overview', consumer+'?lookback=120', False, 200),
    ('invalid_window', consumer+'?lookback=7', False, 422),
    ('future_date', consumer+'?as_of=2099-01-01', False, 422),
    ('known_before_first_seen', consumer+'?as_of=2026-10-12&mode=known', False, 200),
]:
    status, value = get(url, token)
    assert status == expected, (label, status, value)
    checks[label] = {'status': status}
    if label == 'known_before_first_seen':
        assert value['days'] == [], value
        checks[label]['days'] = 0
    if label == 'consumer_overview':
        assert len(value['days']) == 121, len(value['days'])
        latest = value['overview']
        assert latest['trade_date'] == '2026-10-13', latest['trade_date']
        assert latest['market']['ma20_eligible_count'] > 4900, latest['market']
        checks[label].update(first=value['days'][0]['trade_date'], last=value['days'][-1]['trade_date'], days=len(value['days']))
        excerpt = {k: v for k, v in value.items() if k != 'days'}
        excerpt['history_summary'] = checks[label]
        Path(__file__).with_name('api-response-excerpt.json').write_text(json.dumps(excerpt, ensure_ascii=False, indent=2))
print(json.dumps(checks, ensure_ascii=False, indent=2))
