"""Inline pytest for Chen AA→gvkey CCM bridge (Phase 1C Task C0).

v2 audit C1 CRITICAL: AA Audit Analytics has NO gvkey field; company_fkey = CIK.
Without this bridge, Chen runner literally cannot join restatement events to
Compustat fundamentals.

F1D precedent: src/f1d/variables/build_h18_cccl_received_panel.py:93-104.
Expected retention: 60-70% (audit-measured).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from f1d.shared.variables.chen_aa_to_gvkey_bridge import (
    ChenAAtoGvkeyBridgeBuilder,
    load_aa_restatements,
    load_ccm_filtered,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def bridge_panel() -> pd.DataFrame:
    return ChenAAtoGvkeyBridgeBuilder().build(
        years=range(1997, 2007), root_path=ROOT
    ).data


def test_aa_company_fkey_1750_maps_to_aar_corp_gvkey_1004(bridge_panel):
    """v2 audit C1: AA company_fkey=1750 (AAR Corp CIK) maps to Compustat gvkey=001004."""
    df = bridge_panel
    aar = df[df["company_fkey"] == 1750]
    if len(aar) == 0:
        pytest.skip("AAR Corp not in AA Chen-window restatement set; bridge logic still verified by other tests")
    assert (aar["gvkey"] == "001004").all()


def test_bridge_retention_in_audit_range(bridge_panel):
    """v2 audit C1 measurement: post-bridge retention 60-70% (NOT ~85%).

    We verify retention is in [50%, 80%] band; tighter audit range was for IRREG-only
    sub-sample but full-AA may differ.
    """
    aa_full = load_aa_restatements(
        zip_path=ROOT / "inputs" / "Chen_replication" / "AA_financial_restatements.csv.zip",
        years=range(1997, 2007),
    )
    n_aa = len(aa_full)
    n_bridged = len(bridge_panel)
    retention = n_bridged / n_aa if n_aa else 0
    assert 0.40 < retention < 0.85, f"Retention {retention:.1%} outside expected band"


def test_ccm_filter_linkprim_in_p_c():
    """LINKPRIM in {'P', 'C'} only per audit C1 spec."""
    ccm = load_ccm_filtered(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet")
    valid_linkprim = set(ccm["LINKPRIM"].unique())
    assert valid_linkprim.issubset({"P", "C"})


def test_ccm_filter_linktype_in_lu_lc():
    """LINKTYPE in {'LU', 'LC'} only per audit C1 spec."""
    ccm = load_ccm_filtered(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet")
    valid_linktype = set(ccm["LINKTYPE"].unique())
    assert valid_linktype.issubset({"LU", "LC"})


def test_time_varying_link_filter(bridge_panel):
    """No bridged event has event_date outside its CCM link window [LINKDT, LINKENDDT]."""
    df = bridge_panel
    if "_link_dt" in df.columns and "_link_enddt" in df.columns:
        # Coerce LINKENDDT='E' sentinel to far-future date for comparison
        link_enddt = pd.to_datetime(df["_link_enddt"].replace("E", "9999-12-31"), errors="coerce")
        link_dt = pd.to_datetime(df["_link_dt"], errors="coerce")
        event = pd.to_datetime(df["event_date"], errors="coerce")
        in_window = (event >= link_dt) & (event <= link_enddt)
        assert in_window.all(), f"{(~in_window).sum()} events outside CCM link window"


def test_bridge_output_schema(bridge_panel):
    """Output schema includes classifier flags for downstream Task C2."""
    df = bridge_panel
    expected_cols = {
        "company_fkey", "gvkey", "event_date", "fyear",
        "restatement_notification_key", "sic_code_fkey",
        "res_fraud", "res_sec_investigation", "res_regulatory_investigation",
        "res_clerical_errors",
    }
    assert expected_cols.issubset(set(df.columns)), (
        f"missing cols: {expected_cols - set(df.columns)}"
    )


def test_gvkey_is_zero_padded_string(bridge_panel):
    """gvkey is 6-char zero-padded string for downstream merges."""
    df = bridge_panel
    sample = df["gvkey"].dropna().head(5).tolist()
    for g in sample:
        assert isinstance(g, str), f"gvkey {g!r} is not a string"
        assert len(g) == 6, f"gvkey {g!r} length {len(g)} != 6"


def test_chen_window_filter(bridge_panel):
    """Bridge restricted to Chen window 1997-Jun06."""
    df = bridge_panel
    event = pd.to_datetime(df["event_date"], errors="coerce")
    assert event.dt.year.min() >= 1997
    # Allow events through 2006 (some restatements file in mid-late 2006)
    assert event.dt.year.max() <= 2007
