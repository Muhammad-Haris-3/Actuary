"""M2 -- attribute NOAA zone-coded damage to counties.

PREREGISTRATION.md §4.0 fixes the rules. M1 left 37.7% of zone damage unmatched
because the NWS crosswalk is an April 2026 snapshot while events begin in 2020,
and NWS renumbers zones.

This adds a NAME-based second pass, and -- the point of the exercise -- MEASURES
its accuracy against the zones that already match by id, rather than assuming it.
A name match is weaker evidence than an id match. Which pass produced each row is
recorded, so the join stays auditable.

Emits data/m2/county_year_hazard_damage.parquet.
"""
import glob
import gzip
import os
import re
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "data", "cache")
OUT = os.path.join(HERE, "..", "data", "m2")

USE = ["EVENT_ID", "STATE", "STATE_FIPS", "YEAR", "EVENT_TYPE",
       "CZ_TYPE", "CZ_FIPS", "CZ_NAME", "DAMAGE_PROPERTY", "DAMAGE_CROPS"]
MULT = {"": 1.0, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12, "H": 1e2}

# Directional and qualifier words NWS prepends to a county name when it splits
# one county into several forecast zones. Stripping them is what makes
# "LOWER LAFOURCHE" resolve to Lafourche Parish.
QUAL = {"UPPER", "LOWER", "NORTH", "SOUTH", "EAST", "WEST", "CENTRAL",
        "COASTAL", "INLAND", "NORTHERN", "SOUTHERN", "EASTERN", "WESTERN",
        "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST", "INTERIOR",
        "METRO", "GREATER", "MOUNTAINS", "VALLEY", "PLATEAU", "FOOTHILLS"}

# NOAA EVENT_TYPE -> NRI hazard prefix. Only mappings that are unambiguous.
EVENT_TO_HAZ = {
    "Hurricane (Typhoon)": "HRCN", "Hurricane": "HRCN", "Tropical Storm": "HRCN",
    "Tropical Depression": "HRCN", "Storm Surge/Tide": "HRCN",
    "Tornado": "TRND",
    "Flash Flood": "RFLD", "Flood": "RFLD",
    "Coastal Flood": "CFLD",
    "Hail": "HAIL",
    "Lightning": "LTNG",
    "Wildfire": "WFIR",
    "Drought": "DRGT",
    "High Wind": "SWND", "Strong Wind": "SWND", "Thunderstorm Wind": "SWND",
    "Excessive Heat": "HWAV", "Heat": "HWAV",
    "Extreme Cold/Wind Chill": "CWAV", "Cold/Wind Chill": "CWAV",
    "Frost/Freeze": "CWAV",
    "Winter Storm": "WNTW", "Winter Weather": "WNTW", "Blizzard": "WNTW",
    "Heavy Snow": "WNTW", "Lake-Effect Snow": "WNTW", "Sleet": "WNTW",
    "Ice Storm": "ISTM",
    "Avalanche": "AVLN",
    "Landslide": "LNDS", "Debris Flow": "LNDS",
    "Tsunami": "TSUN",
    "Volcanic Ash": "VLCN", "Volcanic Ashfall": "VLCN",
    "Earthquake": "ERQK",
}

# PREREGISTRATION.md §4.1 / FINDINGS F0-T2: first year strictly after the
# binding boundary, per hazard.
HOLDOUT_START = {
    "LTNG": 2020, "ISTM": 2020, "AVLN": 2020, "RFLD": 2020,
    "CWAV": 2022, "HWAV": 2022, "WNTW": 2022, "DRGT": 2022, "HAIL": 2022,
    "SWND": 2022, "LNDS": 2022, "TRND": 2022, "TSUN": 2022, "HRCN": 2022,
    "ERQK": 2022, "WFIR": 2022,
    "VLCN": 2023,
    "CFLD": None,  # no declared period of record -- excluded
}


def parse_damage(v):
    s = str(v).strip()
    if s == "" or s.lower() in ("nan", "none"):
        return 0.0
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)\s*([KMBTHkmbth]?)", s)
    return float(m.group(1)) * MULT[m.group(2).upper()] if m else 0.0


def norm_name(s):
    s = re.sub(r"[^A-Z ]", " ", str(s).upper())
    toks = [t for t in s.split() if t]
    while toks and toks[0] in QUAL:
        toks = toks[1:]
    while toks and toks[-1] in QUAL:
        toks = toks[:-1]
    return " ".join(toks)


def load_events():
    fr = []
    for f in sorted(glob.glob(os.path.join(CACHE, "noaa", "*.csv.gz"))):
        with gzip.open(f, "rt", encoding="utf-8", errors="replace") as fh:
            fr.append(pd.read_csv(fh, usecols=lambda c: c in USE, low_memory=False))
    df = pd.concat(fr, ignore_index=True)
    df["dmg"] = df.DAMAGE_PROPERTY.map(parse_damage) + df.DAMAGE_CROPS.map(parse_damage)
    return df[df.STATE_FIPS.notna() & df.CZ_FIPS.notna()].copy()


def main():
    os.makedirs(OUT, exist_ok=True)
    df = load_events()
    df["sf"] = df.STATE_FIPS.astype(int).map("%02d".__mod__)

    cw = pd.read_csv(os.path.join(CACHE, "zone_county.dbx"), sep="|", header=None,
                     dtype=str, names=["ST", "ZONE", "CWA", "NAME", "STATE_ZONE",
                                       "COUNTY", "FIPS", "TZ", "FE", "LAT", "LON"])
    cw["sf"] = cw.FIPS.str[:2]
    cw["zk"] = cw.sf + "Z" + cw.ZONE.str.zfill(3)

    zone_map = cw.groupby("zk").FIPS.apply(list).to_dict()

    # county-name lookup, per state, from the crosswalk itself
    cty = cw[["sf", "COUNTY", "FIPS"]].drop_duplicates()
    cty["key"] = cty.sf + "|" + cty.COUNTY.map(norm_name)
    name_map = cty.groupby("key").FIPS.apply(lambda s: sorted(set(s))).to_dict()

    # ---- pass 1: id ----------------------------------------------------
    z = df[df.CZ_TYPE == "Z"].copy()
    z["zk"] = z.sf + "Z" + z.CZ_FIPS.astype(int).map("%03d".__mod__)
    z["by_id"] = z.zk.map(zone_map)

    # ---- pass 2: name --------------------------------------------------
    z["nkey"] = z.sf + "|" + z.CZ_NAME.map(norm_name)
    z["by_name"] = z.nkey.map(name_map)

    # ---- validate pass 2 against pass 1 --------------------------------
    both = z[z.by_id.notna() & z.by_name.notna()]
    agree = both.apply(lambda r: bool(set(r.by_id) & set(r.by_name)), axis=1)
    exact = both.apply(lambda r: set(r.by_id) == set(r.by_name), axis=1)
    print("=" * 72)
    print("NAME-MATCH ACCURACY, measured against id-matched zones")
    print("  zones resolvable by BOTH id and name : %d events" % len(both))
    print("  name result overlaps id result       : %.2f%%" % (100 * agree.mean()))
    print("  name result identical to id result   : %.2f%%" % (100 * exact.mean()))
    print("  damage-weighted overlap              : %.2f%%"
          % (100 * both.dmg[agree].sum() / both.dmg.sum() if both.dmg.sum() else 0))

    # ---- assemble ------------------------------------------------------
    z["fips_list"] = z.by_id
    z["method"] = np.where(z.by_id.notna(), "zone_id", None)
    need = z.by_id.isna() & z.by_name.notna()
    z.loc[need, "fips_list"] = z.loc[need, "by_name"]
    z.loc[need, "method"] = "zone_name"
    z["method"] = z.method.fillna("unmatched")

    c = df[df.CZ_TYPE == "C"].copy()
    c["fips_list"] = (c.STATE_FIPS.astype(int) * 1000
                      + c.CZ_FIPS.astype(int)).map("%05d".__mod__).map(lambda x: [x])
    c["method"] = "county_fips"

    allev = pd.concat([c, z], ignore_index=True)
    tot = allev.dmg.sum()
    print("\nATTRIBUTION, damage-weighted")
    for m, g in allev.groupby("method"):
        print("  %-12s %8d events  $%10.4g  (%5.1f%%)" % (m, len(g), g.dmg.sum(),
                                                          100 * g.dmg.sum() / tot))
    attributed = allev[allev.method != "unmatched"]
    print("  %-12s %8d events  $%10.4g  (%5.1f%%)" % ("TOTAL ATTR", len(attributed),
          attributed.dmg.sum(), 100 * attributed.dmg.sum() / tot))

    # ---- explode, equal split (§4.0) -----------------------------------
    a = attributed.copy()
    a["n_cty"] = a.fips_list.map(len)
    a["share"] = a.dmg / a.n_cty
    a["haz"] = a.EVENT_TYPE.map(EVENT_TO_HAZ)
    unmapped = a[a.haz.isna()]
    print("\n  events with no NRI hazard mapping: %d  ($%.4g, %.2f%% of attributed)"
          % (len(unmapped), unmapped.dmg.sum(), 100 * unmapped.dmg.sum() / a.dmg.sum()))
    if len(unmapped):
        print("   ", unmapped.EVENT_TYPE.value_counts().head(6).to_dict())

    a = a[a.haz.notna()].explode("fips_list").rename(columns={"fips_list": "fips"})
    out = (a.groupby(["fips", "YEAR", "haz", "method"], as_index=False)
             .agg(damage=("share", "sum"), events=("EVENT_ID", "size")))

    # ---- apply per-hazard out-of-sample boundary -----------------------
    out["holdout_start"] = out.haz.map(HOLDOUT_START)
    oos = out[out.holdout_start.notna() & (out.YEAR >= out.holdout_start)]
    print("\nOUT-OF-SAMPLE FILTER (§4.1)")
    print("  county-year-hazard rows, all years : %d  ($%.4g)" % (len(out), out.damage.sum()))
    print("  after per-hazard boundary          : %d  ($%.4g)" % (len(oos), oos.damage.sum()))
    print("  dropped as in-sample or excluded   : $%.4g" % (out.damage.sum() - oos.damage.sum()))

    oos.to_parquet(os.path.join(OUT, "county_year_hazard_damage.parquet"), index=False)
    print("\nwrote data/m2/county_year_hazard_damage.parquet")
    return oos


if __name__ == "__main__":
    main()
