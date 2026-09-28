# Actuary

**FEMA's National Risk Index directs federal money by telling every US county
how much disaster damage to expect. Checked against the losses that arrived
after it was built, 29% of it cannot be tested at all, and on the rest it ranks
counties weakly — weakest at the part funding decisions use.**

[**Live site**](https://actuary-ochre.vercel.app) ·
[Decision memo](MEMO.md) ·
[Pre-registration](PREREGISTRATION.md) (committed *before* any outcome data was downloaded) ·
[Findings](FINDINGS.md)

> **Status: complete.** M0–M7 are done and the memo is published. The index has
> not been validated, and it has not been refuted: nearly a third of it was never
> exercised.

---

## The question

The National Risk Index gives every county an Expected Annual Loss in dollars —
**$76.7 billion a year** nationally. That figure feeds federal grant scoring,
state hazard mitigation plans, and the designation of Community Disaster
Resilience Zones.

FEMA's own documentation says the index **is not meant to predict** how much
damage a community will experience. So a number that disclaims prediction is
being used to direct money, and no published study appeared to have checked
whether the dollars land where it says. This project checked.

The method is not new — comparing modelled annual loss to realized loss is
routine in insurance. What appears not to have been done is applying it to this
public index, at the county level where it is used, on losses that arrived
*after* the data that built it.

## The test

- **The index:** the March 2023 release, built from loss records ending in 2019
  for most hazards and 2021 for the rest. The out-of-sample window is set **per
  hazard** from FEMA's own hazard metadata, not from the publication date — an
  early version of this project got that wrong and the correction is recorded in
  [`FINDINGS.md`](FINDINGS.md) F0-T2.
- **Realized loss:** 439,152 NOAA Storm Events records from 2020–2026, and, for
  flood only, 972,470 NFIP insurance claims as an independent second instrument.
- **Compared:** the index's building and agriculture loss (`EALB + EALA`)
  against recorded property and crop damage. The population component is
  deliberately excluded — scoring deaths-converted-to-dollars against building
  damage would mark the index wrong for being right.
- **Scored against three reference predictors**, foremost naive extrapolation:
  assume the next years look like the last decade.

**Every threshold was written down before the data was downloaded.** Where the
plan turned out to be wrong, it was amended in a new numbered version stating
what had been seen and why, with the old version left standing (§8 of the
pre-registration).

## What was found

**1. Only about seven tenths of the index can be checked at all.**
Earthquake is 27% of the index's dollar value, recurs on century timescales, and
**is not recorded in the national storm database at all**. Coastal flooding adds
2%, because the index does not state what history it was built from. Every
result below concerns the testable 70.97%, never the index as a whole.

**2. On the part that can be checked, it ranks counties weakly.**

| Hazard | Score | Bar set in advance (0.5) |
|---|---|---|
| Tornado | 0.36 | not met |
| Hurricane | 0.34 | not met |
| Riverine flood | 0.30 | not met |
| Wildfire | 0.26 | not met |
| Hail | 0.19 | not met |
| Winter weather | −0.01 | not met |
| Cold wave | −0.06 | not met |

Split in two, the skill separates cleanly. On **which counties get hit**, the
index beats the simple alternatives for 4 of 11 hazards; on **how big the loss
is once a county is hit**, for 8 of 11. It is better at *sizing* a loss than at
*locating* one — the opposite of what a funding decision needs. For cold waves
it scores **0.38 on locating, where 0.50 is a coin toss**.

**3. The obvious comparison was misleading, and only a second source caught it.**
Against naive extrapolation the index loses on 10 of 13 hazards, and that
survived two robustness checks. It did not survive the third. Flood is the one
hazard measured by two independent record-keepers, and **the two agree with each
other at only 0.40**. Drawn from the *same* record as the answer, the past
decade beats the index 0.68 to 0.44; drawn from the *other* record, the index
wins 0.44 to 0.28. Each record carries its own reporting habits, so the naive
comparison was partly scoring bureaucratic persistence as skill.

## What this does not say

- **Nothing about whether the index over- or under-states losses.** Observed
  damage ran at a quarter to a half of its expectation, but storm records
  undercount, the attribution excludes 9% of dollars, and the window may have
  been quiet. Those cannot be separated here.
- **Nothing about lives** — the population component was excluded by design.
- **No recommendation to FEMA.** This measures whether a number predicts; what
  follows is a policy question the data does not answer.
- **Nothing about how the money is distributed.** That mitigation funding
  favours wealthier communities is established elsewhere and was not re-derived.

## Running it

The analysis is Python (`numpy`, `pandas`, `scipy`, `pyogrio`); the site is
Next.js. Source data is free and keyless but large, so it is not committed —
`data/cache/` is expected to hold:

| Path | Source |
|---|---|
| `data/cache/noaa/*.csv.gz` | NOAA Storm Events annual detail files, 2020–2026 |
| `data/cache/NRI_GDB_Counties/NRI_GDB_Counties.gdb` | National Risk Index county geodatabase (FEMA, archived on Datalumos) |
| `data/cache/zone_county.dbx` | NWS forecast-zone to county correspondence |

NFIP claims are fetched from the OpenFEMA API by `m6_nfip.py`.

```bash
python scripts/m1_reporting_completeness.py   # M1: is damage reporting complete enough to score?
python scripts/m2_zone_attribution.py         # M2: attribute zone-coded damage to counties
python scripts/m3_score.py                    # M3: the first join to the index
python scripts/m45_robustness.py              # M4–M5: reference predictors and robustness checks
python scripts/m6_nfip.py                     # M6: NFIP claims as an independent instrument
npm run data                                  # M7: freeze results into the site's data module
npm install && npm run dev                    # the site
```

The site never contains a hand-typed number: `m7_build_site_data.py` generates
everything it renders from the committed result files, so the page and
[`FINDINGS.md`](FINDINGS.md) cannot drift apart.

## Repository

| Path | |
|---|---|
| [`MEMO.md`](MEMO.md) | The decision memo — the findings in plain language |
| [`PREREGISTRATION.md`](PREREGISTRATION.md) | The rules, fixed before outcome data was downloaded, with every amendment recorded |
| [`FINDINGS.md`](FINDINGS.md) | Every measured result, in the order it was established, corrections included |
| [`LITERATURE.md`](LITERATURE.md) | What was already known, and why this had not been done |
| [`Actuary_SRS_v1.0.md`](Actuary_SRS_v1.0.md) | The original specification |
| `scripts/` | One script per milestone, M1–M7 |
| `src/` | The site |
