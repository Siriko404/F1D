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


# Brexit DiD output window.
WINDOW_START_YQ = 20101
WINDOW_END_YQ = 20164

# Within-firm z-score base window (full IBES sample).
ZSCORE_START = pd.Timestamp("2000-01-01")
ZSCORE_END = pd.Timestamp("2025-12-31")


def _load_cusip_to_gvkey_map(root_path: Path) -> pd.Series:
    """Build CUSIP8 → gvkey lookup from CCM with primary or canonical links."""
    ccm_path = root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
    ccm = pd.read_parquet(ccm_path, columns=["cusip", "gvkey", "LINKPRIM", "LINKTYPE"])
    ccm = ccm[(ccm["LINKPRIM"] == "P") & (ccm["LINKTYPE"].isin(["LU", "LC"]))].copy()
    ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
    ccm["gvkey"] = ccm["gvkey"].astype(int).astype(str).str.zfill(6)
    ccm = ccm.dropna(subset=["cusip8", "gvkey"])
    ccm = ccm[ccm["cusip8"].str.match(r"^[A-Za-z0-9]{8}$")]
    # Keep first per cusip8 (most CUSIPs map to a single gvkey).
    return ccm.drop_duplicates(subset=["cusip8"], keep="first").set_index("cusip8")["gvkey"]


def _load_yearly_ibes_fpi6(year_file: Path, cusip_to_gvkey: pd.Series) -> Optional[pd.DataFrame]:
    """Load one yearly IBES file → filter MEASURE=EPS + FPI=6 → aggregate to (gvkey, fpedats)."""
    import pyarrow.compute as pc
    import pyarrow.dataset as ds

    cols = ["CUSIP", "ANALYS", "VALUE", "MEASURE", "FPI", "FPEDATS"]
    dataset = ds.dataset(year_file, format="parquet")
    available = dataset.schema.names
    load_cols = [c for c in cols if c in available]
    filt = (pc.field("MEASURE") == "EPS") & (pc.field("FPI") == "6")
    table = dataset.to_table(columns=load_cols, filter=filt)
    df = table.to_pandas()
    if len(df) == 0:
        return None

    df = df.dropna(subset=["CUSIP", "VALUE", "FPEDATS"])
    df["cusip8"] = df["CUSIP"].astype(str).str[:8]
    df = df[~df["cusip8"].isin(["00000000", "nan", "NaN", "None", ""])]
    df["gvkey"] = df["cusip8"].map(cusip_to_gvkey)
    df = df.dropna(subset=["gvkey"]).copy()
    df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
    df = df.dropna(subset=["VALUE"])
    df["fpedats"] = pd.to_datetime(df["FPEDATS"], errors="coerce")
    df = df.dropna(subset=["fpedats"])
    if len(df) == 0:
        return None

    # Aggregate to (gvkey, fpedats): mean of MEANEST across analysts.
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

        cusip_to_gvkey = _load_cusip_to_gvkey_map(root_path)
        logger.info(f"BrexitConsensusEPSBuilder: CUSIP-to-gvkey map: {len(cusip_to_gvkey):,} unique cusip8")

        ibes_dir = root_path / "inputs" / "tr_ibes"
        year_files = sorted(ibes_dir.glob("tr_ibes_*.parquet"))
        chunks: List[pd.DataFrame] = []
        for yf in year_files:
            year = int(yf.stem.split("_")[-1])
            if year < 2000 or year > 2025:
                continue
            chunk = _load_yearly_ibes_fpi6(yf, cusip_to_gvkey)
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
        out = out[["gvkey", "cal_yr_qtr", "consensus_eps_z"]]
        logger.info(f"  Brexit-window rows (gvkey, cal_yr_qtr): {len(out):,}")
        logger.info(f"  unique gvkeys with consensus EPS in Brexit window: {out['gvkey'].nunique():,}")

        stats = self.get_stats(out["consensus_eps_z"], "consensus_eps_z")
        metadata = {
            "source": "IBES Detail (FPI=6 FQ1) + within-firm z-score over 2000-2025",
            "n_rows_brexit_window": int(len(out)),
            "n_unique_gvkeys_brexit": int(out["gvkey"].nunique()),
            "lag_convention": "BUILDER emits contemporaneous value; runner applies 1Q-lag at panel-assembly",
            "column": "consensus_eps_z",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
