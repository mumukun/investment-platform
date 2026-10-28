import sys, json, time, urllib.request, urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, "backend")
from app.auth import SESSION_COOKIE, AuthUser, issue_session
from app.config import get_settings
from app.integrations.stock_analyzer import StockAnalyzerClient
s = get_settings()
assert not s.seed_demo_data
cookie = issue_session(s, AuthUser(open_id="production-smoke", name="Production smoke", role="admin", auth_type="password"))
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
now = datetime.now(ZoneInfo("Asia/Shanghai"))
checks = []
def get(path):
    req = urllib.request.Request("http://127.0.0.1:8000" + path, headers={"Cookie": SESSION_COOKIE+"="+cookie})
    with opener.open(req, timeout=45) as response:
        assert response.status == 200
        return json.load(response)
def summary(path, data):
    row = {"path": path, "status": "PASS_READ_CONTRACT"}
    if isinstance(data, list):
        row["items"] = len(data)
    else:
        for value, flag in ((data.get("meta"), "isMock"), (data.get("source_status"), "is_mock")):
            if isinstance(value, dict): assert not value.get(flag)
        for key in ("contract_version", "trade_date", "actual_trade_date", "quality", "freshness_status", "data_time", "generated_at", "display_basis", "phase"):
            value = data.get(key)
            if isinstance(value, (str,int,float,bool)) or value is None:
                row[key] = value
        for key in ("trade_date", "actual_trade_date"):
            if data.get(key): assert data[key][:10] <= now.date().isoformat(), "future trade date"
        for key in ("items", "events", "rows", "boards", "series"):
            if isinstance(data.get(key), list): row[key] = len(data[key])
    return row
paths = [
    "/api/v1/watchlist",
    "/api/v1/short-selection/tail?contract_version=investment-dashboard-short-tail-selection-v2",
    "/api/v1/swing-selection/list?page=1&page_size=2&scope=all&contract_version=investment-dashboard-swing-selection-v4",
    "/api/v1/sector-workbench",
]
for path in paths:
    started = time.monotonic()
    try:
        payload = get(path)
        result = summary(path,payload)
        if path == "/api/v1/watchlist":
            client=StockAnalyzerClient(s.stock_analyzer_base_url,s.stock_analyzer_token,s.stock_analyzer_timeout_seconds)
            source=client.fetch_watchlist()
            assert source.ok and source.count == len(source.items)
            result["provider_contract_validated"] = True
            result["provider_items"] = source.count
            result["provider_with_quote"] = sum(item.current_price is not None for item in source.items)
            result["provider_quote_dates"] = sorted({str(item.quote_date) for item in source.items if item.quote_date is not None})
            assert len(payload) == source.count
        if "short-selection/tail?" in path:
            from app.integrations.short_tail import TailSelectionV2
            TailSelectionV2.model_validate(payload)
            observed=payload.get("current") or {}
            result["current"]={key:observed.get(key) for key in ("quality","evaluated_at","trade_date","coverage","issues")}
            result["current"]["items"]=len(observed.get("items",[]))
            client=StockAnalyzerClient(s.stock_analyzer_base_url,s.stock_analyzer_token,s.stock_analyzer_timeout_seconds)
            direct=client.fetch_short_tail(contract_version="investment-dashboard-short-tail-selection-v2").model_dump()
            dc=direct.get("current") or {}
            result["provider_current"]={key:dc.get(key) for key in ("quality","evaluated_at","trade_date","coverage","issues")}
            counts=dc.get("coverage") or {}
            result["diagnostic_counts_present"]=all(key in counts for key in (
                "fresh_quote_count","expected_quote_count","history_checked_count",
                "history_ready_count","history_missing_count","feature_ready_count"))
            if counts.get("history_checked_count")==0:
                assert "基础池历史/复权输入全部不可用" not in dc.get("issues",[])
        if "swing-selection/list?" in path:
            client=StockAnalyzerClient(s.stock_analyzer_base_url,s.stock_analyzer_token,s.stock_analyzer_timeout_seconds)
            source=client.fetch_swing_selection(contract_version="investment-dashboard-swing-selection-v4",limit=2).model_dump()
            assert payload["trade_date"] == source["trade_date"]
            assert payload["rules_version"] == source["rules_version"]
            result["provider_contract_validated"] = True
        result["elapsed_seconds"] = round(time.monotonic()-started,3)
        if path=="/api/v1/sector-workbench":
            result["meta"]=payload.get("meta")
            result["summaries"]=len(payload.get("summaries",[]))
        checks.append(result)
        print(json.dumps(result,ensure_ascii=False),flush=True)
    except Exception as exc:
        result={"path":path,"status":"FAIL","kind":type(exc).__name__}
        if isinstance(exc, urllib.error.HTTPError): result["http_status"] = exc.code
        result["elapsed_seconds"] = round(time.monotonic()-started,3)
        checks.append(result)
        print(json.dumps(result),flush=True)
print(json.dumps({"ok":all(c["status"]!="FAIL" for c in checks),"checks":checks},ensure_ascii=False))
if any(c["status"]=="FAIL" for c in checks):sys.exit(1)
