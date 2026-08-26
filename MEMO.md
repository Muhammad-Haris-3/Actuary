# Actuary — decision memo

**What we checked, what we found, and what we still cannot say.**
Muhammad Haris Khokhar · 26 August 2026 ·
[github.com/Muhammad-Haris-3/Actuary](https://github.com/Muhammad-Haris-3/Actuary)

---

## The question

FEMA publishes a National Risk Index. It gives every county in the United States
a dollar figure: how much damage it should expect from natural hazards in an
average year. Nationally those figures add to **$76.7 billion a year**.

The number is used. It feeds federal grant scoring, state hazard mitigation
plans, and the designation of Community Disaster Resilience Zones.

FEMA's own documentation says the index **is not meant to predict how much damage
a community will experience**. It describes a relative comparison between places,
built from historical losses.

So a number that disclaims prediction is being used to direct money, and no
published study appeared to have checked whether the dollars land where it says.
That is what this project checked.

**The method is not new.** Comparing a modelled annual loss to what actually
happened is routine practice in insurance. What appears not to have been done is
applying it to this particular public index, at the geography where it is
actually used, on losses that arrived *after* the data that built it.

---

## How the test was set up

The index version used was published in **March 2023**, and it is built from
loss records that end in **2019** for most hazards and 2021 for the rest. So
anything that happened after that date is a fair test: the index could not have
seen it.

Realized losses came from the National Weather Service's storm records — 439,152
events from 2020 to 2026 — and, for floods only, from 972,470 federal flood
insurance claims.

**Every threshold in the test was written down and published before the data was
downloaded.** What would count as the index working, which years could be scored,
what the comparison predictors would be — all fixed in advance, in a document
that is in the public repository with its own timestamp. Where the plan turned
out to be wrong, it was amended in a new numbered version stating what had been
seen and why, with the old version left standing.

---

## Finding 1 — Only about seven tenths of the index can be checked at all

**29% of the index's dollar value cannot be tested by anyone, on any data
available for free.**

The largest single piece is **earthquake, which is 27% of the whole index**. Two
reasons, and the second is worse than the first: damaging earthquakes arrive on
century timescales, so a six-year window contains almost none — and the national
storm database **does not record earthquakes at all**.

Coastal flooding adds a further 2%: the index does not state what period of
history it was built from, so no honest boundary can be drawn.

**Nothing in this memo is a statement about the National Risk Index as a whole.**
It concerns the roughly 71% of its dollar value driven by hazards that recur
often enough to be observed.

---

## Finding 2 — On the part that can be checked, the index ranks counties weakly

The test asks whether counties the index calls risky are the counties that went
on to lose money. A score of 1.0 would be perfect ordering, 0.0 no relationship.

| Hazard | Score | Bar set in advance |
|---|---|---|
| Tornado | 0.36 | not met |
| Hurricane | 0.34 | not met |
| Riverine flood | 0.30 | not met |
| Wildfire | 0.26 | not met |
| Hail | 0.19 | not met |
| Winter weather | −0.01 | not met |
| Cold wave | −0.06 | not met |

**No hazard met the standard set before the data was seen** (0.5, with the
uncertainty range staying above 0.3). Two scored slightly below zero.

**But the index is not useless, and the shape of its skill matters.** Split the
question in two and it separates cleanly:

- **"Which counties get hit?"** — the index beats simple alternatives for 4 of 11
  hazards.
- **"How big will the loss be, once a county is hit?"** — it beats them for 8 of
  11.

The index is better at *sizing* a loss than at *locating* one. That is the
opposite of what a funding decision needs, because deciding which counties to
fund is entirely a locating problem.

One result should not be smoothed over: for **cold waves the index scores 0.38 on
locating, where 0.50 is a coin toss.** It ranked the counties that went on to
record cold-wave damage *below* the ones that did not. That rests on 43 counties
and is thin, but it is not noise around chance.

---

## Finding 3 — The obvious comparison is misleading, and we only caught it because of a second source

The natural way to judge an index is to ask whether it beats doing nothing clever
— just assuming the next decade looks like the last one.

**On that comparison the index loses on 10 of 13 hazards.** It survived two
checks: restricting to the 22 states that record damage most reliably (the gap
*widened*), and shortening the window (unchanged).

**That result did not survive the third check.**

Floods are the only hazard measured by two independent record-keepers — storm
reports and insurance claims. The first thing that shows is that **the two only
agree with each other at 0.40**. Two attempts to measure the same floods, in the
same counties, in the same years, disagree substantially. That alone caps how
well *anything* can score.

The second thing is the important one. When "the last decade" is drawn from the
**same** record-keeper as the answer, it beats the index handsomely — 0.68 to
0.44. When it is drawn from the **other** record-keeper, the index wins — 0.44 to
0.28.

The reason is that each record carries its own habits. A county with flood
insurance policies in force files claims in both decades partly because the
policies are there, not because it floods more. Storm reporting carries the
equivalent habit. **The naive comparison was partly measuring bureaucratic
persistence and scoring it as skill.**

So the headline from the previous stage is not safe. It holds firmly for eleven
hazards where only one record exists — and reverses for the one hazard where a
second record exists to check it.

---

## What this does not say

- **The index has not been validated, and it has not been refuted.** Nearly a
  third of it was never exercised.
- **No conclusion about whether the index over- or under-states losses.** Observed
  damage ran at a quarter to a half of the index's expectation, but storm records
  are known to undercount, our own attribution excludes 9% of dollars, and the
  window may simply have been quiet. Those three cannot be separated here.
- **Nothing about lives.** The records used carry property and crop damage. The
  index also counts deaths and injuries, converted to dollars, and that component
  was deliberately excluded — measuring it against building damage would score
  the index wrong for being right.
- **No recommendation about what FEMA should do.** This measures whether a number
  predicts. What follows from that is a policy question this data does not
  answer.
- **Nothing about how the money is distributed.** That FEMA mitigation funding
  favours wealthier communities is already established elsewhere and was cut from
  this project rather than re-derived.

---

## What a reader should take away

**Three things, in order of how confident we are:**

1. **A large part of a widely used federal risk index cannot be checked against
   outcomes at all** — a quarter of it because the national loss database does
   not record the hazard in question. That is a fact about the available
   evidence, and it is not in dispute.

2. **Two federal records of the same floods agree with each other at 0.40.**
   Before asking whether any risk model is right, it is worth knowing that the
   yardsticks disagree this much.

3. **On the hazards that can be checked, the index orders counties weakly, and
   its weakness is concentrated in the judgement that funding decisions actually
   use.** Whether it beats simple extrapolation depends on a methodological choice
   that is easy to get wrong and that we got wrong at first.

The third is the least certain and is stated as a tension rather than a verdict.
Publishing it that way is the point: the confident version of this memo was
available two stages ago, and it was wrong.
