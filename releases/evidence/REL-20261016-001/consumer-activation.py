import sys
sys.path.insert(0, '/app/backend')
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from app.version import app_version,build_metadata
assert app_version()=="0.23.0"
assert build_metadata()["git_commit"]=="46b2bec9bea7d1adf6889b2b2d01ae1bd1334684"
from app.config import get_settings
from app.integrations.stock_analyzer import StockAnalyzerClient
from app.market_structure import fetch_envelope,sync_projection,read_projection
from app.market_data_projection import sync_capital_flow_snapshot
from app.database import SessionLocal
from app.postmarket_review import review_availability
s=get_settings();client=StockAnalyzerClient(s.stock_analyzer_base_url,s.stock_analyzer_token,s.stock_analyzer_timeout_seconds)
today=datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
with SessionLocal() as db:
 v=fetch_envelope(client); n=sync_projection(db,v);r=read_projection(db,today,120,'rebuilt');m=(r.get('overview') or {}).get('market',{})
 assert m.get('valid_return_count',0)>0,'Consumer statistics unavailable'
 assert any((d.get('microcap_index') or {}).get('close') is not None for d in r['days']),'Consumer microcap absent'
 flow=sync_capital_flow_snapshot(db,client);meta=flow['meta'];assert meta['contractVersion']=='investment-dashboard-capital-flow-v2' and meta['isMock'] is False
 availability=review_availability(db,allow_mock=False)
 history=[{'date':d['trade_date'],'ma20_eligible_count':d['market'].get('ma20_eligible_count'),'ma60_eligible_count':d['market'].get('ma60_eligible_count')} for d in r['days'] if (d['market'].get('ma20_eligible_count') or 0)>0]
 average=[d['third_party_average_price_index'] for d in r['days'] if (d.get('third_party_average_price_index') or {}).get('close') is not None]
 print(json.dumps({'status':'PASS','runtime':build_metadata(),'market_structure':{'days':len(r['days']),'inserted':n,'actual_trade_date':r['actual_market_trade_date'],'valid_return_count':m['valid_return_count'],'pool_count':m.get('pool_count'),'ma20_eligible_count':m.get('ma20_eligible_count'),'ma60_eligible_count':m.get('ma60_eligible_count'),'universe_verified':m.get('universe_verified'),'phase':(r.get('overview') or {}).get('phase')},'last_ma_history_coverage':history[-1] if history else None,'last_average_price':{'date':average[-1]['trade_date'],'close':average[-1]['close']} if average else None,'capital_flow':{'contract_version':meta['contractVersion'],'trade_date':meta['tradeDate'],'quality':meta['quality'],'is_mock':meta['isMock'],'timeline_points':len(flow['timeline'])},'review_availability':{'has_day_statuses':bool(availability.get('day_statuses')),'keys':sorted(availability.keys())}},ensure_ascii=False))
