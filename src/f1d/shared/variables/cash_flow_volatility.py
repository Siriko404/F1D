"""Builder for CFvol — Han-Qiu (2007) JCF cash-flow volatility moderator.

Anchor (verbatim, Section 3 p. 52):
  "...cash flow volatility, CVCFi,t, which is defined as the coefficient of
   variation in a firm's quarterly cash flow over the past 4 years (16 quarters).
   The coefficient of variation is the standard deviation of operating cash flow
   scaled by the absolute value of the mean over the same period."

Formula:
  CFvol_{i,t} = StdDev(OCF_q over t-15..t)  /  |Mean(OCF_q over t-15..t)|

Quarterly OCF derivation: oancfy is YTD cumulative within fiscal year.
  OCF_q = oancfy_t - oancfy_{t-1}  (within same gvkey + fyearq)
  For fqtr=1 (first quarter of fiscal year): OCF_q = oancfy (no subtraction)

Lag: CFvol_{i,t-1} per Han-Qiu Eq.5 RHS specification.

Merge: per-call file_name via merge_asof on (gvkey, start_date -> datadate).

Requires Compustat columns: gvkey, datadate, fyearq, fqtr, oancfy.
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
WINDOW_QUARTERS = 16  # Han-Qiu verbatim


def _load_compustat_quarterly_ocf(root_path: Path) -> pd.DataFrame:
    """Load Compustat quarterly OCF columns from BOTH:
       - inputs/comp_na_daily_all/comp_na_daily_all.parquet (2000-2020)
       - inputs/Compustat_Quarterly_OCF_Extended/*.parquet  (1990-2002, gap fill)
    Concatenate, dedup on (gvkey, datadate) keeping LATER file (the gap-fill is the
    authoritative source for the overlap period; same column source from WRDS comp.fundq).
    """
    cols = ["gvkey", "datadate", "fyearq", "fqtr", "oancfy"]

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

    frames = [main] + extended_frames
    combined = pd.concat(frames, ignore_index=True)

    # Dedup (gvkey, datadate) — both sources from comp.fundq, identical schema; main first
    # so duplicates resolved to main file (latest restatement). For pre-2000 dates only
    # extended is present, so no conflict there.
    combined = combined.sort_values(["gvkey", "datadate"], kind="stable")
    combined = combined.drop_duplicates(subset=["gvkey", "datadate"], keep="first")
    combined = combined.dropna(subset=["fyearq", "fqtr"])
    return combined


def _compute_quarterly_ocf(comp: pd.DataFrame) -> pd.Series:
    """Convert YTD oancfy to quarterly OCF via within-fyearq diff."""
    comp = comp.sort_values(["gvkey", "fyearq", "fqtr"], kind="stable")
    prev_oancfy = comp.groupby(["gvkey", "fyearq"])["oancfy"].shift(1)
    # First quarter of fyearq has no prior; oancfy IS the quarterly value
    quarterly_ocf = comp["oancfy"] - prev_oancfy.fillna(0)
    return quarterly_ocf


def _compute_cfvol(comp: pd.DataFrame) -> pd.DataFrame:
    """Per-gvkey 16-quarter rolling CV of quarterly OCF; lag by 1 quarter.

    Returns DataFrame: gvkey, datadate, CFvol (already lagged per Han-Qiu).
    """
    comp = comp.sort_values(["gvkey", "datadate"], kind="stable").copy()
    comp["ocf_q"] = _compute_quarterly_ocf(comp)

    grp = comp.groupby("gvkey", sort=False)["ocf_q"]
    comp["ocf_std_16q"] = grp.transform(lambda x: x.rolling(WINDOW_QUARTERS, min_periods=WINDOW_QUARTERS).std())
    comp["ocf_mean_16q"] = grp.transform(lambda x: x.rolling(WINDOW_QUARTERS, min_periods=WINDOW_QUARTERS).mean())

    cfvol_raw = comp["ocf_std_16q"] / comp["ocf_mean_16q"].abs()
    cfvol_raw = cfvol_raw.replace([np.inf, -np.inf], np.nan)
    comp["CFvol_contemp"] = cfvol_raw

    # Lag by 1 quarter per Han-Qiu Eq.5 RHS (CVCF_{i,t-1})
    comp["CFvol"] = comp.groupby("gvkey", sort=False)["CFvol_contemp"].shift(1)

    return comp[["gvkey", "datadate", "CFvol"]].copy()


class CashFlowVolatilityBuilder(VariableBuilder):
    """Build CFvol per Han-Qiu (2007) — 16-quarter CV of quarterly OCF, lagged.

    Returns (file_name, CFvol) keyed on call file_name via merge_asof on
    (gvkey, start_date -> Compustat datadate, backward direction).
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

        # Load full Compustat (1990-2020) by combining gap-fill + main files
        comp = _load_compustat_quarterly_ocf(root_path)

        cfvol_df = _compute_cfvol(comp)

        # merge_asof to manifest via call start_date -> Compustat datadate (backward)
        # merge_asof requires BOTH sides sorted on the merge key (datadate / start_date)
        cfvol_df = cfvol_df.dropna(subset=["CFvol"]).sort_values("datadate")
        manifest_sorted = manifest.sort_values("start_date")

        merged = pd.merge_asof(
            manifest_sorted,
            cfvol_df,
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )

        data = merged[["file_name", "CFvol"]].copy()
        stats = self.get_stats(data["CFvol"], "CFvol")

        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "CFvol",
                "source": "Compustat oancfy / Han-Qiu 2007 16q CV (lagged)",
                "window_quarters": WINDOW_QUARTERS,
                "anchor": "Han-Qiu 2007 JCF Section 3 p. 52",
            },
        )


__all__ = ["CashFlowVolatilityBuilder"]
