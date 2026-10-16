import sys,json,urllib.request
sys.path.insert(0,'backend')
from app.auth import AuthUser,SESSION_COOKIE,issue_session
from app.config import get_settings
s=get_settings();t=issue_session(s,AuthUser(open_id='production-smoke',name='Production smoke',role='admin',auth_type='password'));o=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(path):
 with o.open(urllib.request.Request('http://127.0.0.1:8000'+path,headers={'Cookie':SESSION_COOKIE+'='+t}),timeout=60) as r:return json.load(r)
r=get('/api/v1/capital-flow/research');assert r['meta']['quality']=='healthy' and not r['meta']['collecting'] and r['meta']['processed']==r['meta']['coverage']==r['meta']['total']==len(r['rows'])
m=get('/api/v1/market-structure/overview?lookback=120');d=m['overview'];h=d['collection_health'];assert h['status']=='healthy' and h['failure_count']==h['missing_count']==0
a=d.get('third_party_average_price_index');assert a and a['id']=='eastmoney:47.800005' and a['close']>0
ma=next((x for x in reversed(m['days']) if x['market'].get('ma20_eligible_count',0)>0),None)
print(json.dumps({'status':'PASS','sector_research':{'as_of':r['asOf'],**{k:r['meta'][k] for k in ['quality','collecting','processed','coverage','total','failed']}},'market_structure':{'trade_date':d['trade_date'],'collection_health':{k:h[k] for k in ['status','failure_count','missing_count','checked_at','expected_trade_date','pending_current_close']},'third_party_average_price':{k:a.get(k) for k in ['id','trade_date','close','observation_method','data_time']},'last_eligible_ma':None if not ma else {'trade_date':ma['trade_date'],'ma20':ma['market']['ma20_eligible_count'],'ma60':ma['market']['ma60_eligible_count']}}},ensure_ascii=False,default=str))
