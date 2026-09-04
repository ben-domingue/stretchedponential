import csv, collections, numpy as np, json, battery, prep
sub = prep.subtlex()
rows = prep.spelling2pronounce()
print("responses:", len(rows))
byword = collections.defaultdict(list)
for w,r,rt in rows: byword[w].append(r)
kept = {w for w in byword if w.strip().lower() in sub}
print("words:", len(byword), "matched:", len(kept))
zipf = {w: sub[w.strip().lower()]['zipf'] for w in kept}
cdv  = {w: np.log10(sub[w.strip().lower()]['cd']+1) for w in kept}

res = {}
# --- A. aggregate battery (Glasgow analogue): rounded item mean difficulty
words = sorted(kept)
mean_diff = np.array([np.mean(byword[w]) for w in words])
S_agg = np.clip(np.rint(mean_diff), 1, 6).astype(int)
x_agg = -np.array([zipf[w] for w in words])          # rarity = -Zipf, ascends with difficulty
print("\ncorr(mean difficulty, Zipf) =", np.corrcoef(mean_diff, [zipf[w] for w in words])[0,1].round(3))
res['agg'] = battery.battery(S_agg, x_agg, "spelling2pronounce | rounded item-mean difficulty x (-)SUBTLEX-US Zipf")
print(battery.report(res['agg']))

# --- A'. robustness: contextual diversity
res['agg_cd'] = battery.battery(S_agg, -np.array([cdv[w] for w in words]),
                                "spelling2pronounce | rounded item-mean difficulty x (-)log contextual diversity")
print(battery.report(res['agg_cd']))

# --- B. individual-level battery (the new bit)
Si = np.array([r for w,r,rt in rows if w in kept])
xi = -np.array([zipf[w] for w,r,rt in rows if w in kept])
res['ind'] = battery.battery(Si, xi, "spelling2pronounce | INDIVIDUAL ratings x (-)SUBTLEX-US Zipf")
print(battery.report(res['ind']))

np.save("spell_cache.npy", {"words":words,"S_agg":S_agg,"x_agg":x_agg}, allow_pickle=True)
import pickle; pickle.dump(res, open("res_spell.pkl","wb"))

# --- C. exclusion funnel: drop categories with < 0.5% of words (Vlad's IGN 5-10 analogue)
import numpy as np
cnt = np.bincount(S_agg, minlength=7)
keep_cats = [c for c in range(1,7) if cnt[c] >= 0.005*len(S_agg)]
m = np.isin(S_agg, keep_cats)
print("\nexclusion funnel keeps categories", keep_cats, "->", m.sum(), "words")
res['agg_trim'] = battery.battery(S_agg[m], x_agg[m],
    f"spelling2pronounce | rounded item-mean difficulty {keep_cats[0]}-{keep_cats[-1]} x (-)SUBTLEX-US Zipf")
print(battery.report(res['agg_trim']))

# --- D. per-rater stability (raters with >=200 ratings)
import collections
byr = collections.defaultdict(list)
zl = {w: zipf[w] for w in kept}
for w,r,rt in rows:
    if w in kept: byr[rt].append((r, -zl[w]))
big = sorted([rt for rt in byr if len(byr[rt]) >= 200]); import random; random.Random(42).shuffle(big); big = big[:400]
print(f"\nper-rater: {len(big)} raters with >=200 rated words")
rs = []
for rt in big:
    Sr = np.array([a for a,b in byr[rt]]); xr = np.array([b for a,b in byr[rt]])
    if len(np.unique(Sr)) < 4: continue
    try: rs.append(battery.battery(Sr, xr, "", nbins=200)['r'])
    except Exception: pass
rs = np.array(rs); rs = rs[np.isfinite(rs) & (rs > 0.2) & (rs < 5)]
print(f"per-rater r: n={len(rs)} median={np.median(rs):.3f} IQR=[{np.percentile(rs,25):.3f},{np.percentile(rs,75):.3f}] frac>1: {np.mean(rs>1):.3f}")
np.save("per_rater_r.npy", rs)
import pickle; pickle.dump(res, open("res_spell.pkl","wb"))
