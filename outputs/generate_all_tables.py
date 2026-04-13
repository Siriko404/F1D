#!/usr/bin/env python3
"""Generate complete LaTeX tables for all hypothesis suites from regression .txt files.

Each table includes:
- Explicit DV column headers
- All 4 IVs with coefficients + SEs
- All control variables with coefficients + SEs
- Significant coefficients in bold
- FE indicators, N, Within-R²
"""

import re
import subprocess
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent / "econometric"


def resolve_suite_dir(dir_value: str) -> Path:
    """Resolve a suite dir entry to the latest valid run on disk.

    Format:
      - "suite_name"                  → auto-pick latest timestamped subdir
      - "suite_name/timestamp"        → timestamp is ignored; auto-latest
      - "suite_name/:pin:<timestamp>" → force that exact run (escape hatch)

    A run is "valid" if it contains at least one regression_results_col*.txt
    or a *_table.tex (for prebuilt/moderation suites). Dirs starting with "_"
    (e.g. _archived) are skipped.
    """
    parts = dir_value.split("/", 1)
    suite_name = parts[0]
    suite_root = BASE / suite_name

    if len(parts) == 2 and parts[1].startswith(":pin:"):
        pinned = suite_root / parts[1][len(":pin:"):]
        if not pinned.exists():
            raise FileNotFoundError(f"Pinned run not found: {pinned}")
        return pinned

    if not suite_root.exists():
        return BASE / dir_value  # let downstream .exists() checks fail naturally

    candidates = []
    for p in suite_root.iterdir():
        if not p.is_dir() or p.name.startswith("_"):
            continue
        has_results = any(p.glob("regression_results_col*.txt")) or any(p.glob("*_table.tex"))
        if has_results:
            candidates.append(p)
    if not candidates:
        return BASE / dir_value
    return max(candidates, key=lambda p: p.name)


def _load_dv_means(suite_dir, col_offset=0):
    """Load DV means from model_diagnostics.csv (regression-sample means)."""
    diag_path = suite_dir / "model_diagnostics.csv"
    if not diag_path.exists():
        return {}
    df = pd.read_csv(diag_path)
    if "dv_mean" not in df.columns:
        return {}
    means = {}
    for _, row in df.iterrows():
        dv = row["dv"]
        if dv not in means:
            means[dv] = row["dv_mean"]
    return means

SUITES = [
    # ── H1 family ──
    {
        "id": "H1",
        "dir": "h1_cash_holdings",
        "caption": "H1: Speech Uncertainty and Cash Holdings",
        "label": "tab:h1",
        "cols": 12,
        "dvs": [
            ("CashRatio", 6),
            (r"CashRatio\_lead", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    {
        "id": "H1.1",
        "type": "moderation",
        "dir": "h1_1_cash_tsimm",
        "caption": "H1.1: Product Similarity--Moderated Speech Uncertainty and Cash Holdings",
        "label": "tab:h1_1",
        "cols": 4,
        "dvs": [
            ("CashRatio", 4),
        ],
        "key_vars": [
            "Manager_QA_Unc_c",
            "z_log_TotalSimilarity",
            "MgrQAUnc_x_zlogTSIMM",
        ],
        "key_labels": [
            r"Manager\_QA\_Unc\_c",
            r"z\_log\_TotalSimilarity",
            r"MgrQAUnc\_x\_zlogTSIMM",
        ],
        "key_tails": ["one_pos", "two", "two"],
        "lagged_dv_var": "Lagged_DV",
        "lagged_dv_label": r"Lagged\_DV",
    },
    {
        "id": "H1.1b",
        "type": "moderation",
        "dir": "h1_1b_cash_tsimm_binary",
        "caption": "H1.1b: Binary Product Similarity--Moderated Speech Uncertainty and Cash Holdings",
        "label": "tab:h1_1b",
        "cols": 4,
        "dvs": [
            ("CashRatio", 4),
        ],
        "key_vars": [
            "Manager_QA_Unc_c",
            "HighTSIMM",
            "MgrQAUnc_x_HighTSIMM",
        ],
        "key_labels": [
            r"Manager\_QA\_Unc\_c",
            "HighTSIMM",
            r"MgrQAUnc\_x\_HighTSIMM",
        ],
        "key_tails": ["one_pos", "two", "two"],
        "lagged_dv_var": "Lagged_DV",
        "lagged_dv_label": r"Lagged\_DV",
    },
    {
        "id": "H1.2",
        "type": "moderation",
        "dir": "h1_2_cash_constraint",
        "caption": "H1.2: Financial Constraint--Moderated Speech Uncertainty and Cash Holdings (Three-Category)",
        "label": "tab:h1_2",
        "cols": 4,
        "col_files": {
            1: "regression_results_col5.txt",
            2: "regression_results_col6.txt",
            3: "regression_results_col7.txt",
            4: "regression_results_col8.txt",
        },
        "dvs": [
            ("CashRatio", 4),
        ],
        "base_iv": {
            "files": {
                1: "regression_results_col1.txt",
                2: "regression_results_col2.txt",
                3: "regression_results_col3.txt",
                4: "regression_results_col4.txt",
            },
            "var": "Manager_QA_Unc_c",
            "label": r"Manager\_QA\_Unc\_c",
            "tail": "one_pos",
        },
        "key_vars": [
            "MgrQAUnc_x_IG",
            "BelowIG",
            "Unrated",
            "MgrQAUnc_x_BelowIG",
            "MgrQAUnc_x_Unrated",
        ],
        "key_labels": [
            r"MgrQAUnc\_x\_IG",
            "BelowIG",
            "Unrated",
            r"MgrQAUnc\_x\_BelowIG",
            r"MgrQAUnc\_x\_Unrated",
        ],
        "key_tails": ["one_pos", "two", "two", "two", "two"],
        "lagged_dv_var": "Lagged_DV",
        "lagged_dv_label": r"Lagged\_DV",
    },
    # ── H4 family ──
    {
        "id": "H4a",
        "dir": "h4_leverage",
        "caption": "H4a: Speech Uncertainty and Book Leverage",
        "label": "tab:h4a",
        "cols": 12,
        "dvs": [
            ("Leverage", 6),
            (r"Leverage\_lead", 6),
        ],
        "tail": "two",
        "hyp_dir": None,
    },
    {
        "id": "H4b",
        "dir": "h4_leverage",
        "caption": "H4b: Speech Uncertainty and Debt-to-Capital",
        "label": "tab:h4b",
        "cols": 12,
        "col_offset": 12,
        "dvs": [
            ("DebtToCapital", 6),
            (r"DebtToCapital\_lead", 6),
        ],
        "tail": "two",
        "hyp_dir": None,
    },
    # ── H5 (Wang 2020) ──
    {
        "id": "H5",
        "dir": "h5b_wang_disp",
        "caption": "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)",
        "label": "tab:h5",
        "cols": 12,
        "dvs": [
            ("DISP", 6),
            (r"DISP\_lead", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H7 (12-col 2-DV: contemp + t+1 lead, 2026-04-17 upgrade) ──
    {
        "id": "H7",
        "dir": "h7_illiquidity",
        "caption": "H7: Speech Uncertainty and 3-Day Post-Call Illiquidity Change ($\\Delta$Amihud, $[+1,+3]-[-3,-1]$)",
        "label": "tab:h7",
        "cols": 12,
        "dvs": [
            (r"DeltaILLIQ", 6),
            (r"DeltaILLIQ\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H7b (12-col 2-DV) ──
    {
        "id": "H7b",
        "dir": "h7b_amihud_level",
        "caption": "H7b: Speech Uncertainty and 3-Day Post-Call Amihud Illiquidity Level ($[+1,+3]$)",
        "label": "tab:h7b",
        "cols": 12,
        "dvs": [
            (r"PostCallAmihud", 6),
            (r"PostCallAmihud\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H7c (NEW: BGT 2018 25-day post-call Amihud LEVEL) ──
    {
        "id": "H7c",
        "dir": "h7c_amihud_bgt_level",
        "caption": "H7c: Speech Uncertainty and BGT (2018) 25-Day Post-Call Amihud Level ($[0,+25]$, day 0 included)",
        "label": "tab:h7c",
        "cols": 12,
        "dvs": [
            (r"BGTLevel\_Amihud", 6),
            (r"BGTLevel\_Amihud\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H7d (NEW: BGT-Window Amihud DELTA) ──
    {
        "id": "H7d",
        "dir": "h7d_amihud_bgt_delta",
        "caption": "H7d: Speech Uncertainty and BGT-Window 25-Day Amihud Delta ($[+1,+25]-[-25,-1]$)",
        "label": "tab:h7d",
        "cols": 12,
        "dvs": [
            (r"BGTDelta\_Amihud", 6),
            (r"BGTDelta\_Amihud\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H7e (NEW: BGT-Window Amihud AVERAGE) ──
    {
        "id": "H7e",
        "dir": "h7e_amihud_bgt_avg",
        "caption": "H7e: Speech Uncertainty and BGT-Window 25-Day Amihud Average ($[-25,+25]$, 51-day symmetric)",
        "label": "tab:h7e",
        "cols": 12,
        "dvs": [
            (r"BGTAvg\_Amihud", 6),
            (r"BGTAvg\_Amihud\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H11 family ──
    {
        "id": "H11",
        "type": "moderation",
        "dir": "h11_prisk_uncertainty",
        "caption": "H11: Political Risk and Language Uncertainty",
        "label": "tab:h11",
        "cols": 8,
        "col_files": {
            1: "regression_results_Main_UncAnsMgr_industry.txt",
            2: "regression_results_Main_UncAnsCEO_industry.txt",
            3: "regression_results_Main_UncPreMgr_industry.txt",
            4: "regression_results_Main_UncPreCEO_industry.txt",
            5: "regression_results_Main_UncAnsMgr_firm.txt",
            6: "regression_results_Main_UncAnsCEO_firm.txt",
            7: "regression_results_Main_UncPreMgr_firm.txt",
            8: "regression_results_Main_UncPreCEO_firm.txt",
        },
        "dvs": [
            (r"Industry FE", 4),
            (r"Firm FE", 4),
        ],
        "col_dv_labels": [
            "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
            "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
        ],
        "key_vars": ["PRisk"],
        "key_labels": ["PRisk"],
        "key_tails": ["one_pos"],
    },
    {
        "id": "H11-Lag1",
        "type": "moderation",
        "dir": "h11_prisk_uncertainty_lag",
        "caption": "H11-Lag1: Political Risk (1-Qtr Lag) and Language Uncertainty",
        "label": "tab:h11_lag1",
        "cols": 8,
        "col_files": {
            1: "regression_results_Main_UncAnsMgr_lag1_industry.txt",
            2: "regression_results_Main_UncAnsCEO_lag1_industry.txt",
            3: "regression_results_Main_UncPreMgr_lag1_industry.txt",
            4: "regression_results_Main_UncPreCEO_lag1_industry.txt",
            5: "regression_results_Main_UncAnsMgr_lag1_firm.txt",
            6: "regression_results_Main_UncAnsCEO_lag1_firm.txt",
            7: "regression_results_Main_UncPreMgr_lag1_firm.txt",
            8: "regression_results_Main_UncPreCEO_lag1_firm.txt",
        },
        "dvs": [
            (r"Industry FE", 4),
            (r"Firm FE", 4),
        ],
        "col_dv_labels": [
            "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
            "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
        ],
        "key_vars": ["PRisk_lag"],
        "key_labels": [r"PRisk$_{t-1}$"],
        "key_tails": ["one_pos"],
    },
    {
        "id": "H11-Lag2",
        "type": "moderation",
        "dir": "h11_prisk_uncertainty_lag",
        "caption": "H11-Lag2: Political Risk (2-Qtr Lag) and Language Uncertainty",
        "label": "tab:h11_lag2",
        "cols": 8,
        "col_files": {
            1: "regression_results_Main_UncAnsMgr_lag2_industry.txt",
            2: "regression_results_Main_UncAnsCEO_lag2_industry.txt",
            3: "regression_results_Main_UncPreMgr_lag2_industry.txt",
            4: "regression_results_Main_UncPreCEO_lag2_industry.txt",
            5: "regression_results_Main_UncAnsMgr_lag2_firm.txt",
            6: "regression_results_Main_UncAnsCEO_lag2_firm.txt",
            7: "regression_results_Main_UncPreMgr_lag2_firm.txt",
            8: "regression_results_Main_UncPreCEO_lag2_firm.txt",
        },
        "dvs": [
            (r"Industry FE", 4),
            (r"Firm FE", 4),
        ],
        "col_dv_labels": [
            "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
            "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
        ],
        "key_vars": ["PRisk_lag2"],
        "key_labels": [r"PRisk$_{t-2}$"],
        "key_tails": ["one_pos"],
    },
    # ── H12 ──
    {
        "id": "H12",
        "dir": "h12_payout",
        "caption": "H12: Speech Uncertainty and Quarterly Payout Ratio",
        "label": "tab:h12",
        "cols": 12,
        "dvs": [
            (r"PayoutRatio\_q", 6),
            (r"PayoutRatio\_q\_lead\_qtr", 6),
        ],
        "tail": "one",
        "hyp_dir": "<",
        "time_fe_label": "Year FE",
    },
    # ── H12b ── (dividend payer binary — Hoberg-Prabhala 2009 ex-date analog)
    {
        "id": "H12b",
        "dir": "h12b_dividend_payer",
        "caption": "H12b: Speech Uncertainty and Dividend Payer Indicator (Hoberg-Prabhala 2009 analog)",
        "label": "tab:h12b",
        "cols": 12,
        "dvs": [
            (r"DivPayerQ", 6),
            (r"DivPayerQ\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": "<",
        "time_fe_label": "Year FE",
    },
    # ── H13 family ──
    {
        "id": "H13",
        "dir": "h13_capex",
        "caption": "H13: Speech Uncertainty and Capital Expenditure",
        "label": "tab:h13",
        "cols": 12,
        "dvs": [
            ("Capex", 6),
            (r"Capex\_lead", 6),
        ],
        "tail": "two",
        "hyp_dir": None,
    },
    {
        "id": "H13.1",
        "type": "moderation",
        "dir": "h13_1_competition",
        "caption": "H13.1: Product Similarity--Moderated Speech Uncertainty and Capital Expenditure",
        "label": "tab:h13_1",
        "cols": 8,
        "col_files": {
            1: "regression_results_col1_Capex_tsimm.txt",
            2: "regression_results_col2_Capex_tsimm.txt",
            3: "regression_results_col3_Capex_tsimm.txt",
            4: "regression_results_col4_Capex_tsimm.txt",
            5: "regression_results_col5_Capex_lead_tsimm.txt",
            6: "regression_results_col6_Capex_lead_tsimm.txt",
            7: "regression_results_col7_Capex_lead_tsimm.txt",
            8: "regression_results_col8_Capex_lead_tsimm.txt",
        },
        "dvs": [
            ("Capex", 4),
            (r"Capex\_lead", 4),
        ],
        "lagged_dv_var": "Lagged_DV",
        "lagged_dv_label": r"Lagged\_DV",
        "key_vars": [
            "Manager_QA_Unc_c",
            "z_log_TotalSimilarity",
            "MgrQAUnc_x_zlogTSIMM",
        ],
        "key_labels": [
            r"Manager\_QA\_Unc\_c",
            r"z\_log\_TotalSimilarity",
            r"MgrQAUnc\_x\_zlogTSIMM",
        ],
        "key_tails": ["two", "two", "two"],
    },
    # ── H13.2 ──
    {
        "id": "H13.2",
        "dir": "h13_2_capex_leads",
        "caption": "H13.2: Speech Uncertainty and Capital Expenditure --- Lead Horizons",
        "label": "tab:h13_2",
        "cols": 16,
        "dvs": [
            (r"Capex\_lead", 4),
            (r"Capex\_lead2", 4),
            (r"Capex\_lead3", 4),
            (r"Capex\_lead4", 4),
        ],
        "tail": "two",
        "hyp_dir": None,
    },
    # ── H14 (12-col 2-DV: contemp + t+1 lead, 2026-04-17 upgrade) ──
    {
        "id": "H14",
        "dir": "h14_bidask_spread",
        "caption": "H14: Speech Uncertainty and Lee (2016) 3-Day Bid-Ask Spread Change ($\\Delta$DSPREAD, $[+1,+3]-[-3,-1]$)",
        "label": "tab:h14",
        "cols": 12,
        "dvs": [
            ("DSPREAD", 6),
            (r"DSPREAD\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H14b (12-col 2-DV) ──
    {
        "id": "H14b",
        "dir": "h14b_spread_level",
        "caption": "H14b: Speech Uncertainty and Lee (2016) 3-Day Post-Call Bid-Ask Spread Level ($[+1,+3]$)",
        "label": "tab:h14b",
        "cols": 12,
        "dvs": [
            (r"PostCallSpread", 6),
            (r"PostCallSpread\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H14c (NEW: BGT-Window 25-Day Closing-Quote Spread LEVEL) ──
    {
        "id": "H14c",
        "dir": "h14c_spread_bgt_level",
        "caption": "H14c: Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Level ($[0,+25]$, day 0 included)",
        "label": "tab:h14c",
        "cols": 12,
        "dvs": [
            (r"BGTLevel\_Spread", 6),
            (r"BGTLevel\_Spread\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H14d (NEW: BGT-Window Spread DELTA) ──
    {
        "id": "H14d",
        "dir": "h14d_spread_bgt_delta",
        "caption": "H14d: Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Delta ($[+1,+25]-[-25,-1]$)",
        "label": "tab:h14d",
        "cols": 12,
        "dvs": [
            (r"BGTDelta\_Spread", 6),
            (r"BGTDelta\_Spread\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H14e (NEW: BGT-Window Spread AVERAGE) ──
    {
        "id": "H14e",
        "dir": "h14e_spread_bgt_avg",
        "caption": "H14e: Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Average ($[-25,+25]$, 51-day symmetric)",
        "label": "tab:h14e",
        "cols": 12,
        "dvs": [
            (r"BGTAvg\_Spread", 6),
            (r"BGTAvg\_Spread\_lead1", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H16 ──
    {
        "id": "H16",
        "dir": "h16_rd_sales",
        "caption": r"H16: Speech Uncertainty and R\&D Investment Intensity",
        "label": "tab:h16",
        "cols": 12,
        "dvs": [
            ("RDSales", 6),
            (r"RDSales\_lead", 6),
        ],
        "tail": "two",
        "hyp_dir": None,
    },
    # ── H17 ──
    {
        "id": "H17",
        "dir": "h17_repurchase_intensity",
        "caption": "H17: Speech Uncertainty and Repurchase Intensity",
        "label": "tab:h17",
        "cols": 12,
        "dvs": [
            ("RepurchaseIntensity", 6),
            (r"RepurchaseIntensity\_lead\_qtr", 6),
        ],
        "tail": "two",
        "hyp_dir": None,
    },
    # ── H18 ──
    {
        "id": "H18",
        "dir": "h18_cccl_received",
        "caption": "H18: Speech Uncertainty and SEC Comment Letters",
        "label": "tab:h18",
        "cols": 6,
        "dvs": [
            (r"CCCL", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H18b (Logit robustness) ──
    {
        "id": "H18b",
        "dir": "h18b_cccl_logit",
        "caption": "H18b: Logit Robustness --- Speech Uncertainty and SEC Comment Letters",
        "label": "tab:h18b",
        "cols": 2,
        "dvs": [
            (r"CCCL", 2),
        ],
        "tail": "one",
        "hyp_dir": ">",
        "r2_label": r"Pseudo~$R^2$",
        "skip_adj_r2": True,
    },
    # ── H19b (Chang et al. 2006 robustness) ──
    {
        "id": "H19b",
        "dir": "h19b_external_funding",
        "caption": r"H19b: Speech Uncertainty and External vs Internal Financing (Chang et al. 2006)",
        "label": "tab:h19b",
        "cols": 12,
        "dvs": [
            ("ChangExternalFunding", 6),
            (r"ChangExternalFunding\_lead", 6),
        ],
        "tail": "one",
        "hyp_dir": "<",
    },
    # ── H20b (Chang et al. 2006 robustness) ──
    {
        "id": "H20b",
        "dir": "h20b_debt_choice",
        "caption": r"H20b: Speech Uncertainty and Debt vs Equity Choice (Chang et al. 2006)",
        "label": "tab:h20b",
        "cols": 12,
        "dvs": [
            ("ChangDebtChoice", 6),
            (r"ChangDebtChoice\_lead", 6),
        ],
        "tail": "two",
        "hyp_dir": None,
    },
    # ── H21 ──
    {
        "id": "H21",
        "dir": "h21_sec_letters",
        "caption": "H21: Speech Uncertainty and SEC Comment Letter Count",
        "label": "tab:h21",
        "cols": 6,
        "dvs": [
            (r"SEC\_Letters\_fwd", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H22 ──
    {
        "id": "H22",
        "dir": "h22_equity_constraints",
        "caption": "H22: Speech Uncertainty and Equity Financing Constraints",
        "label": "tab:h22",
        "cols": 4,
        "dvs": [
            (r"EquityDelayCon\_lead", 4),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
    # ── H23 ──
    {
        "id": "H23",
        "type": "moderation",
        "dir": "h23_competition_uncertainty",
        "caption": "H23: Product-Market Competition and Uncertainty Language",
        "label": "tab:h23",
        "cols": 8,
        "col_files": {
            1: "regression_results_col1.txt",
            2: "regression_results_col2.txt",
            3: "regression_results_col3.txt",
            4: "regression_results_col4.txt",
            5: "regression_results_col5.txt",
            6: "regression_results_col6.txt",
            7: "regression_results_col7.txt",
            8: "regression_results_col8.txt",
        },
        "dvs": [
            (r"QA\_Uncertainty", 2),
            (r"Pres\_Uncertainty", 2),
            (r"QA\_Uncertainty", 2),
            (r"Pres\_Uncertainty", 2),
        ],
        "col_dv_labels": [
            "Manager", "CEO", "Manager", "CEO",
            "Manager", "CEO", "Manager", "CEO",
        ],
        "key_vars": ["z_log_TotalSimilarity"],
        "key_labels": [r"$z(\log(\mathrm{TSIMM}))$"],
        "key_tails": ["two"],
        "fe_rows": [
            ("Industry FE", ["Yes", "Yes", "Yes", "Yes", "", "", "", ""]),
            ("Firm FE", ["", "", "", "", "Yes", "Yes", "Yes", "Yes"]),
            ("Year FE", ["Yes", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes"]),
        ],
        "time_fe_label": "Year FE",
    },
    # ── H24 / H24b / H25 Macro Uncertainty Suites ──
    # Reverse-direction suites: aggregate monthly macro uncertainty (EPU / GEPU / GPR)
    # predicts call-level language uncertainty. 8 cols = 4 DVs × 2 FE types
    # (Industry FE cols 1-4, Firm FE cols 5-8), ALL with Calendar Year FE.
    # Year-Quarter FE NOT used (would absorb the macro IV). Two-way clustered
    # SEs (firm, cal_yr_qtr). Auto FE detection from runner output.
    {
        "id": "H24",
        "type": "moderation",
        "dir": "h24_us_epu",
        "caption": "H24: US Economic Policy Uncertainty and Call Language Uncertainty",
        "label": "tab:h24",
        "cols": 8,
        "col_files": {
            1: "regression_results_col1.txt",
            2: "regression_results_col2.txt",
            3: "regression_results_col3.txt",
            4: "regression_results_col4.txt",
            5: "regression_results_col5.txt",
            6: "regression_results_col6.txt",
            7: "regression_results_col7.txt",
            8: "regression_results_col8.txt",
        },
        "dvs": [
            (r"Industry + Cal.~Year FE", 4),
            (r"Firm + Cal.~Year FE", 4),
        ],
        "col_dv_labels": [
            "Mgr QA", "Mgr Pres", "CEO QA", "CEO Pres",
            "Mgr QA", "Mgr Pres", "CEO QA", "CEO Pres",
        ],
        "key_vars": ["US_EPU_log"],
        "key_labels": [r"$\log(\mathrm{US\ EPU})_{t}$"],
        "key_tails": ["one_pos"],
    },
    {
        "id": "H24b",
        "type": "moderation",
        "dir": "h24b_global_epu",
        "caption": "H24b: Global Economic Policy Uncertainty and Call Language Uncertainty",
        "label": "tab:h24b",
        "cols": 8,
        "col_files": {
            1: "regression_results_col1.txt",
            2: "regression_results_col2.txt",
            3: "regression_results_col3.txt",
            4: "regression_results_col4.txt",
            5: "regression_results_col5.txt",
            6: "regression_results_col6.txt",
            7: "regression_results_col7.txt",
            8: "regression_results_col8.txt",
        },
        "dvs": [
            (r"Industry + Cal.~Year FE", 4),
            (r"Firm + Cal.~Year FE", 4),
        ],
        "col_dv_labels": [
            "Mgr QA", "Mgr Pres", "CEO QA", "CEO Pres",
            "Mgr QA", "Mgr Pres", "CEO QA", "CEO Pres",
        ],
        "key_vars": ["GEPU_log"],
        "key_labels": [r"$\log(\mathrm{GEPU})_{t}$"],
        "key_tails": ["one_pos"],
    },
    {
        "id": "H25",
        "type": "moderation",
        "dir": "h25_gpr",
        "caption": "H25: Geopolitical Risk and Call Language Uncertainty",
        "label": "tab:h25",
        "cols": 8,
        "col_files": {
            1: "regression_results_col1.txt",
            2: "regression_results_col2.txt",
            3: "regression_results_col3.txt",
            4: "regression_results_col4.txt",
            5: "regression_results_col5.txt",
            6: "regression_results_col6.txt",
            7: "regression_results_col7.txt",
            8: "regression_results_col8.txt",
        },
        "dvs": [
            (r"Industry + Cal.~Year FE", 4),
            (r"Firm + Cal.~Year FE", 4),
        ],
        "col_dv_labels": [
            "Mgr QA", "Mgr Pres", "CEO QA", "CEO Pres",
            "Mgr QA", "Mgr Pres", "CEO QA", "CEO Pres",
        ],
        "key_vars": ["GPR_log"],
        "key_labels": [r"$\log(\mathrm{GPR})_{t}$"],
        "key_tails": ["one_pos"],
    },
]

IV_NAMES = [
    "CEO_QA_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    "Manager_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    # Post-rename short names (pipeline outputs use these now)
    "UncAnsCEO",
    "UncPreCEO",
    "UncAnsMgr",
    "UncPreMgr",
]

# Also match averaged versions (firm-year averaged IVs)
IV_ALIASES = {
    "Avg_CEO_QA_Uncertainty_pct": "CEO_QA_Uncertainty_pct",
    "Avg_CEO_Pres_Uncertainty_pct": "CEO_Pres_Uncertainty_pct",
    "Avg_Manager_QA_Uncertainty_pct": "Manager_QA_Uncertainty_pct",
    "Avg_Manager_Pres_Uncertainty_pct": "Manager_Pres_Uncertainty_pct",
}

# Display names for table output (old pipeline name -> new standard name)
IV_DISPLAY = {
    "CEO_QA_Uncertainty_pct": "UncAnsCEO",
    "CEO_Pres_Uncertainty_pct": "UncPreCEO",
    "Manager_QA_Uncertainty_pct": "UncAnsMgr",
    "Manager_Pres_Uncertainty_pct": "UncPreMgr",
    "Avg_CEO_QA_Uncertainty_pct": "UncAnsCEO",
    "Avg_CEO_Pres_Uncertainty_pct": "UncPreCEO",
    "Avg_Manager_QA_Uncertainty_pct": "UncAnsMgr",
    "Avg_Manager_Pres_Uncertainty_pct": "UncPreMgr",
}

# Control display names (old pipeline name -> new standard name)
CTRL_DISPLAY = {
    "Size": "lnAssets",
    "BM": "BTM",
    "BookLev": "Leverage",
    "CashHoldings": "CashRatio",
    "DividendPayer": "DivDummy",
    "OCF_Volatility": "sCFO",
    "CashFlow": "CashFlowAt",
    "CapexAt": "Capex",
    "RD_Intensity": "RDSales",
    "Intangibility": "FracInt",
    "AssetGrowth": "dAA",
    "EPS_Growth": "EPSgrowth",
    "loss_dummy": "Loss",
    "earnings_volatility": "EarnVol",
    "firm_maturity": "FirmMat",
    "Volatility": "DailyVola",
    "delta_amihud": "DeltaILLIQ",
    "pre_call_amihud": "PreCallILLIQ",
    "amihud_illiq": "ILLIQ",
    "WangDISP": "DISP",
    "CCCL": "CCCL",
    "PRiskQ": "PRisk",
    "PRiskQ_lag": "PRisk_lag",
    "PRiskQ_lag2": "PRisk_lag2",
    "PRiskQ_lead": "PRisk_lead",
    "PRiskQ_lead2": "PRisk_lead2",
    "tnic3tsimm": "TotalSimilarity",
    "z_log_tnic3tsimm": "z_log_TotalSimilarity",
    "Analyst_QA_Uncertainty_pct": "UncQue",
    "Entire_All_Negative_pct": "NegCall",
    "Entire_All_Uncertainty_pct": "UncCall",
    "Pres_Control": "Pres Unc.",
}

def fix_bare_superscripts(tex):
    """Fix bare ^{...} outside math mode → $^{...}$ for prebuilt tex files."""
    return re.sub(r'(?<!\$)\^(\{[^}]*\})', r'$^\1$', tex)


def display_name(varname):
    """Map old pipeline variable name to new standard display name."""
    return IV_DISPLAY.get(varname, CTRL_DISPLAY.get(varname, varname))


def tex_escape(varname):
    """Escape variable name for LaTeX — applies display rename first."""
    name = display_name(varname)
    return name.replace("_", r"\_")


def parse_txt(fpath):
    """Parse a regression_results_col*.txt file. Returns dict of var -> (beta, se, pval)."""
    text = fpath.read_text(encoding="utf-8")
    results = {}

    # Extract R² (plain, not within — matches first "R-squared:" line in PanelOLS summary)
    m = re.search(r"R-squared:\s+([-\d.eE+]+)", text)
    r2 = float(m.group(1)) if m else None

    # Extract Adjusted R² from runner header line (PanelOLS doesn't print it in summary)
    m_adj = re.search(r"Adj_R2:\s+([-\d.eE+]+)", text)
    adj_r2 = float(m_adj.group(1)) if m_adj else None

    # Extract N
    m = re.search(r"No\. Observations:\s+(\d+)", text)
    n_obs = int(m.group(1)) if m else None

    # Extract FE info
    fe_info = ""
    if "Other Effect" in text or "other effect" in text.lower():
        fe_info = "industry"
    if "EntityEffects" in text or "entity_effects" in text.lower():
        fe_info = "firm"
    # Detect "Entity" in "Included effects:" line (firm FE via PanelOLS)
    if re.search(r"Included effects:.*Entity", text):
        fe_info = "firm"
    # Check header lines (overrides auto-detection)
    m_fe = re.search(r"FE:\s+(\w+)", text)
    if m_fe:
        fe_info = m_fe.group(1).lower()

    # Extract controls type
    m_ctrl = re.search(r"Controls:\s+(\w+)", text)
    ctrl_type = m_ctrl.group(1) if m_ctrl else ""

    # Parse parameter table (handles both PanelOLS and OLS formats)
    in_params = False
    for line in text.split("\n"):
        if ("Parameter  Std. Err." in line or "Parameter Estimates" in line
                or ("coef" in line and "std err" in line and "P>" in line)):
            in_params = True
            continue
        if in_params and line.startswith("==="):
            if results:
                break
            continue
        if in_params and line.startswith("---"):
            continue
        if in_params and line.strip():
            parts = line.split()
            if len(parts) >= 4:
                var_name = parts[0]
                # Skip categorical FE dummies (C(ceo_id), C(year), etc.)
                if var_name.startswith("C("):
                    continue
                try:
                    beta = float(parts[1])
                    se = float(parts[2])
                    pval = float(parts[4]) if len(parts) > 4 else 1.0
                    results[var_name] = (beta, se, pval)
                except (ValueError, IndexError):
                    continue

    return results, r2, n_obs, fe_info, ctrl_type, adj_r2


def sig_stars(pval, tail):
    """Return significance stars. For two-tailed, use raw p. For one-tailed, use p/2 if right direction."""
    if pval < 0.01:
        return "***"
    if pval < 0.05:
        return "**"
    if pval < 0.10:
        return "*"
    return ""


def fmt_coef(beta, se, pval_two, tail, hyp_dir):
    """Format coefficient with bold if significant + stars."""
    assert hyp_dir in (">", "<", None), f"Unrecognized hyp_dir: {hyp_dir!r}"
    if tail == "one" and hyp_dir == ">":
        p_test = pval_two / 2 if beta > 0 else 1 - pval_two / 2
    elif tail == "one" and hyp_dir == "<":
        p_test = pval_two / 2 if beta < 0 else 1 - pval_two / 2
    else:
        p_test = pval_two

    stars = sig_stars(p_test, tail)
    b_str = f"{beta:.4f}"
    se_str = f"({se:.4f})"

    if stars:
        b_str = r"\textbf{" + b_str + "}" + f"$^{{{stars}}}$"

    return b_str, se_str


def generate_interaction_table(suite):
    """Generate a single LaTeX table for H13.1-style interaction suites.

    Each of 6 IVs was tested separately with its own interaction term.
    The table shows 4 columns (2 DVs x 2 FE), with rows for:
      - 6 IV main effects (each from its own regression)
      - tnic3hhi (from one representative regression per column)
      - 6 IV x HHI interaction terms (each from its own regression)
      - Controls, FE indicators, N, R²
    """
    import pandas as pd

    suite_dir = resolve_suite_dir(suite["dir"])
    diag_path = suite_dir / "model_diagnostics.csv"
    if not diag_path.exists():
        return ""

    diag = pd.read_csv(diag_path)
    n_cols = suite["cols"]
    tail = suite["tail"]
    hyp_dir = suite.get("hyp_dir")

    # Define columns: (DV, FE) combos
    col_specs = [
        ("Capex", "industry"),
        ("Capex", "firm"),
        ("Capex_lead", "industry"),
        ("Capex_lead", "firm"),
    ]

    ivs = [
        ("UncAnsCEO", r"UncAnsCEO"),
        ("UncPreCEO", r"UncPreCEO"),
        ("UncAnsMgr", r"UncAnsMgr"),
        ("UncPreMgr", r"UncPreMgr"),
    ]

    def _get_row(iv_name, dv, fe):
        """Get diagnostics row for a specific (iv, dv, fe) combo."""
        mask = (diag["iv"] == iv_name) & (diag["dv"] == dv) & (diag["fe"] == fe)
        rows = diag[mask]
        return rows.iloc[0] if len(rows) > 0 else None

    def _fmt(val, pval):
        stars = sig_stars(pval, "two")
        b_str = f"{val:.4f}"
        if stars:
            b_str = r"\textbf{" + b_str + "}" + f"$^{{{stars}}}$"
        return b_str

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{" + suite["caption"] + "}")
    lines.append(r"\label{" + suite["label"] + "}")
    lines.append(r"\scriptsize")
    lines.append(r"\begin{tabular}{l" + "c" * n_cols + "}")
    lines.append(r"\toprule")

    # Column numbers
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    # DV headers
    dv_parts = suite["dvs"]
    dv1_label, dv1_span = dv_parts[0]
    dv2_label, dv2_span = dv_parts[1]
    lines.append(
        f" & \\multicolumn{{{dv1_span}}}{{c}}{{{dv1_label}}} "
        f"& \\multicolumn{{{dv2_span}}}{{c}}{{{dv2_label}}} " + r"\\"
    )
    lines.append(
        f"\\cmidrule(lr){{2-{dv1_span + 1}}} "
        f"\\cmidrule(lr){{{dv1_span + 2}-{dv1_span + dv2_span + 1}}}"
    )
    lines.append(r"\midrule")

    # --- IV main effect rows (β₁ from each IV's own regression) ---
    for iv_name, iv_label in ivs:
        coef_cells = []
        se_cells = []
        for dv, fe in col_specs:
            row = _get_row(iv_name, dv, fe)
            if row is not None:
                coef_cells.append(_fmt(row["beta_iv"], row["p_two_iv"]))
                se_cells.append(f"({row['se_iv']:.4f})")
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{iv_label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # --- tnic3hhi row (pick one representative per column — Manager QA, largest N) ---
    coef_cells = []
    se_cells = []
    for dv, fe in col_specs:
        row = _get_row("UncAnsMgr", dv, fe)
        if row is not None:
            coef_cells.append(_fmt(row["beta_hhi"], row["p_two_hhi"]))
            se_cells.append(f"({row['se_hhi']:.4f})")
        else:
            coef_cells.append("")
            se_cells.append("")
    lines.append(r"TNIC3HHI & " + " & ".join(coef_cells) + r" \\")
    lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # --- Interaction rows (β₃ from each IV's own regression) ---
    for iv_name, iv_label in ivs:
        interaction_label = f"{iv_label} $\\times$ HHI"
        coef_cells = []
        se_cells = []
        for dv, fe in col_specs:
            row = _get_row(iv_name, dv, fe)
            if row is not None:
                coef_cells.append(_fmt(row["beta_interaction"], row["p_two_interaction"]))
                se_cells.append(f"({row['se_interaction']:.4f})")
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{interaction_label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # --- Control coefficients from parsed .txt files ---
    # Build file mapping: (dv, fe) -> txt file path
    dv_file_map = {
        "Capex": "Capex",
        "Capex_lead": "Capex_lead",
    }
    fe_file_map = {"industry": "industry", "firm": "firm"}
    # Use Manager_QA regression for control coefficients (representative)
    rep_iv = "Manager_QA"
    col_parsed = {}
    control_vars_ordered = []
    control_vars_seen = set()
    skip_vars = {"Intercept"}
    # Collect IVs and interaction vars to exclude from controls
    iv_exclude = set()
    for iv_name, _ in ivs:
        iv_exclude.add(iv_name)
    iv_exclude.add("tnic3hhi")
    for iv_name, _ in ivs:
        iv_exclude.add(f"{iv_name}_x_hhi")

    for col_idx, (dv, fe) in enumerate(col_specs):
        fname = f"regression_results_{rep_iv}_{dv_file_map[dv]}_{fe_file_map[fe]}.txt"
        fpath = suite_dir / fname
        if fpath.exists():
            results, r2, n, _, _, adj_r2 = parse_txt(fpath)
            col_parsed[col_idx] = {"results": results, "r2": r2, "n": n, "adj_r2": adj_r2}
            for v in results.keys():
                if v not in control_vars_seen and v not in iv_exclude and v not in skip_vars:
                    control_vars_seen.add(v)
                    control_vars_ordered.append(v)

    # Print control rows
    for var in control_vars_ordered:
        coef_cells = []
        se_cells = []
        for col_idx in range(len(col_specs)):
            parsed = col_parsed.get(col_idx)
            if parsed and var in parsed["results"]:
                beta, se, pval = parsed["results"][var]
                b_str, s_str = fmt_coef(beta, se, pval, "two", None)
                coef_cells.append(b_str)
                se_cells.append(s_str)
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{tex_escape(var)} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # --- Footer: FE, N, R² ---
    ind_cells = []
    firm_cells = []
    year_cells = []
    yr_qtr_cells = []
    for dv, fe in col_specs:
        base_fe = fe.replace("_yq", "") if fe else ""
        is_yq = fe.endswith("_yq") if fe else False
        ind_cells.append("Yes" if base_fe == "industry" else "")
        firm_cells.append("Yes" if base_fe == "firm" else "")
        year_cells.append("Yes" if not is_yq else "")
        yr_qtr_cells.append("Yes" if is_yq else "")
    lines.append(r"Industry FE & " + " & ".join(ind_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_cells) + r" \\")
    lines.append(r"Year FE & " + " & ".join(year_cells) + r" \\")
    if any(c == "Yes" for c in yr_qtr_cells):
        lines.append(r"Year-Quarter FE & " + " & ".join(yr_qtr_cells) + r" \\")

    lines.append(r"\midrule")

    # N and R² from parsed files
    n_cells = []
    r2_cells = []
    adj_r2_cells = []
    for col_idx in range(len(col_specs)):
        parsed = col_parsed.get(col_idx)
        if parsed:
            n_cells.append(f"{parsed['n']:,}")
            r2_val = parsed['r2']
            r2_cells.append(f"{r2_val:.2e}" if r2_val is not None and abs(r2_val) < 0.001 else f"{r2_val:.3f}" if r2_val is not None else "")
            adj_val = parsed.get('adj_r2')
            adj_r2_cells.append(f"{adj_val:.3f}" if adj_val is not None else "")
        else:
            n_cells.append("")
            r2_cells.append("")
            adj_r2_cells.append("")
    lines.append(r"N & " + " & ".join(n_cells) + r" \\")
    lines.append(r"$R^2$ & " + " & ".join(r2_cells) + r" \\")
    lines.append(r"Adj.~$R^2$ & " + " & ".join(adj_r2_cells) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    lines.append(r"\begin{minipage}{\linewidth}")
    lines.append(r"\vspace{2pt}\scriptsize")
    lines.append(r"\textit{Notes:} ")
    lines.append(r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed).")
    lines.append(r" Each IV row comes from a separate regression with that IV, TNIC3HHI, and their interaction.")
    lines.append(r" TNIC3HHI is the Hoberg-Phillips (2016) text-based Herfindahl index.")
    lines.append(r" Control coefficients shown from Manager QA regression (representative).")
    lines.append(r" Significant coefficients in \textbf{bold}.")
    _twoway_ids = {
        "H1", "H1.1", "H1.1b", "H1.2", "H4a", "H4b", "H13", "H13.2", "H16",
        # 2026-04-17 liquidity-extension upgrade: 10 suites added (H7/H7b/H14/H14b
        # upgraded firm-only -> two-way; H7c/d/e + H14c/d/e are new BGT 25-day suites)
        "H7", "H7b", "H7c", "H7d", "H7e",
        "H14", "H14b", "H14c", "H14d", "H14e",
        # 2026-04-10 H12b dividend payer binary (Hoberg-Prabhala 2009 ex-date analog)
        "H12b",
        # 2026-04-10 H24/H24b/H25 reverse macro uncertainty suites
        # (firm × cal_yr_qtr two-way clustering; time FE omitted because it
        # would absorb the macro IV — see run_h24_us_epu.py)
        "H24", "H24b", "H25",
    }
    if suite.get("id", "") in _twoway_ids:
        lines.append(r" Standard errors (in parentheses) two-way clustered (firm, time).")
    else:
        lines.append(r" Standard errors (in parentheses) clustered at firm level.")
    lines.append(r" Main sample (excludes financial and utility firms).")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def generate_moderation_table(suite):
    """Generate a LaTeX table for moderation suites (H1.1, H1.2, etc.).

    These have a small number of columns (typically 2) with key variables
    (IV, moderator(s), interaction(s)) shown prominently, then all controls
    with coefficients and SEs, matching the style of the main suite tables.
    """
    suite_dir = resolve_suite_dir(suite["dir"])
    n_cols = suite["cols"]
    key_vars = suite["key_vars"]
    key_labels = suite["key_labels"]
    key_tails = suite["key_tails"]

    # Parse all column files
    col_files = suite.get("col_files", {})
    col_data = {}
    all_vars_ordered = []
    all_vars_seen = set()
    for c in range(1, n_cols + 1):
        if c in col_files:
            fpath = suite_dir / col_files[c]
        else:
            fpath = suite_dir / f"regression_results_col{c}.txt"
        if not fpath.exists():
            continue
        results, r2, n, fe, ctrl, adj_r2 = parse_txt(fpath)
        cluster_fallback = bool(re.search(r"Cluster_Fallback:\s*True", fpath.read_text(encoding="utf-8")))
        col_data[c] = {"results": results, "r2": r2, "n": n, "fe": fe, "ctrl": ctrl, "adj_r2": adj_r2, "cluster_fallback": cluster_fallback}
        for v in results.keys():
            if v not in all_vars_seen:
                all_vars_seen.add(v)
                all_vars_ordered.append(v)

    if not col_data:
        return ""

    # Separate key vars, lagged DV, and controls
    key_set = set(key_vars)
    lagged_dv_var = suite.get("lagged_dv_var")
    skip_vars = {"Intercept"}
    if lagged_dv_var:
        skip_vars.add(lagged_dv_var)
    controls_in_data = [v for v in all_vars_ordered
                        if v not in key_set and v not in skip_vars]

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{" + suite["caption"] + "}")
    lines.append(r"\label{" + suite["label"] + "}")
    lines.append(r"\scriptsize")
    lines.append(r"\begin{tabular}{l" + "c" * n_cols + "}")
    lines.append(r"\toprule")

    # Column numbers
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    # DV headers
    dv_parts = suite["dvs"]
    col_dv_labels = suite.get("col_dv_labels")

    if len(dv_parts) == 1:
        dv_label, dv_span = dv_parts[0]
        lines.append(f" & \\multicolumn{{{dv_span}}}{{c}}{{{dv_label}}} " + r"\\")
        lines.append(f"\\cmidrule(lr){{2-{dv_span + 1}}}")
    elif all(span == 1 for _, span in dv_parts):
        # Simple case: each DV is 1 column
        dv_labels = " & ".join(label for label, _ in dv_parts)
        lines.append(f" & {dv_labels} " + r"\\")
    else:
        # Multi-span DV group headers
        dv_header_parts = []
        cmidrule_parts = []
        col_start = 2
        for label, span in dv_parts:
            dv_header_parts.append(f"\\multicolumn{{{span}}}{{c}}{{{label}}}")
            col_end = col_start + span - 1
            cmidrule_parts.append(f"\\cmidrule(lr){{{col_start}-{col_end}}}")
            col_start = col_end + 1
        lines.append(" & " + " & ".join(dv_header_parts) + r" \\")
        lines.append(" ".join(cmidrule_parts))

    # Per-column DV sub-labels (e.g., CapEx_t, CapEx_{t+1} under each moderator group)
    if col_dv_labels:
        sub_labels = " & ".join(col_dv_labels)
        lines.append(f" & {sub_labels} " + r"\\")

    lines.append(r"\midrule")

    # Base IV row: unconditional IV from separate base-model files
    base_iv = suite.get("base_iv")
    if base_iv:
        base_data = {}
        for pos, fname in base_iv["files"].items():
            fpath = suite_dir / fname
            if fpath.exists():
                results, *_ = parse_txt(fpath)
                base_data[pos] = results
        bvar = base_iv["var"]
        blabel = base_iv["label"]
        btail = base_iv.get("tail", "two")
        coef_cells = []
        se_cells = []
        for c in range(1, n_cols + 1):
            if c in base_data and bvar in base_data[c]:
                beta, se, pval = base_data[c][bvar]
                if btail == "one_pos":
                    b_str, s_str = fmt_coef(beta, se, pval, "one", ">")
                elif btail == "one_neg":
                    b_str, s_str = fmt_coef(beta, se, pval, "one", "<")
                else:
                    b_str, s_str = fmt_coef(beta, se, pval, "two", None)
                coef_cells.append(b_str)
                se_cells.append(s_str)
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{blabel} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    # Key variable rows (IV, moderator(s), interaction(s))
    for var, label, tail_type in zip(key_vars, key_labels, key_tails):
        coef_cells = []
        se_cells = []
        for c in range(1, n_cols + 1):
            if c in col_data and var in col_data[c]["results"]:
                beta, se, pval = col_data[c]["results"][var]
                if tail_type == "one_pos":
                    b_str, s_str = fmt_coef(beta, se, pval, "one", ">")
                elif tail_type == "one_neg":
                    b_str, s_str = fmt_coef(beta, se, pval, "one", "<")
                else:
                    b_str, s_str = fmt_coef(beta, se, pval, "two", None)
                coef_cells.append(b_str)
                se_cells.append(s_str)
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    # Lagged DV row (separate from controls, between key vars and controls)
    if lagged_dv_var:
        lagged_dv_label = suite.get("lagged_dv_label", tex_escape(lagged_dv_var))
        coef_cells = []
        se_cells = []
        for c in range(1, n_cols + 1):
            if c in col_data and lagged_dv_var in col_data[c]["results"]:
                beta, se, pval = col_data[c]["results"][lagged_dv_var]
                b_str, s_str = fmt_coef(beta, se, pval, "two", None)
                coef_cells.append(b_str)
                se_cells.append(s_str)
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{lagged_dv_label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # Control rows (all two-tailed, with bold significance)
    for var in controls_in_data:
        label = tex_escape(var)
        coef_cells = []
        se_cells = []
        for c in range(1, n_cols + 1):
            if c in col_data and var in col_data[c]["results"]:
                beta, se, pval = col_data[c]["results"][var]
                b_str, s_str = fmt_coef(beta, se, pval, "two", None)
                coef_cells.append(b_str)
                se_cells.append(s_str)
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # FE rows — use override if provided, else detect from parsed files
    fe_rows_override = suite.get("fe_rows")
    if fe_rows_override:
        for fe_label, fe_cells in fe_rows_override:
            lines.append(f"{fe_label} & " + " & ".join(fe_cells) + r" \\")
    else:
        ind_cells = []
        firm_cells = []
        year_cells = []
        yr_qtr_cells = []
        for c in range(1, n_cols + 1):
            fe = col_data.get(c, {}).get("fe", "")
            base_fe = fe.replace("_yq", "") if fe else ""
            is_yq = fe.endswith("_yq") if fe else False
            ind_cells.append("Yes" if base_fe == "industry" else "")
            firm_cells.append("Yes" if base_fe == "firm" else "")
            year_cells.append("Yes" if not is_yq else "")
            yr_qtr_cells.append("Yes" if is_yq else "")
        has_ind = any(c == "Yes" for c in ind_cells)
        has_firm = any(c == "Yes" for c in firm_cells)
        if has_ind:
            lines.append(r"Industry FE & " + " & ".join(ind_cells) + r" \\")
        if has_firm:
            lines.append(r"Firm FE & " + " & ".join(firm_cells) + r" \\")
        time_fe = suite.get("time_fe_label", "Year FE")
        lines.append(f"{time_fe} & " + " & ".join(year_cells) + r" \\")
        if any(c == "Yes" for c in yr_qtr_cells):
            lines.append(r"Year-Quarter FE & " + " & ".join(yr_qtr_cells) + r" \\")
    lines.append(r"\midrule")

    # N row
    n_cells = []
    for c in range(1, n_cols + 1):
        n = col_data.get(c, {}).get("n")
        n_cells.append(f"{n:,}" if n else "")
    lines.append(r"N & " + " & ".join(n_cells) + r" \\")

    # R² and Adj R²
    r2_label = suite.get("r2_label", r"$R^2$")
    r2_cells = []
    adj_r2_cells = []
    for c in range(1, n_cols + 1):
        r2 = col_data.get(c, {}).get("r2")
        if r2 is not None:
            r2_cells.append(f"{r2:.2e}" if abs(r2) < 0.001 else f"{r2:.3f}")
        else:
            r2_cells.append("")
        adj = col_data.get(c, {}).get("adj_r2")
        adj_r2_cells.append(f"{adj:.3f}" if adj is not None else "")
    lines.append(f"{r2_label} & " + " & ".join(r2_cells) + r" \\")
    if not suite.get("skip_adj_r2"):
        lines.append(r"Adj.~$R^2$ & " + " & ".join(adj_r2_cells) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    # Build tail note based on key_tails config
    all_two = all(t == "two" for t in key_tails)
    if all_two:
        tail_note = r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed)."
    else:
        has_neg = any(t == "one_neg" for t in key_tails)
        direction = r"$\beta < 0$" if has_neg else r"$\beta > 0$"
        tail_note = (r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$."
                     f" IVs one-tailed ({direction}); controls two-tailed.")

    lines.append(r"\begin{minipage}{\linewidth}")
    lines.append(r"\vspace{2pt}\scriptsize")
    lines.append(r"\textit{Notes:} ")
    lines.append(tail_note)
    lines.append(r" Significant coefficients in \textbf{bold}.")
    _twoway_ids = {
        "H1", "H1.1", "H1.1b", "H1.2", "H4a", "H4b", "H13", "H13.2", "H16",
        # 2026-04-17 liquidity-extension upgrade: 10 suites added (H7/H7b/H14/H14b
        # upgraded firm-only -> two-way; H7c/d/e + H14c/d/e are new BGT 25-day suites)
        "H7", "H7b", "H7c", "H7d", "H7e",
        "H14", "H14b", "H14c", "H14d", "H14e",
        # 2026-04-10 H12b dividend payer binary (Hoberg-Prabhala 2009 ex-date analog)
        "H12b",
        # 2026-04-10 H24/H24b/H25 reverse macro uncertainty suites
        # (firm × cal_yr_qtr two-way clustering; time FE omitted because it
        # would absorb the macro IV — see run_h24_us_epu.py)
        "H24", "H24b", "H25",
    }
    if suite.get("id", "") in _twoway_ids:
        lines.append(r" Standard errors (in parentheses) two-way clustered (firm, time).")
    else:
        lines.append(r" Standard errors (in parentheses) clustered at firm level.")
    lines.append(r" Main sample (excludes financial and utility firms).")
    lines.append(r" $R^2$ includes absorbed fixed effects (not within-$R^2$).")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def generate_table(suite):
    """Generate a complete LaTeX table for one suite."""
    suite_dir = resolve_suite_dir(suite["dir"])
    n_cols = suite["cols"]
    tail = suite["tail"]
    hyp_dir = suite.get("hyp_dir")

    # Parse all column files
    col_files = suite.get("col_files", {})
    col_offset = suite.get("col_offset", 0)
    col_data = {}
    all_vars_seen = set()
    all_vars_ordered = []  # Preserve order, collecting from ALL columns
    for c in range(1, n_cols + 1):
        if c in col_files:
            fpath = suite_dir / col_files[c]
        else:
            fpath = suite_dir / f"regression_results_col{c + col_offset}.txt"
        if not fpath.exists():
            continue
        results, r2, n, fe, ctrl, adj_r2 = parse_txt(fpath)
        cluster_fallback = bool(re.search(r"Cluster_Fallback:\s*True", fpath.read_text(encoding="utf-8")))
        col_data[c] = {"results": results, "r2": r2, "n": n, "fe": fe, "ctrl": ctrl, "adj_r2": adj_r2, "cluster_fallback": cluster_fallback}
        # Add new variables in order they appear, preserving first-seen order
        for v in results.keys():
            if v not in all_vars_seen:
                all_vars_seen.add(v)
                all_vars_ordered.append(v)

    if not col_data:
        return ""

    # Separate IVs and controls (skip Intercept — not meaningful with absorbed FE)
    iv_set = set(IV_NAMES)
    iv_alias_map = dict(IV_ALIASES)
    ivs_in_data = []
    controls_in_data = []
    skip_vars = {"Intercept"}
    for v in all_vars_ordered:
        if v in skip_vars:
            continue
        canonical = iv_alias_map.get(v, v)
        if canonical in iv_set:
            ivs_in_data.append(v)
        else:
            controls_in_data.append(v)

    # Build table
    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{" + suite["caption"] + "}")
    lines.append(r"\label{" + suite["label"] + "}")
    lines.append(r"\scriptsize")
    lines.append(r"\begin{tabular}{l" + "c" * n_cols + "}")
    lines.append(r"\toprule")

    # Column numbers
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    # DV headers
    dv_parts = suite["dvs"]
    if len(dv_parts) == 1:
        dv_label, dv_span = dv_parts[0]
        lines.append(f" & \\multicolumn{{{dv_span}}}{{c}}{{{dv_label}}} " + r"\\")
        lines.append(f"\\cmidrule(lr){{2-{dv_span + 1}}}")
    else:
        dv_header_parts = []
        cmidrule_parts = []
        col_start = 2
        for label, span in dv_parts:
            dv_header_parts.append(f"\\multicolumn{{{span}}}{{c}}{{{label}}}")
            col_end = col_start + span - 1
            cmidrule_parts.append(f"\\cmidrule(lr){{{col_start}-{col_end}}}")
            col_start = col_end + 1
        lines.append(" & " + " & ".join(dv_header_parts) + r" \\")
        lines.append(" ".join(cmidrule_parts))

    lines.append(r"\midrule")

    # IV rows
    for var in ivs_in_data:
        canonical = iv_alias_map.get(var, var)
        label = tex_escape(var)
        coef_cells = []
        se_cells = []
        for c in range(1, n_cols + 1):
            if c in col_data and var in col_data[c]["results"]:
                beta, se, pval = col_data[c]["results"][var]
                b_str, s_str = fmt_coef(beta, se, pval, tail, hyp_dir)
                coef_cells.append(b_str)
                se_cells.append(s_str)
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # Control rows
    for var in controls_in_data:
        label = tex_escape(var)
        coef_cells = []
        se_cells = []
        for c in range(1, n_cols + 1):
            if c in col_data and var in col_data[c]["results"]:
                beta, se, pval = col_data[c]["results"][var]
                # Controls: always two-tailed significance
                b_str, s_str = fmt_coef(beta, se, pval, "two", None)
                coef_cells.append(b_str)
                se_cells.append(s_str)
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # Extended controls indicator row
    ext_cells = []
    for c in range(1, n_cols + 1):
        ctrl = col_data.get(c, {}).get("ctrl", "")
        ext_cells.append("Yes" if ctrl == "extended" else "")
    lines.append(r"Extended Controls & " + " & ".join(ext_cells) + r" \\")

    # FE rows (supports _yq suffix for calendar year-quarter FE)
    ind_cells = []
    firm_cells = []
    year_cells = []
    yr_qtr_cells = []
    for c in range(1, n_cols + 1):
        fe = col_data.get(c, {}).get("fe", "")
        base_fe = fe.replace("_yq", "") if fe else ""
        is_yq = fe.endswith("_yq") if fe else False
        ind_cells.append("Yes" if base_fe == "industry" else "")
        firm_cells.append("Yes" if base_fe == "firm" else "")
        year_cells.append("Yes" if not is_yq else "")
        yr_qtr_cells.append("Yes" if is_yq else "")
    has_ind = any(c == "Yes" for c in ind_cells)
    has_firm = any(c == "Yes" for c in firm_cells)
    if has_ind:
        lines.append(r"Industry FE & " + " & ".join(ind_cells) + r" \\")
    if has_firm:
        lines.append(r"Firm FE & " + " & ".join(firm_cells) + r" \\")
    time_fe = suite.get("time_fe_label", "Year FE")
    lines.append(f"{time_fe} & " + " & ".join(year_cells) + r" \\")
    if any(c == "Yes" for c in yr_qtr_cells):
        lines.append(r"Year-Quarter FE & " + " & ".join(yr_qtr_cells) + r" \\")

    lines.append(r"\midrule")

    # N row
    n_cells = []
    for c in range(1, n_cols + 1):
        n = col_data.get(c, {}).get("n")
        n_cells.append(f"{n:,}" if n else "")
    lines.append(r"N & " + " & ".join(n_cells) + r" \\")

    # R² and Adj R² rows
    r2_label = suite.get("r2_label", r"$R^2$")
    r2_cells = []
    adj_r2_cells = []
    for c in range(1, n_cols + 1):
        r2 = col_data.get(c, {}).get("r2")
        if r2 is not None:
            r2_cells.append(f"{r2:.2e}" if abs(r2) < 0.001 else f"{r2:.3f}")
        else:
            r2_cells.append("")
        adj = col_data.get(c, {}).get("adj_r2")
        adj_r2_cells.append(f"{adj:.3f}" if adj is not None else "")
    lines.append(f"{r2_label} & " + " & ".join(r2_cells) + r" \\")
    if not suite.get("skip_adj_r2"):
        lines.append(r"Adj.~$R^2$ & " + " & ".join(adj_r2_cells) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    # Notes
    if tail == "one":
        sig_note = r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for IVs; two-tailed for controls)."
    else:
        sig_note = r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed)."

    lines.append(r"\begin{minipage}{\linewidth}")
    lines.append(r"\vspace{2pt}\scriptsize")
    lines.append(r"\textit{Notes:} " + sig_note)
    lines.append(r" Significant coefficients in \textbf{bold}.")
    _twoway_ids = {
        "H1", "H1.1", "H1.1b", "H1.2", "H4a", "H4b", "H13", "H13.2", "H16",
        # 2026-04-17 liquidity-extension upgrade: 10 suites added (H7/H7b/H14/H14b
        # upgraded firm-only -> two-way; H7c/d/e + H14c/d/e are new BGT 25-day suites)
        "H7", "H7b", "H7c", "H7d", "H7e",
        "H14", "H14b", "H14c", "H14d", "H14e",
        # 2026-04-10 H12b dividend payer binary (Hoberg-Prabhala 2009 ex-date analog)
        "H12b",
        # 2026-04-10 H24/H24b/H25 reverse macro uncertainty suites
        # (firm × cal_yr_qtr two-way clustering; time FE omitted because it
        # would absorb the macro IV — see run_h24_us_epu.py)
        "H24", "H24b", "H25",
    }
    if suite.get("id", "") in _twoway_ids:
        lines.append(r" Standard errors (in parentheses) two-way clustered (firm, time).")
        fallback_cols = [c for c in range(1, n_cols + 1) if col_data.get(c, {}).get("cluster_fallback")]
        if fallback_cols:
            cols_str = ", ".join(f"({c})" for c in fallback_cols)
            lines.append(
                r" Columns " + cols_str + r" fall back to firm-only clustering"
                r" (two-way clustered VCV rank-deficient; coefficients unchanged)."
            )
    else:
        lines.append(r" Standard errors (in parentheses) clustered at firm level.")
    lines.append(r" Main sample (excludes financial and utility firms).")
    lines.append(r" $R^2$ includes absorbed fixed effects (not within-$R^2$).")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def main():
    out_dir = Path(__file__).resolve().parent

    # Resolve each suite's dir to the latest run on disk
    print("Resolving latest runs:")
    for suite in SUITES:
        try:
            resolved = resolve_suite_dir(suite["dir"])
            marker = "" if resolved.exists() else "  [MISSING]"
            print(f"  {suite['id']:<8} -> {resolved.relative_to(BASE)}{marker}")
        except FileNotFoundError as e:
            print(f"  {suite['id']:<8} -> ERROR: {e}")
    print()

    # Generate individual .tex files
    all_tex = []
    for suite in SUITES:
        print(f"Generating {suite['id']}...")
        if suite.get("prebuilt_tex"):
            tex_path = resolve_suite_dir(suite["dir"]) / suite["prebuilt_tex"]
            if tex_path.exists():
                tex = fix_bare_superscripts(tex_path.read_text(encoding="utf-8"))
                all_tex.append(tex)
                print(f"  OK (prebuilt)")
            else:
                print(f"  SKIPPED (prebuilt tex not found: {tex_path})")
        elif suite.get("type") == "moderation":
            tex = generate_moderation_table(suite)
            if tex:
                all_tex.append(tex)
                print(f"  OK")
            else:
                print(f"  SKIPPED (no data)")
        elif suite.get("type") == "interaction":
            tex = generate_interaction_table(suite)
            if tex:
                all_tex.append(tex)
                print(f"  OK")
            else:
                print(f"  SKIPPED (no data)")
        else:
            tex = generate_table(suite)
            if tex:
                all_tex.append(tex)
                print(f"  OK")
            else:
                print(f"  SKIPPED (no data)")

    # Write master document
    master = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[margin=1.2cm,landscape]{geometry}",
        r"\usepackage{booktabs}",
        r"\usepackage{amsmath}",
        r"\usepackage{newtxtext,newtxmath}",
        r"\usepackage{graphicx}",
        r"\usepackage{float}",
        r"\pagestyle{plain}",
        r"\pagenumbering{arabic}",
        r"\begin{document}",
    ]
    for i, tex in enumerate(all_tex):
        master.append(tex)
        if i < len(all_tex) - 1:
            master.append(r"\clearpage")
    master.append(r"\end{document}")

    tex_path = out_dir / "all_tables.tex"
    tex_path.write_text("\n".join(master), encoding="utf-8")
    print(f"\nWrote {tex_path}")

    # Compile PDF
    print("Compiling PDF...")
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
        cwd=str(out_dir),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"SUCCESS: {out_dir / 'all_tables.pdf'}")
    else:
        print("FAILED:")
        for line in result.stdout.split("\n"):
            if "!" in line or "Error" in line:
                print(f"  {line}")

    # Cleanup aux files
    for ext in [".aux", ".log"]:
        p = out_dir / f"all_tables{ext}"
        if p.exists():
            p.unlink()


if __name__ == "__main__":
    main()
