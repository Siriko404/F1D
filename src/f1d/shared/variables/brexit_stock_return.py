"""Brexit-verbatim stock-return builder — H1.5.brexit_did design.

Campello et al. (2022 JFQA) Table 1 note (verbatim): "STOCK_RETURNS are
defined as the quarterly buy-and-hold return." The paper is SILENT on the
data source and on whether the return includes dividends (grep-confirmed
2026-05-17: CRSP is named only for the βᵁᴷ exposure measure, eq-13, never
for this control). Sina decision 2026-05-17: use the CRSP daily stock file
(CRSP_DSF) quarterly buy-and-hold TOTAL return — CRSP ``RET`` is the
holding-period return INCLUDING dividends and is split/distribution
adjusted, which is the standard meaning of "buy-and-hold return".

    STOCK_RETURN_q(firm) = Π_{d in calendar quarter q} (1 + RET_d) − 1

PERMNO → gvkey via the CRSP/Compustat link (CCM, time-varying:
LINKPRIM ∈ {P,C}, LINKTYPE ∈ {LU,LC}, LINKDT ≤ quarter-end ≤ LINKENDDT).
1% winsorization within cal_yr_qtr (verbatim: "All variables are
winsorized at the 1% level."). The 1-quarter lag for eq-(14) is applied
by the panel runner; this builder emits the contemporaneous quarter value
(buffered back to 2009Q4 so the runner can lag at 2010Q1).

Output:
    outputs/variables/brexit_stock_return/<ts>/brexit_stock_return.parquet
    schema: gvkey (zfill-6), cal_yr_qtr (int YYYY*10+Q), brexit_stock_return
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


WINDOW_START_YQ = 20094  # 2009Q4 (buffer so the runner can 1Q-lag at 2010Q1)
WINDOW_END_YQ = 20164    # 2016Q4
COL_NAME = "brexit_stock_return"
WINSOR_PCT = 0.01

_FNAME_RE = re.compile(r"CRSP_DSF_(\d{4})_Q([1-4])\.parquet$", re.IGNORECASE)


def _winsorize_within(df: pd.DataFrame, col: str, group: str, pct: float = WINSOR_PCT) -> pd.DataFrame:
    """1% winsorization within each group (cal_yr_qtr) — matches sibling control builders."""
    def _w(s: pd.Series) -> pd.Series:
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        return s.clip(lower=lo, upper=hi)
    df = df.copy()
    df[col] = df.groupby(group, observed=True)[col].transform(_w)
    return df


def _qend(yq: int) -> pd.Timestamp:
    """Calendar quarter-end date for cal_yr_qtr int YYYY*10+Q."""
    yr, q = yq // 10, yq % 10
    return pd.Timestamp(yr, q * 3, 1) + pd.offsets.MonthEnd(0)


def _load_ccm_permno_map(root_path: Path) -> pd.DataFrame:
    """CCM PERMNO → gvkey, time-varying. LINKPRIM=P, LINKTYPE∈{LU,LC}."""
    ccm_path = root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
    ccm = pd.read_parquet(
        ccm_path, columns=["gvkey", "LPERMNO", "LINKPRIM", "LINKTYPE", "LINKDT", "LINKENDDT"]
    )
    ccm = ccm[ccm["LINKPRIM"].eq("P") & ccm["LINKTYPE"].isin(["LU", "LC"])].copy()
    ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce")
    ccm = ccm.dropna(subset=["LPERMNO"])
    ccm["LPERMNO"] = ccm["LPERMNO"].astype("int64")
    ccm["gvkey"] = ccm["gvkey"].astype(int).astype(str).str.zfill(6)
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(
        ccm["LINKENDDT"].astype(str).replace({"E": "2099-12-31"}), errors="coerce"
    )
    return ccm.dropna(subset=["gvkey", "LINKDT", "LINKENDDT"])[
        ["LPERMNO", "gvkey", "LINKDT", "LINKENDDT"]
    ]


def _map_permno_to_gvkey(qdf: pd.DataFrame, ccm: pd.DataFrame) -> pd.DataFrame:
    """Attach gvkey to (PERMNO, cal_yr_qtr) rows where LINKDT ≤ qend ≤ LINKENDDT."""
    qdf = qdf.copy()
    qdf["qend"] = qdf["cal_yr_qtr"].map(_qend)
    m = qdf.merge(ccm, left_on="PERMNO", right_on="LPERMNO", how="left")
    valid = (m["LINKDT"] <= m["qend"]) & (m["qend"] <= m["LINKENDDT"])
    m = m[valid].copy()
    # If a PERMNO has >1 valid link for a quarter, keep the earliest-started.
    m = m.sort_values("LINKDT").drop_duplicates(subset=["PERMNO", "cal_yr_qtr"], keep="first")
    return m[["gvkey", "cal_yr_qtr", COL_NAME]]


class BrexitStockReturnBuilder(VariableBuilder):
    """Campello-verbatim quarterly buy-and-hold TOTAL return (CRSP RET, div-incl)."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = COL_NAME

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years
        dsf_dir = root_path / "inputs" / "CRSP_DSF"
        files = []
        for p in sorted(dsf_dir.glob("CRSP_DSF_*.parquet")):
            mobj = _FNAME_RE.search(p.name)
            if not mobj:
                continue
            yq = int(mobj.group(1)) * 10 + int(mobj.group(2))
            if WINDOW_START_YQ <= yq <= WINDOW_END_YQ:
                files.append((yq, p))
        if not files:
            raise ValueError(f"No CRSP_DSF files in window under {dsf_dir}")
        logger.info(f"BrexitStockReturnBuilder: {len(files)} CRSP_DSF quarter files")

        rows = []
        for yq, p in files:
            d = pd.read_parquet(p, columns=["PERMNO", "date", "RET"])
            d["RET"] = pd.to_numeric(d["RET"], errors="coerce")
            # CRSP missing-return codes (e.g. -66/-77/-88/-99) and NaN: a daily
            # RET ≤ -1 (≤ -100%) is impossible for a real return → drop, keeps
            # compounding factors positive.
            d = d[d["RET"].notna() & (d["RET"] > -1.0)]
            d["PERMNO"] = pd.to_numeric(d["PERMNO"], errors="coerce")
            d = d.dropna(subset=["PERMNO"])
            d["PERMNO"] = d["PERMNO"].astype("int64")
            # Quarterly buy-and-hold: Π(1+RET) − 1 over the calendar quarter.
            g = d.groupby("PERMNO")["RET"].apply(lambda s: float(np.prod(1.0 + s.values) - 1.0))
            qd = g.reset_index().rename(columns={"RET": COL_NAME})
            qd["cal_yr_qtr"] = yq
            rows.append(qd)

        allq = pd.concat(rows, ignore_index=True)
        ccm = _load_ccm_permno_map(root_path)
        out = _map_permno_to_gvkey(allq, ccm)
        out = out.dropna(subset=[COL_NAME])
        out = out[np.isfinite(out[COL_NAME])]
        out = out.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
            subset=["gvkey", "cal_yr_qtr"], keep="last"
        ).reset_index(drop=True)
        out = _winsorize_within(out, COL_NAME, "cal_yr_qtr")
        out = out[["gvkey", "cal_yr_qtr", COL_NAME]].reset_index(drop=True)
        logger.info(f"  rows: {len(out):,}; gvkeys: {out['gvkey'].nunique():,}")

        stats = self.get_stats(out[COL_NAME], COL_NAME)
        metadata = {
            "source": "CRSP_DSF daily RET (holding-period return, dividend-inclusive, split-adj)",
            "formula": "quarterly buy-and-hold = prod(1+RET_daily) - 1 over calendar quarter",
            "permno_gvkey_link": "CCM time-varying LPERMNO (LINKPRIM∈{P,C}, LINKTYPE∈{LU,LC})",
            "winsorization": f"{WINSOR_PCT*100}% within cal_yr_qtr (verbatim: all variables winsorized at 1%)",
            "decision": "paper-silent on source/dividends; Sina 2026-05-17 = CRSP total return incl. dividends",
            "n_rows": int(len(out)),
            "n_unique_gvkeys": int(out["gvkey"].nunique()),
            "column": COL_NAME,
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
