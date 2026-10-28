import json,os
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from stock_analyzer import local_db
from stock_analyzer.market_data import reader
url=reader.database_url()
now=datetime.now(ZoneInfo("Asia/Shanghai"))
with local_db.readonly_connect(url) as conn:
    quotes=conn.execute("""SELECT market,count(*) AS rows,count(DISTINCT instrument_id) AS instruments,
        count(DISTINCT instrument_id) FILTER (WHERE trade_date=%s) AS today_instruments,
        count(DISTINCT instrument_id) FILTER (WHERE source_time>=%s) AS recently_observed_instruments,
        max(trade_date) AS trade_date,max(source_time) AS source_time,max(received_at) AS received_at
        FROM market_quote_latest GROUP BY market ORDER BY market""",(now.date(),now-timedelta(seconds=180))).fetchall()
    states=conn.execute("""SELECT dataset,scope_key,status,expected_count,ready_count,data_date,
        data_time,checked_at,last_success_at FROM market_data_state
        WHERE scope_key='all' OR (dataset='system' AND scope_key='collector')
        ORDER BY dataset,scope_key""").fetchall()
    indexes=conn.execute("""SELECT i.indisvalid,i.indisready FROM pg_index i
        JOIN pg_class c ON c.oid=i.indexrelid JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE c.relname='idx_security_rule_named_code_date' AND n.nspname=current_schema()""").fetchall()
sessions,directory=reader.references(url)
out={"read_at":now.isoformat(),"runtime_role":os.getenv("STOCK_ANALYZER_RUNTIME_ROLE"),
"quotes":quotes,"states":states,"reference":{"directory_complete":directory.get("complete"),
"directory_rows":len(directory.get("items",[])),"calendar_rows":len(sessions)},"named_rule_index":indexes}
print(json.dumps(out,default=str,ensure_ascii=False))
assert indexes and all(i["indisvalid"] and i["indisready"] for i in indexes)
assert any(r["market"]=="CN" and r["today_instruments"]>0 for r in quotes)
assert directory.get("complete") and sessions
h=next(r for r in states if r["dataset"]=="system")
assert h["status"]=="ready" and (now-h["checked_at"]).total_seconds()<=60
