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

### The publication date is not the boundary

The index is computed from a fixed historical record, and **that record ends
years before the file is published.**

FEMA's documentation gives the loss input as **SHELDUS**, and the period of
record as **1996–2019** for versions up to and including the March 2023 release.
The December 2025 release (v1.20) extends it **through 2023**.

**So the honest out-of-sample boundary is the last event that fed the index, not
the date the file was written.** If the archived February 2025 snapshot carries
the 1996–2019 record — which its date makes likely but does not prove — then
losses from **2020 through 2026 are genuinely out-of-sample: roughly seven
years, not sixteen months.**

**Open, and blocking §5 of the pre-registration:** which SHELDUS version the
archived snapshot used. It is stated in the version documentation bundled with
the download. **No holdout window is fixed until that is read**, and it is task
one.

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

- Files are geodatabases in zips; reading them needs `geopandas`/`fiona`
  (free). FEMA also publishes CSV tables of the same content, which avoid the
  GDAL dependency and should be preferred if reachable.
- 401 MB of tract data is gitignored. Aggregates are committed; raw is not.
- Nothing in the stack costs anything.
