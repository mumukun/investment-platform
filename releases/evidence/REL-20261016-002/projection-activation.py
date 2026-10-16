import sys,json
sys.path.insert(0,'backend')
from app.config import get_settings
from app.integrations.stock_analyzer import StockAnalyzerClient
from app.market_structure import fetch_envelope,sync_projection,read_projection
from app.database import SessionLocal
s=get_settings();client=StockAnalyzerClient(s.stock_analyzer_base_url,s.stock_analyzer_token,s.stock_analyzer_timeout_seconds)
value=fetch_envelope(client)
with SessionLocal() as db:
 inserted=sync_projection(db,value);db.commit();result=read_projection(db,value.requested_date.isoformat(),120,'rebuilt')
latest=result['overview'];health=latest.get('collection_health');assert health is not None
assert health['status']=='healthy' and health['failure_count']==0
print(json.dumps({'status':'PASS','contract':result.get('contract_version'),'trade_date':latest['trade_date'],'inserted':inserted,'collection_health':health,'style_rows_with_returns':sum(any(x.get('returns',{}).get(n) is not None for n in ['5','20','60']) for x in latest['styles']),'indices_with_close':sum(x.get('close') is not None for x in latest['indices']),'average_price':latest.get('average_price_index')},ensure_ascii=False,default=str))
