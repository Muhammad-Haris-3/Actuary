import { RESULTS } from "@/lib/results";

/* One red. Everything else is bone or a step down from it — the project's
   subject carries the accent, its comparisons do not. Zero corner radius. */
const ACCENT = "#ec3013";
const ACCENT_TEXT = "#ff9783";
const BAD = "#ff563c";
const BONE = "#f3f2f2";
const MUTED = "#9b9797";
const FAINT = "#949090";
const DIM = "#3a3736";
const RULE = "rgba(243,242,242,.16)";

/* ------------------------------------------------------------------ */
export function CoverageBar() {
  const c = RESULTS.coverage;
  const parts = [
    { label: "Testable", v: c.testable, fill: BONE, ink: "#141312" },
    { label: "Earthquake", v: c.earthquake, fill: ACCENT, ink: "#141312" },
    { label: "Coastal flood", v: c.coastalExcluded, fill: DIM, ink: BONE },
    { label: "Volcanic · tsunami · avalanche", v: c.otherUntestable, fill: "#2a2726", ink: BONE },
  ];
  const W = 820;
  const H = 78;
  let x = 0;
  return (
    <figure>
      <div className="plate">
        <div className="scroll">
          <svg viewBox={`0 0 ${W} ${H + 30}`} width="100%" role="img"
               aria-label="Share of the index's dollar value that can and cannot be tested">
            {parts.map((p) => {
              const w = (p.v / 100) * W;
              const el = (
                <g key={p.label}>
                  <rect x={x} y={0} width={Math.max(w - 3, 1)} height={H} fill={p.fill} />
                  {w > 90 && (
                    <>
                      <text x={x + 14} y={32} fill={p.ink} fontSize={22} fontWeight={800}
                            letterSpacing="-0.03em">{p.v.toFixed(2)}%</text>
                      <text x={x + 14} y={52} fill={p.ink} fontSize={10} fontWeight={800}
                            letterSpacing="0.14em" opacity={0.72}>
                        {p.label.toUpperCase()}
                      </text>
                    </>
                  )}
                </g>
              );
              x += w;
              return el;
            })}
            <text x={0} y={H + 22} fill={FAINT} fontSize={10} fontWeight={800}
                  letterSpacing="0.14em">TESTABLE — RECURS INSIDE A DECADE</text>
            <text x={W} y={H + 22} fill={ACCENT_TEXT} fontSize={10} fontWeight={800}
                  letterSpacing="0.14em" textAnchor="end">
              UNTESTABLE OR EXCLUDED — {(100 - c.testable).toFixed(2)}%
            </text>
          </svg>
        </div>
      </div>
      <figcaption>
        Earthquake is 27.04% of the index on its own, and it is untestable twice
        over: damaging earthquakes recur on century timescales, and the national
        storm database does not record earthquakes at all. Coastal flooding is
        excluded because the index never declares what period of history built it.
      </figcaption>
    </figure>
  );
}

/* ------------------------------------------------------------------ */
export function InstrumentScatter() {
  const pts = RESULTS.flood.scatter;
  const W = 440;
  const H = 440;
  const P = 56;
  const lo = 2;
  const hi = 9.5;
  const sx = (v: number) => P + ((v - lo) / (hi - lo)) * (W - P - 14);
  const sy = (v: number) => H - P - ((v - lo) / (hi - lo)) * (H - P - 14);
  const ticks = [3, 5, 7, 9];
  const fmt = (t: number) =>
    t >= 9 ? "$1bn" : t >= 6 ? `$${10 ** (t - 6)}m` : `$${10 ** (t - 3)}k`;
  return (
    <figure>
      <div className="plate">
        <div className="scroll">
          <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxWidth: 440 }} role="img"
               aria-label="NOAA flood damage against NFIP paid claims, by county">
            {ticks.map((t) => (
              <g key={t}>
                <line x1={sx(t)} y1={H - P} x2={sx(t)} y2={14} stroke={RULE} />
                <line x1={P} y1={sy(t)} x2={W - 14} y2={sy(t)} stroke={RULE} />
                <text x={sx(t)} y={H - P + 17} fill={FAINT} fontSize={10} fontWeight={800}
                      letterSpacing="0.08em" textAnchor="middle">{fmt(t)}</text>
                <text x={P - 8} y={sy(t) + 4} fill={FAINT} fontSize={10} fontWeight={800}
                      letterSpacing="0.08em" textAnchor="end">{fmt(t)}</text>
              </g>
            ))}
            <line x1={sx(lo)} y1={sy(lo)} x2={sx(hi)} y2={sy(hi)} stroke={ACCENT}
                  strokeDasharray="6 5" strokeWidth={1.5} opacity={0.85} />
            {pts.map(([a, b], i) => (
              <rect key={i} x={sx(a) - 2} y={sy(b) - 2} width={4} height={4}
                    fill={BONE} opacity={0.4} />
            ))}
            <text x={(W + P) / 2} y={H - 12} fill={MUTED} fontSize={10} fontWeight={800}
                  letterSpacing="0.14em" textAnchor="middle">
              NOAA STORM REPORTS
            </text>
            <text x={16} y={H / 2} fill={MUTED} fontSize={10} fontWeight={800}
                  letterSpacing="0.14em" textAnchor="middle"
                  transform={`rotate(-90 16 ${H / 2})`}>
              NFIP CLAIMS PAID
            </text>
          </svg>
        </div>
      </div>
      <figcaption>
        One mark per county, 2020 onward, both axes logarithmic, showing only
        counties where both records report loss. The red line is perfect
        agreement. Spearman between the two is{" "}
        {RESULTS.flood.instrumentAgreement} across all counties and{" "}
        {RESULTS.flood.instrumentAgreementBoth} among these{" "}
        {RESULTS.flood.nBoth.toLocaleString()}. A further {RESULTS.flood.noaaOnly}{" "}
        counties carry storm-reported flood damage and no insurance claim;{" "}
        {RESULTS.flood.nfipOnly} carry claims and no storm-reported damage.
      </figcaption>
    </figure>
  );
}

/* ------------------------------------------------------------------ */
export function ReversalChart() {
  const rows = RESULTS.flood.rows;
  const W = 820;
  const rowH = 52;
  const H = rows.length * rowH + 42;
  const L = 268;
  const max = 0.75;
  const bw = (v: number) => (v / max) * (W - L - 84);
  const colour = (k: string) => (k === "index" ? ACCENT : k === "same" ? BONE : MUTED);
  return (
    <figure>
      <div className="plate">
        <div className="scroll">
          <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
               aria-label="Predictor performance against each flood record">
            <text x={L} y={12} fill={FAINT} fontSize={10} fontWeight={800}
                  letterSpacing="0.14em">
              PREDICTING NFIP CLAIMS — THE INDEPENDENT RECORD
            </text>
            {rows.map((r, i) => {
              const y = 26 + i * rowH;
              const c = colour(r.kind);
              return (
                <g key={r.label}>
                  <text x={L - 14} y={y + 18} fill={r.kind === "index" ? BONE : MUTED}
                        fontSize={13} fontWeight={r.kind === "index" ? 800 : 400}
                        textAnchor="end">{r.label}</text>
                  <rect x={L} y={y} width={Math.max(bw(r.nfip), 1)} height={24} fill={c} />
                  <text x={L + bw(r.nfip) + 12} y={y + 18} fill={c} fontSize={15}
                        fontWeight={800} letterSpacing="-0.02em">{r.nfip.toFixed(3)}</text>
                  <rect x={L} y={y + 27} width={Math.max(bw(r.noaa), 1)} height={7}
                        fill={c} opacity={0.34} />
                  <text x={L + bw(r.noaa) + 12} y={y + 34} fill={FAINT} fontSize={10}
                        fontWeight={800} letterSpacing="0.08em">
                    {r.noaa.toFixed(3)} VS NOAA
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
        <div className="legend">
          <span><i style={{ background: ACCENT }} />The index</span>
          <span><i style={{ background: BONE }} />Naive, same record it is tested on</span>
          <span><i style={{ background: MUTED }} />Naive, the other record</span>
        </div>
      </div>
      <figcaption>
        Solid bars score against NFIP claims, faint bars against NOAA storm
        reports. The two naive rows are the same idea — extrapolate the last
        decade — differing only in which record supplied that decade. Tested on
        the record it came from, the naive baseline beats the index. Tested across
        records, it does not.
      </figcaption>
    </figure>
  );
}

/* ------------------------------------------------------------------ */
export function SplitChart() {
  const hz = RESULTS.hazards.filter((h) => h.aucIndex !== null && h.magIndex !== null);
  const W = 820;
  const colW = W / 2 - 30;
  const rowH = 30;
  const H = hz.length * rowH + 68;
  const L = 128;
  const mid = W / 2 + 30;

  const bar = (x0: number, v: number, span: number, base = 0.5) => {
    const half = span / 2;
    const c = x0 + half;
    const d = ((v - base) / base) * half;
    return { x: d >= 0 ? c : c + d, w: Math.max(Math.abs(d), 1.5), c };
  };

  return (
    <figure>
      <div className="plate">
        <div className="scroll">
          <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
               aria-label="Index skill split into locating and sizing">
            <text x={L} y={12} fill={BONE} fontSize={11} fontWeight={800}
                  letterSpacing="0.14em">WHICH COUNTIES GET HIT</text>
            <text x={L} y={26} fill={FAINT} fontSize={10}>AUC — 0.50 is a coin toss</text>
            <text x={mid} y={12} fill={BONE} fontSize={11} fontWeight={800}
                  letterSpacing="0.14em">HOW BIG, ONCE HIT</text>
            <text x={mid} y={26} fill={FAINT} fontSize={10}>rank correlation among counties with loss</text>

            {hz.map((h, i) => {
              const y = 44 + i * rowH;
              const a = bar(L, h.aucIndex as number, colW - 46);
              const an = bar(L, h.aucNaive as number, colW - 46);
              const m = bar(mid, (h.magIndex as number) + 0.5, colW - 46);
              const mn = bar(mid, (h.magNaive as number) + 0.5, colW - 46);
              const below = (h.aucIndex as number) < 0.5;
              return (
                <g key={h.code}>
                  <text x={L - 12} y={y + 13} fill={below ? BAD : BONE} fontSize={12}
                        fontWeight={below ? 800 : 400} textAnchor="end">{h.name}</text>
                  <line x1={a.c} y1={y - 2} x2={a.c} y2={y + 20} stroke={RULE} strokeWidth={1} />
                  <rect x={an.x} y={y + 13} width={an.w} height={5} fill={MUTED} opacity={0.8} />
                  <rect x={a.x} y={y} width={a.w} height={11} fill={below ? BAD : ACCENT} />
                  <line x1={m.c} y1={y - 2} x2={m.c} y2={y + 20} stroke={RULE} strokeWidth={1} />
                  <rect x={mn.x} y={y + 13} width={mn.w} height={5} fill={MUTED} opacity={0.8} />
                  <rect x={m.x} y={y} width={m.w} height={11}
                        fill={(h.magIndex as number) < 0 ? BAD : ACCENT} />
                </g>
              );
            })}
          </svg>
        </div>
        <div className="legend">
          <span><i style={{ background: ACCENT }} />The index</span>
          <span><i style={{ background: MUTED }} />Naive extrapolation</span>
          <span><i style={{ background: BAD }} />Index below chance</span>
        </div>
      </div>
      <figcaption>
        Bars run right from the centre line where the predictor beats chance and
        left where it does not. The index wins the sizing question for eight of
        eleven hazards and the locating question for only four — and locating is
        the judgement a funding decision is made of. Cold wave runs left: the
        index ranked counties that went on to record cold-wave damage below the
        ones that did not.
      </figcaption>
    </figure>
  );
}
