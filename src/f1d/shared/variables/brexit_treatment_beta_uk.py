"""Brexit β^UK treatment builder — H1.5.brexit_did design.

Replicates Campello et al. 2022 JFQA equation (13) verbatim (paper p.3191):

    vol(r_it) = α_i + β_i^UK · vol(FTSE100_t) + θ · CONTROLS_t + ε

where CONTROLS = vol(SP500) + vol(FX£), all at monthly frequency, t ∈ 2010M1
through 2014M12 (60 monthly observations per firm), per spec lines 807-815 of
``tmp/3did_replication_v2_2026_05_08.md``.

Volatility convention is realized vol = standard deviation of intramonth daily
log-returns. This is the academic standard (Andersen-Bollerslev-Diebold-Labys
realized-vol) and matches Campello §IV.A.1 verbatim "the volatility of equity
returns". Daily inputs:

    - CRSP DSF (firm equity returns + S&P 500 sprtrn)
    - Yahoo daily ^FTSE (FTSE100 close)
    - BoE USD/GBP daily

Treatment label per spec lines 812-814:

    β^UK ranked across NONNEGATIVE values only.
        TREATED    β^UK > top-tercile breakpoint   (Campello 449 firms; cut 0.68)
        CONTROL    β^UK < bottom-tercile breakpoint (Campello 360 firms; cut 0.28)
        DROPPED    middle tercile + all negative β^UK firms

F1D-restricted universe will produce different breakpoints; we use F1D-relative
terciles within nonneg β^UK and document the cutoffs in the output diagnostics.

Architecture (per ~/.claude/plans/tender-popping-origami.md Section 1):

    1. Build 60-row monthly time-series of vol_FTSE100, vol_SP500, vol_FX£.
    2. Stream CRSP daily (year-by-year) → aggregate to monthly std per (gvkey, m).
       PERMNO→gvkey mapping is date-windowed per CCM linktable conventions
       (LINKDT ≤ date ≤ LINKENDDT, LINKPRIM='P', LINKTYPE in {LU,LC}).
    3. Closed-form vectorized OLS: Y @ M.T where M = (X'X)^-1 X' is precomputed
       once (3-control + 1-intercept design, 60×4). β^UK is column 1 of result.
    4. Tercile assignment on nonneg β^UK only.

Memory budget: peaks during one year's CRSP daily load (~150 MB raw). Monthly
aggregation collapses to ~300K rows. Total wall-time ~30-60 seconds first run.

Output:
    outputs/variables/brexit_treatment_beta_uk/<ts>/beta_uk_per_firm.parquet
    schema: gvkey (str-zfill-6), beta_uk, beta_se, n_obs, HIGH_BETA_UK
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats

logger = logging.getLogger(__name__)


# Estimation window per spec lines 339, 807-808.
BETA_UK_YEARS = list(range(2010, 2015))  # 2010, 2011, 2012, 2013, 2014
BETA_UK_START = pd.Timestamp("2010-01-01")
BETA_UK_END = pd.Timestamp("2014-12-31")
N_MONTHS_FULL = 60  # 5 years × 12 months — complete sample required per spec

# Minimum number of intramonth daily observations to consider a monthly std
# observation valid. Months with fewer obs are dropped from a firm's series.
# 15 trading days ≈ ¾ of a typical 21-day month.
MIN_DAYS_PER_MONTH = 15

# Number of regressors in equation (13) excluding intercept:
# vol(FTSE100), vol(SP500), vol(FX£).
N_REGRESSORS = 3

# Output column for HIGH_BETA_UK treatment dummy.
TREATMENT_COL = "HIGH_BETA_UK"


def _to_log_return(price: pd.Series) -> pd.Series:
    """Daily log-return = ln(P_t / P_{t-1}). Drops first row (NaN)."""
    return np.log(price.astype(float) / price.astype(float).shift(1))


def _monthly_std(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    group_cols: List[str] | None = None,
) -> pd.DataFrame:
    """Aggregate daily values to monthly std-dev within (group_cols, year, month).

    Months with fewer than MIN_DAYS_PER_MONTH observations are dropped.
    Returns DataFrame with [group_cols..., year_month, vol].
    """
    df = df.copy()
    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    keys = (group_cols or []) + ["year", "month"]
    agg = df.groupby(keys, observed=True)[value_col].agg(["std", "count"]).reset_index()
    agg = agg[agg["count"] >= MIN_DAYS_PER_MONTH]
    agg = agg.rename(columns={"std": "vol"})
    agg["year_month"] = agg["year"] * 100 + agg["month"]
    return agg.drop(columns=["std"] if "std" in agg.columns else [])


def _build_macro_vol_panel(root_path: Path) -> pd.DataFrame:
    """Construct 60-row monthly time-series of vol_FTSE100, vol_SP500, vol_FX£.

    Returns DataFrame indexed 0..59 with columns [year_month, vol_ftse, vol_sp500, vol_fx].
    """
    # FTSE100 — daily close from yfinance
    ftse_path = root_path / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv"
    ftse = pd.read_csv(ftse_path, parse_dates=["Date"])
    ftse = ftse.rename(columns={"Date": "date", "Close": "close"})
    ftse = ftse[["date", "close"]].sort_values("date").reset_index(drop=True)
    ftse["log_ret"] = _to_log_return(ftse["close"])
    ftse = ftse.dropna(subset=["log_ret"])
    ftse_w = ftse[(ftse["date"] >= BETA_UK_START) & (ftse["date"] <= BETA_UK_END)].copy()
    ftse_monthly = _monthly_std(ftse_w, "date", "log_ret")
    ftse_monthly = ftse_monthly.rename(columns={"vol": "vol_ftse"})

    # USD/GBP — daily from BoE; XUDLUSS = USD per GBP
    gbp_path = root_path / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv"
    gbp = pd.read_csv(gbp_path)
    gbp.columns = [c.strip().upper() for c in gbp.columns]
    gbp = gbp.rename(columns={"DATE": "date", "XUDLUSS": "fx"})
    gbp["date"] = pd.to_datetime(gbp["date"], format="%d %b %Y")
    gbp = gbp[["date", "fx"]].sort_values("date").reset_index(drop=True)
    gbp["log_ret"] = _to_log_return(gbp["fx"])
    gbp = gbp.dropna(subset=["log_ret"])
    gbp_w = gbp[(gbp["date"] >= BETA_UK_START) & (gbp["date"] <= BETA_UK_END)].copy()
    gbp_monthly = _monthly_std(gbp_w, "date", "log_ret")
    gbp_monthly = gbp_monthly.rename(columns={"vol": "vol_fx"})

    # S&P 500 — sprtrn from CRSP DSF is the daily simple return on the index.
    # Apply log1p for consistency with FTSE+GBP series (both log-returns of levels).
    sp_rows = []
    for year in BETA_UK_YEARS:
        for q in range(1, 5):
            fp = root_path / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
            if not fp.exists():
                continue
            # sprtrn is constant across all rows on a given date → drop_duplicates(date).
            df = pd.read_parquet(fp, columns=["date", "sprtrn", "PERMNO"])
            df = df.dropna(subset=["sprtrn"]).drop_duplicates(subset=["date"])
            df["date"] = pd.to_datetime(df["date"])
            sp_rows.append(df[["date", "sprtrn"]])
    sp = pd.concat(sp_rows, ignore_index=True).drop_duplicates(subset=["date"]).sort_values("date")
    sp_w = sp[(sp["date"] >= BETA_UK_START) & (sp["date"] <= BETA_UK_END)].copy()
    sp_w["log_ret"] = np.log1p(sp_w["sprtrn"])
    sp_w = sp_w.replace([np.inf, -np.inf], np.nan).dropna(subset=["log_ret"])
    sp_monthly = _monthly_std(sp_w, "date", "log_ret")
    sp_monthly = sp_monthly.rename(columns={"vol": "vol_sp500"})

    # Merge by year_month — INNER join to ensure all 3 series present each month.
    macro = ftse_monthly[["year_month", "vol_ftse"]].merge(
        sp_monthly[["year_month", "vol_sp500"]], on="year_month", how="inner"
    ).merge(
        gbp_monthly[["year_month", "vol_fx"]], on="year_month", how="inner"
    )
    macro = macro.sort_values("year_month").reset_index(drop=True)

    if len(macro) != N_MONTHS_FULL:
        logger.warning(
            f"Macro panel has {len(macro)} months, expected {N_MONTHS_FULL}. "
            f"Year-months present: {macro['year_month'].tolist()}"
        )

    return macro


def _load_ccm_for_window(root_path: Path) -> pd.DataFrame:
    """Load CCM linktable filtered for primary + canonical/unsearched links.

    Returns DataFrame with columns gvkey (zfill-6 str), LPERMNO (int),
    LINKDT (datetime64), LINKENDDT (datetime64; 'E' → 2099-12-31).
    """
    ccm_path = root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
    ccm = pd.read_parquet(
        ccm_path, columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKPRIM", "LINKTYPE"]
    )
    # Filter per audit MAJOR-5: primary + canonical/unsearched only.
    ccm = ccm[ccm["LINKPRIM"] == "P"].copy()
    ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])].copy()

    # Convert dates; 'E' (ongoing link) → far future.
    ccm["LINKENDDT"] = ccm["LINKENDDT"].astype(str).replace({"E": "2099-12-31"})
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
    ccm = ccm.dropna(subset=["LINKDT", "LINKENDDT", "LPERMNO"])

    # Restrict to links overlapping with β^UK window.
    overlap = (ccm["LINKENDDT"] >= BETA_UK_START) & (ccm["LINKDT"] <= BETA_UK_END)
    ccm = ccm[overlap].copy()

    ccm["gvkey"] = ccm["gvkey"].astype(int).astype(str).str.zfill(6)
    ccm["LPERMNO"] = ccm["LPERMNO"].astype(int)
    return ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]]


def _aggregate_firm_monthly_vol(root_path: Path, ccm: pd.DataFrame) -> pd.DataFrame:
    """Stream CRSP daily year-by-year → monthly firm vol → gvkey-keyed.

    Memory pattern: load 1 year's 4 quarterly parquets, project to 3 cols,
    aggregate to monthly std, free the daily DataFrame, advance to next year.

    Returns DataFrame [gvkey, year_month, vol_r] (all year_months for each
    gvkey, possibly < 60 obs for firms with mid-window listing/delisting events).
    """
    monthly_rows: List[pd.DataFrame] = []

    for year in BETA_UK_YEARS:
        year_dfs: List[pd.DataFrame] = []
        for q in range(1, 5):
            fp = root_path / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
            if not fp.exists():
                logger.warning(f"CRSP DSF missing: {fp}")
                continue
            df = pd.read_parquet(fp, columns=["PERMNO", "date", "RET"])
            df["date"] = pd.to_datetime(df["date"])
            df = df.dropna(subset=["RET", "PERMNO"])
            # CRSP RET can be string-coded for special values ('B','C','S','T'); drop.
            df["RET"] = pd.to_numeric(df["RET"], errors="coerce")
            df = df.dropna(subset=["RET"])
            df["PERMNO"] = df["PERMNO"].astype(int)
            year_dfs.append(df)

        if not year_dfs:
            continue
        year_df = pd.concat(year_dfs, ignore_index=True)
        del year_dfs

        # Window-trim before merge to reduce join cost.
        year_df = year_df[
            (year_df["date"] >= BETA_UK_START) & (year_df["date"] <= BETA_UK_END)
        ]

        # Map PERMNO → gvkey via date-windowed CCM (per audit MAJOR-5 logic).
        # Non-equi join: keep CCM rows where LINKDT ≤ date ≤ LINKENDDT.
        # Use merge_asof on PERMNO+date pairs — but pandas merge_asof requires
        # sorted-by-time-key. Simpler: cross-join on PERMNO then filter date.
        merged = year_df.merge(
            ccm.rename(columns={"LPERMNO": "PERMNO"}),
            on="PERMNO",
            how="inner",
        )
        merged = merged[
            (merged["date"] >= merged["LINKDT"]) & (merged["date"] <= merged["LINKENDDT"])
        ]
        merged = merged[["gvkey", "date", "RET"]]

        # Daily log-return ln(1+RET); drop missing/extreme losses.
        merged["log_ret"] = np.log1p(merged["RET"])
        merged = merged.replace([np.inf, -np.inf], np.nan).dropna(subset=["log_ret"])

        # Monthly std per (gvkey, year, month).
        m = _monthly_std(merged, "date", "log_ret", group_cols=["gvkey"])
        m = m.rename(columns={"vol": "vol_r"})
        monthly_rows.append(m[["gvkey", "year_month", "vol_r"]])
        del year_df, merged, m

    out = pd.concat(monthly_rows, ignore_index=True)
    return out.sort_values(["gvkey", "year_month"]).reset_index(drop=True)


def _vectorized_ols(
    Y: np.ndarray, X: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Closed-form vectorized OLS: Y_i = X β_i + ε_i for many firms i.

    Args:
        Y: (n_firms, n_obs) firm volatility matrix.
        X: (n_obs, k) design matrix [1, vol_ftse, vol_sp500, vol_fx].

    Returns:
        beta: (n_firms, k) OLS coefficients.
        se:   (n_firms, k) classical homoskedastic OLS standard errors —
              DIAGNOSTIC ONLY; not used downstream by treatment classifier
              (which keys off the point estimate β^UK and tercile rank only).
              For inference on β^UK itself we would prefer Newey-West or
              heteroskedasticity-robust SE; not implemented here since the
              treatment dummy HIGH_BETA_UK doesn't read the SE column.
    """
    n_obs, k = X.shape
    # M = (X'X)^-1 X' — shape (k, n_obs). Compute once.
    XtX_inv = np.linalg.inv(X.T @ X)  # (k, k)
    M = XtX_inv @ X.T  # (k, n_obs)
    beta = Y @ M.T  # (n_firms, k)

    # Residuals e_i = Y_i - X β_i for each firm.
    Y_hat = beta @ X.T  # (n_firms, n_obs)
    resid = Y - Y_hat  # (n_firms, n_obs)
    sigma2 = (resid * resid).sum(axis=1) / (n_obs - k)  # (n_firms,)

    # Var(β_i) = σ²_i · (X'X)^-1; SE = sqrt(diag · σ²)
    diag_XtX_inv = np.diag(XtX_inv)  # (k,)
    se = np.sqrt(np.outer(sigma2, diag_XtX_inv))  # (n_firms, k)
    return beta, se


def _assign_terciles_nonneg(
    beta_uk: pd.Series,
) -> Tuple[pd.Series, Dict[str, float]]:
    """Tercile cuts on NONNEGATIVE β^UK only (per spec line 812).

    Returns (HIGH_BETA_UK assignment, breakpoints dict).
    HIGH_BETA_UK = 1 if top tercile (treated), 0 if bottom tercile (control), NaN else.
    """
    nonneg = beta_uk[beta_uk >= 0].dropna()
    if len(nonneg) < 3:
        logger.warning(f"Only {len(nonneg)} nonneg β^UK values; tercile cuts unreliable.")
        return pd.Series(np.nan, index=beta_uk.index), {}

    breakpoints = {
        "p33_nonneg": float(nonneg.quantile(1 / 3)),
        "p67_nonneg": float(nonneg.quantile(2 / 3)),
        "n_nonneg": int(len(nonneg)),
        "n_negative_dropped": int((beta_uk < 0).sum()),
    }
    p33 = breakpoints["p33_nonneg"]
    p67 = breakpoints["p67_nonneg"]

    high = pd.Series(np.nan, index=beta_uk.index)
    high[(beta_uk >= 0) & (beta_uk <= p33)] = 0.0  # bottom tercile = control
    high[(beta_uk >= 0) & (beta_uk >= p67)] = 1.0  # top tercile = treated
    # Middle tercile + negatives stay NaN (excluded from regression).
    return high, breakpoints


class BrexitBetaUKBuilder(VariableBuilder):
    """Static-per-firm β^UK estimator (Campello et al. 2022 JFQA equation 13).

    The ``years`` argument to ``build`` is IGNORED — the estimation window is
    fixed at 2010M1-2014M12 per spec lines 339, 807-808. Output is gvkey-level
    and time-invariant; the runner merges HIGH_BETA_UK onto the panel by gvkey.
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = TREATMENT_COL

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years  # estimation window is fixed; see class docstring.

        logger.info("BrexitBetaUKBuilder: building macro vol panel ...")
        macro = _build_macro_vol_panel(root_path)
        logger.info(f"  macro panel: {len(macro)} months, range {macro['year_month'].min()}-{macro['year_month'].max()}")

        logger.info("BrexitBetaUKBuilder: loading CCM linktable ...")
        ccm = _load_ccm_for_window(root_path)
        logger.info(f"  CCM links covering Brexit window: {len(ccm):,} ({ccm['gvkey'].nunique():,} unique gvkeys)")

        logger.info("BrexitBetaUKBuilder: aggregating firm-monthly vol from CRSP DSF ...")
        firm_monthly = _aggregate_firm_monthly_vol(root_path, ccm)
        logger.info(f"  firm-month rows: {len(firm_monthly):,} ({firm_monthly['gvkey'].nunique():,} unique gvkeys)")

        # Pivot to (gvkey × month) wide matrix, retaining only firms with full N_MONTHS_FULL coverage.
        wide = firm_monthly.pivot(index="gvkey", columns="year_month", values="vol_r")
        # Reindex columns to the macro panel's exact 60 months.
        macro_months = macro["year_month"].tolist()
        wide = wide.reindex(columns=macro_months)
        # Keep only firms with all 60 obs.
        complete = wide.dropna(how="any")
        n_dropped = len(wide) - len(complete)
        logger.info(f"  complete-window firms (N={N_MONTHS_FULL}): {len(complete):,} (dropped {n_dropped:,} partial-window)")

        # Build design matrix X = [1, vol_ftse, vol_sp500, vol_fx] (60 × 4).
        X_macro = macro.set_index("year_month").loc[macro_months, ["vol_ftse", "vol_sp500", "vol_fx"]].to_numpy(dtype=float)
        X = np.column_stack([np.ones(len(X_macro)), X_macro])  # (60, 4)
        Y = complete.to_numpy(dtype=float)  # (n_firms, 60)

        # Closed-form vectorized OLS.
        logger.info(f"BrexitBetaUKBuilder: vectorized OLS on Y={Y.shape}, X={X.shape}")
        beta, se = _vectorized_ols(Y, X)
        # Column index 1 = β^UK (FTSE100 coef); col 0 = intercept.
        gvkeys = complete.index.to_numpy()
        out = pd.DataFrame(
            {
                "gvkey": gvkeys,
                "beta_uk": beta[:, 1],
                "beta_se": se[:, 1],
                "n_obs": N_MONTHS_FULL,
            }
        )

        # Tercile assignment.
        high, bp = _assign_terciles_nonneg(out["beta_uk"])
        out[TREATMENT_COL] = high
        logger.info(
            f"  β^UK distribution: mean={out['beta_uk'].mean():.4f}, "
            f"min={out['beta_uk'].min():.4f}, max={out['beta_uk'].max():.4f}"
        )
        logger.info(f"  tercile breakpoints: {bp}")
        n_treated = (out[TREATMENT_COL] == 1).sum()
        n_control = (out[TREATMENT_COL] == 0).sum()
        logger.info(f"  TREATED (top tercile, nonneg): {n_treated:,} firms")
        logger.info(f"  CONTROL (bottom tercile, nonneg): {n_control:,} firms")

        # Stats on the treatment column for VariableResult contract.
        stats = self.get_stats(out[TREATMENT_COL], TREATMENT_COL)

        metadata = {
            "source": "Campello et al. 2022 JFQA equation (13)",
            "estimation_window": f"{BETA_UK_START.date()} to {BETA_UK_END.date()}",
            "n_months": N_MONTHS_FULL,
            "n_firms_complete_window": int(len(out)),
            "n_treated_high_beta_uk": int(n_treated),
            "n_control_low_beta_uk": int(n_control),
            "tercile_breakpoints": bp,
            "column": TREATMENT_COL,
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
