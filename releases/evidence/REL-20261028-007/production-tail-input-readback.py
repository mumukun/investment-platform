import json
from datetime import datetime
from zoneinfo import ZoneInfo
from stock_analyzer import local_db,current_candidates
from stock_analyzer import short_tail_engine as e
from stock_analyzer.market_data import reader
now=datetime.now(ZoneInfo('Asia/Shanghai'))
with local_db.readonly_connect(reader.database_url()) as c:
 c.execute("SET LOCAL statement_timeout='20s'")
 row=c.execute("SELECT built_at,payload FROM api_read_projection WHERE cache_key=%s",('current:tail:'+now.date().isoformat(),)).fetchone()
p=current_candidates.decode(row['payload']);at=datetime.fromisoformat(p['evaluated_at']);q=list(p.get('input_quotes',{}).values())
print(json.dumps({'read_at':now.isoformat(),'built_at':row['built_at'],'evaluated_at':at,'evaluation_age_seconds':(now-at).total_seconds(),'publication_seconds':(row['built_at']-at).total_seconds(),'coverage':p['coverage'],'input_quotes':len(q),'source_names':sorted({str(v.get('source')) for v in q}),'latest_source':max((v.get('quote_time') or '' for v in q),default=None),'valid_at_evaluation':sum(e.quote_valid(v,at) for v in q),'valid_now':sum(e.quote_valid(v,now) for v in q),'positive_amount':sum(e.positive(v.get('amount')) for v in q),'future_received':sum(bool(e.stamp(v.get('received_at')) and e.stamp(v['received_at'])>at) for v in q)},default=str))
