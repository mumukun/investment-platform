"""Read-only synthetic sensitivity analysis of existing pure rule functions.

Usage: python3 -B assess_intraday_algorithm.py /path/to/stock-analyzer result.json
No database, network, application mutation, or return/backtest claim.
"""
import copy
import json
import math
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import mean

repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo))
from stock_analyzer import short_tail_engine as tail
from stock_analyzer import swing_engine as swing
from stock_analyzer import swing_features as sf

day = '2026-10-23'
sessions = []
d = date(2026, 1, 1)
while d <= date(2026, 10, 23):
    if d.weekday() < 5:
        sessions.append(d.isoformat())
    d += timedelta(days=1)
history_dates = [d for d in sessions if d < day][-25:]
at = datetime.fromisoformat(day + 'T10:00:30+08:00')

def inputs(hist_amount, current_amount):
    quotes, rules, histories, members = {}, {}, {}, []
    for i in range(20):
        code = f'600{i:03d}'
        price = 10.5 if i < 10 else 10.44
        industry = 'synthetic-A' if i < 10 else 'synthetic-B'
        quotes[code] = dict(code=code, name='synthetic', price=price,
            previous_close=10.48, change_pct=(price/10.48-1)*100,
            amount=current_amount, high=max(price+.03, 10.53), low=10.38,
            quote_time=day+'T10:00:00+08:00', received_at=day+'T10:00:01+08:00',
            source='tencent', industry=industry)
        rules[code] = dict(code=code, trade_date=day, exchange='SSE', board='主板',
            listing_date='2020-01-01', price_limit_pct=10., price_tick=.01,
            is_st=False, is_suspended=False, is_no_limit_day=False)
        histories[code] = [dict(trade_date=d, adjusted_close=10+j*.02,
            adjusted_high=10+j*.02+.1, adjusted_low=10+j*.02-.1,
            amount=hist_amount, adjustment_as_of=history_dates[-1])
            for j,d in enumerate(history_dates)]
        members.append(dict(code=code, listing_date='2020-01-01', industry=industry))
    return quotes, rules, histories, dict(items=members, complete=True, as_of=day), sessions

cases = []
for label, historical, current in [('both_pass', 2e8, 2e8),
    ('newly_active_stock', .8e8, 2e8), ('early_session', 2e8, .2e8)]:
    q,r,h,d,cal = inputs(historical, current)
    original = tail.evaluate(q,r,h,d,cal,at)
    strict = [i for i in original['items'] if i['eligible']]
    # Counterfactual ONLY for the liquidity predicate. All other original
    # item reasons are retained; this is not a new engine implementation.
    replaced = [i for i in original['items'] if
        not [reason for reason in i['reasons'] if reason != '当日累计成交额不足1亿元']
        and mean(b['amount'] for b in h[i['code']][-20:]) >= tail.MIN_AMOUNT]
    cases.append(dict(case=label, history_average=historical, current_amount=current,
        original_eligible=len(strict), history_gate_eligible=len(replaced),
        removed=len({i['code'] for i in strict}-{i['code'] for i in replaced}),
        added=len({i['code'] for i in replaced}-{i['code'] for i in strict})))
assert [(i['original_eligible'],i['history_gate_eligible']) for i in cases] == [(10,10),(10,0),(0,10)]

q,r,h,d,cal = inputs(2e8,None)
missing = tail.evaluate(q,r,h,d,cal,at)
missing_case = dict(current_amount=None, original_items=len(missing['items']),
    original_coverage=missing['market']['coverage'],
    usable_price_history_structures=sum(bool(tail.features(h[c],v,cal,day)['paths']) for c,v in q.items()))
assert missing_case['original_items']==0

q,r,h,d,cal=inputs(2e8,2e8)
for j,code in enumerate(q):
    q[code]['amount']=(1.1+j/10)*1e8
    for bar in h[code]:
        bar['amount']=(3-j/20)*1e8
result=tail.evaluate(q,r,h,d,cal,at)
strict=[i for i in result['items'] if i['eligible']]
original_order=[i['code'] for i in strict]
replaced_order=[i['code'] for i in sorted(strict,key=lambda i:(
    -(i['sector_relative'] or 0),-(i['relative'] or 0),
    abs(i['price']-i['features']['support'])/i['features']['atr'],
    -mean(b['amount'] for b in h[i['code']][-20:]),i['code']))]
rank_case=dict(original_eligible_count=len(strict),
    changed_positions=sum(a!=b for a,b in zip(original_order,replaced_order)))
assert rank_case['changed_positions']==10

history = [d for d in sessions if d < day][-140:]
groups={'historical_ma':['ma5','ma10','ma20','ma60','ma10_slope','ma20_slope','ma60_slope'],
        'historical_atr':['atr_5','atr_20','natr_20']}
wave={k:dict(comparisons=0,decision_changes=0,numerical_changes=0,example=None) for k in groups}
for shape in ['rising','flat','falling','turning']:
    bars=[]
    for j,dt in enumerate(history):
        close={'rising':10+j*.02,'flat':12+.05*math.sin(j/5),
               'falling':14-j*.01,'turning':12+(j-115)*(.02 if j>=115 else -.004)}[shape]
        bars.append(dict(trade_date=dt,adjusted_open=close,adjusted_high=close+.1,
                         adjusted_low=close-.1,adjusted_close=close,amount=2e8))
    baseline=sf.build_features(bars,index_pct10=0,index_pct20=0,sector_pct10=0)
    prev=bars[-1]['adjusted_close']
    for bp in range(-800,801,25):
        price=prev*(1+bp/10000)
        quote=dict(prev_close=prev,price=price,open=prev,
                   high_today=max(prev,price)+.02,low_today=min(prev,price)-.02,amount=1e7)
        live=sf.build_intraday_features(bars,quote,trade_date=day,baseline_date=history[-1],
            baseline_features=baseline,index_pct10=0,index_pct20=0,sector_pct10=0)
        assert live is not None
        for pattern in swing.PATTERNS:
            def evaluate(f):
                return swing.evaluate_candidate(code='600000',name='synthetic',industry='synthetic',
                    pattern=pattern,features=f,avg_amount_yi=2,security_ok=True,
                    market_regime='健康轮动',sector_lifecycle='二次确认')
            old=evaluate(live)
            assert old==evaluate(copy.deepcopy(live))
            for name,keys in groups.items():
                swapped={**live,**{key:baseline[key] for key in keys}}
                new=evaluate(swapped)
                report=wave[name]
                report['comparisons']+=1
                decisions=('observation_ok','state','participation_decision')
                numbers=('structure_completion','key_level','stop_reference','risk_distance_atr')
                changed=any(old[k]!=new[k] for k in decisions)
                report['decision_changes']+=changed
                report['numerical_changes']+=any(old[k]!=new[k] for k in numbers)
                if changed and report['example'] is None:
                    report['example']=dict(shape=shape,current_change_bp=bp,pattern=pattern,
                        before={k:old[k] for k in decisions+numbers},after={k:new[k] for k in decisions+numbers})
output=dict(kind='synthetic_sensitivity_analysis_not_market_backtest',
    source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
    python=sys.version.split()[0],rules=dict(swing=swing.RULES_VERSION,short_tail=tail.RULES),
    short_liquidity=cases,missing_amount=missing_case,short_ranking=rank_case,
    swing_feature_substitution=wave,
    limits=['Synthetic boundary cases do not estimate market-wide change rate or returns.',
            'Original functions only; revised implementation and end-to-end parity are not tested.'])
Path(sys.argv[2]).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(output,ensure_ascii=False,indent=2))
