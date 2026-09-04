import csv, collections, numpy as np, battery, pickle
res={}

# ---- kalimah: Arabic word norms, cov_frequency in table ----
rows=[r for r in csv.DictReader(open('kalimahnorms_alzahrani_2025.csv'))
      if r['cov_frequency'] not in ('','NA') and r['resp'] not in ('','NA')]
for item,label in [('aoa','age of acquisition'),('cnc','concreteness')]:
    sub=[r for r in rows if r['item']==item]
    for drop0 in (False,True):
        S=np.array([int(float(r['resp'])) for r in sub])
        x=np.array([np.log10(float(r['cov_frequency'])) for r in sub])
        if drop0:
            m=S>0; S,x=S[m],x[m]
        sgn = -1 if item=='aoa' else 1     # later-acquired words are rarer
        key=f"kalimah_{item}{'_no0' if drop0 else ''}"
        res[key]=battery.battery(S, sgn*x,
            f"kalimah {label} (K={len(np.unique(S))}) x {'(-)' if sgn<0 else ''}log corpus frequency"
            + (" [0 dropped]" if drop0 else ""))
        print(battery.report(res[key]), flush=True)
        # aggregate (item-mean) variant
        if not drop0:
            by=collections.defaultdict(list); fx={}
            for r,s,xx in zip(sub,S,x): by[r['id']].append(s); fx[r['id']]=xx
            ids=sorted(by); Sa=np.clip(np.rint([np.mean(by[i]) for i in ids]),0,7).astype(int)
            xa=sgn*np.array([fx[i] for i in ids])
            res[key+"_agg"]=battery.battery(Sa,xa,f"kalimah {label} ROUNDED ITEM MEAN x {'(-)' if sgn<0 else ''}log frequency")
            print(battery.report(res[key+"_agg"]), flush=True)

# ---- Forthmann creative quality ----
rows=[r for r in csv.DictReader(open('Forthmann-2024-creative_quality.csv'))
      if r['itemcov_frequency'] not in ('','NA') and r['resp'] not in ('','NA')]
S=np.array([int(float(r['resp'])) for r in rows])
x=-np.array([np.log10(float(r['itemcov_frequency'])) for r in rows])   # rarer idea = more creative
res['forthmann']=battery.battery(S,x,"Forthmann-2024 creative quality x (-)log idea frequency")
print(battery.report(res['forthmann']), flush=True)

pickle.dump(res, open("res_others.pkl","wb"))
