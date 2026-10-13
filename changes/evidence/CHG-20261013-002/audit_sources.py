import json
from pathlib import Path
from stock_analyzer import local_db
from stock_analyzer.settings import load_settings
from stock_analyzer.market_structure import flow
url=load_settings().hotmap.database_url
with local_db.connect(url) as c:
 rows=c.execute("""SELECT kind,count(*) AS versions,count(distinct entity_id) AS entities,min(trade_date) AS first,max(trade_date) AS last FROM market_structure_fact GROUP BY kind ORDER BY kind""").fetchall()
 samples={}
 for identity in ('sh:510300','sz:159919'):
  data=c.execute("""SELECT DISTINCT ON(kind,trade_date) kind,trade_date,payload FROM market_structure_fact WHERE entity_id=%s AND kind IN ('share','nav') AND trade_date IN ('2026-10-09','2026-10-12') ORDER BY kind,trade_date,first_seen_at""",(identity,)).fetchall()
  shares={str(r['trade_date']):r['payload'] for r in data if r['kind']=='share'}
  nav=next(r['payload'] for r in data if r['kind']=='nav' and str(r['trade_date'])=='2026-10-12')
  calc=flow(shares['2026-10-12'],shares['2026-10-09'],nav,day='2026-10-12',previous_day='2026-10-09')
  assert calc['flow_est_cny']==(shares['2026-10-12']['total_shares']-shares['2026-10-09']['total_shares'])*nav['unit_nav']
  samples[identity]={'today_shares':shares['2026-10-12'],'previous_shares':shares['2026-10-09'],'unit_nav':nav,'computed':calc}
 checks=c.execute("SELECT payload FROM market_structure_fact WHERE kind='adjustment_check' ORDER BY first_seen_at DESC LIMIT 2").fetchall()
 report={'verified_at':'2026-10-13','final_coverage_counts':rows,'math_samples':samples,'adjustment_registry':[{'year':r['payload'].get('entity_id'),'events':len(r['payload'].get('events',[])),'complete':r['payload'].get('complete')} for r in checks],'limitations':['Historical SH/SZ membership not verified; never reuse current directory as historical membership','A500 free index adapter failed; no substitute benchmark','Annual split registry is a public cross-check, source publication time is unavailable','Free-source historical first_seen_at is collection time, not historical publication time']}
print(json.dumps(report,ensure_ascii=False,default=str,indent=2))
