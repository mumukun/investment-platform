"""One affected production boundary: tail HTTP contracts and Consumer routes."""
import json
import re
import sys
from datetime import datetime
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, "backend")
from app.api import short_tail_selection, short_tail_stats, short_tail_tracking
from app.config import get_settings
from app.database import SessionLocal
from app.integrations.stock_analyzer import StockAnalyzerClient

s = get_settings()
client = StockAnalyzerClient(s.stock_analyzer_base_url, s.stock_analyzer_token, s.stock_analyzer_timeout_seconds)
opener = build_opener(ProxyHandler({}))
now = datetime.now(ZoneInfo("Asia/Shanghai"))
result = {"checked_at": now.isoformat(), "scope": "new-tail-provider-consumer-boundary"}
try:
    opener.open(s.stock_analyzer_base_url + "/api/integrations/investment-dashboard/short-selection/tail", timeout=10)
    raise AssertionError("missing service authentication")
except HTTPError as error:
    assert error.code == 401
    result["unauthenticated_status"] = error.code
with patch("app.integrations.stock_analyzer.urlopen", opener.open):
    selected = client.fetch_short_tail()
    tracked = client.fetch_short_tail("tracking", limit=50)
    stats = client.fetch_short_tail("stats")
    with SessionLocal() as db:
        projected = short_tail_selection(date_to=None, db=db, client=client)
    rows = short_tail_tracking(date_to=None, model="fixed_tp3", limit=50, offset=0, client=client)
    summary = short_tail_stats(date_to=None, model="fixed_tp3", client=client)
    assert projected["trade_date"] == selected.trade_date <= now.date().isoformat()
    assert rows["total"] == tracked.total == stats.overall.formal_signals
    assert summary["overall"] == stats.overall.model_dump()
    if not stats.overall.settled:
        assert stats.overall.win_rate is None and stats.overall.loss_rate is None
    result["tail"] = {"selection_contract": selected.contract_version, "tracking_contract": tracked.contract_version,
                      "stats_contract": stats.contract_version, "rules_version": selected.rules_version,
                      "trade_date": selected.trade_date, "phase": selected.phase, "quality": selected.quality,
                      "signals": tracked.total, "entries": stats.overall.entries, "settled": stats.overall.settled,
                      "win_rate": stats.overall.win_rate, "issues": selected.issues,
                      "consumer_routes_match": True}
    research = client.fetch_short_tail("stats", model="observed_trail_a2_d1")
    assert research.tracking_version != stats.tracking_version
    result["separate_research_tracking"] = True

# Verify the deployed lazy page bundle includes the new direct per-stock view.
web = "http://127.0.0.1:9360"
with opener.open(web + "/", timeout=10) as response:
    html = response.read().decode()
script = re.search(r'src="(/assets/index-[^\"]+\.js)"', html)
assert script
with opener.open(web + script.group(1), timeout=10) as response:
    main_js = response.read().decode()
chunk = re.search(r'ShortSelectionView-[\w-]+\.js', main_js)
assert chunk
with opener.open(web + "/assets/" + chunk.group(), timeout=10) as response:
    bundle = response.read().decode()
assert "每只股票收益" in bundle and "尾盘隔夜" in bundle
result["deployed_tail_page_bundle"] = chunk.group()
print(json.dumps(result, ensure_ascii=False, indent=2))
