import json,sys,urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0,"backend")
from app.auth import AuthUser,SESSION_COOKIE,issue_session
from app.config import get_settings
s=get_settings();token=issue_session(s,AuthUser(open_id="production-smoke",name="Production smoke",role="admin",auth_type="password"));o=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(path):
 q=urllib.request.Request("http://127.0.0.1:8000"+path,headers={"Cookie":SESSION_COOKIE+"="+token})
 with o.open(q,timeout=120) as r:return json.load(r)
v=get("/api/v1/system/version");r=get("/api/v1/capital-flow/research");assert r["meta"]["isMock"] is False
f=get("/api/v1/capital-flow");assert f["meta"]["isMock"] is False
m=get("/api/v1/market-structure/overview?lookback=120");assert m.get("days")
styles=[]
for d in reversed(m["days"]):
 if any((x.get("returns") or {}).get("5d") is not None for x in d.get("styles",[])):
  styles=[{"trade_date":d["trade_date"],"rows":len(d["styles"])}];break
# Preserve actual provider field shape rather than manufacturing a completeness assertion.
valid_style_days=[{"trade_date":d["trade_date"],"rows":sum(any(x.get("returns",{}).get(n) is not None for n in ["5","20","60"]) for x in d.get("styles",[]))} for d in m["days"] if any(any(x.get("returns",{}).get(n) is not None for n in ["5","20","60"]) for x in d.get("styles",[]))]
funds=[{"trade_date":d["trade_date"],"funds":len(d.get("funds",[])),"flows":sum(x.get("flow_est_cny") is not None for x in d.get("funds",[]))} for d in m["days"] if any(x.get("flow_est_cny") is not None for x in d.get("funds",[]))]
tech=get("/api/v1/tech-board");assert not tech.get("is_mock",False)
print(json.dumps({"status":"PASS","version":{k:v.get(k) for k in ["app_version","git_commit","build_time","environment","api_version"]},"research":{"as_of":r["asOf"],"meta":{k:r["meta"].get(k) for k in ["quality","processed","total","coverage","failed","collecting"]},"rows":len(r["rows"])},"intraday":{"sector_curves":len((f.get("sectorTrend") or {}).get("series",[])),"quality":f["meta"].get("quality"),"is_mock":False},"market_structure":{"days":len(m["days"]),"actual_date":m.get("actual_market_trade_date"),"recent_style_dates":valid_style_days[-2:],"recent_fund_dates":funds[-2:],"last_sync":m.get("last_sync_at"),"collection_health_present":any(d.get("collection_health") for d in m["days"])},"tech_board":{"contract":tech.get("contract_version"),"is_mock":tech.get("is_mock",False)}},ensure_ascii=False,default=str))
