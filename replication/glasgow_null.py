"""Does Vlad's own word-familiarity r survive a strictly Fechnerian generating model?

Null: an individual familiarity rating is a LINEAR function of Zipf plus noise,
rounded to the 1-7 scale -- equally spaced categories in log frequency, r = 1 by
construction. Calibrated to the Glasgow Norms' own regression on Zipf, its
per-word residual spread, its per-word rating SDs and its per-word N.
Then averaged over N raters and rounded, exactly as Vlad's battery does.
"""
import csv, re, numpy as np, prep, battery
sub=prep.subtlex()
rows=list(csv.reader(open('glasgow.csv')))
W,M,SD,N=[],[],[],[]
for r in rows[2:]:
    if not r or not r[0].strip(): continue
    w=re.sub(r'\s*\(.*?\)\s*','',r[0]).strip().lower()
    try: m,s,n=float(r[17]),float(r[18]),float(r[19])
    except ValueError: continue
    if w in sub and n>=5: W.append(w); M.append(m); SD.append(s); N.append(int(n))
M=np.array(M); SD=np.array(SD); N=np.array(N); z=np.array([sub[w]['zipf'] for w in W])
print(f"n={len(W)}  median raters/word={np.median(N):.0f}  median within-word SD={np.median(SD):.2f}")
b,a=np.polyfit(z,M,1); resid=M-(a+b*z); s_between=np.sqrt(max(resid.var()-np.mean(SD**2/N),0))
print(f"item mean FAM = {a:.3f} + {b:.3f}*Zipf ; residual between-word SD = {s_between:.3f}")

def r_of(means):
    S=np.clip(np.rint(means),1,7).astype(int)
    cnt=np.bincount(S,minlength=8)
    keep=[c for c in range(1,8) if cnt[c]>=0.005*len(S)]
    m=np.isin(S,keep); c=np.unique(S[m])
    return battery.fit_thresholds(S[m],z[m],"geom",len(c),c)["r"], cnt[1:], keep

r_obs,cnt,keep=r_of(M); print(f"\nOBSERVED (Glasgow item means) r = {r_obs:.3f}  counts {cnt}  kept {keep}")

rng=np.random.default_rng(42); sims=[]
for rep in range(6):
    lat=a+b*z+rng.normal(0,s_between,len(z))                 # linear in Zipf
    sim=np.array([np.clip(np.rint(lat[i]+rng.normal(0,SD[i],N[i])),1,7).mean() for i in range(len(z))])
    sim=sim-sim.mean()+M.mean()
    rr,cc,kk=r_of(sim); sims.append(rr)
    print(f"  SIMULATED (Fechnerian null) r = {rr:.3f}  counts {cc}  kept {kk}")
print(f"\nA strictly equidistant generating model, averaged and rounded the same way, gives "
      f"r = {np.mean(sims):.3f} [{min(sims):.3f}, {max(sims):.3f}] vs observed {r_obs:.3f}.")
