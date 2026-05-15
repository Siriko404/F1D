#!/usr/bin/env python3
"""Trace each filter's drop on the 898 HIGH_BETA_UK-classified firms.

Per advisor 2026-05-14 7:30pm EDT: gap is at HIGH_BETA_UK restriction step,
not IBES. 898 classified firms → 556 survive into regression. Hypothesis:
SIC drop (4900-4999, 6000-6999) applied AFTER β^UK estimation removes
util+fin classified firms.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, "src")

from f1d.shared.path_utils import get_latest_output_dir  # type: ignore


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path.cwd()

    print("=" * 80)
    print("DIAGNOSE: Where do the 898 classified firms drop in the funnel?")
    print("=" * 80)

    bu_dir = get_latest_output_dir(
        root / "outputs" / "variables" / "brexit_treatment_beta_uk",
        required_file="beta_uk_per_firm.parquet",
    )
    bu = pd.read_parquet(bu_dir / "beta_uk_per_firm.parquet")
    classified = bu[bu["HIGH_BETA_UK"].isin([0.0, 1.0])].copy()
    print(f"\nA. β^UK builder output:           {len(bu):>6,} firms total")
    print(f"   nonneg β^UK:                   {(bu['beta_uk'] >= 0).sum():>6,}")
    print(f"   classified (top-N + bot-N):    {len(classified):>6,} firms")
    print(f"     of which top (HIGH=1):       {(classified['HIGH_BETA_UK'] == 1).sum():>6,}")
    print(f"     of which bot (HIGH=0):       {(classified['HIGH_BETA_UK'] == 0).sum():>6,}")

    # Load Compustat SIC + window coverage
    import pyarrow.parquet as pq
    from datetime import datetime as _dt
    cpath = root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    table = pq.read_table(
        cpath,
        columns=["gvkey", "datadate", "sic", "atq", "mkvaltq", "cheq"],
        filters=[("datadate", ">=", _dt(2010, 1, 1)),
                 ("datadate", "<",  _dt(2017, 1, 1))],
    )
    comp = table.to_pandas()
    del table
    comp["datadate"] = pd.to_datetime(comp["datadate"])
    comp["cal_yr_qtr"] = comp["datadate"].dt.year * 10 + comp["datadate"].dt.quarter
    comp["gvkey"] = comp["gvkey"].astype(int).astype(str).str.zfill(6)
    comp["sic_int"] = pd.to_numeric(comp["sic"], errors="coerce")
    for c in ["atq", "mkvaltq", "cheq"]:
        comp[c] = pd.to_numeric(comp[c], errors="coerce")
    print(f"\nB. Compustat rows 2010-2016:    {len(comp):>6,}")
    print(f"   unique gvkeys:                  {comp['gvkey'].nunique():>6,}")

    # B1. Classified firms WITH ANY Compustat record in window
    in_window = comp["gvkey"].drop_duplicates().to_frame()
    surv_window = classified.merge(in_window, on="gvkey", how="inner")
    print(f"\nC. Classified firms WITH any Compustat row 2010-2016:")
    print(f"   survive:                       {len(surv_window):>6,}  (lost {len(classified) - len(surv_window):,})")

    # B2. Apply SIC filter
    comp_sic_keep = comp[~((comp["sic_int"] >= 4900) & (comp["sic_int"] <= 4999))]
    comp_sic_keep = comp_sic_keep[~((comp_sic_keep["sic_int"] >= 6000) & (comp_sic_keep["sic_int"] <= 6999))]
    sic_survivors = comp_sic_keep["gvkey"].drop_duplicates().to_frame()
    surv_sic = surv_window.merge(sic_survivors, on="gvkey", how="inner")
    print(f"\nD. After SIC drop (4900-4999, 6000-6999):")
    print(f"   survive:                       {len(surv_sic):>6,}  (lost {len(surv_window) - len(surv_sic):,})")

    # Breakdown of SIC losses on classified firms
    classified_sic = classified.merge(
        comp[["gvkey", "sic_int"]].drop_duplicates("gvkey"),
        on="gvkey", how="left",
    )
    util_drop = classified_sic[classified_sic["sic_int"].between(4900, 4999)]
    fin_drop = classified_sic[classified_sic["sic_int"].between(6000, 6999)]
    missing_sic = classified_sic[classified_sic["sic_int"].isna()]
    print(f"   util (4900-4999):              {len(util_drop):>6,}")
    print(f"   fin  (6000-6999):              {len(fin_drop):>6,}")
    print(f"   missing SIC:                   {len(missing_sic):>6,}")

    # B3. Apply $10M filter: classified firms with ALL Q's mkvaltq + atq ≥ $10M would be too strict
    # Per runner: filter is per-cell, AND-keep both ≥$10M. Cells dropped per firm.
    cells_pass_10M = comp_sic_keep[(comp_sic_keep["mkvaltq"].fillna(0) >= 10.0) & (comp_sic_keep["atq"] >= 10.0)]
    cell_count_per_firm = cells_pass_10M.groupby("gvkey").size()
    firms_with_any_10M_cell = cell_count_per_firm[cell_count_per_firm > 0].index
    surv_10M_any = surv_sic[surv_sic["gvkey"].isin(firms_with_any_10M_cell)]
    print(f"\nE. After $10M filter (firms with ≥1 surviving cell):")
    print(f"   survive:                       {len(surv_10M_any):>6,}  (lost {len(surv_sic) - len(surv_10M_any):,})")

    # B4. Cells in regression sample per firm
    print(f"\nF. Cell-density of surviving classified firms (post-SIC, post-$10M):")
    cell_density = cells_pass_10M[cells_pass_10M["gvkey"].isin(surv_10M_any["gvkey"])].groupby("gvkey").size()
    n_cells_total = int(cell_density.sum())
    print(f"   total cells in panel:          {n_cells_total:>6,}")
    print(f"   mean cells/firm:               {cell_density.mean():.2f}")
    print(f"   median cells/firm:             {cell_density.median():.0f}")
    print(f"   firms with 28 Qs:              {(cell_density == 28).sum():>6,}")
    print(f"   firms with ≥21 Qs:             {(cell_density >= 21).sum():>6,}")
    print(f"   firms with <12 Qs:             {(cell_density < 12).sum():>6,}")

    print()
    print("=" * 80)
    print("FUNNEL SUMMARY")
    print("=" * 80)
    n0 = len(classified)
    n1 = len(surv_window)
    n2 = len(surv_sic)
    n3 = len(surv_10M_any)
    print(f"  Classified firms (898 expected):  {n0:>4,}")
    print(f"  → in Compustat 2010-2016 window:  {n1:>4,}  ({n0-n1:>4} dropped)")
    print(f"  → after SIC drop (util+fin):      {n2:>4,}  ({n1-n2:>4} dropped)")
    print(f"  → after $10M (≥1 valid cell):     {n3:>4,}  ({n2-n3:>4} dropped)")
    print(f"  Regression diagnostic showed:     556 firms appear in HIGH_BETA_UK={{0,1}} cells")
    print()
    print(f"  Campello target firms:            898 (top-449 + bot-449 of nonneg β^UK)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
