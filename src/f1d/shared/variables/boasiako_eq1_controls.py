"""Boasiako Eq 1 controls builder (Phase 1A Task A5).

Builds 11 firm-level controls per spec §3.3 verbatim:

    1.  Firm Size              = log(AT)
    2.  Firm Age               = log(years_in_CRSP_Compustat)
    3.  Book Leverage          = (DLC + DLTT) / AT
    4.  Market-to-book         = (AT - BVE + MVE) / AT
                                 BVE = CEQ; MVE = PRCC_F * CSHO
    5.  Cash Flow              = (OIBDP - XINT - TXT - DVC) / AT
                                 (audit M3: Bates 2009 interpretation; spec wording
                                  'earnings after interest, dividends, and taxes but
                                  before depreciation' is non-standard)
    6.  Capital Expenditure    = CAPX / AT_BoY (lag1)
    7.  Acquisition Expenditure = AQC / AT_BoY
    8.  Dividend Paying        = 1 if (DVC > 0) else 0
    9.  R&D Expenditure        = XRD / AT_BoY  (missing → 0)
    10. Net Working Capital    = (ACT - LCT - DLC) / (AT - CHE)
                                 (NET_ASSETS denom = AT - CHE per spec §3.3 footnote)
    11. Industry Cash Flow Vol = built SEPARATELY in Task A6 (not in this output)

Winsorize 1% both tails on all firm-level continuous variables per spec line 1054.

v2 audit M3 — CF formula is Bates 2009 interpretation:
- Spec line 1046 wording 'earnings after interest, dividends, and taxes but
  before depreciation' is non-standard.
- Plan picks (OIBDP - XINT - TXT - DVC) / AT per Bates 2009.
- Mid-execution NLM verify recommended; sensitivity with DVT (total div) instead
  of DVC if results unstable.

m7 audit deviation — Firm Age:
- Computed as fyear - min(fyear) over each gvkey's appearance in F1D's
  compustat_annual.csv (which starts ~1990 for most firms).
- For firms IPO'd before 1990 this UNDER-estimates age. Documented as deviation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from f1d.shared._compustat_annual_reader import read_compustat_annual

from .base import VariableBuilder, VariableResult, VariableStats


CONTINUOUS_CONTROLS: List[str] = [
    "firm_size",
    "firm_age",
    "book_leverage",
    "market_to_book",
    "cash_flow",
    "capital_expenditure",
    "acquisition_expenditure",
    "rd_expenditure",
    "nwc",
]


def _winsorize_1pct(s: pd.Series) -> pd.Series:
    """Clip series to its 1st/99th percentile per spec line 1054."""
    ser = pd.to_numeric(s, errors="coerce")
    p1 = ser.quantile(0.01)
    p99 = ser.quantile(0.99)
    if pd.isna(p1) or pd.isna(p99):
        return ser
    return ser.clip(lower=p1, upper=p99)


class BoasiakoEq1ControlsBuilder(VariableBuilder):
    """Build 11-control firm-year panel for Boasiako Eq 1."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "firm_size"  # representative

    def build(self, years: range, root_path: Path) -> VariableResult:
        # Load Compustat Annual fields needed for 10 of 11 controls (IndCFVol is Task A6)
        # We need a wider year window for lag computation (load years[0]-1 through years[-1])
        years_list = list(years)
        load_years = range(years_list[0] - 1, years_list[-1] + 1)

        comp = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=[
                "gvkey", "datadate", "sic", "state", "loc",
                "at", "che", "ceq", "csho", "prcc_f",
                "dlc", "dltt", "oibdp", "xint", "txt", "dvc", "dvt",
                "capx", "aqc", "xrd", "act", "lct",
            ],
            years=load_years,
            us_only=True,
        )

        # Drop rows missing AT or with non-positive AT
        comp = comp.dropna(subset=["at"]).copy()
        comp = comp[comp["at"] > 0].copy()

        # Sort for lag computation
        comp = comp.sort_values(["gvkey", "fyear"], kind="stable").reset_index(drop=True)

        # Lag-1 AT (BoY) for ratio denominators
        comp["at_lag"] = comp.groupby("gvkey")["at"].shift(1)

        # 1. Firm Size = log(AT)
        comp["firm_size"] = np.log(comp["at"])

        # 2. Firm Age = log(years since first F1D appearance) — audit m7 deviation acknowledged
        first_year = comp.groupby("gvkey")["fyear"].transform("min")
        years_active = (comp["fyear"] - first_year).clip(lower=1)  # at least 1 to avoid log(0)
        comp["firm_age"] = np.log(years_active.astype(float))

        # 3. Book Leverage = (DLC + DLTT) / AT
        comp["book_leverage"] = (
            comp["dlc"].fillna(0) + comp["dltt"].fillna(0)
        ) / comp["at"]

        # 4. Market-to-book = (AT - BVE + MVE) / AT
        bve = comp["ceq"]
        mve = comp["prcc_f"] * comp["csho"]
        comp["market_to_book"] = (comp["at"] - bve + mve) / comp["at"]

        # 5. Cash Flow = (OIBDP - XINT - TXT - DVC) / AT (audit M3: Bates 2009 interpretation)
        comp["cash_flow"] = (
            comp["oibdp"].fillna(0)
            - comp["xint"].fillna(0)
            - comp["txt"].fillna(0)
            - comp["dvc"].fillna(0)
        ) / comp["at"]

        # 6. Capital Expenditure = CAPX / AT_BoY
        comp["capital_expenditure"] = comp["capx"] / comp["at_lag"]

        # 7. Acquisition Expenditure = AQC / AT_BoY
        comp["acquisition_expenditure"] = comp["aqc"] / comp["at_lag"]

        # 8. Dividend Paying = 1 if DVC > 0
        comp["dividend_paying"] = (comp["dvc"].fillna(0) > 0).astype(int)

        # 9. R&D Expenditure = XRD / AT_BoY (missing → 0 per spec line 1071 verbatim)
        comp["rd_expenditure"] = comp["xrd"].fillna(0) / comp["at_lag"]

        # 10. NWC = (ACT - LCT - DLC) / (AT - CHE) (net-assets denom per spec §3.3 footnote)
        net_assets = comp["at"] - comp["che"].fillna(0)
        nwc_num = comp["act"] - comp["lct"] - comp["dlc"].fillna(0)
        comp["nwc"] = np.where(net_assets > 0, nwc_num / net_assets, np.nan)

        # Restrict to plan years (drop the lag-loading first year)
        comp = comp[comp["fyear"].isin(years_list)].copy()

        # Dedup to (gvkey, fyear) — keep last datadate
        comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
        comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

        # Winsorize 1% both tails on continuous controls per spec line 1054
        # (post-dedup so percentiles match the actual regression-sample distribution)
        for col in CONTINUOUS_CONTROLS:
            comp[col] = _winsorize_1pct(comp[col])

        # Final output
        out_cols = ["gvkey", "fyear"] + CONTINUOUS_CONTROLS + ["dividend_paying"]
        out = comp[out_cols].reset_index(drop=True)

        # Stats on representative col (firm_size)
        fs = out["firm_size"].dropna()
        stats = VariableStats(
            name="firm_size",
            n=int(len(fs)),
            mean=float(fs.mean()),
            std=float(fs.std()),
            min=float(fs.min()),
            p25=float(fs.quantile(0.25)),
            median=float(fs.median()),
            p75=float(fs.quantile(0.75)),
            max=float(fs.max()),
            n_missing=int(out["firm_size"].isna().sum()),
            pct_missing=float(out["firm_size"].isna().mean()),
        )
        metadata: Dict[str, Any] = {
            "source": "Boasiako-O'Connor Keefe (2020) EFM Section 3.3 spec verbatim",
            "n_controls": 11,
            "n_continuous_controls": len(CONTINUOUS_CONTROLS),
            "winsorize_pct": 0.01,
            "cf_formula": "(OIBDP-XINT-TXT-DVC)/AT (Bates 2009 interpretation per audit M3)",
            "nwc_denom": "AT - CHE (net-assets denom per spec §3.3 footnote)",
            "rd_missing_zero": True,
            "firm_age_caveat": "log(years since first F1D Compustat appearance); under-estimates pre-1990 IPOs (audit m7)",
            "n_firm_years": len(out),
            "years": [years_list[0], years_list[-1]],
            "column": "firm_size",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
