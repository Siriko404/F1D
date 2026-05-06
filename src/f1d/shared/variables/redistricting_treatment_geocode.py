"""Builder for Redistricting DiD treatment label — H1.6 TEST 3.

GEOCODE + SHAPEFILE variant of redistricting_treatment.py — replaces lossy
ZCTA-CD crosswalk path with geocoded HQ lat/lon + point-in-polygon spatial
join against Lewis et al. 2013 Congressional District boundary shapefiles.

Methodology source (Hasan 2022 NLM-verified verbatim):
    "For this design, we take all firms located in a given congressional
     district five years prior to redistricting and classify them into
     three groups as per their RANKING of political risk. For all firms
     located in the new districts, we use their political risk ranking
     and then repeat the process as measured over the five years
     preceding the redistricting."

    "Treated is a categorical variable, ranging from +1 to -1. +1 if
     firm-level political risk has increased due to congressional
     redistricting, zero if political risk has remained unchanged, and
     -1 if political risk has decreased due to redistricting. After,
     an indicator variable, equals to 1 after 2011, and 0 otherwise."

The original redistricting_treatment.py used Census ZCTA-CD relationship
files (lossy: 113th-Congress version unweighted, ZCTAs spanning multiple
CDs assigned to FIRST-LISTED CD). Empirical mover ratio under that path
within the 18 redistricted Hasan-states was 16% — vs Hasan's reported 66%.
A 4x under-detection of district moves indicated mapping precision was
the dominant gap.

This builder replaces the ZCTA-CD lookup with:
    HQ address (Compustat add1 + city + state + zip5)
        -> Census Batch Geocoder (Public_AR_Current benchmark)
        -> firm lat/lon
        -> spatial join (point-in-polygon) against Lewis 2013 CD shapefiles
        -> 111th-Congress CD (PRE) and 113th-Congress CD (POST)
    -> rank tertile within each CD using firm 5-yr pre-window mean PRisk
    -> Treated +1/0/-1 per Hasan verbatim spec

Source for shapefiles: https://github.com/JeffreyBLewis/congressional-district-boundaries
(referenced from cdmaps.polisci.ucla.edu — UCLA Political Science).

Inputs (acquired by Day-1 scripts):
- inputs/firm_geocodes/firm_lat_lon.parquet
    columns: gvkey, period, latitude, longitude, match_status
- inputs/Lewis2013_CD/111/*.geojson      (51 files; 435 polygons covering 50 states)
- inputs/Lewis2013_CD/113/*.geojson      (51 files; 435 polygons covering 50 states)
- inputs/FirmLevelRisk/firmquarter_2022q1.csv  (PRisk overall)
- manifest (file_name, gvkey, start_date)

Outputs (per call via file_name):
- Treated_redist_geo  in {-1, 0, +1}: firm-level redistricting treatment
- Post_redist_geo     in {0, 1}: 1 if year > 2011
- DiD_Redist_geo      in {-1, 0, +1}: Treated * Post product
- pre_cd_geo, post_cd_geo                    district codes (state+CD)
- pre_tertile_geo, post_tertile_geo          rank groupings
- prisk_5yr_pre_mean                         firm's 5-year pre-window mean PRisk
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from .political_risk_subtopics import _parse_cal_q
from .winsorization import winsorize_by_year
from f1d.shared.path_utils import get_latest_output_dir


PATH_GEOCODES = "inputs/firm_geocodes/firm_lat_lon.parquet"
PATH_SHP_111 = "inputs/Lewis2013_CD/111"
PATH_SHP_113 = "inputs/Lewis2013_CD/113"
PATH_PRISK = "inputs/FirmLevelRisk/firmquarter_2022q1.csv"

# Pre-window for PRisk firm-mean: 5 years preceding 2011 redistricting.
PRE_WINDOW_START = "2006q1"
PRE_WINDOW_END = "2010q4"

# Hasan: "After 2011" — Post=1 if calendar year > 2011.
POST_THRESHOLD_YEAR = 2011


def _load_cd_shapefile(directory: Path, congress: int) -> "pd.DataFrame":
    """Load + concat Lewis 2013 GeoJSONs for a given Congress.

    Filters to polygons whose [startcong, endcong] range covers the target
    Congress. Returns a GeoDataFrame with columns:
        statename, district, startcong, endcong, geometry
    plus a derived state_cd code (FIPS state + zero-padded district).
    """
    import geopandas as gpd

    files = sorted(directory.glob("*.geojson"))
    if not files:
        raise FileNotFoundError(
            f"No Lewis 2013 GeoJSONs in {directory}. "
            f"Run scripts/adhoc/download_lewis2013_cd_geojson.py first."
        )
    gdfs = [gpd.read_file(fp) for fp in files]
    gdf = pd.concat(gdfs, ignore_index=True)
    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs="EPSG:4269")
    # Filter to the target Congress
    gdf = gdf[
        (gdf["startcong"] <= congress) & (gdf["endcong"] >= congress)
    ].copy()
    if len(gdf) == 0:
        raise RuntimeError(
            f"No polygons cover {congress}th Congress in {directory}"
        )
    # statefp is sometimes blank in source; map from statename if needed.
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
    gdf["cd_str"] = (
        gdf["district"].astype(float).astype(int).astype(str).str.zfill(2)
    )
    gdf["state_cd"] = gdf["statefp"].astype(str) + gdf["cd_str"]
    return gdf[["statename", "statefp", "district", "state_cd", "geometry"]]


def _spatial_join_firms_to_cd(
    firm_pts: "pd.DataFrame",
    cd_polys: "pd.DataFrame",
    period_label: str,
) -> pd.DataFrame:
    """Point-in-polygon join: returns firm_pts with state_cd_<period> column."""
    import geopandas as gpd
    from shapely.geometry import Point

    # Build firm-pts GeoDataFrame
    firm_pts = firm_pts.dropna(subset=["latitude", "longitude"]).copy()
    if len(firm_pts) == 0:
        return pd.DataFrame(columns=["gvkey", f"state_cd_{period_label}"])
    geom = [
        Point(lon, lat) for lon, lat in zip(
            firm_pts["longitude"], firm_pts["latitude"]
        )
    ]
    pts_gdf = gpd.GeoDataFrame(
        firm_pts[["gvkey"]].copy(), geometry=geom, crs="EPSG:4326"
    )
    # Reproject to NAD83 to match Lewis shapefile CRS
    pts_gdf = pts_gdf.to_crs("EPSG:4269")
    # Spatial join with polygons
    joined = gpd.sjoin(
        pts_gdf, cd_polys[["state_cd", "geometry"]],
        how="left", predicate="within",
    )
    # Some firms may fall on shared boundary edges — keep first match per gvkey
    joined = (
        joined.sort_values(["gvkey", "state_cd"])
        .drop_duplicates(subset=["gvkey"], keep="first")
    )
    out = joined[["gvkey", "state_cd"]].rename(
        columns={"state_cd": f"state_cd_{period_label}"}
    )
    return out.reset_index(drop=True)


class RedistrictingTreatmentGeocodeBuilder(VariableBuilder):
    """Geocode + Lewis 2013 shapefile variant of RedistrictingTreatmentBuilder.

    Returns VariableResult with columns:
        file_name, Treated_redist_geo, Post_redist_geo, DiD_Redist_geo,
        pre_cd_geo, post_cd_geo,
        pre_tertile_geo, post_tertile_geo,
        prisk_5yr_pre_mean
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = "DiD_Redist_geo"

    def build(self, years: range, root_path: Path) -> VariableResult:
        # 1. Manifest
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest = pd.read_parquet(
            manifest_dir / "master_sample_manifest.parquet",
            columns=["file_name", "gvkey", "start_date"],
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()
        n_calls = len(manifest)

        # 2. Load Lewis 2013 CD shapefiles (PRE = 111CD; POST = 113CD)
        cd_111 = _load_cd_shapefile(root_path / PATH_SHP_111, congress=111)
        cd_113 = _load_cd_shapefile(root_path / PATH_SHP_113, congress=113)
        print(
            f"    RedistrictingTreatmentGeocodeBuilder: "
            f"111CD polygons={len(cd_111):,} | 113CD polygons={len(cd_113):,}"
        )

        # 3. Load firm geocodes
        geo = pd.read_parquet(root_path / PATH_GEOCODES)
        geo["gvkey"] = geo["gvkey"].astype(str).str.zfill(6)
        geo_pre = geo[geo["period"] == "pre"].copy()
        geo_post = geo[geo["period"] == "post"].copy()
        print(
            f"    RedistrictingTreatmentGeocodeBuilder: "
            f"geocoded firms pre={len(geo_pre):,} (lat/lon non-null="
            f"{geo_pre['latitude'].notna().sum():,}); "
            f"post={len(geo_post):,} (lat/lon non-null="
            f"{geo_post['latitude'].notna().sum():,})"
        )

        # 4. Spatial join: firm pre-period lat/lon -> 111CD; post -> 113CD
        firm_pre_cd = _spatial_join_firms_to_cd(geo_pre, cd_111, "pre")
        firm_post_cd = _spatial_join_firms_to_cd(geo_post, cd_113, "post")
        firm_cd = firm_pre_cd.merge(firm_post_cd, on="gvkey", how="outer")
        n_pre = firm_cd["state_cd_pre"].notna().sum()
        n_post = firm_cd["state_cd_post"].notna().sum()
        n_both = (
            firm_cd["state_cd_pre"].notna() & firm_cd["state_cd_post"].notna()
        ).sum()
        print(
            f"    RedistrictingTreatmentGeocodeBuilder: pre-CD matched={n_pre:,} | "
            f"post-CD matched={n_post:,} | BOTH={n_both:,}"
        )

        # Empirical mover-rate diagnostic (vs Hasan-reported 66%)
        both_idx = (
            firm_cd["state_cd_pre"].notna() & firm_cd["state_cd_post"].notna()
        )
        movers = (
            firm_cd.loc[both_idx, "state_cd_pre"]
            != firm_cd.loc[both_idx, "state_cd_post"]
        ).sum()
        n_both_int = int(n_both)
        if n_both_int:
            print(
                f"    RedistrictingTreatmentGeocodeBuilder: "
                f"mover ratio (CD changed pre->post): "
                f"{movers:,}/{n_both_int:,} = {movers / n_both_int * 100:.1f}%"
            )

        # 5. Load firm-level PRisk for 5-year pre-window
        prisk_cols = ["gvkey", "date", "PRisk"]
        prisk = pd.read_csv(
            root_path / PATH_PRISK, sep="\t", on_bad_lines="skip",
            usecols=prisk_cols,
        )
        prisk["gvkey"] = prisk["gvkey"].astype(str).str.zfill(6)
        prisk = prisk.dropna(subset=["PRisk"])
        prisk["cal_q"] = prisk["date"].apply(_parse_cal_q)
        prisk = prisk.dropna(subset=["cal_q"])
        prisk["year"] = prisk["cal_q"].str[:4].astype(int)
        prisk = prisk[
            (prisk["cal_q"] >= PRE_WINDOW_START)
            & (prisk["cal_q"] <= PRE_WINDOW_END)
        ].copy()
        prisk = winsorize_by_year(prisk, ["PRisk"], year_col="year")
        prisk = (
            prisk.sort_values("PRisk", ascending=False)
            .drop_duplicates(subset=["gvkey", "cal_q"], keep="first")
        )
        firm_prisk = (
            prisk.groupby("gvkey")["PRisk"].mean().reset_index()
            .rename(columns={"PRisk": "prisk_5yr_pre_mean"})
        )
        firm_qcount = prisk.groupby("gvkey")["cal_q"].nunique().rename("n_pre")
        firm_prisk = firm_prisk.merge(firm_qcount, on="gvkey", how="left")
        firm_prisk = firm_prisk[firm_prisk["n_pre"] >= 8].copy()
        print(
            f"    RedistrictingTreatmentGeocodeBuilder: firms with >=8 "
            f"pre-window PRisk obs = {len(firm_prisk):,}"
        )

        # 6. Merge firm_cd + firm_prisk
        firm = firm_cd.merge(
            firm_prisk[["gvkey", "prisk_5yr_pre_mean"]],
            on="gvkey", how="inner",
        )
        firm = firm.dropna(subset=["state_cd_pre", "state_cd_post"])
        print(
            f"    RedistrictingTreatmentGeocodeBuilder: firms with pre-CD + "
            f"post-CD + PRisk = {len(firm):,}"
        )

        # 7. Tertile rank within each pre-CD and within each post-CD
        def _tertile(s: pd.Series) -> pd.Series:
            try:
                return pd.qcut(
                    s.rank(method="first"), q=3, labels=[0, 1, 2]
                ).astype(float)
            except Exception:
                return pd.Series(np.nan, index=s.index)

        firm["pre_tertile"] = (
            firm.groupby("state_cd_pre")["prisk_5yr_pre_mean"]
            .transform(_tertile)
        )
        firm["post_tertile"] = (
            firm.groupby("state_cd_post")["prisk_5yr_pre_mean"]
            .transform(_tertile)
        )

        # 8. Treated_redist_geo
        delta = firm["post_tertile"] - firm["pre_tertile"]
        firm["Treated_redist_geo"] = np.where(
            delta > 0, 1.0,
            np.where(delta < 0, -1.0, np.where(delta == 0, 0.0, np.nan)),
        )
        n_pos = int((firm["Treated_redist_geo"] == 1).sum())
        n_neg = int((firm["Treated_redist_geo"] == -1).sum())
        n_zero = int((firm["Treated_redist_geo"] == 0).sum())
        n_nan = int(firm["Treated_redist_geo"].isna().sum())
        print(
            f"    RedistrictingTreatmentGeocodeBuilder: Treated +1={n_pos:,} | "
            f"0={n_zero:,} | -1={n_neg:,} | NaN={n_nan:,} (of {len(firm):,})"
        )

        # 9. Per-call merge: attach Treated + Post + DiD
        firm_keep = [
            "gvkey",
            "state_cd_pre", "state_cd_post",
            "pre_tertile", "post_tertile",
            "Treated_redist_geo", "prisk_5yr_pre_mean",
        ]
        merged = manifest.merge(firm[firm_keep], on="gvkey", how="left")
        merged["Post_redist_geo"] = (
            merged["year"] > POST_THRESHOLD_YEAR
        ).astype(float)
        merged["DiD_Redist_geo"] = (
            merged["Treated_redist_geo"] * merged["Post_redist_geo"]
        )
        merged = merged.rename(columns={
            "state_cd_pre": "pre_cd_geo",
            "state_cd_post": "post_cd_geo",
            "pre_tertile": "pre_tertile_geo",
            "post_tertile": "post_tertile_geo",
        })

        out_cols = [
            "file_name",
            "Treated_redist_geo", "Post_redist_geo", "DiD_Redist_geo",
            "pre_cd_geo", "post_cd_geo",
            "pre_tertile_geo", "post_tertile_geo",
            "prisk_5yr_pre_mean",
        ]
        data = merged[out_cols].drop_duplicates(subset=["file_name"]).copy()

        n_calls_treated = int(data["Treated_redist_geo"].notna().sum())
        n_calls_pos = int((data["Treated_redist_geo"] == 1).sum())
        n_calls_neg = int((data["Treated_redist_geo"] == -1).sum())
        n_calls_zero = int((data["Treated_redist_geo"] == 0).sum())
        print(
            f"    RedistrictingTreatmentGeocodeBuilder: per-call coverage: "
            f"Treated-labelled={n_calls_treated:,} / {n_calls:,}"
        )
        print(
            f"      cohort split: +1={n_calls_pos:,}  0={n_calls_zero:,}  "
            f"-1={n_calls_neg:,}"
        )

        return VariableResult(
            data=data,
            stats=self.get_stats(data["DiD_Redist_geo"], "DiD_Redist_geo"),
            metadata={
                "columns": out_cols[1:],
                "primary_column": "DiD_Redist_geo",
                "source": (
                    "Hasan 2022 Section 5.1 verbatim: firm-rank-within-district "
                    "redistricting DiD using Lewis 2013 Congressional District "
                    "shapefiles (111th/113th) + Census Geocoder firm HQ lat/lon "
                    "(point-in-polygon spatial join)."
                ),
                "pre_window": f"{PRE_WINDOW_START}-{PRE_WINDOW_END}",
                "post_threshold_year": POST_THRESHOLD_YEAR,
                "n_firms_pos": n_pos,
                "n_firms_zero": n_zero,
                "n_firms_neg": n_neg,
                "n_calls_pos": n_calls_pos,
                "n_calls_zero": n_calls_zero,
                "n_calls_neg": n_calls_neg,
                "mover_rate_pct": (
                    None if n_both_int == 0
                    else round(movers / n_both_int * 100, 1)
                ),
            },
        )


__all__ = ["RedistrictingTreatmentGeocodeBuilder"]
