"""Builder for aggregate macro uncertainty variables — H24 / H24b / H25.

Loads three published macro-uncertainty series and matches them to each
earnings call by the calendar month of its start_date:

    - Geopolitical Risk      (Caldara & Iacoviello 2022, AER)
        inputs/matteoiacoviello/GPR_Global/data_gpr_export.xls
    - US Economic Policy Unc (Baker, Bloom & Davis 2016, QJE)
        inputs/EconomicPolicyUncertaintyIndex/US/US_Policy_Uncertainty_Data.xlsx
    - Global EPU             (Davis 2016, NBER WP 22740)
        inputs/EconomicPolicyUncertaintyIndex/Global/Global_Policy_Uncertainty_Data.xlsx

Processing:
    1. For each file, read the monthly series and normalise to a long
       DataFrame with (ym, value) where ym = year*100 + month (Int64).
    2. Drop footer rows (common in policyuncertainty.com spreadsheets) via
       pd.to_numeric(...).notna() filtering on the year/month columns.
    3. Log-transform each series where value > 0.
    4. Merge each series onto the manifest by ym computed from start_date.

Output columns (one row per manifest file_name):
    file_name, GPR, US_EPU, GEPU_current,
               GPR_log, US_EPU_log, GEPU_log

Temporal Structure:
    Macro value is matched to the call's calendar month (no aggregation,
    no lag). Identification variance is preserved within quarter; quarterly
    two-way clustering in downstream PanelOLS handles macro shock correlation.

Notes:
    - Column-name detection is deliberately flexible because the published
      spreadsheets have used slightly different headers across versions.
      If no known column variant is found the builder raises a clear error
      that includes the actual column list for the failing file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from f1d.shared.path_utils import get_latest_output_dir


# Hardcoded file paths — follows the PRiskQBuilder precedent (prisk_q.py:37)
GPR_FILE = "inputs/matteoiacoviello/GPR_Global/data_gpr_export.xls"
US_EPU_FILE = "inputs/EconomicPolicyUncertaintyIndex/US/US_Policy_Uncertainty_Data.xlsx"
GEPU_FILE = "inputs/EconomicPolicyUncertaintyIndex/Global/Global_Policy_Uncertainty_Data.xlsx"

# Candidate column names — tried in order
GPR_VALUE_CANDIDATES = ["GPR", "gpr", "GPR_rec", "gpr_rec"]
US_EPU_VALUE_CANDIDATES = [
    "News_Based_Policy_Uncert_Index",
    "News_Based_Policy_Uncertainty_Index",
    "news_based_policy_uncert_index",
    "News Based Policy Uncert Index",
]
GEPU_VALUE_CANDIDATES = ["GEPU_current", "gepu_current", "GEPU Current"]


def _first_present(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _build_ym_from_year_month(df: pd.DataFrame) -> pd.DataFrame:
    """Build ym = year*100 + month from a frame with Year+Month columns.

    Drops rows where either Year or Month cannot be coerced to numeric
    (filters common footer/notes rows in policyuncertainty.com spreadsheets).
    """
    year_col = _first_present(df, ["Year", "year", "YEAR"])
    month_col = _first_present(df, ["Month", "month", "MONTH"])
    if year_col is None or month_col is None:
        raise ValueError(
            f"Year/Month columns not found. Available columns: {list(df.columns)}"
        )
    df = df.copy()
    df["_year_num"] = pd.to_numeric(df[year_col], errors="coerce")
    df["_month_num"] = pd.to_numeric(df[month_col], errors="coerce")
    df = df.dropna(subset=["_year_num", "_month_num"]).copy()
    df["ym"] = (df["_year_num"].astype(int) * 100 + df["_month_num"].astype(int)).astype("Int64")
    return df.drop(columns=["_year_num", "_month_num"])


def _load_gpr(path: Path) -> pd.DataFrame:
    """Load Caldara-Iacoviello GPR, return columns: ym, GPR."""
    if not path.exists():
        raise FileNotFoundError(f"GPR data not found: {path}")

    df = pd.read_excel(path)

    value_col = _first_present(df, GPR_VALUE_CANDIDATES)
    if value_col is None:
        raise ValueError(
            f"No GPR value column found in {path.name}. "
            f"Tried {GPR_VALUE_CANDIDATES}. Available: {list(df.columns)}"
        )

    # Date column: GPR file typically uses a single 'month' column (datetime),
    # but may also be (Year, Month). Try datetime first.
    date_col = _first_present(df, ["month", "Month", "date", "Date", "MONTH", "DATE"])
    if date_col is not None and pd.api.types.is_datetime64_any_dtype(df[date_col]):
        dt = pd.to_datetime(df[date_col], errors="coerce")
        out = pd.DataFrame(
            {
                "ym": (dt.dt.year.astype("Int64") * 100 + dt.dt.month.astype("Int64")).astype("Int64"),
                "GPR": pd.to_numeric(df[value_col], errors="coerce"),
            }
        )
    elif date_col is not None:
        # Try parsing as datetime (covers string-formatted dates)
        dt = pd.to_datetime(df[date_col], errors="coerce")
        if dt.notna().sum() > 0.5 * len(df):
            out = pd.DataFrame(
                {
                    "ym": (dt.dt.year.astype("Int64") * 100 + dt.dt.month.astype("Int64")).astype("Int64"),
                    "GPR": pd.to_numeric(df[value_col], errors="coerce"),
                }
            )
        else:
            # Fall back to (Year, Month)
            tmp = _build_ym_from_year_month(df)
            out = pd.DataFrame({"ym": tmp["ym"], "GPR": pd.to_numeric(tmp[value_col], errors="coerce")})
    else:
        tmp = _build_ym_from_year_month(df)
        out = pd.DataFrame({"ym": tmp["ym"], "GPR": pd.to_numeric(tmp[value_col], errors="coerce")})

    out = out.dropna(subset=["ym", "GPR"]).drop_duplicates(subset=["ym"], keep="last")
    return out


def _load_us_epu(path: Path) -> pd.DataFrame:
    """Load BBD US EPU (news-based), return columns: ym, US_EPU."""
    if not path.exists():
        raise FileNotFoundError(f"US EPU data not found: {path}")

    df = pd.read_excel(path)
    value_col = _first_present(df, US_EPU_VALUE_CANDIDATES)
    if value_col is None:
        raise ValueError(
            f"No US EPU news-based column found in {path.name}. "
            f"Tried {US_EPU_VALUE_CANDIDATES}. Available: {list(df.columns)}"
        )

    tmp = _build_ym_from_year_month(df)
    out = pd.DataFrame(
        {"ym": tmp["ym"], "US_EPU": pd.to_numeric(tmp[value_col], errors="coerce")}
    )
    out = out.dropna(subset=["ym", "US_EPU"]).drop_duplicates(subset=["ym"], keep="last")
    return out


def _load_gepu(path: Path) -> pd.DataFrame:
    """Load Davis GEPU (GEPU_current), return columns: ym, GEPU_current."""
    if not path.exists():
        raise FileNotFoundError(f"GEPU data not found: {path}")

    df = pd.read_excel(path)
    value_col = _first_present(df, GEPU_VALUE_CANDIDATES)
    if value_col is None:
        raise ValueError(
            f"No GEPU_current column found in {path.name}. "
            f"Tried {GEPU_VALUE_CANDIDATES}. Available: {list(df.columns)}"
        )

    tmp = _build_ym_from_year_month(df)
    out = pd.DataFrame(
        {"ym": tmp["ym"], "GEPU_current": pd.to_numeric(tmp[value_col], errors="coerce")}
    )
    out = out.dropna(subset=["ym", "GEPU_current"]).drop_duplicates(subset=["ym"], keep="last")
    return out


def _safe_log(s: pd.Series) -> pd.Series:
    """Log-transform with positive-value guard (returns NaN for value ≤ 0)."""
    return np.log(s.where(s > 0))


class MacroUncertaintyBuilder(VariableBuilder):
    """Match monthly macro-uncertainty series onto each call by calendar month.

    Returns six columns per call: the three raw series (GPR, US_EPU,
    GEPU_current) and their log-transformed counterparts (GPR_log,
    US_EPU_log, GEPU_log).

    This builder intentionally does NOT apply winsorization — the inputs are
    already aggregate monthly indices and winsorizing them would distort the
    macro time series.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Primary column used for downstream get_stats reporting
        self.column = "GPR_log"
        self._skip_winsorization = True

    def build(self, years: range, root_path: Path) -> VariableResult:
        # 1. Load manifest (file_name + start_date)
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "start_date"]
        )
        manifest["start_date"] = pd.to_datetime(manifest["start_date"], errors="coerce")
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # 2. Compute calendar ym for merge
        manifest["ym"] = (
            manifest["start_date"].dt.year.astype("Int64") * 100
            + manifest["start_date"].dt.month.astype("Int64")
        ).astype("Int64")

        # 3. Load each macro file
        gpr_path = root_path / GPR_FILE
        us_epu_path = root_path / US_EPU_FILE
        gepu_path = root_path / GEPU_FILE

        print(f"    MacroUncertaintyBuilder: loading {gpr_path.name} ...")
        gpr = _load_gpr(gpr_path)
        print(f"    MacroUncertaintyBuilder: {len(gpr):,} GPR monthly rows")

        print(f"    MacroUncertaintyBuilder: loading {us_epu_path.name} ...")
        us_epu = _load_us_epu(us_epu_path)
        print(f"    MacroUncertaintyBuilder: {len(us_epu):,} US EPU monthly rows")

        print(f"    MacroUncertaintyBuilder: loading {gepu_path.name} ...")
        gepu = _load_gepu(gepu_path)
        print(f"    MacroUncertaintyBuilder: {len(gepu):,} GEPU monthly rows")

        # 4. Merge all three onto manifest by ym
        merged = manifest.merge(gpr, on="ym", how="left")
        merged = merged.merge(us_epu, on="ym", how="left")
        merged = merged.merge(gepu, on="ym", how="left")

        # 5. Log transforms
        merged["GPR_log"] = _safe_log(merged["GPR"])
        merged["US_EPU_log"] = _safe_log(merged["US_EPU"])
        merged["GEPU_log"] = _safe_log(merged["GEPU_current"])

        out_cols = [
            "file_name",
            "GPR",
            "US_EPU",
            "GEPU_current",
            "GPR_log",
            "US_EPU_log",
            "GEPU_log",
        ]
        data = merged[out_cols].drop_duplicates(subset=["file_name"]).copy()

        # Match diagnostics
        n_total = len(data)
        for col in ["GPR", "US_EPU", "GEPU_current"]:
            n_match = data[col].notna().sum()
            pct = 100.0 * n_match / n_total if n_total else 0.0
            print(
                f"    MacroUncertaintyBuilder: {col} matched {n_match:,}/{n_total:,} "
                f"({pct:.1f}%)"
            )

        return VariableResult(
            data=data,
            stats=self.get_stats(data["GPR_log"], "GPR_log"),
            metadata={
                "columns": out_cols[1:],
                "source": (
                    "Caldara & Iacoviello (2022) GPR; "
                    "Baker, Bloom & Davis (2016) US EPU; "
                    "Davis (2016) GEPU"
                ),
                "description": (
                    "Monthly aggregate macro-uncertainty series matched to each "
                    "call by calendar month (year*100+month). Log-transformed "
                    "variants provided for use as primary IVs in H24 / H24b / H25."
                ),
                "n_total": n_total,
            },
        )


__all__ = ["MacroUncertaintyBuilder"]
