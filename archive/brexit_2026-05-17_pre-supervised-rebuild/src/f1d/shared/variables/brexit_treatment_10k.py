"""Brexit 10-K treatment builder — H1.5.brexit_did design (Module #3).

Reads the durable cache produced by ``scripts/brexit/parse_10k_keywords.py``
and assigns the binary treatment dummy ``HIGH_10K`` per gvkey using the
Campello et al. 2022 JFQA Section IV.A.2 cutoff convention (verbatim spec
lines 159-160 of ``tmp/3did_replication_v2_2026_05_08.md``):

    HIGH_10K = 1   if total_count > 5      (Campello: 807 firms)
    HIGH_10K = 0   if total_count == 0     (Campello: 433 firms)
    HIGH_10K = NaN if 1 <= total_count <= 5 (excluded — binary contrast only)

The ETL stage already deduplicated to one filing per gvkey (latest by
filing_date per audit MINOR-5). This builder only reads + thresholds.

CAMPELLO REPRODUCTION GAP (evidence-based, advisor 2026-05-08).
F1D 9-keyword pure-tally on Compustat-mapped 2015 10-Ks produces HIGH_10K=2,847
(vs Campello 807) and HIGH_10K=0=261 (vs Campello 433). Diagnostic localization:

    full 9-keyword pure tally:                              2,847 firms (>5)
    drop 'uncertainty' + 'uncertain' from tally:              994 firms (>5)
    pure brexit/referendum/great-britain only:                  5 firms (>5)
    n_brexit = 0 across all 3,820 firms (CORRECT — 2015 10-Ks pre-date the
                Feb 2016 referendum announcement; "Brexit" rarely used yet).

The 2,847 vs 807 gap is NOT a "different universe" issue — both samples are
Compustat-mapped (LINKPRIM='P', LINKTYPE in {LU,LC} per audit MAJOR-5). The
likely mechanism is that Campello's "uncertainty" + "uncertain" matching had
an undisclosed constraint (context-windowed proximity to UK/Brexit, or
Item-scope restriction to risk-factors only) that my pure-9-keyword tally
does not implement. The published methodology (spec §1F + footnote 14) does
NOT describe such a constraint, so this builder follows verbatim spec.

WITHIN-FIRM SIGNAL PRESERVATION. While absolute counts differ from Campello,
the relative ranking of firms by Brexit exposure remains informative — firms
with multi-keyword presence in their 10-K disclose more UK/uncertainty
exposure than firms with zero entries. The DiD identification reads the
treatment-vs-control contrast within the panel, not the absolute count.

Output:
    outputs/variables/brexit_treatment_10k/<ts>/treatment_10k_per_firm.parquet
    schema: gvkey (zfill-6 str), total_count (int), HIGH_10K (float64)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from f1d.shared.path_utils import get_latest_output_dir

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


# Cutoff thresholds per spec §1F + Campello fn 14 verbatim.
HIGH_THRESHOLD = 5    # total_count > 5 → treated
ZERO_THRESHOLD = 0    # total_count == 0 → control
TREATMENT_COL = "HIGH_10K"

# ETL cache lives at this base path.
KEYWORD_CACHE_BASE = Path("outputs/intermediate/brexit_10k_keyword_counts")


def _assign_high_10k(total_count: pd.Series) -> pd.Series:
    """Per spec §1F: 1 if >5, 0 if =0, NaN otherwise."""
    high = pd.Series(np.nan, index=total_count.index)
    high[total_count > HIGH_THRESHOLD] = 1.0
    high[total_count == ZERO_THRESHOLD] = 0.0
    return high


class Brexit10KTreatmentBuilder(VariableBuilder):
    """Read parse_10k_keywords cache → HIGH_10K per gvkey.

    The ``years`` argument to ``build`` is IGNORED — the 10-K classifier is
    based on 2015 calendar-year filings only per spec §1F.
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = TREATMENT_COL

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years  # 2015 calendar-year filings only.

        cache_base = root_path / KEYWORD_CACHE_BASE
        latest = get_latest_output_dir(
            cache_base, required_file="keyword_counts_per_filing.parquet"
        )
        cache_path = latest / "keyword_counts_per_filing.parquet"
        logger.info(f"Brexit10KTreatmentBuilder: reading cache from {cache_path}")

        df = pd.read_parquet(cache_path, columns=["gvkey", "total_count", "filing_date", "filing_type"])
        # Defensive — ETL already deduplicated, but verify.
        n_pre = len(df)
        df = df.sort_values(["gvkey", "filing_date"], kind="stable").drop_duplicates(
            subset=["gvkey"], keep="last"
        ).reset_index(drop=True)
        n_post = len(df)
        if n_pre != n_post:
            logger.warning(
                f"  ETL cache had {n_pre - n_post} duplicate gvkey rows; deduped here as defense-in-depth."
            )

        df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
        df[TREATMENT_COL] = _assign_high_10k(df["total_count"])

        n_treated = int((df[TREATMENT_COL] == 1).sum())
        n_control = int((df[TREATMENT_COL] == 0).sum())
        n_intermediate = int(df[TREATMENT_COL].isna().sum())
        logger.info(
            f"  HIGH_10K=1 (>5): {n_treated:,}; HIGH_10K=0 (=0): {n_control:,}; "
            f"intermediate (1-5, dropped): {n_intermediate:,}"
        )

        out = df[["gvkey", "total_count", TREATMENT_COL]].copy()
        stats = self.get_stats(out[TREATMENT_COL], TREATMENT_COL)
        metadata = {
            "source": "Campello et al. 2022 JFQA Section IV.A.2 + footnote 14",
            "cache_input": str(cache_path),
            "n_total": int(len(out)),
            "n_treated_high_10k": n_treated,
            "n_control_zero_10k": n_control,
            "n_intermediate_dropped": n_intermediate,
            "high_threshold": HIGH_THRESHOLD,
            "zero_threshold": ZERO_THRESHOLD,
            "column": TREATMENT_COL,
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
