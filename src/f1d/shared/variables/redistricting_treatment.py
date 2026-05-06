"""Builder for Redistricting DiD treatment label — H1.6 design.

Replicates Hasan, Alam, Paramati & Islam (2022) RQFA Layer-2 verbatim
methodology (NLM-verified):

NLM-VERIFIED VERBATIM (Hasan 2022 Section 5.1, Page 324):
    "For this design, we take all firms located in a given congressional
     district five years prior to redistricting and classify them into
     three groups as per their RANKING of political risk. For all firms
     located in the new districts, we use their political risk ranking
     and then repeat the process as measured over the five years
     preceding the redistricting."

NLM-VERIFIED VERBATIM (Hasan 2022 Table 4 footnote, Page 325):
    "Treated is a categorical variable, ranging from +1 to -1. +1 if
     firm-level political risk has increased due to congressional
     redistricting, zero if political risk has remained unchanged, and
     -1 if political risk has decreased due to redistricting. After,
     an indicator variable, equals to 1 after 2011, and 0 otherwise."

NLM-VERIFIED VERBATIM (timing):
    "The proposed new district lines of the 2010 census were settled
     in court in 2011. Thus, we consider 2011 when redistricting was
     implemented."

OPERATIONALIZATION (this builder):

1. Per firm: get HQ ZIP for pre-period (modal addzip 2006-2010) and
   post-period (modal addzip 2012-2016) from Compustat addzip.
2. Look up pre-CD via 111th-Congress ZCTA-CD crosswalk (PRE-redistricting
   map; uses 2002 boundaries effective 2003-2012).
3. Look up post-CD via 113th-Congress ZCTA-CD crosswalk (POST-redistricting
   map; uses 2010 boundaries effective 2013+).
4. Compute firm-level mean PRisk over 5-year pre-window 2006-2010
   (5 years preceding 2011 redistricting court settlement).
5. Within each pre-CD: rank firms by mean PRisk -> tertile group
   {Low=0, Mid=1, High=2}.
6. Within each post-CD: same firms ranked into tertile group based on
   the SAME mean PRisk window but the new district population.
7. delta_tertile_i = post_tertile_i - pre_tertile_i  (in {-2,-1,0,1,2})
   Treated_i = +1 if delta > 0  (firm's PRisk-RANK increased after redistricting)
   Treated_i =  0 if delta == 0 (rank unchanged)
   Treated_i = -1 if delta < 0  (rank decreased)
8. Post_redist_t = 1 if year > 2011 (Hasan verbatim "After 2011"); else 0.
9. DiD_Redist_{i,t} = Treated_i * Post_redist_t.

Multi-CD ZCTAs:
- 111 file (PRE): pick CD with max ZPOPPCT per ZCTA (population-weighted modal).
- 113 file (POST): pick first-listed CD per ZCTA (LIMITATION — Census did not
  publish weighted version; ~few-percent of ZCTAs span multiple CDs;
  documented in metadata).

Sample-size expectations (per plan v3 risk register):
- Plan: ~12-17K firm-quarter observations after sample-window + Main filters
  (50-70% of Hasan's reported N=24,311)
- Likely Treated=0 dominant (firms whose ZIP didn't span CD boundary changes
  AND whose tertile didn't shift): plan v3 mitigates via 3-group symmetric
  treatment.

Outputs (per call via file_name):
- Treated_redist        in {-1, 0, +1}: firm-level redistricting treatment
- Post_redist           in {0, 1}: 1 if year > 2011
- DiD_Redist            in {-1, 0, +1}: Treated * Post product
- pre_cd, post_cd       district codes (state+CD)
- pre_tertile, post_tertile  rank groupings for diagnostics
- prisk_5yr_pre_mean    firm's 5-year pre-window mean PRisk

Inputs:
- inputs/Census_CD_Crosswalks/zcta_cd111_rel_10.txt (PRE; weighted)
- inputs/Census_CD_Crosswalks/natl_zccd_delim_113.txt (POST; unweighted)
- inputs/comp_na_daily_all/comp_na_daily_all.parquet (addzip per gvkey-quarter)
- inputs/FirmLevelRisk/firmquarter_2022q1.csv (PRisk overall)
- manifest (file_name, gvkey, start_date)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from .winsorization import winsorize_by_year
from .political_risk_subtopics import _parse_cal_q
from f1d.shared.path_utils import get_latest_output_dir


PATH_CW_111 = "inputs/Census_CD_Crosswalks/zcta_cd111_rel_10.txt"
PATH_CW_113 = "inputs/Census_CD_Crosswalks/natl_zccd_delim_113.txt"
PATH_COMPUSTAT = "inputs/comp_na_daily_all/comp_na_daily_all.parquet"
PATH_PRISK = "inputs/FirmLevelRisk/firmquarter_2022q1.csv"

# Pre-window for PRisk firm-mean: 5 years preceding 2011 redistricting.
PRE_WINDOW_START = "2006q1"
PRE_WINDOW_END = "2010q4"

# Compustat addzip windows (Hasan: pre = 5y pre; post = years post-2011).
PRE_ADDZIP_YEARS = range(2006, 2011)   # 2006-2010 inclusive
POST_ADDZIP_YEARS = range(2012, 2017)  # 2012-2016 inclusive

# Hasan: "After 2011" — Post=1 if calendar year > 2011.
POST_THRESHOLD_YEAR = 2011


def _load_cw_111(path: Path) -> pd.DataFrame:
    """Load 111th-Congress ZCTA-CD crosswalk (weighted) and pick modal CD per ZCTA."""
    df = pd.read_csv(path, dtype={"ZCTA5": str, "STATE": str, "CD": str})
    df["ZCTA5"] = df["ZCTA5"].str.zfill(5)
    df["STATE"] = df["STATE"].str.zfill(2)
    df["CD"] = df["CD"].astype(str).str.zfill(2)
    # Drop PR/territories (state >= "60" in FIPS)
    df = df[df["STATE"].astype(int) < 60].copy()
    # For each ZCTA, pick CD with max ZPOPPCT (population-weighted modal).
    df = df.sort_values(["ZCTA5", "ZPOPPCT"], ascending=[True, False])
    df = df.drop_duplicates(subset=["ZCTA5"], keep="first")
    df["state_cd_pre"] = df["STATE"] + df["CD"]
    return df[["ZCTA5", "state_cd_pre"]].copy()


def _load_cw_113(path: Path) -> pd.DataFrame:
    """Load 113th-Congress ZCTA-CD crosswalk (unweighted; 1-line title + header).

    LIMITATION: Census did not publish a weighted version. ZCTAs that span
    multiple 113th CDs get the FIRST-LISTED CD per ZCTA (alphanumeric).
    ~few-percent of ZCTAs are affected; documented in metadata.
    """
    # Skip first row (title), use second as header.
    df = pd.read_csv(path, skiprows=1, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "State": "STATE",
        "ZCTA": "ZCTA5",
        "Congressional District": "CD",
    })
    df["ZCTA5"] = df["ZCTA5"].str.zfill(5)
    df["STATE"] = df["STATE"].str.zfill(2)
    df["CD"] = df["CD"].str.zfill(2)
    # Drop PR/territories (state >= "60" in FIPS) and non-numeric district codes.
    df = df[df["STATE"].astype(int) < 60].copy()
    # Keep first listing per ZCTA (alphanumeric).
    df = df.sort_values(["ZCTA5", "CD"]).drop_duplicates(
        subset=["ZCTA5"], keep="first"
    )
    df["state_cd_post"] = df["STATE"] + df["CD"]
    return df[["ZCTA5", "state_cd_post"]].copy()


def _firm_modal_zip(comp: pd.DataFrame, years: range) -> pd.DataFrame:
    """Per gvkey, return modal addzip across the given year range."""
    sub = comp[comp["year"].isin(list(years))].copy()
    sub = sub.dropna(subset=["addzip"])
    if len(sub) == 0:
        return pd.DataFrame(columns=["gvkey", "ZCTA5"])
    # Strip ZIP+4 suffix (-NNNN) and pad to 5 digits.
    sub["zip5"] = (
        sub["addzip"].astype(str).str.split("-").str[0].str.zfill(5).str[:5]
    )
    # Keep only numeric zips (ignore Canadian / international postal codes).
    sub = sub[sub["zip5"].str.match(r"^\d{5}$")].copy()
    if len(sub) == 0:
        return pd.DataFrame(columns=["gvkey", "ZCTA5"])
    # Modal zip per gvkey
    counts = sub.groupby(["gvkey", "zip5"]).size().reset_index(name="n")
    counts = counts.sort_values(
        ["gvkey", "n", "zip5"], ascending=[True, False, True]
    )
    modal = counts.drop_duplicates(subset=["gvkey"], keep="first")[
        ["gvkey", "zip5"]
    ].rename(columns={"zip5": "ZCTA5"})
    return modal


class RedistrictingTreatmentBuilder(VariableBuilder):
    """Build firm-level redistricting Treated label + per-call DiD_Redist.

    Returns VariableResult with columns:
      file_name, Treated_redist, Post_redist, DiD_Redist,
      pre_cd, post_cd, pre_tertile, post_tertile, prisk_5yr_pre_mean
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = "DiD_Redist"

    def build(self, years: range, root_path: Path) -> VariableResult:
        # 1. Load manifest
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

        # 2. Load CD crosswalks (pre + post)
        cw_111 = _load_cw_111(root_path / PATH_CW_111)
        cw_113 = _load_cw_113(root_path / PATH_CW_113)
        print(
            f"    RedistrictingTreatmentBuilder: 111CW {len(cw_111):,} "
            f"unique ZCTAs; 113CW {len(cw_113):,} unique ZCTAs"
        )

        # 3. Load Compustat addzip per (gvkey, datadate); compute modal per period.
        comp = pd.read_parquet(
            root_path / PATH_COMPUSTAT,
            columns=["gvkey", "datadate", "addzip"],
        )
        comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
        comp["datadate"] = pd.to_datetime(comp["datadate"])
        comp["year"] = comp["datadate"].dt.year

        modal_pre = _firm_modal_zip(comp, PRE_ADDZIP_YEARS).rename(
            columns={"ZCTA5": "zcta_pre"}
        )
        modal_post = _firm_modal_zip(comp, POST_ADDZIP_YEARS).rename(
            columns={"ZCTA5": "zcta_post"}
        )
        print(
            f"    RedistrictingTreatmentBuilder: pre-period modal-zip firms = "
            f"{len(modal_pre):,}; post-period = {len(modal_post):,}"
        )

        # 4. Lookup pre-CD and post-CD per firm.
        firm_cd = modal_pre.merge(modal_post, on="gvkey", how="outer")
        firm_cd = firm_cd.merge(
            cw_111.rename(columns={"ZCTA5": "zcta_pre"}),
            on="zcta_pre", how="left",
        )
        firm_cd = firm_cd.merge(
            cw_113.rename(columns={"ZCTA5": "zcta_post"}),
            on="zcta_post", how="left",
        )

        n_pre_matched = firm_cd["state_cd_pre"].notna().sum()
        n_post_matched = firm_cd["state_cd_post"].notna().sum()
        n_both = (
            firm_cd["state_cd_pre"].notna() & firm_cd["state_cd_post"].notna()
        ).sum()
        print(
            f"    RedistrictingTreatmentBuilder: pre-CD matched={n_pre_matched:,} | "
            f"post-CD matched={n_post_matched:,} | BOTH={n_both:,}"
        )

        # 5. Load firm-level PRisk (overall) for 5-year pre-window.
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
        # Per-year winsorization stable
        prisk = winsorize_by_year(prisk, ["PRisk"], year_col="year")
        # Dedup (gvkey, cal_q): keep max PRisk
        prisk = (
            prisk.sort_values("PRisk", ascending=False)
            .drop_duplicates(subset=["gvkey", "cal_q"], keep="first")
        )

        firm_prisk = (
            prisk.groupby("gvkey")["PRisk"].mean().reset_index()
            .rename(columns={"PRisk": "prisk_5yr_pre_mean"})
        )
        # Require >= 8 quarters of pre-window data (mirrors H1.5 convention).
        firm_qcount = prisk.groupby("gvkey")["cal_q"].nunique().rename("n_pre")
        firm_prisk = firm_prisk.merge(firm_qcount, on="gvkey", how="left")
        firm_prisk = firm_prisk[firm_prisk["n_pre"] >= 8].copy()
        print(
            f"    RedistrictingTreatmentBuilder: firms with >=8 pre-window PRisk obs = "
            f"{len(firm_prisk):,}"
        )

        # 6. Merge firm_cd + firm_prisk
        firm = firm_cd.merge(firm_prisk[["gvkey", "prisk_5yr_pre_mean"]], on="gvkey", how="inner")
        firm = firm.dropna(subset=["state_cd_pre", "state_cd_post"])
        print(
            f"    RedistrictingTreatmentBuilder: firms with pre-CD + post-CD + PRisk = "
            f"{len(firm):,}"
        )

        # 7. Tertile rank within each pre-CD and within each post-CD.
        def _tertile(s: pd.Series) -> pd.Series:
            # qcut to 3 tiles; if not enough unique values, fall back to NaN.
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

        # 8. Treated_redist
        delta = firm["post_tertile"] - firm["pre_tertile"]
        firm["Treated_redist"] = np.where(
            delta > 0, 1.0,
            np.where(delta < 0, -1.0, np.where(delta == 0, 0.0, np.nan)),
        )

        n_pos = int((firm["Treated_redist"] == 1).sum())
        n_neg = int((firm["Treated_redist"] == -1).sum())
        n_zero = int((firm["Treated_redist"] == 0).sum())
        n_nan = int(firm["Treated_redist"].isna().sum())
        print(
            f"    RedistrictingTreatmentBuilder: Treated +1={n_pos:,} | "
            f"0={n_zero:,} | -1={n_neg:,} | NaN={n_nan:,} (of {len(firm):,})"
        )

        # 9. Per-call merge: attach Treated + Post + DiD
        firm_keep_cols = [
            "gvkey",
            "state_cd_pre", "state_cd_post",
            "pre_tertile", "post_tertile",
            "Treated_redist", "prisk_5yr_pre_mean",
        ]
        merged = manifest.merge(firm[firm_keep_cols], on="gvkey", how="left")
        merged["Post_redist"] = (
            merged["year"] > POST_THRESHOLD_YEAR
        ).astype(float)
        merged["DiD_Redist"] = (
            merged["Treated_redist"] * merged["Post_redist"]
        )
        merged = merged.rename(columns={
            "state_cd_pre": "pre_cd",
            "state_cd_post": "post_cd",
        })

        out_cols = [
            "file_name",
            "Treated_redist", "Post_redist", "DiD_Redist",
            "pre_cd", "post_cd",
            "pre_tertile", "post_tertile",
            "prisk_5yr_pre_mean",
        ]
        data = merged[out_cols].drop_duplicates(subset=["file_name"]).copy()

        # Per-call diagnostic counts
        n_calls_treated = int((data["Treated_redist"].notna()).sum())
        n_calls_pos = int((data["Treated_redist"] == 1).sum())
        n_calls_neg = int((data["Treated_redist"] == -1).sum())
        n_calls_zero = int((data["Treated_redist"] == 0).sum())
        print(
            f"    RedistrictingTreatmentBuilder: per-call coverage: "
            f"Treated-labelled={n_calls_treated:,} / {n_calls:,}"
        )
        print(
            f"      cohort split: +1={n_calls_pos:,}  0={n_calls_zero:,}  "
            f"-1={n_calls_neg:,}"
        )

        return VariableResult(
            data=data,
            stats=self.get_stats(data["DiD_Redist"], "DiD_Redist"),
            metadata={
                "columns": out_cols[1:],
                "primary_column": "DiD_Redist",
                "source": (
                    "Hasan 2022 Section 5.1 verbatim: firm-rank-within-district "
                    "redistricting DiD using 111th (PRE) and 113th (POST) Census "
                    "ZCTA-to-CD crosswalks plus firm 5-year pre-window PRisk mean."
                ),
                "pre_window": f"{PRE_WINDOW_START}-{PRE_WINDOW_END}",
                "post_threshold_year": POST_THRESHOLD_YEAR,
                "n_firms_treated_labelled": n_pos + n_zero + n_neg,
                "n_firms_pos": n_pos,
                "n_firms_zero": n_zero,
                "n_firms_neg": n_neg,
                "n_calls_pos": n_calls_pos,
                "n_calls_zero": n_calls_zero,
                "n_calls_neg": n_calls_neg,
                "limitation_113cw": (
                    "113th-Congress ZCTA-CD file is unweighted (Census did not "
                    "publish a population-weighted version). ZCTAs that span "
                    "multiple 113th CDs are assigned to the FIRST-LISTED CD "
                    "per ZCTA (alphanumeric ordering)."
                ),
            },
        )


__all__ = ["RedistrictingTreatmentBuilder"]
