# IRW × stretched-exponential — replication attempt

Run 2026-09-04, following the scouting run in `../README.md`. Report published at
<https://claude.ai/code/artifact/1038d007-df5e-4073-a078-eb97e95c3479>
(republish `report.html` to that URL to update in place).

## Headline

| Battery | Rating (oriented so it ascends with frequency) | n | K | r |
|---|---|---:|---:|---:|
| **Glasgow FAM × SUBTLEX Zipf** (control) | familiarity, rounded item mean | 5,515 | 5 | **1.474** |
| spelling2pronounce, item mean | ease = 7 − difficulty, rounded item mean | 22,791 | 5 | 1.388 |
| **spelling2pronounce, individual** | ease, single ratings | 604,265 | 6 | **0.972** |
| kalimahnorms (Arabic) | earliness = 8 − AoA | 65,051 | 7 | 1.209 |
| Forthmann-2024 | conventionality = 6 − creative quality | 14,028 | 5 | 1.189 |

Per-rater (366 raters, ≥200 words each): median r = 1.008, IQR [0.889, 1.111], 52.7% > 1.

1. **The battery is validated.** Simulation recovers r = 1.008 / 1.237 / 1.403 for true
   1.00 / 1.24 / 1.41. Re-run on Chituc's own Glasgow battery it returns r = 1.474
   (1.363 keeping sparse cells) against his published 1.409.
2. **Aggregation manufactures most of it.** The fitted individual-level model has r = 0.972.
   Simulate from it (word random effect σ = 0.767, matching the observed dispersion of word
   means), average over each word's real rater count, round — and the aggregate battery reports
   r = 1.285 [1.275, 1.300] vs the observed 1.388. ~77% of ln r is made by the aggregation step.
   The same test on Glasgow gives only 1.087 vs 1.474, so **Chituc's result survives its null;
   the IRW one does not.**
3. **The widening follows the stimulus, not the scale.** In all three IRW batteries the rated
   attribute runs against frequency (harder / later-acquired / more creative = rarer), and the
   widening lands at the high-frequency end every time — the *bottom* of each scale as
   administered. Glasgow cannot separate these because familiarity and frequency co-vary.
4. **The anchor control is uninformative on word data.** Rank/CDF beats log magnitude by
   ΔAIC 6.7 (Glasgow) and 70.2 (spelling individual) — opposite to Chituc's IGN result — but
   log Zipf and the normal quantile of frequency rank are near-linearly related, so the test
   has no power here. Fitted r is identical under both anchors.

## Files

| File | What it is |
|---|---|
| `battery.py` | the battery: mean-function race (SE / quadratic / linear / power / saturated) + threshold tournament (free / equidistant / geometric widths), binned ordinal-logistic likelihood |
| `anchors.py` | log-magnitude vs rank/CDF anchor race |
| `prep.py` | SUBTLEX-US loader, IRW table readers |
| `sim.py` | estimator validation on synthetic r = 1.00 / 1.24 / 1.41 |
| `control.py` | Glasgow Norms positive control |
| `agg_artifact2.py` | calibrated average-then-round null, spelling2pronounce |
| `glasgow_null.py` | Fechnerian null, Glasgow Norms |
| `run_*.py` | the individual battery runs; `*.out` are their captured outputs |
| `final.py` | one pass over everything → `data/results.json` |
| `fetch.R`, `probe7.R` | `irw_fetch` for the IRW tables; schema probe for further candidates |
| `data/results.json` | every number in the report |
| `report.html` | the published report |

## Inputs (not committed)

- IRW via the `irw` R package v1.1.2: `spelling2pronounce_edwards2023`,
  `kalimahnorms_alzahrani_2025`, `Forthmann-2024-creative_quality`.
- SUBTLEX-US 74,286-word list:
  <https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexus/subtlexus2.zip>
  (match rate against the 23,282 IRW word strings: 97.9%).
- Glasgow Norms (Scott et al. 2019) BRM supplement:
  `https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-018-1099-3/MediaObjects/13428_2018_1099_MOESM2_ESM.csv`

Seed 42 throughout. Threshold likelihood is evaluated on x binned into 600 equal-count cells;
on the simulation check this moves recovered r in the fourth decimal.

## Next

The clean individual-level test of the *exact* Glasgow construct is a familiarity rating with
individual responses. Two IRW tables have one, both needing an external exposure count:
`emoji_scheffler_2024` (107 emoji, K = 101, 153 raters) and `famous_melodies`
(109 melodies, K = 9, 397 raters). Together they also span the K sweep the page predicts
should drive r → 1.
