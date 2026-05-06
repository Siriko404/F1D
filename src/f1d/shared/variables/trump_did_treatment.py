"""Builder for Trump 2016 DiD treatment label — H1.5 design.

Treatment definition (per `tmp/sec_iiie4_design_revised_2026_05_05_pm.md`
+ plan v3 `tender-popping-origami.md`):

    For each firm i:
        trade_i = mean(PRiskT_trade) over Q4 2011 - Q3 2016 (20 quarters)
        tax_i   = mean(PRiskT_tax)   over Q4 2011 - Q3 2016 (20 quarters)

    For each FF12 industry j:
        trade_med_j = median(trade_i for firms in industry j)
        tax_med_j   = median(tax_i   for firms in industry j)

    BothHigh_i = 1 if (trade_i >= trade_med_j) AND (tax_i >= tax_med_j)
    BothLow_i  = 1 if (trade_i <  trade_med_j) AND (tax_i <  tax_med_j)
    Off-diagonal firms (HighTrade-LowTax or LowTrade-HighTax) get
        BothHigh = NaN AND BothLow = NaN -> dropped at runner complete-case.

    Post_t = 1 if cal_yr_qtr >= 2016q4 (Trump elected Nov 2016) else 0
    DiD_Trump_{i,t} = BothHigh_i * Post_t

Why "BothHigh trade x tax" (verbatim from spec v3):
    Trump's two main exposure vectors were tariffs (trade) and TCJA (tax).
    Firms heavily exposed to BOTH dimensions are the most plausibly-treated
    cohort. Median-split avoids relying on extreme tails. Industry-own median
    isolates within-industry exposure heterogeneity (controls for industry
    composition shifts).

Pre-period 5 years (Q4 2011 - Q3 2016) chosen because:
    1. Pre-fixes treatment label BEFORE Trump's election (no look-ahead)
    2. Smooths firm-quarter noise (mean over 20 obs)
    3. Aligns with Hu 2024 RAST template's use of multi-quarter pre-window
    4. Excludes Q4 2016 (the event quarter)

Inputs:
    - PRiskSubtopicsBuilder output (PRiskT_trade, PRiskT_tax per gvkey x cal_q)
    - manifest (file_name, gvkey, start_date) for call-level mapping
    - h1_cash_holdings_panel.parquet for ff12_code per gvkey

Outputs (call-level via file_name):
    - BothHigh        in {0, 1}: 1 if firm is BothHigh-exposure
    - BothLow         in {0, 1}: 1 if firm is BothLow-exposure
    - Post_trump      in {0, 1}: 1 if cal_yr_qtr >= 2016q4
    - DiD_Trump       in {0, 1}: BothHigh * Post_trump (the treatment indicator)
    - trade_pre_mean  : firm's pre-window mean of PRiskT_trade (for diagnostics)
    - tax_pre_mean    : firm's pre-window mean of PRiskT_tax (for diagnostics)

Off-diagonal firms (NaN BothHigh/BothLow) are PRESENT in the output panel
but with NaN labels. The runner filters them out via complete-case at
regression time per spec v3 Variant A ("drop off-diagonal entirely").
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from .political_risk_subtopics import PRiskSubtopicsBuilder
from f1d.shared.path_utils import get_latest_output_dir


# Pre-window for treatment-label fixation (5 years = 20 quarters).
# Q4 2011 -> 2011q4 ; Q3 2016 -> 2016q3
PRE_WINDOW_START = "2011q4"
PRE_WINDOW_END = "2016q3"

# Trump elected November 8, 2016 (Q4 2016). Post = on/after 2016q4.
POST_THRESHOLD_YR_QTR = 20164  # cal_yr*10 + cal_qtr (4)


def _cal_q_in_window(cal_q: str, start: str, end: str) -> bool:
    """Inclusive cal_q range check via lex sort (works for YYYYqQ format)."""
    return start <= cal_q <= end


def _yr_qtr_int(cal_q: str) -> int:
    """'2016q4' -> 20164 integer key (matches build_cal_yr_qtr_index)."""
    parts = cal_q.lower().split("q")
    return int(parts[0]) * 10 + int(parts[1])


class TrumpDiDTreatmentBuilder(VariableBuilder):
    """Build firm-level BothHigh/BothLow treatment + per-call DiD_Trump indicator.

    Returns VariableResult with columns:
      file_name, BothHigh, BothLow, Post_trump, DiD_Trump,
      trade_pre_mean, tax_pre_mean
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Optional override for pre-window or industry-classification source
        self.pre_start: str = config.get("pre_window_start", PRE_WINDOW_START)
        self.pre_end: str = config.get("pre_window_end", PRE_WINDOW_END)
        self.column = "DiD_Trump"  # primary DiD treatment indicator

    def build(self, years: range, root_path: Path) -> VariableResult:
        # 1. Load manifest — file_name, gvkey, start_date
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"
        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year

        # Manifest cal_q + cal_yr_qtr
        manifest["cal_q"] = (
            manifest["start_date"].dt.year.astype(str)
            + "q"
            + manifest["start_date"].dt.quarter.astype(str)
        )
        manifest["cal_yr_qtr"] = (
            manifest["start_date"].dt.year * 10
            + manifest["start_date"].dt.quarter
        )

        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # 2. Pull PRiskT_trade + PRiskT_tax per (gvkey, cal_q) via subtopics builder
        # Use full pre-window range, even if outside `years` (firm-level fixed labels
        # require the 5-year pre-window observed regardless of regression sample).
        pre_yrs = range(
            int(self.pre_start[:4]), int(self.pre_end[:4]) + 1
        )
        sub_builder = PRiskSubtopicsBuilder(
            {"subtopics": ["PRiskT_trade", "PRiskT_tax"]}
        )
        # Manually load TSV directly to bypass manifest filter (we need
        # firm-quarter rows for ALL firms in pre-window, not just F1D calls).
        prisk_path = root_path / "inputs" / "FirmLevelRisk" / "firmquarter_2022q1.csv"
        if not prisk_path.exists():
            raise FileNotFoundError(f"PRisk data not found: {prisk_path}")

        from .political_risk_subtopics import _parse_cal_q
        from .winsorization import winsorize_by_year

        cols = ["gvkey", "date", "PRiskT_trade", "PRiskT_tax"]
        prisk_df = pd.read_csv(
            prisk_path, sep="\t", on_bad_lines="skip", usecols=cols
        )
        prisk_df["gvkey"] = prisk_df["gvkey"].astype(str).str.zfill(6)
        prisk_df = prisk_df.dropna(subset=["PRiskT_trade", "PRiskT_tax"], how="all")
        prisk_df["cal_q"] = prisk_df["date"].apply(_parse_cal_q)
        prisk_df = prisk_df.dropna(subset=["cal_q"])
        prisk_df["year"] = prisk_df["cal_q"].str[:4].astype(int)
        prisk_df = prisk_df[prisk_df["year"].isin(list(pre_yrs))].copy()

        # Dedup (gvkey, cal_q) — keep row with max sum of subtopics
        prisk_df["_sum"] = prisk_df[["PRiskT_trade", "PRiskT_tax"]].sum(
            axis=1, skipna=True
        )
        prisk_df = (
            prisk_df.sort_values("_sum", ascending=False)
            .drop_duplicates(subset=["gvkey", "cal_q"], keep="first")
            .drop(columns=["_sum"])
        )

        # Per-year winsorization on PRisk subtopics (for pre-window stability).
        prisk_df = winsorize_by_year(
            prisk_df, ["PRiskT_trade", "PRiskT_tax"], year_col="year"
        )
        print(
            f"    TrumpDiDTreatmentBuilder: PRisk pre-window rows = "
            f"{len(prisk_df):,} ({prisk_df['gvkey'].nunique():,} unique firms)"
        )

        # 3. Filter to pre-window quarters [pre_start, pre_end]
        in_window = prisk_df["cal_q"].apply(
            lambda q: _cal_q_in_window(q, self.pre_start, self.pre_end)
        )
        pre_df = prisk_df[in_window].copy()
        print(
            f"    TrumpDiDTreatmentBuilder: pre-window {self.pre_start}..{self.pre_end} -> "
            f"{len(pre_df):,} firm-quarter rows"
        )

        # 4. Aggregate to firm-mean per gvkey
        firm_means = (
            pre_df.groupby("gvkey")[["PRiskT_trade", "PRiskT_tax"]]
            .mean()
            .reset_index()
            .rename(
                columns={
                    "PRiskT_trade": "trade_pre_mean",
                    "PRiskT_tax": "tax_pre_mean",
                }
            )
        )
        # Require minimum number of pre-window observations per firm.
        # Mirror Han-Qiu / Bates 2009 pattern: at least 8 quarters of 20.
        firm_obs = (
            pre_df.groupby("gvkey")["cal_q"].nunique().rename("n_pre_obs")
        )
        firm_means = firm_means.merge(firm_obs, on="gvkey", how="left")
        firm_means_full = firm_means[firm_means["n_pre_obs"] >= 8].copy()
        print(
            f"    TrumpDiDTreatmentBuilder: firms with >=8 pre-window obs = "
            f"{len(firm_means_full):,} / {len(firm_means):,}"
        )

        # 5. Merge ff12_code per gvkey from H1 panel (for industry-own median).
        h1_panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h1_cash_holdings",
            required_file="h1_cash_holdings_panel.parquet",
        )
        h1_path = h1_panel_dir / "h1_cash_holdings_panel.parquet"
        h1_panel = pd.read_parquet(h1_path, columns=["gvkey", "ff12_code"])
        h1_panel["gvkey"] = h1_panel["gvkey"].astype(str).str.zfill(6)
        # First non-null ff12_code per gvkey (firms have stable industry classification)
        gvkey_to_ff12 = (
            h1_panel.dropna(subset=["ff12_code"])
            .groupby("gvkey")["ff12_code"]
            .first()
            .reset_index()
        )
        firm_labels = firm_means_full.merge(gvkey_to_ff12, on="gvkey", how="left")
        firm_labels = firm_labels.dropna(subset=["ff12_code"])

        # 6. FF12-industry-own median split
        firm_labels["trade_med_ff12"] = firm_labels.groupby("ff12_code")[
            "trade_pre_mean"
        ].transform("median")
        firm_labels["tax_med_ff12"] = firm_labels.groupby("ff12_code")[
            "tax_pre_mean"
        ].transform("median")

        firm_labels["high_trade"] = (
            firm_labels["trade_pre_mean"] >= firm_labels["trade_med_ff12"]
        )
        firm_labels["high_tax"] = (
            firm_labels["tax_pre_mean"] >= firm_labels["tax_med_ff12"]
        )

        bh = firm_labels["high_trade"] & firm_labels["high_tax"]
        bl = (~firm_labels["high_trade"]) & (~firm_labels["high_tax"])

        firm_labels["BothHigh"] = np.where(
            bh, 1.0, np.where(bl, 0.0, np.nan)
        )
        firm_labels["BothLow"] = np.where(
            bl, 1.0, np.where(bh, 0.0, np.nan)
        )

        n_high = int((firm_labels["BothHigh"] == 1).sum())
        n_low = int((firm_labels["BothLow"] == 1).sum())
        n_off = int(firm_labels["BothHigh"].isna().sum())
        n_total_firms = len(firm_labels)
        print(
            f"    TrumpDiDTreatmentBuilder: BothHigh={n_high:,}  BothLow={n_low:,}  "
            f"off-diagonal={n_off:,} (NaN, dropped at runner) / total={n_total_firms:,}"
        )

        firm_labels_keep_cols = [
            "gvkey",
            "trade_pre_mean",
            "tax_pre_mean",
            "BothHigh",
            "BothLow",
        ]
        firm_labels_min = firm_labels[firm_labels_keep_cols].copy()

        # 7. Per-call merge to manifest, attach Post + DiD_Trump
        merged = manifest.merge(firm_labels_min, on="gvkey", how="left")
        merged["Post_trump"] = (
            merged["cal_yr_qtr"] >= POST_THRESHOLD_YR_QTR
        ).astype(float)
        merged["DiD_Trump"] = (
            merged["BothHigh"] * merged["Post_trump"]
        )

        out_cols = [
            "file_name",
            "BothHigh",
            "BothLow",
            "Post_trump",
            "DiD_Trump",
            "trade_pre_mean",
            "tax_pre_mean",
        ]
        data = merged[out_cols].copy()
        data = data.drop_duplicates(subset=["file_name"])

        # Diagnostic summary
        n_calls_total = len(data)
        n_calls_treated = int((data["BothHigh"] == 1).sum())
        n_calls_control = int((data["BothLow"] == 1).sum())
        n_calls_off = int(data["BothHigh"].isna().sum())
        print(
            f"    TrumpDiDTreatmentBuilder: per-call coverage on F1D panel — "
            f"BothHigh={n_calls_treated:,}  BothLow={n_calls_control:,}  "
            f"off-diagonal={n_calls_off:,} / total calls={n_calls_total:,}"
        )

        n_calls_did_eq_1 = int((data["DiD_Trump"] == 1).sum())
        print(
            f"    TrumpDiDTreatmentBuilder: DiD_Trump==1 cells = "
            f"{n_calls_did_eq_1:,} (BothHigh AND Post_trump)"
        )

        return VariableResult(
            data=data,
            stats=self.get_stats(data["DiD_Trump"], "DiD_Trump"),
            metadata={
                "columns": out_cols[1:],
                "primary_column": "DiD_Trump",
                "source": "Hassan PRiskT_trade x PRiskT_tax + manifest cal_yr_qtr",
                "description": (
                    "Trump 2016 DiD treatment indicator. Firm BothHigh / BothLow "
                    f"labels fixed pre-event over {self.pre_start}-{self.pre_end}. "
                    "Industry-own FF12 median split. Post = cal_yr_qtr >= 2016q4. "
                    "Off-diagonal firms (HighTrade x LowTax or LowTrade x HighTax) "
                    "yield NaN BothHigh/BothLow -> dropped at runner."
                ),
                "pre_window_start": self.pre_start,
                "pre_window_end": self.pre_end,
                "post_threshold_yr_qtr": POST_THRESHOLD_YR_QTR,
                "n_firms_total": n_total_firms,
                "n_firms_BothHigh": n_high,
                "n_firms_BothLow": n_low,
                "n_firms_off_diagonal": n_off,
                "n_calls_BothHigh": n_calls_treated,
                "n_calls_BothLow": n_calls_control,
                "n_calls_DiD_eq_1": n_calls_did_eq_1,
            },
        )


__all__ = ["TrumpDiDTreatmentBuilder"]
