# Actuary — Pre-registration

**v1.1 — written 2026-08-26. Amends v1.0 of the same day, after M1 measured the
outcome data and before any correlation has been computed.**

**Amendment made after seeing a result.** M1 found that only **28.0%** of NOAA
damage dollars carry a county FIPS — hurricane, 45.2% of all damage and 29.25%
of the index's dollar value, is **entirely** zone-coded. Taken at face value that
puts the testable share near 26%, **below the 50% floor in §6, and the project
would have ended.** A free NWS zone–county crosswalk raises county-attributable
damage to **72.9%**, and §4 now declares that step and its apportionment rule.

v1.0 did not anticipate the step. It is added here, before any correlation
exists, and **v1.0 stands intact in git history.**

No correlation, ranking, or join between the index and any outcome has been
computed as this is committed.

The point of this document is that the thresholds below cannot be chosen once the
results are known. The constants it fixes live in code, where the test suite
asserts them against this text.

---

## §1 What had already been seen when this was written

Stating it first, because a pre-registration written after looking at *some* data
is only honest about the part it declares.

Everything in this section was **already measured**. **None of it is a
prediction.** Full record in `FINDINGS.md`.

### The predictor — seen in full

The March 2023 snapshot (v1.19.0) has been opened and profiled completely:
3,231 counties, 466 fields, 56 states and territories, national Expected Annual
Loss **$76.72 bn/yr**, and the per-hazard breakdown in F0-T3 — Hurricane 29.25%,
Earthquake 27.04%, Tornado 13.18%, Riverine Flooding 8.80%.

**This is deliberate and is not contamination.** The index is the *predictor*.
Examining a predictor before fixing a test is ordinary; examining the *outcome*
is what pre-registration exists to prevent, and no outcome data has been touched.

### The input periods — seen, and they define the test

`NRI_HazardInfo` gives a period of record per hazard (F0-T2). The binding
boundary is the later of the frequency window and the SHELDUS loss window
(1996–2019), and it differs by hazard: 2019 for four hazards, 2021 for twelve,
2022 for volcanic activity, and undeclared for coastal flooding.

### What was already known from the literature

Social vulnerability indexes explain **assistance applications** far better than
they explain **property loss** (`LITERATURE.md` §2). That result is why §3 fixes
the outcome before any download, and it is not a finding of this project.

### What had NOT been done

No NOAA Storm Events file downloaded. No NFIP claim retrieved. No county scored,
no correlation computed, no model fitted. **Nothing in §3 onward has been run.**

---

## §2 The claim this project intends to test

> **For the hazards that recur inside a decade, FEMA's National Risk Index
> Expected Annual Loss predicts the geographic distribution of realized losses
> in the period after the data that built it.**

### And the claim it explicitly does not make

**This project cannot validate the National Risk Index**, and no sentence
implying otherwise may appear anywhere in it.

Earthquake is 27.04% of the index's dollar value and manifests on century
timescales. Together with volcanic activity, tsunami and avalanche, **27.48% of
the index cannot be exercised by any holdout available here.** Coastal flooding,
at a further 1.67%, declares no period of record and is excluded.

**70.85% of the index's dollar value is testable. That figure is published beside
every headline**, in those words.

---

## §3 The outcome, fixed before any of it is downloaded

**Primary outcome: direct property damage**, in dollars, by county, by year.

- **NOAA Storm Events** `DAMAGE_PROPERTY` + `DAMAGE_CROPS`, aggregated to county
  and year, inflation-adjusted to 2020 dollars to match the index's own basis.
- **NFIP claims** (`FimaNfipClaims`) as the **independent** read for riverine and
  coastal flooding, since insurance claims are a separate instrument from storm
  reports.

**Secondary, reported but never headline: FEMA assistance uptake** — Individual
and Households Program registrations, Public Assistance obligations.

**The secondary outcome may not be substituted for the primary at any point.**
The literature records that indexes score far better against assistance uptake
than against property loss; a project free to choose between them after seeing
both has chosen its answer. Both are published, and the assistance-based figure
is labelled **"the flattering measure"** wherever it appears.

### The measurement problem, declared now

NOAA Storm Events damage figures are **inconsistently reported**, and a zero can
mean *no loss* or *no one recorded a loss*. **The two are not distinguishable in
the data.** Therefore:

- No county-year is dropped for having zero damage.
- **Reporting completeness is measured and published first**, as the share of
  county-years carrying any damage figure, broken down by state — because
  reporting practice varies by state and that variation would otherwise be read
  as risk being wrong.
- If completeness is below **60%** nationally, the primary analysis is reported
  as **bounded** rather than point-estimated, with a stated best and worst case.

---

## §4 The test

### §4.0 Attributing damage to counties — added in v1.1

NOAA codes 45.9% of events, and 72.0% of damage dollars, to **NWS forecast
zones** rather than counties. Zone events are mapped to counties through the
public NWS zone–county correlation file, and the rules are fixed here:

| Case | Share of zone damage | Rule |
|---|---|---|
| Zone maps to exactly one county | 57.7% | Assign in full |
| Zone maps to several counties | 4.6% | **Split equally** among them |
| Zone key not in the crosswalk | 37.7% | **Excluded, and the excluded total published** beside every figure |

**Equal splitting is chosen over population or building-value weighting** because
both of those are components of the index's own exposure term, and weighting the
outcome by the predictor's inputs is circular. Equal splitting is cruder and
neutral. It touches 4.6% of zone damage, so the choice cannot drive the result;
a population-weighted variant is computed as a robustness check and published if
it moves any headline by more than two points.

**The unmatched 37.7% is a known defect, not an acceptable loss.** The crosswalk
is an April 2026 snapshot while events begin in 2020, and NWS renumbers zones.
Retrieving historical crosswalk versions is M2 work. Until it is done, every
figure carries the share of damage excluded for want of a zone match, by hazard.

**This crosswalk is ours, not FEMA's.** Apportioning zone events to counties is a
substantial part of what SHELDUS — the index's own licensed loss input — sells.
Any disagreement between this project and FEMA may therefore originate in the
apportionment rather than in the index, and that possibility is stated wherever a
disagreement is reported.

### §4.1 Windows, per hazard

Each hazard is scored **only on years strictly after its binding input boundary**
(F0-T2): 2020 onward for lightning, ice storm, avalanche and riverine flooding;
2022 onward for the twelve hazards ending 2021; 2023 onward for volcanic
activity. Coastal flooding is excluded.

**No hazard is scored on a year that fed it.** The per-hazard boundaries are
fixed here and may not be moved.

A **conservative variant** — every hazard scored on 2023 onward, after the latest
input of any hazard — is computed and published beside the primary, so a reader
who distrusts the per-hazard boundaries has a single unimpeachable number.

### §4.2 The statistic

For each testable hazard, across counties:

- **Spearman rank correlation** between predicted EAL and realized loss.
  Rank, not Pearson: both distributions are heavy-tailed, and a single hurricane
  would otherwise decide the answer.
- **Share of realized loss captured by the top decile** of counties ranked by
  predicted EAL, against the share a random ranking captures.
- **Calibration ratio**: total realized loss ÷ (EAL × years elapsed). One means
  the index has the magnitude right; this is reported per hazard and never
  aggregated into a single national figure.

**95% bootstrap intervals throughout, resampled by state** — losses within a
state are correlated through shared weather and shared reporting practice, and
resampling counties would understate every interval.

### §4.3 What counts as the index working

Fixed now, per testable hazard:

| | Threshold |
|---|---|
| **Supported** | Spearman ρ **≥ 0.5** with the interval's lower bound above **0.3** |
| **Weak** | ρ between 0.2 and 0.5, or an interval spanning 0.3 |
| **Not supported** | ρ **< 0.2**, or an interval including zero |

**The headline is the per-hazard table, not an average.** An index that predicts
tornado loss well and flood loss badly has not "worked overall", and no single
number will be offered that permits that reading.

---

## §5 Reference lines, published beside every result

The index must be compared against something, or "ρ = 0.45" means nothing.

Three naive predictors, all computed from data available **before** each hazard's
boundary:

1. **Building value exposure alone** (`BUILDVALUE`) — the crudest possible proxy.
2. **Population alone** (`POPULATION`).
3. **Realized loss in the index's own input window**, per county — that is,
   *just extrapolating the past*, which is what a person with a spreadsheet and
   no index would do.

**If the index does not beat all three, that is the finding**, and it will be
reported as prominently as the alternative. Reference 3 is the one that matters:
the index's central contribution over naive extrapolation is what is being
tested.

This threshold exists because of Triage, where a gradient-boosted model beat one
integer column by 1.06× with an interval spanning 1.0.

---

## §6 What would kill the project

Any one of these ends it, and the negative result is published as prominently as
a positive one would be:

- **Reporting completeness collapses.** If NOAA damage reporting proves so sparse
  or so state-dependent that realized loss cannot be measured, the project
  reports that the outcome data cannot support the question, and stops.
- **The testable share falls below half.** F0-T3 puts it at 70.85% on index
  grounds. M1 nearly pushed it to ~26% on outcome-geography grounds before the
  §4.0 crosswalk recovered it. **The share is recomputed after §4.0 exclusions
  and published; below 50% the project stops.**
- **Reporting rate explains the result.** M1-T1 found a 50.4 point spread in
  damage reporting between states, concentrated in the hail and tornado states
  where the index carries high expected loss. If the correlation between the
  index and realized loss is not robust to controlling for a state's reporting
  rate, **the finding is about NOAA, not about FEMA**, and is published as
  such.
- **The NFIP and NOAA reads contradict each other for flood.** Two instruments
  disagreeing is a measurement finding, not a risk finding, and it is published
  as one rather than resolved by picking the more convenient.
- **A later index version turns out to be obtainable and materially different.**
  Then the March 2023 result is a statement about one version, and must say so.

---

## §7 Declared in advance about what this cannot claim

- **No validation of the National Risk Index.** 29.15% of its dollar value is
  untestable or excluded here (§2).
- **No claim about social vulnerability or community resilience.** Only Expected
  Annual Loss is in scope; that ground is covered (`LITERATURE.md` §2).
- **No methodological novelty.** Comparing modelled annual loss to observed loss
  is standard catastrophe-model practice; what is new is the target and the
  temporal boundary, not the method (`LITERATURE.md` §3).
- **No claim about grant allocation.** That FEMA mitigation funding favours
  wealthier, whiter, higher-property-value communities is established, and
  re-deriving it would be replication presented as a finding
  (`LITERATURE.md` §4).
- **NOAA is not an independent instrument.** SHELDUS, the index's own loss input,
  is built largely from NOAA Storm Data. Every NOAA-based figure carries that
  statement. NFIP claims are independent and are the reason flood is read twice.
- **No policy recommendation.** The project reports whether a number predicts.
  What FEMA should do about it is not a question this data answers.
- **Nothing here describes any index but the National Risk Index, version
  1.19.0, March 2023.**

---

## §8 Amendments

Any change to this document is a new numbered version, committed separately, with
the reason stated and the previous version left intact in git history. An
amendment made after seeing a result says so in its first line.

**No amendment may weaken §3, §4.0, §4.1, §4.3 or §5 after the corresponding
analysis has been run.** In particular the primary outcome may not be changed to
assistance uptake, and the per-hazard boundaries may not be moved.

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-26 | Initial. Committed after the literature search and after the index was profiled, before any outcome data was downloaded. |
| 1.1 | 2026-08-26 | §4.0 added — zone-to-county attribution, with the apportionment rule and the treatment of unmatched zones fixed before any correlation exists. §6 gains a reporting-rate kill criterion after M1-T1 measured a 50.4 point interstate spread. Written after M1 measured the outcome data, before any join to the index. |
