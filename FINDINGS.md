# Findings

Recorded as they are established. Numbers here are measured, never quoted.

---

## F0-T1 — The index is obtainable, and its holdout is longer than its archive date

**Method.** OpenFEMA API queried live; NOAA Storm Events file listing retrieved;
the Datalumos archive of the National Risk Index downloaded and opened.

### What is reachable, free and keyless

| Source | Status |
|---|---|
| OpenFEMA API | **Verified.** NFIP claims **2,724,656** · HMA projects 56,347 · Public Assistance projects 847,356 · disaster declarations 70,249 · IA registrations 26,250,920 |
| NOAA Storm Events | **Verified.** HTTP 200, annual CSVs `d2020`–`d2026` |
| National Risk Index | **Not on the OpenFEMA API** (checked). Bulk download from `hazards.fema.gov`, mirrored on ArcGIS Hub and Datalumos |

### The Datalumos archive holds exactly one snapshot

| File | Size | Archived |
|---|---|---|
| `NRI_GDB_CensusTracts.zip` | 401.4 MB | **2025-02-07** |
| `NRI_GDB_Counties.zip` | 86.2 MB | 2025-02-07 |
| `NRI_GDB_States.zip` | 38.1 MB | 2025-02-07 |

One capture, not a version series. Read naively, that caps the out-of-sample
window at **February 2025 → mid-2026, about sixteen months.** Across three
thousand counties that is badly underpowered for hazards recurring on decade
timescales: a single hurricane season would dominate, and the test would measure
weather rather than the index.

### The publication date is not the boundary

The bundled metadata identifies the snapshot as **National Risk Index March 2023,
version 1.19.0**, revision date **2023-03-13**. FEMA's version documentation for
v1.19.0 gives the historic loss ratio as **SHELDUS Version 19.0, 1996–2019**.

**The honest boundary is the last event that fed the index, not the date the file
was written.** That is what F0-T2 establishes precisely, and it is not a single
date.

---

## F0-T2 — CORRECTION: the boundary is per-hazard, and F0-T1 got it wrong

**An earlier version of this document, committed 2026-08-26, stated two things
that are false.** Both are corrected here rather than edited away; the wrong
version stands in git history.

**Wrong claim 1: "the archived snapshot is not self-documenting."** It is. The
geodatabase carries a second layer, `NRI_HazardInfo`, stating the period of
record for every hazard. The error came from reading only the `.xml` and `.docx`
metadata files beside the geodatabase and never opening the geodatabase itself.

**Wrong claim 2: "the holdout begins 2020-01-01."** That is right for four
hazards and wrong for the other fourteen.

### What `NRI_HazardInfo` actually says

The index has **two** input periods per hazard, and they differ: an *annualized
frequency* window, and the *historic loss ratio* window (SHELDUS 1996–2019).

| Hazard | Frequency period | Model | Binding end | Holdout starts |
|---|---|---|---|---|
| Lightning | 1991–**2012** | Frequency | 2019 | **2020** |
| Ice Storm | 1946–**2014** | Frequency | 2019 | **2020** |
| Avalanche | 1960–**2019** | Frequency | 2019 | **2020** |
| Riverine Flooding | 1996–**2019** | Frequency | 2019 | **2020** |
| Cold Wave, Heat Wave, Winter Weather | 2005–2021 | Frequency | 2021 | **2022** |
| Drought | 2000–2021 | Frequency | 2021 | **2022** |
| Hail, Strong Wind | 1986–2021 | Frequency | 2021 | **2022** |
| Landslide | 2010–2021 | Frequency | 2021 | **2022** |
| Tornado | 1950–2021 | Frequency | 2021 | **2022** |
| Tsunami | 1800–2021 | Frequency | 2021 | **2022** |
| Hurricane | East 1851–2021 / West 1949–2021 | Frequency | 2021 | **2022** |
| Earthquake | 2021 dataset | **Probability** | 2021 | **2022** |
| Wildfire | 2021 dataset | **Probability** | 2021 | **2022** |
| Volcanic Activity | 9310BC–**2022** | Frequency | 2022 | **2023** |
| Coastal Flooding | **N/A — "various, see documentation"** | Frequency | **unknown** | **excluded** |

**The binding boundary is the later of the two input windows**, hazard by hazard.
A single global holdout date would either leak index inputs into the scoring
window or discard years of usable outcome data, depending on which date was
chosen.

**Coastal Flooding declares no period at all** and is therefore excluded from the
primary analysis rather than assigned a guessed boundary.

Earthquake and Wildfire are **probability models, not frequency counts over a
window**, and are grounded differently from the other sixteen.

---

## F0-T3 — A quarter of the index cannot be tested on any feasible holdout

**Method.** `NRI_Counties` layer read in full: **3,231 counties, 466 fields, 56
states and territories.** No nulls in `EAL_VALT`, `EAL_VALB`, `POPULATION` or
`BUILDVALUE`; `RISK_SCORE` is null for 88 counties.

National Expected Annual Loss totals **$76.72 billion per year**.

### Where that figure comes from

| Hazard | Total EAL | Share | Counties with EAL > 0 |
|---|---|---|---|
| Hurricane | $22.44 bn | **29.25%** | 2,308 |
| **Earthquake** | **$20.74 bn** | **27.04%** | 3,229 |
| Tornado | $10.11 bn | 13.18% | 3,224 |
| Riverine Flooding | $6.75 bn | 8.80% | 3,164 |
| Wildfire | $3.48 bn | 4.54% | 3,142 |
| Heat Wave | $2.31 bn | 3.01% | 2,604 |
| Strong Wind | $2.24 bn | 2.91% | 3,187 |
| Hail | $2.12 bn | 2.77% | 3,206 |
| Drought | $1.67 bn | 2.17% | 2,681 |
| Coastal Flooding | $1.28 bn | 1.67% | 479 |
| Cold Wave | $0.94 bn | 1.23% | 2,300 |
| Lightning | $0.81 bn | 1.06% | 3,108 |
| Ice Storm | $0.76 bn | 0.99% | 3,002 |
| Winter Weather | $0.49 bn | 0.64% | 3,094 |
| Volcanic Activity | $0.25 bn | 0.32% | 77 |
| Landslide | $0.24 bn | 0.31% | 3,142 |
| Avalanche | $0.08 bn | 0.11% | 208 |
| Tsunami | $0.004 bn | 0.01% | 80 |

### The limitation this creates, and it is the central one

**Earthquake is 27.04% of the index's dollar value.** Earthquake losses arrive on
century timescales. A four-to-six-year holdout will contain almost none, so **no
amount of care makes this window capable of testing that quarter of the index.**
The same applies to volcanic activity, tsunami and avalanche.

| | Share of national EAL |
|---|---|
| Earthquake + Volcanic + Tsunami + Avalanche | **27.48%** |
| Coastal Flooding (no declared period) | 1.67% |
| **Untestable or excluded** | **29.15%** |
| **Testable on this window** | **70.85%** |

**The project therefore cannot validate the National Risk Index.** It can test
the 70.85% of its dollar value driven by hazards that actually recur inside a
decade, and it must say exactly that, in those words, wherever a headline appears.

A test that quietly reported "the index predicts well" while a quarter of it was
never exercised would be the most publishable wrong answer available here.

---

## Consequences for the build

- Counties geodatabase: **104 MB unzipped, 55 internal files, 466 fields**.
  Per-hazard EAL is `{HAZ}_EALB` (building), `{HAZ}_EALT` (total), `{HAZ}_ALRB`
  (rate); composites are `EAL_VALB` and `EAL_VALT`.
- Read with **`pyogrio.read_arrow`** — `read_dataframe` requires geopandas, which
  is not installed and is not needed. `pyarrow` and `pandas` suffice.
- 401 MB of tract data is gitignored. Aggregates are committed; raw is not.
- Nothing in the stack costs anything.

### A circularity that has to be declared, not solved

**SHELDUS is itself built largely from NOAA Storm Data.** Scoring the index
against NOAA Storm Events is therefore *not* an independent measurement — it is
the same instrument, read over a later period.

For a temporal holdout that is acceptable and arguably correct: holding the
instrument fixed isolates prediction from measurement disagreement. **But it must
be stated wherever a NOAA-based figure appears**, and it is why NFIP claims
matter — insurance claims are a genuinely separate instrument, and give an
independent read for flood specifically.

**SHELDUS itself is licensed and is not free.** It is therefore never used here,
which is fortunate: using the index's own input as the outcome would be circular
in the way that matters.
