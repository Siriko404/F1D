#!/usr/bin/env python3
"""
Cross-panel data identity audit (one-off, 2026-04-16).

Purpose: verify that variables which appear in multiple per-suite panels
have IDENTICAL values for the same (gvkey, file_name) row across panels.

If two panels disagree on UncAnsMgr for the same call → bug
(stale panel, divergent winsorization, schema drift, etc.).

Run: python scripts/audit_cross_panel_identity.py
Output: stdout summary + written to outputs/_audits/cross_panel_identity_<ts>.txt
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Latest panel per active suite (as of 2026-04-16)
SUITE_PANELS = {
    "h1":  "outputs/variables/h1_cash_holdings/2026-04-09_224348/h1_cash_holdings_panel.parquet",
    "h2":  "outputs/variables/h2_investment/2026-03-25_224731/h2_investment_panel.parquet",
    "h4":  "outputs/variables/h4_leverage/2026-04-09_224744/h4_leverage_panel.parquet",
    "h5":  "outputs/variables/h5_dispersion/2026-03-18_184756/h5_dispersion_panel.parquet",
    "h7":  "outputs/variables/h7_illiquidity/2026-04-09_225201/h7_illiquidity_panel.parquet",
    "h11": "outputs/variables/h11_prisk_uncertainty/2026-04-09_225456/h11_prisk_uncertainty_panel.parquet",
    "h13": "outputs/variables/h13_capex/2026-04-09_230002/h13_capex_panel.parquet",
    "h14": "outputs/variables/h14_bidask_spread/2026-04-09_230354/h14_bidask_spread_panel.parquet",
    "h17": "outputs/variables/h17_repurchase_intensity/2026-04-09_231012/h17_repurchase_intensity_panel.parquet",
    "h12": "outputs/variables/h12_payout/2026-04-10_073015/h12_payout_panel.parquet",
    "h22": "outputs/variables/h22_equity_constraints/2026-04-09_231807/h22_equity_constraints_panel.parquet",
    "h23": "outputs/variables/h23_competition_uncertainty/2026-04-09_232028/h23_competition_uncertainty_panel.parquet",
    "h24": "outputs/variables/h24_h24b_h25_macro/2026-04-09_232139/h24_h24b_h25_macro_panel.parquet",
    "h18": "outputs/variables/h18_cccl_received/2026-04-09_231119/h18_cccl_received_panel.parquet",
    "h19": "outputs/variables/h19_h20_financing/2026-04-09_231346/h19_h20_financing_panel.parquet",
    "h19b":"outputs/variables/h19b_h20b_financing/2026-04-09_231450/h19b_h20b_financing_panel.parquet",
    "h11_lag": "outputs/variables/h11_prisk_uncertainty_lag/2026-04-09_225639/h11_prisk_uncertainty_lag_panel.parquet",
}

# Test variables: should be IDENTICAL across panels that contain them
# (since all are computed by shared engines from same raw inputs)
TEST_VARS = [
    "UncAnsMgr",
    "UncPreMgr",
    "UncAnsCEO",
    "UncPreCEO",
    "lnAssets",
    "TobinsQ",
    "ROA",
    "BookLev",
    "DivDummy",
    "Leverage",
    "Capex",
    "CashRatio",
]

# Tolerance for float comparison (treat <1e-9 abs diff as match)
TOL = 1e-9


def main():
    proj_root = Path(__file__).resolve().parents[1]
    out_dir = proj_root / "outputs" / "_audits"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_file = out_dir / f"cross_panel_identity_{ts}.txt"

    log_lines = []

    def log(msg=""):
        print(msg)
        log_lines.append(msg)

    log(f"Cross-panel identity audit — {ts}")
    log("=" * 80)

    # Load panels
    panels = {}
    for k, rel in SUITE_PANELS.items():
        p = proj_root / rel
        if not p.exists():
            log(f"  [MISS] {k}: {rel}")
            continue
        try:
            df = pd.read_parquet(p)
            panels[k] = df
            log(f"  [OK]   {k}: {len(df):>8,} rows × {len(df.columns):>4} cols  ({rel})")
        except Exception as e:
            log(f"  [FAIL] {k}: {e}")

    log()
    log(f"Loaded {len(panels)} / {len(SUITE_PANELS)} panels.")
    log()

    # Split panels into call-level (file_name index) vs firm-year (gvkey + fyearq)
    call_panels = {k: df for k, df in panels.items() if "file_name" in df.columns}
    fy_panels = {k: df for k, df in panels.items() if "file_name" not in df.columns}
    log(f"Call-level panels (join on (gvkey,file_name)): {list(call_panels.keys())}")
    log(f"Firm-year panels (join on (gvkey,fyearq)):     {list(fy_panels.keys())}")
    log()

    def run_pairwise(group_panels, idx_cols, group_label):
        log("=" * 80)
        log(f"PAIRWISE IDENTITY CHECK ({group_label}) — index = {idx_cols}")
        log("=" * 80)
        if len(group_panels) < 2:
            log("  Fewer than 2 panels in group; skipping.")
            return []

        # Discover which test variables actually appear in each panel
        var_in_panel = {v: [k for k, df in group_panels.items() if v in df.columns] for v in TEST_VARS}
        log("Test variable presence:")
        for v, ks in var_in_panel.items():
            log(f"  {v:<12}  {len(ks):>2} panels: {ks}")
        log()
        log(f"{'Var':<12} {'A':<8} {'B':<8} {'N_overlap':>10} {'N_mismatch':>11} {'Pct_mis':>8} {'MaxAbsDiff':>14}")
        log("-" * 80)

        issues = []
        for v in TEST_VARS:
            keys = var_in_panel[v]
            if len(keys) < 2:
                continue
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    a, b = keys[i], keys[j]
                    cols = idx_cols + [v]
                    if not all(c in group_panels[a].columns for c in idx_cols) or \
                       not all(c in group_panels[b].columns for c in idx_cols):
                        continue
                    pa = group_panels[a][cols].dropna(subset=[v])
                    pb = group_panels[b][cols].dropna(subset=[v])
                    merged = pa.merge(pb, on=idx_cols, suffixes=("_a", "_b"))
                    if len(merged) == 0:
                        log(f"{v:<12} {a:<8} {b:<8} {0:>10} {'-':>11} {'-':>8} {'-':>14}  [no overlap]")
                        continue
                    diff = (merged[f"{v}_a"] - merged[f"{v}_b"]).abs()
                    n_mis = int((diff > TOL).sum())
                    pct = 100.0 * n_mis / len(merged)
                    max_d = float(diff.max())
                    flag = ""
                    if n_mis > 0:
                        flag = "  [!] MISMATCH"
                        issues.append((group_label, v, a, b, n_mis, len(merged), max_d))
                    log(f"{v:<12} {a:<8} {b:<8} {len(merged):>10,} {n_mis:>11,} {pct:>7.2f}% {max_d:>14.6g}{flag}")
        log()
        return issues

    issues = []
    issues.extend(run_pairwise(call_panels, ["gvkey", "file_name"], "CALL-LEVEL"))
    # Firm-year panels: try (gvkey, fyearq) — fall back to (gvkey, fyear) if needed
    if fy_panels:
        sample_fy = next(iter(fy_panels.values()))
        fy_idx = None
        for cand in [["gvkey", "fyearq"], ["gvkey", "fyear"], ["gvkey", "cal_yr"]]:
            if all(c in sample_fy.columns for c in cand):
                fy_idx = cand
                break
        if fy_idx:
            issues.extend(run_pairwise(fy_panels, fy_idx, "FIRM-YEAR"))
        else:
            log(f"Firm-year panels: no shared index found. Cols of {list(fy_panels.keys())[0]}: {list(sample_fy.columns)[:15]}")

    log()
    log("=" * 80)
    log(f"SUMMARY: {len(issues)} issues found")
    log("=" * 80)
    if issues:
        log("Mismatched (group, var, panel_a, panel_b, n_mis, n_overlap, max_abs_diff):")
        for it in issues:
            log(f"  {it}")
    else:
        log("All shared variables identical across all overlapping panels.")

    out_file.write_text("\n".join(log_lines))
    log(f"\nReport written to: {out_file}")


if __name__ == "__main__":
    main()
