# Findings

Recorded as they are established. Numbers here are measured, never quoted.

---

## F0-T1 — The index is obtainable, and its holdout is five times longer than it looks

**Method.** OpenFEMA API queried live; NOAA Storm Events file listing retrieved;
the Datalumos archive of the National Risk Index inspected; FEMA version
documentation searched for the period of record of the loss inputs.

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
window at **February 2025 → mid-2026 — about sixteen months.** Across 3,144
counties that is badly underpowered for hazards that recur on decade timescales:
a single hurricane season would dominate the result, and the test would measure
weather rather than the index.

### The publication date is not the boundary — confirmed

The index is computed from a fixed historical record, and **that record ends
years before the file is published.**

The bundled metadata identifies the snapshot as **National Risk Index March 2023,
version 1.19.0**, revision date **2023-03-13**. It does **not** state the period
of record — that lives in a separate FEMA document, which is a finding in its own
right: **the archived snapshot is not self-documenting**, and anyone reading it
alone would have no way to know what window it was fitted on.

FEMA's version documentation for v1.19.0 states the historic loss ratio uses
**SHELDUS Version 19.0, covering 1996–2019**, with tornado frequency, exposure
and loss ratio drawn from **1986–2019**.

| | |
|---|---|
| Snapshot | v1.19.0, published 2023-03-13, archived 2025-02-07 |
| **Last event feeding the index** | **2019-12-31** |
| Outcome data available to | 2026 (NOAA Storm Events `d2026`) |
| **Out-of-sample window** | **2020-01-01 onward — about six and a half years** |

**The naive reading would have given sixteen months and an underpowered test.**
The honest boundary is the last event that fed the index, and it is five times
longer.

**Fixed here before any outcome data is downloaded:** the holdout begins
**2020-01-01**. Nothing dated earlier may enter the scoring window, for any
hazard, and tornado is *not* given an earlier start despite its longer input
record — the boundary is the end of the record, which is 2019 for both.

### A circularity that has to be declared, not solved

**SHELDUS is itself built largely from NOAA Storm Data.** Scoring the index
against NOAA Storm Events is therefore *not* an independent measurement — it is
the same instrument, read over a later period.

For a temporal holdout that is acceptable and arguably correct: holding the
instrument fixed isolates prediction from measurement disagreement. **But it must
be stated wherever a NOAA-based figure appears**, and it is the reason NFIP
claims matter — insurance claims are a genuinely separate instrument, and give an
independent read for flood specifically.

**SHELDUS itself is licensed and is not free.** It is therefore never used here,
which is fortunate: using the index's own input as the outcome would be circular
in the way that matters.

### Consequences for the build

- The counties geodatabase is **104 MB unzipped, 55 internal files, 479 fields**.
  Per-hazard Expected Annual Loss is exposed as `{HAZ}_EALB` (building),
  `{HAZ}_EALT` (total) and `{HAZ}_ALRB` (rate), with composites `EAL_VALB` and
  `EAL_VALT`.
- **No geospatial reader is installed** — `geopandas`, `fiona`, `pyogrio` and
  `osgeo` are all absent; `pandas` and `pyarrow` are present. One free
  dependency (`pyogrio`) or the CSV distribution of the same tables resolves it.
- 401 MB of tract data is gitignored. Aggregates are committed; raw is not.
- Nothing in the stack costs anything.
