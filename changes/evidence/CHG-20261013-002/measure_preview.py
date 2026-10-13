import json,time,statistics,urllib.request
results={}
for name,url,headers in [('provider','http://127.0.0.1:18829/api/integrations/investment-dashboard/market-structure?lookback=120',{'Authorization':'Bearer market-structure-local-test'}),('overview','http://127.0.0.1:18029/api/v1/market-structure/overview?lookback=120',{}),('history','http://127.0.0.1:18029/api/v1/market-structure/regime/history?lookback=120',{})]:
    durations=[]
    for n in range(20):
        start=time.perf_counter()
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=10) as response:
            body=response.read()
            if response.status !=200: raise ValueError('Bad status')
        durations.append((time.perf_counter()-start)*1000)
    results[name]={'requests':20,'p95_ms':sorted(durations)[18],'median_ms':statistics.median(durations),'bytes':len(body),'scope':'localhost cached data, not production or cold browser navigation'}
print(json.dumps(results,indent=2))
