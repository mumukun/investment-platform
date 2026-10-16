import json,os
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from stock_analyzer.settings import load_settings
from stock_analyzer import local_db
from stock_analyzer.market_breadth import capture
from stock_analyzer.market_structure_store import load_facts,envelope
from stock_analyzer.market_structure_sync import compute,public_call
assert os.environ.get('MARKET_STRUCTURE_HISTORY_BACKFILL_ENABLED')=='true'
now=datetime.now(ZoneInfo('Asia/Shanghai'));end=now.date().isoformat();start=(now.date()-timedelta(days=500)).isoformat();url=load_settings().hotmap.database_url
with local_db.connect(url) as c:
 assert c.execute("SELECT pg_try_advisory_lock(hashtext('market-structure-sync')) AS locked").fetchone()['locked']
 facts=load_facts(url,start,end,include_stock=False);calendar=sorted(facts['calendar']['calendar'])
 report=capture(url,start,end,calendar,fetch=public_call,max_codes=10)
 report['compute']=compute(url,end,days=121,phase='intraday' if now.hour<16 else 'eod')
 v=envelope(url,end);m=v['overview']['market']
 report['latest']={k:m.get(k) for k in ('valid_return_count','pool_count','ma20_eligible_count','ma60_eligible_count','universe_verified')}
 print(json.dumps(report,ensure_ascii=False))
