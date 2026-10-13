"""Read-only bounded public-source verification; no service credentials."""
import concurrent.futures
import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PYTHON = '/Users/mukun/work/workspace/stock/stock-analyzer/.venv/bin/python'
CASES = [('stock_zh_a_spot_em', {}), ('stock_info_a_code_name', {}),
 ('stock_zh_a_hist', {'symbol':'600000','start_date':'20260101','end_date':'20261012','adjust':'qfq'}),
 ('tool_trade_date_hist_sina', {}),
 *[('stock_zh_index_daily_em', {'symbol':s,'start_date':'20260101','end_date':'20261012'}) for s in ['sh000300','sh000985','sh000688','csi932000']],
 *[('fund_etf_scale_sse', {'date':d}) for d in ['20261009','20261012']],
 ('fund_scale_daily_szse', {'start_date':'20261009','end_date':'20261012','symbol':'ETF'}),
 *[('fund_etf_fund_info_em', {'fund':c,'start_date':'20260101','end_date':'20261012'}) for c in ['510050','510300','510310','510330','159919','510500','512100','588000','588080','159915']],
 ('fund_etf_spot_em', {})]
SCRIPT = '''import requests, json, sys, akshare as ak
original=requests.sessions.Session.request
def bounded(self,method,url,**kw):
 kw.setdefault('timeout',10)
 return original(self,method,url,**kw)
requests.sessions.Session.request=bounded
name,params=json.loads(sys.argv[1])
try:
 df=getattr(ak,name)(**params)
 result={'status':'success' if len(df) else 'empty','akshare_version':ak.__version__,'rows':len(df),'fields':list(df.columns),'sample':json.loads(df.head(2).to_json(orient='records',force_ascii=False,date_format='iso'))}
 dates=[c for c in df.columns if '日期' in str(c) or c in ['date','trade_date']]
 result['date_ranges']={str(c):{'min':str(df[c].min()),'max':str(df[c].max())} for c in dates}
 print('PROBE_JSON'+json.dumps(result,ensure_ascii=False))
except Exception as e:
 print('PROBE_JSON'+json.dumps({'status':'failed','akshare_version':ak.__version__,'error_type':type(e).__name__},ensure_ascii=False))
'''
def probe(case):
 started=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
 try:
  run=subprocess.run([PYTHON,'-c',SCRIPT,json.dumps(case)],capture_output=True,text=True,timeout=35)
  lines=[line[10:] for line in run.stdout.splitlines() if line.startswith('PROBE_JSON')]
  result=json.loads(lines[-1]) if lines else {'status':'failed','error_type':'NoStructuredResult'}
 except subprocess.TimeoutExpired:
  result={'status':'timeout','limit_seconds':35}
 result.update(interface=case[0],parameters=case[1],tested_at=started)
 print(case[0],case[1],result['status'],flush=True)
 return result
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  results=list(pool.map(probe,CASES))
 Path(__file__).with_name('source-probe.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
