#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1.2 HFC Channel — CEO 2-IV DECOMPOSED (DWZ Eq.5 × Unrated)
================================================================================
ID: econometric/run_h1_2_cash_constraint_ceo2iv_decomp
Description: DWZ-decomposition variant of H1.2.ceo2. Replaces the main
             speech-uncertainty IV stack (UncAnsCEO_c + UncPreCEO_c) with the
             DWZ Eq.5 decomposition: ClarityCEO_QtrExp_c (persistent CEO trait,
             = -CEO FE) + UncResCEO_QtrExp_c (call-level state residual).
             Both decomp components computed via strict no-look-ahead
             quarterly-expanding fit of DWZ Eq.4 — see
             run_h0_3_ceo_clarity_expanding.py. Both decomp IVs mean-centered
             on Main sample. ONE Unrated interaction term estimated: UncResCEO ×
             Unrated (state channel only). ClarityCEO × Unrated DROPPED — trait
             × constraint has theoretically ambiguous direction (constraint
             priority pushes cash UP, clarity perception pushes cash DOWN —
             competing forces with no clean monotone prediction). Moderator is
             BINARY Unrated vs Rated (FP 2006 verbatim spec) — BelowIG level
             dummy AND BelowIG interactions DROPPED entirely. Reference group =
             Rated firms (IG ∪ BelowIG).

Tail directions:
    Main ClarityCEO_QtrExp_c: one-tail NEG
        (high persistent clarity → less precautionary cash; HC at trait level)
    Main UncResCEO_QtrExp_c: one-tail POS
        (positive within-quarter uncertainty surprise → more cash; HC at state level)
    Interaction UncResCEO × Unrated: one-tail POS
        (HFC amplification at state level — clean precautionary mechanism)
    Unrated level dummy: two-tailed (no directional prior on level shift).

Channel: CH1 — Precautionary liquidity under external-finance frictions.

Parent suite: H1.2.ceo2 (Cash × Constraint, CEO 2-IV UncAns/UncPre)
DWZ source: Demerjian, Wang & Zarowin (2021), Eq.4 + Eq.5.

Model Specification:
    CashRatio = b1*ClarityCEO_c + b2*UncResCEO_c
              + b3*Unrated
              + b4*(UncResCEO_c x Unrated)
              + controls + IndustryFE + CalendarYearFE + e

16 Models (8 displayed: cols 5-8 + 13-16 = interaction specs only):
    Block 1 (cols 1-8):  DV = CashRatio_t
    Block 2 (cols 9-16): DV = CashRatio_lead

Moderator: BINARY Unrated dummy from S&P splticrm (Compustat Daily Ratings).
    Rated (reference): any splticrm match (IG and BelowIG combined per FP 2006)
    Unrated: no splticrm match
    Merge: merge_asof on (gvkey, start_date) — no look-ahead.

Sample: Main only (FF12 not in {8, 11}). Fiscal years 2002-2016. Decomp parquet
    merge drops rows with NaN Clarity/UncRes (Q1 of each year unestimable under
    strict-expanding spec). Final sample size strictly smaller than parent
    H1.2.ceo2 due to decomp coverage cost.

Unit: Call-level. Panel index: ["gvkey", "cal_yr"] or ["gvkey", "cal_yr_qtr"].
SEs: Firm-clustered.

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet
    - outputs/econometric/ceo_clarity_expanding/<latest>/ceo_clarity_qtrexp_residuals.parquet
    - inputs/compustat_daily_ratings/compustat_daily_ratings.csv

Outputs:
    - outputs/econometric/h1_2_cash_constraint_ceo2iv_decomp/{timestamp}/...

Deterministic: true
Author: Thesis Author
Date: 2026-04-23
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import (
    extract_coefs_panelols,
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

# Dual-stack 5-IV design (per H1 pilot pattern, commit 484eeda).
# Two regressions per cell on intersection sample:
#   Reg A (DWZ-faithful Full):    Cash ~ Clarity_c + UncRes_c + UncPre_c + Unr [+ ints] + ctrls + FE
#   Reg B (No-look-ahead QtrExp): Cash ~ Clarity_QtrExp_c + UncRes_QtrExp_c + UncPre_c + Unr [+ ints] + ctrls + FE
# All centered on Main sample for clean interaction interpretation.
# UncPreCEO_c is shared between Reg A and Reg B; Reg A is canonical display source.

# Reg A (Full method) IVs
IVS_REG_A_RAW = ["ClarityCEO", "UncResCEO", "UncPreCEO"]
IVS_REG_A_CENTERED = ["ClarityCEO_c", "UncResCEO_c", "UncPreCEO_c"]

# Reg B (QtrExp method) IVs
IVS_REG_B_RAW = ["ClarityCEO_QtrExp", "UncResCEO_QtrExp", "UncPreCEO"]
IVS_REG_B_CENTERED = ["ClarityCEO_QtrExp_c", "UncResCEO_QtrExp_c", "UncPreCEO_c"]

# All 5 unique raw + centered IVs (UncPreCEO is shared; centering applied to all 5)
ALL_RAW_IVS = ["ClarityCEO", "UncResCEO", "ClarityCEO_QtrExp", "UncResCEO_QtrExp", "UncPreCEO"]
ALL_CENTERED_IVS = ["ClarityCEO_c", "UncResCEO_c", "ClarityCEO_QtrExp_c", "UncResCEO_QtrExp_c", "UncPreCEO_c"]
IV_RAW_TO_CENTERED = dict(zip(ALL_RAW_IVS, ALL_CENTERED_IVS))

# Legacy aliases (some downstream code paths reference IVS_RAW/IVS_CENTERED).
# Kept for backwards compatibility; equal to the union sets.
IVS_RAW = ALL_RAW_IVS
IVS_CENTERED = ALL_CENTERED_IVS

# Decomp parquets carry the QtrExp variants; Full method uses extended dir.
DECOMP_IVS_RAW = ["ClarityCEO_QtrExp", "UncResCEO_QtrExp"]

CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO",
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
    "Lagged_DV",  # Unified lagged DV
]

# Binary moderator (Unrated vs Rated reference) per FP 2006 verbatim.
MOD_UNRATED = "Unrated"

# 3 unique HFC interaction terms (Clarity × Unrated DROPPED for both methods —
# trait × constraint mixes competing forces; no clean monotone HFC prediction).
INT_A_UNCRES_UNRATED = "UncResCEO_c_x_Unrated"
INT_B_UNCRES_UNRATED = "UncResCEO_QtrExp_c_x_Unrated"
INT_UNCPRE_UNRATED   = "UncPreCEO_c_x_Unrated"   # shared between Reg A and Reg B
ALL_INTERACTIONS = [INT_A_UNCRES_UNRATED, INT_B_UNCRES_UNRATED, INT_UNCPRE_UNRATED]

# Legacy aliases (existing _save_latex_table / report references).
INT_UNRATED_UNCRES = INT_B_UNCRES_UNRATED  # legacy points to QtrExp variant
INT_UNRATED_UNCPRE = INT_UNCPRE_UNRATED
INT_UNRATED_TERMS = [INT_B_UNCRES_UNRATED, INT_UNCPRE_UNRATED]  # Reg B's pair (legacy)

# 9 display IV rows in LOCKED stacked-pair order (do NOT reorder).
DISPLAY_IVS = [
    "ClarityCEO_c",                    # Row 1 (Reg A uncond, NEG)
    "ClarityCEO_QtrExp_c",             # Row 2 (Reg B uncond, NEG)
    "UncResCEO_c",                     # Row 3 (Reg A uncond, POS)
    "UncResCEO_QtrExp_c",              # Row 4 (Reg B uncond, POS)
    "UncPreCEO_c",                     # Row 5 (Reg A uncond, POS)
    MOD_UNRATED,                       # Row 6 (Reg A int, two-tail)
    INT_A_UNCRES_UNRATED,              # Row 7 (Reg A int, POS)
    INT_B_UNCRES_UNRATED,              # Row 8 (Reg B int, POS)
    INT_UNCPRE_UNRATED,                # Row 9 (Reg A int, POS)
]

IV_TAIL_DIRECTION: Dict[str, str] = {
    "ClarityCEO_c":              "negative",
    "ClarityCEO_QtrExp_c":       "negative",
    "UncResCEO_c":               "positive",
    "UncResCEO_QtrExp_c":        "positive",
    "UncPreCEO_c":               "positive",
    MOD_UNRATED:                 "none",          # two-tailed level dummy
    INT_A_UNCRES_UNRATED:        "positive",
    INT_B_UNCRES_UNRATED:        "positive",
    INT_UNCPRE_UNRATED:          "positive",
}

VARIABLE_LABELS = {
    "ClarityCEO_c":         "CEO Clarity (DWZ Full, c)",
    "ClarityCEO_QtrExp_c":  "CEO Clarity (DWZ Qtr-Exp, c)",
    "UncResCEO_c":          "CEO Residual Unc. (DWZ Full, c)",
    "UncResCEO_QtrExp_c":   "CEO Residual Unc. (DWZ Qtr-Exp, c)",
    "UncPreCEO_c":          "CEO Pres Unc. (c)",
    MOD_UNRATED:            "Unrated",
    INT_A_UNCRES_UNRATED:   r"UncRes (Full) $\times$ Unrated",
    INT_B_UNCRES_UNRATED:   r"UncRes (Qtr-Exp) $\times$ Unrated",
    INT_UNCPRE_UNRATED:     r"UncPre $\times$ Unrated",
}

# Investment-grade rating codes (BBB- and above)
IG_RATINGS = {"AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-"}

MIN_CALLS_PER_FIRM = 5
YEAR_MIN = 2002
YEAR_MAX = 2016

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission.
# Display layout mirrors parent H1.2.ceo2: 16 underlying regressions,
# 8 interaction specs displayed (cols 5-8 + 13-16 renumbered 1-8).
# Top main-IV rows pull from the matching unconditional spec
# (interaction_col - 4); moderator levels + Unrated interactions
# come from the interaction spec.
# ------------------------------------------------------------------
SUITE_ID = "H1.2.ceo2.decomp"
SUITE_DIR_NAME = "h1_2_cash_constraint_ceo2iv_decomp"
SUITE_TITLE = (
    "Financial Constraint-Moderated CEO Speech Uncertainty and Cash Holdings "
    "(CEO 5-IV Dual Stack: DWZ-Faithful Full + Quarterly-Expanding + Pres x Unrated)"
)
SUITE_CAPTION = (
    r"H1.2 CEO 5-IV Dual Stack HFC: ClarityCEO + UncResCEO (DWZ Full + Qtr-Exp) + "
    r"UncPreCEO $\times$ Unrated Constraint"
)
SUITE_LABEL = "tab:h1_2_ceo2_decomp"
SAMPLE_LABEL = (
    "Main sample (excludes financial and utility firms). Fiscal years 2002-2016. "
    "DWZ Eq.5 decomposition: Clarity = -CEO FE; UncRes = call-level residual. "
    "Two methods reported per cell: DWZ-faithful Full + no-look-ahead quarterly-expanding."
)
HYP_DIR = "positive"  # Suite-level Pydantic placeholder; per-IV via IV_TAIL_DIRECTION + spec stitching.
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []

MODEL_SPECS = [
    # Block 1: CashRatio_t
    # Unconditional specs (no interactions): cols 1-4, full FE ladder
    {"col": 1, "dv": "CashRatio",      "fe": "industry",    "extra_controls": [], "interactions": False},
    {"col": 2, "dv": "CashRatio",      "fe": "firm",        "extra_controls": [], "interactions": False},
    {"col": 3, "dv": "CashRatio",      "fe": "industry_yq", "extra_controls": [], "interactions": False},
    {"col": 4, "dv": "CashRatio",      "fe": "firm_yq",     "extra_controls": [], "interactions": False},
    # Interaction specs (IG-reference conditional effect): cols 5-8, full FE ladder
    {"col": 5, "dv": "CashRatio",      "fe": "industry",    "extra_controls": [], "interactions": True},
    {"col": 6, "dv": "CashRatio",      "fe": "firm",        "extra_controls": [], "interactions": True},
    {"col": 7, "dv": "CashRatio",      "fe": "industry_yq", "extra_controls": [], "interactions": True},
    {"col": 8, "dv": "CashRatio",      "fe": "firm_yq",     "extra_controls": [], "interactions": True},
    # Block 2: CashRatio_lead (one-quarter-ahead)
    # Unconditional specs: cols 9-12
    {"col":  9, "dv": "CashRatio_lead", "fe": "industry",    "extra_controls": [], "interactions": False},
    {"col": 10, "dv": "CashRatio_lead", "fe": "firm",        "extra_controls": [], "interactions": False},
    {"col": 11, "dv": "CashRatio_lead", "fe": "industry_yq", "extra_controls": [], "interactions": False},
    {"col": 12, "dv": "CashRatio_lead", "fe": "firm_yq",     "extra_controls": [], "interactions": False},
    # Interaction specs: cols 13-16
    {"col": 13, "dv": "CashRatio_lead", "fe": "industry",    "extra_controls": [], "interactions": True},
    {"col": 14, "dv": "CashRatio_lead", "fe": "firm",        "extra_controls": [], "interactions": True},
    {"col": 15, "dv": "CashRatio_lead", "fe": "industry_yq", "extra_controls": [], "interactions": True},
    {"col": 16, "dv": "CashRatio_lead", "fe": "firm_yq",     "extra_controls": [], "interactions": True},
]

DV_TEX = {
    "CashRatio": r"Cash$_t$",
    "CashRatio_lead": r"Cash$_{t+1}$",
}

SUMMARY_STATS_VARS = [
    {"col": "CashRatio", "label": "Cash Holdings$_t$"},
    {"col": "CashRatio_lead", "label": "Cash Holdings$_{t+1}$"},
    # Dual-stack 5 IVs (Full method + QtrExp variant + shared UncPreCEO)
    {"col": "ClarityCEO", "label": "CEO Clarity (DWZ Full, raw)"},
    {"col": "ClarityCEO_c", "label": "CEO Clarity (DWZ Full, c)"},
    {"col": "ClarityCEO_QtrExp", "label": "CEO Clarity (DWZ Qtr-Exp, raw)"},
    {"col": "ClarityCEO_QtrExp_c", "label": "CEO Clarity (DWZ Qtr-Exp, c)"},
    {"col": "UncResCEO", "label": "CEO UncRes (DWZ Full, raw)"},
    {"col": "UncResCEO_c", "label": "CEO UncRes (DWZ Full, c)"},
    {"col": "UncResCEO_QtrExp", "label": "CEO UncRes (DWZ Qtr-Exp, raw)"},
    {"col": "UncResCEO_QtrExp_c", "label": "CEO UncRes (DWZ Qtr-Exp, c)"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty (raw)"},
    {"col": "UncPreCEO_c", "label": "CEO Pres Uncertainty (c)"},
    {"col": MOD_UNRATED, "label": "Unrated (dummy)"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Capex", "label": "CapEx / Assets"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RDSales", "label": "R\\&D Intensity"},
    {"col": "CashFlowAt", "label": "Cash Flow"},
    {"col": "DailyVola", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H1.2 Financing-Constraint-Moderated Cash Holdings (3-category)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load H1 panel + merge BOTH DWZ-decomp parquets (Full + QtrExp).

    Dual-stack 5-IV design (per H1 pilot):
      - UncPreCEO: H1 panel (raw, single source).
      - ClarityCEO + UncResCEO (DWZ Full method): from ceo_clarity_extended/{latest}/
        ClarityCEO joined on ceo_id (per-CEO constant per DWZ Eq.5);
        UncResCEO joined on file_name (call-level).
      - ClarityCEO_QtrExp + UncResCEO_QtrExp (no-look-ahead variant): from
        ceo_clarity_expanding/{latest}/, both joined on file_name.
    """
    print("\n" + "=" * 60)
    print("Loading H1 panel + merging DWZ decomp parquets (Full + QtrExp)")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h1_cash_holdings",
            required_file="h1_cash_holdings_panel.parquet",
        )
        panel_file = panel_dir / "h1_cash_holdings_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    # H1 panel: DV + controls + UncPreCEO (raw) + ceo_id (needed for Full FE merge).
    columns = [
        "file_name",
        "gvkey", "ceo_id", "year", "fyearq_int", "ff12_code", "start_date",
        "CashRatio", "CashRatio_lag", "CashRatio_lead",
        "UncPreCEO",
        *[c for c in CONTROLS if c != "Lagged_DV"],  # lagged created dynamically
    ]

    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  H1 panel:        {panel_file}")
    print(f"  H1 rows:         {len(panel):,}")

    # ----- Merge 1: DWZ Full residual (UncResCEO) on file_name -----
    full_dir = get_latest_output_dir(
        root_path / "outputs" / "econometric" / "ceo_clarity_extended",
        required_file="ceo_clarity_residual.parquet",
    )
    full_resid_file = full_dir / "ceo_clarity_residual.parquet"
    full_resid = pd.read_parquet(full_resid_file, columns=["file_name", "UncResCEO"])
    print(f"  Full residual:   {full_resid_file}")
    print(f"  Full resid rows: {len(full_resid):,}")
    panel = panel.merge(full_resid, on="file_name", how="left", validate="one_to_one")
    print(f"  After Full UncResCEO merge: {panel['UncResCEO'].notna().sum():,} matched")

    # ----- Merge 2: DWZ Full FE (ClarityCEO) on ceo_id (per-CEO constant) -----
    full_fe_file = full_dir / "ceo_clarity_fe.parquet"
    full_fe = pd.read_parquet(full_fe_file, columns=["ceo_id", "ClarityCEO"])
    print(f"  Full FE:         {full_fe_file}")
    print(f"  Full FE rows:    {len(full_fe):,} CEOs")
    if panel["ceo_id"].dtype != full_fe["ceo_id"].dtype:
        full_fe["ceo_id"] = full_fe["ceo_id"].astype(panel["ceo_id"].dtype)
    panel = panel.merge(full_fe, on="ceo_id", how="left", validate="many_to_one")
    print(f"  After Full ClarityCEO merge: {panel['ClarityCEO'].notna().sum():,} matched")

    # ----- Merge 3: DWZ QtrExp variant (Clarity_QtrExp + UncRes_QtrExp) on file_name -----
    decomp_dir = get_latest_output_dir(
        root_path / "outputs" / "econometric" / "ceo_clarity_expanding",
        required_file="ceo_clarity_qtrexp_residuals.parquet",
    )
    decomp_file = decomp_dir / "ceo_clarity_qtrexp_residuals.parquet"
    decomp = pd.read_parquet(
        decomp_file,
        columns=["file_name", *DECOMP_IVS_RAW],
    )
    print(f"  QtrExp:          {decomp_file}")
    print(f"  QtrExp rows:     {len(decomp):,} "
          f"(non-NaN Clarity_QtrExp: {decomp[DECOMP_IVS_RAW[0]].notna().sum():,})")
    panel = panel.merge(decomp, on="file_name", how="left", validate="one_to_one")
    print(f"  After QtrExp merge: {panel[DECOMP_IVS_RAW[0]].notna().sum():,} matched")

    # Per-IV non-NaN summary (intersection enforced at complete-case stage downstream).
    print("\n  Per-IV non-NaN counts (intersection enforced downstream):")
    for iv in ALL_RAW_IVS:
        n = panel[iv].notna().sum()
        print(f"    {iv:25s}: {n:,} ({100*n/len(panel):.1f}%)")

    # Build calendar year-quarter index AFTER all merges.
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

    return panel, panel_file


def load_and_merge_ratings(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Load S&P credit ratings and merge via merge_asof. Binary Unrated dummy only.

    Binary classification per FP 2006:
        - Any splticrm match (IG or BelowIG) → Unrated=0 (reference: Rated)
        - No splticrm match                  → Unrated=1

    Data: Monthly Compustat Daily Ratings (2000-01 to 2017-02).
    22 rating codes: AAA, AA+, AA, AA-, A+, A, A-, BBB+, BBB, BBB-,
    BB+, BB, BB-, B+, B, B-, CCC+, CCC, CCC-, CC, D, SD.
    """
    print("\n" + "=" * 60)
    print("Merging S&P Credit Ratings (merge_asof, binary Unrated)")
    print("=" * 60)

    ratings_path = root_path / "inputs" / "compustat_daily_ratings" / "compustat_daily_ratings.csv"
    if not ratings_path.exists():
        raise FileNotFoundError(f"Ratings data not found: {ratings_path}")

    ratings = pd.read_csv(
        ratings_path, usecols=["gvkey", "datadate", "splticrm"], low_memory=False,
    )
    print(f"  Loaded ratings: {len(ratings):,} rows")

    # Parse dates, format gvkey to match panel (zero-padded 6-char string)
    ratings["datadate"] = pd.to_datetime(ratings["datadate"])
    ratings["gvkey"] = ratings["gvkey"].astype(str).str.zfill(6)
    ratings = ratings.dropna(subset=["datadate"])
    ratings = ratings.sort_values("datadate").reset_index(drop=True)

    # Ensure panel has datetime start_date for merge_asof
    panel["_start_dt"] = pd.to_datetime(panel["start_date"])
    panel = panel.sort_values("_start_dt").reset_index(drop=True)

    before = len(panel)

    # merge_asof: for each call, find the most recent rating on or before call date
    panel = pd.merge_asof(
        panel,
        ratings[["gvkey", "datadate", "splticrm"]].rename(
            columns={"datadate": "_rating_date"}
        ),
        left_on="_start_dt",
        right_on="_rating_date",
        by="gvkey",
        direction="backward",
    )

    assert len(panel) == before, f"merge_asof changed row count: {before} -> {len(panel)}"

    # Binary classification: Rated (splticrm not null) vs Unrated
    has_rating = panel["splticrm"].notna()
    panel[MOD_UNRATED] = (~has_rating).astype(float)

    # Diagnostics
    n_rated = int(has_rating.sum())
    n_unrated = int(panel[MOD_UNRATED].sum())
    n_total = len(panel)

    print(f"  Rated (reference): {n_rated:,} ({100*n_rated/n_total:.1f}%)")
    print(f"  Unrated:           {n_unrated:,} ({100*n_unrated/n_total:.1f}%)")

    # Clean up temp columns
    panel = panel.drop(columns=["_start_dt", "_rating_date", "splticrm"], errors="ignore")

    return panel


def center_iv(panel: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Mean-center each of the 5 CEO IVs on Main sample (after FF12 filter, before complete-case).

    Centers Reg A (Full): ClarityCEO, UncResCEO, UncPreCEO.
    Centers Reg B (QtrExp): ClarityCEO_QtrExp, UncResCEO_QtrExp.
    UncPreCEO is shared (only one centered version produced).
    """
    print("\n" + "=" * 60)
    print("Centering 5 CEO IVs on Main sample (3 Full + 2 QtrExp; UncPreCEO shared)")
    print("=" * 60)

    main_mask = ~panel["ff12_code"].isin([8, 11])
    iv_means: Dict[str, float] = {}

    for raw, centered in zip(ALL_RAW_IVS, ALL_CENTERED_IVS):
        iv_main = panel.loc[main_mask, raw].dropna()
        mu = float(iv_main.mean())
        panel[centered] = panel[raw] - mu
        iv_means[raw] = mu
        print(f"  {raw:25s}: Main obs={len(iv_main):,}  mean={mu:+.4f}  "
              f"centered mean={panel.loc[main_mask, centered].dropna().mean():+.6f}")

    return panel, iv_means


# ==============================================================================
# Regression
# ==============================================================================


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only (exclude Finance ff12=8, Utility ff12=11)."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any]
) -> pd.DataFrame:
    """Prepare data for one regression spec with two interaction terms."""
    dv = spec["dv"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    # Determine time column based on FE type
    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"

    # Create Lagged_DV: always lag of the base DV (t-1), regardless of t/t+1
    base_dv = dv.replace("_lead", "")
    lag_col = f"{base_dv}_lag"
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    use_interactions = spec.get("interactions", True)

    # Intersection sample: require ALL 5 raw + 5 centered IVs non-NaN (Reg A + Reg B union).
    required = ([dv] + ALL_RAW_IVS + ALL_CENTERED_IVS + [MOD_UNRATED]
                + all_controls + ["gvkey", time_col, "ff12_code"])

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # 3 unique HFC interaction terms (Clarity × Unrated DROPPED for both methods —
    # trait × constraint mixes competing forces; no clean monotone HFC prediction).
    #   Reg A: UncResCEO_c × Unrated
    #   Reg B: UncResCEO_QtrExp_c × Unrated
    #   Shared: UncPreCEO_c × Unrated (Reg A is canonical display source)
    if use_interactions:
        df[INT_A_UNCRES_UNRATED] = df["UncResCEO_c"]            * df[MOD_UNRATED]
        df[INT_B_UNCRES_UNRATED] = df["UncResCEO_QtrExp_c"]     * df[MOD_UNRATED]
        df[INT_UNCPRE_UNRATED]   = df["UncPreCEO_c"]            * df[MOD_UNRATED]

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases on intersection sample (drops Q1 rows with NaN Clarity_QtrExp/UncRes_QtrExp).
    all_required = required + (ALL_INTERACTIONS if use_interactions else [])
    complete_mask = df[all_required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases (5-IV intersection): {len(df):,}")

    # Min calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()

    n_firms = df["gvkey"].nunique()
    n_time_periods = df.groupby(["gvkey", time_col]).ngroups
    n_unrated = int(df[MOD_UNRATED].sum())
    n_rated = int((df[MOD_UNRATED] == 0).sum())
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {n_firms:,} firms, {n_time_periods:,} firm-time-periods")
    print(f"  Binary split: {n_rated:,} Rated ({100*n_rated/len(df):.1f}%) / "
          f"{n_unrated:,} Unrated ({100*n_unrated/len(df):.1f}%)")

    return df


def compute_vif(df: pd.DataFrame, exog_cols: List[str]) -> Dict[str, float]:
    """Compute VIF for each regressor."""
    from numpy.linalg import LinAlgError

    X = df[exog_cols].dropna()
    if len(X) < len(exog_cols) + 1:
        return {}

    X = X.copy()
    X["_const"] = 1.0
    cols_with_const = exog_cols + ["_const"]

    vif_dict = {}
    try:
        X_arr = X[cols_with_const].values.astype(float)
        for i, col in enumerate(exog_cols):
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            vif_dict[col] = variance_inflation_factor(X_arr, i)
    except (LinAlgError, ValueError):
        pass

    return vif_dict


def _extract_coef(model, name: str) -> Tuple[float, float, float]:
    """Extract (beta, se, p_two) for a named coefficient (legacy helper)."""
    beta = float(model.params.get(name, np.nan))
    se = float(model.std_errors.get(name, np.nan))
    p = float(model.pvalues.get(name, np.nan))
    return beta, se, p


def _fit_one(df_panel: pd.DataFrame, dv: str, exog: List[str], base_fe: str) -> Any:
    """Single PanelOLS fit. Industry FE via other_effects; Firm FE via from_formula."""
    if base_fe == "industry":
        model_obj = PanelOLS(
            dependent=df_panel[dv],
            exog=df_panel[exog],
            entity_effects=False,
            time_effects=True,
            other_effects=df_panel["ff12_code"],
            drop_absorbed=True,
            check_rank=False,
        )
        return model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
    else:  # firm
        exog_str = " + ".join(exog)
        formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        return model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)


def _stash_iv_to_meta(meta: Dict[str, Any], model: Any, iv: str) -> None:
    """Extract one IV's beta/SE/t/p_one from a fitted PanelOLS into meta dict.

    p_one direction follows IV_TAIL_DIRECTION map. Two-tailed IVs (Unrated) get
    p_one = p_two. drop_absorbed missing IVs render NaN with a warning.
    """
    if iv not in model.params.index:
        print(f"    {iv}: DROPPED by drop_absorbed — cell will be empty")
        meta[f"{iv}_beta"] = np.nan
        meta[f"{iv}_se"] = np.nan
        meta[f"{iv}_t"] = np.nan
        meta[f"{iv}_p_one"] = np.nan
        return

    beta = float(model.params[iv])
    se = float(model.std_errors[iv])
    p_two = float(model.pvalues[iv])
    t_stat = float(model.tstats[iv])

    if not np.isnan(p_two) and not np.isnan(beta):
        direction = IV_TAIL_DIRECTION.get(iv, "positive")
        if direction == "positive":
            p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
        elif direction == "negative":
            p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
        else:  # "none" → two-tailed (Unrated level)
            p_one = p_two
    else:
        p_one = np.nan

    meta[f"{iv}_beta"] = beta
    meta[f"{iv}_se"] = se
    meta[f"{iv}_t"] = t_stat
    meta[f"{iv}_p_one"] = p_one

    stars = "***" if p_one < 0.01 else ("**" if p_one < 0.05 else ("*" if p_one < 0.10 else ""))
    print(f"    {iv:35s}: beta={beta:+.4f}  SE={se:.4f}  p={p_one:.4f} {stars}")


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any]
) -> Tuple[Any, Any, Dict[str, Any]]:
    """Run TWO PanelOLS regressions per spec (dual-stack 5-IV design).

      Reg A (DWZ-faithful Full):    Cash ~ Clarity_c + UncRes_c + UncPre_c + Unr [+ ints A] + ctrls + FE
      Reg B (No-look-ahead QtrExp): Cash ~ Clarity_QtrExp_c + UncRes_QtrExp_c + UncPre_c + Unr [+ ints B] + ctrls + FE

    Both run on the SAME intersection sample. Display semantics:
      - Clarity_QtrExp + UncRes_QtrExp + INT_B_UNCRES_UNRATED come from Reg B; everything else from Reg A.
      - N + R^2 from Reg A (DWZ-faithful primary anchor).

    Failure handling (mirrors H1 pilot):
      - Reg A fails → return (None, None, {}); col skipped.
      - Reg B fails with Reg A success → render Reg A only; Reg B cells empty.

    Returns (model_a, model_b, meta) or (None, None, {}) on Reg A failure.
    """
    dv = spec["dv"]
    col_num = spec["col"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"
    base_fe = fe.replace("_yq", "")
    fe_label = f"{'Firm' if base_fe == 'firm' else 'Industry(FF12)'} + {'CalYrQtr' if fe.endswith('_yq') else 'CalYear'}"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, None, {}

    use_interactions = spec.get("interactions", True)

    # Build Reg A + Reg B exog stacks
    if use_interactions:
        exog_a = IVS_REG_A_CENTERED + [MOD_UNRATED] + [INT_A_UNCRES_UNRATED, INT_UNCPRE_UNRATED] + all_controls
        exog_b = IVS_REG_B_CENTERED + [MOD_UNRATED] + [INT_B_UNCRES_UNRATED, INT_UNCPRE_UNRATED] + all_controls
    else:
        exog_a = IVS_REG_A_CENTERED + [MOD_UNRATED] + all_controls
        exog_b = IVS_REG_B_CENTERED + [MOD_UNRATED] + all_controls

    n_firms = df_prepared["gvkey"].nunique()
    n_time_periods = df_prepared.groupby(["gvkey", time_col]).ngroups
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, firm-time-periods={n_time_periods:,}")
    if extra_controls:
        print(f"  Extra controls: {extra_controls}")
    print(f"  Reg A exog: {len(exog_a)} vars (3 IVs + Unr + {2 if use_interactions else 0} ints + {len(all_controls)} ctrls)")
    print(f"  Reg B exog: {len(exog_b)} vars (3 IVs + Unr + {2 if use_interactions else 0} ints + {len(all_controls)} ctrls)")

    df_panel = df_prepared.set_index(["gvkey", time_col])

    # ----- Reg A fit -----
    t0 = datetime.now()
    try:
        model_a = _fit_one(df_panel, dv, exog_a, base_fe)
    except Exception as e:
        print(f"  ERROR Reg A: {e}", file=sys.stderr)
        model_a = None
    elapsed_a = (datetime.now() - t0).total_seconds()

    if model_a is None:
        print(f"  [FAIL] Reg A failed; skipping col {col_num}")
        return None, None, {}
    print(f"  Reg A [OK] in {elapsed_a:.1f}s | R^2={model_a.rsquared:.4f} | N={int(model_a.nobs):,}")

    # ----- Reg B fit -----
    t0 = datetime.now()
    try:
        model_b = _fit_one(df_panel, dv, exog_b, base_fe)
    except Exception as e:
        print(f"  ERROR Reg B: {e}", file=sys.stderr)
        model_b = None
    elapsed_b = (datetime.now() - t0).total_seconds()
    if model_b is not None:
        print(f"  Reg B [OK] in {elapsed_b:.1f}s | R^2={model_b.rsquared:.4f} | N={int(model_b.nobs):,}")
    else:
        print(f"  Reg B [FAIL] — QtrExp display cells will be empty in this col")

    # VIF on Reg A's exog (single source for diagnostics)
    vif = compute_vif(df_prepared, exog_a)

    n_unrated = int(df_prepared[MOD_UNRATED].sum())
    n_rated = int((df_prepared[MOD_UNRATED] == 0).sum())

    # Build merged meta with per-IV keys (mirrors H1 pilot pattern: <iv>_beta/_se/_t/_p_one)
    meta: Dict[str, Any] = {
        "col": col_num, "dv": dv, "fe": fe,
        "interactions": use_interactions,
        "n_obs": int(model_a.nobs), "n_firms": n_firms, "n_time_periods": n_time_periods,
        "r2": float(model_a.rsquared),
        "adj_r2": 1 - (1 - model_a.rsquared) * (model_a.nobs - 1) / model_a.df_resid,
        "dv_mean": float(model_a.model.dependent.dataframe.mean().iloc[0]),
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
        "n_rated": n_rated, "n_unrated": n_unrated,
        "sample_years": f"{YEAR_MIN}-{YEAR_MAX}",
    }

    # ---- Reg A IV coefs (Clarity_c, UncRes_c, UncPre_c, Unrated, INT_A_UNCRES, INT_UNCPRE) ----
    print(f"  Reg A coefs:")
    for iv in IVS_REG_A_CENTERED + [MOD_UNRATED]:
        _stash_iv_to_meta(meta, model_a, iv)
    if use_interactions:
        for iv in [INT_A_UNCRES_UNRATED, INT_UNCPRE_UNRATED]:
            _stash_iv_to_meta(meta, model_a, iv)

    # ---- Reg B IV coefs (Clarity_QtrExp_c, UncRes_QtrExp_c, INT_B_UNCRES — display only) ----
    if model_b is not None:
        print(f"  Reg B coefs (_QtrExp display + diagnostics):")
        for iv in ["ClarityCEO_QtrExp_c", "UncResCEO_QtrExp_c"]:
            _stash_iv_to_meta(meta, model_b, iv)
        if use_interactions:
            _stash_iv_to_meta(meta, model_b, INT_B_UNCRES_UNRATED)
        # Reg B's UncPreCEO_c + UncPreCEO_c × Unrated for diagnostics CSV (NOT displayed).
        for iv in ["UncPreCEO_c", INT_UNCPRE_UNRATED]:
            if iv in model_b.params.index:
                meta[f"{iv}_beta_qtrexp"] = float(model_b.params[iv])
                meta[f"{iv}_se_qtrexp"] = float(model_b.std_errors[iv])
            else:
                meta[f"{iv}_beta_qtrexp"] = np.nan
                meta[f"{iv}_se_qtrexp"] = np.nan
        meta["r2_qtrexp"] = float(model_b.rsquared)
        meta["adj_r2_qtrexp"] = 1 - (1 - model_b.rsquared) * (model_b.nobs - 1) / model_b.df_resid
    else:
        for iv in ["ClarityCEO_QtrExp_c", "UncResCEO_QtrExp_c"]:
            meta[f"{iv}_beta"] = np.nan
            meta[f"{iv}_se"] = np.nan
            meta[f"{iv}_t"] = np.nan
            meta[f"{iv}_p_one"] = np.nan
        if use_interactions:
            meta[f"{INT_B_UNCRES_UNRATED}_beta"] = np.nan
            meta[f"{INT_B_UNCRES_UNRATED}_se"] = np.nan
            meta[f"{INT_B_UNCRES_UNRATED}_t"] = np.nan
            meta[f"{INT_B_UNCRES_UNRATED}_p_one"] = np.nan
        meta["UncPreCEO_c_beta_qtrexp"] = np.nan
        meta["UncPreCEO_c_se_qtrexp"] = np.nan
        meta[f"{INT_UNCPRE_UNRATED}_beta_qtrexp"] = np.nan
        meta[f"{INT_UNCPRE_UNRATED}_se_qtrexp"] = np.nan
        meta["r2_qtrexp"] = None
        meta["adj_r2_qtrexp"] = None

    # VIF (Reg A canonical source)
    if vif and use_interactions:
        for t in [INT_A_UNCRES_UNRATED, INT_UNCPRE_UNRATED]:
            meta[f"vif_{t}"] = vif.get(t, np.nan)
        meta[f"vif_{MOD_UNRATED}"] = vif.get(MOD_UNRATED, np.nan)

    # Sanity: warn if any DISPLAY_IV missing/NaN
    for iv in DISPLAY_IVS:
        if not use_interactions and iv in (INT_A_UNCRES_UNRATED, INT_B_UNCRES_UNRATED, INT_UNCPRE_UNRATED):
            continue  # uncond specs legitimately lack interaction terms
        if f"{iv}_beta" not in meta or pd.isna(meta.get(f"{iv}_beta")):
            print(f"  WARN col {col_num}: display IV {iv} missing/NaN")

    return model_a, model_b, meta


def _sig_stars_one(p: float) -> str:
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def _sig_stars_two(p: float) -> str:
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


# ==============================================================================
# Output
# ==============================================================================


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write 8-column LaTeX table: 4 interaction CashRatio_t + 4 interaction CashRatio_lead.

    Dual-stack 5-IV display: 9 rows (5 main + Unrated + 3 interactions). Coefficients
    pulled from interaction-spec metas only (mains are conditional slopes at Unrated=0).
    Iterates DISPLAY_IVS for locked stacked-pair order. Per-IV stars use one-tail
    direction map; Unrated level uses two-tail stars.
    """
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    def fmt_coef(val: float, stars: str) -> str:
        if np.isnan(val): return ""
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        if np.isnan(val): return ""
        return f"({val:.4f})"

    def fmt_r2(val: float) -> str:
        if np.isnan(val): return ""
        if abs(val) < 0.001: return f"{val:.2e}"
        return f"{val:.3f}"

    display_cols = [5, 6, 7, 8, 13, 14, 15, 16]
    metas = [results_by_col.get(c, {}) for c in display_cols]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{" + SUITE_CAPTION + r"}",
        r"\label{" + SUITE_LABEL + r"}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * 8 + "}",
        r"\toprule",
        " & " + " & ".join(f"({i})" for i in range(1, 9)) + r" \\",
        r" & \multicolumn{4}{c}{Cash Holdings$_t$} & \multicolumn{4}{c}{Cash Holdings$_{t+1}$} \\",
        r"\cmidrule(lr){2-5} \cmidrule(lr){6-9}",
        r"\midrule",
    ]

    # 9 IV rows in stacked-pair order (DISPLAY_IVS); per-IV stars by tail direction.
    for iv in DISPLAY_IVS:
        label = VARIABLE_LABELS.get(iv, iv).replace("_", r"\_")
        direction = IV_TAIL_DIRECTION.get(iv, "positive")
        stars_fn = _sig_stars_two if direction == "none" else _sig_stars_one
        parts_b, parts_se = [], []
        for m in metas:
            beta = m.get(f"{iv}_beta", np.nan)
            p_one = m.get(f"{iv}_p_one", np.nan)
            parts_b.append(fmt_coef(beta, stars_fn(p_one)))
            parts_se.append(fmt_se(m.get(f"{iv}_se", np.nan)))
        lines.append(f"{label} & {' & '.join(parts_b)} \\\\")
        lines.append(f" & {' & '.join(parts_se)} \\\\")

    lines.append(r"\midrule")
    lines.append(r"Controls & " + " & ".join(["Ext"] * 8) + r" \\")
    # FE indicator rows
    ind_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").startswith("industry") else ""
                 for c in display_cols]
    firm_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").startswith("firm") else ""
                  for c in display_cols]
    yr_cells = ["Yes" if not results_by_col.get(c, {}).get("fe", "").endswith("_yq") else ""
                for c in display_cols]
    yq_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").endswith("_yq") else ""
                for c in display_cols]
    lines.append(r"Industry FE & " + " & ".join(ind_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_cells) + r" \\")
    lines.append(r"Calendar Year FE & " + " & ".join(yr_cells) + r" \\")
    lines.append(r"Calendar Year-Quarter FE & " + " & ".join(yq_cells) + r" \\")
    lines.append(r"\midrule")

    n_row = " & ".join(f"{m.get('n_obs', 0):,}" for m in metas)
    lines.append(f"N (calls) & {n_row} \\\\")
    r2_row = " & ".join(fmt_r2(m.get("r2", np.nan)) for m in metas)
    lines.append(f"$R^2$ & {r2_row} \\\\")
    ar2_row = " & ".join(fmt_r2(m.get("adj_r2", np.nan)) for m in metas)
    lines.append(f"Adj.~$R^2$ & {ar2_row} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"DWZ Eq.5 decomposition of CEO Q\&A uncertainty into a persistent CEO trait ",
        r"component (\textit{ClarityCEO}) and a within-quarter state component (\textit{UncResCEO}). ",
        r"Two estimation methods reported per cell on the same intersection sample: the ",
        r"\textit{DWZ-faithful Full} method (rows 1, 3, 7) uses a single full-panel Eq.4 regression ",
        r"following DWZ; the \textit{quarterly-expanding} variant (rows 2, 4, 8) uses a recursively-trained ",
        r"Eq.4 to avoid forward-looking contamination. \textit{UncPreCEO} (rows 5, 9) enters both ",
        r"regressions as a third raw IV; coefficient + SE reported from the Full-method (Reg A) ",
        r"specification --- the QtrExp specification's UncPreCEO and UncPreCEO$\times$Unrated ",
        r"coefficients are saved in \texttt{model\_diagnostics.csv} as ",
        r"\texttt{UncPreCEO\_c\_beta\_qtrexp} etc. for reader inspection. ",
        r"\textit{ClarityCEO} $\times$ Unrated NOT estimated for either method: trait $\times$ constraint ",
        r"mixes competing forces (constraint pushes cash UP via HFC priority; high clarity pushes cash DOWN ",
        r"via reduced perception) --- no clean monotone HFC prediction. ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for directional IVs; two-tailed for Unrated level). ",
        r"Per-IV directions: \textit{ClarityCEO} (Full + Qtr-Exp) $\beta < 0$; \textit{UncResCEO} (Full + Qtr-Exp), ",
        r"\textit{UncPreCEO}, and HFC interactions $\beta > 0$; \textit{Unrated} level two-tailed. ",
        r"Moderator is BINARY: Unrated vs Rated reference group (FP 2006; Rated $=$ any S\&P long-term issuer rating). ",
        r"Rating matched via merge\_asof to most recent rating before call date. ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"Main sample (excludes financial and utility firms). ",
        r"Sample restricted to fiscal years 2002--2016 (ratings coverage). ",
        r"$N$ and $R^2$ shown for the DWZ-faithful (Reg A) specification; ",
        r"the quarterly-expanding $R^2$ (\texttt{r2\_qtrexp}) is in \texttt{model\_diagnostics.csv}. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_2_cash_constraint_ceo2iv_decomp_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {tex_path.name}")


def save_outputs(all_results: List[Dict[str, Any]], out_dir: Path) -> pd.DataFrame:
    """Save all outputs."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        col_num = meta["col"]
        has_int = meta.get("interactions", True)
        fname = f"regression_results_col{col_num}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            spec_type = "Interaction" if has_int else "Base"
            f.write(f"H1.2 CEO 2-IV Decomposed Financing-Constraint-Moderated Cash Holdings [{spec_type}]\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"IVs: {', '.join(IVS_RAW)} (DWZ Eq.5 qtr-exp; mean-centered)\n")
            f.write(f"Moderator: Unrated only (binary; FP 2006)\n")
            if has_int:
                f.write(f"Interactions: {', '.join(INT_UNRATED_TERMS)}\n")
                f.write(f"Tail: UncResxUnrated one-tail POS (Clarity×Unrated DROPPED)\n")
            else:
                f.write(f"Interactions: none (base model)\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Sample years: {YEAR_MIN}-{YEAR_MAX}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
            if has_int:
                f.write(f"VIF(int_uncres_unrated): {meta.get('vif_int_uncres_unrated', 'N/A')}\n")
            f.write(f"N: Rated={meta['n_rated']}, Unrated={meta['n_unrated']}\n")
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    _save_latex_table(all_results, out_dir)

    return diag_df


def generate_report(
    all_results: List[Dict[str, Any]], out_dir: Path,
    duration: float, iv_means: Dict[str, float],
) -> None:
    """Generate markdown report for CEO 5-IV dual-stack decomp variant."""
    iv_means_str = ", ".join(f"{k}={v:+.4f}" for k, v in iv_means.items())
    lines = [
        "# H1.2 CEO 5-IV Dual Stack DECOMP Financing-Constraint-Moderated Cash Holdings",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** Two regressions per cell on intersection sample:",
        f"  - **Reg A (DWZ-faithful Full)**: Clarity_c + UncRes_c + UncPre_c + Unr [+ ints A] + ctrls + FE",
        f"  - **Reg B (No-look-ahead QtrExp)**: Clarity_QtrExp_c + UncRes_QtrExp_c + UncPre_c + Unr [+ ints B] + ctrls + FE",
        f"**Display rows (stacked-pair, 9 IVs):**",
        f"  1. ClarityCEO_c (Reg A; NEG)        2. ClarityCEO_QtrExp_c (Reg B; NEG)",
        f"  3. UncResCEO_c (Reg A; POS)         4. UncResCEO_QtrExp_c (Reg B; POS)",
        f"  5. UncPreCEO_c (Reg A; POS — Reg B in CSV)",
        f"  6. Unrated (Reg A; two-tail)",
        f"  7. UncResCEO_c x Unr (Reg A; POS)   8. UncResCEO_QtrExp_c x Unr (Reg B; POS)",
        f"  9. UncPreCEO_c x Unr (Reg A; POS — Reg B in CSV)",
        f"**Per-IV tails:** ClarityCEO (both methods) NEG; UncResCEO (both methods), UncPreCEO, HFC interactions POS; Unrated two-tailed.",
        f"**ClarityCEO x Unrated DROPPED**: trait x constraint mixes competing forces; no clean monotone HFC prediction.",
        f"**Channel:** CH1 — Precautionary liquidity under external-finance frictions",
        f"**IV centering means:** {iv_means_str}",
        f"**Sample years:** {YEAR_MIN}-{YEAR_MAX}",
        "",
        "## Results (interaction-spec coefs; conditional slopes at Unrated=0)",
        "",
        "| Col | DV | Spec | ClarityCEO (Full) | UncResCEO (Full) | INT_A_UNCRES | INT_B_UNCRES | N | R2 (Reg A) |",
        "|-----|----|------|-------------------|------------------|--------------|--------------|---|------------|",
    ]

    for r in all_results:
        m = r.get("meta", {})
        if not m:
            continue
        b_cl = m.get("ClarityCEO_c_beta", np.nan)
        p_cl = m.get("ClarityCEO_c_p_one", np.nan)
        b_un = m.get("UncResCEO_c_beta", np.nan)
        p_un = m.get("UncResCEO_c_p_one", np.nan)
        if m.get("interactions"):
            b_int_a = m.get(f"{INT_A_UNCRES_UNRATED}_beta", np.nan)
            p_int_a = m.get(f"{INT_A_UNCRES_UNRATED}_p_one", np.nan)
            b_int_b = m.get(f"{INT_B_UNCRES_UNRATED}_beta", np.nan)
            p_int_b = m.get(f"{INT_B_UNCRES_UNRATED}_p_one", np.nan)
            int_a_str = f"{b_int_a:+.4f}{_sig_stars_one(p_int_a)} ({p_int_a:.3f})"
            int_b_str = f"{b_int_b:+.4f}{_sig_stars_one(p_int_b)} ({p_int_b:.3f})"
        else:
            int_a_str, int_b_str = "—", "—"
        spec_label = "Int" if m.get("interactions") else "Base"
        s_cl = _sig_stars_one(p_cl) if not np.isnan(p_cl) else ""
        s_un = _sig_stars_one(p_un) if not np.isnan(p_un) else ""
        lines.append(
            f"| ({m['col']}) | {m['dv']} | {spec_label} | "
            f"{b_cl:+.4f}{s_cl} ({p_cl:.3f}) | "
            f"{b_un:+.4f}{s_un} ({p_un:.3f}) | "
            f"{int_a_str} | {int_b_str} | "
            f"{m['n_obs']:,} | {m['r2']:.4f} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- ClarityCEO (Full + QtrExp; NEG): persistent CEO clarity → less precautionary cash (rated firms baseline)",
        "- UncResCEO (Full + QtrExp; POS): within-quarter uncertainty surprise → more cash (rated firms baseline)",
        "- UncPreCEO (Reg A only; POS): presentation-segment uncertainty → more cash",
        "- INT_A/B_UNCRES_UNRATED (POS): HFC amplification at state level for unrated firms (both methods)",
        "- INT_UNCPRE_UNRATED (Reg A only; POS): HFC amplification at presentation level",
        "- Trait × constraint interaction NOT estimated (theoretically ambiguous direction)",
        "- Reference group: Rated (IG ∪ BelowIG) firms; binary moderator per FP 2006",
    ]

    with open(out_dir / "report_step4_H1_2_ceo2iv_decomp.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1_2_ceo2iv_decomp.md")


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H1.2.ceo2.decomp.json from runner state.

    16 underlying regressions:
      - Cols 1-4:  unconditional, DV=CashRatio_t
      - Cols 5-8:  interaction,   DV=CashRatio_t
      - Cols 9-12: unconditional, DV=CashRatio_lead
      - Cols 13-16: interaction,  DV=CashRatio_lead

    Display table = 8 cols: interaction cols 5-8 + 13-16. Main decomp IV slopes
    (ClarityCEO_c, UncResCEO_c) come from matched UNCONDITIONAL spec
    (interaction_col - 4); moderator level + Unrated interactions from
    interaction spec. Per-IV directional p stitched across 3 directions
    (positive/negative/none) per IV_TAIL_DIRECTION.
    """
    results_by_col = {
        r["meta"]["col"]: r for r in all_results if r.get("meta")
    }

    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    display_cols = [5, 6, 7, 8, 13, 14, 15, 16]
    for interaction_col in display_cols:
        if interaction_col not in results_by_col:
            raise RuntimeError(
                f"H1.2.ceo2 spec build: missing interaction result for col {interaction_col}"
            )
        unconditional_col = interaction_col - 4
        if unconditional_col not in results_by_col:
            raise RuntimeError(
                f"H1.2.ceo2 spec build: missing unconditional result for col {unconditional_col}"
            )

        int_entry = results_by_col[interaction_col]
        int_model_a = int_entry["model"]            # Reg A int
        int_model_b = int_entry.get("model_b")      # Reg B int (may be None)
        int_meta = int_entry["meta"]
        uncond_entry = results_by_col[unconditional_col]
        uncond_model_a = uncond_entry["model"]      # Reg A uncond
        uncond_model_b = uncond_entry.get("model_b")  # Reg B uncond (may be None)

        spec = next(s for s in MODEL_SPECS if s["col"] == interaction_col)
        fe = spec["fe"]
        base_fe = fe.replace("_yq", "")
        fe_entity = "industry" if base_fe == "industry" else "firm"
        fe_time = (
            "calendar_year_quarter" if fe.endswith("_yq") else "calendar_year"
        )

        extra_controls = spec.get("extra_controls", [])
        control_vars = list(CONTROLS) + list(extra_controls)

        try:
            dv_mean: Optional[float] = float(
                int_model_a.model.dependent.dataframe.mean().iloc[0]
            )
        except Exception:
            dv_mean = None

        col_metadata.append(
            {
                "col": len(col_metadata) + 1,
                "dv": spec["dv"],
                "fe_entity": fe_entity,
                "fe_time": fe_time,
                "control_vars": control_vars,
                "n_obs": int(int_meta["n_obs"]),
                "n_firms": int(int_meta.get("n_firms", 0)) or None,
                "r2": float(int_meta["r2"]),
                "adj_r2": float(int_meta.get("adj_r2", float("nan"))),
                "dv_mean": dv_mean,
                "cluster_fallback": False,
            }
        )

        # ----- Dual-stack 9-IV coef extraction (4 model sources × per-direction extracts) -----
        merged_coefs: Dict[str, Dict[str, Any]] = {}

        # Reg A uncond: ClarityCEO_c (NEG), UncResCEO_c (POS), UncPreCEO_c (POS)
        for direction in ("positive", "negative"):
            ivs_for_dir = [
                ivc for ivc in IVS_REG_A_CENTERED
                if IV_TAIL_DIRECTION.get(ivc) == direction
            ]
            if not ivs_for_dir:
                continue
            coefs = extract_coefs_panelols(
                model=uncond_model_a,
                key_ivs=ivs_for_dir,
                all_vars=list(IVS_REG_A_CENTERED),
                hyp_dir=direction,
            )
            for ivc in ivs_for_dir:
                if ivc in coefs:
                    merged_coefs[ivc] = coefs[ivc]

        # Reg B uncond: ClarityCEO_QtrExp_c (NEG), UncResCEO_QtrExp_c (POS)
        # all_vars EXCLUDES UncPreCEO_c (Reg A canonical source)
        if uncond_model_b is not None:
            qtrexp_uncond_ivs = ["ClarityCEO_QtrExp_c", "UncResCEO_QtrExp_c"]
            for direction in ("positive", "negative"):
                ivs_for_dir = [
                    ivc for ivc in qtrexp_uncond_ivs
                    if IV_TAIL_DIRECTION.get(ivc) == direction
                ]
                if not ivs_for_dir:
                    continue
                coefs = extract_coefs_panelols(
                    model=uncond_model_b,
                    key_ivs=ivs_for_dir,
                    all_vars=qtrexp_uncond_ivs,
                    hyp_dir=direction,
                )
                for ivc in ivs_for_dir:
                    if ivc in coefs:
                        merged_coefs[ivc] = coefs[ivc]

        # Reg A int: Unrated (none), INT_A_UNCRES_UNRATED (pos), INT_UNCPRE_UNRATED (pos)
        reg_a_int_vars = [MOD_UNRATED, INT_A_UNCRES_UNRATED, INT_UNCPRE_UNRATED]
        for direction in ("positive", "none"):
            ivs_for_dir = [
                v for v in reg_a_int_vars
                if IV_TAIL_DIRECTION.get(v, "none") == direction
            ]
            if not ivs_for_dir:
                continue
            coefs = extract_coefs_panelols(
                model=int_model_a,
                key_ivs=ivs_for_dir,
                all_vars=reg_a_int_vars,
                hyp_dir=direction,
            )
            for v in ivs_for_dir:
                if v in coefs:
                    merged_coefs[v] = coefs[v]

        # Reg B int: INT_B_UNCRES_UNRATED only (UncPreCEO×Unr from Reg A as canonical source)
        if int_model_b is not None:
            coefs_b_int = extract_coefs_panelols(
                model=int_model_b,
                key_ivs=[INT_B_UNCRES_UNRATED],
                all_vars=[INT_B_UNCRES_UNRATED],
                hyp_dir="positive",
            )
            if INT_B_UNCRES_UNRATED in coefs_b_int:
                merged_coefs[INT_B_UNCRES_UNRATED] = coefs_b_int[INT_B_UNCRES_UNRATED]

        # Controls from Reg A int (canonical single source; matches existing pattern)
        control_coefs = extract_coefs_panelols(
            model=int_model_a,
            key_ivs=[],  # treat all as controls → p_one=None
            all_vars=control_vars,
            hyp_dir="none",
        )
        merged_coefs.update(control_coefs)

        # Sanity: warn if any DISPLAY_IV missing (likely drop_absorbed)
        for iv in DISPLAY_IVS:
            if iv not in merged_coefs:
                print(f"  WARN col {interaction_col}: display IV '{iv}' missing from coefs "
                      f"(likely drop_absorbed by FE) — cell will render empty")

        coefs_per_col.append(merged_coefs)

    # Display 9 IVs in LOCKED stacked-pair order (DISPLAY_IVS).
    ivs = [
        {
            "name": iv,
            "label": VARIABLE_LABELS.get(iv, iv).replace("_", r"\_"),
            "tail": ("one_neg" if IV_TAIL_DIRECTION.get(iv) == "negative"
                     else "two"     if IV_TAIL_DIRECTION.get(iv) == "none"
                     else "one_pos"),
        }
        for iv in DISPLAY_IVS
    ]

    # 8 display cols: 4 CashRatio_t + 4 CashRatio_lead
    header_rows = [
        [
            {"label": "CashRatio", "span": 4},
            {"label": r"CashRatio\_lead", "span": 4},
        ]
    ]

    paths = write_suite_spec(
        output_dir=out_dir,
        runner_id=SUITE_DIR_NAME,
        sub_tables=[
            {
                "suite_id": SUITE_ID,
                "dir_name": SUITE_DIR_NAME,
                "title": SUITE_TITLE,
                "caption": SUITE_CAPTION,
                "label": SUITE_LABEL,
                "col_range": list(range(1, len(col_metadata) + 1)),
                "header_rows": header_rows,
                "suite_type": "moderation",
            }
        ],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=SAMPLE_LABEL,
        clustering=CLUSTERING,
        tail=TAIL,
        ivs=ivs,
        controls={
            "base": list(CONTROLS),
            "extended_only": list(EXTENDED_ONLY_CONTROLS),
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_2_CashConstraint_ceo2iv_decomp",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H1.2 CEO 2-IV DECOMP Financing-Constraint-Moderated Cash Holdings")
    print("=" * 80)
    print(f"Timestamp:  {timestamp}")
    print(f"Output:     {out_dir}")
    print(f"Design:     2 decomp IVs × 2 DVs × (base + interaction) × 4 FE types = 16 models (8 displayed)")
    print(f"Channel:    CH1 — Precautionary liquidity under external-finance frictions")
    print(f"Moderator:  Binary Unrated vs Rated (FP 2006)")
    print(f"IVs:        {', '.join(IVS_RAW)}  (DWZ Eq.5 qtr-expanding)")
    print(f"Tails:      Clarity NEG / UncRes POS / UncRes×Unrated POS  (Clarity×Unrated DROPPED as theoretically ambiguous)")
    print(f"Sample:     {YEAR_MIN}-{YEAR_MAX}")

    # Load panel + merge decomp parquet
    panel, panel_file = load_panel(root, panel_path)

    # Merge S&P credit ratings via merge_asof (binary Unrated only)
    panel = load_and_merge_ratings(panel, root)

    # Filter to sample years
    before_year = len(panel)
    panel = panel[panel["fyearq_int"].between(YEAR_MIN, YEAR_MAX)].copy()
    print(f"\n  Year filter ({YEAR_MIN}-{YEAR_MAX}): {len(panel):,} / {before_year:,} "
          f"(dropped {before_year - len(panel):,})")

    # Center both decomp IVs on Main sample
    panel, iv_means = center_iv(panel)

    # Filter to Main sample
    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    n_unrated = int(panel[MOD_UNRATED].sum())
    n_rated = int((panel[MOD_UNRATED] == 0).sum())

    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    print(f"  Binary (Main): {n_rated:,} Rated ({100*n_rated/main_n:.1f}%) / "
          f"{n_unrated:,} Unrated ({100*n_unrated/main_n:.1f}%)")

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H1.2 CEO 2-IV Decomp Cash Holdings (Main Sample, 2002--2016)",
        label="tab:summary_stats_h1_2_ceo2_decomp",
    )
    print("  Saved: summary_stats.csv/.tex")

    # Run 2 regressions
    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} ---")
        try:
            df_prep = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue
        if len(df_prep) < 100:
            print(f"  Skipping: too few obs")
            continue

        model_a, model_b, meta = run_regression(df_prep, spec)
        if model_a is not None and meta:
            all_results.append({"model": model_a, "model_b": model_b, "meta": meta})

    # Save outputs
    diag_df = save_outputs(all_results, out_dir)
    _write_suite_spec_json(all_results, out_dir)

    # Attrition
    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel (H1)", full_n + (before_year - len(panel.index))),
            (f"Year filter ({YEAR_MIN}-{YEAR_MAX})", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("Rated firms (reference)", n_rated),
            ("Unrated firms", n_unrated),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(
            attrition_stages, out_dir,
            "H1.2 CEO 2-IV DECOMP Financing-Constraint-Moderated Cash Holdings",
        )
        print("  Saved: sample_attrition.csv/.tex")

    # Manifest
    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={
            "panel": panel_file,
            "ratings": root / "inputs" / "compustat_daily_ratings" / "compustat_daily_ratings.csv",
        },
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, out_dir, duration, iv_means)

    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    # Per-IV sig summary across 16 specs (8 interaction + 8 unconditional)
    print("\nPer-IV significance summary (one-tail directional, p<0.05; β must match direction):")
    interaction_metas = [r["meta"] for r in all_results if r["meta"].get("interactions")]
    uncond_metas = [r["meta"] for r in all_results if not r["meta"].get("interactions")]

    def _count_sig(metas: list, iv: str) -> int:
        direction = IV_TAIL_DIRECTION.get(iv, "positive")
        count = 0
        for m in metas:
            beta = m.get(f"{iv}_beta")
            p_one = m.get(f"{iv}_p_one")
            if beta is None or p_one is None or pd.isna(beta) or pd.isna(p_one):
                continue
            if direction == "positive" and beta > 0 and p_one < 0.05:
                count += 1
            elif direction == "negative" and beta < 0 and p_one < 0.05:
                count += 1
            elif direction == "none" and p_one < 0.05:
                count += 1
        return count

    # Main IVs: from BOTH uncond + int specs (mains exist in both, slightly different coefs)
    print("  Main IVs (across all 16 spec×reg fits):")
    for iv in DISPLAY_IVS[:5] + [MOD_UNRATED]:
        sig_uncond = _count_sig(uncond_metas, iv)
        sig_int = _count_sig(interaction_metas, iv)
        direction = IV_TAIL_DIRECTION.get(iv, "positive")
        sign_str = ">" if direction == "positive" else ("<" if direction == "negative" else "≠")
        print(f"    {iv:35s} (β {sign_str} 0): "
              f"uncond {sig_uncond}/{len(uncond_metas)} | int {sig_int}/{len(interaction_metas)}")

    # Interactions: int specs only
    print("  Interaction IVs (int specs only):")
    for iv in [INT_A_UNCRES_UNRATED, INT_B_UNCRES_UNRATED, INT_UNCPRE_UNRATED]:
        sig_int = _count_sig(interaction_metas, iv)
        print(f"    {iv:35s} (β > 0): {sig_int}/{len(interaction_metas)} sig")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IVs: {', '.join(IVS_RAW)}")
        print(f"  Centered: {', '.join(IVS_CENTERED)}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print(f"  Controls: {len(CONTROLS)}")
        print(f"  Moderator: {MOD_UNRATED} (binary)")
        print(f"  Interactions: {', '.join(INT_UNRATED_TERMS)}")
        print(f"  IV_TAIL_DIRECTION: {IV_TAIL_DIRECTION}")
        print(f"  Sample years: {YEAR_MIN}-{YEAR_MAX}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
