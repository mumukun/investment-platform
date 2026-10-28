"""Read and serialize a response in memory; no publish or refresh is invoked."""
import json
from stock_analyzer import local_db

read = local_db.readonly_connect
def readonly(database_url, schema=None):
    conn = read(database_url, schema=schema)
    conn.execute("SET LOCAL statement_timeout = '10s'")
    return conn
local_db.connect = readonly

from stock_analyzer import api
payload = api.investment_dashboard_short_selection.__wrapped__()
json.dumps(payload, allow_nan=False)
print(json.dumps({'status':'RESPONSE_JSON_PASS','candidates':len(payload['candidates'])}))
