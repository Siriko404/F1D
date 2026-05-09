"""Boasiako Eq 1 Disclosure Law treatment builder (Phase 1A Task A4).

Builds Disclosure_Law(0/1)_{s,t} per spec line 1009 verbatim:

    "Disclosure Law(0/1)_{s,t} is a dummy variable that switches to one
     the year after the focal state passed the disclosure law"

v2 audit V1 lock: Y+1 timing per spec §3.2 (NOT Table A1's "after enactment"
which has Y vs Y+1 ambiguity). NLM 1-page-early drift bug acknowledged;
mid-execution PDF re-verify Table A1 caption is recommended (defer).

v2 audit M7 lock: us_only=True via reader (17.4% of F1D rows are non-US
Canadian provinces using overlapping 2-letter state codes).

v2 audit P5 lock: 4 never-treated states (AL/KY/NM/SD passed AFTER 2010,
the sample-end-bound by Mississippi 2010) encoded as Disclosure_Law=0
throughout the 1997-2015 sample window. Per Boasiako Section 2.1 verbatim
"all 50 states pass eventually" but the 4 are post-MS-2010 and don't appear
in our 46-state passage CSV.

Inputs:
- inputs/Boasiako_replication/NCSL/disclosure_law_passage_years.csv (46 states)
- inputs/Compustat_Annual/compustat_annual.csv via _compustat_annual_reader
  (reads gvkey, datadate, sic, state, loc; us_only=True; SIC excl 6000-6999 + 4900-4999)

Output (per gvkey × fyear):
    gvkey, fyear, state, Disclosure_Law

State assignment: Compustat ``state`` field = HQ state for US firms (loc=='USA').
Per spec §3.2 verbatim: "focusing on the states in which firms are headquartered
is a conservative approach, since it essentially downward biases β". Conservative
bias acknowledged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from f1d.shared._compustat_annual_reader import read_compustat_annual

from .base import VariableBuilder, VariableResult, VariableStats


def load_disclosure_law_passage_years(csv_path: Path) -> pd.DataFrame:
    """Load 46-state passage-year CSV.

    Args:
        csv_path: path to disclosure_law_passage_years.csv

    Returns:
        DataFrame with cols: state_name, state_code, year_passed, source.
        46 rows (CA 2002 + 19 in 2005 + 13 in 2006 + 5 in 2007 + 6 in 2008 + 1 in 2009 + 1 in 2010 = 46).
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"disclosure_law_passage_years.csv not found at {csv_path}")
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["state_code", "year_passed"]).copy()
    df["year_passed"] = df["year_passed"].astype(int)
    return df


class BoasiakoDisclosureLawTreatmentBuilder(VariableBuilder):
    """Build (gvkey, fyear, state, Disclosure_Law) panel for Boasiako Eq 1.

    Per spec §3.2 verbatim:
        Disclosure_Law(0/1)_{s,t} = 1 iff state s passed law in year ≤ t-1
                                  = 0 otherwise (incl. year of passage and never-treated)
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "Disclosure_Law"

    def build(self, years: range, root_path: Path) -> VariableResult:
        # Load passage-year CSV
        csv_path = (
            root_path / "inputs" / "Boasiako_replication" / "NCSL"
            / "disclosure_law_passage_years.csv"
        )
        passage = load_disclosure_law_passage_years(csv_path)
        passage_map: Dict[str, int] = dict(zip(passage["state_code"], passage["year_passed"]))

        # Load Compustat Annual (us_only by default per audit M7)
        comp = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=["gvkey", "datadate", "sic", "state", "loc"],
            years=years,
            us_only=True,
        )
        # Drop rows missing state (some US firms have empty state field)
        comp = comp.dropna(subset=["state"]).copy()
        # Compustat uses "PR" for Puerto Rico, "VI" for Virgin Islands, etc.
        # Restrict to standard 50 states + DC for clean Boasiako-spec matching
        valid_us_states = {
            "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
            "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
            "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
            "VA","WA","WV","WI","WY","DC",
        }
        comp = comp[comp["state"].isin(valid_us_states)].copy()

        # Compute Disclosure_Law per (state, fyear) per Y+1 timing
        # passage[s] = year state s passed; treatment turns on year AFTER (passage[s] + 1)
        def _compute(row) -> int:
            s = row["state"]
            t = row["fyear"]
            if pd.isna(t):
                return 0
            t_int = int(t)
            if s not in passage_map:
                # Never-treated state (AL/KY/NM/SD per audit P5)
                return 0
            year_passed = passage_map[s]
            return 1 if t_int >= year_passed + 1 else 0

        comp["Disclosure_Law"] = comp.apply(_compute, axis=1).astype("Int64")

        # Dedup to (gvkey, fyear) — keep last datadate within fyear (year-end)
        comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
        comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

        out = comp[["gvkey", "fyear", "state", "Disclosure_Law"]].reset_index(drop=True)

        n_treated = int((out["Disclosure_Law"] == 1).sum())
        n_total = len(out)

        stats = VariableStats(
            name="Disclosure_Law",
            n=n_total,
            mean=float(out["Disclosure_Law"].mean()),
            std=float(out["Disclosure_Law"].std()),
            min=0,
            p25=float(out["Disclosure_Law"].quantile(0.25)),
            median=float(out["Disclosure_Law"].median()),
            p75=float(out["Disclosure_Law"].quantile(0.75)),
            max=1,
            n_missing=0,
            pct_missing=0.0,
        )
        metadata: Dict[str, Any] = {
            "source": "Boasiako-O'Connor Keefe (2020) EFM Online Appendix Table B.1",
            "passage_years_csv": str(csv_path),
            "n_states_in_passage_csv": int(len(passage)),
            "n_never_treated_states": 4,  # AL, KY, NM, SD (audit P5)
            "y_plus_1_timing": True,  # audit V1 lock per spec §3.2
            "n_firm_years": n_total,
            "n_treated_firm_years": n_treated,
            "frac_treated": float(n_treated / n_total) if n_total else 0.0,
            "column": "Disclosure_Law",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
