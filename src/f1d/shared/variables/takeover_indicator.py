"""Builder for takeover event indicators from SDC M&A data.

Reads inputs/SDC/sdc-ma-merged.parquet and returns a firm-level DataFrame
with takeover classification columns. Returns one row per gvkey (firm),
not per file_name — this builder operates at firm granularity.

Architecture note: Unlike call-level builders (which return file_name + column),
this builder returns gvkey + takeover columns. The takeover panel builder
(build_takeover_panel.py) aggregates calls to firm-year and then joins these
columns on gvkey.

Takeover classification:
  - Takeover = 1 if firm received any bid (Completed, Withdrawn, or Pending)
               with a US public target in the sample period.
  - Takeover_Date = Date Announced of first bid
  - Takeover_Attitude = Deal Attitude of the first bid received
  - Takeover_Type:
      'Uninvited' if attitude is 'Hostile' or 'Unsolicited'
      'Friendly'  if attitude is 'Friendly' or 'Neutral'
      'Unknown'   otherwise (No Applicable, etc.)

Linkage: manifest CUSIP (9-char) → SDC 'Target 6-digit CUSIP' (first 6 chars).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


class TakeoverIndicatorBuilder(VariableBuilder):
    """Build firm-level takeover indicators from SDC M&A data.

    Source: inputs/SDC/sdc-ma-merged.parquet
    Linkage: manifest CUSIP[:6] == SDC 'Target 6-digit CUSIP'

    Returns a DataFrame with columns:
        gvkey, Takeover, Takeover_Type, Takeover_Date, Takeover_Attitude

    One row per gvkey. Firms not in SDC or not targeted get Takeover=0.
    """

    SDC_FILE = "sdc-ma-merged.parquet"

    # SDC Deal Attitude → Takeover_Type classification
    UNINVITED_ATTITUDES = {"Hostile", "Unsolicited"}
    FRIENDLY_ATTITUDES = {"Friendly", "Neutral"}

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.year_start: int = config.get("year_start", 2002)
        self.year_end: int = config.get("year_end", 2018)

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build firm-level takeover indicators.

        Args:
            years: Range of sample years (used to filter SDC by announcement date)
            root_path: Project root path

        Returns:
            VariableResult with firm-level data (gvkey + takeover columns).
            Note: data has gvkey as key, not file_name.
        """
        from f1d.shared.path_utils import get_latest_output_dir

        year_start = min(years)
        year_end = max(years)

        # Load manifest to get gvkey ↔ CUSIP mapping
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest = pd.read_parquet(
            manifest_dir / "master_sample_manifest.parquet",
            columns=["gvkey", "cusip"],
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["cusip6"] = manifest["cusip"].astype(str).str[:6]

        # Unique gvkey → cusip6 mapping (one cusip per gvkey)
        firm_cusip = (
            manifest[["gvkey", "cusip6"]].drop_duplicates(subset=["gvkey"]).copy()
        )
        print(f"    Firm CUSIP map: {len(firm_cusip):,} unique gvkeys")

        # Load SDC data
        sdc_path = root_path / "inputs" / "SDC" / self.SDC_FILE
        if not sdc_path.exists():
            raise FileNotFoundError(
                f"SDC M&A data not found at: {sdc_path}\n"
                "Expected: inputs/SDC/sdc-ma-merged.parquet"
            )

        sdc = pd.read_parquet(
            sdc_path,
            columns=[
                "Target 6-digit CUSIP",
                "Date Announced",
                "Deal Status",
                "Deal Attitude",
                "Target Public Status",
                "Target Nation",
            ],
        )
        sdc = sdc.rename(columns={"Target 6-digit CUSIP": "cusip6"})

        # Filter: US public targets, sample period, actionable statuses
        sdc_year = pd.to_datetime(sdc["Date Announced"], errors="coerce").dt.year
        sdc_filtered = sdc[
            (sdc_year >= year_start)
            & (sdc_year <= year_end)
            & (sdc["Target Nation"] == "United States")
            & (sdc["Target Public Status"] == "Public")
            & (sdc["Deal Status"].isin(["Completed", "Withdrawn", "Pending"]))
        ].copy()
        sdc_filtered["Date Announced"] = pd.to_datetime(
            sdc_filtered["Date Announced"], errors="coerce"
        )
        print(
            f"    SDC filtered: {len(sdc_filtered):,} deals "
            f"(US public, {year_start}-{year_end}, completed/withdrawn/pending)"
        )
        print(
            "    Deal Attitude breakdown: "
            + ", ".join(
                f"{k}: {v}"
                for k, v in sdc_filtered["Deal Attitude"].value_counts().items()
            )
        )

        # Merge SDC onto firm CUSIP map
        sdc_with_gvkey = firm_cusip.merge(
            sdc_filtered[["cusip6", "Date Announced", "Deal Attitude"]],
            on="cusip6",
            how="inner",
        )
        print(f"    SDC matched to gvkey: {len(sdc_with_gvkey):,} rows")

        # For each firm, take the FIRST announced bid (earliest Date Announced)
        if len(sdc_with_gvkey) > 0:
            sdc_first = (
                sdc_with_gvkey.sort_values("Date Announced")
                .groupby("gvkey")
                .first()
                .reset_index()
                .rename(
                    columns={
                        "Date Announced": "Takeover_Date",
                        "Deal Attitude": "Takeover_Attitude",
                    }
                )
            )
            sdc_first["Takeover"] = 1

            def classify_type(attitude: str) -> str:
                if attitude in self.UNINVITED_ATTITUDES:
                    return "Uninvited"
                elif attitude in self.FRIENDLY_ATTITUDES:
                    return "Friendly"
                return "Unknown"

            sdc_first["Takeover_Type"] = sdc_first["Takeover_Attitude"].apply(
                classify_type
            )
            n_targeted = len(sdc_first)
            print(f"    Unique firms targeted: {n_targeted:,}")
            print(
                "    Takeover_Type breakdown: "
                + ", ".join(
                    f"{k}: {v}"
                    for k, v in sdc_first["Takeover_Type"].value_counts().items()
                )
            )
        else:
            sdc_first = pd.DataFrame(
                columns=[
                    "gvkey",
                    "Takeover_Date",
                    "Takeover_Attitude",
                    "Takeover",
                    "Takeover_Type",
                ]
            )

        # Build full firm-level output: all firms in manifest, Takeover=0 if not targeted
        all_gvkeys = firm_cusip[["gvkey"]].copy()
        result = all_gvkeys.merge(sdc_first, on="gvkey", how="left")
        result["Takeover"] = result["Takeover"].fillna(0).astype(int)
        result["Takeover_Type"] = result["Takeover_Type"].fillna("None")

        n_takeover = result["Takeover"].sum()
        print(
            f"    Output: {len(result):,} firms, "
            f"{n_takeover:,} targeted ({100.0 * n_takeover / len(result):.1f}%)"
        )

        # Validate required columns present
        for col in ["Takeover", "Takeover_Type", "Takeover_Date"]:
            if col not in result.columns:
                raise ValueError(
                    f"'{col}' not found in TakeoverIndicatorBuilder output. "
                    "Check SDC merge logic."
                )

        stats = VariableStats(
            name="Takeover",
            n=int(result["Takeover"].sum()),
            mean=float(result["Takeover"].mean()),
            std=float(result["Takeover"].std()),
            min=0.0,
            p25=0.0,
            median=0.0,
            p75=0.0,
            max=1.0,
            n_missing=0,
            pct_missing=0.0,
        )

        return VariableResult(
            data=result,
            stats=stats,
            metadata={
                "column": "Takeover",
                "source": "inputs/SDC/",
                "merge_key": "gvkey via cusip6",
                "note": "Firm-level (not call-level); gvkey is key, not file_name",
            },
        )


__all__ = ["TakeoverIndicatorBuilder"]
