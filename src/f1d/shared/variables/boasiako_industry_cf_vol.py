"""Boasiako Eq 1 Industry Cash Flow Volatility builder (Phase 1A Task A6).

Spec line 1052 verbatim:
    "Industry Cash Flow Volatility = SD of industry-AVERAGE cash flows
     for previous 10 years (≥3 yrs required)"

This is σ OVER TIME of industry-MEAN CF series (NOT firm-CF σ averaged across firms).
Different from Chen (Task C4), which uses industry-MEDIAN.

Industry classification: FF49 per spec §3.2 footnote 5 (Boasiako uses Fama-French
49-industry, NOT FF48 which is Chen's choice).

Algorithm:
1. Compute firm-year CF using Boasiako Bates 2009 formula (= Eq 1 controls' cash_flow):
   CF_i,t = (OIBDP - XINT - TXT - DVC) / AT
2. Aggregate to industry-MEAN CF per (ff49_code, fyear).
3. For each (ff49_code, fyear): σ over [t-10, t-1] window of the industry-MEAN CF series.
4. v2 audit V3 lock: ≥3 obs floor; <3 → NaN.

Output (per ff49_code × fyear):
    ff49_code, fyear, industry_cf_vol
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from f1d.shared._compustat_annual_reader import read_compustat_annual

from .base import VariableBuilder, VariableResult, VariableStats
from .ff49_industry_classifier import FF49IndustryClassifierBuilder

# v2 audit V3: σ over [t-10, t-1] window with ≥3 obs floor
WINDOW_LEN = 10
MIN_OBS = 3


class BoasiakoIndustryCFVolBuilder(VariableBuilder):
    """Build (ff49_code, fyear, industry_cf_vol) panel for Boasiako Eq 1."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "industry_cf_vol"

    def build(self, years: range, root_path: Path) -> VariableResult:
        # Need extended year window (load years[0]-10 through years[-1]) to compute σ over [t-10, t-1]
        years_list = list(years)
        load_start = years_list[0] - WINDOW_LEN
        load_end = years_list[-1]
        load_years = range(load_start, load_end + 1)

        # Load Compustat fields needed for CF formula (Bates 2009 per audit M3)
        comp = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=["gvkey", "datadate", "sic", "at", "oibdp", "xint", "txt", "dvc"],
            years=load_years,
            us_only=True,
        )
        comp = comp.dropna(subset=["at"]).copy()
        comp = comp[comp["at"] > 0].copy()

        # CF = (OIBDP - XINT - TXT - DVC) / AT (same as Eq 1 controls' cash_flow)
        comp["cf"] = (
            comp["oibdp"].fillna(0)
            - comp["xint"].fillna(0)
            - comp["txt"].fillna(0)
            - comp["dvc"].fillna(0)
        ) / comp["at"]

        # Merge FF49 classifier
        ff49 = FF49IndustryClassifierBuilder().build(years=load_years, root_path=root_path).data
        comp = comp.merge(ff49[["gvkey", "fyear", "ff49_code"]], on=["gvkey", "fyear"], how="inner")

        # Dedup to (gvkey, fyear) — keep last datadate
        comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
        comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

        # Industry-MEAN CF per (ff49_code, fyear)
        ind_mean = (
            comp.groupby(["ff49_code", "fyear"])["cf"]
            .mean()
            .reset_index()
            .rename(columns={"cf": "industry_mean_cf"})
        )

        # Compute σ over [t-WINDOW_LEN, t-1] for each (ff49_code, fyear)
        ind_mean = ind_mean.sort_values(["ff49_code", "fyear"]).reset_index(drop=True)
        rows = []
        for ff49_code, grp in ind_mean.groupby("ff49_code"):
            grp = grp.sort_values("fyear").reset_index(drop=True)
            yr_to_mean: Dict[int, float] = dict(zip(grp["fyear"], grp["industry_mean_cf"]))
            for _, row in grp.iterrows():
                t = int(row["fyear"])
                # Prior-window: fyear in [t - WINDOW_LEN, t - 1]
                window_vals = [
                    yr_to_mean[y] for y in range(t - WINDOW_LEN, t)
                    if y in yr_to_mean and not pd.isna(yr_to_mean[y])
                ]
                if len(window_vals) >= MIN_OBS:
                    sigma = float(np.std(window_vals, ddof=1))
                else:
                    sigma = np.nan
                rows.append({
                    "ff49_code": ff49_code,
                    "fyear": t,
                    "industry_cf_vol": sigma,
                })

        out = pd.DataFrame(rows)
        # Restrict to plan years
        out = out[out["fyear"].isin(years_list)].reset_index(drop=True)

        valid = out["industry_cf_vol"].dropna()
        stats = VariableStats(
            name="industry_cf_vol",
            n=int(len(valid)),
            mean=float(valid.mean()) if len(valid) else 0.0,
            std=float(valid.std()) if len(valid) else 0.0,
            min=float(valid.min()) if len(valid) else 0.0,
            p25=float(valid.quantile(0.25)) if len(valid) else 0.0,
            median=float(valid.median()) if len(valid) else 0.0,
            p75=float(valid.quantile(0.75)) if len(valid) else 0.0,
            max=float(valid.max()) if len(valid) else 0.0,
            n_missing=int(out["industry_cf_vol"].isna().sum()),
            pct_missing=float(out["industry_cf_vol"].isna().mean()),
        )
        metadata: Dict[str, Any] = {
            "source": "Boasiako-O'Connor Keefe (2020) EFM Section 3.3 line 1052",
            "industry_classification": "FF49",  # spec §3.2 footnote 5
            "industry_aggregation": "MEAN",  # spec line 1052; distinct from Chen's MEDIAN
            "window_years": WINDOW_LEN,
            "min_obs_floor": MIN_OBS,
            "n_industries_with_valid_vol": int(out.dropna(subset=["industry_cf_vol"])["ff49_code"].nunique()),
            "n_industry_years": int(len(out)),
            "n_industry_years_with_valid_vol": int(len(valid)),
            "cf_formula": "(OIBDP-XINT-TXT-DVC)/AT (Bates 2009 — audit M3)",
            "column": "industry_cf_vol",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
