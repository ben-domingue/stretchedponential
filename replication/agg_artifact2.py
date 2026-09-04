"""Same test, but the simulator is calibrated to the real dispersion of word means.

Individual ratings are generated from the fitted individual-level GRM (r~1) PLUS a
word random intercept whose SD is tuned so simulated per-word mean ease matches the
observed SD. Any r>1 that comes out is manufactured by average-then-round alone.
"""
import collections, numpy as np, prep, battery
from scipy.special import expit
sub=prep.subtlex(); rows=prep.spelling2pronounce()
kept={w for w,_,_ in rows if w.strip().lower() in sub}
zf={w:sub[w.strip().lower()]['zipf'] for w in kept}
byw=collections.defaultdict(list)
for w,r,_ in rows:
    if w in kept: byw[w].append(7-r)
ws=sorted(byw); nw=np.array([len(byw[w]) for w in ws]); xw=np.array([zf[w] for w in ws])
Si=np.concatenate([byw[w] for w in ws]); xi=np.repeat(xw,nw)
cats=np.arange(1,7)
fit=battery.fit_thresholds(Si,xi,"free",6,cats); taus,beta=fit["taus"],fit["beta"]
r_ind=battery.fit_thresholds(Si,xi,"geom",6,cats)["r"]
obs_mean=np.array([np.mean(byw[w]) for w in ws]); target=obs_mean.std()
print(f"individual-level r = {r_ind:.4f};  observed SD of per-word mean ease = {target:.3f}")

def agg_r(means):
    Sa=np.clip(np.rint(means),1,6).astype(int)
    cnt=np.bincount(Sa,minlength=7)
    keep=[c for c in range(1,7) if cnt[c] >= 0.005*len(Sa)]   # same sparse-cell rule both sides
    m=np.isin(Sa,keep)
    c=np.unique(Sa[m]); return battery.fit_thresholds(Sa[m],xw[m],"geom",len(c),c)["r"], cnt[1:], keep

r_obs,cnt,keep=agg_r(obs_mean); print(f"OBSERVED aggregate r = {r_obs:.3f}  counts {cnt}  kept {keep}")

rng=np.random.default_rng(42)
def sim_means(sigma):
    u=rng.normal(0,sigma,len(ws))
    cum=np.empty((len(ws),7)); cum[:,0]=0; cum[:,6]=1
    cum[:,1:6]=expit(taus[None,:]-(beta*xw+u)[:,None])
    p=np.clip(np.diff(cum,axis=1),1e-12,None); p/=p.sum(1,keepdims=True)
    mm=np.array([rng.choice(6,size=nw[i],p=p[i]).mean() for i in range(len(ws))])
    return mm - mm.mean() + obs_mean.mean()   # match location; only dispersion+rounding is under test

lo,hi=0.0,8.0
for _ in range(12):
    mid=(lo+hi)/2
    s=sim_means(mid).std()
    if s<target: lo=mid
    else: hi=mid
sigma=(lo+hi)/2; print(f"calibrated word-effect sigma = {sigma:.3f} -> simulated SD {sim_means(sigma).std():.3f}")
sims=[]
for rep in range(6):
    rr,cc,kk=agg_r(sim_means(sigma)); sims.append(rr)
    print(f"  SIMULATED aggregate r = {rr:.3f}  counts {cc}  kept {kk}")
print(f"\nGenerating model r = {r_ind:.3f} (flat).  Average-then-round yields r = {np.mean(sims):.3f} "
      f"[{min(sims):.3f}, {max(sims):.3f}].  Observed = {r_obs:.3f}.")
