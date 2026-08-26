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

---

## M1-T1 — Damage reporting passes the §3 gate, but reporting practice varies by 50 points

**Method.** All NOAA Storm Events detail files for 2020–2026 downloaded
(73 MB gzipped, **439,152 events**) and parsed. `DAMAGE_PROPERTY` and
`DAMAGE_CROPS` distinguish a blank field from an explicit zero, and the two are
counted separately throughout.

| | |
|---|---|
| Events | 439,152 |
| Damage field populated | 351,999 (**80.2%**) |
| Populated and greater than zero | 84,363 (19.2%) |
| **Populated but exactly zero** | **267,636 (60.9%)** |
| Blank — no figure at all | 87,153 (19.8%) |

**County-year completeness: 94.9%** (19,244 of 20,275 county-years with at least
one event carry a damage figure).

**Against the §3 threshold of 60% — PASS. Point estimates are permitted.**

### But reporting practice is not uniform, and the pattern is hostile

| Lowest | | Highest | |
|---|---|---|---|
| Colorado | **49.6%** | Rhode Island | 100.0% |
| Nebraska | 55.3% | Puerto Rico | 99.8% |
| South Carolina | 57.1% | Louisiana | 99.7% |
| Maine | 60.2% | Nevada | 99.4% |
| Oklahoma | 62.7% | Mississippi | 99.4% |
| Wyoming | 63.8% | Arizona | 99.3% |
| Kansas | 64.7% | Florida | 99.3% |

**A 50.4 point spread.** And the low-reporting states are Colorado, Nebraska,
Oklahoma and Kansas — hail and tornado country, which is exactly where the index
carries high expected loss.

**So the index will appear to over-predict in the states that report least, for
reasons that have nothing to do with the index.** Every state-level figure must
be published beside that state's reporting rate, and the national result must be
tested for sensitivity to it. This is recorded before any correlation has been
computed.

---

## M1-T2 — Two thirds of the damage is not county-coded, and the fix is free

This nearly ended the project, and it is the reason M1 exists.

**Only 54.1% of events, and 28.0% of dollars, carry a county FIPS.** The rest are
`CZ_TYPE='Z'` — National Weather Service forecast zones, which are not counties.

**The hazards that vanish are the expensive ones:**

| Event type | Damage | Share of all | County-coded |
|---|---|---|---|
| **Hurricane (Typhoon)** | $50.8 bn | **45.2%** | **0.0%** |
| Wildfire | $11.4 bn | 10.1% | 0.1% |
| Storm Surge/Tide | $5.2 bn | 4.6% | 0.0% |
| High Wind | $4.9 bn | 4.4% | 0.0% |
| Tropical Storm | $4.7 bn | 4.2% | 0.0% |
| Drought | $1.7 bn | 1.5% | 0.0% |

Against F0-T3: hurricane alone is **29.25% of the index's dollar value**, and
none of its realized damage is county-coded. Taken at face value this would have
pushed the testable share to roughly 26% — **below the 50% floor in
`PREREGISTRATION.md` §6, which would have killed the project.**

### The zone-to-county crosswalk, measured

NWS publishes a zone–county correlation file, free
(`weather.gov/source/gis/Shapefiles/County/bp16ap26.dbx`, 350 KB): 4,875 rows,
4,080 zones, 3,269 counties.

**89.8% of zones map to exactly one county** — median 1, mean 1.19, max 10. The
apportionment problem is far smaller than the zone coding implied.

| Of the $81.0 bn zone-coded damage | |
|---|---|
| Matched to the crosswalk | $50.5 bn (**62.3%**) |
| ... in single-county zones, no apportionment needed | $46.8 bn (**57.7%**) |
| ... in multi-county zones, apportionment required | $3.7 bn (4.6%) |
| **Unmatched zone key** | **$30.5 bn (37.7%)** |

**County-attributable damage rises from 28.0% to 72.9% of all dollars.**

Per hazard: hurricane 57.6% recovered (all single-county), tropical storm 88.6%,
wildfire 99.1%, drought 100%, coastal flood 95.5%, winter storm 89.3%, ice storm
63.3%. **High wind recovers only 8.7%** and is the worst case.

**§6 does not fire — conditional on using the crosswalk.** That step was not in
the pre-registration, and v1.1 adds it with its apportionment rule fixed before
any correlation is computed.

### Two things this leaves open

**$30.5 bn of zone damage does not match the crosswalk.** The file is an April
2026 snapshot and the events run from 2020; NWS renumbers zones, so stale
identifiers are the likely cause. Historical crosswalk versions exist and
retrieving them is M2 work. Until then the unmatched amount is **excluded and
published**, never silently dropped.

**Building this crosswalk is reproducing part of what SHELDUS does.** SHELDUS is
the index's own loss input, it is licensed, and apportioning NOAA zone events to
counties is a large part of what it sells. Doing it independently is legitimate —
and it means the apportionment rule is ours, not FEMA's, and must be stated
wherever it bears.

---

## M2-T1 — Name matching recovers the missing damage, and it was validated rather than assumed

**Method.** The 37.7% of zone damage that matched no zone key was diagnosed
before any fix was attempted. The cause is **zone renumbering**, confirmed: NOAA
codes Louisiana zone 41 as `CALCASIEU` in 2020, while the April 2026 crosswalk
maps Louisiana zones 1-254 to entirely different names.

The unmatched zone *names* are recoverable, though: `CALCASIEU`,
`LOWER LAFOURCHE`, `UPPER TERREBONNE` are Louisiana parishes split into
directional sub-zones. Stripping the qualifier resolves them.

**A name match is weaker evidence than an id match** — the same problem Downfall
recorded on `short_name` — so it was measured before it was used.

### The validation

126,549 events are resolvable by **both** id and name. Comparing the two:

| | |
|---|---|
| Name result overlaps id result | **99.48%** |
| Name result identical to id result | 98.35% |
| **Damage-weighted overlap** | **99.87%** |

The second pass reproduces the first almost exactly where both are available,
which is what licenses using it where only the second exists.

### What it recovers

| Method | Events | Damage | Share |
|---|---|---|---|
| County FIPS, direct | 237,786 | $31.45 bn | 28.0% |
| Zone id | 173,169 | $50.51 bn | 44.9% |
| **Zone name (new)** | **3,877** | **$20.45 bn** | **18.2%** |
| **Attributed** | **414,832** | **$102.4 bn** | **91.1%** |
| Unmatched | 24,319 | $10.06 bn | 8.9% |

**Attribution rises from 72.9% to 91.1% of all damage dollars.** Every row records
which pass produced it, so the join remains auditable.

0.14% of attributed damage carries an event type with no NRI hazard equivalent —
heavy rain, dense fog, funnel cloud, high surf — and is dropped rather than
forced into a category.

---

## M2-T2 — The testable share holds at 70.97%, and earthquake is simply absent

After the per-hazard out-of-sample boundary (§4.1): **70,580 county-year-hazard
rows, $63.97 bn of loss.**

| | Share of index EAL |
|---|---|
| Hazards with 100+ counties reporting out-of-sample loss | **70.97%** |
| Thin — tsunami, volcanic | 0.33% |
| **Absent — earthquake (27.04%), coastal flooding (1.67%)** | **28.71%** |

**Against the §6 / §11.1 threshold of 50% — PASS.**

**Earthquake has no out-of-sample rows at all.** NOAA Storm Events does not cover
earthquakes. F0-T3 predicted it would be untestable on timescale grounds; it is
in fact untestable on *instrument* grounds, which is a stronger statement. A
quarter of the index cannot be scored here by any means available.

---

## M2-T3 — A specification error, found by looking at heat waves

| Hazard | Out-of-sample counties | Realized damage | Index EAL share |
|---|---|---|---|
| Heat Wave | 1,431 | **$36,020** | 3.01% |
| Cold Wave | 2,219 | $77.1 M | 1.23% |

Heat waves appear in 1,431 counties and cause essentially **no property damage**.
That is not a data defect. Heat kills people; it does not flatten buildings.

The index's `EALT` is a **composite of building, population and agriculture**
consequence, with population loss converted to dollars. NOAA's
`DAMAGE_PROPERTY + DAMAGE_CROPS` measures **buildings and crops only**.

**Scoring `EALT` against property damage is a category error**, and it would have
made the index look badly wrong on precisely the hazards whose harm is counted in
lives. Comparing building-and-agriculture EAL against building-and-crop damage is
the like-for-like test.

`PREREGISTRATION.md` v1.2 fixes the comparison as **`{HAZ}_EALB + {HAZ}_EALA`
against `DAMAGE_PROPERTY + DAMAGE_CROPS`**, before any correlation is computed.
The population component is out of scope and said to be.
