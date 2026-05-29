"""Brexit consensus-EPS builder — H1.5.brexit_did design (Module #5).

Per Campello et al. 2022 JFQA Section II.D firm-control #6 verbatim:

    "1-quarter-ahead consensus EPS forecast"

mapped to IBES Detail conventions: FPI=6 (FQ1, the first FY-quarter-ahead).
Aggregation per (gvkey, fpedats) takes the MEAN of MEANEST across analysts;
MEANEST itself is already a per-analyst-EPS-forecast value (the IBES Detail
file is one row per analyst-estimate, so we re-aggregate to a single number
per firm-period).

Standardization (per ~/.claude/plans/tender-popping-origami.md plan-deviation
log + advisor recommendation, since Campello's 'standardized' wording is
ambiguous): within-firm z-score over the firm's full IBES sample 2000-2025.

    z_{i,t} = (mean_eps_{i,t} - mu_i) / sigma_i

The 1Q-lag at panel-assembly time (in the Brexit runner) is applied via
groupby('gvkey').shift(1) on cal_yr_qtr-sorted data, so this builder emits
the contemporaneous value labeled by its native cal_yr_qtr; the runner
performs the lag.

⚠ FLAG (resolve at eq-(14) panel assembly, NOT here — needs panel
context): output is keyed by `fpedats` (forecast-period-end, forward-
looking). A runner shift(1) then makes the period-t control = the
forecast for fiscal quarter (t−1), which DROPS the "1-quarter-AHEAD"
forward-looking property. Verbatim is ambiguous on whether Campello
wants this treated as an ordinary lagged control (shift) or the
forward-look kept (no runner shift). Decide when building the panel.

Output:
    outputs/variables/brexit_consensus_eps/<ts>/consensus_eps_per_firm_quarter.parquet
    schema: gvkey (zfill-6 str), cal_yr_qtr (int YYYY*10+Q), consensus_eps_z
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)

WINSOR_PCT = 0.01  # verbatim Table 1 note: "All variables are winsorized at the 1% level."


def _winsorize_within(df: pd.DataFrame, col: str, group: str, pct: float = WINSOR_PCT) -> pd.DataFrame:
    """1% winsorization within each group (cal_yr_qtr) — matches sibling control builders."""
    def _w(s: pd.Series) -> pd.Series:
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        return s.clip(lower=lo, upper=hi)
    df = df.copy()
    df[col] = df.groupby(group, observed=True)[col].transform(_w)
    return df


# Brexit DiD output window.
WINDOW_START_YQ = 20101
WINDOW_END_YQ = 20164

# Within-firm z-score base window (full IBES sample).
ZSCORE_START = pd.Timestamp("2000-01-01")
ZSCORE_END = pd.Timestamp("2025-12-31")


def _load_ccm_full(root_path: Path) -> pd.DataFrame:
    """Load CCM with LINKPRIM=P only + date-ranges for time-varying CUSIP→gvkey."""
    ccm_path = root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
    ccm = pd.read_parquet(ccm_path,
                          columns=["cusip", "tic", "gvkey", "LINKPRIM", "LINKTYPE",
                                   "LINKDT", "LINKENDDT"])
    ccm = ccm[ccm["LINKPRIM"].eq("P") & ccm["LINKTYPE"].isin(["LU", "LC"])].copy()
    ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
    ccm["gvkey"] = ccm["gvkey"].astype(int).astype(str).str.zfill(6)
    ccm["tic"] = ccm["tic"].astype(str).str.upper().str.strip()
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(
        ccm["LINKENDDT"].astype(str).replace({"E": "2099-12-31"}), errors="coerce"
    )
    ccm = ccm.dropna(subset=["gvkey", "LINKDT", "LINKENDDT"])
    return ccm


def _load_cusip_to_gvkey_map(root_path: Path) -> pd.DataFrame:
    """CUSIP8 + (LINKDT, LINKENDDT) → gvkey table for time-varying lookup."""
    ccm = _load_ccm_full(root_path)
    ccm = ccm.dropna(subset=["cusip8"])
    ccm = ccm[ccm["cusip8"].str.match(r"^[A-Za-z0-9]{8}$")]
    return ccm[["cusip8", "gvkey", "LINKDT", "LINKENDDT"]]


def _load_ticker_to_gvkey_map(root_path: Path) -> pd.DataFrame:
    """TICKER + (LINKDT, LINKENDDT) → gvkey table for time-varying lookup."""
    ccm = _load_ccm_full(root_path)
    ccm = ccm.dropna(subset=["tic"])
    return ccm[["tic", "gvkey", "LINKDT", "LINKENDDT"]]


def _timevar_lookup(df: pd.DataFrame, key_col: str, lookup: pd.DataFrame,
                    lookup_key: str, date_col: str = "fpedats") -> pd.Series:
    """Time-varying CCM lookup: match df[key_col] → gvkey where LINKDT ≤ df[date_col] ≤ LINKENDDT.

    Returns Series of gvkey aligned with df.index. If multiple matches per
    (key, date), keeps the first by LINKDT.
    """
    if key_col not in df.columns:
        return pd.Series(index=df.index, dtype="object")
    sub = df[[key_col, date_col]].copy()
    sub["_orig_idx"] = sub.index
    merged = sub.merge(lookup, left_on=key_col, right_on=lookup_key, how="left")
    valid = (merged["LINKDT"].isna()) | (
        (merged[date_col] >= merged["LINKDT"]) & (merged[date_col] <= merged["LINKENDDT"])
    )
    merged = merged[valid]
    merged = merged.sort_values("LINKDT").drop_duplicates(subset=["_orig_idx"], keep="first")
    out = pd.Series(index=df.index, dtype="object")
    out.loc[merged["_orig_idx"]] = merged["gvkey"].values
    return out


def _load_yearly_ibes_fpi6(
    year_file: Path,
    cusip_lookup: pd.DataFrame,
    ticker_lookup: pd.DataFrame,
) -> Optional[pd.DataFrame]:
    """Load one yearly IBES file → MEASURE=EPS + FPI=6 → aggregate to (gvkey, fpedats).

    Mapping chain (Sina decision 2026-05-14 'all 4 fixes'):
        1. CUSIP8 → gvkey (time-varying via LINKDT/LINKENDDT, LINKPRIM in {P,C})
        2. OFTIC ticker → gvkey (time-varying) — fallback for foreign CUSIPs
        3. TICKER (IBES internal) → gvkey (time-varying) — third fallback
    """
    import pyarrow.compute as pc
    import pyarrow.dataset as ds

    cols = ["CUSIP", "OFTIC", "TICKER", "ANALYS", "VALUE", "MEASURE", "FPI", "FPEDATS"]
    dataset = ds.dataset(year_file, format="parquet")
    available = dataset.schema.names
    load_cols = [c for c in cols if c in available]
    filt = (pc.field("MEASURE") == "EPS") & (pc.field("FPI") == "6")
    table = dataset.to_table(columns=load_cols, filter=filt)
    df = table.to_pandas()
    if len(df) == 0:
        return None

    df = df.dropna(subset=["VALUE", "FPEDATS"])
    df["fpedats"] = pd.to_datetime(df["FPEDATS"], errors="coerce")
    df = df.dropna(subset=["fpedats"])
    df["cusip8"] = df["CUSIP"].astype(str).str[:8]
    df["cusip8"] = df["cusip8"].where(~df["cusip8"].isin(["00000000", "nan", "NaN", "None", ""]))
    df["oftic_up"] = df["OFTIC"].astype(str).str.upper().str.strip() if "OFTIC" in df.columns else None
    df["ticker_up"] = df["TICKER"].astype(str).str.upper().str.strip() if "TICKER" in df.columns else None

    # Time-varying lookups for all 3 keys.
    g_cusip = _timevar_lookup(df, "cusip8", cusip_lookup, "cusip8")
    g_oftic = _timevar_lookup(df, "oftic_up", ticker_lookup, "tic")
    g_ticker = _timevar_lookup(df, "ticker_up", ticker_lookup, "tic")

    df["gvkey"] = g_cusip.fillna(g_oftic).fillna(g_ticker)
    df = df.dropna(subset=["gvkey"]).copy()
    df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
    df = df.dropna(subset=["VALUE"])
    if len(df) == 0:
        return None

    grouped = df.groupby(["gvkey", "fpedats"], observed=True)["VALUE"].mean().reset_index()
    grouped = grouped.rename(columns={"VALUE": "mean_eps"})
    return grouped


def _within_firm_zscore(df: pd.DataFrame) -> pd.DataFrame:
    """Compute z-score of mean_eps within each gvkey across full sample."""
    grp = df.groupby("gvkey")["mean_eps"]
    df["_mu"] = grp.transform("mean")
    df["_sd"] = grp.transform("std")
    # Avoid div-by-0: firms with sd=0 (rare, single observation or constant) → NaN.
    df["consensus_eps_z"] = np.where(
        (df["_sd"].notna()) & (df["_sd"] > 0),
        (df["mean_eps"] - df["_mu"]) / df["_sd"],
        np.nan,
    )
    return df.drop(columns=["_mu", "_sd"])


def _fpedats_to_cal_yr_qtr(d: pd.Timestamp) -> int:
    return int(d.year) * 10 + int((d.month - 1) // 3 + 1)


class BrexitConsensusEPSBuilder(VariableBuilder):
    """Build per-firm-quarter within-firm-z-scored 1Q-ahead consensus EPS forecast."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "consensus_eps_z"

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years  # window-fixed at Brexit panel; full IBES sample for z-score.

        cusip_lookup = _load_cusip_to_gvkey_map(root_path)
        ticker_lookup = _load_ticker_to_gvkey_map(root_path)
        logger.info(
            f"BrexitConsensusEPSBuilder: CUSIP CCM rows: {len(cusip_lookup):,}; "
            f"ticker CCM rows: {len(ticker_lookup):,} (time-varying lookups)"
        )

        ibes_dir = root_path / "inputs" / "tr_ibes"
        year_files = sorted(ibes_dir.glob("tr_ibes_*.parquet"))
        chunks: List[pd.DataFrame] = []
        for yf in year_files:
            year = int(yf.stem.split("_")[-1])
            if year < 2000 or year > 2025:
                continue
            chunk = _load_yearly_ibes_fpi6(yf, cusip_lookup, ticker_lookup)
            if chunk is not None and len(chunk) > 0:
                chunks.append(chunk)
                logger.info(f"  {yf.name}: {len(chunk):,} (gvkey, fpedats) aggregated rows")

        if not chunks:
            raise ValueError("No IBES FPI=6 EPS rows loaded.")

        df = pd.concat(chunks, ignore_index=True)
        # Dedup any (gvkey, fpedats) overlap between yearly files (rare, but defensive).
        df = df.sort_values(["gvkey", "fpedats"], kind="stable").drop_duplicates(
            subset=["gvkey", "fpedats"], keep="last"
        )
        logger.info(f"  total (gvkey, fpedats) rows after concat+dedup: {len(df):,}")

        # Within-firm z-score over full IBES sample.
        df = _within_firm_zscore(df)

        # Map fpedats → cal_yr_qtr.
        df["cal_yr_qtr"] = df["fpedats"].apply(_fpedats_to_cal_yr_qtr)

        # Restrict to Brexit panel window 2010Q1-2016Q4 for the output.
        out = df[(df["cal_yr_qtr"] >= WINDOW_START_YQ) & (df["cal_yr_qtr"] <= WINDOW_END_YQ)].copy()
        out = out[["gvkey", "cal_yr_qtr", "consensus_eps_z"]].dropna(subset=["consensus_eps_z"])
        # Verbatim Table 1 note: "All variables are winsorized at the 1%
        # level." Applied to the standardized variable within cal_yr_qtr
        # (same cross-sectional convention as the other firm controls).
        out = _winsorize_within(out, "consensus_eps_z", "cal_yr_qtr")
        logger.info(f"  Brexit-window rows (gvkey, cal_yr_qtr): {len(out):,}")
        logger.info(f"  unique gvkeys with consensus EPS in Brexit window: {out['gvkey'].nunique():,}")

        stats = self.get_stats(out["consensus_eps_z"], "consensus_eps_z")
        metadata = {
            "source": "IBES Detail (FPI=6 FQ1) mean 1Q-ahead EPS forecast",
            "standardization": "within-firm z-score over 2000-2025 (verbatim 'standardized' is undefined; operationalization — Sina-flagged)",
            "winsorization": f"{WINSOR_PCT*100}% within cal_yr_qtr (verbatim: all variables winsorized at 1%)",
            "n_rows_brexit_window": int(len(out)),
            "n_unique_gvkeys_brexit": int(out["gvkey"].nunique()),
            "lag_convention": "BUILDER emits contemporaneous value; runner applies 1Q-lag at panel-assembly",
            "column": "consensus_eps_z",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
