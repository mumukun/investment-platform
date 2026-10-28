"""Read stored facts only; no source requests, initialization or maintenance."""
import json
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from stock_analyzer import local_db
from stock_analyzer.market_data import reader
now=datetime.now(ZoneInfo("Asia/Shanghai"))
url=reader.database_url()
sessions,directory=reader.references(url)
codes=[r["code"] for r in directory.get("items",[])]
with local_db.readonly_connect(url) as conn:
    conn.execute("SET LOCAL statement_timeout='30s'")
    cn=conn.execute("""SELECT count(DISTINCT code) instruments,
      count(DISTINCT code) FILTER(WHERE trade_date=%s) today,
      count(DISTINCT code) FILTER(WHERE source_time>=%s AND source_time<=%s) fresh,
      min(source_time) oldest,max(source_time) newest,max(received_at) received
      FROM market_quote_latest WHERE market='CN' AND asset_kind='stock' AND price_basis='none' AND code=ANY(%s)""",
      (now.date(),now-timedelta(seconds=180),now,codes)).fetchone()
    states=conn.execute("""SELECT dataset,scope_key,status,expected_count,ready_count,data_date,data_time,checked_at,issue
      FROM market_data_state WHERE (dataset='system' AND scope_key IN('collector','publication'))
      OR (dataset IN('cn-quotes','cn-quote-samples') AND scope_key IN('all','published'))
      ORDER BY dataset,scope_key""").fetchall()
    activity=conn.execute("""SELECT state,wait_event_type,wait_event,round(extract(epoch FROM (clock_timestamp()-query_start))) age_seconds,
      left(query,140) query FROM pg_stat_activity WHERE datname=current_database()
      AND state<>'idle' AND pid<>pg_backend_pid() ORDER BY query_start LIMIT 8""").fetchall()
heartbeat=next((r for r in states if r['dataset']=='system' and r['scope_key']=='collector'),None)
publication=next((r for r in states if r['dataset']=='system' and r['scope_key']=='publication'),None)
metrics=json.loads(publication['issue']) if publication and publication['issue'] and publication['issue'].startswith('{') else None
active=now.date().isoformat() in sessions and (('09:30'<=now.strftime('%H:%M')<='11:30') or ('13:00'<=now.strftime('%H:%M')<='15:00'))
out={'read_at':now.isoformat(),'session':'active' if active else 'outside_active_session','directory':len(codes),
 'quotes':cn,'fresh_coverage':round(cn['fresh']/len(codes),4) if codes else None,
 'heartbeat_age_seconds':round((now-heartbeat['checked_at']).total_seconds(),2) if heartbeat else None,
 'publication':metrics,'states':states,'active_queries':activity}
out['acceptance']={'heartbeat':bool(heartbeat and (now-heartbeat['checked_at']).total_seconds()<=60),
 'fresh_coverage':cn['fresh']>=len(codes)*.8 if active and codes else 'NOT_ACTIVE_SESSION',
 'bounded_queue_age':metrics['oldest_pending_seconds']<=60 if metrics else 'METRICS_UNAVAILABLE'}
print(json.dumps(out,ensure_ascii=False,default=str),flush=True)
