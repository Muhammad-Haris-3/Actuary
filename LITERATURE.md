# Literature

**Searched 2026-08-26, before any data was downloaded and before any
pre-registration was written.**

This is the check that killed the previous project (see
[Reach](https://github.com/Muhammad-Haris-3/Reach)), where it was scheduled after
feasibility instead of before it. It runs first here.

**Verdict: the project survives, narrowed.** The scorecard stands and appears
genuinely unclaimed. **The grant-allocation audit does not** — its central
finding is already established — and it is demoted from a headline to a
secondary descriptive section, or dropped.

---

## 1. Has anyone validated the National Risk Index against realized losses?

**No published study found.** Searches for NRI validation, accuracy assessment,
and predictive performance return FEMA's own documentation — the
[technical documentation](https://www.fema.gov/sites/default/files/documents/fema_national-risk-index_technical-documentation.pdf)
(v1.20, December 2025), the
[methodology overview](https://www.fema.gov/sites/default/files/documents/fema_national-risk-index_methodology-hazards-overview.pdf),
the [primer](https://www.fema.gov/sites/default/files/documents/fema_national-risk-index_primer.pdf)
and the [FAQ](https://www.fema.gov/sites/default/files/documents/fema_national-risk-index_faq-page-documentation.pdf)
— and no peer-reviewed evaluation.

This is stated as **"no study was found"**, not as "no study exists". The
absence of a result from a search is weaker evidence than a result, and it is
recorded at that strength.

### What FEMA itself says, which is the reason the project exists

FEMA's documentation states plainly that the index's purpose **is not to predict
the amount of damage communities will experience**. It is a *relative* risk
assessment, built from historical losses and smoothed by a Bayesian credibility
approach to stabilise small-sample estimates.

Meanwhile the index carries an **Expected Annual Loss** in dollars, and it feeds
BRIC technical evaluation criteria, state hazard mitigation plans, and Community
Disaster Resilience Zone designations.

**A number that disclaims prediction is being used to direct money.** Whether it
predicts is therefore a fair question, and one FEMA has not answered.

### The nearest thing to a call for this work

> "There are still many limitations on these indexes and there is a need for
> ground truthing and validation before using composite indexes for resource
> allocation."
> — [Just Solutions](https://justsolutionscollective.org/the-national-risk-index-funding-disaster-resilience-and-mitigation-in-frontline-communities/)

---

## 2. Index validation has been done — for the social vulnerability half

This is the closest prior work and it constrains what Actuary may claim.

**["How Valid Are Social Vulnerability Models?"](https://collaborate.princeton.edu/en/publications/how-valid-are-social-vulnerability-models-3/)**
Spatial regression of social vulnerability indexes on Hurricane Sandy outcomes —
housing assistance applicants, affected renters, housing damage, property loss —
controlling for flood exposure.

**Its finding is a direct warning to this project:**

> The indexes best explained **housing assistance applicants**, whereas they
> **poorly explained property loss.**

An index scored against *who applied for help* looks far better than the same
index scored against *what was destroyed*. Choosing the outcome after seeing
both would decide the answer. **Actuary must fix property loss as the primary
outcome before any data is downloaded**, and report the assistance-based figure
only beside it, clearly labelled as the flattering one.

The study evaluates **social vulnerability indexes, not the National Risk
Index**, and explicitly calls for more empirical validation. A related study
validated social vulnerability indicators against death and damage across 11,629
non-coastal US flood events (2008–2012).

**Consequence:** the NRI has three components — Expected Annual Loss, Social
Vulnerability, Community Resilience. **The social vulnerability component is
substantially covered by existing work.** Actuary's contribution is confined to
the **Expected Annual Loss** component, and must say so.

---

## 3. The method is standard — in insurance, on commercial models

Comparing modelled average annual loss to observed county-level losses is
routine catastrophe-model validation practice
([Verisk](https://www.verisk.com/blog/modeling-fundamentals-evaluating-u-s--flood-model-loss-output-with-historical-loss-experience/),
[NAIC primer](https://content.naic.org/sites/default/files/committees-pending-action-cat-mod-primer.pdf)).

The closest published application is
**[Dusseau et al., *Journal of Catastrophe Risk and Resilience*](https://journalofcrr.com/research/04-01-dusseau-et-al/)**,
which validates seven commercial flood models — Verisk, KatRisk, Moody's RMS,
Karen Clark & Company, Aon, the Florida Public Flood Loss Model and First Street
— against **NFIP claims 1978–2024**, the same outcome data Actuary would use.

| Their result | |
|---|---|
| Verisk, KatRisk, RMS | ~4% differential to historical losses |
| First Street | ~2× higher nationally |
| Karen Clark & Company | ~13× lower than peers in Florida |

**They do not evaluate the National Risk Index.** Scale is national and state,
with Florida detail.

**So Actuary is not methodologically novel, and will not claim to be.** What is
unclaimed is the target and three properties of the test:

| | Dusseau et al. | Actuary |
|---|---|---|
| Subject | Seven commercial models | **FEMA's public policy index** |
| Scale | National, state | **County and tract — the resolution at which the NRI is actually used to allocate** |
| Sample | Full historical claims | **Out-of-sample in time: a dated index version, scored on losses after it was published** |
| Hazards | Flood | **Multi-hazard, as far as outcome data allows** |

---

## 4. Grant allocation is already established — this half is dropped

The audit half of the original pitch does not survive.

Empirical work already shows HMA funds go **disproportionately to whiter and
wealthier communities**, and that FEMA is more likely to protect areas with high
property values and low social vulnerability
([Assessing distributive inequities in FEMA's disaster recovery assistance fund allocation](https://www.sciencedirect.com/science/article/pii/S2212420922000747);
[Equity in FEMA hazard mitigation assistance programs](https://www.sciencedirect.com/science/article/abs/pii/S1462901122002350)).
BRIC's distribution is documented — five of the wealthiest states took 70% of
funding. The benefit-cost side is settled too: FEMA mitigation grants return
roughly **4:1**, and a 23-year study puts societal savings at **$6 per $1**
([Natural Hazards Review](https://ascelibrary.org/doi/abs/10.1061/%28ASCE%291527-6988%282007%298%3A4%2897%29);
[CRS R46989](https://www.congress.gov/crs-product/R46989)).

Re-deriving "the money goes to richer places" would be a replication presented as
a finding. **It is cut.** If the grant data is used at all it is as a descriptive
appendix, in the past tense, citing the work above.

---

## 5. What this leaves

> Does FEMA's National Risk Index Expected Annual Loss predict realized losses,
> out-of-sample in time, at the resolution the index is used?

Everything else the original pitch contained has been claimed by someone.

### Design consequences carried into the pre-registration

1. **Primary outcome is property loss**, fixed before download. Assistance
   applications are reported beside it and named as the flattering measure (§2).
2. **The test must be out-of-sample in time.** The index is built from historical
   losses; scoring it on historical losses is circular and would produce a
   flattering, publishable, meaningless number. A dated version scored on
   subsequent losses is the only honest test.
3. **Scope is Expected Annual Loss.** No claim about the social vulnerability or
   community resilience components — that ground is taken.
4. **No methodological novelty is claimed.** The method is standard practice; the
   target has not had it applied.
5. **The outcome data is the weak link, not the method.** NFIP claims cover only
   *insured flood* losses; NOAA Storm Events damage estimates are known to be
   inconsistently reported. The pre-registration must fix how a miss is
   distinguished from a gap in the record before any number is computed.

### Data reachability, checked rather than assumed

| Source | Status |
|---|---|
| OpenFEMA API | **Verified live, keyless.** NFIP claims 2,724,656 · HMA projects 56,347 · PA projects 847,356 · disaster declarations 70,249 |
| NOAA Storm Events | **Verified**, HTTP 200, annual CSVs through 2026 |
| **National Risk Index** | **Not verified.** `hazards.fema.gov` resolves but the connection is blocked from the machine used for this check. **Not** served by the OpenFEMA API (checked). Mirrors exist on ArcGIS Hub and [Datalumos](https://www.datalumos.org/datalumos/project/218382/version/V1/view) — the latter matters, because archived *versions* are what the out-of-sample-in-time test needs. **Confirming this is task one, and the project does not start until it is confirmed.** |

Everything above is free and open.
