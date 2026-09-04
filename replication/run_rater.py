import collections, random, numpy as np, prep, battery
sub=prep.subtlex(); rows=prep.spelling2pronounce()
kept={w for w,_,_ in rows if w.strip().lower() in sub}
zf={w:sub[w.strip().lower()]['zipf'] for w in kept}
byr=collections.defaultdict(list)
for w,r,rt in rows:
    if w in kept: byr[rt].append((7-r, zf[w]))     # ease, ascends with frequency
big=sorted([rt for rt in byr if len(byr[rt])>=200]); random.Random(42).shuffle(big); big=big[:400]
print(f"{len([k for k in byr if len(byr[k])>=200])} raters with >=200 words; using {len(big)}")
rs=[]
for rt in big:
    Sr=np.array([a for a,b in byr[rt]]); xr=np.array([b for a,b in byr[rt]])
    if len(np.unique(Sr))<5: continue
    try: v=battery.fit_thresholds(Sr,xr,"geom",len(np.unique(Sr)),np.unique(Sr),nbins=150)["r"]
    except Exception: continue
    if np.isfinite(v) and 0.2<v<6: rs.append(v)
rs=np.array(rs)
print(f"per-rater r: n={len(rs)} median={np.median(rs):.3f} IQR=[{np.percentile(rs,25):.3f},{np.percentile(rs,75):.3f}] frac>1={np.mean(rs>1):.3f}")
np.save("per_rater_r.npy", rs)
