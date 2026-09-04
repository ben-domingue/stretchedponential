"""Vlad's 'Range, not frequency' control (his Sec. 5.5), run on every battery.

log-magnitude anchor  vs  rank/CDF anchor (Bhui & Gershman efficient coding).
If the geometric widening is a fact about the report scale it should survive the
rank anchor; if it is the thin high-frequency tail of a Zipf distribution it
should collapse to r ~ 1 once the stimulus is rank-transformed.
"""
import numpy as np, battery
from scipy.stats import norm

def rank_anchor(x):
    o = np.argsort(np.argsort(x, kind="stable"))
    return norm.ppf((o+0.5)/len(x))

def anchor_race(S, x, label):
    S = np.asarray(S); x = np.asarray(x, float)
    ok = np.isfinite(x); S, x = S[ok], x[ok]
    cats = np.unique(S); K = len(cats)
    out = {}
    for nm, xx in (("log magnitude", x), ("rank / CDF", rank_anchor(x))):
        free = battery.fit_thresholds(S, xx, "free", K, cats)
        geom = battery.fit_thresholds(S, xx, "geom", K, cats)
        equi = battery.fit_thresholds(S, xx, "equi", K, cats)
        w = np.diff(free["taus"])/abs(free["beta"])
        out[nm] = dict(AIC_free=free["AIC"], AIC_geom=geom["AIC"], AIC_equi=equi["AIC"],
                       r=geom["r"], widths=w/w[0])
    print(f"--- {label}   n={len(S)} K={K}")
    for nm, v in out.items():
        print(f"    {nm:14s} AIC free={v['AIC_free']:12.1f}  geom={v['AIC_geom']:12.1f}"
              f"  equi={v['AIC_equi']:12.1f}   r={v['r']:.3f}   "
              f"widths(rel)=[{', '.join(f'{q:.2f}' for q in v['widths'])}]")
    print(f"    anchor verdict: dAIC(rank - log) on free model = "
          f"{out['rank / CDF']['AIC_free']-out['log magnitude']['AIC_free']:+.1f} "
          "(positive => log magnitude wins, as Vlad reports)", flush=True)
    return out
