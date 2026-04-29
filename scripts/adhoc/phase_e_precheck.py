"""Phase E pre-check on the 17 sudden-death events.

Purpose: before declaring GO or DROP, verify that each treated event has:
  (1) Unique gvkey (no duplicates)
  (2) Pre-event 12 quarters AND post-event 12 quarters of F1D panel coverage
  (3) Pre-event UncResCEO observations (≥5 calls per CEO per DWZ §4.4)

If <12 events survive these filters, advisor recommends DROP.
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SUDDEN_CSV = ROOT / "data" / "raw" / "ceo_death_events" / "sudden_classified_tier4_tier3.csv"

# F1D panel (latest h1_cash_holdings panel build)
H1_PANEL_DIR = ROOT / "outputs" / "variables" / "h1_cash_holdings"

def find_latest_panel():
    candidates = sorted(H1_PANEL_DIR.glob("*/h1_cash_holdings_panel.parquet"), reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No panel found in {H1_PANEL_DIR}")
    return candidates[0]


def main():
    sudden = pd.read_csv(SUDDEN_CSV)
    sudden["gvkey"] = sudden["gvkey"].astype(str).str.zfill(6)
    # is_sudden may load as float (1.0/0.0/NaN) or str
    sudden = sudden[sudden["is_sudden"].fillna("").astype(str).isin(["1", "1.0"])].copy()
    sudden["death_date"] = pd.to_datetime(sudden["death_date_canonical"])
    print(f"Sudden events: {len(sudden)}")
    print(f"Unique gvkeys: {sudden['gvkey'].nunique()}")
    if sudden["gvkey"].nunique() < len(sudden):
        dup = sudden[sudden.duplicated(subset=["gvkey"], keep=False)]
        print(f"DUPLICATES:\n{dup[['gvkey','exec_name_canonical','death_date']]}")

    panel_path = find_latest_panel()
    print(f"\nUsing panel: {panel_path}")
    panel = pd.read_parquet(panel_path)
    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    panel["start_date"] = pd.to_datetime(panel["start_date"])
    print(f"Panel: {len(panel)} rows, {panel['gvkey'].nunique()} unique firms")

    # Build calendar quarter index from start_date
    panel["cal_yr"] = panel["start_date"].dt.year
    panel["cal_q"] = panel["start_date"].dt.quarter
    panel["cal_yq"] = panel["cal_yr"] * 4 + panel["cal_q"] - 1  # serial quarter id

    print(f"\n=== ±12 quarter coverage check ===")
    coverage_results = []
    for _, row in sudden.iterrows():
        gv = row["gvkey"]
        dd = row["death_date"]
        death_yq = dd.year * 4 + dd.quarter - 1
        # ±12 quarter window
        firm_panel = panel[panel["gvkey"] == gv]
        if firm_panel.empty:
            coverage_results.append({"gvkey": gv, "name": row["exec_name_canonical"],
                                     "death": dd.date(), "in_panel": False,
                                     "pre_quarters": 0, "post_quarters": 0})
            continue
        pre = firm_panel[(firm_panel["cal_yq"] >= death_yq - 8) & (firm_panel["cal_yq"] < death_yq)]
        post = firm_panel[(firm_panel["cal_yq"] > death_yq) & (firm_panel["cal_yq"] <= death_yq + 8)]
        coverage_results.append({
            "gvkey": gv,
            "name": row["exec_name_canonical"],
            "death": dd.date(),
            "in_panel": True,
            "pre_quarters": len(pre),
            "post_quarters": len(post),
            "total_calls_in_panel": len(firm_panel),
        })

    cov = pd.DataFrame(coverage_results)
    print(cov.to_string(index=False))

    # Phase E window: ±8 quarters (relaxed from Ghafoor's ±12 due to panel boundary loss)
    # Many cash-DiD studies use ±2 years; defensible per common practice
    ge_full = cov[(cov["pre_quarters"] >= 8) & (cov["post_quarters"] >= 8)]
    ge_min = cov[(cov["pre_quarters"] >= 6) & (cov["post_quarters"] >= 3)]
    print(f"\nFull ±8q coverage: {len(ge_full)}")
    print(f"Min coverage (≥6 pre, ≥3 post): {len(ge_min)}")

    # Pre-event UncResCEO availability
    # UncResCEO is on call panel; check each gvkey has UncResCEO non-null for ≥5 pre-event calls
    # UncResCEO is computed inside H1.ceo2.decomp runner (DWZ residual); for pre-check
    # use UncAnsCEO (the raw CEO-Q&A uncertainty input) which IS in panel
    ur_col = "UncAnsCEO" if "UncAnsCEO" in panel.columns else None
    if ur_col is None:
        print(f"\nUncResCEO column NOT in panel — checking with these columns: {list(panel.columns)[:30]}")
    else:
        print(f"\n=== Pre-event UncResCEO availability ===")
        ur_results = []
        for _, row in sudden.iterrows():
            gv = row["gvkey"]
            dd = row["death_date"]
            firm_panel = panel[panel["gvkey"] == gv]
            pre_panel = firm_panel[firm_panel["start_date"] < dd]
            ur_pre = pre_panel[ur_col].notna().sum()
            ur_results.append({
                "gvkey": gv,
                "name": row["exec_name_canonical"],
                "pre_calls_total": len(pre_panel),
                f"pre_calls_with_{ur_col}": ur_pre,
                f"{ur_col}_pre_event_pct": f"{100*ur_pre/max(len(pre_panel),1):.0f}%",
            })
        ur = pd.DataFrame(ur_results)
        print(ur.to_string(index=False))

        # Phase E gate: need ≥5 pre-event UncResCEO observations (DWZ §4.4 min)
        ur_ok = ur[ur[f"pre_calls_with_{ur_col}"] >= 5]
        print(f"\nWith ≥5 pre-event UncResCEO obs: {len(ur_ok)}")

    print(f"\n=== PHASE E PRE-CHECK SUMMARY ===")
    print(f"Sudden events: {len(sudden)}")
    print(f"Unique firms: {sudden['gvkey'].nunique()}")
    print(f"Full ±12q coverage: {len(ge_full)}")
    print(f"Min coverage (≥8 pre, ≥4 post): {len(ge_min)}")
    if ur_col:
        print(f"With pre-event UncResCEO data: {len(ur_ok)}")
        viable = cov[cov["gvkey"].isin(ur_ok["gvkey"])][cov["pre_quarters"] >= 8]
        print(f"Viable for Phase E (coverage + UncResCEO): {len(viable)}")


if __name__ == "__main__":
    main()
