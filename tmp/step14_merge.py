"""POST_t + HIGH_beta_UK + complete-case merge (Step 1.4)
Paper: Table 8 col 1 DiD — 2016:Q3-Q4 vs 2015:Q3-Q4
"""
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"

# ── Build POST_t ─────────────────────────────────────────────────────────
# POST_t = 1 for 2016:Q3-Q4, = 0 for 2015:Q3-Q4 (pre-period)
# Table 8: compares these two windows

# ── Load β^UK_i from previous build ──────────────────────────────────────
betas = pd.read_parquet("tmp/beta_uk_output.parquet")  # save from build
print("beta_uk loaded" if False else "need to save beta output first")

# ── Complete-case merge: load all variables ──────────────────────────────
# CASH, SIZE, CASH_FLOW, TOBIN_Q, SALES_GROWTH, STOCK_RETURNS, CONSENSUS_EPS
# Plus panel identifiers + FIC

# Build complete panel for 2015:Q3-Q4 and 2016:Q3-Q4
# Each variable has gvkey + cal_yr_qtr + value

print("Step 1.4 — complete-case merge placeholder")
print("Need to compile all 7 variables + β^UK_i into single panel")
