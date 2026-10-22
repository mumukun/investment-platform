import io,json,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'backend')
from app.integrations.stock_analyzer import StockAnalyzerClient
trend=json.loads(Path('../investment-platform/changes/evidence/CHG-20261021-011/trend-replay.json').read_text())
payload={'summary':{'netInflow':0,'speed':0},'levels':[],'timeline':[{'time':'15:00','market':0}], 'sectorTrend':trend,'meta':{'isMock':False,'marketFlowAvailable':True,'contractVersion':'investment-dashboard-capital-flow-sina-v2','tradeDate':'2026-10-21','updatedAt':'2026-10-21T15:01:00+08:00'}}
with patch('app.integrations.stock_analyzer.urlopen',return_value=io.BytesIO(json.dumps(payload).encode())):
    result=StockAnalyzerClient('http://offline.test','fixture').fetch_capital_flow(sina_only=True)
assert result.sectorTrend==trend
print(f'PASS: actual Provider replay → Consumer validation, {len(trend["sampleWarnings"])} diagnostics preserved, original {len(trend["series"])} series unchanged, zero network requests')
