"""Chen restatement treatment builder with 3-variant classifier (Phase 1C Task C2).

Per Sina Q1 lock 2026-05-09: 3 classifier variants for IRREG (Hennes 2008
GAO data not licensed; AA Audit Analytics WRDS substitute):
    Variant A: IRREG = (res_fraud == 1)
    Variant B: IRREG = (res_fraud == 1) OR (res_sec_investigation == 1)
    Variant C: Variant B OR (res_regulatory_investigation == 1)

v2 audit M0b post-bridge expected counts: A=89 / B=311 / C=315 (vs Chen's n=270).
Variant B closest; sensitivity-table approach preserves all 3 per Sina lock.

Treatment construction per spec C2 verbatim:
    POST_{i,t} = 1 after restatement, 0 before
    Year 0 (announcement year) EXCLUDED
    Window: [-3, -1] pre vs [+1, +3] post

v2 audit m6 tie-break: sort by (gvkey, event_date, restatement_notification_key)
ascending; keep='first' for "subsequent restatements" exclusion per spec Table 1
Panel A "-396 Subsequent restatements (keep first only)".

Sample:
- Reads Task C0 bridge output (gvkey-mapped events)
- SIC excl 6000-6999 + 4900-4999 per spec C1 verbatim (via SIC join)
- Industry classification via Task C1 FF48 (used for downstream PSM industry constraint)

Output (per gvkey × event_year):
    gvkey, event_year, IRREG, classifier_variant, sic_code_at_event, ff48_at_event,
    pre_window_start_fyear, pre_window_end_fyear,
    post_window_start_fyear, post_window_end_fyear
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Literal

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from .chen_aa_to_gvkey_bridge import ChenAAtoGvkeyBridgeBuilder
from .ff48_industry_classifier import FF48IndustryClassifierBuilder


ClassifierVariant = Literal["A", "B", "C"]


def _compute_irreg(df: pd.DataFrame, variant: ClassifierVariant) -> pd.Series:
    """Compute IRREG flag per Sina Q1-locked variant."""
    fraud = df["res_fraud"].fillna(0).astype(int)
    sec = df["res_sec_investigation"].fillna(0).astype(int)
    reg = df["res_regulatory_investigation"].fillna(0).astype(int)
    if variant == "A":
        return (fraud == 1).astype(int)
    elif variant == "B":
        return ((fraud == 1) | (sec == 1)).astype(int)
    elif variant == "C":
        return ((fraud == 1) | (sec == 1) | (reg == 1)).astype(int)
    else:
        raise ValueError(f"Unknown classifier variant: {variant}")


class ChenRestatementTreatmentBuilder(VariableBuilder):
    """Build (gvkey, event_year, IRREG, ...) panel for Chen DiD.

    Args:
        config: dict with optional key 'classifier_variant' in {'A', 'B', 'C'}.
                Defaults to 'B' (post-bridge expected primary winner per audit M0b).
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.classifier_variant: ClassifierVariant = (config or {}).get("classifier_variant", "B")
        self.column = "IRREG"

    def build(self, years: range, root_path: Path) -> VariableResult:
        # Load bridge output (Task C0)
        bridge = ChenAAtoGvkeyBridgeBuilder().build(years=years, root_path=root_path).data

        # Industry filter via SIC code at event (Chen spec C1: excl SIC 6000-6999 + 4900-4999)
        bridge = bridge.dropna(subset=["sic_code_fkey"]).copy()
        bridge["sic_code_fkey"] = pd.to_numeric(bridge["sic_code_fkey"], errors="coerce").astype("Int64")
        bridge = bridge[
            ~(bridge["sic_code_fkey"].between(6000, 6999)) &
            ~(bridge["sic_code_fkey"].between(4900, 4999))
        ].copy()

        # Compute IRREG flag per variant
        bridge["IRREG"] = _compute_irreg(bridge, self.classifier_variant)

        # v2 audit m6 tie-break: sort + keep first per gvkey ("Subsequent restatements -396")
        bridge = bridge.sort_values(
            ["gvkey", "event_date", "restatement_notification_key"], kind="stable"
        )
        bridge = bridge.drop_duplicates(subset=["gvkey"], keep="first")

        # Restrict to Chen window 1997 - June 2006 per spec C1
        bridge["event_year"] = bridge["event_date"].dt.year.astype(int)
        bridge = bridge[bridge["event_year"].between(1997, 2006)].copy()
        # Exclude Jul 2006 - Dec 2006 events (Chen window ends June 2006)
        bridge = bridge[
            ~((bridge["event_year"] == 2006) & (bridge["event_date"].dt.month > 6))
        ].copy()

        # Merge FF48 industry at event year for downstream PSM
        ff48 = FF48IndustryClassifierBuilder().build(years=years, root_path=root_path).data
        bridge = bridge.merge(
            ff48[["gvkey", "fyear", "ff48_code"]].rename(columns={"fyear": "event_year"}),
            on=["gvkey", "event_year"], how="left",
        )

        # Window definition per spec C2 verbatim ([-3,-1] pre vs [+1,+3] post; year 0 excluded)
        bridge["pre_window_start_fyear"] = bridge["event_year"] - 3
        bridge["pre_window_end_fyear"] = bridge["event_year"] - 1
        bridge["post_window_start_fyear"] = bridge["event_year"] + 1
        bridge["post_window_end_fyear"] = bridge["event_year"] + 3

        bridge["classifier_variant"] = self.classifier_variant
        bridge["sic_code_at_event"] = bridge["sic_code_fkey"]
        bridge["ff48_at_event"] = bridge["ff48_code"]

        out_cols = [
            "gvkey", "event_year", "event_date", "IRREG", "classifier_variant",
            "sic_code_at_event", "ff48_at_event",
            "pre_window_start_fyear", "pre_window_end_fyear",
            "post_window_start_fyear", "post_window_end_fyear",
        ]
        out_cols = [c for c in out_cols if c in bridge.columns]
        out = bridge[out_cols].reset_index(drop=True)

        n_total = len(out)
        n_irreg = int((out["IRREG"] == 1).sum())
        n_error = int((out["IRREG"] == 0).sum())

        valid = out["IRREG"]
        stats = VariableStats(
            name="IRREG",
            n=int(len(valid)),
            mean=float(valid.mean()),
            std=float(valid.std()),
            min=0, p25=0.0, median=0.0, p75=1.0, max=1,
            n_missing=0, pct_missing=0.0,
        )
        metadata: Dict[str, Any] = {
            "source": "Audit Analytics financial_restatements via chen_aa_to_gvkey_bridge",
            "classifier_variant": self.classifier_variant,
            "classifier_definition": {
                "A": "res_fraud == 1",
                "B": "(res_fraud == 1) OR (res_sec_investigation == 1)",
                "C": "Variant B OR (res_regulatory_investigation == 1)",
            }[self.classifier_variant],
            "v2_audit_m0b_expected_count": {"A": 89, "B": 311, "C": 315}[self.classifier_variant],
            "chen_paper_target_n": 270,
            "n_total_first_restatements": n_total,
            "n_irregularity": n_irreg,
            "n_error": n_error,
            "tie_break_order": "(gvkey, event_date, restatement_notification_key) ASC; keep first per audit m6",
            "industry_excl": "SIC 6000-6999 (financial) + 4900-4999 (utility) per spec C1",
            "window": "Chen window 1997 - June 2006",
            "post_window": "[+1, +3] relative to event_year (year 0 excluded per spec C2)",
            "pre_window": "[-3, -1] relative to event_year",
            "column": "IRREG",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
