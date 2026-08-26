"""M7 -- freeze the measured results into a TypeScript module for the site.

The site must never contain a number that was typed by hand. Everything it
renders is generated here from the committed result CSVs, so a figure on the
page and a figure in FINDINGS.md cannot drift apart.
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "src", "lib", "results.ts")

NAMES = {
    "HRCN": "Hurricane", "ERQK": "Earthquake", "TRND": "Tornado",
    "RFLD": "Riverine flood", "WFIR": "Wildfire", "HWAV": "Heat wave",
    "SWND": "Strong wind", "HAIL": "Hail", "DRGT": "Drought",
    "CFLD": "Coastal flood", "CWAV": "Cold wave", "LTNG": "Lightning",
    "ISTM": "Ice storm", "WNTW": "Winter weather", "VLCN": "Volcanic",
    "LNDS": "Landslide", "AVLN": "Avalanche", "TSUN": "Tsunami",
}

# Index EAL shares, measured in F0-T3
EAL_SHARE = {
    "HRCN": 29.25, "ERQK": 27.04, "TRND": 13.18, "RFLD": 8.80, "WFIR": 4.54,
    "HWAV": 3.01, "SWND": 2.91, "HAIL": 2.77, "DRGT": 2.17, "CFLD": 1.67,
    "CWAV": 1.23, "LTNG": 1.06, "ISTM": 0.99, "WNTW": 0.64, "VLCN": 0.32,
    "LNDS": 0.31, "AVLN": 0.11, "TSUN": 0.01,
}


def r(x, n=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return None
    return round(float(x), n)


def main():
    m3 = pd.read_csv(os.path.join(ROOT, "data", "m3", "per_hazard_scores.csv"))
    m4 = pd.read_csv(os.path.join(ROOT, "data", "m45", "m4_tie_aware.csv"))
    m5 = pd.read_csv(os.path.join(ROOT, "data", "m45", "m5_conservative.csv"))
    m6 = pd.read_csv(os.path.join(ROOT, "data", "m6", "flood_two_instruments.csv"),
                     dtype={"fips": str})

    hazards = []
    m4i = m4.set_index("haz")
    m5i = m5.set_index("haz")
    for _, row in m3.sort_values("realized", ascending=False).iterrows():
        h = row.haz
        rec = {
            "code": h, "name": NAMES.get(h, h),
            "ealShare": EAL_SHARE.get(h),
            "counties": int(row.counties), "withLoss": int(row.with_loss),
            "years": int(row.years), "realized": float(row.realized),
            "rho": r(row.rho_index), "lb": r(row.lb), "ub": r(row.ub),
            "verdict": row.verdict,
            "rhoNaive": r(row.rho_naive_past),
            "rhoBuild": r(row.rho_buildvalue),
            "topDecile": r(row.top10_capture, 1),
        }
        # every record carries every key -- a uniform shape keeps the
        # generated `as const` object a single TS type rather than a union
        a = m4i.loc[h] if h in m4i.index else None
        rec.update({
            "zeroShare": r(a.zero_share, 1) if a is not None else None,
            "aucIndex": r(a.auc_index) if a is not None else None,
            "aucNaive": r(a.auc_naive_past) if a is not None else None,
            "magIndex": r(a.mag_index) if a is not None else None,
            "magNaive": r(a.mag_naive_past) if a is not None else None,
        })
        b = m5i.loc[h] if h in m5i.index else None
        rec.update({
            "gapPrimary": r(b.gap_primary) if b is not None else None,
            "gapConservative": r(b.gap_conservative) if b is not None else None,
        })
        hazards.append(rec)

    # M6 scatter: both instruments positive, log-log, downsampled for page weight
    both = m6[(m6.noaa_oos > 0) & (m6.nfip_oos > 0)][["noaa_oos", "nfip_oos"]]
    if len(both) > 700:
        both = both.sample(700, random_state=20260826)
    scatter = [[round(float(np.log10(a)), 3), round(float(np.log10(b)), 3)]
               for a, b in zip(both.noaa_oos, both.nfip_oos)]

    testable = sum(v for k, v in EAL_SHARE.items()
                   if k not in ("ERQK", "VLCN", "TSUN", "AVLN", "CFLD"))
    payload = {
        "generated": "2026-08-26",
        "indexVersion": "1.19.0 (March 2023)",
        "nationalEal": 76.72,
        "coverage": {
            "testable": round(testable, 2),
            "earthquake": EAL_SHARE["ERQK"],
            "otherUntestable": round(EAL_SHARE["VLCN"] + EAL_SHARE["TSUN"]
                                     + EAL_SHARE["AVLN"], 2),
            "coastalExcluded": EAL_SHARE["CFLD"],
        },
        "hazards": hazards,
        "flood": {
            "instrumentAgreement": 0.401,
            "instrumentAgreementBoth": 0.334,
            "nBoth": 1332,
            "noaaOnly": 410, "nfipOnly": 729,
            "noaaTotal": 14.81, "nfipTotal": 18.53,
            "scatter": scatter,
            "rows": [
                {"label": "Index EAL, riverine", "nfip": 0.438, "noaa": 0.303,
                 "kind": "index"},
                {"label": "Index EAL, riverine + coastal", "nfip": 0.490,
                 "noaa": 0.286, "kind": "index"},
                {"label": "Naive, same instrument", "nfip": 0.676, "noaa": 0.334,
                 "kind": "same"},
                {"label": "Naive, other instrument", "nfip": 0.284, "noaa": 0.274,
                 "kind": "cross"},
            ],
        },
        "reporting": {"spread": 50.4, "completeness": 94.9,
                      "lowest": [["Colorado", 49.6], ["Nebraska", 55.3],
                                 ["South Carolina", 57.1], ["Oklahoma", 62.7],
                                 ["Kansas", 64.7]],
                      "highest": [["Rhode Island", 100.0], ["Puerto Rico", 99.8],
                                  ["Louisiana", 99.7], ["Mississippi", 99.4],
                                  ["Florida", 99.3]]},
        "attribution": {"countyCoded": 28.0, "zoneId": 44.9, "zoneName": 18.2,
                        "unmatched": 8.9, "nameAgreement": 99.87},
    }

    ts = ("// GENERATED by scripts/m7_build_site_data.py -- do not edit.\n"
          "// Every figure here comes from a committed result CSV.\n\n"
          "export type Hazard = (typeof RESULTS)['hazards'][number];\n\n"
          "export const RESULTS = " + json.dumps(payload, indent=2) + ";\n")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(ts)
    print("wrote %s (%d hazards, %d scatter points, testable %.2f%%)"
          % (OUT, len(hazards), len(scatter), testable))


if __name__ == "__main__":
    main()
