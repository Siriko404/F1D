"""Builder for EmploymentGrowth_lead (H13.2 Dependent Variable).

Computes ln(EMP_{t+1}) - ln(EMP_t) from Compustat Annual `emp` (Employees).

Compustat Annual (`inputs/Compustat_Annual/compustat_annual.csv`) contains the
`emp` variable (number of employees in thousands) which is annual/fiscal-year data.

Construction:
    1. Load manifest (file_name, gvkey, start_date)
    2. Load Compustat Annual data with emp
    3. Match calls to Compustat Annual via gvkey + fyearq (fiscal year)
    4. For each (gvkey, fyearq), take EMP value
    5. Compute EmploymentGrowth_lead:
       - ln(EMP_{t+1}) - ln(EMP_t) within gvkey
       - Validate consecutive fiscal years
       - EMP must be strictly positive for log
    6. Merge back to all calls by (gvkey, fyearq)

Edge cases:
    - EMP <= 0 -> NaN (log undefined)
    - Non-consecutive fiscal years -> NaN
    - Missing EMP at t or t+1 -> NaN
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from .panel_utils import attach_fyearq
from f1d.shared.path_utils import get_latest_output_dir

logger = logging.getLogger(__name__)


class EmploymentGrowthLeadBuilder(VariableBuilder):
    """Build EmploymentGrowth_lead = ln(EMP_{t+1}) - ln(EMP_t).

    Uses Compustat Annual `emp` (Employees in thousands).
    Computes log difference within firm, validating consecutive fiscal years.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
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
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Step 1: Load Compustat Annual data with emp
        comp_annual_path = root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv"
        if not comp_annual_path.exists():
            raise FileNotFoundError(
                f"Compustat Annual file not found: {comp_annual_path}"
            )

        logger.info(f"  Loading Compustat Annual from {comp_annual_path}")
        comp_annual = pd.read_csv(
            comp_annual_path,
            usecols=["gvkey", "fyear", "datadate", "emp"],
            low_memory=False,
        )
        comp_annual["gvkey"] = comp_annual["gvkey"].astype(str).str.zfill(6)
        comp_annual["datadate"] = pd.to_datetime(comp_annual["datadate"], errors="coerce")
        comp_annual["fyear"] = pd.to_numeric(comp_annual["fyear"], errors="coerce")
        comp_annual["emp"] = pd.to_numeric(comp_annual["emp"], errors="coerce")

        # Keep last observation per (gvkey, fyear) - most recent restatement
        comp_annual = comp_annual.sort_values(["gvkey", "fyear", "datadate"])
        comp_annual = comp_annual.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

        logger.info(f"  Loaded {len(comp_annual):,} firm-year observations from Compustat Annual")

        # Step 2: Attach fyearq to manifest for matching
        manifest = attach_fyearq(manifest, root_path)
        manifest["fyearq_int"] = pd.to_numeric(manifest["fyearq"], errors="coerce")

        # Step 3: Merge EMP from Compustat Annual to manifest by (gvkey, fyearq)
        # fyearq = fiscal year from quarterly data; fyear = fiscal year from annual data
        emp_lookup = comp_annual[["gvkey", "fyear", "emp"]].copy()
        emp_lookup = emp_lookup.rename(columns={"fyear": "fyearq_int"})

        merged = manifest.merge(
            emp_lookup,
            on=["gvkey", "fyearq_int"],
            how="left"
        )

        logger.info(f"  Matched EMP: {merged['emp'].notna().sum():,} / {len(manifest):,} calls")

        # Step 4: Find latest call per (gvkey, fyearq) for EMP
        merged["start_date_dt"] = pd.to_datetime(merged["start_date"], errors="coerce")

        valid_mask = merged["fyearq_int"].notna()
        merged_valid = merged[valid_mask].copy()

        # Get latest call per firm-fiscal-year
        latest_idx = merged_valid.groupby(["gvkey", "fyearq_int"])["start_date_dt"].idxmax()
        firm_year = merged_valid.loc[
            latest_idx, ["gvkey", "fyearq_int", "emp"]
        ].copy()
        firm_year = firm_year.rename(columns={"fyearq_int": "fyearq"})

        # Step 5: Compute EmploymentGrowth_lead = ln(EMP_{t+1}) - ln(EMP_t)
        firm_year = firm_year.sort_values(["gvkey", "fyearq"]).reset_index(drop=True)

        # Next fiscal year and next EMP
        firm_year["fyearq_lead"] = firm_year.groupby("gvkey")["fyearq"].shift(-1)
        firm_year["emp_lead"] = firm_year.groupby("gvkey")["emp"].shift(-1)

        # Validate consecutive fiscal years (gap = 1)
        fyearq_int = firm_year["fyearq"].astype("Int64")
        fyearq_lead_int = firm_year["fyearq_lead"].astype("Int64")
        is_consecutive = (fyearq_lead_int - fyearq_int) == 1

        # Conditions: consecutive years, both EMP positive
        emp_t = firm_year["emp"]
        emp_t1 = firm_year["emp_lead"]

        valid_emp = (
            is_consecutive &
            emp_t.notna() & (emp_t > 0) &
            emp_t1.notna() & (emp_t1 > 0)
        )

        firm_year["EmploymentGrowth_lead"] = np.where(
            valid_emp,
            np.log(emp_t1) - np.log(emp_t),
            np.nan
        )

        logger.info(
            f"  EmploymentGrowth_lead: {firm_year['EmploymentGrowth_lead'].notna().sum():,} / "
            f"{len(firm_year):,} firm-years"
        )

        # Step 6: Merge back to all calls by (gvkey, fyearq_int)
        lead_lookup = firm_year[["gvkey", "fyearq", "EmploymentGrowth_lead"]].copy()
        lead_lookup = lead_lookup.rename(columns={"fyearq": "fyearq_int"})

        final_merged = manifest[["file_name"]].merge(
            merged[["file_name", "gvkey", "fyearq_int"]].merge(
                lead_lookup,
                on=["gvkey", "fyearq_int"],
                how="left"
            ),
            on="file_name",
            how="left"
        )

        data = final_merged[["file_name", "EmploymentGrowth_lead"]].copy()
        stats = self.get_stats(data["EmploymentGrowth_lead"], "EmploymentGrowth_lead")

        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "EmploymentGrowth_lead",
                "source": "Compustat Annual/emp (ln(EMP_{t+1}) - ln(EMP_t))",
                "n_valid_emp": int(valid_emp.sum()),
                "n_total_firm_years": len(firm_year),
            },
        )


__all__ = ["EmploymentGrowthLeadBuilder"]
