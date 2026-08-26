"""M6 -- NFIP claims as an instrument independent of NOAA.

Everything through M5 rests on NOAA Storm Events, and NOAA shares its lineage
with SHELDUS, the index's own historic-loss input. Nothing has been checked
against an instrument the index did not partly come from.

NFIP claims are insurance records, not storm reports: a different collector, a
different incentive, a different failure mode. They cover flood only.

PREREGISTRATION.md §3 carries NFIP as the independent read; §6 makes disagreement
between the two instruments a MEASUREMENT finding to be published as one, not
resolved by picking the more convenient.
"""
import json
import os
import time
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
from scipy import stats

import m3_score as m3

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "data", "cache")
OUT = os.path.join(HERE, "..", "data", "m6")
UA = {"User-Agent": "actuary-research/0.1"}
API = "https://www.fema.gov/api/open/v2/FimaNfipClaims"
PAGE = 10000
FIELDS = "dateOfLoss,countyCode,amountPaidOnBuildingClaim,amountPaidOnContentsClaim"


def fetch_claims():
    path = os.path.join(CACHE, "nfip_claims_2010on.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    rows, skip = [], 0
    while True:
        q = urllib.parse.urlencode({
            "$top": PAGE, "$skip": skip, "$select": FIELDS,
            "$filter": "dateOfLoss ge '2010-01-01'", "$orderby": "id"})
        req = urllib.request.Request(API + "?" + q, headers=UA)
        for attempt in range(4):
            try:
                d = json.load(urllib.request.urlopen(req, timeout=300))
                break
            except Exception as e:
                if attempt == 3:
                    raise
                time.sleep(3 * (attempt + 1))
        batch = d.get("FimaNfipClaims", [])
        if not batch:
            break
        rows.extend(batch)
        skip += PAGE
        if skip % 100000 == 0:
            print("  %d ..." % len(rows))
    df = pd.DataFrame(rows)
    df.to_parquet(path, index=False)
    return df


def main():
    os.makedirs(OUT, exist_ok=True)
    print("fetching NFIP claims (2010 onward) ...")
    cl = fetch_claims()
    print("  %d claims" % len(cl))

    cl["paid"] = (pd.to_numeric(cl.amountPaidOnBuildingClaim, errors="coerce").fillna(0)
                  + pd.to_numeric(cl.amountPaidOnContentsClaim, errors="coerce").fillna(0))
    cl["year"] = pd.to_datetime(cl.dateOfLoss, errors="coerce", utc=True).dt.year
    cl["fips"] = cl.countyCode.astype(str).str.extract(r"(\d{5})")[0]
    cl = cl[cl.fips.notna() & cl.year.notna()]
    print("  usable: %d claims, $%.4g paid, %d counties"
          % (len(cl), cl.paid.sum(), cl.fips.nunique()))

    # RFLD boundary is 2019 -> out-of-sample is 2020 onward
    oosn = cl[cl.year >= 2020].groupby("fips", as_index=False).paid.sum() \
             .rename(columns={"paid": "nfip_oos"})
    pren = cl[cl.year.between(2010, 2019)].groupby("fips", as_index=False).paid.sum() \
             .rename(columns={"paid": "nfip_pre"})
    print("  out-of-sample 2020+: $%.4g across %d counties"
          % (oosn.nfip_oos.sum(), len(oosn)))

    nri = m3.load_index()
    noaa = pd.read_parquet(os.path.join(HERE, "..", "data", "m2",
                                        "county_year_hazard_damage.parquet"))
    noaa_f = noaa[noaa.haz == "RFLD"].groupby("fips", as_index=False).damage.sum() \
                 .rename(columns={"damage": "noaa_oos"})
    noaa_pre = m3.attributed_damage((2010, 2019))
    noaa_pre = noaa_pre[noaa_pre.haz == "RFLD"][["fips", "damage"]] \
        .rename(columns={"damage": "noaa_pre"})

    d = nri[["fips", "STATEABBRV"]].copy()
    d["eal_rfld"] = (pd.to_numeric(nri["RFLD_EALB"], errors="coerce").fillna(0)
                     + pd.to_numeric(nri["RFLD_EALA"], errors="coerce").fillna(0))
    # CFLD carries no agriculture component (NRI_HazardInfo: EAL_Agriculture = 0)
    cfld = pd.to_numeric(nri["CFLD_EALB"], errors="coerce").fillna(0)
    if "CFLD_EALA" in nri.columns:
        cfld = cfld + pd.to_numeric(nri["CFLD_EALA"], errors="coerce").fillna(0)
    d["eal_flood"] = d.eal_rfld + cfld
    for t in (oosn, pren, noaa_f, noaa_pre):
        d = d.merge(t, on="fips", how="left")
    d = d.fillna({"nfip_oos": 0, "nfip_pre": 0, "noaa_oos": 0, "noaa_pre": 0})
    d = d[d.eal_rfld > 0]
    print("  panel: %d counties with RFLD EAL > 0" % len(d))

    def auc(pred, hit):
        a, b = pred[hit], pred[~hit]
        if len(a) == 0 or len(b) == 0:
            return np.nan
        return stats.mannwhitneyu(a, b, alternative="two-sided").statistic / (len(a) * len(b))

    print("\n" + "=" * 92)
    print("1. DO THE TWO INSTRUMENTS AGREE?  (out-of-sample flood loss per county)")
    print("=" * 92)
    print("  Spearman, NOAA flood damage vs NFIP paid           : %.3f"
          % stats.spearmanr(d.noaa_oos, d.nfip_oos).statistic)
    both = d[(d.noaa_oos > 0) & (d.nfip_oos > 0)]
    print("  ... among counties positive in BOTH (n=%d)         : %.3f"
          % (len(both), stats.spearmanr(both.noaa_oos, both.nfip_oos).statistic))
    print("  counties with NOAA loss but no NFIP claim          : %d"
          % ((d.noaa_oos > 0) & (d.nfip_oos == 0)).sum())
    print("  counties with NFIP claim but no NOAA loss          : %d"
          % ((d.nfip_oos == 0) & (d.noaa_oos > 0)).sum() if False else
          "%d" % ((d.nfip_oos > 0) & (d.noaa_oos == 0)).sum())
    print("  total NOAA flood $%.4g  vs  NFIP paid $%.4g"
          % (d.noaa_oos.sum(), d.nfip_oos.sum()))

    print("\n" + "=" * 92)
    print("2. THE TEST, RERUN ON THE INDEPENDENT INSTRUMENT")
    print("=" * 92)
    hdr = "  %-34s %9s %9s %9s" % ("predictor", "rho", "AUC", "mag")
    for outcome, oname, naive_col in [("nfip_oos", "NFIP paid (independent)", "nfip_pre"),
                                      ("noaa_oos", "NOAA damage (M3 baseline)", "noaa_pre")]:
        y = d[outcome].to_numpy(float)
        hit = y > 0
        sub = d[y > 0]
        print("\n  OUTCOME: %s   (%d of %d counties with loss)"
              % (oname, hit.sum(), len(d)))
        print(hdr)
        for label, col in [("index EAL (riverine)", "eal_rfld"),
                           ("index EAL (riverine + coastal)", "eal_flood"),
                           ("naive: same instrument 2010-19", naive_col),
                           ("naive: other instrument 2010-19",
                            "noaa_pre" if outcome == "nfip_oos" else "nfip_pre")]:
            x = d[col].to_numpy(float)
            mag = (stats.spearmanr(sub[col], sub[outcome]).statistic
                   if len(sub) >= 30 else np.nan)
            print("  %-34s %9.3f %9.3f %9.3f"
                  % (label, stats.spearmanr(x, y).statistic, auc(x, hit), mag))

    d.to_csv(os.path.join(OUT, "flood_two_instruments.csv"), index=False)
    print("\nwrote data/m6/flood_two_instruments.csv")


if __name__ == "__main__":
    main()
