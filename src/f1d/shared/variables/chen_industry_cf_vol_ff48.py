"""Chen Industry Cash Flow Volatility builder (Phase 1C Task C4).

Per Chen 2017 JAAF spec C3 (PDF p.6, j.295) verbatim — SIGMA control:
    "industry-MEDIAN of std-dev of OCF over previous 10 yrs"
    Industry classification: FF48 (Table 4 footer PDF p.15)

Construction (firm-σ-then-industry-MEDIAN, distinct from Chen's PS_DEMAND
IND_STDCF in Task C6 which is σ-of-industry-MEDIAN-series):

1. Compute CF_i,t = OANCF / AT per firm-year (matches Chen baseline CF in C3,
   distinct from Boasiako Bates 2009 (OIBDP-XINT-TXT-DVC)/AT in Task A6).
2. Per firm: σ over fyears [t-10, t-1] of firm-level CF (≥3 obs floor —
   audit V3 lock inherited from Boasiako Task A6).
3. Merge FF48 industry assignment (Task C1).
4. Per (ff48, fyear): industry-MEDIAN over firms of firm-level σ.

Distinct from:
- Boasiako IndCFVol (Task A6): CF=Bates 2009; σ-of-industry-MEAN-CF-series; FF49.
- Chen IND_STDCF (Task C6 PS_DEMAND): σ-of-industry-MEDIAN-CF-series; FF48.

Output (per ff48_code × fyear):
    ff48_code, fyear, sigma_chen
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from f1d.shared._compustat_annual_reader import read_compustat_annual

from .base import VariableBuilder, VariableResult, VariableStats
from .ff48_industry_classifier import FF48IndustryClassifierBuilder

# v2 audit V3 inherited: σ over [t-10, t-1] window with ≥3 obs floor
WINDOW_LEN = 10
MIN_OBS = 3


def _firm_sigma_over_window(
    firm_cf: Dict[int, float], t: int, window: int = WINDOW_LEN, min_obs: int = MIN_OBS
) -> float:
    """Compute σ of firm's CF over fyears [t-window, t-1] with min_obs floor."""
    vals = [
        firm_cf[y] for y in range(t - window, t)
        if y in firm_cf and not pd.isna(firm_cf[y])
    ]
    if len(vals) < min_obs:
        return np.nan
    return float(np.std(vals, ddof=1))


class ChenIndustryCFVolFF48Builder(VariableBuilder):
    """Build (ff48_code, fyear, sigma_chen) panel for Chen baseline + PSM."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "sigma_chen"

    def build(self, years: range, root_path: Path) -> VariableResult:
        years_list = list(years)
        # Load 10y prefix for window calculation
        load_start = years_list[0] - WINDOW_LEN
        load_end = years_list[-1]
        load_years = range(load_start, load_end + 1)

        # Load Compustat fields needed for CF (Chen verbatim OANCF/AT)
        comp = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=["gvkey", "datadate", "sic", "at", "oancf"],
            years=load_years,
            us_only=True,
        )
        comp = comp.dropna(subset=["at"]).copy()
        comp = comp[comp["at"] > 0].copy()

        # CF = OANCF/AT (Chen verbatim — NOT Boasiako Bates 2009)
        comp["cf"] = comp["oancf"] / comp["at"]
        comp = comp.dropna(subset=["cf"]).copy()

        # Dedup to (gvkey, fyear) — keep last datadate
        comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
        comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")
        comp["fyear"] = comp["fyear"].astype(int)

        # Compute firm-level σ over [t-10, t-1] per (gvkey, fyear)
        firm_sigma_rows = []
        for gvkey, grp in comp.groupby("gvkey"):
            firm_cf: Dict[int, float] = dict(zip(grp["fyear"], grp["cf"]))
            for t in grp["fyear"]:
                sigma = _firm_sigma_over_window(firm_cf, int(t))
                firm_sigma_rows.append({
                    "gvkey": gvkey,
                    "fyear": int(t),
                    "firm_sigma": sigma,
                })
        firm_sigma_df = pd.DataFrame(firm_sigma_rows)

        # Merge FF48
        ff48 = FF48IndustryClassifierBuilder().build(years=load_years, root_path=root_path).data
        firm_sigma_df = firm_sigma_df.merge(
            ff48[["gvkey", "fyear", "ff48_code"]], on=["gvkey", "fyear"], how="inner"
        )

        # Industry-MEDIAN of firm-σ per (ff48, fyear)
        out = (
            firm_sigma_df.dropna(subset=["firm_sigma"])
            .groupby(["ff48_code", "fyear"])["firm_sigma"]
            .median()
            .reset_index()
            .rename(columns={"firm_sigma": "sigma_chen"})
        )

        # Restrict to plan years
        out = out[out["fyear"].isin(years_list)].reset_index(drop=True)

        valid = out["sigma_chen"].dropna()
        stats = VariableStats(
            name="sigma_chen",
            n=int(len(valid)),
            mean=float(valid.mean()) if len(valid) else 0.0,
            std=float(valid.std()) if len(valid) else 0.0,
            min=float(valid.min()) if len(valid) else 0.0,
            p25=float(valid.quantile(0.25)) if len(valid) else 0.0,
            median=float(valid.median()) if len(valid) else 0.0,
            p75=float(valid.quantile(0.75)) if len(valid) else 0.0,
            max=float(valid.max()) if len(valid) else 0.0,
            n_missing=int(out["sigma_chen"].isna().sum()),
            pct_missing=float(out["sigma_chen"].isna().mean()),
        )
        metadata: Dict[str, Any] = {
            "source": "Chen et al (2017) JAAF spec C3 SIGMA + Table 4 footer (PDF p.6 + p.15)",
            "industry_classification": "FF48",  # Chen Table 4 footer; distinct from Boasiako FF49
            "industry_aggregation": "MEDIAN",  # spec C3; distinct from Boasiako MEAN
            "construction": "firm-σ-then-industry-MEDIAN",
            "vs_boasiako": "Boasiako = σ-of-industry-MEAN-CF-series (different)",
            "vs_chen_ind_stdcf": "C6 IND_STDCF = σ-of-industry-MEDIAN-CF-series (different — same formula but inverted aggregation order)",
            "window_years": WINDOW_LEN,
            "min_obs_floor": MIN_OBS,
            "cf_formula": "OANCF/AT (Chen verbatim — NOT Boasiako Bates 2009)",
            "n_industries_with_valid_vol": int(out.dropna(subset=["sigma_chen"])["ff48_code"].nunique()),
            "n_industry_years": int(len(out)),
            "n_industry_years_with_valid_vol": int(len(valid)),
            "column": "sigma_chen",
            "task": "Phase 1C C4",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
