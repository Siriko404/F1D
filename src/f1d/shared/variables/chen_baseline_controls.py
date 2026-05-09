"""Chen baseline controls builder (Phase 1C Task C3).

Builds 7 of 8 firm-level controls per Chen 2017 JAAF spec C3 verbatim
(PDF p.6, j.295). The 8th — SIGMA (industry-MEDIAN OCF σ over 10y, FF48) —
is built standalone in Task C4 (`chen_industry_cf_vol_ff48.py`) and merged
in the runner (parallel to Boasiako's Task A6 IndCFVol pattern).

Verbatim definitions (locked via /pdf-strict pdfplumber re-verify 2026-05-08):

    Q     = (#AT + (#PRCC_F · #CSHO − #CEQ)) / #AT
    SIZE  = ln(#AT)
    CF    = #OANCF / #AT     (Chen verbatim — NOT Boasiako's Bates 2009 (OIBDP-XINT-TXT-DVC)/AT)
    NWC   = (#ACT − #CHE − #LCT + #DLC) / #AT     (CORRECTION 2 vs old v1)
    LEV   = (#DLTT + #DLC) / #AT
    NSEG  = count of biz segments  (=1 if missing — Compustat Segment file not in F1D inputs)
    AGE   = ln(yrs since first appearance in Compustat)

Notes / deviations:

- F1D has no Compustat Segment file in inputs/. Per spec C3 verbatim
  "=1 if missing", every gvkey-year gets NSEG=1. Documented as deviation;
  PSM probit absorbs this into intercept.

- AGE under-estimates pre-1990 IPOs since F1D Compustat Annual starts ~1990
  for most firms (audit m7 — same caveat as Boasiako Eq 1 firm_age).

- Winsorization: 1% both tails on continuous controls (pooled across years),
  matching Boasiako Eq 1 pattern. Chen spec does not pin scope; pooled is
  defensible default for annual-frequency panel.

- Window: load 1 year before plan start for AGE first-appearance baseline;
  output restricted to plan years.

- Drop financials (SIC 6000-6999) + utilities (SIC 4900-4999) at reader level
  per spec C1 verbatim.

Output schema:
    gvkey, fyear, q, size, cf, nwc, lev, nseg, age
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from f1d.shared._compustat_annual_reader import read_compustat_annual

from .base import VariableBuilder, VariableResult, VariableStats


CONTINUOUS_CONTROLS: List[str] = [
    "q",
    "size",
    "cf",
    "nwc",
    "lev",
    "age",
]


def _winsorize_1pct(s: pd.Series) -> pd.Series:
    """Clip series to its 1st/99th percentile (pooled across years)."""
    ser = pd.to_numeric(s, errors="coerce")
    p1 = ser.quantile(0.01)
    p99 = ser.quantile(0.99)
    if pd.isna(p1) or pd.isna(p99):
        return ser
    return ser.clip(lower=p1, upper=p99)


class ChenBaselineControlsBuilder(VariableBuilder):
    """Build 7-of-8 control firm-year panel for Chen DiD baseline regression.

    SIGMA (8th control) is built separately by ChenIndustryCFVolFF48Builder
    (Task C4) and merged in the runner.
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "size"  # representative

    def build(self, years: range, root_path: Path) -> VariableResult:
        years_list = list(years)
        # Load 1 year early to support AGE first-appearance baseline
        load_years = range(years_list[0] - 1, years_list[-1] + 1)

        comp = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=[
                "gvkey", "datadate", "sic", "loc",
                "at", "che", "ceq", "csho", "prcc_f",
                "dlc", "dltt", "oancf",
                "act", "lct",
            ],
            years=load_years,
            us_only=True,
        )

        # Drop rows missing AT or with non-positive AT
        comp = comp.dropna(subset=["at"]).copy()
        comp = comp[comp["at"] > 0].copy()

        # Sort for downstream operations
        comp = comp.sort_values(["gvkey", "fyear"], kind="stable").reset_index(drop=True)

        # 1. Q = (#AT + (#PRCC_F · #CSHO − #CEQ)) / #AT
        mve = comp["prcc_f"] * comp["csho"]
        comp["q"] = (comp["at"] + (mve - comp["ceq"])) / comp["at"]

        # 2. SIZE = ln(#AT)
        comp["size"] = np.log(comp["at"])

        # 3. CF = #OANCF / #AT (Chen verbatim — NOT Boasiako's Bates 2009)
        comp["cf"] = comp["oancf"] / comp["at"]

        # 4. NWC = (#ACT − #CHE − #LCT + #DLC) / #AT (CORRECTION 2)
        comp["nwc"] = (
            comp["act"]
            - comp["che"].fillna(0)
            - comp["lct"]
            + comp["dlc"].fillna(0)
        ) / comp["at"]

        # 5. LEV = (#DLTT + #DLC) / #AT
        comp["lev"] = (
            comp["dltt"].fillna(0) + comp["dlc"].fillna(0)
        ) / comp["at"]

        # 6. NSEG = 1 (no Compustat Segment file in F1D inputs; per spec verbatim "=1 if missing")
        comp["nseg"] = 1

        # 7. AGE = ln(yrs since first appearance in Compustat)
        first_year = comp.groupby("gvkey")["fyear"].transform("min")
        years_active = (comp["fyear"] - first_year).clip(lower=1)
        comp["age"] = np.log(years_active.astype(float))

        # Restrict to plan years (drop the lag-loading first year)
        comp = comp[comp["fyear"].isin(years_list)].copy()

        # Dedup to (gvkey, fyear) — keep last datadate
        comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
        comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

        # Winsorize 1% on continuous controls (pooled; post-dedup so percentiles match
        # the actual regression-sample distribution)
        for col in CONTINUOUS_CONTROLS:
            comp[col] = _winsorize_1pct(comp[col])

        out_cols = ["gvkey", "fyear"] + CONTINUOUS_CONTROLS + ["nseg"]
        out = comp[out_cols].reset_index(drop=True)

        # Stats on representative col (size)
        sz = out["size"].dropna()
        stats = VariableStats(
            name="size",
            n=int(len(sz)),
            mean=float(sz.mean()),
            std=float(sz.std()),
            min=float(sz.min()),
            p25=float(sz.quantile(0.25)),
            median=float(sz.median()),
            p75=float(sz.quantile(0.75)),
            max=float(sz.max()),
            n_missing=int(out["size"].isna().sum()),
            pct_missing=float(out["size"].isna().mean()),
        )
        metadata: Dict[str, Any] = {
            "source": "Chen et al (2017) JAAF Section 3 + Table 4 footer (PDF p.6 + p.15)",
            "n_controls": 7,
            "n_continuous_controls": len(CONTINUOUS_CONTROLS),
            "winsorize_pct": 0.01,
            "winsorize_scope": "pooled across years",
            "cf_formula": "OANCF/AT (Chen verbatim — NOT Boasiako's Bates 2009)",
            "nwc_formula": "(ACT - CHE - LCT + DLC) / AT (Chen CORRECTION 2)",
            "q_formula": "(AT + (PRCC_F * CSHO - CEQ)) / AT",
            "lev_formula": "(DLTT + DLC) / AT",
            "nseg_default": 1,
            "nseg_caveat": "Compustat Segment file not in F1D inputs/; per spec '=1 if missing'",
            "age_caveat": "log(years since first F1D Compustat appearance); under-estimates pre-1990 IPOs (audit m7)",
            "n_firm_years": len(out),
            "years": [years_list[0], years_list[-1]],
            "column": "size",
            "task": "Phase 1C C3",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
