import csv, collections, re, numpy as np, prep, anchors
sub = prep.subtlex()

# 1. CONTROL: Glasgow FAM
rows = list(csv.reader(open('glasgow.csv')))
W,F=[],[]
for r in rows[2:]:
    if not r or not r[0].strip(): continue
    w = re.sub(r'\s*\(.*?\)\s*','',r[0]).strip().lower()
    try: f=float(r[17])
    except ValueError: continue
    if w in sub: W.append(w); F.append(f)
z=np.array([sub[w]['zipf'] for w in W]); S=np.clip(np.rint(F),1,7).astype(int)
anchors.anchor_race(S, z, "CONTROL Glasgow FAM x Zipf  (S ascends with frequency)")

# 2. spelling2pronounce, individual + item-mean
srows = prep.spelling2pronounce()
kept = {w for w,_,_ in srows if w.strip().lower() in sub}
zf = {w: sub[w.strip().lower()]['zipf'] for w in kept}
byw = collections.defaultdict(list)
for w,r,rt in srows:
    if w in kept: byw[w].append(r)
ws = sorted(byw)
Sa = np.clip(np.rint([np.mean(byw[w]) for w in ws]),1,6).astype(int)
xa = np.array([zf[w] for w in ws])
m = Sa <= 5
anchors.anchor_race(7-Sa[m], xa[m], "spelling2pronounce item-mean EASE(7-difficulty) x Zipf  (S ascends with frequency)")
Si = np.array([r for w,r,_ in srows if w in kept])
xi = np.array([zf[w] for w,r,_ in srows if w in kept])
anchors.anchor_race(7-Si, xi, "spelling2pronounce INDIVIDUAL ease x Zipf  (S ascends with frequency)")

# 3. kalimah aoa (reversed so S ascends with frequency)
kr=[r for r in csv.DictReader(open('kalimahnorms_alzahrani_2025.csv'))
    if r['cov_frequency'] not in ('','NA') and r['item']=='aoa' and r['resp'] not in ('','NA')]
S=np.array([int(float(r['resp'])) for r in kr]); x=np.array([np.log10(float(r['cov_frequency'])) for r in kr])
mm=S>0
anchors.anchor_race(8-S[mm], x[mm], "kalimah EARLY-acquired (8-aoa) x log freq  (S ascends with frequency)")

# 4. Forthmann (reversed)
fr=[r for r in csv.DictReader(open('Forthmann-2024-creative_quality.csv'))
    if r['itemcov_frequency'] not in ('','NA') and r['resp'] not in ('','NA')]
S=np.array([int(float(r['resp'])) for r in fr]); x=np.array([np.log10(float(r['itemcov_frequency'])) for r in fr])
anchors.anchor_race(6-S, x, "Forthmann UNoriginality (6-quality) x log idea freq  (S ascends with frequency)")
