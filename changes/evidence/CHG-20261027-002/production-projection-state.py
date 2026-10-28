"""Read versioned prepared-result metadata without building or publishing."""
import json
from datetime import datetime, timezone
from stock_analyzer import local_db
from stock_analyzer.settings import load_settings
from stock_analyzer.version import APP_VERSION

with local_db.readonly_connect(load_settings().hotmap.database_url) as conn:
    conn.execute("SET LOCAL statement_timeout = '6s'")
    rows = conn.execute(
        """SELECT cache_key,built_at,checked_at,failed_at,
                  payload->>'generated_at' AS generated_at,
                  payload->>'data_time' AS data_time
           FROM api_read_projection WHERE cache_key LIKE %s ORDER BY cache_key""",
        (APP_VERSION + ':%',),
    ).fetchall()
print(json.dumps({'read_at':datetime.now(timezone.utc).isoformat(),
                  'application_version':APP_VERSION,
                  'projections':rows}, default=lambda value:value.isoformat()))
