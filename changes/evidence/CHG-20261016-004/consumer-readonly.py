"""Read only Dashboard's own public-market projections. No synchronization."""
import sys, json
sys.path.insert(0, '/app/backend')
from datetime import datetime
from zoneinfo import ZoneInfo
from app.database import SessionLocal
from app.market_structure import read_projection
from app.version import build_metadata
with SessionLocal() as db:
    db.connection().exec_driver_sql('SET TRANSACTION READ ONLY')
    result=read_projection(db,datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat(),120,'rebuilt')
print(json.dumps({'runtime':build_metadata(),'projection':result},ensure_ascii=False,default=str))
