"""Chituc stretched-exponential battery, ported for IRW tables.

Two halves, both as on vladchituc.com/s/stretched-exponential.html:
  A. mean-function race   : NLS/OLS of log-stimulus x on rating S
  B. threshold tournament : anchored ordinal-logistic GRM, three threshold families
"""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

# ---------- A. mean function race ----------
def _aic(rss, n, k):
    return n*np.log(rss/n) + 2*(k+1)          # +1 for sigma

def _r2(y, yh):
    return 1 - np.sum((y-yh)**2)/np.sum((y-np.mean(y))**2)

def mean_function_race(S, x):
    S = np.asarray(S, float); x = np.asarray(x, float); n = len(S)
    cats = np.unique(S)
    cmean = np.array([x[S == c].mean() for c in cats])
    out = {}

    def add(name, pred_fun, k, theta):
        yh = pred_fun(S)
        rss = np.sum((x-yh)**2)
        out[name] = dict(params=k, AIC=_aic(rss, n, k),
                         r2_obs=_r2(x, yh),
                         r2_cat=_r2(cmean, pred_fun(cats)),
                         theta=theta)

    # linear (Fechner: fixed stimulus ratio per step)
    b = np.polyfit(S, x, 1); add("linear (Fechner)", lambda s: np.polyval(b, s), 2, b)
    # quadratic
    q = np.polyfit(S, x, 2); add("quadratic", lambda s: np.polyval(q, s), 3, q)
    # power law in the rating
    Sm = S.min() - 1.0
    p = np.polyfit(np.log(S-Sm), x, 1); add("power law", lambda s: np.polyval(p, np.log(s-Sm)), 2, p)
    # stretched exponential  x = c + A exp(beta S)  -- profile over beta (linear in c, A)
    from scipy.optimize import minimize_scalar
    Sc = S - S.mean()
    cats_arr = np.unique(S)
    nc = np.array([np.sum(S == c) for c in cats_arr]); cm = cmean
    Scc = cats_arr - S.mean()
    tss = np.sum((x - x.mean())**2)
    def prof(beta):
        # RSS over observations reduces to a weighted fit on category means + within-cat SS
        E = np.exp(beta*Scc)
        W = nc
        Sw = W.sum(); Se_ = (W*E).sum(); See = (W*E*E).sum()
        Sy = (W*cm).sum(); Sey = (W*E*cm).sum()
        den = Sw*See - Se_**2
        if abs(den) < 1e-300: return np.inf, (0.0, 0.0)
        A = (Sw*Sey - Se_*Sy)/den
        c0 = (Sy - A*Se_)/Sw
        rss_between = np.sum(W*(cm - (c0 + A*E))**2)
        return rss_between, (c0, A)
    grid = np.linspace(-3.0, 3.0, 601)
    vals = np.array([prof(b)[0] for b in grid])
    b0 = grid[np.nanargmin(vals)]
    rr = minimize_scalar(lambda b: prof(b)[0], bracket=None,
                         bounds=(b0-0.02, b0+0.02), method="bounded",
                         options=dict(xatol=1e-10))
    beta_hat = rr.x if rr.fun <= prof(b0)[0] else b0
    c0, A = prof(beta_hat)[1]
    th = np.array([c0, A, beta_hat])
    add("stretched exponential", lambda s: th[0]+th[1]*np.exp(th[2]*(s - S.mean())), 4, th)
    # saturated: free category means
    idx = {c: i for i, c in enumerate(cats)}
    add("free category means", lambda s: cmean[[idx[v] for v in s]], len(cats), cmean)
    return out, cats, cmean

# ---------- B. threshold tournament (anchored GRM) ----------
def _taus(family, th, K):
    if family == "free":
        return np.cumsum(np.r_[th[0], np.exp(th[1:K-1])])
    if family == "equi":
        return th[0] + np.exp(th[1])*np.arange(K-1)
    if family == "geom":
        t1, d, r = th[0], np.exp(th[1]), np.exp(th[2])
        j = np.arange(K-1)
        step = d*(r**j)                     # gap j->j+1
        return t1 + np.r_[0.0, np.cumsum(step[:-1])]
    raise ValueError(family)

def _binned(y, x, K, nbins):
    """Collapse (y, x) to <=nbins x-cells with category counts. Exact if unique x <= nbins."""
    xu_all = np.unique(x)
    if len(xu_all) <= nbins:
        idx = np.searchsorted(xu_all, x); xu = xu_all
    else:
        edges = np.unique(np.quantile(x, np.linspace(0, 1, nbins+1)[1:-1]))
        raw = np.searchsorted(edges, x)
        used, idx = np.unique(raw, return_inverse=True)
        xu = np.bincount(idx, weights=x)/np.bincount(idx)
    cnt = np.zeros((len(xu), K))
    np.add.at(cnt, (idx, y), 1.0)
    return xu, cnt

def _nll(th, family, K, xu, cnt):
    taus = _taus(family, th[:-1], K)
    eta = th[-1]*xu
    cum = np.empty((len(xu), K+1))
    cum[:, 0] = 0.0; cum[:, K] = 1.0
    cum[:, 1:K] = expit(taus[None, :] - eta[:, None])
    p = np.clip(np.diff(cum, axis=1), 1e-12, None)
    return -np.sum(cnt*np.log(p))

def _npar(family, K):
    return {"free": K, "equi": 3, "geom": 4}[family]

def fit_thresholds(S, x, family, K, cats, nbins=600, _cache={}):
    y = np.searchsorted(cats, S)
    x = np.asarray(x, float)
    key = (id(S), id(x), K, nbins)
    if key not in _cache:
        _cache.clear(); _cache[key] = _binned(y, x, K, nbins)
    xu, cnt = _cache[key]
    q = np.quantile(x, np.cumsum(np.bincount(y, minlength=K)/len(y))[:-1])
    b0 = 1.0/max(np.std(x), 1e-6)
    t0 = np.sort(q*b0)
    starts = []
    if family == "free":
        starts.append(np.r_[t0[0], np.log(np.maximum(np.diff(t0), 1e-3)), b0])
    elif family == "equi":
        starts.append(np.r_[t0[0], np.log(max(np.mean(np.diff(t0)), 1e-3)), b0])
    else:
        w = np.maximum(np.diff(t0), 1e-3)
        r0 = (w[-1]/w[0])**(1/max(len(w)-1, 1)) if len(w) > 1 else 1.0
        for rr in [r0, 1.0, 1.2, 1.5, 0.8, 2.0]:
            starts.append(np.r_[t0[0], np.log(w[0]), np.log(max(rr, 1e-3)), b0])
    best = None
    for s0 in starts:
        s = s0
        for meth in ("Nelder-Mead", "BFGS", "Nelder-Mead", "BFGS"):
            try:
                res = minimize(_nll, s, args=(family, K, xu, cnt), method=meth,
                               options=dict(maxiter=20000, maxfev=40000, xatol=1e-9, fatol=1e-9)
                               if meth == "Nelder-Mead" else dict(maxiter=5000))
            except Exception:
                break
            if np.isfinite(res.fun):
                s = res.x
                if best is None or res.fun < best.fun: best = res
    k = _npar(family, K)
    return dict(family=family, nll=best.fun, params=k, AIC=2*best.fun+2*k,
                theta=best.x, taus=_taus(family, best.x[:-1], K), beta=best.x[-1],
                r=(np.exp(best.x[2]) if family == "geom" else None))

def battery(S, x, label="", nbins=600):
    """S ascending rating; x log-stimulus, oriented so higher S <-> higher x."""
    S = np.asarray(S); x = np.asarray(x, float)
    ok = np.isfinite(x) & np.isfinite(S.astype(float))
    S, x = S[ok], x[ok]
    cats = np.unique(S); K = len(cats)
    mf, cats, cmean = mean_function_race(S, x)
    th = {f: fit_thresholds(S, x, f, K, cats, nbins=nbins) for f in ("free", "equi", "geom")}
    widths = np.diff(th["free"]["taus"])/abs(th["free"]["beta"])
    lr = 2*(th["equi"]["nll"] - th["free"]["nll"])
    return dict(label=label, n=len(S), K=K, cats=cats, cmean=cmean,
                counts=np.array([np.sum(S == c) for c in cats]),
                mf=mf, th=th, free_widths=widths,
                lr_equi_vs_free=lr, lr_df=K-3,
                r=th["geom"]["r"],
                dAIC_equi_minus_geom=th["equi"]["AIC"]-th["geom"]["AIC"])

def report(res):
    L = []
    L.append(f"=== {res['label']}   n={res['n']}  K={res['K']}")
    L.append(f"  category means of log-stimulus: " +
             ", ".join(f"{int(c)}:{m:.3f}(n={n})" for c, m, n in zip(res['cats'], res['cmean'], res['counts'])))
    d = np.diff(res['cmean'])
    L.append(f"  step sizes in log-stimulus:     " + ", ".join(f"{v:.3f}" for v in d))
    L.append(f"  step ratios (growth of steps):  " + ", ".join(f"{v:.3f}" for v in d[1:]/d[:-1]))
    L.append("  -- mean-function race (lower AIC better) --")
    for k, v in sorted(res['mf'].items(), key=lambda kv: kv[1]['AIC']):
        L.append(f"    {k:24s} p={v['params']:>2}  AIC={v['AIC']:11.1f}  R2obs={v['r2_obs']:.4f}  R2cat={v['r2_cat']:.4f}")
    L.append("  -- threshold tournament (anchored GRM) --")
    for k, v in sorted(res['th'].items(), key=lambda kv: kv[1]['AIC']):
        nm = {"geom": "geometric widths", "equi": "equidistant", "free": "flexible (free)"}[k]
        L.append(f"    {nm:24s} p={v['params']:>2}  AIC={v['AIC']:11.1f}" + (f"   r={v['r']:.4f}" if v['r'] else ""))
    L.append(f"  free widths (log-stimulus units): " + ", ".join(f"{v:.3f}" for v in res['free_widths']))
    L.append(f"  LR equidistant vs free: chi2={res['lr_equi_vs_free']:.1f} df={res['lr_df']}")
    L.append(f"  GEOMETRIC r = {res['r']:.4f}    dAIC(equi - geom) = {res['dAIC_equi_minus_geom']:.1f}")
    return "\n".join(L)
