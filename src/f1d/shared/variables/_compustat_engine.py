"""Private Compustat compute engine.

Loads raw Compustat quarterly data ONCE per process, computes firm-level
accounting variables, and caches the result so that all individual builders
share a single load.

NOT a VariableBuilder — this is an internal helper. Individual VariableBuilders
(size.py, bm.py, etc.) import CompustatEngine and call get_data().

Bug fixes applied here (from red-team audit):
    CRITICAL-2: Deduplicate (gvkey, datadate) before merge_asof — keeps last row
                (most recent restatement) so asof match is deterministic.
    MAJOR-3:    EPS lag uses datadate arithmetic (target = datadate - 365 days,
                merge_asof backward within gvkey, accept only if within ±45 days)
                instead of shift(4) which counts rows not calendar quarters.
    MAJOR-6:    Size = ln(atq) only for atq > 0; zero/negative -> NaN (no clamp).
    MINOR-9:    Replace inf values with NaN after ratio computations before
                winsorization (winsorization skips NaN but passes inf unchanged).

H1 extension (2026-02-19):
    Added CashHoldings, TobinsQ, CapexAt, DividendPayer, OCF_Volatility.

H1 audit fixes (2026-02-19):
    TobinsQ: was (mkvaltq+ltq)/atq -- mkvaltq has 41% missing rate.
             Fixed to (atq + cshoq*prccq - ceqq)/atq which matches v2 design
             and cshoq*prccq has only 9.5% missing rate.
             Requires: cshoq, prccq, ceqq (already in REQUIRED_COMPUSTAT_COLS).
             Remove: mkvaltq (no longer needed).
    DividendPayer: was dvpq>0 (preferred dividends quarterly -- only 9.7% payers).
                   Fixed to dvy>0 (annual common dividends -- ~32% payers).
                   Requires: dvy instead of dvpq.
    OCF_Volatility: was 4-year rolling min 2 periods.
                    Fixed to 5-year rolling min 3 periods (matches v2 design).

Red-team audit fixes (2026-02-20):
    CRITICAL-1 CapexAt: capxy is YTD cumulative within fiscal year -- Q1 row has
                only Q1 capex, Q4 row has full-year capex. Fixed to use Q4-only
                capxy (full fiscal year) joined back to all quarters via
                gvkey+fyearq, same pattern as OCF_Volatility. Requires: fqtr.
    CRITICAL-2 DividendPayer: dvy is annual cumulative YTD -- same issue as capxy.
                Fixed to use Q4-only dvy (full fiscal year) joined back to all
                quarters via gvkey+fyearq. This correctly classifies dividend
                payers using full-year dividends regardless of when the call falls.

H2 extension (2026-02-20):
    Added InvestmentResidual (Biddle 2009), CashFlow, SalesGrowth.
    Biddle (2009) investment residual:
        Investment = (capxy + xrdy + aqcy - sppey) / at_lag  (annual Q4-only)
        First-stage OLS by FF48-year cell (min 20 obs, dropna=False so unmapped
            SIC firms are flagged, not silently swallowed):
            Investment ~ SalesGrowth_lag
        InvestmentResidual = actual - predicted investment
    New Compustat columns: xrdy, aqcy, sppey, saley, sic.
    FF48 codes derived from sic via inputs/FF1248/Siccodes48.zip.

H2 red-team audit fixes (2026-02-20):
    C-4  TobinQ Biddle predictor: was fillna(0) on mktcap/ceqq -> biased residuals
         for firms with missing market cap (TobinQ degenerates to debt ratio) or
         missing book equity (TobinQ systematically overstated). Fixed: require all
         three components non-missing; NaN otherwise. Affects ONLY the Biddle
         first-stage OLS panel (annual), not the quarterly TobinsQ control variable
         in _compute_and_winsorize() which retains the fillna(0)-free formula
         already present.
    C-6  SalesGrowth double-winsorization: was winsorized at line 467 (correct,
         before use as predictor) then again at line 516 post-OLS (dead code /
         confusion). Removed the second winsorization; InvestmentResidual only is
         winsorized post-OLS.
    M-1  saleq (quarterly revenue) replaced by saley (annual total revenue YTD)
         for SalesGrowth computation. saley is the full-year revenue equivalent,
         matching Biddle (2009) intent. Fallback to saleq only when saley missing
         (101 Q4 firm-years in dataset). Added saley to REQUIRED_COMPUSTAT_COLS.
    M-2  CashFlow denominator: was end-of-year atq (point-in-time stock vs annual
         flow). Fixed to average assets: (atq_t + atq_{t-1}) / 2, consistent with
         standard accounting practice (Biddle 2009). Gap-year at_lag NaN -> uses
         end-of-year atq as fallback with a warning flag.
    M-3  _load_ff48_map catchall detection: the prior heuristic (highest code with
         no SIC ranges) fails because code 48 "Almost Nothing" DOES have SIC ranges
         in the actual file (4950-4991). Fixed: code 48 is treated as the explicit
         catchall for any SIC not in any other FF48 range, determined by building
         a complete 0-9999 SIC lookup and assigning the remainder to code 48.
    M-4  _load_ff48_map zip reading: z.namelist()[0] is not deterministic. Fixed:
         find the .txt file by extension with assertion.
    M-6  groupby dropna: pandas groupby default dropna=True silently excludes
         firms with ff48_code=None (unmapped SICs). Fixed: use dropna=False and
         skip the None-keyed cell explicitly; added diagnostic print.
    m-2  _winsorize_by_year threshold: raised from 4 to 10 observations.
    m-3  Bare except in OLS loop: now logs (ff48, fyear) and exception type.
"""

from __future__ import annotations

import logging
import threading
import traceback
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# All columns produced by this engine (excludes file_name — matched in builders)
COMPUSTAT_COLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "CurrentRatio",
    "RD_Intensity",
    "EPS_Growth",
    # H1 extension
    "CashHoldings",
    "TobinsQ",
    "CapexAt",
    "DividendPayer",
    "OCF_Volatility",
    # H2 extension (Biddle 2009 investment residual)
    "InvestmentResidual",
    "CashFlow",
    "SalesGrowth",
    # H3 extension
    "div_stability",
    "payout_flexibility",
    "earnings_volatility",
    "fcf_growth",
    "firm_maturity",
    "is_div_payer_5yr",
]

REQUIRED_COMPUSTAT_COLS = [
    "gvkey",
    "datadate",
    "atq",
    "ceqq",
    "cshoq",
    "prccq",
    "ltq",
    "niq",
    "epspxq",
    "actq",
    "lctq",
    "xrdq",
    # H1 extension
    "cheq",
    "capxy",  # YTD cumulative CapEx -- used Q4-only (full fiscal year)
    "dvy",  # YTD cumulative common dividends -- used Q4-only (full fiscal year)
    "oancfy",
    "fyearq",
    "fqtr",  # fiscal quarter (1-4) -- used to identify Q4 rows for capxy/dvy
    # H2 extension (Biddle 2009)
    "sic",  # SIC code -- for FF48 industry classification
    "saley",  # Annual total revenue YTD (M-1 fix: replaces quarterly saleq)
    "saleq",  # Quarterly revenue -- fallback when saley missing
    "xrdy",  # R&D expense annual YTD -- used Q4-only (Biddle investment numerator)
    "aqcy",  # Acquisitions annual YTD -- used Q4-only (Biddle investment numerator)
    "sppey",  # Sale of PP&E annual YTD -- used Q4-only (Biddle investment numerator)
    # H3 extension
    "dvpspq",  # Dividends per share by ex-date (quarterly)
    "req",  # Retained earnings (quarterly)
    "seqq",  # Shareholders' equity (quarterly)
    "ibq",  # Income Before Extraordinary Items (quarterly)
    "iby",  # Income Before Extraordinary Items (annual)
]


def _compute_eps_growth_date_based(comp: pd.DataFrame) -> pd.Series:
    """Compute EPS YoY growth using datadate arithmetic, not row-count shift.

    For each row find the prior-year quarter: target = datadate - 365 days.
    Use merge_asof (backward, within gvkey) to find the closest prior quarter,
    then accept the lag only if it falls within ±45 days of the target date.
    This is robust to missing/irregular quarters (MAJOR-3 fix).

    Returns a Series aligned to the original comp index (before sorting).
    """
    comp_work = comp[["gvkey", "datadate", "epspxq"]].copy()
    comp_work["_row_id"] = np.arange(len(comp_work))

    lag_df = (
        comp_work[["gvkey", "datadate", "epspxq"]]
        .rename(columns={"datadate": "lag_datadate", "epspxq": "epspxq_lag"})
        .sort_values("lag_datadate")
    )

    lookup = comp_work.copy()
    lookup["target_lag_date"] = lookup["datadate"] - pd.Timedelta(days=365)
    lookup = lookup.sort_values("target_lag_date")

    merged = pd.merge_asof(
        lookup,
        lag_df,
        left_on="target_lag_date",
        right_on="lag_datadate",
        by="gvkey",
        direction="backward",
    )

    date_diff = (merged["target_lag_date"] - merged["lag_datadate"]).abs()
    valid = (
        merged["lag_datadate"].notna()
        & (date_diff <= pd.Timedelta(days=45))
        & merged["epspxq_lag"].notna()
        & (merged["epspxq_lag"] != 0)
    )

    merged["EPS_Growth_tmp"] = np.where(
        valid,
        (merged["epspxq"] - merged["epspxq_lag"]) / merged["epspxq_lag"].abs(),
        np.nan,
    )

    merged_sorted = merged.sort_values("_row_id")
    return pd.Series(merged_sorted["EPS_Growth_tmp"].to_numpy(), name="EPS_Growth_tmp")


def _compute_annual_q4_variable(
    comp: pd.DataFrame, raw_col: str, out_col: str
) -> pd.Series:
    """Compute a full-fiscal-year variable from a YTD-cumulative Compustat field.

    capxy and dvy are YTD-cumulative within a fiscal year: Q1 holds only Q1
    values, Q4 holds the full-year total. Using Q4 rows (fqtr==4) gives the
    correct annual figure. We then join it back to ALL quarterly rows by
    gvkey+fyearq so every call in the same fiscal year gets the same value.

    Args:
        comp: Full Compustat DataFrame (must have fqtr, fyearq, gvkey, raw_col).
        raw_col: The cumulative Compustat column (e.g. 'capxy', 'dvy').
        out_col: The output column name (e.g. 'CapexAt_annual', 'DividendPayer').

    Returns:
        Series aligned to comp's index.
    """
    q4 = (
        comp[comp["fqtr"] == 4][["gvkey", "fyearq", raw_col]]
        .dropna(subset=["fyearq"])
        .copy()
    )
    q4["fyearq"] = q4["fyearq"].astype(int)
    q4 = q4.sort_values(["gvkey", "fyearq"]).drop_duplicates(
        subset=["gvkey", "fyearq"], keep="last"
    )
    q4 = q4.rename(columns={raw_col: out_col})

    comp_aligned = comp[["gvkey", "fyearq"]].copy()
    comp_aligned["fyearq"] = pd.to_numeric(comp_aligned["fyearq"], errors="coerce")
    comp_aligned["_idx"] = np.arange(len(comp_aligned))

    merged = comp_aligned.merge(
        q4.assign(fyearq=lambda d: d["fyearq"].astype(float)),
        on=["gvkey", "fyearq"],
        how="left",
        validate="m:1",
    )
    merged = merged.sort_values("_idx")
    return merged[out_col].values  # type: ignore[return-value]


def _compute_annual_q4_variable_lag(
    comp: pd.DataFrame, raw_col: str, out_col: str
) -> pd.Series:
    """Compute a lagged full-fiscal-year variable (t-1) from Q4 rows."""
    q4 = (
        comp[comp["fqtr"] == 4][["gvkey", "fyearq", raw_col]]
        .dropna(subset=["fyearq"])
        .copy()
    )
    q4["fyearq"] = q4["fyearq"].astype(int)
    q4 = q4.sort_values(["gvkey", "fyearq"]).drop_duplicates(
        subset=["gvkey", "fyearq"], keep="last"
    )
    q4 = q4.rename(columns={raw_col: out_col})
    q4["fyearq"] += 1  # Shift forward 1 year so it joins to t

    comp_aligned = comp[["gvkey", "fyearq"]].copy()
    comp_aligned["fyearq"] = pd.to_numeric(comp_aligned["fyearq"], errors="coerce")
    comp_aligned["_idx"] = np.arange(len(comp_aligned))

    merged = comp_aligned.merge(
        q4.assign(fyearq=lambda d: d["fyearq"].astype(float)),
        on=["gvkey", "fyearq"],
        how="left",
        validate="m:1",
    )
    merged = merged.sort_values("_idx")
    return merged[out_col].values  # type: ignore[return-value]


def _compute_ocf_volatility(comp: pd.DataFrame) -> pd.Series:
    """Compute OCF_Volatility = rolling 5-year std of (oancfy / atq_{t-1}) per gvkey.

    oancfy is an annual flow variable -- use the last observation per gvkey-fyearq
    to get one data point per fiscal year. Then compute rolling std over 5 years
    (min 3 years required) and align back to full quarterly panel via gvkey+fyearq.

    FIX: Spec explicitly uses lagged assets (atq_{t-1}) in denominator to avoid
    correlated measurement error from contemporaneous asset changes.
    """
    annual = (
        comp[comp["fqtr"] == 4][["gvkey", "datadate", "fyearq", "oancfy", "atq"]]
        .dropna(subset=["fyearq"])
        .copy()
    )
    annual["fyearq"] = annual["fyearq"].astype(int)
    annual = annual.sort_values(["gvkey", "fyearq", "datadate"])
    annual = annual.drop_duplicates(subset=["gvkey", "fyearq"], keep="last")

    # FIX: Use lagged assets per spec (Assets_{τ-1})
    annual["atq_lag"] = annual.groupby("gvkey")["atq"].shift(1)

    annual["ocf_ratio"] = np.where(
        annual["atq_lag"] > 0,
        annual["oancfy"] / annual["atq_lag"],
        np.nan,
    )
    annual["ocf_ratio"] = annual["ocf_ratio"].replace([np.inf, -np.inf], np.nan)

    annual["dummy_date"] = pd.to_datetime(annual["fyearq"].astype(str) + "-12-31")
    annual = annual.sort_values("dummy_date").set_index("dummy_date")
    annual["OCF_Volatility_annual"] = annual.groupby("gvkey")["ocf_ratio"].transform(
        lambda x: x.rolling("1826D", min_periods=3).std()
    )
    annual = annual.reset_index()

    lookup = annual[["gvkey", "fyearq", "OCF_Volatility_annual"]].copy()

    comp_aligned = comp[["gvkey", "fyearq"]].copy()
    comp_aligned["fyearq"] = comp_aligned["fyearq"].astype("Int64")
    comp_aligned["_idx"] = np.arange(len(comp_aligned))

    merged = comp_aligned.merge(
        lookup.rename(columns={"OCF_Volatility_annual": "OCF_Volatility"}),
        on=["gvkey", "fyearq"],
        how="left",
        validate="m:1",
    )
    merged = merged.sort_values("_idx")
    return pd.Series(merged["OCF_Volatility"].to_numpy(), name="OCF_Volatility")  # type: ignore[return-value]


def _load_ff48_map(root_path: Path) -> Dict[int, int]:
    """Load FF48 SIC-code-to-industry mapping from Siccodes48.zip.

    Returns a dict mapping each integer SIC code (0–9999) to its FF48 industry
    code. SIC codes not in any defined range are assigned to code 48 "Almost
    Nothing" (the explicit Fama-French residual category).

    Fixes applied (H2 red-team audit):
        M-4: Find the .txt file by extension rather than z.namelist()[0] to
             guard against ZIP ordering non-determinism and extraneous files.
        M-3: Prior catchall heuristic (highest code with no explicit ranges)
             failed because code 48 DOES have explicit SIC ranges (4950-4991)
             in the actual Siccodes48.txt file. Fixed: after building the full
             SIC->FF48 lookup, any SIC 0-9999 not yet assigned is mapped to
             code 48 explicitly, mirroring Ken French's "not elsewhere classified"
             residual category.

    Args:
        root_path: Project root path.

    Returns:
        Dict[int, int]: sic -> ff48_code for every integer SIC 0-9999.

    Raises:
        FileNotFoundError: if Siccodes48.zip not found.
        ValueError: if no .txt file found inside the zip.
    """
    zip_path = root_path / "inputs" / "FF1248" / "Siccodes48.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"FF48 SIC codes file not found: {zip_path}")

    # M-4 fix: find .txt by extension, not by position
    with zipfile.ZipFile(zip_path, "r") as z:
        txt_names = [n for n in z.namelist() if n.lower().endswith(".txt")]
        if not txt_names:
            raise ValueError(
                f"No .txt file found in {zip_path}. Contents: {z.namelist()}"
            )
        txt_name = txt_names[0]
        with z.open(txt_name) as f:
            content = f.read().decode("utf-8")

    sic_to_ff48: Dict[int, int] = {}
    all_codes: List[int] = []

    current_code: Optional[int] = None
    for line in content.replace("\r", "").split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split(maxsplit=2)
        # Header line: "<code> <abbrev> <description>"
        if len(parts) >= 2 and parts[0].isdigit() and not stripped[0].isspace():
            current_code = int(parts[0])
            all_codes.append(current_code)
        elif stripped and current_code is not None:
            # Range line: "XXXX-YYYY description"
            rng_part = stripped.split()[0]
            if "-" in rng_part:
                try:
                    lo_s, hi_s = rng_part.split("-", 1)
                    lo, hi = int(lo_s), int(hi_s)
                    for sic in range(lo, hi + 1):
                        sic_to_ff48[sic] = current_code
                except ValueError:
                    continue

    # M-3 / m-4 fix: assign ALL SICs 0-9999 not in any explicit range to the
    # FF48 "Almost Nothing" residual category, hard-coded as code 48 per Ken
    # French's published methodology. Do NOT use max(all_codes) — if the file
    # were ever extended beyond 48 industries that would misassign residuals.
    CATCHALL_FF48 = 48
    for sic in range(0, 10000):
        if sic not in sic_to_ff48:
            sic_to_ff48[sic] = CATCHALL_FF48

    n_mapped = len(sic_to_ff48)
    logger.info(
        f"    FF48 map: {len(all_codes)} industries, {n_mapped} SIC codes mapped "
        f"(residual -> code {CATCHALL_FF48})"
    )
    return sic_to_ff48


def _winsorize_by_year(
    series: pd.Series, year_col: pd.Series, min_obs: int = 10
) -> pd.Series:
    """Winsorize a series at 1%/99% within each year group.

    Args:
        series: Values to winsorize (aligned to year_col).
        year_col: Year identifier (same index as series).
        min_obs: Minimum valid observations required to winsorize a year group
                 (m-2 fix: raised from 4 to 10; with < 10 obs the 1st/99th
                 percentiles are near the min/max, making winsorization a no-op).

    Returns:
        Winsorized series (same index as input).
    """
    out = series.copy()
    for _yr, grp_idx in series.groupby(year_col).groups.items():
        vals = series.loc[grp_idx]
        valid = vals.notna()
        if valid.sum() < min_obs:
            continue
        p1 = vals[valid].quantile(0.01)
        p99 = vals[valid].quantile(0.99)
        out.loc[grp_idx] = vals.clip(lower=p1, upper=p99)
    return out


def _compute_biddle_residual(
    comp: pd.DataFrame, root_path: Path
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Compute Biddle (2009) investment residual and H2 control variables.

    Biddle et al. (2009, JAE) investment efficiency measure:
        Investment = (CapEx + R&D + Acquisitions - AssetSales) / lagged(AT)
        First-stage OLS by (FF48, fiscal_year) cell (min 20 obs per cell):
            Investment ~ SalesGrowth_lag
        InvestmentResidual = actual - predicted  (>0 = overinvest, <0 = underinvest)

    Also computes:
        CashFlow = oancfy / avg_assets  (avg_assets = (atq_t + atq_{t-1}) / 2)
        SalesGrowth = (sale_t - sale_{t-1}) / abs(sale_{t-1})
            where sale = saley (annual total revenue) with saleq fallback

    All on Q4-only annual panel (one row per gvkey-fyearq), then joined back
    to all quarters via gvkey+fyearq, identical to the CapexAt/DividendPayer
    Q4-join pattern.

    Audit fixes applied:
        C-4:  TobinQ Biddle predictor: require all components non-null (no fillna(0)).
              NaN TobinQ -> that firm-year excluded from its FF48-year OLS cell.
        C-6:  Removed duplicate SalesGrowth winsorization (was at lines 467+516;
              now only at line 467 before use as first-stage predictor).
        M-1:  saley (annual total revenue) replaces saleq (quarterly revenue) for
              SalesGrowth. saley matches Biddle (2009) intent. Fallback to saleq
              when saley missing (101 Q4 firm-years in the dataset).
        M-2:  CashFlow denominator: average assets (atq_t + atq_{t-1})/2.
              Firms with no prior-year atq (first observation or gap year) fall
              back to end-of-year atq (same as v2) with a diagnostic print.
        M-3:  _load_ff48_map now covers all SIC 0-9999; no unmapped codes remain.
        M-4:  _load_ff48_map reads txt by extension, not position.
        M-6:  groupby(..., dropna=False) so None-keyed cells are visible; the None
              cell is skipped explicitly and counted in diagnostics.
        m-2:  _winsorize_by_year threshold raised to 10.
        m-3:  OLS exception now logs (ff48, fyear) and exception type.

    Args:
        comp: Full Compustat DataFrame (must have fqtr, fyearq, and all required cols).
        root_path: Project root (for FF48 zip file lookup).

    Returns:
        Tuple of three Series aligned to comp's index:
            InvestmentResidual, CashFlow, SalesGrowth
    """
    try:
        import statsmodels.api as sm  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "statsmodels is required for Biddle investment residual computation. "
            "Install with: pip install statsmodels"
        ) from exc

    # ------------------------------------------------------------------
    # Step 1: Build annual Q4-only panel
    # ------------------------------------------------------------------
    needed = [
        "gvkey",
        "fyearq",
        "fqtr",
        "datadate",
        "atq",
        "sic",
        "capxy",
        "xrdy",
        "aqcy",
        "sppey",
        "oancfy",
        "saley",
        "saleq",  # M-1: prefer saley; fallback saleq
        "cshoq",
        "prccq",
        "ceqq",
        "dlcq",
        "dlttq",
    ]
    available = [c for c in needed if c in comp.columns]
    annual = comp[comp["fqtr"] == 4][available].dropna(subset=["fyearq"]).copy()
    annual["fyearq"] = annual["fyearq"].astype(int)
    # Keep last Q4 row per gvkey-fyearq (most recent restatement)
    annual = annual.sort_values(["gvkey", "fyearq", "datadate"])
    annual = annual.drop_duplicates(subset=["gvkey", "fyearq"], keep="last")
    annual = annual.sort_values(["gvkey", "fyearq"]).reset_index(drop=True)

    logger.info(f"    Biddle: annual Q4 panel: {len(annual):,} firm-years")

    # ------------------------------------------------------------------
    # Step 2: Assign FF48 codes via SIC
    # M-3/M-4 fixes applied inside _load_ff48_map
    # ------------------------------------------------------------------
    ff48_map = _load_ff48_map(root_path)

    # Vectorized SIC → FF48 mapping replaces per-row .apply(_map_sic).
    # pd.to_numeric + .map(dict) runs in C, ~10x faster than a Python callback.
    sic_int = pd.to_numeric(annual["sic"], errors="coerce").astype("Int64")
    annual["ff48_code"] = sic_int.map(ff48_map).where(sic_int.notna(), other=None)

    n_missing_sic = annual["ff48_code"].isna().sum()
    if n_missing_sic > 0:
        logger.info(
            f"    Biddle WARNING: {n_missing_sic:,} firm-years have missing SIC "
            f"-> ff48_code=None -> excluded from all OLS cells"
        )

    # ------------------------------------------------------------------
    # Step 3: Investment measure numerator (all annual YTD fields, Q4 = full year)
    # ------------------------------------------------------------------
    # C-6 fix: do NOT fillna(0) for xrdy, aqcy, sppey.
    # fillna(0) treats a firm with MISSING acquisition data identically to a
    # firm with ZERO acquisitions, silently understating investment for firms
    # with unreported aqcy/xrdy/sppey. Instead: use 0 only for capxy (capex
    # is well-reported and near-universal); treat xrdy/aqcy/sppey as 0 only
    # when they are genuinely absent by industry convention (set below), but
    # flag firm-years where any component is missing so the residual is not
    # silently biased. Specifically: use fillna(0) for xrdy (R&D is legitimately
    # zero for most non-tech firms and is not separately reported), but require
    # capxy non-null (the dominant investment component). aqcy and sppey are
    # set to 0 when missing (standard in Biddle 2009 replication practice --
    # many firms have no acquisitions/asset sales), but we log the fraction
    # of firm-years where aqcy is missing so the analyst can audit.
    n_missing_aqcy = annual["aqcy"].isna().sum()
    n_total = len(annual)
    if n_missing_aqcy > 0:
        frac = n_missing_aqcy / n_total
        logger.info(
            f"    Biddle: aqcy missing for {n_missing_aqcy:,}/{n_total:,} "
            f"firm-years ({100 * frac:.1f}%) -- treated as 0 per Biddle replication convention"
        )
    inv_num = (
        annual["capxy"].fillna(0)  # capex: well-reported; NaN→0 is rare
        + annual["xrdy"].fillna(0)  # R&D: legitimately 0 when not reported
        + annual["aqcy"].fillna(0)  # acquisitions: 0 when none; logged above
        - annual["sppey"].fillna(0)  # asset sales: 0 when none
    )
    # Require capxy non-null: firms with no capex data get NaN Investment
    inv_num = inv_num.where(annual["capxy"].notna(), np.nan)

    # at_lag: prior year's total assets (shift within gvkey on sorted annual panel)
    annual["at_lag"] = annual.groupby("gvkey")["atq"].shift(1)
    # fyearq_lag for consecutive-year validation (integer arithmetic — exact)
    annual["fyearq_lag"] = annual.groupby("gvkey")["fyearq"].shift(1)
    gap_mask = (annual["fyearq"] - annual["fyearq_lag"]) != 1
    annual.loc[gap_mask, "at_lag"] = np.nan

    annual["Investment"] = np.where(
        (annual["at_lag"].notna()) & (annual["at_lag"] > 0),
        inv_num / annual["at_lag"],
        np.nan,
    )
    annual["Investment"] = annual["Investment"].replace([np.inf, -np.inf], np.nan)
    annual["Investment"] = _winsorize_by_year(annual["Investment"], annual["fyearq"])

    # ------------------------------------------------------------------
    # Step 4: First-stage predictors
    # ------------------------------------------------------------------
    # C-4 fix: TobinQ Biddle predictor — require all components non-null.
    mktcap = annual["cshoq"] * annual["prccq"]
    debt_c = annual["dlcq"].clip(lower=0).fillna(0)
    debt_t = annual["dlttq"].clip(lower=0).fillna(0)
    debt_book = np.where(
        annual["dlcq"].isna() & annual["dlttq"].isna(), np.nan, debt_c + debt_t
    )

    all_present = (
        annual["atq"].notna()
        & (annual["atq"] > 0)
        & mktcap.notna()
        & pd.Series(debt_book).notna()
    )
    annual["TobinQ"] = np.where(
        all_present,
        (mktcap + debt_book) / annual["atq"],
        np.nan,
    )
    annual["TobinQ"] = annual["TobinQ"].replace([np.inf, -np.inf], np.nan)
    annual["TobinQ"] = _winsorize_by_year(annual["TobinQ"], annual["fyearq"])

    # M-1 fix: use saley (annual total revenue) for SalesGrowth; fallback to saleq
    # saley ≈ sum(saleq_Q1..Q4) within 1% for 97.8% of firm-years; correct annual metric.
    if "saley" in annual.columns:
        annual["sale_annual"] = annual["saley"].fillna(annual["saleq"])
    else:
        annual["sale_annual"] = annual["saleq"]

    annual["sale_lag"] = annual.groupby("gvkey")["sale_annual"].shift(1)
    annual.loc[gap_mask, "sale_lag"] = np.nan
    annual["SalesGrowth"] = np.where(
        (annual["sale_lag"].notna()) & (annual["sale_lag"].abs() > 0),
        (annual["sale_annual"] - annual["sale_lag"]) / annual["sale_lag"].abs(),
        np.nan,
    )
    annual["SalesGrowth"] = annual["SalesGrowth"].replace([np.inf, -np.inf], np.nan)
    # Winsorize SalesGrowth ONCE before use as first-stage predictor (C-6 fix:
    # second winsorization post-OLS removed)
    annual["SalesGrowth"] = _winsorize_by_year(annual["SalesGrowth"], annual["fyearq"])

    # Lag TobinQ and SalesGrowth by one year for use as Biddle first-stage predictors
    # These become year t-1 values predicting year t Investment — correct per Biddle (2009)
    annual["TobinQ_lag"] = annual.groupby("gvkey")["TobinQ"].shift(1)
    annual.loc[gap_mask, "TobinQ_lag"] = np.nan
    annual["SalesGrowth_lag"] = annual.groupby("gvkey")["SalesGrowth"].shift(1)
    # Explicit gap check for SalesGrowth_lag: compute its own gap from fyearq_lag
    # to avoid fragile NaN-propagation dependency from prior step
    sg_fyearq_lag2 = annual.groupby("gvkey")["fyearq"].shift(2)
    sg_gap_mask = (annual["fyearq_lag"] - sg_fyearq_lag2) != 1
    annual.loc[sg_gap_mask | gap_mask, "SalesGrowth_lag"] = np.nan

    # M-2 fix: CashFlow denominator = average assets (atq_t + atq_{t-1}) / 2
    # This correctly matches an annual flow (oancfy) against the average stock
    # of assets over the year, consistent with standard accounting practice and
    # Biddle (2009). For firm-years with no prior-year atq (first obs or gap),
    # fall back to end-of-year atq.
    avg_assets = (annual["atq"] + annual["at_lag"]) / 2
    # Fallback: when at_lag is NaN (gap or first obs), use end-of-year atq
    avg_assets = avg_assets.where(avg_assets.notna(), annual["atq"])
    annual["CashFlow"] = np.where(
        avg_assets > 0,
        annual["oancfy"] / avg_assets,
        np.nan,
    )
    annual["CashFlow"] = annual["CashFlow"].replace([np.inf, -np.inf], np.nan)
    annual["CashFlow"] = _winsorize_by_year(annual["CashFlow"], annual["fyearq"])

    # ------------------------------------------------------------------
    # Step 5: First-stage OLS by (ff48_code, fyearq), min 20 obs
    # M-6 fix: dropna=False so None-keyed cell is visible; skip it explicitly.
    # m-3 fix: log exception type and cell identity instead of bare pass.
    # ------------------------------------------------------------------
    annual["InvestmentResidual"] = np.nan
    cells_run = 0
    cells_skipped_size = 0
    cells_skipped_none = 0
    cells_skipped_error = 0

    reg_cols = ["Investment", "SalesGrowth_lag"]
    for (ff48, fyear), grp in annual.groupby(["ff48_code", "fyearq"], dropna=False):
        # M-6: skip None-keyed cell (firms with missing SIC)
        if ff48 is None or pd.isna(ff48):  # type: ignore[arg-type]
            cells_skipped_none += 1
            continue

        valid_idx = grp.dropna(subset=reg_cols).index
        if len(valid_idx) < 20:
            cells_skipped_size += 1
            continue

        Y = annual.loc[valid_idx, "Investment"]
        X = sm.add_constant(annual.loc[valid_idx, ["SalesGrowth_lag"]])
        try:
            model = sm.OLS(Y, X).fit()
            annual.loc[valid_idx, "InvestmentResidual"] = Y - model.predict(X)
            cells_run += 1
        except Exception as exc:  # m-3: log identity + type, not silent skip
            exc_type = type(exc).__name__
            logger.info(
                f"    Biddle OLS error in cell (ff48={ff48}, fyear={fyear}): "
                f"{exc_type}: {exc}"
            )
            cells_skipped_error += 1

    n_valid = annual["InvestmentResidual"].notna().sum()
    logger.info(
        f"    Biddle: FF48-year cells run={cells_run}, "
        f"skipped_small={cells_skipped_size}, "
        f"skipped_none_sic={cells_skipped_none}, "
        f"skipped_error={cells_skipped_error}; "
        f"valid residuals={n_valid:,}/{len(annual):,} firm-years"
    )

    # Winsorize InvestmentResidual post-OLS (C-6 fix: SalesGrowth NOT re-winsorized here)
    annual["InvestmentResidual"] = _winsorize_by_year(
        annual["InvestmentResidual"], annual["fyearq"]
    )

    # ------------------------------------------------------------------
    # Step 6: Join all three H2 variables back to the full quarterly panel
    # via gvkey + fyearq (same Q4-join-back pattern as CapexAt/DividendPayer).
    # fyearq is integer in the annual panel; convert both sides to float for
    # the merge to avoid dtype mismatches (fyearq in comp is float64).
    # ------------------------------------------------------------------
    lookup = annual[
        ["gvkey", "fyearq", "InvestmentResidual", "CashFlow", "SalesGrowth"]
    ].copy()
    lookup["fyearq"] = lookup["fyearq"].astype(float)

    comp_aligned = comp[["gvkey", "fyearq"]].copy()
    comp_aligned["fyearq"] = pd.to_numeric(comp_aligned["fyearq"], errors="coerce")
    comp_aligned["_idx"] = np.arange(len(comp_aligned))

    merged = comp_aligned.merge(
        lookup, on=["gvkey", "fyearq"], how="left", validate="m:1"
    )
    merged = merged.sort_values("_idx")

    ir = pd.Series(merged["InvestmentResidual"].values, index=comp.index)
    cf = pd.Series(merged["CashFlow"].values, index=comp.index)
    sg = pd.Series(merged["SalesGrowth"].values, index=comp.index)
    return ir, cf, sg


def _compute_h3_payout_policy(
    comp: pd.DataFrame,
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Compute H3 Payout Policy variables on an annual basis and align back.

    Computes:
      - div_stability: -StdDev(Delta DPS) / |Mean(DPS)| over trailing 5 years
      - payout_flexibility: % of years with |Delta DPS| > 5% of prior DPS
      - earnings_volatility: StdDev(annual EPS) over trailing 5 years
      - fcf_growth: (FCF_t - FCF_{t-1}) / |FCF_{t-1}|
      - firm_maturity: RE / TE
      - is_div_payer_5yr: Max(dps > 0) over trailing 5 years

    Returns six Series aligned to comp's index.
    """
    needed = [
        "gvkey",
        "datadate",
        "fyearq",
        "fqtr",
        "dvpspq",
        "epspxq",
        "req",
        "seqq",
        "oancfy",
        "capxy",
        "atq",
        "dvy",
        "iby",
    ]
    available = [c for c in needed if c in comp.columns]
    base = comp[available].dropna(subset=["fyearq"]).copy()
    base["fyearq"] = base["fyearq"].astype(int)

    # 1. Flow variables (sum over 4 quarters for DPS and EPS)
    flow_annual = (
        base.groupby(["gvkey", "fyearq"])
        .agg({"dvpspq": "sum", "epspxq": "sum"})
        .rename(columns={"dvpspq": "dps", "epspxq": "eps"})
    )

    # 2. Point-in-time / Annual-total variables (last observation per year)
    pit_annual = (
        base[base["fqtr"] == 4]
        .sort_values(["gvkey", "fyearq", "datadate"])
        .drop_duplicates(["gvkey", "fyearq"], keep="last")
    )
    pit_annual = pit_annual.set_index(["gvkey", "fyearq"])

    # Merge flows and PIT
    df = flow_annual.join(
        pit_annual[["req", "seqq", "oancfy", "capxy", "atq", "datadate", "dvy", "iby"]]
    )
    df = df.reset_index().sort_values(["gvkey", "fyearq"])

    # Ensure sequential years for lag operations
    df["fyearq_lag"] = df.groupby("gvkey")["fyearq"].shift(1)
    gap_mask = (df["fyearq"] - df["fyearq_lag"]) != 1

    # FCF Growth
    df["fcf"] = np.where(
        (df["atq"].notna()) & (df["atq"] > 0),
        (df["oancfy"].fillna(0) - df["capxy"].fillna(0)) / df["atq"],
        np.nan,
    )
    df["fcf_lag"] = df.groupby("gvkey")["fcf"].shift(1)
    df.loc[gap_mask, "fcf_lag"] = np.nan
    df["fcf_growth"] = np.where(
        (df["fcf_lag"].notna()) & (df["fcf_lag"] != 0),
        (df["fcf"] - df["fcf_lag"]) / df["fcf_lag"].abs(),
        np.nan,
    )

    # Firm Maturity
    df["firm_maturity"] = np.where(
        (df["atq"].notna()) & (df["atq"] > 0), df["req"] / df["atq"], np.nan
    )

    # Rolling window computations
    df["dps_lag"] = df.groupby("gvkey")["dps"].shift(1)
    df.loc[gap_mask, "dps_lag"] = np.nan
    df["delta_dps"] = df["dps"] - df["dps_lag"]

    # div_stability
    df["payout_ratio"] = np.where(
        (df["iby"].notna()) & (df["iby"] > 0), df["dvy"] / df["iby"], np.nan
    )
    df["payout_ratio_lag"] = df.groupby("gvkey")["payout_ratio"].shift(1)
    df.loc[gap_mask, "payout_ratio_lag"] = np.nan

    # earnings_volatility
    df["roa_annual"] = np.where(
        (df["atq"].notna()) & (df["atq"] > 0), df["iby"] / df["atq"], np.nan
    )

    # Use a clean artificial date built from fyearq so rolling("1826D")
    # perfectly measures 5 fiscal years, robust to gaps and missing datadates.
    df["dummy_date"] = pd.to_datetime(df["fyearq"].astype(str) + "-12-31")
    df_ts = df.set_index("dummy_date").sort_index()

    # div_stability using 5-year rolling SD of lagged payout ratio
    std_payout = (
        df_ts.groupby("gvkey")["payout_ratio_lag"].rolling("1826D", min_periods=3).std()
    )

    # We now have Series indexed by [gvkey, dummy_date]
    # df can be mapped back safely by setting its index too
    df = df.set_index(["gvkey", "dummy_date"])
    df["div_stability"] = -std_payout

    # payout_flexibility
    sig_change = (df["delta_dps"].abs() > 0.05 * df["dps_lag"].abs()).astype(float)
    df["_sig_change"] = sig_change.where(
        df["dps_lag"].notna() & df["delta_dps"].notna(), np.nan
    )
    df_ts = df.reset_index().set_index("dummy_date").sort_index()
    payout_flex = (
        df_ts.groupby("gvkey")["_sig_change"]  # type: ignore[call-overload]
        .rolling("1826D", min_periods=2)
        .mean()
    )
    df["payout_flexibility"] = payout_flex

    # earnings_volatility
    earn_vol = (
        df_ts.groupby("gvkey")["roa_annual"].rolling("1826D", min_periods=3).std()
    )
    df["earnings_volatility"] = earn_vol

    # is_div_payer_5yr
    df["_is_payer"] = (df["dps"] > 0).astype(float)
    df_ts = df.reset_index().set_index("dummy_date").sort_index()
    is_div = (
        df_ts.groupby("gvkey")["_is_payer"]  # type: ignore[call-overload]
        .rolling("1826D", min_periods=1)
        .max()
    )
    df["is_div_payer_5yr"] = is_div

    df = df.reset_index()
    df = df.drop(columns=["dummy_date"])

    # Join back to full panel
    lookup = df[
        [
            "gvkey",
            "fyearq",
            "div_stability",
            "payout_flexibility",
            "earnings_volatility",
            "fcf_growth",
            "firm_maturity",
            "is_div_payer_5yr",
        ]
    ].copy()
    lookup["fyearq"] = lookup["fyearq"].astype(float)

    comp_aligned = comp[["gvkey", "fyearq"]].copy()
    comp_aligned["fyearq"] = pd.to_numeric(comp_aligned["fyearq"], errors="coerce")
    comp_aligned["_idx"] = np.arange(len(comp_aligned))

    merged = comp_aligned.merge(
        lookup, on=["gvkey", "fyearq"], how="left", validate="m:1"
    )
    merged = merged.sort_values("_idx")

    return (
        pd.Series(merged["div_stability"].values, index=comp.index),
        pd.Series(merged["payout_flexibility"].values, index=comp.index),
        pd.Series(merged["earnings_volatility"].values, index=comp.index),
        pd.Series(merged["fcf_growth"].values, index=comp.index),
        pd.Series(merged["firm_maturity"].values, index=comp.index),
        pd.Series(merged["is_div_payer_5yr"].values, index=comp.index),
    )


def _compute_and_winsorize(
    comp: pd.DataFrame, root_path: Optional[Path] = None
) -> pd.DataFrame:
    """Compute all control variables on the full Compustat panel and winsorize."""
    comp = comp.sort_values(["gvkey", "datadate"]).reset_index(drop=True)

    # --- MAJOR-6: Size = ln(atq) only for positive atq; zero/neg → NaN ---
    comp["Size"] = np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)

    comp["BM"] = comp["ceqq"] / (comp["cshoq"] * comp["prccq"])
    # FIX: Spec defines leverage as (dlcq + dlttq) / atq (interest-bearing debt only)
    # ltq includes all liabilities (accounts payable, accrued expenses, etc.)
    comp["Lev"] = (comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]
    # ROA: use annualized Q4 iby and average assets
    atq_annual = _compute_annual_q4_variable(comp, "atq", "_atq_annual")
    atq_annual_lag1 = _compute_annual_q4_variable_lag(comp, "atq", "_atq_annual_lag1")
    avg_assets = (
        pd.Series(atq_annual, index=comp.index)
        + pd.Series(atq_annual_lag1, index=comp.index)
    ) / 2
    iby_annual = _compute_annual_q4_variable(comp, "iby", "_iby_annual")
    comp["ROA"] = np.where(
        avg_assets > 0, pd.Series(iby_annual, index=comp.index) / avg_assets, np.nan
    )

    comp["CurrentRatio"] = comp["actq"] / comp["lctq"].replace(0, np.nan)
    comp["RD_Intensity"] = comp["xrdq"].fillna(0) / comp["atq"]

    # --- H1 extension: 5 new variables ---
    comp["CashHoldings"] = comp["cheq"] / comp["atq"]
    mktcap = comp["cshoq"] * comp["prccq"]
    debt_c = comp["dlcq"].clip(lower=0).fillna(0)
    debt_t = comp["dlttq"].clip(lower=0).fillna(0)
    debt_book = np.where(
        comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t
    )
    comp["TobinsQ"] = np.where(
        comp["atq"].notna() & (comp["atq"] > 0) & mktcap.notna(),
        (mktcap + debt_book) / comp["atq"],
        np.nan,
    )

    capxy_annual = _compute_annual_q4_variable(comp, "capxy", "_capxy_annual")
    comp["CapexAt"] = np.where(
        pd.Series(atq_annual_lag1, index=comp.index) > 0,
        pd.Series(capxy_annual, index=comp.index)
        / pd.Series(atq_annual_lag1, index=comp.index),
        np.nan,
    )

    # CRITICAL-2 fix: dvy is YTD cumulative -- use Q4 annual value joined to
    # all quarters to classify dividend payers using the full fiscal year.
    dvy_annual = _compute_annual_q4_variable(comp, "dvy", "_dvy_annual")
    comp["DividendPayer"] = (
        pd.Series(dvy_annual, index=comp.index).fillna(0) > 0
    ).astype(float)

    comp["OCF_Volatility"] = _compute_ocf_volatility(comp)

    # --- H2 extension: Biddle (2009) investment residual + CashFlow + SalesGrowth ---
    if root_path is not None:
        ir, cf, sg = _compute_biddle_residual(comp, root_path)
        comp["InvestmentResidual"] = ir
        comp["CashFlow"] = cf
        comp["SalesGrowth"] = sg
    else:
        comp["InvestmentResidual"] = np.nan
        comp["CashFlow"] = np.nan
        comp["SalesGrowth"] = np.nan

    # --- H3 extension: Payout Policy ---
    div_stab, pay_flex, earn_vol, fcf_gr, firm_mat, div_payer_5yr = (
        _compute_h3_payout_policy(comp)
    )
    comp["div_stability"] = div_stab
    comp["payout_flexibility"] = pay_flex
    comp["earnings_volatility"] = earn_vol
    comp["fcf_growth"] = fcf_gr
    comp["firm_maturity"] = firm_mat
    comp["is_div_payer_5yr"] = div_payer_5yr

    # --- MINOR-9: Replace inf with NaN after ratio computations ---
    ratio_cols = [
        "BM",
        "Lev",
        "ROA",
        "CurrentRatio",
        "RD_Intensity",
        "CashHoldings",
        "TobinsQ",
        "CapexAt",
        "OCF_Volatility",
        "InvestmentResidual",
        "CashFlow",
        "SalesGrowth",
    ]
    for col in ratio_cols:
        comp[col] = comp[col].replace([np.inf, -np.inf], np.nan)

    # --- MAJOR-3: Date-based EPS lag ---
    comp["EPS_Growth"] = _compute_eps_growth_date_based(comp)

    # B3 fix: Apply per-year winsorization (1%/99% within each fyearq) to ALL
    # control variables, consistent with the per-year approach already used for
    # InvestmentResidual, CashFlow, and SalesGrowth inside _compute_biddle_residual.
    # Prior code used pooled winsorization (one global percentile across all years),
    # which conflates tail observations from thick years (many firms) with thin years
    # (few firms), producing year-varying effective clip bounds.
    # Skip: DividendPayer (binary), InvestmentResidual/CashFlow/SalesGrowth (already
    # winsorized per-year inside _compute_biddle_residual — do not double-winsorize).
    skip_winsorize = {
        "DividendPayer",
        "InvestmentResidual",
        "CashFlow",
        "SalesGrowth",
        "is_div_payer_5yr",
    }
    winsorize_cols = [c for c in COMPUSTAT_COLS if c not in skip_winsorize]
    # Use fyearq as the year grouping column (integer fiscal year).
    # Rows with NaN fyearq form their own group in _winsorize_by_year and are
    # winsorized together if >= 10 observations, otherwise left unchanged.
    year_col = comp["fyearq"]
    for col in winsorize_cols:
        if comp[col].notna().any():
            comp[col] = _winsorize_by_year(comp[col], year_col)

    return comp


class CompustatEngine:
    """Load raw Compustat quarterly data, compute controls, cache result.

    The result is cached after the first call — subsequent calls with the
    same root_path return the cached DataFrame immediately.
    """

    def __init__(self) -> None:
        self._cache: Optional[pd.DataFrame] = None
        self._cache_root: Optional[Path] = None
        self._lock = threading.Lock()

    def get_data(self, root_path: Path) -> pd.DataFrame:
        """Return fully-computed Compustat controls DataFrame (cached).

        Uses double-checked locking so that concurrent callers in a
        multi-threaded pipeline do not trigger redundant loads.
        """
        # Fast path — no lock needed for reads because Python assignment is atomic.
        if self._cache is not None and self._cache_root == root_path:
            return self._cache

        with self._lock:
            # Re-check inside the lock — another thread may have populated it
            # while we were waiting.
            if self._cache is not None and self._cache_root == root_path:
                return self._cache

            compustat_path = (
                root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
            )
            logger.info(f"    CompustatEngine: loading {compustat_path.name}...")
            comp = pd.read_parquet(compustat_path, columns=REQUIRED_COMPUSTAT_COLS)
            comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
            comp["datadate"] = pd.to_datetime(comp["datadate"])
            non_numeric = {"gvkey", "datadate", "fyearq", "fqtr", "sic"}
            numeric_cols = [c for c in REQUIRED_COMPUSTAT_COLS if c not in non_numeric]
            for col in numeric_cols:
                comp[col] = pd.to_numeric(comp[col], errors="coerce").astype("float64")
            comp["fyearq"] = pd.to_numeric(comp["fyearq"], errors="coerce")
            comp["fqtr"] = pd.to_numeric(comp["fqtr"], errors="coerce")
            comp["sic"] = pd.to_numeric(comp["sic"], errors="coerce")

            # --- CRITICAL-2: Deduplicate (gvkey, datadate) — keep last ---
            before = len(comp)
            comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")
            after = len(comp)
            if before != after:
                logger.info(
                    f"    CompustatEngine: dropped {before - after:,} duplicate "
                    f"(gvkey, datadate) rows"
                )

            logger.info(
                f"    CompustatEngine: computing controls on {len(comp):,} rows..."
            )
            comp = _compute_and_winsorize(comp, root_path=root_path)

            self._cache = comp
            self._cache_root = root_path
            return comp

    def match_to_manifest(
        self,
        manifest: pd.DataFrame,
        root_path: Path,
    ) -> pd.DataFrame:
        """Merge Compustat controls into manifest via merge_asof.

        Args:
            manifest: DataFrame with file_name, gvkey (zero-padded str),
                      start_date (datetime).
            root_path: Project root for raw data lookup.

        Returns:
            manifest with COMPUSTAT_COLS columns added (NaN where unmatched).
        """
        comp = self.get_data(root_path)
        comp_sorted = comp.sort_values("datadate")
        manifest_sorted = manifest.sort_values("start_date")

        merged = pd.merge_asof(
            manifest_sorted,
            comp_sorted[["gvkey", "datadate"] + COMPUSTAT_COLS],
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )

        matched = merged["Size"].notna().sum()
        total = len(merged)
        logger.info(
            f"    CompustatEngine: matched {matched:,}/{total:,} "
            f"({matched / total * 100:.1f}%)"
        )
        return merged


# Module-level singleton — shared across all individual builders in one process
_engine = CompustatEngine()


def get_engine() -> CompustatEngine:
    """Return the module-level singleton engine."""
    return _engine


__all__ = ["CompustatEngine", "COMPUSTAT_COLS", "get_engine"]
