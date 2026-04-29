"""Builder for HedgingNeeds — Acharya-Almeida-Campello (2007) JFI hedging-needs moderator.

Anchor (verbatim, Section 4.2.3, pp. 538-539):
  "...compute the median three-year-ahead sales growth rate in the firm's
   three-digit SIC industry and then compute the correlation between this
   measure of industry-level demand and the firm's cash flow."

Formula:
  Step 1: SG_{i,t} = (sale_{i,t} - sale_{i,t-1}) / |sale_{i,t-1}|   (firm-year)
  Step 2: IndSG3_{j,t} = median_{i in j} SG_{i,t+3}                  (industry-year)
  Step 3: HedgingNeeds_{i,t} = corr(CashFlow_{i,s}, IndSG3_{j(i),s}) over s in
                               [t-4..t]  (5-year rolling window per firm)

Disclosed deviations from ACW 2007 verbatim:
  - Industry: FF12 (matches our pipeline) instead of 3-digit SIC
  - Sample: all non-financial / non-utility (matches F1D) vs ACW manufacturing-only
  - Frequency: annual hedging-needs forward-merged to firm-quarter via fyearq
  - Window: 5-year rolling (matches our sCFO convention; ACW used full firm history)

Merge: per-call file_name via merge_asof on (gvkey, start_date -> fiscal-year-end
  hedging-needs value forward-applied within fiscal year).

Requires Compustat columns: gvkey, datadate, fyearq, fqtr, sic, saley, oancfy, atq.
Industry is FF12 (assigned via existing FF12 SIC map; share with engine).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from f1d.shared.path_utils import get_latest_output_dir


COMPUSTAT_PATH = "inputs/comp_na_daily_all/comp_na_daily_all.parquet"
COMPUSTAT_EXTENDED_DIR = "inputs/Compustat_Quarterly_OCF_Extended"
ROLLING_WINDOW_YEARS = 5  # 5-year per-firm rolling correlation
SALES_GROWTH_AHEAD = 3    # 3-year-ahead industry median (ACW verbatim)


def _load_compustat_annual(root_path: Path) -> pd.DataFrame:
    """Load gvkey + Q4-only (fiscal year-end) rows for: saley, oancfy, atq, sic, fyearq.

    Q4-only ensures saley/oancfy are full-year YTD totals at fiscal-year close.
    """
    cols = ["gvkey", "datadate", "fyearq", "fqtr", "sic", "saley", "oancfy", "atq"]
    main = pd.read_parquet(root_path / COMPUSTAT_PATH, columns=cols)
    main["gvkey"] = main["gvkey"].astype(str).str.zfill(6)
    main["datadate"] = pd.to_datetime(main["datadate"])

    extended_dir = root_path / COMPUSTAT_EXTENDED_DIR
    extended_frames = []
    if extended_dir.exists():
        for ext_file in sorted(extended_dir.glob("*.parquet")):
            ext = pd.read_parquet(ext_file, columns=cols)
            ext["gvkey"] = ext["gvkey"].astype(str).str.zfill(6)
            ext["datadate"] = pd.to_datetime(ext["datadate"])
            extended_frames.append(ext)

    combined = pd.concat([main] + extended_frames, ignore_index=True)
    combined = combined.sort_values(["gvkey", "datadate"], kind="stable")
    combined = combined.drop_duplicates(subset=["gvkey", "datadate"], keep="first")
    combined = combined.dropna(subset=["fyearq", "fqtr"])

    # Q4-only rows = fiscal-year-end full-year totals
    annual = combined[combined["fqtr"] == 4].copy()
    return annual


def _ff12_from_sic(sic_series: pd.Series) -> pd.Series:
    """Map SIC -> Fama-French 12 industry code. Inline implementation (independent of engine)."""
    sic = pd.to_numeric(sic_series, errors="coerce")
    out = pd.Series([np.nan] * len(sic), index=sic.index)
    # FF12 ranges (1-12). 8=Finance (NoBus), 11=Util excluded via Main filter downstream.
    def assign(s):
        if pd.isna(s):
            return np.nan
        s = int(s)
        if 100 <= s <= 999 or 2000 <= s <= 2399 or 2700 <= s <= 2749 or 2770 <= s <= 2799 or 3100 <= s <= 3199 or 3940 <= s <= 3989:
            return 1   # NoDur
        if 2520 <= s <= 2589 or 2600 <= s <= 2699 or 2750 <= s <= 2769 or 3000 <= s <= 3099 or 3200 <= s <= 3569 or 3580 <= s <= 3629 or 3700 <= s <= 3799 or 3860 <= s <= 3879 or 3900 <= s <= 3939 or 3990 <= s <= 3999:
            return 2   # Durbl
        if 2520 <= s <= 2589 or 2600 <= s <= 2699 or 2750 <= s <= 2769 or 3000 <= s <= 3099:
            return 3   # Manuf
        if 1200 <= s <= 1399 or 2900 <= s <= 2999:
            return 4   # Enrgy
        if 2800 <= s <= 2829 or 2840 <= s <= 2899:
            return 5   # Chems
        if 3570 <= s <= 3579 or 3660 <= s <= 3692 or 3694 <= s <= 3699 or 3810 <= s <= 3829 or 7370 <= s <= 7379:
            return 6   # BusEq
        if 4800 <= s <= 4899:
            return 7   # Telcm
        if 4900 <= s <= 4949:
            return 8   # Utils
        if 5000 <= s <= 5999 or 7200 <= s <= 7299 or 7600 <= s <= 7699:
            return 9   # Shops
        if 2830 <= s <= 2839 or 3693 <= s <= 3693 or 3840 <= s <= 3859 or 8000 <= s <= 8099:
            return 10  # Hlth
        if 6000 <= s <= 6999:
            return 11  # Money
        return 12      # Other
    return sic.apply(assign)


def _compute_hedging_needs(annual: pd.DataFrame) -> pd.DataFrame:
    """Compute firm-year HedgingNeeds via 3 steps.

    Returns: gvkey, fyearq, HedgingNeeds (Float64, NaN if window < 5 years).
    """
    df = annual.sort_values(["gvkey", "fyearq"], kind="stable").copy()
    df["fyearq"] = pd.to_numeric(df["fyearq"], errors="coerce").astype("Int64")
    df["ff12_code"] = _ff12_from_sic(df["sic"])

    # Cast numeric columns to float64 (some Compustat columns load as object dtype)
    for col in ["saley", "oancfy", "atq"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Step 1: firm-year sales growth = (saley_t - saley_{t-1}) / |saley_{t-1}|
    df["saley_lag"] = df.groupby("gvkey", sort=False)["saley"].shift(1)
    df["SG"] = np.where(
        df["saley_lag"].abs() > 0,
        (df["saley"] - df["saley_lag"]) / df["saley_lag"].abs(),
        np.nan,
    )
    df["SG"] = df["SG"].replace([np.inf, -np.inf], np.nan)

    # Firm cash flow = oancfy / avg_assets (matches engine CashFlow var)
    df["atq_lag"] = df.groupby("gvkey", sort=False)["atq"].shift(1)
    df["avg_at"] = (df["atq"] + df["atq_lag"]) / 2.0
    df["CashFlow"] = np.where(
        df["avg_at"] > 0,
        df["oancfy"] / df["avg_at"],
        np.nan,
    )
    df["CashFlow"] = df["CashFlow"].replace([np.inf, -np.inf], np.nan)

    # Step 2: industry-year median 3-year-ahead sales growth
    # First compute industry-year median SG, then shift -3 years (look-ahead) per industry
    ind_year_median = (
        df.dropna(subset=["ff12_code"])
        .groupby(["ff12_code", "fyearq"])["SG"]
        .median()
        .reset_index()
        .rename(columns={"SG": "IndSG"})
    )
    ind_year_median = ind_year_median.sort_values(["ff12_code", "fyearq"], kind="stable")
    ind_year_median["IndSG3"] = ind_year_median.groupby("ff12_code", sort=False)["IndSG"].shift(-SALES_GROWTH_AHEAD)
    df = df.merge(
        ind_year_median[["ff12_code", "fyearq", "IndSG3"]],
        on=["ff12_code", "fyearq"],
        how="left",
        validate="many_to_one",
    )

    # Step 3: per-gvkey 5-year rolling correlation between CashFlow and IndSG3
    df = df.sort_values(["gvkey", "fyearq"], kind="stable")

    def rolling_corr(group: pd.DataFrame) -> pd.Series:
        cf = group["CashFlow"]
        sg = group["IndSG3"]
        # require both non-NaN within window; need >= 3 valid pairs to compute corr
        return cf.rolling(ROLLING_WINDOW_YEARS, min_periods=3).corr(sg)

    df["HedgingNeeds"] = df.groupby("gvkey", group_keys=False).apply(rolling_corr).reset_index(level=0, drop=True)
    df["HedgingNeeds"] = df["HedgingNeeds"].replace([np.inf, -np.inf], np.nan)

    return df[["gvkey", "fyearq", "HedgingNeeds"]].copy()


class HedgingNeedsBuilder(VariableBuilder):
    """Build HedgingNeeds per ACW 2007 — corr(firm CF, ind 3-yr-ahead median SG), 5-yr roll.

    Returns (file_name, HedgingNeeds) keyed on call file_name.
    Hedging-needs is firm-year; merged via fyearq alignment to call panel.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Need to attach fyearq to manifest — do it via Compustat datadate merge_asof
        annual = _load_compustat_annual(root_path)
        hn = _compute_hedging_needs(annual)
        hn = hn.dropna(subset=["HedgingNeeds"]).copy()

        # Merge hn to manifest via (gvkey, fyearq) — need fyearq on manifest first
        # Use merge_asof on datadate to attach fyearq
        comp_dt_lookup = annual[["gvkey", "datadate", "fyearq"]].dropna(subset=["fyearq"]).copy()
        comp_dt_lookup["fyearq"] = pd.to_numeric(comp_dt_lookup["fyearq"], errors="coerce").astype("Int64")
        comp_dt_lookup = comp_dt_lookup.sort_values(["datadate"])
        manifest_sorted = manifest.sort_values("start_date")

        manifest_aug = pd.merge_asof(
            manifest_sorted,
            comp_dt_lookup,
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )

        hn["fyearq"] = pd.to_numeric(hn["fyearq"], errors="coerce").astype("Int64")
        merged = manifest_aug.merge(
            hn,
            on=["gvkey", "fyearq"],
            how="left",
            validate="many_to_one",
        )

        data = merged[["file_name", "HedgingNeeds"]].copy()
        stats = self.get_stats(data["HedgingNeeds"], "HedgingNeeds")

        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "HedgingNeeds",
                "source": "ACW 2007 corr(CF, ind 3yr-ahead median SG); 5yr roll; FF12 industry",
                "rolling_window_years": ROLLING_WINDOW_YEARS,
                "sales_growth_ahead_years": SALES_GROWTH_AHEAD,
                "anchor": "ACW 2007 JFI Section 4.2.3 p.538-539",
            },
        )


__all__ = ["HedgingNeedsBuilder"]
