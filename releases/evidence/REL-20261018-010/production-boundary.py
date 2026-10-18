"""Run inside the deployed Dashboard API; only caches are synchronized, no paid APIs."""
import json
import time
from app.api import get_stock_analyzer_client
from app.version import build_metadata
from app.database import SessionLocal
from app.integrations.stock_analyzer import StockAnalyzerError
from app import sector_fund_research, sector_fund_members, tech_board

runtime = build_metadata()
assert runtime["app_version"] == "0.28.0"
assert runtime["git_commit"] == "122a79d6e970a302236600aa60d01c7aadbeb7bc"
client = get_stock_analyzer_client()
report = {"environment": "Production", "scope": "changed Sina/technology boundaries"}
header = None
for attempt in range(18):
    try:
        with SessionLocal() as db:
            header = sector_fund_research.project(db, client, source="sina")
        if len(header["rows"]) == 48 and header["meta"]["coverage"]:
            break
    except StockAnalyzerError:
        pass
    time.sleep(5)
if not header or len(header["rows"]) != 48 or not header["meta"]["coverage"]:
    raise SystemExit("Sina industry scan unavailable; preserve production receipt")
assert header["contractVersion"] == "investment-dashboard-sina-sector-fund-v1"
day = header["asOf"]
report["industries"] = {"asOf": day, "total": len(header["rows"]), "coverage": header["meta"]["coverage"], "quality": header["meta"]["quality"]}
client.fetch_sector_fund_members("new_zzhy", day, refresh=True)
member = None
for attempt in range(24):
    try:
        with SessionLocal() as db:
            member = sector_fund_members.project(db, client, "new_zzhy", day)
        if member.get("snapshot") and member["snapshot"]["asOf"] == day:
            break
    except StockAnalyzerError:
        pass
    time.sleep(5)
if not member or not member.get("snapshot"):
    raise SystemExit("Sina industry members unavailable; preserve production receipt")
s = member["snapshot"]
assert s["code"] == "new_zzhy" and s["asOf"] == day and s["total"] == len(s["items"])
assert any(i["code"] == "002511" and i["windows"]["5"]["netFlowYi"] is not None for i in s["items"])
report["paperMembers"] = {"asOf": s["asOf"], "total": s["total"], "sourceTotal": s["sourceTotal"], "excluded": len(s["excluded"]), "quality": member["quality"], "contract": member["contractVersion"]}
with SessionLocal() as db:
    detail = sector_fund_research.project(db, client, "new_zzhy", day, source="sina")
assert detail["detail"]["code"] == s["code"]
assert detail["detail"]["daily"][-1]["date"] == day
with SessionLocal() as db:
    tech_board.sync(db, client)
    tech, state = tech_board.load(db)
assert len(tech["boards"]) == 15
assert tech["mapping_version"].endswith("v2")
report["technology"] = {"boards": len(tech["boards"]), "mapping": tech["mapping_version"], "quotes": sum(b.get("quote") is not None for b in tech["boards"]), "memberLists": sum(b.get("members") is not None for b in tech["boards"]), "issues": len(tech.get("issues", []))}
report["dashboardRuntime"] = build_metadata()
report["result"] = "PASS"
print(json.dumps(report, ensure_ascii=False, indent=2))
