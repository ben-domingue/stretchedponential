# IRW × stretched-exponential scouting run

Scouting the Item Response Warehouse for datasets that can test the
geometric-category-width law in Vlad Chituc's page,
<https://vladchituc.com/s/stretched-exponential.html>.

Run 2026-08-27 against IRW metadata (3,648 tables) and live `irw` R package
probes (v1.0.1). Source metadata: `irw/src/metadata/metadata.csv`.

## The claim being tested

An ordinal rating scale, treated as a categorization of an objective stimulus Φ
measured in log-stimulus space, has category boundaries that widen by a roughly
constant factor r > 1 per step. Equivalently, on category means:

    log Φ = c + A · exp(β · S)          β = ln r

Fitted alternatives it has to beat: equidistant (Fechnerian, r = 1) spacing,
and a power law in raw Φ. Published r values: IGN 1.234–1.269, stellar
magnitudes 1.173, Glasgow word familiarity 1.409.

## The filter

Three ingredients, all at once:

1. an ordinal rating S with K ≥ 5 categories;
2. **an objective, ratio-scaled Φ attached to the rated object** — the binding
   constraint, and what decides the whole shortlist;
3. enough rated objects (for thresholds) and raters per object (for per-rater r).

Ingredient 2 fails for a normal IRW table, where `item` is a questionnaire item
and `id` is a person. Only two structures supply it:

- the **29 tables with a `rater` column** where `id` is a stimulus →
  `rater_tables.csv`
- the **41 tables carrying `itemcov_*` fields**, a few of which hold a usable Φ
  in the table itself → `itemcov_inventory.csv`

## Files

| File | What it is |
|---|---|
| `scouting_report.html` | The full report. Published at <https://claude.ai/code/artifact/2ac54beb-21ac-459e-a980-01e0c086670f> — republish this file to that URL to update in place. |
| `rater_tables.csv` | All 29 rater-structured tables: K, item/object counts, response totals, full variable list. Sorted by n_responses. |
| `itemcov_inventory.csv` | All 42 `itemcov_*` field names across the 41 tables that carry them, with the tables for each. |
| `n_categories_distribution.csv` | Tables per K across the warehouse (K = 0 … 1,152). Supports the K-sweep argument below. |
| `probes/probe*.R` | The live schema probes actually run: column lists, `id`/`item`/`rater` cardinalities, response ranges, sample values for 34 candidate tables. |
| `probes/probe*.out` | Their captured output. `probe6` was run in the foreground and its output was not captured — rerun the script to regenerate. |

## Shortlist

**Tier 1 — ready now**

| Table | Objects | Raters | K | Φ |
|---|---|---|---|---|
| `spelling2pronounce_edwards2023` | 23,282 word strings | 2,515 | 6 | SUBTLEX-UK/US Zipf frequency (join on the word) |
| `famous_melodies` | 109 melodies | 397 | 9 | Objective exposure: chart / streaming counts |
| `Forthmann-2024-creative_quality` | 3,719 ideas | 3 | 5 | `itemcov_frequency` — **in table** |
| `Ellipse_Corssley_2024` | 8,890 essays | 27 | 6 | Essay length from the public ELLIPSE corpus |
| `det_naismith_2023` | 573 essays | 2 human + 1 machine | — | `itemcov_length_characters` — **in table** |

**Recommended first move.** `spelling2pronounce_edwards2023` × SUBTLEX. Cleanest
join in the warehouse, and individual-level — which patches the page's own
standing caveat that its word-familiarity battery is aggregate (item means over
raters) only. 2,515 raters also supports the per-rater stability check that the
stellar section runs on 14 observers. Unverified prerequisite: the match rate of
the 23,282 word strings against a SUBTLEX entry.

Tier 2 candidates and their catches are in `scouting_report.html`.

## Why the IRW, rather than a fourth dataset

1. **Individual-level ratings at scale** — retires the aggregate-level caveat.
2. **A sweep across K** — β = 1/(kγ) predicts r → 1 as the scale gets finer.
   Frequency-anchored tables sit at K = 6 (`spelling2pronounce`), K = 9
   (`famous_melodies`) and K = 101 (`emoji_scheffler_2024`) with stimulus type
   roughly fixed. See `n_categories_distribution.csv`.
3. **Same stimuli, many rating dimensions** — `fractals_rating` 7,
   `Ellipse_Corssley_2024` 8, `famous_melodies` and `emoji_scheffler_2024` 5
   each. Separates "r is a property of report scales" from "r tracks the
   construct".
4. **Range vs. frequency (Parducci) across corpora** — different tables present
   very different stimulus distributions to raters.

## Ruled out

- `concretewords` — the `item` column holds Qualtrics response hashes, not words.
- `klatt_2016_speed_estimation` — only two objective speeds (50, 55 km/h).
- `mentalrotation_wolf_2024` — has `itemcov_angle`, but 4 levels and binary resp.
- `roar_lexical`, `spalex_aguasvivas_2020` — binary accuracy, not ratings.
- `amatus_cipora_2024_arithmetic`, `himmelstein-*` — same, dichotomous.
- `allen_2025_delaydiscount` — objective amounts/delays in item text, but binary choice.
- Most of the 29 rater tables (`de_vries_2022_hexaco_other`,
  `socialstereotype_hughes_2025_*`, `hpwt_bayona_2025_jobperformance`) are
  people rating **people** — no objective Φ for the rated object.
