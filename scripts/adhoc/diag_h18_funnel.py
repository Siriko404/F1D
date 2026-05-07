"""Diagnostic: where do we lose movers vs Hasan in the 18-state subset?

Goal: identify which step in the geocode -> CD assignment -> PRisk filter
-> tertile chain causes our 248 movers (16% of 1,532 18-state firms) to
fall below Hasan's 941 movers (66% of 1,431 affected firms).

Usage:
    python scripts/adhoc/diag_h18_funnel.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(".")

HASAN_18_STATES = {
    "AZ", "FL", "GA", "NV", "SC", "TX", "UT", "WA",
    "IA", "IL", "LA", "MA", "MI", "MO", "NJ", "NY", "OH", "PA",
}

# Inputs
PATH_GEO_F1D = ROOT / "inputs/firm_geocodes/firm_lat_lon.parquet"
PATH_GEO_FULL = ROOT / "inputs/firm_geocodes/firm_lat_lon_full_compustat.parquet"
PATH_PRISK = ROOT / "inputs/FirmLevelRisk/firmquarter_2022q1.csv"
PATH_LEWIS_111 = ROOT / "inputs/Lewis2013_CD/111"
PATH_LEWIS_113 = ROOT / "inputs/Lewis2013_CD/113"

# PRisk pre-window
PRE_WINDOW_START = "2006q1"
PRE_WINDOW_END = "2010q4"


def _parse_cal_q(date_str: str) -> str | None:
    """PRisk file already uses 'yyyyqN' format. Pass-through validation."""
    try:
        s = str(date_str).strip()
        # Already cal_q format like '2002q1'
        if len(s) == 6 and s[4] == "q" and s[:4].isdigit() and s[5].isdigit():
            return s
        # YYYY-MM-DD or YYYYMMDD -> derive
        if "-" in s:
            y, m, _ = s.split("-")
        else:
            y, m = s[:4], s[4:6]
        y, m = int(y), int(m)
        q = (m - 1) // 3 + 1
        return f"{y}q{q}"
    except Exception:
        return None


def _load_cd_shapefile(directory: Path, congress: int):
    import geopandas as gpd
    files = sorted(directory.glob("*.geojson"))
    gdfs = [gpd.read_file(fp) for fp in files]
    gdf = pd.concat(gdfs, ignore_index=True)
    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs="EPSG:4269")
    gdf = gdf[(gdf["startcong"] <= congress) & (gdf["endcong"] >= congress)].copy()
    state_to_fips = {
        "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
        "California": "06", "Colorado": "08", "Connecticut": "09",
        "Delaware": "10", "District Of Columbia": "11", "Florida": "12",
        "Georgia": "13", "Hawaii": "15", "Idaho": "16", "Illinois": "17",
        "Indiana": "18", "Iowa": "19", "Kansas": "20", "Kentucky": "21",
        "Louisiana": "22", "Maine": "23", "Maryland": "24",
        "Massachusetts": "25", "Michigan": "26", "Minnesota": "27",
        "Mississippi": "28", "Missouri": "29", "Montana": "30",
        "Nebraska": "31", "Nevada": "32", "New Hampshire": "33",
        "New Jersey": "34", "New Mexico": "35", "New York": "36",
        "North Carolina": "37", "North Dakota": "38", "Ohio": "39",
        "Oklahoma": "40", "Oregon": "41", "Pennsylvania": "42",
        "Rhode Island": "44", "South Carolina": "45", "South Dakota": "46",
        "Tennessee": "47", "Texas": "48", "Utah": "49", "Vermont": "50",
        "Virginia": "51", "Washington": "53", "West Virginia": "54",
        "Wisconsin": "55", "Wyoming": "56",
    }
    gdf["statefp"] = gdf["statename"].map(state_to_fips)
    gdf["cd_str"] = gdf["district"].astype(float).astype(int).astype(str).str.zfill(2)
    gdf["state_cd"] = gdf["statefp"].astype(str) + gdf["cd_str"]
    return gdf[["statename", "statefp", "district", "state_cd", "geometry"]]


def _spatial_join(firm_pts: pd.DataFrame, cd_polys, period_label: str) -> pd.DataFrame:
    import geopandas as gpd
    from shapely.geometry import Point
    firm_pts = firm_pts.dropna(subset=["latitude", "longitude"]).copy()
    geom = [Point(lon, lat) for lon, lat in zip(firm_pts["longitude"], firm_pts["latitude"])]
    pts_gdf = gpd.GeoDataFrame(firm_pts[["gvkey"]].copy(), geometry=geom, crs="EPSG:4326")
    pts_gdf = pts_gdf.to_crs("EPSG:4269")
    joined = gpd.sjoin(
        pts_gdf, cd_polys[["state_cd", "geometry"]],
        how="left", predicate="within",
    )
    joined = joined.sort_values(["gvkey", "state_cd"]).drop_duplicates(subset=["gvkey"], keep="first")
    out = joined[["gvkey", "state_cd"]].rename(columns={"state_cd": f"state_cd_{period_label}"})
    return out.reset_index(drop=True)


def main():
    print("=" * 80)
    print("FUNNEL DIAGNOSTIC: where do movers leak out of our 18-state spec?")
    print("=" * 80)

    # 1. Load firm-level geocodes (full Compustat)
    print("\n[1] Load firm geocodes (full Compustat)")
    geo = pd.read_parquet(PATH_GEO_FULL)
    print(f"    Rows: {len(geo):,}")
    print(f"    Unique firms: {geo['gvkey'].nunique():,}")
    print(f"    With lat/lon: {geo['latitude'].notna().sum():,}")

    # Apply 18-state filter at FIRM level (modal state)
    geo["state"] = geo["state"].astype(str)
    print(f"\n[2] 18-state filter (modal state from geocode)")
    g18_pre = geo[(geo["period"] == "pre") & (geo["state"].isin(HASAN_18_STATES))]
    g18_post = geo[(geo["period"] == "post") & (geo["state"].isin(HASAN_18_STATES))]
    g_other_pre = geo[(geo["period"] == "pre") & (~geo["state"].isin(HASAN_18_STATES))]
    print(f"    Pre period rows in 18 states: {len(g18_pre):,}")
    print(f"    Post period rows in 18 states: {len(g18_post):,}")
    print(f"    Pre period rows OUTSIDE 18 states: {len(g_other_pre):,}")

    firms_18_pre = set(g18_pre["gvkey"].unique())
    firms_18_post = set(g18_post["gvkey"].unique())
    firms_18_either = firms_18_pre | firms_18_post
    firms_18_both = firms_18_pre & firms_18_post
    print(f"    Unique 18-state firms (pre OR post): {len(firms_18_either):,}")
    print(f"    Unique 18-state firms (pre AND post): {len(firms_18_both):,}")

    # 3. CD assignment via spatial join
    print(f"\n[3] Load Lewis 2013 CD shapefiles + spatial join")
    cd_111 = _load_cd_shapefile(PATH_LEWIS_111, 111)
    cd_113 = _load_cd_shapefile(PATH_LEWIS_113, 113)
    print(f"    111CD polygons: {len(cd_111)} | 113CD polygons: {len(cd_113)}")

    # Restrict spatial join to 18-state firms only
    g_pre_18 = geo[(geo["period"] == "pre") & geo["gvkey"].isin(firms_18_either)].copy()
    g_post_18 = geo[(geo["period"] == "post") & geo["gvkey"].isin(firms_18_either)].copy()

    pre_cd = _spatial_join(g_pre_18, cd_111, "pre")
    post_cd = _spatial_join(g_post_18, cd_113, "post")
    print(f"    Firms with pre-CD assigned: {len(pre_cd):,}")
    print(f"    Firms with post-CD assigned: {len(post_cd):,}")

    cd = pre_cd.merge(post_cd, on="gvkey", how="outer")
    n_pre = cd["state_cd_pre"].notna().sum()
    n_post = cd["state_cd_post"].notna().sum()
    n_both = (cd["state_cd_pre"].notna() & cd["state_cd_post"].notna()).sum()
    print(f"    Pre-CD non-null: {n_pre:,} | Post-CD non-null: {n_post:,} | BOTH: {n_both:,}")

    # 4. Movers (district CD changed pre -> post)
    print(f"\n[4] Movers diagnostic (within 18-state subset)")
    cd_both = cd[cd["state_cd_pre"].notna() & cd["state_cd_post"].notna()].copy()
    cd_both["mover"] = cd_both["state_cd_pre"] != cd_both["state_cd_post"]
    n_movers = int(cd_both["mover"].sum())
    n_stayers = int((~cd_both["mover"]).sum())
    n_total_both = len(cd_both)
    pct = n_movers / max(n_total_both, 1) * 100
    print(f"    Total 18-state firms with BOTH pre+post CD: {n_total_both:,}")
    print(f"    Movers (CD changed): {n_movers:,} ({pct:.1f}%)")
    print(f"    Stayers (CD unchanged): {n_stayers:,} ({100-pct:.1f}%)")
    print(f"    HASAN BENCHMARK: 941 movers / 1,431 affected = 65.8%")
    print(f"    OUR RATE: {n_movers:,} / {n_total_both:,} = {pct:.1f}%")
    print(f"    GAP: {65.8 - pct:.1f} pp under-detection")

    # 5. PRisk filter (≥8 obs in 2006q1-2010q4 pre-window)
    print(f"\n[5] PRisk pre-window filter (>=8 obs in 2006q1-2010q4)")
    prisk = pd.read_csv(PATH_PRISK, sep="\t", on_bad_lines="skip", usecols=["gvkey", "date", "PRisk"])
    prisk["gvkey"] = prisk["gvkey"].astype(str).str.zfill(6)
    prisk = prisk.dropna(subset=["PRisk"])
    prisk["cal_q"] = prisk["date"].astype(str).apply(_parse_cal_q)
    prisk = prisk.dropna(subset=["cal_q"])
    prisk = prisk[(prisk["cal_q"] >= PRE_WINDOW_START) & (prisk["cal_q"] <= PRE_WINDOW_END)].copy()
    qcount = prisk.groupby("gvkey")["cal_q"].nunique().rename("n_pre").reset_index()
    qcount8 = qcount[qcount["n_pre"] >= 8].copy()

    # Apply to mover sets
    movers_with_prisk = cd_both[cd_both["mover"] & cd_both["gvkey"].isin(qcount8["gvkey"])]
    movers_without_prisk = cd_both[cd_both["mover"] & ~cd_both["gvkey"].isin(qcount8["gvkey"])]
    print(f"    Total firms with >=8 PRisk obs in 2006-2010: {len(qcount8):,}")
    print(f"    Movers passing PRisk filter: {len(movers_with_prisk):,}")
    print(f"    Movers DROPPED by PRisk filter: {len(movers_without_prisk):,}")

    # 6. Tertile rank computation: of the survivors, what fraction get Treated=±1?
    print(f"\n[6] Tertile rank computation (Treated assignment)")
    # Need pre/post tertile per firm. Compute firm's 5y mean PRisk:
    firm_prisk = prisk.groupby("gvkey")["PRisk"].mean().reset_index().rename(columns={"PRisk": "prisk_5yr"})
    firm_prisk = firm_prisk.merge(qcount, on="gvkey", how="left")
    firm_prisk = firm_prisk[firm_prisk["n_pre"] >= 8]

    cd_full = cd_both.merge(firm_prisk[["gvkey", "prisk_5yr"]], on="gvkey", how="inner")
    print(f"    Firms with both CDs + PRisk: {len(cd_full):,}")

    def _tertile(s: pd.Series) -> pd.Series:
        try:
            return pd.qcut(s.rank(method="first"), q=3, labels=[0, 1, 2]).astype(float)
        except Exception:
            return pd.Series(np.nan, index=s.index)

    cd_full["pre_t"] = cd_full.groupby("state_cd_pre")["prisk_5yr"].transform(_tertile)
    cd_full["post_t"] = cd_full.groupby("state_cd_post")["prisk_5yr"].transform(_tertile)

    delta = cd_full["post_t"] - cd_full["pre_t"]
    cd_full["Treated"] = np.where(delta > 0, 1, np.where(delta < 0, -1, np.where(delta == 0, 0, np.nan)))

    npos = int((cd_full["Treated"] == 1).sum())
    nneg = int((cd_full["Treated"] == -1).sum())
    nzero = int((cd_full["Treated"] == 0).sum())
    nnan = int(cd_full["Treated"].isna().sum())
    print(f"    Treated +1: {npos:,}")
    print(f"    Treated  0: {nzero:,}")
    print(f"    Treated -1: {nneg:,}")
    print(f"    Treated NaN (single-firm-district): {nnan:,}")
    print(f"    Active treated (+/-1): {npos + nneg:,}")
    print(f"    HASAN BENCHMARK: 941 movers (Treated=±1) of 1,431 affected = 66%")
    print(f"    OUR RATE: {npos+nneg:,} / {len(cd_full):,} = {(npos+nneg)/max(len(cd_full),1)*100:.1f}%")

    # 7. Where movers go: are they in Treated=0 (rank stable across districts) or NaN?
    print(f"\n[7] Where do movers (CD changed) end up in Treated assignment?")
    cd_movers = cd_full[cd_full["mover"]].copy()
    print(f"    Total movers in cd_full: {len(cd_movers):,}")
    for tval, lab in [(1, "+1"), (0, " 0"), (-1, "-1"), (np.nan, "NaN")]:
        if pd.isna(tval):
            n = int(cd_movers["Treated"].isna().sum())
        else:
            n = int((cd_movers["Treated"] == tval).sum())
        print(f"    Movers w/ Treated={lab}: {n:,}")

    print(f"\n[8] Where do stayers end up?")
    cd_stayers = cd_full[~cd_full["mover"]].copy()
    print(f"    Total stayers in cd_full: {len(cd_stayers):,}")
    for tval, lab in [(1, "+1"), (0, " 0"), (-1, "-1"), (np.nan, "NaN")]:
        if pd.isna(tval):
            n = int(cd_stayers["Treated"].isna().sum())
        else:
            n = int((cd_stayers["Treated"] == tval).sum())
        print(f"    Stayers w/ Treated={lab}: {n:,}")

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()
