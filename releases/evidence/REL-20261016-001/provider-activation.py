import json
import requests
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from stock_analyzer.settings import load_settings
from stock_analyzer import local_db
from stock_analyzer.market_breadth import capture
from stock_analyzer.market_structure_sources import fetch_microcap_index,_fetch_average_price_daily
from stock_analyzer.market_structure_store import load_facts,save_facts,envelope
from stock_analyzer.market_structure_sync import compute
from stock_analyzer.version import APP_VERSION
assert APP_VERSION == '4.0.0'
now=datetime.now(ZoneInfo('Asia/Shanghai')); end=now.date().isoformat();start=(now.date()-timedelta(days=500)).isoformat()
url=load_settings().hotmap.database_url
with local_db.connect(url) as conn:
 assert conn.execute("SELECT pg_try_advisory_lock(hashtext('market-structure-sync')) AS locked").fetchone()['locked'], 'Market structure collector busy; no concurrent writes'
 facts=load_facts(url,start,end,include_stock=False)
 calendar=sorted(facts.get('calendar',{}).get('calendar',{}))
 assert calendar, 'Persisted calendar missing'
 report=capture(url,start,end,calendar)
 bars=fetch_microcap_index((now.date()-timedelta(days=30)).isoformat(),end)
 report['microcap_bars_saved']=save_facts(url,'microcap_index',bars)
 # A single operator recovery of actual past-day bars; no current intraday bar is accepted.
 try:
  previous=(now.date()-timedelta(days=1)).isoformat()
  average=_fetch_average_price_daily((now.date()-timedelta(days=30)).isoformat(),previous)
  report['average_history_bars_saved']=save_facts(url,'average_price_index',average)
 except (requests.RequestException, ValueError) as e:
  report['average_history_recovery']={'status':'UNAVAILABLE_OLD_CACHE_RETAINED','error_type':type(e).__name__}
 report['compute']=compute(url,end,days=121,phase='intraday' if now.hour<16 else 'eod')
 value=envelope(url,end)
 latest=value.get('overview') or {}; m=latest.get('market',{})
 assert m.get('valid_return_count',0)>0,'No valid persisted stock statistics'
 assert any((d.get('microcap_index') or {}).get('close') is not None for d in value['days']), 'Microcap facts absent'
 report['result']={'application_version':APP_VERSION,'rules_version':value['rules_version'],'actual_trade_date':value['actual_market_trade_date'],'phase':latest.get('phase'),'valid_return_count':m.get('valid_return_count'),'pool_count':m.get('pool_count'),'ma20_eligible_count':m.get('ma20_eligible_count'),'ma60_eligible_count':m.get('ma60_eligible_count'),'universe_verified':m.get('universe_verified'),'quality':value['quality']['status'],'days':len(value['days'])}
 from stock_analyzer.add_stock import search_stocks
 matches=search_stocks('600519')
 assert any(r.get('code')=='600519' for r in matches), 'Stock search source smoke failed'
 report['search_smoke']={'query':'600519','match':True,'results':len(matches)}
 print(json.dumps(report,ensure_ascii=False))
