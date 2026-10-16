"""Run inside the existing Provider; own database read-only, no source requests."""
import json, os, re
import psycopg
from psycopg.rows import dict_row
from stock_analyzer.version import APP_VERSION
schema = os.environ.get('STOCK_ANALYZER_DB_SCHEMA', 'stock_analyzer')
assert re.fullmatch('[a-z_][a-z0-9_]*', schema)
with psycopg.connect(os.environ['STOCK_ANALYZER_DATABASE_URL'], row_factory=dict_row,
                     options='-c default_transaction_read_only=on -c search_path=' + schema) as conn:
    facts = conn.execute("SELECT kind,entity_id,max(trade_date) AS latest,count(*) AS count FROM market_structure_fact WHERE kind IN ('index','etf_price','share','nav','average_price_index','microcap_index','local_breadth') GROUP BY kind,entity_id ORDER BY kind,entity_id").fetchall()
    days = conn.execute("SELECT DISTINCT ON (trade_date) trade_date,payload FROM market_structure_generation WHERE rules_version='market-structure-rules-v1.3.0' ORDER BY trade_date DESC,first_available_at DESC LIMIT 3").fetchall()
    sync = conn.execute("SELECT payload FROM market_structure_fact WHERE kind='sync' ORDER BY first_seen_at DESC LIMIT 1").fetchone()
    summaries=[]
    for r in days:
        d=r['payload'];m=d['market']
        summaries.append(dict(date=d['trade_date'],phase=d['phase'],generated_at=d['generated_at'],quality=d['quality'],indices=[dict(id=i['id'],close=i['close'],returns=i['returns']) for i in d['indices']],styles=d['styles'],market={k:m.get(k) for k in ('valid_return_count','ma20_eligible_count','ma60_eligible_count','data_time','reason_codes')},funds=[{k:f.get(k) for k in ('code','price_close','share_date','nav_date','flow_est_cny','reason_codes')} for f in d['funds']]))
print(json.dumps(dict(version=APP_VERSION,facts=facts,days=summaries,last_collection=sync['payload'] if sync else None),ensure_ascii=False,default=str))
