"""
================================================================================
Panel Building Utilities — Canonical Shared Helpers
================================================================================
ID: shared/variables/panel_utils
Purpose: Single canonical definitions for panel-building helper functions used
         across all Stage 3 panel builders and Stage 4 econometric scripts.

WHY THIS FILE EXISTS:
    Three helper functions were copy-pasted across 13+ panel builders with
    subtle divergences (missing dtype=object, two distinct attach_fyearq
    variants, latent dtype crashes). Centralising them here guarantees:
      - assign_industry_sample: consistent Finance/Utility/Main classification
        with enforced dtype=object (historical bug fix).
      - attach_fyearq: single merge strategy with explicit datetime coercion
        (fixes latent crash in h1/h2 when start_date is object dtype), unique
        file_name guard (prevents silent corruption), and a loud failure on
        catastrophic match rates.

USAGE:
    from f1d.shared.variables.panel_utils import assign_industry_sample, attach_fyearq

CANONICAL DEFINITIONS:
    assign_industry_sample  — FF12 code → Finance / Utility / Main
    attach_fyearq           — merge_asof call start_date → Compustat datadate
                              to attach fyearq (Compustat fiscal year)

Author: Thesis Author
Date: 2026-02-21
================================================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from f1d.shared.variables._compustat_engine import get_engine

logger = logging.getLogger(__name__)


def assign_industry_sample(ff12_code: pd.Series) -> pd.Series:
    """Map Fama-French 12-industry code to Finance / Utility / Main sample.

    This is the CANONICAL definition used by all panel builders and econometric
    scripts. Do not redefine locally.

    Classification:
        FF12 code 11 → "Finance"
        FF12 code  8 → "Utility"
        all others   → "Main"

    NaN ff12_code values are classified as "Main" (default behaviour via
    np.select, consistent with prior pipeline versions).

    Args:
        ff12_code: Series of integer (or float) FF12 industry codes.

    Returns:
        Series of strings {"Main", "Finance", "Utility"} with dtype=object,
        same index as ff12_code.
    """
    conditions = [ff12_code == 11, ff12_code == 8]
    choices = ["Finance", "Utility"]
    return pd.Series(
        np.select(conditions, choices, default="Main"),
        index=ff12_code.index,
        dtype=object,  # enforced: prevents dtype divergence (historical bug fix)
    )


def attach_fyearq(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Attach Compustat fiscal year (fyearq) to a call-level panel.

    Uses a backward merge_asof: for each call, finds the most recent Compustat
    reporting date (datadate) ≤ call start_date for the same gvkey, and takes
    its fyearq. This is the same matching strategy used by all Compustat
    variable builders.

    This is the CANONICAL implementation used by all Stage 3 panel builders.
    It replaces the 6–7 copy-pasted local variants that previously existed in
    h1, h2, h3, h4, h6, and h7.

    Design decisions (see refactor plan for full rationale):
        - Explicit datetime coercion (fixes latent crash in former h1/h2 variant
          when start_date has object dtype).
        - Map-back via set_index("file_name") preserves original panel row order
          (safe for downstream lead/lag operations that use idxmax).
        - file_name uniqueness is asserted before set_index to prevent silent
          duplicate-key corruption.
        - Raises ValueError if match rate < 80% (loud failure, not silent NaN).

    Args:
        panel:      Call-level DataFrame. Must contain:
                      - file_name  (str, UNIQUE per row)
                      - gvkey      (str, zero-padded)
                      - start_date (datetime64 or ISO string)
        root_path:  Project root Path, passed to CompustatEngine.get_data().

    Returns:
        panel (copy) with "fyearq" column added. Rows that cannot be matched
        receive NaN. Original row order is preserved.

    Raises:
        ValueError: if panel["file_name"] contains duplicates.
        ValueError: if fewer than 80% of panel rows match a Compustat fyearq.
    """
    if "fyearq" in panel.columns:
        return (
            panel.copy()
        )  # idempotent — return copy so caller mutations don't alias back

    # Guard: file_name must be unique — set_index would produce ambiguous Series
    # if duplicates exist, causing silent many-to-one mapping errors.
    dup_mask = panel[
        "file_name"
    ].duplicated()  # compute once; reused by .any() and .sum()
    if dup_mask.any():
        n_dup = dup_mask.sum()
        raise ValueError(
            f"attach_fyearq: panel has {n_dup:,} duplicate file_name values. "
            'The map-back via set_index("file_name") requires unique file_name. '
            "Deduplicate the panel before calling attach_fyearq."
        )

    engine = get_engine()
    comp = engine.get_data(root_path)

    fyearq_df = (
        comp[["gvkey", "datadate", "fyearq"]]
        .dropna(subset=["fyearq"])
        .sort_values("datadate")
        .copy()
    )

    panel_sorted = panel.sort_values("start_date").copy()

    # Explicit datetime coercion: fixes latent ValueError in former h1/h2 variant
    # where start_date (object dtype) was passed directly to merge_asof against
    # a datetime64 right key, causing a MergeError in pandas.
    panel_sorted["_start_date_dt"] = pd.to_datetime(
        panel_sorted["start_date"], errors="coerce"
    )
    # Rows where start_date cannot be parsed get NaN via .map() below (not dropped
    # from the returned panel — they are simply absent from merged and thus unmapped).
    panel_sorted_valid = panel_sorted.dropna(subset=["_start_date_dt"])

    merged = pd.merge_asof(
        panel_sorted_valid,
        fyearq_df,
        left_on="_start_date_dt",
        right_on="datadate",
        by="gvkey",
        direction="backward",
    )

    fyearq_map = merged.set_index("file_name")["fyearq"]

    panel = panel.copy()
    panel["fyearq"] = panel["file_name"].map(fyearq_map)

    n_total = len(panel)
    n_matched = panel["fyearq"].notna().sum()
    n_missing = n_total - n_matched

    if n_total > 0 and (n_matched / n_total) < 0.8:
        raise ValueError(
            f"attach_fyearq: only {n_matched:,}/{n_total:,} "
            f"({100 * n_matched / n_total:.1f}%) calls matched to a Compustat fyearq. "
            "Expected ≥80% match rate for a properly-linked Compustat panel. "
            "This indicates a likely data or merge-key problem (wrong gvkey format, "
            "mismatched date range, or empty Compustat cache). "
            "Investigate before proceeding."
        )

    if n_missing > 0:
        logger.warning(
            "attach_fyearq: %d/%d calls (%.1f%%) could not be matched to a fyearq "
            "(NaN assigned). Downstream lead/lag variables built on fyearq grouping "
            "will also be NaN for these calls.",
            n_missing,
            n_total,
            100 * n_missing / n_total,
        )
    else:
        logger.debug("attach_fyearq: all %d calls matched to fyearq.", n_total)

    return panel


def build_cal_yr_qtr_index(panel: pd.DataFrame) -> pd.DataFrame:
    """Create calendar year-quarter time index for Year-Quarter FE specifications.

    Derives calendar year and quarter from the call's start_date:
        cal_yr  = start_date.dt.year   (e.g., 2010)
        cal_qtr = start_date.dt.quarter (1-4)
        cal_yr_qtr = cal_yr * 10 + cal_qtr  (e.g., 20103 = 2010 Q3)

    Used as PanelOLS time index for Calendar Year-Quarter FE specs.
    No Compustat data needed — purely derived from call date.

    Args:
        panel: DataFrame with start_date column (datetime64 or ISO string).

    Returns:
        panel (copy) with cal_yr, cal_qtr, and cal_yr_qtr columns added.
        Rows with unparseable start_date get NaN.
    """
    panel = panel.copy()
    dt = pd.to_datetime(panel["start_date"], errors="coerce")
    panel["cal_yr"] = dt.dt.year.astype("Int64")
    panel["cal_qtr"] = dt.dt.quarter.astype("Int64")
    panel["cal_yr_qtr"] = (panel["cal_yr"] * 10 + panel["cal_qtr"]).astype("Int64")
    return panel
