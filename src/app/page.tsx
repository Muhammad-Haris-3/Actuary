import {
  CoverageBar,
  InstrumentScatter,
  ReversalChart,
  SplitChart,
} from "@/components/charts";
import { RESULTS } from "@/lib/results";

const REPO = "https://github.com/Muhammad-Haris-3/Actuary";
const bn = (v: number) => `$${(v / 1e9).toFixed(1)}bn`;

export default function Page() {
  const { coverage, flood, reporting, attribution, hazards } = RESULTS;
  const untestable = 100 - coverage.testable;

  return (
    <main>
      <section className="first">
        <p className="kicker">National Risk Index · version {RESULTS.indexVersion}</p>
        <h1>A number that disclaims prediction, used to direct money.</h1>
        <p className="lead">
          FEMA gives every US county a dollar figure for how much damage it should
          expect in an average year — <strong>${RESULTS.nationalEal}bn</strong>{" "}
          nationally. The figure feeds federal grant scoring and resilience-zone
          designations. FEMA&rsquo;s own documentation says it{" "}
          <strong>is not meant to predict</strong> how much damage a community will
          experience.
        </p>
        <p className="lead">
          This checks whether it does, on losses that arrived after the data that
          built it. Every threshold was published before the data was downloaded.
        </p>

        <div className="stats">
          <div className="stat">
            <span className="v acc">{coverage.testable}%</span>
            <span className="k">of the index&rsquo;s dollar value can be tested at all</span>
          </div>
          <div className="stat">
            <span className="v bad">{flood.instrumentAgreement}</span>
            <span className="k">agreement between two federal records of the same floods</span>
          </div>
          <div className="stat">
            <span className="v">0</span>
            <span className="k">of 13 hazards met the standard set in advance</span>
          </div>
          <div className="stat">
            <span className="v acc">4 of 11</span>
            <span className="k">hazards where the index beats naive extrapolation at locating loss</span>
          </div>
        </div>

        <div className="card flag">
          <p style={{ margin: 0 }}>
            <strong>The headline changed twice.</strong> After the first scoring
            pass the answer looked clear: simple extrapolation beat the index
            almost everywhere. A second, independent record of the same losses
            showed that comparison was partly measuring bureaucratic persistence
            and scoring it as skill. What is published here is the tension, not
            either half of it.
          </p>
        </div>
      </section>

      <hr className="rule" />

      <section id="coverage">
        <p className="kicker">Finding one</p>
        <h2>Nearly a third of the index cannot be checked by anyone</h2>
        <p>
          Before asking whether the index is right, it is worth asking how much of
          it is answerable. <strong>{untestable.toFixed(2)}%</strong> of its dollar
          value cannot be tested against outcomes on any freely available data.
        </p>
        <CoverageBar />
        <p>
          This is the most solid result here and it is not in dispute: it is a fact
          about the available evidence rather than about the index. It also means{" "}
          <strong>
            nothing on this page is a statement about the National Risk Index as a
            whole
          </strong>
          .
        </p>
      </section>

      <hr className="rule" />

      <section id="instruments">
        <p className="kicker">Finding two</p>
        <h2>The yardsticks disagree with each other</h2>
        <p>
          Floods are the only hazard measured by two independent record-keepers:
          National Weather Service storm reports, and federal flood insurance
          claims. Over the same counties and the same years they recorded{" "}
          <strong>${flood.noaaTotal}bn</strong> and{" "}
          <strong>${flood.nfipTotal}bn</strong> of loss respectively — and they rank
          counties differently.
        </p>
        <InstrumentScatter />
        <p>
          Two attempts to measure the same floods correlate at{" "}
          <strong>{flood.instrumentAgreement}</strong>. That caps how well{" "}
          <em>any</em> risk model can score against both at once, and every
          correlation below should be read against it.
        </p>
      </section>

      <hr className="rule" />

      <section id="reversal">
        <p className="kicker">Finding three · the least certain</p>
        <h2>The obvious comparison was misleading</h2>
        <p>
          The natural test of an index is whether it beats assuming the next decade
          looks like the last one. On that comparison the index lost for ten of
          thirteen hazards — and it survived restricting to the states that record
          damage most reliably, and survived shortening the window.
        </p>
        <p>
          It did not survive having a second record to check against.
        </p>
        <ReversalChart />
        <p>
          Each record carries its own habits. A county with flood policies in force
          files claims in both decades partly because the policies are there, not
          because it floods more; storm reporting carries the equivalent habit in
          county reporting practice. Drawing the naive baseline from the{" "}
          <em>other</em> record strips that persistence out — and the ordering
          reverses.
        </p>
        <div className="card warn">
          <p style={{ margin: 0 }}>
            <strong>This does not vindicate the index.</strong> It is one hazard —
            the only one with two instruments. The cross-record test is noisier
            than the one it overturns. And a practitioner holding claims history
            genuinely does hold a better predictor of future claims than the index
            is, whatever the reason.
          </p>
        </div>
      </section>

      <hr className="rule" />

      <section id="split">
        <p className="kicker">Finding four</p>
        <h2>The weakness sits exactly where funding decisions are made</h2>
        <p>
          Splitting the question in two separates it cleanly. Asking{" "}
          <em>which counties get hit</em> is a different problem from asking{" "}
          <em>how big the loss will be once one is</em> — and the index is much
          better at the second.
        </p>
        <SplitChart />
        <p>
          Deciding which counties to fund is entirely a locating problem. The index
          is weakest at the judgement its main use consumes.
        </p>
      </section>

      <hr className="rule" />

      <section id="table">
        <p className="kicker">Every hazard, out of sample</p>
        <h2>The full result</h2>
        <p>
          Scored only on years after the data that built each hazard&rsquo;s
          figures. The bar set in advance was 0.5 with the interval staying above
          0.3.
        </p>
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>Hazard</th>
                <th>Share of index</th>
                <th>Counties</th>
                <th>With loss</th>
                <th>Realized</th>
                <th>&rho;</th>
                <th>95% interval</th>
                <th>Naive</th>
                <th>Verdict</th>
              </tr>
            </thead>
            <tbody>
              {hazards.map((h) => (
                <tr key={h.code}>
                  <td className="name">{h.name}</td>
                  <td>{h.ealShare?.toFixed(2)}%</td>
                  <td>{h.counties.toLocaleString()}</td>
                  <td>{h.withLoss.toLocaleString()}</td>
                  <td>{bn(h.realized)}</td>
                  <td className={(h.rho ?? 0) < 0 ? "neg" : undefined}>
                    {h.rho?.toFixed(3)}
                  </td>
                  <td>
                    {h.lb?.toFixed(2)} – {h.ub?.toFixed(2)}
                  </td>
                  <td>{h.rhoNaive?.toFixed(3)}</td>
                  <td>
                    <span className={`tag ${h.verdict === "WEAK" ? "weak" : "no"}`}>
                      {h.verdict === "WEAK" ? "weak" : "not supported"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p style={{ fontSize: ".82rem" }}>
          Earthquake, at 27.04% of the index, appears nowhere above: the storm
          database does not record earthquakes.
        </p>
      </section>

      <hr className="rule" />

      <section id="how">
        <p className="kicker">How it was measured</p>
        <h2>What had to be solved first</h2>
        <p>
          Most of this project was spent on the outcome, not the index. Two
          problems nearly ended it.
        </p>
        <h3>Damage reporting is not uniform</h3>
        <p>
          {reporting.completeness}% of county-years with an event carry a damage
          figure, but the rate varies <strong>{reporting.spread} points</strong>{" "}
          between states — from {reporting.lowest[0][0]} at{" "}
          {reporting.lowest[0][1]}% to {reporting.highest[0][0]} at{" "}
          {reporting.highest[0][1]}%. The worst reporters are hail and tornado
          country, where the index carries high expected loss, so it will appear to
          over-predict there for reasons unrelated to risk. Restricting to the 22
          most reliable states did not change any conclusion.
        </p>
        <h3>Most damage is not recorded against a county</h3>
        <p>
          Only <strong>{attribution.countyCoded}%</strong> of damage dollars carry
          a county code — hurricane, the largest single category, carries none at
          all. The rest are filed against weather forecast zones. Mapping zones to
          counties by identifier recovers {attribution.zoneId}% more, and mapping
          the remainder by zone name recovers a further {attribution.zoneName}%.
        </p>
        <p>
          A name match is weaker evidence than an identifier match, so it was
          measured before it was used: on the 126,549 events resolvable both ways
          the two agree{" "}
          <strong>{attribution.nameAgreement}% by damage weight</strong>. The{" "}
          {attribution.unmatched}% that resolves neither way is excluded and
          reported rather than quietly dropped.
        </p>
      </section>

      <hr className="rule" />

      <section id="cannot">
        <p className="kicker">Limits</p>
        <h2>What this does not say</h2>
        <ul className="plain">
          <li>
            <strong>The index has not been validated, and has not been refuted.</strong>{" "}
            {untestable.toFixed(2)}% of it was never exercised.
          </li>
          <li>
            <strong>Nothing about whether it over- or under-states losses.</strong>{" "}
            Observed damage ran at a quarter to a half of expectation, but storm
            records undercount, our attribution excludes {attribution.unmatched}%,
            and the window may have been quiet. Those cannot be separated here.
          </li>
          <li>
            <strong>Nothing about lives.</strong> The records carry property and
            crop damage. The index also counts deaths and injuries converted to
            dollars, and that component was deliberately excluded — measuring it
            against building damage would score the index wrong for being right.
          </li>
          <li>
            <strong>No recommendation about what FEMA should do.</strong> This
            measures whether a number predicts. What follows is a policy question
            this data does not answer.
          </li>
          <li>
            <strong>Nothing about how the money is distributed.</strong> That
            mitigation funding favours wealthier communities is established
            elsewhere and was cut from this project rather than re-derived.
          </li>
        </ul>
        <div className="card">
          <p style={{ margin: 0 }}>
            The thresholds, the scoring windows and the outcome definition were
            fixed in{" "}
            <a href={`${REPO}/blob/main/PREREGISTRATION.md`}>a public document</a>{" "}
            before the data was downloaded, and amended three times as measurement
            problems emerged — each amendment stating what had been seen and why,
            with the superseded version left standing in the history. The{" "}
            <a href={`${REPO}/blob/main/FINDINGS.md`}>working record</a> includes
            two corrections to earlier claims of my own.
          </p>
        </div>
      </section>
    </main>
  );
}
