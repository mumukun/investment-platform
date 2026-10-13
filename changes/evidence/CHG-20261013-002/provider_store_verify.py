import os
from datetime import datetime,timezone
from stock_analyzer import local_db
from stock_analyzer.market_structure_store import save_facts,load_facts,save_generation,generations
url=os.environ['STOCK_ANALYZER_DATABASE_URL']
assert '127.0.0.1:55441/seat_test' in url
assert os.environ['STOCK_ANALYZER_DB_SCHEMA']=='market_structure_validation'
with local_db.connect(url) as c:
    c.execute("DELETE FROM market_structure_fact WHERE kind='stock' AND entity_id='test-phase'")
    c.execute("DELETE FROM market_structure_generation WHERE input_hash=%s", ('f'*64,))
    c.commit()
base={'entity_id':'test-phase','code':'test-phase','trade_date':'2026-10-12','adjusted_close':10,'nominal_close':10,'amount':1,'source_name':'test','first_seen_at':'2026-10-12T06:00:00+00:00','fetched_at':'2026-10-12T06:00:00+00:00','observation_phase':'intraday'}
save_facts(url,'stock',[base])
final={**base,'adjusted_close':11,'nominal_close':11,'fetched_at':'2026-10-12T09:00:00+00:00','first_seen_at':'2026-10-12T09:00:00+00:00','observation_phase':'eod'}
save_facts(url,'stock',[final])
save_facts(url,'stock',[{**final,'fetched_at':'2026-10-12T10:00:00+00:00','first_seen_at':'2026-10-12T10:00:00+00:00'}])
chosen=load_facts(url,'2026-10-12','2026-10-12')['stock']['test-phase']['2026-10-12']
assert chosen['adjusted_close']==11 and chosen['observation_phase']=='eod'
assert 'revision_status' not in chosen
with local_db.connect(url) as c:
 assert c.execute("SELECT count(*) AS n FROM market_structure_fact WHERE kind='stock' AND entity_id='test-phase'").fetchone()['n']==2
save_facts(url,'stock',[{**final,'adjusted_close':12,'nominal_close':12}])
chosen=load_facts(url,'2026-10-12','2026-10-12')['stock']['test-phase']['2026-10-12']
assert chosen['adjusted_close']==11 and chosen['revision_status']=='source_revision_pending'
payload={'trade_date':'2026-10-12','phase':'eod','input_hash':'f'*64,'first_available_at':'2026-10-13T02:00:00+00:00'}
save_generation(url,payload)
save_generation(url,payload)
assert not generations(url,'2026-10-12',mode='known')
assert generations(url,'2026-10-12',mode='rebuilt')[0]['input_hash']=='f'*64
assert len(generations(url,'2026-10-13',mode='known'))==1
print('PASS: intraday -> first final selection, duplicate facts/generations, final conflict quarantine, point-in-time cutoff')
