"""M1 -- reporting completeness of NOAA Storm Events damage figures.

PREREGISTRATION.md §3 requires this BEFORE any correlation is computed. A zero
in DAMAGE_PROPERTY can mean 'no loss' or 'nobody recorded a loss', and the two
are not distinguishable. If reporting practice varies by state, that variation
would be read as the risk index being wrong in those states.

§6 kill check: if completeness is below 60% nationally, the primary analysis is
reported as bounded rather than point-estimated.

NOTHING HERE TOUCHES THE INDEX. No correlation, no ranking, no join to EAL.
"""
import glob
import gzip
import os
import re
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
NOAA = os.path.join(HERE, "..", "data", "cache", "noaa")
OUT = os.path.join(HERE, "..", "data", "m1")

USE = ["BEGIN_YEARMONTH", "EPISODE_ID", "EVENT_ID", "STATE", "STATE_FIPS",
       "YEAR", "EVENT_TYPE", "CZ_TYPE", "CZ_FIPS", "CZ_NAME",
       "DAMAGE_PROPERTY", "DAMAGE_CROPS"]

MULT = {"": 1.0, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12, "H": 1e2}


def parse_damage(v):
    """Return (value, reported). reported=False means the field was blank."""
    if v is None:
        return np.nan, False
    s = str(v).strip()
    if s == "" or s.lower() in ("nan", "none"):
        return np.nan, False
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)\s*([KMBTHkmbth]?)", s)
    if not m:
        return np.nan, False
    return float(m.group(1)) * MULT[m.group(2).upper()], True


def load():
    frames = []
    for f in sorted(glob.glob(os.path.join(NOAA, "*.csv.gz"))):
        with gzip.open(f, "rt", encoding="utf-8", errors="replace") as fh:
            df = pd.read_csv(fh, usecols=lambda c: c in USE, low_memory=False)
        frames.append(df)
        print("  %s -> %d rows" % (os.path.basename(f)[-24:], len(df)))
    return pd.concat(frames, ignore_index=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    print("loading NOAA Storm Events ...")
    df = load()
    print("total events: %d" % len(df))

    pv, pr = zip(*df["DAMAGE_PROPERTY"].map(parse_damage))
    cv, cr = zip(*df["DAMAGE_CROPS"].map(parse_damage))
    df["prop"], df["prop_rep"] = pv, pr
    df["crop"], df["crop_rep"] = cv, cr
    df["dmg"] = df[["prop", "crop"]].sum(axis=1, min_count=1)
    df["reported"] = df["prop_rep"] | df["crop_rep"]

    print("\n" + "=" * 72)
    print("1. EVENT-LEVEL REPORTING")
    n = len(df)
    print("  events                          : %d" % n)
    print("  damage field populated          : %d (%.1f%%)" % (df.reported.sum(), 100 * df.reported.mean()))
    print("  populated AND > 0               : %d (%.1f%%)"
          % ((df.reported & (df.dmg > 0)).sum(), 100 * (df.reported & (df.dmg > 0)).mean()))
    print("  populated but exactly 0         : %d (%.1f%%)"
          % ((df.reported & (df.dmg == 0)).sum(), 100 * (df.reported & (df.dmg == 0)).mean()))
    print("  blank (no figure at all)        : %d (%.1f%%)"
          % ((~df.reported).sum(), 100 * (~df.reported).mean()))

    print("\n2. GEOGRAPHY -- can an event be tied to a county at all?")
    ct = df.CZ_TYPE.value_counts(dropna=False)
    for k, v in ct.items():
        print("  CZ_TYPE=%-4s %8d (%.1f%%)" % (k, v, 100 * v / n))
    print("  NOTE: only CZ_TYPE='C' carries a county FIPS. 'Z' is a forecast")
    print("        zone and 'M' is marine; neither maps cleanly to a county.")

    cty = df[df.CZ_TYPE == "C"].copy()
    cty = cty[cty.STATE_FIPS.notna() & cty.CZ_FIPS.notna()]
    cty["fips"] = (cty.STATE_FIPS.astype(int) * 1000 + cty.CZ_FIPS.astype(int)).map("%05d".__mod__)
    print("  county-coded events             : %d (%.1f%% of all)" % (len(cty), 100 * len(cty) / n))
    print("  distinct counties seen          : %d" % cty.fips.nunique())

    print("\n3. COUNTY-YEAR COMPLETENESS  (the PREREGISTRATION §3 metric)")
    cy = cty.groupby(["fips", "YEAR"]).agg(
        events=("EVENT_ID", "size"),
        any_reported=("reported", "any"),
        total=("dmg", "sum")).reset_index()
    print("  county-years with >=1 event     : %d" % len(cy))
    print("  ... carrying any damage figure  : %d (%.1f%%)"
          % (cy.any_reported.sum(), 100 * cy.any_reported.mean()))
    print("  ... with total damage > 0       : %d (%.1f%%)"
          % ((cy.total > 0).sum(), 100 * (cy.total > 0).mean()))

    print("\n4. PER-STATE VARIATION  (the part that would masquerade as risk)")
    st = cty.groupby("STATE").agg(
        events=("EVENT_ID", "size"),
        pct_reported=("reported", "mean")).reset_index()
    st["pct_reported"] *= 100
    st = st[st.events >= 200].sort_values("pct_reported")
    print("  states with >=200 county-coded events: %d" % len(st))
    print("\n  LOWEST reporting rates:")
    for _, r in st.head(8).iterrows():
        print("    %-22s %6d events  %5.1f%% populated" % (r.STATE, r.events, r.pct_reported))
    print("\n  HIGHEST reporting rates:")
    for _, r in st.tail(8).iterrows():
        print("    %-22s %6d events  %5.1f%% populated" % (r.STATE, r.events, r.pct_reported))
    print("\n  spread: %.1f pp between highest and lowest"
          % (st.pct_reported.max() - st.pct_reported.min()))

    print("\n5. BY YEAR  (2026 is partial -- reported, not dropped)")
    yr = cty.groupby("YEAR").agg(events=("EVENT_ID", "size"),
                                 pct_reported=("reported", "mean"),
                                 total=("dmg", "sum")).reset_index()
    for _, r in yr.iterrows():
        print("  %d  events=%7d  populated=%5.1f%%  total=$%.4g" %
              (r.YEAR, r.events, 100 * r.pct_reported, r.total))

    print("\n6. VERDICT AGAINST PREREGISTRATION §3")
    nat = 100 * cy.any_reported.mean()
    print("  national county-year completeness: %.1f%%" % nat)
    print("  threshold                        : 60.0%%")
    print("  -> %s" % ("PASS - point estimates permitted" if nat >= 60
                       else "FAIL - results must be reported as BOUNDED"))

    cy.to_parquet(os.path.join(OUT, "county_year_damage.parquet"), index=False)
    st.to_csv(os.path.join(OUT, "state_reporting_rates.csv"), index=False)
    print("\nwrote data/m1/county_year_damage.parquet and state_reporting_rates.csv")


if __name__ == "__main__":
    main()
