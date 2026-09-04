"""Everything the report needs, in one pass -> results.json"""
import csv, re, json, collections, random, numpy as np, prep, battery, anchors
from scipy.special import expit
sub=prep.subtlex(); out={}

def bat(S,x,label,trim=True):
    S=np.asarray(S); x=np.asarray(x,float)
    ok=np.isfinite(x); S,x=S[ok],x[ok]
    if trim:
        cnt=np.bincount(S,minlength=S.max()+2)
        keep=[c for c in np.unique(S) if cnt[c]>=0.005*len(S)]
        m=np.isin(S,keep); S,x=S[m],x[m]
    r=battery.battery(S,x,label)
    fw=r['free_widths']
    return dict(label=label,n=int(r['n']),K=int(r['K']),r=float(r['r']),
                cats=[int(c) for c in r['cats']], counts=[int(c) for c in r['counts']],
                cmean=[float(v) for v in r['cmean']],
                free_widths=[float(v) for v in fw],
                dAIC_equi_geom=float(r['dAIC_equi_minus_geom']),
                AIC_free=float(r['th']['free']['AIC']), AIC_geom=float(r['th']['geom']['AIC']),
                AIC_equi=float(r['th']['equi']['AIC']),
                mf={k:dict(AIC=float(v['AIC']),r2_obs=float(v['r2_obs']),r2_cat=float(v['r2_cat']))
                    for k,v in r['mf'].items()})

# ---------- Glasgow control ----------
rows=list(csv.reader(open('glasgow.csv'))); W,M,SD,N=[],[],[],[]
for r in rows[2:]:
    if not r or not r[0].strip(): continue
    w=re.sub(r'\s*\(.*?\)\s*','',r[0]).strip().lower()
    try: m,s,n=float(r[17]),float(r[18]),float(r[19])
    except ValueError: continue
    if w in sub and n>=5: W.append(w); M.append(m); SD.append(s); N.append(int(n))
M=np.array(M);SD=np.array(SD);N=np.array(N);zg=np.array([sub[w]['zipf'] for w in W])
out['glasgow']=bat(np.clip(np.rint(M),1,7).astype(int), zg,
                   "CONTROL: Glasgow FAM (rounded item mean) x SUBTLEX-US Zipf")
out['glasgow']['corr']=float(np.corrcoef(M,zg)[0,1])

# ---------- spelling2pronounce ----------
srows=prep.spelling2pronounce(); kept={w for w,_,_ in srows if w.strip().lower() in sub}
zf={w:sub[w.strip().lower()]['zipf'] for w in kept}
byw=collections.defaultdict(list)
for w,r,_ in srows:
    if w in kept: byw[w].append(7-r)                   # ease: ascends with frequency
ws=sorted(byw); nw=np.array([len(byw[w]) for w in ws]); xw=np.array([zf[w] for w in ws])
obs_mean=np.array([np.mean(byw[w]) for w in ws])
out['spell_agg']=bat(np.clip(np.rint(obs_mean),1,6).astype(int), xw,
                     "spelling2pronounce: rounded item-mean ease x SUBTLEX-US Zipf")
out['spell_agg']['corr']=float(np.corrcoef(obs_mean,xw)[0,1])
out['spell_agg']['match_rate']=len(kept)/23282
Si=np.concatenate([byw[w] for w in ws]); xi=np.repeat(xw,nw)
out['spell_ind']=bat(Si,xi,"spelling2pronounce: INDIVIDUAL ratings x SUBTLEX-US Zipf")

# ---------- kalimah (Arabic) ----------
kr=[r for r in csv.DictReader(open('kalimahnorms_alzahrani_2025.csv'))
    if r['cov_frequency'] not in ('','NA') and r['item']=='aoa' and r['resp'] not in ('','NA')]
S=np.array([int(float(r['resp'])) for r in kr]); x=np.array([np.log10(float(r['cov_frequency'])) for r in kr])
m=S>0
out['kalimah']=bat(8-S[m],x[m],"kalimah: earliness (8 - age of acquisition) x log corpus frequency")

# ---------- Forthmann ----------
fr=[r for r in csv.DictReader(open('Forthmann-2024-creative_quality.csv'))
    if r['itemcov_frequency'] not in ('','NA') and r['resp'] not in ('','NA')]
S=np.array([int(float(r['resp'])) for r in fr]); x=np.array([np.log10(float(r['itemcov_frequency'])) for r in fr])
out['forthmann']=bat(6-S,x,"Forthmann-2024: conventionality (6 - creative quality) x log idea frequency")

# ---------- per-rater ----------
byr=collections.defaultdict(list)
for w,r,rt in srows:
    if w in kept: byr[rt].append((7-r,zf[w]))
big=sorted([rt for rt in byr if len(byr[rt])>=200]); random.Random(42).shuffle(big)
rs=[]
for rt in big[:400]:
    Sr=np.array([a for a,b in byr[rt]]); xr=np.array([b for a,b in byr[rt]])
    if len(np.unique(Sr))<5: continue
    try: v=battery.fit_thresholds(Sr,xr,"geom",len(np.unique(Sr)),np.unique(Sr),nbins=150)["r"]
    except Exception: continue
    if np.isfinite(v) and 0.2<v<6: rs.append(float(v))
out['per_rater']=dict(n_eligible=len([k for k in byr if len(byr[k])>=200]), n=len(rs),
                      median=float(np.median(rs)), q1=float(np.percentile(rs,25)),
                      q3=float(np.percentile(rs,75)), frac_gt1=float(np.mean(np.array(rs)>1)),
                      values=rs)

# ---------- aggregation null: spelling ----------
cats=np.arange(1,7); fit=battery.fit_thresholds(Si,xi,"free",6,cats)
taus,beta=fit["taus"],fit["beta"]
r_ind=battery.fit_thresholds(Si,xi,"geom",6,cats)["r"]
def agg_r(means):
    Sa=np.clip(np.rint(means),1,6).astype(int); cnt=np.bincount(Sa,minlength=7)
    keep=[c for c in range(1,7) if cnt[c]>=0.005*len(Sa)]; m=np.isin(Sa,keep); c=np.unique(Sa[m])
    return float(battery.fit_thresholds(Sa[m],xw[m],"geom",len(c),c)["r"]), cnt[1:].tolist()
rng=np.random.default_rng(42)
def sim_means(sig):
    u=rng.normal(0,sig,len(ws)); cum=np.empty((len(ws),7)); cum[:,0]=0; cum[:,6]=1
    cum[:,1:6]=expit(taus[None,:]-(beta*xw+u)[:,None])
    p=np.clip(np.diff(cum,axis=1),1e-12,None); p/=p.sum(1,keepdims=True)
    mm=np.array([rng.choice(6,size=nw[i],p=p[i]).mean() for i in range(len(ws))])
    return mm-mm.mean()+obs_mean.mean()
lo,hi=0.,8.
for _ in range(12):
    mid=(lo+hi)/2
    if sim_means(mid).std()<obs_mean.std(): lo=mid
    else: hi=mid
sig=(lo+hi)/2
sims=[agg_r(sim_means(sig))[0] for _ in range(6)]
out['spell_null']=dict(r_individual=float(r_ind), sigma=float(sig), sims=sims,
                       r_sim_mean=float(np.mean(sims)), r_observed=out['spell_agg']['r'],
                       obs_counts=out['spell_agg']['counts'])

# ---------- aggregation null: Glasgow ----------
b,a=np.polyfit(zg,M,1); s_bw=np.sqrt(max((M-(a+b*zg)).var()-np.mean(SD**2/N),0))
def r_of(means):
    S=np.clip(np.rint(means),1,7).astype(int); cnt=np.bincount(S,minlength=8)
    keep=[c for c in range(1,8) if cnt[c]>=0.005*len(S)]; m=np.isin(S,keep); c=np.unique(S[m])
    return float(battery.fit_thresholds(S[m],zg[m],"geom",len(c),c)["r"])
gs=[]
for _ in range(6):
    lat=a+b*zg+rng.normal(0,s_bw,len(zg))
    sm=np.array([np.clip(np.rint(lat[i]+rng.normal(0,SD[i],N[i])),1,7).mean() for i in range(len(zg))])
    gs.append(r_of(sm-sm.mean()+M.mean()))
out['glasgow_null']=dict(slope=float(b),intercept=float(a),between_sd=float(s_bw),
                         sims=gs, r_sim_mean=float(np.mean(gs)), r_observed=out['glasgow']['r'],
                         median_N=float(np.median(N)), median_SD=float(np.median(SD)))

# ---------- anchor race ----------
out['anchor']={}
for k,(S_,x_) in {'glasgow':(np.clip(np.rint(M),1,7).astype(int),zg),
                  'spell_ind':(Si,xi)}.items():
    a_=anchors.anchor_race(S_,x_,k)
    out['anchor'][k]={n:dict(AIC_free=float(v['AIC_free']),AIC_geom=float(v['AIC_geom']),
                             AIC_equi=float(v['AIC_equi']),r=float(v['r'])) for n,v in a_.items()}

json.dump(out, open("results.json","w"), indent=1)
print("\nWROTE results.json")
for k in ('glasgow','spell_agg','spell_ind','kalimah','forthmann'):
    v=out[k]; print(f"  {k:12s} n={v['n']:>7} K={v['K']} r={v['r']:.3f}  dAIC(equi-geom)={v['dAIC_equi_geom']:.0f}")
print("  per-rater median r =", round(out['per_rater']['median'],3))
print("  spell null: individual r=%.3f -> aggregate r=%.3f (observed %.3f)" %
      (out['spell_null']['r_individual'], out['spell_null']['r_sim_mean'], out['spell_null']['r_observed']))
print("  glasgow null: Fechnerian -> aggregate r=%.3f (observed %.3f)" %
      (out['glasgow_null']['r_sim_mean'], out['glasgow_null']['r_observed']))
