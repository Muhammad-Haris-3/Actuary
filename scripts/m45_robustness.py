"""M4 + M5 -- references decomposed, and every robustness check the
pre-registration owes.

M4  §5  the three reference predictors, scored on a tie-aware basis
M5  §4.1 the conservative variant: every hazard scored 2023 onward
    §4.0 the population-weighted apportionment variant promised as a check
    §6   reporting-rate control, formalised

M3-T4 recorded a debt: with 89% of counties reporting zero loss for the rare
hazards, Spearman is dominated by tie structure. This pays it by splitting the
question in two, which is what the zero mass actually means:

  DISCRIMINATION -- does the index know WHERE loss happens?
      AUC = P(index ranks a loss county above a no-loss county). Ties handled
      exactly; 0.5 is coin-flip.
  MAGNITUDE -- given loss happened, does it know HOW MUCH?
      Spearman among counties with loss > 0 only.

Neither replaces the pre-registered headline. Both are added beside it.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

import m2_zone_attribution as m2
import m3_score as m3

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "m45")
PRE = (2010, 2019)
CONSERVATIVE_START = 2023
PREDICTORS = [("index", "eal"), ("naive_past", "pre_damage"),
              ("buildvalue", "BUILDVALUE"), ("population", "POPULATION")]


def auc(pred, hit):
    """P(pred higher for a hit than for a miss), ties counted as half."""
    a, b = pred[hit], pred[~hit]
    if len(a) == 0 or len(b) == 0:
        return np.nan
    u = stats.mannwhitneyu(a, b, alternative="two-sided").statistic
    return u / (len(a) * len(b))


def build_panel(nri, obs, pre, haz):
    eb, ea = "%s_EALB" % haz, "%s_EALA" % haz
    if eb not in nri.columns:
        return None
    d = nri[["fips", "STATEABBRV", "BUILDVALUE", "POPULATION"]].copy()
    d["eal"] = pd.to_numeric(nri[eb], errors="coerce").fillna(0)
    if ea in nri.columns:
        d["eal"] += pd.to_numeric(nri[ea], errors="coerce").fillna(0)
    d = d[d.eal > 0]
    d = d.merge(obs[obs.haz == haz][["fips", "damage"]], on="fips", how="left")
    d["damage"] = d.damage.fillna(0.0)
    d = d.merge(pre[pre.haz == haz][["fips", "pre_damage"]], on="fips", how="left")
    d["pre_damage"] = d.pre_damage.fillna(0.0)
    for c in ("BUILDVALUE", "POPULATION"):
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    return d if len(d) >= 100 and d.damage.sum() > 0 else None


def main():
    os.makedirs(OUT, exist_ok=True)
    nri = m3.load_index()
    oos = pd.read_parquet(os.path.join(HERE, "..", "data", "m2",
                                       "county_year_hazard_damage.parquet"))
    pre = m3.attributed_damage(PRE).rename(columns={"damage": "pre_damage"})

    obs_all = oos.groupby(["fips", "haz"], as_index=False).damage.sum()
    obs_cons = (oos[oos.YEAR >= CONSERVATIVE_START]
                .groupby(["fips", "haz"], as_index=False).damage.sum())

    hazards = ["HRCN", "RFLD", "TRND", "WFIR", "HAIL", "SWND", "LTNG",
               "WNTW", "ISTM", "LNDS", "CWAV"]

    # ---------------- M4: tie-aware decomposition ----------------------
    rows = []
    for h in hazards:
        d = build_panel(nri, obs_all, pre, h)
        if d is None:
            continue
        hit = (d.damage > 0).to_numpy()
        r = {"haz": h, "n": len(d), "hits": int(hit.sum()),
             "zero_share": 100 * (1 - hit.mean())}
        for name, col in PREDICTORS:
            x = d[col].to_numpy(float)
            r["auc_" + name] = auc(x, hit)
        sub = d[d.damage > 0]
        for name, col in PREDICTORS:
            r["mag_" + name] = (stats.spearmanr(sub[col], sub.damage).statistic
                                if len(sub) >= 30 else np.nan)
        rows.append(r)
    m4 = pd.DataFrame(rows)

    pd.set_option("display.width", 250)
    print("=" * 104)
    print("M4 -- DISCRIMINATION: does the index know WHERE loss happens?")
    print("     AUC = P(predictor ranks a loss county above a no-loss county). 0.5 = coin flip.")
    print("=" * 104)
    a = m4[["haz", "n", "hits", "zero_share", "auc_index", "auc_naive_past",
            "auc_buildvalue", "auc_population"]].copy()
    a["index_wins"] = np.where(a.auc_index > a.auc_naive_past, "yes", "NO")
    print(a.to_string(index=False, float_format=lambda x: "%.3f" % x))

    print("\n" + "=" * 104)
    print("M4 -- MAGNITUDE: given loss happened, does it know HOW MUCH?")
    print("     Spearman among counties with loss > 0 only.")
    print("=" * 104)
    b = m4[["haz", "hits", "mag_index", "mag_naive_past", "mag_buildvalue",
            "mag_population"]].copy()
    b["index_wins"] = np.where(b.mag_index > b.mag_naive_past, "yes", "NO")
    print(b.to_string(index=False, float_format=lambda x: "%.3f" % x))

    # ---------------- M5a: conservative window -------------------------
    print("\n" + "=" * 104)
    print("M5 -- CONSERVATIVE VARIANT (§4.1): every hazard scored %d onward"
          % CONSERVATIVE_START)
    print("=" * 104)
    rows = []
    for h in hazards:
        da = build_panel(nri, obs_all, pre, h)
        dc = build_panel(nri, obs_cons, pre, h)
        if da is None or dc is None:
            continue
        rows.append({
            "haz": h,
            "rho_primary": stats.spearmanr(da.eal, da.damage).statistic,
            "rho_conservative": stats.spearmanr(dc.eal, dc.damage).statistic,
            "naive_primary": stats.spearmanr(da.pre_damage, da.damage).statistic,
            "naive_conservative": stats.spearmanr(dc.pre_damage, dc.damage).statistic,
            "loss_primary": da.damage.sum(), "loss_conservative": dc.damage.sum()})
    m5a = pd.DataFrame(rows)
    m5a["gap_primary"] = m5a.rho_primary - m5a.naive_primary
    m5a["gap_conservative"] = m5a.rho_conservative - m5a.naive_conservative
    print(m5a[["haz", "rho_primary", "rho_conservative", "naive_primary",
               "naive_conservative", "gap_primary", "gap_conservative"]]
          .to_string(index=False, float_format=lambda x: "%+.3f" % x))
    print("\n  hazards where the index loses to naive, primary window     : %d of %d"
          % ((m5a.gap_primary < 0).sum(), len(m5a)))
    print("  hazards where the index loses to naive, conservative window: %d of %d"
          % ((m5a.gap_conservative < 0).sum(), len(m5a)))

    # ---------------- M5b: population-weighted apportionment -----------
    print("\n" + "=" * 104)
    print("M5 -- APPORTIONMENT SENSITIVITY (§4.0): equal split vs population-weighted")
    print("=" * 104)
    pop = nri[["fips", "POPULATION"]].copy()
    pop["POPULATION"] = pd.to_numeric(pop.POPULATION, errors="coerce").fillna(0)
    popmap = dict(zip(pop.fips, pop.POPULATION))

    ev = m2.load_events()
    ev = ev[ev.YEAR >= 2020].copy()
    ev["sf"] = ev.STATE_FIPS.astype(int).map("%02d".__mod__)
    cw = pd.read_csv(os.path.join(HERE, "..", "data", "cache", "zone_county.dbx"),
                     sep="|", header=None, dtype=str,
                     names=["ST", "ZONE", "CWA", "NAME", "STATE_ZONE", "COUNTY",
                            "FIPS", "TZ", "FE", "LAT", "LON"])
    cw["sf"] = cw.FIPS.str[:2]
    cw["zk"] = cw.sf + "Z" + cw.ZONE.str.zfill(3)
    zmap = cw.groupby("zk").FIPS.apply(list).to_dict()
    cty = cw[["sf", "COUNTY", "FIPS"]].drop_duplicates()
    cty["key"] = cty.sf + "|" + cty.COUNTY.map(m2.norm_name)
    nmap = cty.groupby("key").FIPS.apply(lambda s: sorted(set(s))).to_dict()

    z = ev[ev.CZ_TYPE == "Z"].copy()
    z["zk"] = z.sf + "Z" + z.CZ_FIPS.astype(int).map("%03d".__mod__)
    z["fl"] = z.zk.map(zmap)
    nd = z.fl.isna()
    z.loc[nd, "fl"] = (z.loc[nd, "sf"] + "|" + z.loc[nd, "CZ_NAME"].map(m2.norm_name)).map(nmap)
    c = ev[ev.CZ_TYPE == "C"].copy()
    c["fl"] = (c.STATE_FIPS.astype(int) * 1000 + c.CZ_FIPS.astype(int)) \
        .map("%05d".__mod__).map(lambda x: [x])
    aa = pd.concat([c, z], ignore_index=True)
    aa = aa[aa.fl.notna()].copy()
    aa["haz"] = aa.EVENT_TYPE.map(m2.EVENT_TO_HAZ)
    aa = aa[aa.haz.notna()].copy()
    aa["hs"] = aa.haz.map(m2.HOLDOUT_START)
    aa = aa[aa.hs.notna() & (aa.YEAR >= aa.hs)]

    recs = []
    for haz, yr, dmg, fl in zip(aa.haz, aa.YEAR, aa.dmg, aa.fl):
        w = np.array([popmap.get(f, 0.0) for f in fl], float)
        w = w / w.sum() if w.sum() > 0 else np.full(len(fl), 1.0 / len(fl))
        for f, ww in zip(fl, w):
            recs.append((f, haz, dmg * ww))
    popw = pd.DataFrame(recs, columns=["fips", "haz", "damage"]) \
             .groupby(["fips", "haz"], as_index=False).damage.sum()

    rows = []
    for h in hazards:
        de = build_panel(nri, obs_all, pre, h)
        dp = build_panel(nri, popw, pre, h)
        if de is None or dp is None:
            continue
        re_, rp = (stats.spearmanr(de.eal, de.damage).statistic,
                   stats.spearmanr(dp.eal, dp.damage).statistic)
        rows.append({"haz": h, "rho_equal_split": re_, "rho_pop_weighted": rp,
                     "delta": rp - re_})
    m5b = pd.DataFrame(rows)
    print(m5b.to_string(index=False, float_format=lambda x: "%+.3f" % x))
    mx = m5b["delta"].abs().max()
    print("\n  largest shift: %.3f  (§4.0 publishes the variant only if > 0.02)" % mx)
    print("  -> %s" % ("MATERIAL, must be published" if mx > 0.02
                       else "immaterial, equal split stands"))

    m4.to_csv(os.path.join(OUT, "m4_tie_aware.csv"), index=False)
    m5a.to_csv(os.path.join(OUT, "m5_conservative.csv"), index=False)
    m5b.to_csv(os.path.join(OUT, "m5_apportionment.csv"), index=False)
    print("\nwrote data/m45/*.csv")


if __name__ == "__main__":
    main()
