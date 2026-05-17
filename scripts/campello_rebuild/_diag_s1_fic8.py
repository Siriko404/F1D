"""STEP-1 filter-8 root-cause diagnostic (systematic-debugging Phase 1).

READ-ONLY. Instruments the 3 boundaries of the HP-FIC100 join:
  (A) raw FIC_Data.zip/fic_data.txt
  (B) HobergPhillipsFIC100Builder output `fic`
  (C) the persisted step1 sample.parquet (post-filter-8)

Decisive test for H1 (merge fan-out): the step1 sample is deduped to
1 row/(gvkey,cal_yr_qtr) at filter 2 and nothing re-dups it EXCEPT a
fan-out at the filter-8 inner-merge. So duplicated (gvkey,cal_yr_qtr)
in the persisted sample > 0  <=>  fan-out CONFIRMED. No re-run of
filters 1-7 needed.
"""
from __future__ import annotations

import sys
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    print("=== STEP-1 FILTER-8 (HP-FIC100) ROOT-CAUSE DIAGNOSTIC ===\n")

    # --- (A) raw zip ---------------------------------------------------
    zp = ROOT / "inputs" / "Brexit_replication" / "HobergPhillips_FIC" / "FIC_Data.zip"
    with zipfile.ZipFile(zp) as zf:
        names = zf.namelist()
        with zf.open("fic_data.txt") as f:
            raw = pd.read_csv(BytesIO(f.read()), sep="\t")
    print(f"(A) FIC_Data.zip members: {names}")
    print(f"    fic_data.txt: {len(raw):,} rows; columns = {list(raw.columns)}")
    print(f"    year span: {raw['year'].min()}–{raw['year'].max()}")
    dup_raw = int(raw.duplicated(['gvkey', 'year']).sum())
    print(f"    duplicated (gvkey,year) in RAW file: {dup_raw:,}"
          f"   (0 ⇒ HP is 1 row/firm-year as expected)")
    print(f"    unique gvkeys (all years): {raw['gvkey'].nunique():,}")
    yr16 = raw[raw['year'].between(2010, 2016)]
    print(f"    rows 2010–2016: {len(yr16):,}; per-year:")
    print(yr16['year'].value_counts().sort_index().to_string())
    print(f"    sample rows:\n{raw.head(3).to_string()}\n")

    # --- (B) builder output -------------------------------------------
    from f1d.shared.variables.hoberg_phillips_fic100 import HobergPhillipsFIC100Builder
    fic = HobergPhillipsFIC100Builder().build(range(2010, 2017), root_path=ROOT).data
    dup_fic = int(fic.duplicated(['gvkey', 'year']).sum())
    print(f"(B) builder `fic`: {len(fic):,} rows; unique (gvkey,year)="
          f"{len(fic) - dup_fic:,}; DUP (gvkey,year)={dup_fic:,}"
          f"   <== H1 fan-out source if >0")
    print(f"    unique gvkeys: {fic['gvkey'].nunique():,}; "
          f"gvkey dtype={fic['gvkey'].dtype}, year dtype={fic['year'].dtype}")

    # --- (C) persisted step1 sample (post-filter-8) -------------------
    base = ROOT / "outputs" / "campello_rebuild" / "step1_sample"
    latest = sorted(d for d in base.iterdir() if d.is_dir())[-1]
    s = pd.read_parquet(latest / "sample.parquet")
    dup_s = int(s.duplicated(['gvkey', 'cal_yr_qtr']).sum())
    print(f"\n(C) latest step1 sample: {latest.name}")
    print(f"    rows={len(s):,}; unique (gvkey,cal_yr_qtr)="
          f"{len(s) - dup_s:,}; firms={s['gvkey'].nunique():,}")
    print(f"    *** DUPLICATED (gvkey,cal_yr_qtr) = {dup_s:,} ***")
    if dup_s > 0:
        print("    => H1 FAN-OUT CONFIRMED: filter-8 inner-merge multiplied "
              "firm-quarters (fic not unique on (gvkey,year)).")
        ex = s[s.duplicated(['gvkey', 'cal_yr_qtr'], keep=False)].sort_values(
            ['gvkey', 'cal_yr_qtr']).head(8)
        print(f"    example duplicated rows:\n{ex.to_string()}")
    else:
        print("    => H1 FAN-OUT REFUTED: sample is 1 row/(gvkey,cal_yr_qtr). "
              "The +3,170 is genuine HP coverage breadth, not inflation.")
        print(f"    fic100_industry_id nulls: {int(s['fic100_industry_id'].isna().sum()):,}")
        print(f"    distinct FIC100 industries in sample: "
              f"{s['fic100_industry_id'].nunique():,}")


if __name__ == "__main__":
    main()
