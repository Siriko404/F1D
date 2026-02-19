"""Builder for Earnings Surprise Decile (SurpDec) variable.

Computes SurpDec directly from raw IBES data (inputs/tr_ibes/tr_ibes.parquet)
and the CRSP-Compustat CCM linktable (inputs/CRSPCompustat_CCM/).

Algorithm (mirrors legacy build_firm_controls.py):
  1. Filter IBES to EPS quarterly forecasts.
  2. Link IBES to gvkey via CUSIP -> CCM.
  3. For each call, find the IBES forecast within +/- 45 days of the call date
     whose STATPERS <= call start_date (most recent pre-call consensus).
  4. Compute raw surprise = ACTUAL - MEANEST.
  5. Within each calendar quarter, rank surprises into -5 to +5 scale
     (SurpDec): positive surprises 1..5, zero = 0, negatives -1..-5.

Returns a VariableResult whose .data contains: file_name, SurpDec.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


def _rank_surprises(group: pd.DataFrame) -> pd.Series:
    """Rank surprises within a quarter to -5..+5 scale."""
    surprises = group["surprise_raw"]
    ranks = pd.Series(np.nan, index=group.index, dtype=float)

    valid_mask = surprises.notna()
    if valid_mask.sum() < 5:
        return ranks

    pos_mask = surprises > 0
    zero_mask = surprises == 0
    neg_mask = surprises < 0

    if pos_mask.sum() > 0:
        pos_ranks = surprises[pos_mask].rank(ascending=False, pct=True)
        ranks.loc[pos_mask] = (5 - pos_ranks * 4).round().clip(1, 5)

    ranks.loc[zero_mask] = 0.0

    if neg_mask.sum() > 0:
        neg_ranks = surprises[neg_mask].abs().rank(ascending=True, pct=True)
        ranks.loc[neg_mask] = -(1 + neg_ranks * 4).round().clip(1, 5)

    return ranks


class EarningsSurpriseBuilder(VariableBuilder):
    """Build Earnings Surprise Decile (SurpDec) from raw IBES data.

    Computes from raw inputs:
        inputs/tr_ibes/tr_ibes.parquet
        inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet

    Returns a VariableResult whose .data contains: file_name, SurpDec.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        ibes_path = root_path / "inputs" / "tr_ibes" / "tr_ibes.parquet"
        ccm_path = (
            root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
        )

        manifest_dir = self._resolve_manifest_dir(root_path)
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        print(f"    EarningsSurpriseBuilder: loading manifest...")
        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        print(f"    EarningsSurpriseBuilder: loading IBES...")
        ibes = pd.read_parquet(
            ibes_path,
            columns=[
                "MEASURE",
                "FISCALP",
                "TICKER",
                "CUSIP",
                "FPEDATS",
                "STATPERS",
                "MEANEST",
                "ACTUAL",
            ],
        )
        ibes = ibes.loc[(ibes["MEASURE"] == "EPS") & (ibes["FISCALP"] == "QTR")].copy()
        ibes = ibes[["CUSIP", "FPEDATS", "STATPERS", "MEANEST", "ACTUAL"]].copy()
        ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"], errors="coerce")
        ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"], errors="coerce")
        ibes["surprise_raw"] = ibes["ACTUAL"] - ibes["MEANEST"]

        # Link IBES CUSIP -> gvkey via CCM
        print(f"    EarningsSurpriseBuilder: linking IBES to gvkey via CCM...")
        ccm = pd.read_parquet(ccm_path, columns=["cusip", "LPERMNO", "gvkey"])
        ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
        ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
        ccm_cusip = ccm[["cusip8", "gvkey"]].drop_duplicates().dropna()

        ibes["cusip8"] = ibes["CUSIP"].astype(str).str[:8]
        ibes_linked = ibes.merge(ccm_cusip, on="cusip8", how="inner")

        ibes_grouped = {gvkey: grp for gvkey, grp in ibes_linked.groupby("gvkey")}

        # Match each call to nearest IBES forecast
        results: List[Dict[str, Any]] = []
        matched = 0

        for _, row in manifest.iterrows():
            gvkey = row["gvkey"]
            call_date = row["start_date"]
            result: Dict[str, Any] = {
                "file_name": row["file_name"],
                "surprise_raw": np.nan,
            }

            if gvkey in ibes_grouped:
                firm_ibes = ibes_grouped[gvkey]
                mask = (
                    (firm_ibes["FPEDATS"] >= call_date - pd.Timedelta(days=45))
                    & (firm_ibes["FPEDATS"] <= call_date + pd.Timedelta(days=45))
                    & (firm_ibes["STATPERS"] <= call_date)
                )
                if mask.any():
                    result["surprise_raw"] = float(
                        firm_ibes.loc[mask].iloc[-1]["surprise_raw"]
                    )
                    matched += 1

            results.append(result)

        print(
            f"    EarningsSurpriseBuilder: matched {matched:,}/{len(manifest):,} "
            f"({matched / len(manifest) * 100:.1f}% if manifest non-empty)"
            if len(manifest) > 0
            else f"    EarningsSurpriseBuilder: empty manifest"
        )

        results_df = pd.DataFrame(results)

        # Compute SurpDec within quarter
        manifest_surp = manifest.merge(results_df, on="file_name", how="left")
        manifest_surp["call_quarter"] = manifest_surp["start_date"].dt.to_period("Q")
        manifest_surp["SurpDec"] = manifest_surp.groupby(
            "call_quarter", group_keys=False
        ).apply(_rank_surprises)

        data = manifest_surp[["file_name", "SurpDec"]].copy()
        stats = self.get_stats(data["SurpDec"], "SurpDec")

        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "source": str(ibes_path),
                "column": "SurpDec",
                "matched": matched,
                "total": len(manifest),
            },
        )

    def _resolve_manifest_dir(self, root_path: Path) -> Path:
        from f1d.shared.path_utils import get_latest_output_dir

        return get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )


__all__ = ["EarningsSurpriseBuilder"]
