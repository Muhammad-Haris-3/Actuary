import { RESULTS } from "@/lib/results";

const ACCENT = "#d9a441";
const BAD = "#e0574f";
const COOL = "#6f8fd6";
const GOOD = "#4fb98a";
const MUTED = "#5a6070";
const FAINT = "#8b90a0";
const RULE = "rgba(238,240,245,.13)";

/* ------------------------------------------------------------------ */
/* What can and cannot be tested                                       */
/* ------------------------------------------------------------------ */
export function CoverageBar() {
  const c = RESULTS.coverage;
  const parts = [
    { label: "Testable", v: c.testable, fill: ACCENT },
    { label: "Earthquake", v: c.earthquake, fill: BAD },
    { label: "Coastal flood", v: c.coastalExcluded, fill: MUTED },
    { label: "Volcanic, tsunami, avalanche", v: c.otherUntestable, fill: "#3a3f4c" },
  ];
  const W = 860;
  const H = 74;
  let x = 0;
  return (
    <figure>
      <div className="scroll">
        <svg viewBox={`0 0 ${W} ${H + 34}`} width="100%" role="img"
             aria-label="Share of the index's dollar value that can and cannot be tested">
          {parts.map((p) => {
            const w = (p.v / 100) * W;
            const el = (
              <g key={p.label}>
                <rect x={x} y={0} width={Math.max(w - 2, 1)} height={H} fill={p.fill} rx={3} />
                {w > 74 && (
                  <>
                    <text x={x + 12} y={30} fill="#0d0f13" fontSize={20} fontWeight={700}
                          fontFamily="var(--font-mono), monospace">
                      {p.v.toFixed(2)}%
                    </text>
                    <text x={x + 12} y={50} fill="rgba(13,15,19,.75)" fontSize={12}
                          fontWeight={600}>
                      {p.label}
                    </text>
                  </>
                )}
              </g>
            );
            x += w;
            return el;
          })}
          <text x={0} y={H + 24} fill={FAINT} fontSize={12}>
            Testable — hazards that recur inside a decade
          </text>
          <text x={W} y={H + 24} fill={FAINT} fontSize={12} textAnchor="end">
            Untestable or excluded — {(100 - c.testable).toFixed(2)}%
          </text>
        </svg>
      </div>
      <figcaption>
        Earthquake is 27.04% of the index on its own. It is untestable twice over:
        damaging earthquakes recur on century timescales, and the national storm
        database does not record earthquakes at all. Coastal flooding is excluded
        because the index does not declare what period of history built it.
      </figcaption>
    </figure>
  );
}

/* ------------------------------------------------------------------ */
/* Two instruments, same floods                                        */
/* ------------------------------------------------------------------ */
export function InstrumentScatter() {
  const pts = RESULTS.flood.scatter;
  const W = 460;
  const H = 460;
  const P = 52;
  const lo = 2;
  const hi = 9.5;
  const sx = (v: number) => P + ((v - lo) / (hi - lo)) * (W - P - 16);
  const sy = (v: number) => H - P - ((v - lo) / (hi - lo)) * (H - P - 16);
  const ticks = [3, 5, 7, 9];
  const fmt = (t: number) =>
    t >= 9 ? "$1bn" : t >= 6 ? `$${10 ** (t - 6)}m` : `$${10 ** (t - 3)}k`;
  return (
    <figure>
      <div className="scroll">
        <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxWidth: 460 }} role="img"
             aria-label="Scatter of NOAA flood damage against NFIP paid claims by county">
          <line x1={sx(lo)} y1={sy(lo)} x2={sx(hi)} y2={sy(hi)} stroke={FAINT}
                strokeDasharray="5 5" strokeWidth={1} />
          {ticks.map((t) => (
            <g key={t}>
              <line x1={sx(t)} y1={H - P} x2={sx(t)} y2={16} stroke={RULE} />
              <line x1={P} y1={sy(t)} x2={W - 16} y2={sy(t)} stroke={RULE} />
              <text x={sx(t)} y={H - P + 18} fill={FAINT} fontSize={11} textAnchor="middle"
                    fontFamily="var(--font-mono), monospace">{fmt(t)}</text>
              <text x={P - 8} y={sy(t) + 4} fill={FAINT} fontSize={11} textAnchor="end"
                    fontFamily="var(--font-mono), monospace">{fmt(t)}</text>
            </g>
          ))}
          {pts.map(([a, b], i) => (
            <circle key={i} cx={sx(a)} cy={sy(b)} r={2.6} fill={ACCENT} opacity={0.42} />
          ))}
          <text x={(W + P) / 2} y={H - 10} fill={FAINT} fontSize={12} textAnchor="middle">
            NOAA storm reports — flood damage
          </text>
          <text x={14} y={H / 2} fill={FAINT} fontSize={12} textAnchor="middle"
                transform={`rotate(-90 14 ${H / 2})`}>
            NFIP insurance claims paid
          </text>
        </svg>
      </div>
      <figcaption>
        One point per county, 2020 onward, both axes logarithmic; only counties
        where both records show loss. The dashed line is perfect agreement.
        Spearman between the two is {RESULTS.flood.instrumentAgreement} across all
        counties and {RESULTS.flood.instrumentAgreementBoth} among these{" "}
        {RESULTS.flood.nBoth.toLocaleString()}. A further {RESULTS.flood.noaaOnly}{" "}
        counties have storm-reported flood damage and no insurance claim;{" "}
        {RESULTS.flood.nfipOnly} have claims and no storm-reported damage.
      </figcaption>
    </figure>
  );
}

/* ------------------------------------------------------------------ */
/* The reversal                                                        */
/* ------------------------------------------------------------------ */
export function ReversalChart() {
  const rows = RESULTS.flood.rows;
  const W = 860;
  const rowH = 46;
  const H = rows.length * rowH + 60;
  const L = 250;
  const max = 0.75;
  const bw = (v: number) => (v / max) * (W - L - 90);
  const colour = (k: string) => (k === "index" ? ACCENT : k === "same" ? BAD : COOL);
  return (
    <figure>
      <div className="scroll">
        <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
             aria-label="Predictor performance against each flood instrument">
          <text x={L} y={16} fill={FAINT} fontSize={11}
                fontFamily="var(--font-mono), monospace">
            PREDICTING NFIP CLAIMS (the independent record)
          </text>
          {rows.map((r, i) => {
            const y = 30 + i * rowH;
            return (
              <g key={r.label}>
                <text x={L - 12} y={y + 17} fill="#eef0f5" fontSize={13} textAnchor="end">
                  {r.label}
                </text>
                <rect x={L} y={y} width={Math.max(bw(r.nfip), 1)} height={22}
                      fill={colour(r.kind)} rx={2} />
                <text x={L + bw(r.nfip) + 10} y={y + 17} fill={colour(r.kind)} fontSize={13}
                      fontWeight={700} fontFamily="var(--font-mono), monospace">
                  {r.nfip.toFixed(3)}
                </text>
                <rect x={L} y={y + 24} width={Math.max(bw(r.noaa), 1)} height={8}
                      fill={colour(r.kind)} opacity={0.34} rx={2} />
                <text x={L + bw(r.noaa) + 10} y={y + 32} fill={FAINT} fontSize={10}
                      fontFamily="var(--font-mono), monospace">
                  {r.noaa.toFixed(3)} vs NOAA
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <div className="legend">
        <span><i style={{ background: ACCENT }} />The index</span>
        <span><i style={{ background: BAD }} />Naive, built from the same record it is tested on</span>
        <span><i style={{ background: COOL }} />Naive, built from the other record</span>
      </div>
      <figcaption>
        Solid bars score against NFIP claims; faint bars against NOAA storm
        reports. The two naive rows are the same idea — extrapolate the last
        decade — differing only in which record supplied that decade. Tested on
        the record it came from, the naive baseline beats the index. Tested across
        records, it does not.
      </figcaption>
    </figure>
  );
}

/* ------------------------------------------------------------------ */
/* Where the index's weakness sits                                     */
/* ------------------------------------------------------------------ */
export function SplitChart() {
  const hz = RESULTS.hazards.filter(
    (h) => h.aucIndex !== null && h.magIndex !== null,
  );
  const W = 860;
  const colW = W / 2 - 24;
  const rowH = 27;
  const H = hz.length * rowH + 74;
  const L = 132;
  const mid = W / 2 + 24;

  const bar = (x0: number, v: number, span: number, base = 0.5) => {
    const half = span / 2;
    const c = x0 + half;
    const d = ((v - base) / base) * half;
    return { x: d >= 0 ? c : c + d, w: Math.max(Math.abs(d), 1.2), c };
  };

  return (
    <figure>
      <div className="scroll">
        <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
             aria-label="Index skill split into discrimination and magnitude">
          <text x={L} y={14} fill="#eef0f5" fontSize={12} fontWeight={700}>
            Which counties get hit
          </text>
          <text x={L} y={28} fill={FAINT} fontSize={10}>
            AUC, 0.50 is a coin toss
          </text>
          <text x={mid} y={14} fill="#eef0f5" fontSize={12} fontWeight={700}>
            How big the loss is, once hit
          </text>
          <text x={mid} y={28} fill={FAINT} fontSize={10}>
            rank correlation among counties with loss
          </text>

          {hz.map((h, i) => {
            const y = 44 + i * rowH;
            const a = bar(L, h.aucIndex as number, colW - 40);
            const an = bar(L, h.aucNaive as number, colW - 40);
            const m = bar(mid, ((h.magIndex as number) + 0.5) as number, colW - 40);
            const mn = bar(mid, ((h.magNaive as number) + 0.5) as number, colW - 40);
            const below = (h.aucIndex as number) < 0.5;
            return (
              <g key={h.code}>
                <text x={L - 10} y={y + 12} fill={below ? "#f2938c" : "#eef0f5"}
                      fontSize={12} textAnchor="end">{h.name}</text>
                <line x1={a.c} y1={y - 1} x2={a.c} y2={y + 18} stroke={FAINT} strokeWidth={1} />
                <rect x={an.x} y={y + 11} width={an.w} height={5} fill={COOL} opacity={0.75} rx={1} />
                <rect x={a.x} y={y} width={a.w} height={10} fill={below ? BAD : ACCENT} rx={1} />
                <line x1={m.c} y1={y - 1} x2={m.c} y2={y + 18} stroke={FAINT} strokeWidth={1} />
                <rect x={mn.x} y={y + 11} width={mn.w} height={5} fill={COOL} opacity={0.75} rx={1} />
                <rect x={m.x} y={y} width={m.w} height={10}
                      fill={(h.magIndex as number) < 0 ? BAD : GOOD} rx={1} />
              </g>
            );
          })}
        </svg>
      </div>
      <div className="legend">
        <span><i style={{ background: ACCENT }} />Index — locating</span>
        <span><i style={{ background: GOOD }} />Index — sizing</span>
        <span><i style={{ background: COOL }} />Naive extrapolation</span>
        <span><i style={{ background: BAD }} />Index below chance</span>
      </div>
      <figcaption>
        Bars run right from the centre line when the predictor beats chance and
        left when it does not. The index wins the sizing question for eight of
        eleven hazards and the locating question for only four — and locating is
        the judgement a funding decision is made of. Cold wave runs left: the
        index ranked counties that went on to record cold-wave damage below the
        ones that did not.
      </figcaption>
    </figure>
  );
}
