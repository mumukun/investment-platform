import json, urllib.request, urllib.error
from stock_analyzer.settings import load_settings
from stock_analyzer.version import APP_VERSION
s=load_settings();o=urllib.request.build_opener(urllib.request.ProxyHandler({}));base="http://127.0.0.1:"+str(s.api.port)
def get(path,auth=True):
 req=urllib.request.Request(base+path,headers={"Authorization":"Bearer "+s.api.token} if auth else {})
 with o.open(req,timeout=90) as r:return json.load(r)
path="/api/integrations/investment-dashboard/capital-flow/research"
try:get(path,False);raise AssertionError("missing auth")
except urllib.error.HTTPError as e:assert e.code==401
r=get(path);assert r["contractVersion"]=="investment-dashboard-sector-fund-research-v1" and r["meta"]["isMock"] is False
meta={k:r["meta"].get(k) for k in ["source","quality","collecting","processed","total","failed","coverage","generatedAt"]}
assert len(r["rows"])==meta["total"] and meta["total"]>12
healthy=[x for x in r["rows"] if x.get("quality")=="healthy"]
sample=healthy[0] if healthy else next((x for x in r["rows"] if x.get("dataDate")),None)
detail=None
if sample:
 d=get(path+"?code="+sample["code"]);detail={"code":sample["code"],"data_date":sample.get("dataDate"),"daily_count":len(d.get("detail",{}).get("daily",[])),"ma20":sample.get("ma20"),"windows":sample.get("windows")}
f=get("/api/integrations/investment-dashboard/capital-flow?contract_version=investment-dashboard-capital-flow-v2")
t=f.get("sectorTrend") or {}
print(json.dumps({"status":"PASS","version":APP_VERSION,"authentication":"401 without Bearer; authenticated read PASS","research":{"as_of":r["asOf"],"meta":meta,"sample":detail},"intraday":{"meta":f.get("meta"),"sector_curves":len(t.get("series",[])),"sector_quality":t.get("quality"),"sector_time":t.get("updatedAt")}},ensure_ascii=False))
