"""Phase A2 — Panel-filter CEO sudden-death candidates to F1D 2,429-firm panel.

Reads q{1,2A,2B,3,4}_with_gvkey.parquet, normalizes gvkey to 6-char zero-padded
string (matching F1D panel format), inner-filters on F1D panel gvkey set, writes
5 q{1,2A,2B,3,4}_panel_filtered.parquet + panel_filter_summary.json.

Usage:
    PYTHONIOENCODING=utf-8 python scripts/adhoc/panel_filter_ceo_deaths_a2.py
"""

from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "ceo_death_events"
PANEL_PATH = ROOT / "outputs" / "variables" / "h1_cash_holdings" / "2026-04-19_182724" / "h1_cash_holdings_panel.parquet"


def normalize_gvkey(s: pd.Series) -> pd.Series:
    """Cast to 6-char zero-padded string. Treat 'nan', '', NaN, '.' as null."""
    out = s.astype(str).str.strip()
    out = out.str.replace(r"\.0+$", "", regex=True)  # strip trailing .0
    out = out.where(~out.str.lower().isin(["nan", "none", "", "."]), other=pd.NA)
    out = out.where(out.isna(), other=out.str.zfill(6))
    return out


def panel_filter(label: str, src_path: Path, panel_set: set) -> dict:
    df = pd.read_parquet(src_path)
    n_in = len(df)
    df["gvkey"] = normalize_gvkey(df["gvkey"])
    n_with_gvkey = df["gvkey"].notna().sum()
    df_panel = df[df["gvkey"].isin(panel_set)].copy()
    n_in_panel = len(df_panel)

    out_path = DATA_DIR / src_path.name.replace("_with_gvkey", "_panel_filtered")
    df_panel.to_parquet(out_path, index=False)

    return {
        "label": label,
        "input_path": str(src_path),
        "output_path": str(out_path),
        "rows_input": int(n_in),
        "rows_with_gvkey": int(n_with_gvkey),
        "rows_in_panel": int(n_in_panel),
        "panel_retention_pct_of_gvkey_matched": round(100 * n_in_panel / n_with_gvkey, 2) if n_with_gvkey else 0.0,
        "panel_retention_pct_of_input": round(100 * n_in_panel / n_in, 2) if n_in else 0.0,
    }


def main():
    panel = pd.read_parquet(PANEL_PATH)
    panel_set = set(panel["gvkey"].astype(str).str.strip().str.zfill(6).unique())
    print(f"F1D panel gvkeys: {len(panel_set)} unique")
    print()

    sources = [
        ("Q1 CapIQ KD", DATA_DIR / "q1_with_gvkey.parquet"),
        ("Q2-A action=Deceased", DATA_DIR / "q2A_with_gvkey.parquet"),
        ("Q2-B text-residual (confirm-only)", DATA_DIR / "q2B_with_gvkey.parquet"),
        ("Q3 BoardEx", DATA_DIR / "q3_with_gvkey.parquet"),
        ("Q4 ExecuComp", DATA_DIR / "q4_with_gvkey.parquet"),
    ]

    results = [panel_filter(lbl, p, panel_set) for lbl, p in sources]

    print(f"{'Source':<38} {'rows_in':>8} {'with_gvkey':>11} {'in_panel':>9} {'ret%_input':>11}")
    print("-" * 80)
    for r in results:
        print(f"{r['label']:<38} {r['rows_input']:>8} {r['rows_with_gvkey']:>11} {r['rows_in_panel']:>9} {r['panel_retention_pct_of_input']:>10.2f}%")

    primary = [r for r in results if r['label'] not in ("Q2-B text-residual (confirm-only)",)]
    primary_total = sum(r['rows_in_panel'] for r in primary)
    confirm_total = sum(r['rows_in_panel'] for r in results if r['label'] == "Q2-B text-residual (confirm-only)")
    print()
    print(f"PRIMARY in-panel total (Q1+Q2A+Q3+Q4): {primary_total}")
    print(f"Q2-B confirm-only in-panel total:       {confirm_total}")

    summary = {
        "panel_path": str(PANEL_PATH),
        "panel_gvkey_count": len(panel_set),
        "per_source": results,
        "totals": {
            "primary_in_panel": int(primary_total),
            "q2b_confirm_only_in_panel": int(confirm_total),
        },
    }
    out_json = DATA_DIR / "panel_filter_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nWrote: {out_json}")


if __name__ == "__main__":
    main()
