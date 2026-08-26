"""M3 -- the first join. Score the index against realized loss.

Everything here is fixed by PREREGISTRATION.md v1.2:
  §3   predictor is {HAZ}_EALB + {HAZ}_EALA, outcome is property + crop damage
  §4.0 zone attribution, equal split, unmatched excluded
  §4.1 per-hazard out-of-sample window
  §4.2 Spearman, top-decile capture, calibration ratio, bootstrap BY STATE
  §4.3 supported / weak / not supported thresholds
  §5   three reference predictors, naive extrapolation foremost

Nothing below chooses a threshold. They were chosen before this ran.
"""
import os
import numpy as np
import pandas as pd
import pyogrio
from scipy import stats

import m2_zone_attribution as m2

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "m3")
GDB = os.path.join(HERE, "..", "data", "cache", "NRI_GDB_Counties",
                   "NRI_GDB_Counties.gdb")

RHO_SUPPORTED, RHO_LB, RHO_WEAK = 0.5, 0.3, 0.2
NBOOT, SEED = 2000, 20260826
PRE_START, PRE_END = 2010, 2019          # naive-extrapolation window, pre every boundary


def load_index():
    _, tbl = pyogrio.read_arrow(GDB, layer="NRI_Counties", read_geometry=False)
    df = tbl.to_pandas()
    df["fips"] = df["STCOFIPS"].astype(str).str.zfill(5) if "STCOFIPS" in df else \
                 df["COUNTYFIPS"].astype(str).str.zfill(5)
    return df


def attributed_damage(years):
    """Re-run the M2 attribution restricted to `years`, returning county x hazard."""
    df = m2.load_events()
    df = df[df.YEAR.between(*years)].copy()
    df["sf"] = df.STATE_FIPS.astype(int).map("%02d".__mod__)
    cw = pd.read_csv(os.path.join(HERE, "..", "data", "cache", "zone_county.dbx"),
                     sep="|", header=None, dtype=str,
                     names=["ST", "ZONE", "CWA", "NAME", "STATE_ZONE", "COUNTY",
                            "FIPS", "TZ", "FE", "LAT", "LON"])
    cw["sf"] = cw.FIPS.str[:2]
    cw["zk"] = cw.sf + "Z" + cw.ZONE.str.zfill(3)
    zone_map = cw.groupby("zk").FIPS.apply(list).to_dict()
    cty = cw[["sf", "COUNTY", "FIPS"]].drop_duplicates()
    cty["key"] = cty.sf + "|" + cty.COUNTY.map(m2.norm_name)
    name_map = cty.groupby("key").FIPS.apply(lambda s: sorted(set(s))).to_dict()

    z = df[df.CZ_TYPE == "Z"].copy()
    z["zk"] = z.sf + "Z" + z.CZ_FIPS.astype(int).map("%03d".__mod__)
    z["fips_list"] = z.zk.map(zone_map)
    need = z.fips_list.isna()
    z.loc[need, "fips_list"] = (z.loc[need, "sf"] + "|"
                                + z.loc[need, "CZ_NAME"].map(m2.norm_name)).map(name_map)
    c = df[df.CZ_TYPE == "C"].copy()
    c["fips_list"] = (c.STATE_FIPS.astype(int) * 1000
                      + c.CZ_FIPS.astype(int)).map("%05d".__mod__).map(lambda x: [x])

    a = pd.concat([c, z], ignore_index=True)
    a = a[a.fips_list.notna()].copy()
    a["haz"] = a.EVENT_TYPE.map(m2.EVENT_TO_HAZ)
    a = a[a.haz.notna()].copy()
    a["share"] = a.dmg / a.fips_list.map(len)
    a = a.explode("fips_list").rename(columns={"fips_list": "fips"})
    return a.groupby(["fips", "haz"], as_index=False)["share"].sum() \
            .rename(columns={"share": "damage"})


def boot_spearman(x, y, states, rng):
    """Bootstrap Spearman, resampling STATES (§4.2) -- losses within a state
    share weather and reporting practice."""
    uniq = np.unique(states)
    idx_by_state = {s: np.where(states == s)[0] for s in uniq}
    out = []
    for _ in range(NBOOT):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_state[s] for s in pick])
        if len(idx) < 10:
            continue
        xv, yv = x[idx], y[idx]
        if np.all(xv == xv[0]) or np.all(yv == yv[0]):
            continue
        out.append(stats.spearmanr(xv, yv).statistic)
    return (np.nanpercentile(out, 2.5), np.nanpercentile(out, 97.5)) if out else (np.nan, np.nan)


def verdict(rho, lb):
    if rho >= RHO_SUPPORTED and lb > RHO_LB:
        return "SUPPORTED"
    if rho < RHO_WEAK or lb <= 0:
        return "NOT SUPPORTED"
    return "WEAK"


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(SEED)

    print("loading index ...")
    nri = load_index()
    print("  %d counties" % len(nri))

    print("building naive-extrapolation baseline (%d-%d) ..." % (PRE_START, PRE_END))
    pre = attributed_damage((PRE_START, PRE_END)).rename(columns={"damage": "pre_damage"})

    oos = pd.read_parquet(os.path.join(HERE, "..", "data", "m2",
                                       "county_year_hazard_damage.parquet"))
    obs = oos.groupby(["fips", "haz"], as_index=False).damage.sum()

    hazards = sorted(set(obs.haz) & set(m2.HOLDOUT_START))
    rows = []
    for h in hazards:
        eb, ea = "%s_EALB" % h, "%s_EALA" % h
        if eb not in nri.columns:
            continue
        base = nri[["fips", "STATEABBRV", "BUILDVALUE", "POPULATION", eb]].copy()
        base["eal"] = pd.to_numeric(nri[eb], errors="coerce").fillna(0)
        if ea in nri.columns:
            base["eal"] += pd.to_numeric(nri[ea], errors="coerce").fillna(0)
        base = base[base.eal > 0]                      # index says this hazard applies here
        if len(base) < 100:
            continue

        d = base.merge(obs[obs.haz == h][["fips", "damage"]], on="fips", how="left")
        d["damage"] = d.damage.fillna(0.0)
        d = d.merge(pre[pre.haz == h][["fips", "pre_damage"]], on="fips", how="left")
        d["pre_damage"] = d.pre_damage.fillna(0.0)
        d["BUILDVALUE"] = pd.to_numeric(d.BUILDVALUE, errors="coerce").fillna(0)
        d["POPULATION"] = pd.to_numeric(d.POPULATION, errors="coerce").fillna(0)

        y = d.damage.to_numpy(float)
        st = d.STATEABBRV.to_numpy()
        if np.all(y == 0):
            continue

        res = {"haz": h, "counties": len(d), "with_loss": int((y > 0).sum()),
               "realized": y.sum(),
               "years": int(oos[oos.haz == h].YEAR.nunique()),
               "eal_annual": d.eal.sum()}
        for name, col in [("index", "eal"), ("buildvalue", "BUILDVALUE"),
                          ("population", "POPULATION"), ("naive_past", "pre_damage")]:
            x = d[col].to_numpy(float)
            rho = stats.spearmanr(x, y).statistic
            res["rho_" + name] = rho
            if name == "index":
                lb, ub = boot_spearman(x, y, st, rng)
                res["lb"], res["ub"] = lb, ub
                res["verdict"] = verdict(rho, lb)
                top = d.nlargest(max(1, len(d) // 10), col)
                res["top10_capture"] = 100 * top.damage.sum() / y.sum() if y.sum() else np.nan
                res["calibration"] = y.sum() / (d.eal.sum() * res["years"]) if d.eal.sum() else np.nan
        rows.append(res)

    r = pd.DataFrame(rows).sort_values("realized", ascending=False)
    pd.set_option("display.width", 250)

    print("\n" + "=" * 100)
    print("PER-HAZARD RESULT  (predictor = EALB + EALA, out-of-sample only)")
    print("=" * 100)
    show = r[["haz", "counties", "with_loss", "years", "realized", "rho_index",
              "lb", "ub", "verdict"]].copy()
    show["realized"] = show.realized.map(lambda v: "$%.3gbn" % (v / 1e9))
    print(show.to_string(index=False, float_format=lambda x: "%.3f" % x))

    print("\n" + "=" * 100)
    print("AGAINST THE REFERENCE PREDICTORS  (§5) -- Spearman rho")
    print("=" * 100)
    ref = r[["haz", "rho_index", "rho_naive_past", "rho_buildvalue", "rho_population"]].copy()
    ref["beats_naive"] = np.where(ref.rho_index > ref.rho_naive_past, "yes", "NO")
    ref["beats_all"] = np.where(
        (ref.rho_index > ref.rho_naive_past) & (ref.rho_index > ref.rho_buildvalue)
        & (ref.rho_index > ref.rho_population), "yes", "NO")
    print(ref.to_string(index=False, float_format=lambda x: "%.3f" % x))

    print("\n" + "=" * 100)
    print("CALIBRATION AND CAPTURE")
    print("=" * 100)
    cal = r[["haz", "top10_capture", "calibration", "eal_annual", "realized", "years"]].copy()
    cal["eal_over_window"] = cal.eal_annual * cal.years
    cal = cal[["haz", "top10_capture", "calibration", "eal_over_window", "realized"]]
    cal["eal_over_window"] = cal.eal_over_window.map(lambda v: "$%.3gbn" % (v / 1e9))
    cal["realized"] = cal.realized.map(lambda v: "$%.3gbn" % (v / 1e9))
    print(cal.to_string(index=False, float_format=lambda x: "%.3f" % x))

    r.to_csv(os.path.join(OUT, "per_hazard_scores.csv"), index=False)
    print("\nwrote data/m3/per_hazard_scores.csv")


if __name__ == "__main__":
    main()
