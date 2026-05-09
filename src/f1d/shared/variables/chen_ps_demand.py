"""Chen PS_DEMAND builder (Phase 1C Task C6).

Per Chen 2017 JAAF spec C7 (PDF p.14-16, j.303-305) verbatim — Duchin 2010 framework:

    Three components per (FF48, fyear):
      IND_STDCF    = σ over previous 10y of industry-MEDIAN CF (CF=OANCF/AT)
      IND_STDQ     = σ over previous 10y of industry-MEDIAN Q  (Q=(AT+(PRCC_F·CSHO−CEQ))/AT)
      NEG_IND_CORR = -1 × corr over previous 10y of (industry-MEDIAN CF, industry-MEDIAN Q)

    PS_DEMAND = mean of percentile ranks of three components, per fyear.

v2 audit V2 lock: percentile rank computed AFTER -1× flip on NEG_IND_CORR
(higher PS_DEMAND ↔ higher precautionary-savings demand).

Distinct from Task C4 SIGMA (firm-σ-then-industry-MEDIAN); this is
σ-of-industry-MEDIAN-series (inverted aggregation order — different number).

Output (per ff48_code × fyear):
    ff48_code, fyear,
    ind_stdcf, ind_stdq, neg_ind_corr,
    pct_ind_stdcf, pct_ind_stdq, pct_neg_ind_corr,
    ps_demand
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from f1d.shared._compustat_annual_reader import read_compustat_annual

from .base import VariableBuilder, VariableResult, VariableStats
from .ff48_industry_classifier import FF48IndustryClassifierBuilder

WINDOW_LEN = 10
MIN_OBS = 3


def _rolling_window_stat(
    series_by_year: Dict[int, float],
    t: int,
    stat: str,
    other_series: Dict[int, float] = None,
    window: int = WINDOW_LEN,
    min_obs: int = MIN_OBS,
) -> float:
    """Compute rolling window stat for a (year → value) series.

    Args:
        series_by_year: {fyear: value}.
        t: target fyear.
        stat: 'std' or 'corr'.
        other_series: required for 'corr' — second {fyear: value}.
        window: prior-window length (10y).
        min_obs: ≥ this many overlap obs required.
    """
    if stat == "std":
        vals = [
            series_by_year[y] for y in range(t - window, t)
            if y in series_by_year and not pd.isna(series_by_year[y])
        ]
        if len(vals) < min_obs:
            return np.nan
        return float(np.std(vals, ddof=1))
    elif stat == "corr":
        if other_series is None:
            raise ValueError("corr requires other_series")
        pairs = [
            (series_by_year[y], other_series[y])
            for y in range(t - window, t)
            if (
                y in series_by_year and y in other_series
                and not pd.isna(series_by_year[y])
                and not pd.isna(other_series[y])
            )
        ]
        if len(pairs) < min_obs:
            return np.nan
        a, b = zip(*pairs)
        a, b = np.array(a), np.array(b)
        sa, sb = a.std(ddof=1), b.std(ddof=1)
        if sa == 0 or sb == 0:
            return np.nan
        return float(np.corrcoef(a, b)[0, 1])
    else:
        raise ValueError(f"Unknown stat: {stat}")


class ChenPSDemandBuilder(VariableBuilder):
    """Build (ff48_code, fyear, ind_stdcf, ind_stdq, neg_ind_corr, ps_demand) panel."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "ps_demand"

    def build(self, years: range, root_path: Path) -> VariableResult:
        years_list = list(years)
        load_start = years_list[0] - WINDOW_LEN
        load_end = years_list[-1]
        load_years = range(load_start, load_end + 1)

        comp = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=["gvkey", "datadate", "sic", "at", "oancf", "csho", "prcc_f", "ceq"],
            years=load_years,
            us_only=True,
        )
        comp = comp.dropna(subset=["at"]).copy()
        comp = comp[comp["at"] > 0].copy()

        # CF = OANCF / AT (Chen verbatim)
        comp["cf"] = comp["oancf"] / comp["at"]
        # Q = (AT + (PRCC_F·CSHO - CEQ)) / AT
        mve = comp["prcc_f"] * comp["csho"]
        comp["q"] = (comp["at"] + (mve - comp["ceq"])) / comp["at"]

        # Dedup to (gvkey, fyear)
        comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
        comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

        # Merge FF48
        ff48 = FF48IndustryClassifierBuilder().build(years=load_years, root_path=root_path).data
        comp = comp.merge(ff48[["gvkey", "fyear", "ff48_code"]], on=["gvkey", "fyear"], how="inner")

        # Industry-MEDIAN CF and Q per (ff48_code, fyear)
        ind_med = (
            comp.dropna(subset=["cf", "q"])
            .groupby(["ff48_code", "fyear"], as_index=False)
            .agg(industry_median_cf=("cf", "median"), industry_median_q=("q", "median"))
        )

        # Compute IND_STDCF, IND_STDQ, NEG_IND_CORR per (ff48, target_year) over [t-10, t-1]
        rows = []
        for ff48_code, grp in ind_med.groupby("ff48_code"):
            grp = grp.sort_values("fyear").reset_index(drop=True)
            cf_by_y: Dict[int, float] = dict(zip(grp["fyear"].astype(int), grp["industry_median_cf"]))
            q_by_y: Dict[int, float] = dict(zip(grp["fyear"].astype(int), grp["industry_median_q"]))
            for t in grp["fyear"].astype(int):
                ind_stdcf = _rolling_window_stat(cf_by_y, t, "std")
                ind_stdq = _rolling_window_stat(q_by_y, t, "std")
                ind_corr = _rolling_window_stat(cf_by_y, t, "corr", other_series=q_by_y)
                neg_ind_corr = -1.0 * ind_corr if not pd.isna(ind_corr) else np.nan
                rows.append({
                    "ff48_code": int(ff48_code),
                    "fyear": int(t),
                    "ind_stdcf": ind_stdcf,
                    "ind_stdq": ind_stdq,
                    "neg_ind_corr": neg_ind_corr,
                })
        out = pd.DataFrame(rows)

        # Audit V2: percentile rank AFTER -1× flip (already applied above).
        # Per fyear (cross-section), rank each component across FF48s present.
        for col in ["ind_stdcf", "ind_stdq", "neg_ind_corr"]:
            out[f"pct_{col}"] = out.groupby("fyear")[col].rank(pct=True)

        # PS_DEMAND = mean of three percentile ranks
        out["ps_demand"] = out[["pct_ind_stdcf", "pct_ind_stdq", "pct_neg_ind_corr"]].mean(axis=1)

        # Restrict to plan years
        out = out[out["fyear"].isin(years_list)].reset_index(drop=True)

        valid = out["ps_demand"].dropna()
        stats = VariableStats(
            name="ps_demand",
            n=int(len(valid)),
            mean=float(valid.mean()) if len(valid) else 0.0,
            std=float(valid.std()) if len(valid) else 0.0,
            min=float(valid.min()) if len(valid) else 0.0,
            p25=float(valid.quantile(0.25)) if len(valid) else 0.0,
            median=float(valid.median()) if len(valid) else 0.0,
            p75=float(valid.quantile(0.75)) if len(valid) else 0.0,
            max=float(valid.max()) if len(valid) else 0.0,
            n_missing=int(out["ps_demand"].isna().sum()),
            pct_missing=float(out["ps_demand"].isna().mean()),
        )
        metadata: Dict[str, Any] = {
            "source": "Chen et al (2017) JAAF Section C7 + Table 4 footer (PDF p.14-16, j.303-305)",
            "framework": "Duchin (2010) precautionary-savings demand",
            "industry_classification": "FF48",
            "window_years": WINDOW_LEN,
            "min_obs_floor": MIN_OBS,
            "components": {
                "IND_STDCF": "σ over 10y of industry-MEDIAN CF (CF=OANCF/AT)",
                "IND_STDQ": "σ over 10y of industry-MEDIAN Q",
                "NEG_IND_CORR": "-1 × corr over 10y of industry-MEDIAN CF and Q series",
            },
            "audit_v2_locked": "percentile rank computed AFTER -1× flip on NEG_IND_CORR",
            "ps_demand_formula": "mean of percentile ranks across (IND_STDCF, IND_STDQ, NEG_IND_CORR)",
            "vs_chen_sigma": "C4 SIGMA = firm-σ-then-industry-MEDIAN (different aggregation order — different value)",
            "n_industry_years": int(len(out)),
            "n_industry_years_valid": int(len(valid)),
            "column": "ps_demand",
            "task": "Phase 1C C6",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
