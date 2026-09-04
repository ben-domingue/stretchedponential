import csv, numpy as np, collections

def subtlex():
    d={}
    with open('SUBTLEXus74286wordstextversion.txt') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            w=row['Word'].strip().lower()
            if w in d: continue
            d[w]=dict(zipf=np.log10(float(row['SUBTLWF']))+3.0,
                      cd=float(row['CDcount']))
    return d

def spelling2pronounce():
    """id = word, item = 'difficulty', resp 1-6, rater = person."""
    S=collections.defaultdict(list)
    rows=[]
    with open('spelling2pronounce_edwards2023.csv') as f:
        for row in csv.DictReader(f):
            if row['resp'] in ('NA',''): continue
            rows.append((row['id'], int(float(row['resp'])), row['rater']))
    return rows
