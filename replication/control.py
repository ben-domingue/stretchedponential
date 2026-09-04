import csv, numpy as np, battery, prep, re
sub = prep.subtlex()
rows = list(csv.reader(open('glasgow.csv')))
hdr, sub_hdr = rows[0], rows[1]
# find FAM mean column
cols = {}
cur = None
for i,h in enumerate(hdr):
    if h.strip(): cur = h.strip()
    cols.setdefault(cur, []).append(i)
fam_M = cols['FAM'][0]; aoa_M = cols['AOA'][0]; cnc_M = cols['CNC'][0]
print("FAM col", fam_M, sub_hdr[fam_M])
W, F = [], []
for r in rows[2:]:
    if not r or not r[0].strip(): continue
    w = re.sub(r'\s*\(.*?\)\s*', '', r[0]).strip().lower()
    try: f = float(r[fam_M])
    except ValueError: continue
    if w in sub: W.append(w); F.append(f)
print("joined", len(W))
z = np.array([sub[w]['zipf'] for w in W])
cd = np.array([np.log10(sub[w]['cd']+1) for w in W])
F = np.array(F)
print("corr(FAM, Zipf) =", round(float(np.corrcoef(F, z)[0,1]),3))
S = np.clip(np.rint(F), 1, 7).astype(int)
print("cat counts", np.bincount(S))
res = battery.battery(S, z, "CONTROL Glasgow FAM (rounded item mean) x SUBTLEX-US Zipf")
print(battery.report(res))
res2 = battery.battery(S, cd, "CONTROL Glasgow FAM x log SUBTLEX-US contextual diversity")
print(battery.report(res2))
