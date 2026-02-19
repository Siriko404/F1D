"""Builder for Compustat-based firm control variables.

Computes Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, and EPS_Growth
directly from raw Compustat quarterly data (inputs/comp_na_daily_all/).

This is the canonical source for all accounting-based controls. The panel
builder calls this once and extracts the columns it needs.

Formula reference (quarterly Compustat variables):
    Size         = ln(atq)                     log total assets
    BM           = ceqq / (cshoq * prccq)      book-to-market
    Lev          = ltq / atq                   leverage
    ROA          = niq / atq                   return on assets
    CurrentRatio = actq / lctq                 current ratio
    RD_Intensity = xrdq / atq                  R&D intensity (missing R&D = 0)
    EPS_Growth   = (epspxq - lag4) / |lag4|   YoY EPS growth (4-quarter lag)

All continuous variables are winsorized at 1% / 99% on the full Compustat panel
before matching to the manifest, matching the legacy build_firm_controls.py logic.

Matching: merge_asof (backward) on start_date within gvkey — finds the most recent
Compustat quarter whose datadate <= call start_date.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats

# Columns built by this builder
COMPUSTAT_COLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "CurrentRatio",
    "RD_Intensity",
    "EPS_Growth",
]

# Raw Compustat columns required
REQUIRED_COMPUSTAT_COLS = [
    "gvkey",
    "datadate",
    "atq",
    "ceqq",
    "cshoq",
    "prccq",
    "ltq",
    "niq",
    "epspxq",
    "actq",
    "lctq",
    "xrdq",
]


def _compute_and_winsorize(comp: pd.DataFrame) -> pd.DataFrame:
    """Compute all 7 control variables on the full Compustat panel and winsorize.

    Vectorized — processes the entire Compustat DataFrame at once.
    Mirrors compute_financial_controls_quarterly() from shared/financial_utils.py.
    """
    comp = comp.sort_values(["gvkey", "datadate"]).reset_index(drop=True)

    # 4-quarter lagged EPS for YoY growth
    comp["epspxq_lag4"] = comp.groupby("gvkey")["epspxq"].shift(4)

    comp["Size"] = np.log(comp["atq"].clip(lower=0.01))
    comp["BM"] = comp["ceqq"] / (comp["cshoq"] * comp["prccq"])
    comp["Lev"] = comp["ltq"] / comp["atq"]
    comp["ROA"] = comp["niq"] / comp["atq"]
    comp["CurrentRatio"] = comp["actq"] / comp["lctq"].replace(0, np.nan)
    comp["RD_Intensity"] = comp["xrdq"].fillna(0) / comp["atq"]

    lag_mask = comp["epspxq_lag4"].notna() & (comp["epspxq_lag4"] != 0)
    comp["EPS_Growth"] = np.where(
        lag_mask,
        (comp["epspxq"] - comp["epspxq_lag4"]) / comp["epspxq_lag4"].abs(),
        np.nan,
    )

    # Winsorize 1% / 99% on full panel
    for col in COMPUSTAT_COLS:
        valid = comp[col].notna()
        if valid.any():
            p1 = comp.loc[valid, col].quantile(0.01)
            p99 = comp.loc[valid, col].quantile(0.99)
            comp[col] = comp[col].clip(lower=p1, upper=p99)

    return comp


class CompustatControlsBuilder(VariableBuilder):
    """Build all Compustat-based firm control variables from raw inputs.

    Loads raw Compustat quarterly data, computes 7 control variables, and
    matches to the manifest via merge_asof (backward join on start_date).

    Returns a VariableResult whose .data contains:
        file_name, Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, EPS_Growth

    The 'years' parameter to build() is used only to load the manifest subset;
    all Compustat data is loaded once for the full panel.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        # --- resolve raw input paths ---
        compustat_path = (
            root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
        )
        manifest_dir = self._resolve_manifest_dir(root_path)
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        print(f"    CompustatControlsBuilder: loading manifest...")
        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        # Filter to requested years
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        print(f"    CompustatControlsBuilder: loading Compustat...")
        comp = pd.read_parquet(compustat_path, columns=REQUIRED_COMPUSTAT_COLS)
        comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
        comp["datadate"] = pd.to_datetime(comp["datadate"])
        for col in REQUIRED_COMPUSTAT_COLS[2:]:
            comp[col] = pd.to_numeric(comp[col], errors="coerce").astype("float64")

        print(f"    CompustatControlsBuilder: computing controls...")
        comp = _compute_and_winsorize(comp)

        # merge_asof: for each call, find most recent quarterly datadate <= start_date
        manifest_sorted = manifest.sort_values("start_date")
        comp_sorted = comp.sort_values("datadate")

        merged = pd.merge_asof(
            manifest_sorted,
            comp_sorted[["gvkey", "datadate"] + COMPUSTAT_COLS],
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )

        matched = merged["Size"].notna().sum()
        total = len(merged)
        print(
            f"    CompustatControlsBuilder: matched {matched:,}/{total:,} "
            f"({matched / total * 100:.1f}%)"
        )

        result_cols = ["file_name"] + COMPUSTAT_COLS
        data = merged[result_cols].copy()

        # Stats on Size as representative variable
        stats = self.get_stats(data["Size"], "CompustatControls_Size")

        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "source": str(compustat_path),
                "columns": COMPUSTAT_COLS,
                "matched": int(matched),
                "total": int(total),
            },
        )

    def _resolve_manifest_dir(self, root_path: Path) -> Path:
        """Find the latest manifest output directory."""
        from f1d.shared.path_utils import get_latest_output_dir

        return get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )


__all__ = ["CompustatControlsBuilder", "COMPUSTAT_COLS"]
