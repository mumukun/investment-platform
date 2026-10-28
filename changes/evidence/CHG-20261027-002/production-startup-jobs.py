"""Read normal post-deployment job results without triggering business writes."""
import argparse
import json
from datetime import datetime, timezone

from stock_analyzer import local_db
from stock_analyzer.settings import load_settings

settings = load_settings()
parser = argparse.ArgumentParser()
parser.add_argument('--since', default='2026-10-28T14:03:58+00:00')
args = parser.parse_args()
with local_db.readonly_connect(settings.hotmap.database_url) as conn:
    conn.execute("SET LOCAL statement_timeout = '6s'")
    rows = conn.execute(
        """SELECT job_name, started_at, finished_at, status
           FROM job_run WHERE started_at::timestamptz >= %s::timestamptz
           ORDER BY started_at DESC LIMIT 30""",
        (args.since,),
    ).fetchall()
result = []
for stored in rows:
    name, start, finish, status = (stored[key] for key in (
        "job_name", "started_at", "finished_at", "status"
    ))
    row = dict(job_name=name, started_at=start, finished_at=finish, status=status)
    if start and finish:
        row["seconds"] = round(
            (datetime.fromisoformat(finish) - datetime.fromisoformat(start)).total_seconds(), 3
        )
    result.append(row)
print(json.dumps({"read_at":datetime.now(timezone.utc).isoformat(),
                  "scope":"READ_ONLY_NATURAL_STARTUP_JOBS", "jobs":result}))
