"""Isolated synthetic benchmark; refuses any database except this task's local test DB."""
import json
import os
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from sqlalchemy import create_engine, desc, select
from sqlalchemy.orm import Session

workspace = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(workspace / "stock-analyzer"), str(workspace / "investment-research-dashboard/backend")]
dsn = os.environ["LATENCY_BENCHMARK_DSN"]
identity = psycopg.conninfo.conninfo_to_dict(dsn)
assert identity["host"] == "127.0.0.1" and identity["port"] == "55489" and identity["dbname"] == "latency_test"

from stock_analyzer import local_db
from stock_analyzer.api_projection import Publisher
from app import api
from app.market_structure import CONTRACT, DOMAIN, overview, read_projection
from app.models import Base, ResearchItem, Snapshot


def timed(function, count=5):
    values = []
    result = None
    for _ in range(count):
        start = time.perf_counter()
        result = function()
        values.append(round((time.perf_counter() - start) * 1000, 3))
    return result, {"samples_ms": values, "median_ms": statistics.median(values),
                    "p95_ms": sorted(values)[max(0, int(len(values) * .95 + .999) - 1)]}


stock_schema = "latency_bench_" + uuid4().hex[:12]
dash_schema = "latency_bench_" + uuid4().hex[:12]
os.environ["STOCK_ANALYZER_DB_SCHEMA"] = stock_schema
report = {"evidence_type": "local synthetic PostgreSQL 16; not production latency",
          "observed_at": datetime.now(timezone.utc).isoformat()}
engine = None
try:
    with local_db.connect(dsn) as conn:
        conn.execute("""INSERT INTO swing_daily_bar(trade_date,code,close)
          SELECT (date '2026-01-01'+d)::text,lpad(c::text,6,'0'),10
          FROM generate_series(0,189) d CROSS JOIN generate_series(1,5000) c""")
        conn.execute("""INSERT INTO a_share_snapshot(trade_date,update_time,code,name,close,change_pct)
          SELECT (date '2026-01-01'+d)::text,'2026-01-01T15:00:00+08:00',lpad(c::text,6,'0'),'Fixture',10,0
          FROM generate_series(0,89) d CROSS JOIN generate_series(1,5000) c""")
        conn.execute("ANALYZE swing_daily_bar")
        conn.execute("ANALYZE a_share_snapshot")
    with local_db.connect(dsn) as conn:
        old = "SELECT trade_date,COUNT(DISTINCT code) n FROM swing_daily_bar GROUP BY trade_date ORDER BY trade_date DESC LIMIT 120"
        new = old.replace("COUNT(DISTINCT code)", "COUNT(*)")
        old_rows = conn.execute(old).fetchall()
        assert conn.execute(new).fetchall() == old_rows
        _, old_time = timed(lambda: conn.execute(old).fetchall())
        _, new_time = timed(lambda: conn.execute(new).fetchall())
        report["sector_coverage_950000_rows"] = {"before": old_time, "after": new_time, "results_equal": True}
        old = """SELECT trade_date FROM (SELECT trade_date FROM limit_up_snapshot_run WHERE trade_date<=%s
          UNION SELECT trade_date FROM a_share_snapshot WHERE trade_date<=%s) days
          ORDER BY trade_date DESC LIMIT %s"""
        new = """SELECT trade_date FROM ((SELECT DISTINCT trade_date FROM limit_up_snapshot_run
          WHERE trade_date<=%s ORDER BY trade_date DESC LIMIT %s) UNION
          (SELECT DISTINCT trade_date FROM a_share_snapshot WHERE trade_date<=%s
          ORDER BY trade_date DESC LIMIT %s)) days ORDER BY trade_date DESC LIMIT %s"""
        old_args, new_args = ("2026-10-21", "2026-10-21", 5), ("2026-10-21", 5, "2026-10-21", 5, 5)
        expected = conn.execute(old, old_args).fetchall()
        assert conn.execute(new, new_args).fetchall() == expected
        _, old_time = timed(lambda: conn.execute(old, old_args).fetchall())
        _, new_time = timed(lambda: conn.execute(new, new_args).fetchall())
        report["limit_dates_450000_rows"] = {"before": old_time, "after": new_time, "results_equal": True}

    builds = []
    large = {"ok": True, "items": [{"code": str(n).zfill(6), "evidence": "fixture only " * 350} for n in range(862)]}
    def build():
        builds.append(1)
        return large
    pub = Publisher(dsn, "benchmark", {"benchmark": build})
    pub.publish("benchmark")
    result, read_time = timed(lambda: pub.read("benchmark"), count=20)
    assert result == large and len(builds) == 1
    report["published_read_862_items"] = {**read_time, "bytes": len(json.dumps(large)), "build_count": len(builds)}

    with psycopg.connect(dsn) as conn:
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(dash_schema)))
    engine = create_engine(dsn.replace("postgresql://", "postgresql+psycopg://"),
                           connect_args={"options": "-c search_path=" + dash_schema})
    Base.metadata.create_all(engine)
    first = datetime(2026, 1, 1, 15, tzinfo=timezone(timedelta(hours=8)))
    with Session(engine) as db:
        for n in range(121):
            day = first + timedelta(days=n)
            payload = {"trade_date": day.date().isoformat(), "first_available_at": day.isoformat(),
                       "rules_version": "fixture", "quality": {"status": "healthy", "reason_codes": [], "sources": []},
                       "market": {"rising_count": 2000}, "methodology": {},
                       "funds": [{"share_date": day.date().isoformat(), "flow_est_cny": None,
                                  "source_records": [{"raw_value": "fixture " * 350}]} for _ in range(15)]}
            db.add(Snapshot(domain=DOMAIN, key=day.date().isoformat()+":"+str(n), session="eod",
                            source="fixture", business_time=day, quality="healthy", version=CONTRACT,
                            is_mock=False, payload=payload))
        for n in range(500):
            db.add(ResearchItem(title=f"Fixture {n}", information_type="第三方观点", source_name="Fixture",
                               published_at=first + timedelta(minutes=n), summary="Summary", related_objects=[],
                               source_payload={"title_original": "Original", "content_original": "body " * 2400},
                               analysis={"level": 4, "direction": "利多", "insight": "insight " * 200},
                               source_version="fixture", is_mock=False))
        db.commit()

    requested = (first + timedelta(days=120)).date().isoformat()
    def old_history():
        with Session(engine) as db:
            day = Snapshot.payload["trade_date"].astext
            return [s.payload for s in reversed(db.scalars(select(Snapshot).where(
                Snapshot.domain == DOMAIN, Snapshot.version == CONTRACT, Snapshot.is_mock.is_(False),
            ).distinct(day).order_by(day.desc(), Snapshot.created_at.desc()).limit(121)).all())]
    def new_history():
        with Session(engine) as db:
            return read_projection(db, requested, 120, "rebuilt")
    expected = old_history()
    full = new_history()
    assert full["days"] == expected
    _, old_time = timed(old_history)
    full, new_time = timed(new_history)
    compact = overview(data=full, compact=True)
    assert [d["trade_date"] for d in compact["days"]] == [d["trade_date"] for d in full["days"]]
    report["structure_121_days"] = {"before": old_time, "warm_after": new_time,
                                    "full_bytes": len(json.dumps(full)), "compact_bytes": len(json.dumps(compact)),
                                    "all_dates_and_values_preserved": True}
    def research(summary):
        with Session(engine) as db:
            return api.research(min_level=2, limit=500, offset=0, summary=summary, db=db)
    full, old_time = timed(lambda: research(False))
    small, new_time = timed(lambda: research(True))
    assert [r["id"] for r in full] == [r["id"] for r in small]
    report["research_500_items"] = {"before": old_time, "after": new_time,
                                   "full_bytes": len(json.dumps(full, default=str)),
                                   "summary_bytes": len(json.dumps(small, default=str)), "all_ids_preserved": True}
finally:
    if engine:
        engine.dispose()
    with psycopg.connect(dsn) as conn:
        for schema in (stock_schema, dash_schema):
            conn.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))

output = Path(__file__).with_name("benchmark-local.json")
output.write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
