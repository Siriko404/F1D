"""Chen AA Audit Analytics → gvkey CCM bridge (Phase 1C Task C0).

v2 audit C1 CRITICAL — without this bridge, Chen runner literally cannot join
restatement events to Compustat. AA's `company_fkey` is CIK (e.g., 1750 = AAR
Corp = Compustat cik=1750.0 = gvkey=001004), NOT gvkey directly.

CCM time-varying join:
    - LINKPRIM in {'P', 'C'} (primary links only)
    - LINKTYPE in {'LU', 'LC'} (unsearched + canonical)
    - event_date in [LINKDT, LINKENDDT]
    - LINKENDDT='E' sentinel = "ongoing" → treat as 9999-12-31

F1D precedent: `src/f1d/variables/build_h18_cccl_received_panel.py:93-104`
(CCCL — also CIK-keyed external dataset).

Expected retention: 60-70% (v2 audit-measured on AA × CCM × Chen-window).

Output schema:
    company_fkey, gvkey, event_date, fyear,
    restatement_notification_key, sic_code_fkey,
    res_fraud, res_sec_investigation, res_regulatory_investigation,
    res_clerical_errors

Used by:
- chen_restatement_treatment.py (Task C2; consumes 3 classifier-variant flags)
- run_h1_5_restatement_did.py (Task C7; merges gvkey-mapped events to Compustat)
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


CHEN_WINDOW_START = "1997-01-01"
CHEN_WINDOW_END = "2007-01-01"  # inclusive of all 2006 restatements per Chen Section 3.1

# AA columns we project (subset of 501-col schema)
AA_COLUMNS = [
    "company_fkey",                  # CIK (AA's firm key)
    "event_date",                    # restatement event date
    "file_date",                     # filing date (alternative key)
    "restatement_notification_key",  # for tie-break per audit m6
    "sic_code_fkey",                 # SIC at event
    "res_fraud",
    "res_sec_investigation",
    "res_regulatory_investigation",
    "res_clerical_errors",
]


def load_aa_restatements(
    zip_path: Path,
    years: Iterable[int] | None = None,
) -> pd.DataFrame:
    """Read AA restatements CSV from in-place zip per Sina's storage-constrained rule.

    Args:
        zip_path: path to AA_financial_restatements.csv.zip
        years: optional fyear filter (derived from event_date)

    Returns:
        DataFrame with AA_COLUMNS subset + parsed event_date + fyear.
    """
    if not zip_path.exists():
        raise FileNotFoundError(f"AA restatements zip not found at {zip_path}")

    with zipfile.ZipFile(zip_path) as zf:
        # Find CSV member
        members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not members:
            raise ValueError(f"No CSV in {zip_path}")
        csv_name = members[0]
        with zf.open(csv_name) as f:
            df = pd.read_csv(f, usecols=lambda c: c in AA_COLUMNS, low_memory=False)

    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df = df.dropna(subset=["event_date", "company_fkey"])
    df["company_fkey"] = pd.to_numeric(df["company_fkey"], errors="coerce")
    df = df.dropna(subset=["company_fkey"])
    df["company_fkey"] = df["company_fkey"].astype(int)
    df["fyear"] = df["event_date"].dt.year.astype("Int64")

    # Restrict to Chen window
    df = df[(df["event_date"] >= CHEN_WINDOW_START) & (df["event_date"] < CHEN_WINDOW_END)]

    if years is not None:
        years_set = set(years)
        df = df[df["fyear"].isin(years_set)]

    # Coerce classifier flags to numeric (some are 0/1, some 'Y'/'N', some NaN)
    for col in ["res_fraud", "res_sec_investigation", "res_regulatory_investigation", "res_clerical_errors"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df.reset_index(drop=True)


def load_ccm_filtered(ccm_path: Path) -> pd.DataFrame:
    """Read CCM with LINKPRIM/LINKTYPE filter + datetime parsing.

    Args:
        ccm_path: path to CRSPCompustat_CCM.parquet

    Returns:
        DataFrame with cols: gvkey (str 6-pad), cik (int), LINKPRIM, LINKTYPE,
        LINKDT (datetime), LINKENDDT (datetime; 'E' → 9999-12-31).
    """
    if not ccm_path.exists():
        raise FileNotFoundError(f"CCM parquet not found at {ccm_path}")

    ccm = pd.read_parquet(ccm_path, columns=["gvkey", "cik", "LINKPRIM", "LINKTYPE", "LINKDT", "LINKENDDT"])

    # Filter LINKPRIM in {P, C} + LINKTYPE in {LU, LC}
    ccm = ccm[ccm["LINKPRIM"].isin({"P", "C"})]
    ccm = ccm[ccm["LINKTYPE"].isin({"LU", "LC"})]

    # Drop rows missing CIK (firm not in CRSP-Compustat-merged universe)
    ccm = ccm.dropna(subset=["cik"]).copy()
    ccm["cik"] = ccm["cik"].astype(int)
    ccm["gvkey"] = ccm["gvkey"].astype(int).astype(str).str.zfill(6)

    # Parse LINKDT + LINKENDDT (sentinel 'E' = ongoing → far-future date that fits in datetime64[ns])
    # Note: datetime64[ns] max ≈ 2262-04-11; using 2099-12-31 to stay well within range
    LINK_OPEN_END = pd.Timestamp("2099-12-31")
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = ccm["LINKENDDT"].astype("string").replace("E", "2099-12-31")
    ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
    # If still NaT after parsing, treat as ongoing
    ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(LINK_OPEN_END)

    return ccm.reset_index(drop=True)


def _bridge_aa_to_ccm(aa: pd.DataFrame, ccm: pd.DataFrame) -> pd.DataFrame:
    """Time-varying CIK→gvkey join.

    For each AA row (cik, event_date), find CCM row(s) where:
        cik matches AND LINKDT <= event_date <= LINKENDDT
    If multiple matches, prefer LINKPRIM='P' over 'C' (CCM precedent).
    """
    # Inner join on cik
    merged = aa.merge(
        ccm.rename(columns={"cik": "company_fkey"}),
        on="company_fkey",
        how="inner",
    )
    # Time-varying filter
    merged = merged[
        (merged["event_date"] >= merged["LINKDT"]) &
        (merged["event_date"] <= merged["LINKENDDT"])
    ].copy()

    # Tie-break: prefer LINKPRIM='P' (priority) over 'C'; then earliest LINKDT
    merged["_linkprim_priority"] = merged["LINKPRIM"].map({"P": 0, "C": 1})
    merged = merged.sort_values(
        ["company_fkey", "event_date", "_linkprim_priority", "LINKDT"], kind="stable"
    )
    # First row per (company_fkey, event_date) wins
    merged = merged.drop_duplicates(subset=["company_fkey", "event_date"], keep="first")

    # Rename for downstream
    merged = merged.rename(columns={"LINKDT": "_link_dt", "LINKENDDT": "_link_enddt"})
    return merged.drop(columns=["_linkprim_priority"]).reset_index(drop=True)


class ChenAAtoGvkeyBridgeBuilder(VariableBuilder):
    """Build (company_fkey, gvkey, event_date, classifier-flags) bridge panel."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "gvkey"

    def build(self, years: range, root_path: Path) -> VariableResult:
        # Load AA restatements (Chen-window-filtered)
        zip_path = root_path / "inputs" / "Chen_replication" / "AA_financial_restatements.csv.zip"
        aa = load_aa_restatements(zip_path, years=years)
        n_aa = len(aa)

        # Load CCM with linktype filter
        ccm_path = root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
        ccm = load_ccm_filtered(ccm_path)

        # Time-varying join
        bridged = _bridge_aa_to_ccm(aa, ccm)
        n_bridged = len(bridged)
        retention = n_bridged / n_aa if n_aa else 0.0

        # Output projection
        out_cols = [
            "company_fkey", "gvkey", "event_date", "fyear",
            "restatement_notification_key", "sic_code_fkey",
            "res_fraud", "res_sec_investigation", "res_regulatory_investigation",
            "res_clerical_errors",
            "_link_dt", "_link_enddt",  # for diagnostics + tests
        ]
        out_cols = [c for c in out_cols if c in bridged.columns]
        out = bridged[out_cols].reset_index(drop=True)

        valid = out["gvkey"].dropna()
        stats = VariableStats(
            name="gvkey",
            n=int(len(valid)),
            mean=0.0, std=0.0, min=0.0, p25=0.0, median=0.0, p75=0.0, max=0.0,
            n_missing=int(out["gvkey"].isna().sum()),
            pct_missing=float(out["gvkey"].isna().mean()),
        )
        metadata: Dict[str, Any] = {
            "source": "Audit Analytics financial_restatements WRDS pull bridged via CRSP-Compustat-Merged",
            "ccm_path": str(ccm_path),
            "aa_zip_path": str(zip_path),
            "ccm_filter": "LINKPRIM in {P,C}, LINKTYPE in {LU,LC}",
            "time_varying_join": "event_date in [LINKDT, LINKENDDT]; LINKENDDT='E' → 9999-12-31",
            "n_aa_rows_in_window": int(n_aa),
            "n_bridged_rows": int(n_bridged),
            "retention_pct": float(retention * 100),
            "audit_expected_retention_pct": "60-70%",  # from v2 audit C1
            "f1d_precedent": "src/f1d/variables/build_h18_cccl_received_panel.py:93-104",
            "column": "gvkey",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
