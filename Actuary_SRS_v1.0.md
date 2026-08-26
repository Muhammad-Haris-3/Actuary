# Actuary — Software Requirements Specification v1.0

**Project:** Actuary — scoring a federal risk index against the losses that landed
**Author:** Muhammad Haris Khokhar
**Date:** 2026-08-26
**Status:** Approved for M2

---

## 1. Introduction

### 1.1 Purpose

FEMA publishes a National Risk Index scoring every US county and census tract for
**Expected Annual Loss** from 18 natural hazards. It carries a dollar figure —
**$76.72 bn/yr** nationally — and it feeds BRIC grant scoring, state hazard
mitigation plans, and Community Disaster Resilience Zone designations.

**FEMA's own documentation states the index is not intended to predict the amount
of damage a community will experience.** It is a *relative* assessment built from
historical losses and smoothed.

So a number that disclaims prediction directs money. Actuary asks whether it
predicts, out-of-sample in time, for the hazards that recur often enough to be
observable.

### 1.2 What makes this different from Headway, Groundtruth and Downfall

**Headway** is the closest sibling: both are referee projects, scoring someone
else's published claims rather than making a forecast. The difference is what is
being refereed. Headway grades predictions the MBTA issues continuously and which
resolve in minutes. **Actuary grades one number, published once, whose subject
matter resolves over decades — and that asymmetry is the project's central
difficulty, not an incidental detail.**

**Groundtruth** marks an observational estimate against a randomised trial that
already measured the answer. Actuary has no trial. Its ground truth is what
actually happened, measured by an instrument that is itself imperfect and
partially shared with the thing being tested (§3.2).

**Downfall** is about demand that goes unrecorded. Actuary is about **loss that is
recorded inconsistently** — 50.4 points of variation between states — and the
project spends more effort characterising its own outcome measure than scoring
the index against it.

Unlike every previous project, **Actuary does not collect its own data.** Both
sides already exist. Its contribution is the boundary between them: which years
may be scored, at what geography, with what excluded.

### 1.3 Scope

**In scope:** ingestion of the National Risk Index March 2023 snapshot and NOAA
Storm Events 2020–2026; zone-to-county attribution; measurement of reporting
completeness; per-hazard out-of-sample scoring of Expected Annual Loss against
realized property damage; NFIP claims as an independent read for flood; naive
reference predictors; a public site; a decision memo.

**Out of scope:** the social vulnerability and community resilience components;
any claim about grant allocation; any policy recommendation; any index other than
v1.19.0; anything requiring paid data or paid infrastructure.

### 1.4 Definitions

| Term | Meaning |
|---|---|
| **EAL** | Expected Annual Loss — the index's dollar estimate of annual damage, per county, per hazard |
| **Binding boundary** | The later of a hazard's frequency window and its SHELDUS loss window. The last year that fed the index for that hazard |
| **Out-of-sample** | A year strictly after a hazard's binding boundary |
| **Realized loss** | `DAMAGE_PROPERTY` + `DAMAGE_CROPS` from NOAA Storm Events, attributed to a county |
| **Zone** | An NWS forecast area. 45.9% of events and 72.0% of damage dollars are coded to zones, not counties |
| **Reporting completeness** | Share of county-years with at least one event that carry any damage figure |
| **Testable share** | Share of the index's national EAL attributable to hazards that can be exercised on the available window and geography |

### 1.5 Intended audience

Hiring managers and technical reviewers primarily. Sections 2, 3 and the decision
memo are written for a reader with no statistical background; sections 6 onward
are written so an independent party can reproduce every number.

---

## 2. Business context and problem statement

### 2.1 Context

After a disaster, the question of where mitigation money should have gone is
asked with hindsight. Before one, it is answered with an index.

The National Risk Index is the most widely used such answer in the United States.
It is free, it is granular, and it looks authoritative: a dollar figure per
county. It is also, by FEMA's own account, not a prediction — a caveat that lives
in a technical PDF while the number lives in grant scoring criteria.

### 2.2 Problem statement

> A federal index assigns every US county an expected annual dollar loss, and
> directs money accordingly. No published study checks whether those dollars land
> where the index says they will.

### 2.3 Primary questions

| # | Question | Method |
|---|---|---|
| BQ-1 | **Can realized loss even be measured?** Reporting completeness, and its variation between states | Descriptive, M1 — **answered** |
| BQ-2 | Can zone-coded damage be attributed to counties without distorting it? | Crosswalk, M2 |
| BQ-3 | **Does EAL rank counties by realized loss, out-of-sample, per hazard?** | Spearman, bootstrapped by state |
| BQ-4 | Does it beat naive extrapolation of past loss? | Reference predictors, §5 of the pre-registration |
| BQ-5 | Is any apparent skill explained by state reporting practice rather than risk? | Robustness to reporting rate |
| BQ-6 | Do NOAA and NFIP agree for flood? | Two instruments, one hazard |

### 2.4 Success criteria

| # | Criterion | Threshold |
|---|---|---|
| SC-1 | Reporting completeness measured before any correlation | ≥ 60%, or results reported as bounded — **met, 94.9%** |
| SC-2 | Testable share after all exclusions | ≥ 50%, published |
| SC-3 | Per-hazard results, never a single national average | Always |
| SC-4 | Every figure beside its reference predictors | Always |
| SC-5 | Out-of-sample boundary respected per hazard | No hazard scored on a year that fed it |
| SC-6 | Cost | Zero. Free and open sources only |
| SC-7 | Legibility | A non-technical reader can state the finding from the memo alone |

---

## 3. Feasibility study

Measured 2026-08-26. Full record in `FINDINGS.md`.

| Factor | Measured |
|---|---|
| Index snapshot | v1.19.0, March 2023, **3,231 counties, 466 fields** |
| National EAL | **$76.72 bn/yr** |
| Concentration | Hurricane 29.25%, Earthquake 27.04%, Tornado 13.18%, Riverine Flooding 8.80% |
| Binding boundaries | Per hazard: 2019 (×4), 2021 (×12), 2022 (×1), undeclared (×1) |
| NOAA events, 2020–2026 | **439,152** |
| Damage field populated | 80.2% of events |
| County-year completeness | **94.9%** |
| Interstate reporting spread | **50.4 points** |
| Damage carrying a county FIPS | **28.0%** |
| After zone crosswalk | **72.9%** |
| Cost | Zero |

### 3.1 Principal risk to validity

**The index cannot be validated, and the project must never imply that it has
been.**

Earthquake is 27.04% of the index's dollar value and arrives on century
timescales. With volcanic activity, tsunami and avalanche, **27.48% of the index
cannot be exercised by any holdout available here**; coastal flooding adds 1.67%
with no declared period of record.

This is the analogue of Headway's arrival-timestamp risk — the measurement
limitation that decides what may be claimed — and it is handled the same way: the
testable share is published beside every headline, in words, and §2 of the
pre-registration forbids the sentence that would misread it.

**A result reading "the index predicts well" while a quarter of it was never
exercised is the most publishable wrong answer available here.**

### 3.2 Second risk: the outcome instrument is partly the index's own input

SHELDUS, the index's historic loss input, is built largely from NOAA Storm Data.
Scoring the index against NOAA Storm Events is therefore **not an independent
measurement** — it is the same instrument read over a later period.

For a temporal holdout this is acceptable and arguably correct: holding the
instrument fixed isolates prediction from measurement disagreement. It is stated
wherever a NOAA figure appears, and it is why NFIP claims are carried as a
separate, genuinely independent read for flood.

### 3.3 Third risk: reporting practice will masquerade as risk

Damage reporting varies **50.4 points** between states, and the worst reporters —
Colorado 49.6%, Nebraska 55.3%, Oklahoma 62.7%, Kansas 64.7% — are hail and
tornado country, where the index carries high expected loss.

**The index will appear to over-predict exactly where damage is least recorded.**
BQ-5 exists for this, and §6 of the pre-registration makes it a kill criterion:
if skill is not robust to controlling for reporting rate, the finding is about
NOAA rather than FEMA and is published as such.

### 3.4 Fourth risk: the attribution is ours

Apportioning zone events to counties is a substantial part of what SHELDUS sells.
Doing it independently is legitimate, but **any disagreement with FEMA may
originate in our apportionment rather than in the index**, and that possibility is
stated wherever a disagreement is reported.

---

## 4. Methodology

Incremental milestones, each with a spec before and a summary after, matching
OrderLens, GridCast, Bellwether, Triage, Groundtruth, Headway and Downfall.

**Definition of Done**, every milestone:

1. Requirements met or deferred with a written reason.
2. Tests pass in CI on a clean clone.
3. Every published number reproducible from committed inputs and a pinned seed.
4. A summary recording what was built, verified, broken and decided.
5. Nothing asserted that was not measured.

---

## 5. Data source specification

All sources free, open, and keyless.

| Source | Supplies |
|---|---|
| **National Risk Index v1.19.0** (Datalumos mirror) | `{HAZ}_EALB/EALT/ALRB`, `EAL_VALT`, `POPULATION`, `BUILDVALUE`, and `NRI_HazardInfo` periods of record |
| **NOAA Storm Events** 2020–2026 | `EVENT_TYPE`, `CZ_TYPE`, `CZ_FIPS`, `STATE_FIPS`, `DAMAGE_PROPERTY`, `DAMAGE_CROPS` |
| **NWS zone–county correlation** | Zone-to-county mapping, 4,875 rows, 4,080 zones |
| **OpenFEMA `FimaNfipClaims`** | 2,724,656 flood claims — the independent read for flood |
| **OpenFEMA IA / PA** | Assistance uptake — the secondary, flattering outcome |

### 5.1 Characteristics requiring handling

| # | Characteristic | Handling |
|---|---|---|
| DC-1 | **A blank damage field and an explicit `0.00K` are different things** — 19.8% blank, 60.9% explicit zero | Parsed separately and never conflated. No county-year dropped for zero |
| DC-2 | **72.0% of damage dollars are zone-coded**, including 100% of hurricane | §4.0 of the pre-registration: crosswalk, equal split for multi-county zones, unmatched excluded and published |
| DC-3 | **37.7% of zone damage matches no zone key** | The crosswalk is an April 2026 snapshot; NWS renumbers zones. M2 retrieves historical versions. Until then, excluded and published per hazard |
| DC-4 | Reporting rate varies 50.4 points between states | Published beside every state figure; BQ-5 tests robustness to it |
| DC-5 | 2026 is a partial year | Reported as partial, never annualised, never dropped |
| DC-6 | Loss distributions are heavy-tailed; one hurricane can dominate | Spearman rank, not Pearson. Bootstrap resampled **by state**, since losses within a state share weather and reporting practice |
| DC-7 | Index dollars are 2020-adjusted | NOAA damage inflation-adjusted to 2020 to match |
| DC-8 | Earthquake and wildfire are probability models, not frequency windows | Grounded differently; noted wherever they appear |

---

## 6. Functional requirements

### 6.1 Ingestion and attribution

| # | Requirement |
|---|---|
| FR-1 | Read the index via `pyogrio.read_arrow`; no geopandas dependency |
| FR-2 | Parse NOAA damage strings distinguishing blank from explicit zero (DC-1) |
| FR-3 | Attribute zone events to counties per pre-registration §4.0 |
| FR-4 | Publish the unmatched share, by hazard, beside every figure |
| FR-5 | Never drop a county-year for reporting zero |

### 6.2 Measurement

| # | Requirement |
|---|---|
| FR-6 | Enforce the per-hazard out-of-sample boundary from `NRI_HazardInfo` |
| FR-7 | Compute Spearman ρ, top-decile capture, and calibration ratio per hazard |
| FR-8 | Bootstrap intervals resampled by state |
| FR-9 | Compute the three reference predictors, including naive extrapolation |
| FR-10 | Test robustness to state reporting rate (BQ-5) |
| FR-11 | Compute the conservative all-hazards-2023-onward variant |
| FR-12 | Read flood twice — NOAA and NFIP — and report disagreement as a finding |

### 6.3 Publication

| # | Requirement |
|---|---|
| FR-13 | Per-hazard results table; **no single national skill number** |
| FR-14 | Testable share published beside every headline |
| FR-15 | Assistance-based figures permanently labelled "the flattering measure" |
| FR-16 | Every figure carries sample size, window, and share excluded |
| FR-17 | `METHODS.md`, `PREREGISTRATION.md`, `LITERATURE.md`, `FINDINGS.md`, and a two-page decision memo |

---

## 7. Non-functional requirements

| # | Requirement |
|---|---|
| NFR-1 | Zero cost. NOAA, OpenFEMA, NWS, Datalumos, GitHub Actions, Vercel free tiers |
| NFR-2 | No database. Cached pulls and committed aggregates |
| NFR-3 | Every number reproducible from committed inputs and a pinned seed |
| NFR-4 | Raw pulls gitignored; aggregates committed |
| NFR-5 | **No claim the pre-registration forbids** — no validation claim, no policy recommendation, no grant-allocation finding |
| NFR-6 | Public repository |
| NFR-7 | The site never advises any community about its own risk |

---

## 8. Architecture

```
National Risk Index v1.19.0        NOAA Storm Events 2020-2026
  (Datalumos, 86 MB GDB)             (7 files, 73 MB, 439,152 events)
        |                                      |
        v                                      v
  pyogrio.read_arrow                    damage parser (DC-1)
  EAL per county per hazard                    |
  NRI_HazardInfo -> boundaries                 v
        |                            NWS zone-county crosswalk
        |                            equal split, unmatched excluded
        |                                      |
        +------------------+-------------------+
                           v
              county x year x hazard realized loss
                           |
        +------------------+-------------------+
        v                                      v
  per-hazard scoring                  reference predictors
  (out-of-sample only)                (exposure, population,
        |                              naive extrapolation)
        v                                      |
  reporting-rate robustness  <-----------------+
        |
        v
  NFIP independent read for flood
        |
        v
  Next.js on Vercel + decision memo
```

### 8.1 Decisions and rejected alternatives

| Decision | Chosen | Rejected | Reason |
|---|---|---|---|
| Subject | NRI Expected Annual Loss | Social vulnerability component | Covered by existing work (`LITERATURE.md` §2) |
| Outcome | Property damage | Assistance uptake | Indexes score far better against uptake; free choice would decide the answer |
| Holdout | Per-hazard binding boundary | Single global date | Leaks inputs or discards years, depending on the date |
| Geography | County | State | The index is used at county and tract level; state-level n is 56 |
| Zone split | Equal | Population-weighted | Population is an input to the index's exposure term — circular |
| Statistic | Spearman | Pearson | Heavy tails; one hurricane would decide it |
| Bootstrap unit | State | County | Losses within a state share weather and reporting practice |
| Loss source | NOAA + NFIP | SHELDUS | SHELDUS is licensed, and is the index's own input |

---

## 9. Analysis plan

1. **Reporting completeness and its interstate variation.** Everything downstream
   is conditional on it. — **done, M1**
2. Zone-to-county attribution, with unmatched share published. — M2
3. Recompute the testable share after all exclusions. **Below 50% the project
   stops.**
4. Per-hazard Spearman, top-decile capture and calibration, out-of-sample only.
5. The three reference predictors, naive extrapolation foremost.
6. Robustness to state reporting rate.
7. NOAA against NFIP for flood.
8. Decision memo.

---

## 10. Milestone plan

| # | Milestone | Exit criterion |
|---|---|---|
| M0 | Literature, index, boundaries | `LITERATURE.md` committed before any data; per-hazard boundaries fixed. **Done** |
| **M1** | **Outcome measurability** | Reporting completeness measured and published. **Done — 94.9%, PASS** |
| **M2** | **Attribution** | Zone-to-county pipeline built; unmatched share reduced and published; testable share recomputed. **Kill point** |
| M3 | First join | Per-hazard out-of-sample scoring, with intervals |
| M4 | References | Naive extrapolation and exposure baselines |
| M5 | Robustness | Reporting-rate control; conservative 2023-onward variant |
| M6 | Flood, twice | NOAA against NFIP |
| M7 | Site | FR-13 to FR-16 live |
| M8 | Memo | Decision memo and write-up |

---

## 11. Risks

| # | Risk | Mitigation |
|---|---|---|
| R-1 | **Read as validating the index** | §3.1. Testable share beside every headline; the claim is forbidden in writing |
| R-2 | Reporting practice drives the result | §3.3. BQ-5, and a kill criterion in pre-registration §6 |
| R-3 | Outcome instrument shared with the index's input | §3.2. Stated on every NOAA figure; NFIP carried as independent |
| R-4 | Our apportionment causes the disagreement | §3.4. Stated wherever a disagreement is reported |
| R-5 | Unmatched zones stay at 37.7% | M2 retrieves historical crosswalks; if it fails, the excluded share is published per hazard and the affected hazards are marked unreliable |
| R-6 | Read as an attack on FEMA | It is a scorecard. FEMA publishes this data when it need not, which is the only reason the project exists — and the site says so |
| R-7 | The index turns out to predict well | A legitimate finding, pre-registered as such |

### 11.1 Kill criterion

**If the testable share after all exclusions falls below 50%, the project stops**
and publishes the negative result: that this index cannot be meaningfully scored
on the data available, and why.

M1 came within sight of it — county-coded damage alone gives a testable share
near 26% — and the zone crosswalk is what keeps the project alive. **If M2 cannot
make that attribution defensible, §11.1 fires.**

---

## 12. Acceptance criteria

| # | Criterion |
|---|---|
| AC-1 | Every FR met or deferred with a written reason |
| AC-2 | SC-1 to SC-7 met, or §11.1 executed |
| AC-3 | Pre-registration thresholds asserted by the test suite |
| AC-4 | No hazard scored on a year that fed it — asserted in code |
| AC-5 | Testable share published beside every headline |
| AC-6 | `LITERATURE.md` committed before any analysis code — **met** |
| AC-7 | Memo readable by a non-technical reader |
| AC-8 | Zero cost, with each free source named |

---

## 13. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-26 | Initial specification, grounded in the M0 and M1 measurements recorded in `FINDINGS.md`, and in `PREREGISTRATION.md` v1.1. |
