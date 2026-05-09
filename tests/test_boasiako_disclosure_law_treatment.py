"""Inline pytest for Boasiako Disclosure Law treatment builder (Phase 1A Task A4).

v2 audit V1 lock: Y+1 timing per spec §3.2 verbatim.
v2 audit M7 lock: loc=='USA' filter applied at reader level.
v2 audit P5 lock: 4 never-treated states (AL/KY/NM/SD) encoded as Disclosure_Law=0.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from f1d.shared.variables.boasiako_disclosure_law_treatment import (
    BoasiakoDisclosureLawTreatmentBuilder,
    load_disclosure_law_passage_years,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def passage_years() -> pd.DataFrame:
    return load_disclosure_law_passage_years(
        ROOT / "inputs" / "Boasiako_replication" / "NCSL" / "disclosure_law_passage_years.csv"
    )


@pytest.fixture(scope="module")
def treatment_panel() -> pd.DataFrame:
    return BoasiakoDisclosureLawTreatmentBuilder().build(
        years=range(1997, 2016), root_path=ROOT
    ).data


def test_passage_years_csv_has_46_states(passage_years):
    """v2 audit P5: CSV has 46 states; 4 missing (AL/KY/NM/SD) passed AFTER 2010."""
    assert len(passage_years) == 46


def test_passage_years_includes_california_2002(passage_years):
    """California passed first (2002) per Boasiako Section 2.1."""
    ca = passage_years[passage_years["state_code"] == "CA"]
    assert len(ca) == 1
    assert ca["year_passed"].iloc[0] == 2002


def test_passage_years_includes_mississippi_2010(passage_years):
    """Mississippi passed last (2010 in our 1997-2015 window) per Boasiako Section 2.1."""
    ms = passage_years[passage_years["state_code"] == "MS"]
    assert len(ms) == 1
    assert ms["year_passed"].iloc[0] == 2010


def test_california_y_plus_1_timing(treatment_panel):
    """v2 audit V1: California passed 2002 → Disclosure_Law=0 in 2002, =1 from 2003 onward."""
    df = treatment_panel
    ca = df[df["state"] == "CA"]
    # In year 2002: not yet treated (year of passage)
    ca_2002 = ca[ca["fyear"] == 2002]
    assert (ca_2002["Disclosure_Law"] == 0).all(), "CA 2002 (year of passage) should be 0"
    # In year 2003: treated (year AFTER passage)
    ca_2003 = ca[ca["fyear"] == 2003]
    assert (ca_2003["Disclosure_Law"] == 1).all(), "CA 2003 (year after) should be 1"
    # In year 2010: still treated
    ca_2010 = ca[ca["fyear"] == 2010]
    assert (ca_2010["Disclosure_Law"] == 1).all()


def test_never_treated_states_zero_throughout(treatment_panel):
    """v2 audit P5: AL/KY/NM/SD passed AFTER 2010; Disclosure_Law=0 throughout 1997-2015."""
    df = treatment_panel
    for state in ["AL", "KY", "NM", "SD"]:
        sub = df[df["state"] == state]
        if len(sub) == 0:
            continue  # state may have no firm-years in F1D Compustat
        assert (sub["Disclosure_Law"] == 0).all(), (
            f"{state} should be Disclosure_Law=0 throughout (passed after 2010)"
        )


def test_pre_treatment_window_all_zero(treatment_panel):
    """In 1997-2001 (before California 2002), all states have Disclosure_Law=0."""
    df = treatment_panel
    pre = df[df["fyear"].between(1997, 2001)]
    # CA was earliest at 2002 → no firms treated 1997-2001 (pre-CA-2002 → after-passage = 1998-2002 still 0)
    # Actually CA's Disclosure_Law turns on 2003. So pre 2003: CA still 0. Pre 2002: all states 0.
    assert (pre["Disclosure_Law"] == 0).all()


def test_treatment_panel_schema(treatment_panel):
    """Output schema: gvkey, fyear, state, Disclosure_Law (+ ff49_code if joined later)."""
    df = treatment_panel
    assert {"gvkey", "fyear", "state", "Disclosure_Law"}.issubset(df.columns)
    assert df["Disclosure_Law"].isin([0, 1]).all()


def test_only_us_firms(treatment_panel):
    """v2 audit M7: us_only filter — non-US firms (province codes) dropped."""
    df = treatment_panel
    # All states should be valid 2-letter US state codes
    valid_us_states = {
        "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
        "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
        "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
        "VA","WA","WV","WI","WY","DC",
    }
    states_in_panel = set(df["state"].dropna().unique())
    invalid = states_in_panel - valid_us_states
    assert not invalid, f"Found non-US state codes (loc=='USA' filter failure?): {invalid}"
