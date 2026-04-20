#!/usr/bin/env python3
"""
Call-level correlation matrix for {Mgr, CEO, NonCEO_Mgr} x {QA, Pres} Uncertainty measures.

Reads Stage 2.2 outputs directly (already call-level pcts) — no flag_speakers
re-run needed. Emits Pearson + Spearman correlation matrices as CSV + PNG.

Measures (pipeline names → thesis names):
    Manager_QA_Uncertainty_pct       = UncAnsMgr
    Manager_Pres_Uncertainty_pct     = UncPreMgr
    CEO_QA_Uncertainty_pct           = UncAnsCEO
    CEO_Pres_Uncertainty_pct         = UncPreCEO
    NonCEO_Manager_QA_Uncertainty_pct   = UncAnsNoCEO
    NonCEO_Manager_Pres_Uncertainty_pct = UncPreNoCEO
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE22_DIR = REPO_ROOT / "outputs" / "2_Textual_Analysis" / "2.2_Variables" / "2026-04-09_223627"

MEASURES = {
    "UncAnsCEO":    "CEO_QA_Uncertainty_pct",
    "UncAnsMgr":    "Manager_QA_Uncertainty_pct",
    "UncAnsNoCEO":  "NonCEO_Manager_QA_Uncertainty_pct",
    "UncPreCEO":    "CEO_Pres_Uncertainty_pct",
    "UncPreMgr":    "Manager_Pres_Uncertainty_pct",
    "UncPreNoCEO":  "NonCEO_Manager_Pres_Uncertainty_pct",
}
DISPLAY_ORDER = ["UncAnsCEO", "UncAnsNoCEO", "UncAnsMgr", "UncPreCEO", "UncPreNoCEO", "UncPreMgr"]


def load_calls() -> pd.DataFrame:
    files = sorted(STAGE22_DIR.glob("linguistic_variables_*.parquet"))
    dfs = []
    wanted_cols = ["file_name", "start_date", "gvkey"] + list(MEASURES.values())
    for f in files:
        dfs.append(pd.read_parquet(f, columns=wanted_cols))
    df = pd.concat(dfs, ignore_index=True)
    # Rename to thesis names
    df = df.rename(columns={v: k for k, v in MEASURES.items()})
    df["year"] = pd.to_datetime(df["start_date"]).dt.year
    return df


def save_heatmap(mat: pd.DataFrame, title: str, out_path: Path, cmap="RdBu_r"):
    mat = mat.reindex(index=DISPLAY_ORDER, columns=DISPLAY_ORDER)
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(
        mat,
        ax=ax,
        cmap=cmap,
        center=0,
        vmin=-1, vmax=1,
        annot=True,
        fmt=".3f",
        annot_kws={"size": 10, "weight": "bold"},
        square=True,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Correlation", "shrink": 0.8},
    )
    ax.set_title(title, fontsize=12, pad=12)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path.name}")


def main():
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = REPO_ROOT / "outputs" / "adhoc" / f"cohort_correlations_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output: {out_dir}")

    print("\nLoading Stage 2.2 call-level measures (2002-2018)...")
    df = load_calls()
    print(f"  Total calls: {len(df):,}  across years {df['year'].min()}-{df['year'].max()}")

    # Report null counts per measure (some calls may be missing CEO/NoCEO if no matching speakers)
    print("\nPer-measure coverage:")
    for m in DISPLAY_ORDER:
        pct = 100.0 * df[m].notna().mean()
        print(f"  {m:14s}  n_nonnull={df[m].notna().sum():>7,}  ({pct:.1f}%)")

    # Pairwise-complete correlations
    mats = {}
    for method in ("pearson", "spearman"):
        mat = df[DISPLAY_ORDER].corr(method=method, min_periods=1000)
        mats[method] = mat
        mat.to_csv(out_dir / f"corr_{method}_pooled.csv")
        print(f"\n{method.upper()} correlation matrix (pooled, pairwise-complete):")
        print(mat.round(3).to_string())

    # Heatmaps
    save_heatmap(
        mats["pearson"],
        "Pearson correlations — Mgr/CEO/NonCEO_Mgr Uncertainty measures\n(call-level, pooled 2002-2018, pairwise-complete)",
        out_dir / "viz_corr_pearson.png",
    )
    save_heatmap(
        mats["spearman"],
        "Spearman rank correlations — Mgr/CEO/NonCEO_Mgr Uncertainty measures\n(call-level, pooled 2002-2018, pairwise-complete)",
        out_dir / "viz_corr_spearman.png",
    )

    # Sample-size matrix (how many pairwise-complete obs per cell)
    n_mat = pd.DataFrame(index=DISPLAY_ORDER, columns=DISPLAY_ORDER, dtype=int)
    for a in DISPLAY_ORDER:
        for b in DISPLAY_ORDER:
            n_mat.loc[a, b] = int(df[[a, b]].dropna().shape[0])
    n_mat.to_csv(out_dir / "corr_sample_sizes.csv")

    # Per-year Pearson (uncertainty in Ans context only — 3x3 for cleanness)
    print("\nPer-year Pearson (UncAns only 3x3):")
    ans3 = ["UncAnsCEO", "UncAnsNoCEO", "UncAnsMgr"]
    yearly_corr_rows = []
    for year, grp in df.groupby("year"):
        n = grp[ans3].dropna().shape[0]
        if n < 100:
            continue
        c = grp[ans3].corr(method="pearson")
        yearly_corr_rows.append({
            "year": year, "n": n,
            "CEO_NoCEO": c.loc["UncAnsCEO", "UncAnsNoCEO"],
            "CEO_Mgr":   c.loc["UncAnsCEO", "UncAnsMgr"],
            "NoCEO_Mgr": c.loc["UncAnsNoCEO", "UncAnsMgr"],
        })
    yearly_corr = pd.DataFrame(yearly_corr_rows)
    yearly_corr.to_csv(out_dir / "corr_pearson_yearly_ans.csv", index=False)
    print(yearly_corr.round(3).to_string(index=False))

    # Summary report
    p = mats["pearson"]
    s = mats["spearman"]
    lines = [
        "# Cohort Measure Correlation Matrix",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Stage 2.2 source:** `{STAGE22_DIR.name}`",
        f"**Calls:** {len(df):,}  ({df['year'].min()}-{df['year'].max()})",
        "",
        "## Measures",
        "",
        "| Thesis name | Pipeline column |",
        "|---|---|",
    ]
    for k, v in MEASURES.items():
        lines.append(f"| `{k}` | `{v}` |")

    lines += [
        "",
        "## Pearson correlation (pooled)",
        "",
        "| | " + " | ".join(DISPLAY_ORDER) + " |",
        "|---" + "|---" * len(DISPLAY_ORDER) + "|",
    ]
    for a in DISPLAY_ORDER:
        row = [f"**{a}**"] + [f"{p.loc[a, b]:.3f}" for b in DISPLAY_ORDER]
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "## Spearman correlation (pooled)",
        "",
        "| | " + " | ".join(DISPLAY_ORDER) + " |",
        "|---" + "|---" * len(DISPLAY_ORDER) + "|",
    ]
    for a in DISPLAY_ORDER:
        row = [f"**{a}**"] + [f"{s.loc[a, b]:.3f}" for b in DISPLAY_ORDER]
        lines.append("| " + " | ".join(row) + " |")

    # Key observations block
    lines += [
        "",
        "## Key pairs (H1.r relevant)",
        "",
        f"- `corr(UncAnsCEO, UncAnsMgr)`   = **{p.loc['UncAnsCEO', 'UncAnsMgr']:.3f}**  ← nesting driver (Mgr pool contains CEO words)",
        f"- `corr(UncAnsCEO, UncAnsNoCEO)` = **{p.loc['UncAnsCEO', 'UncAnsNoCEO']:.3f}**  ← orthogonal partition (disjoint speakers)",
        f"- `corr(UncAnsNoCEO, UncAnsMgr)` = **{p.loc['UncAnsNoCEO', 'UncAnsMgr']:.3f}**  ← partial overlap (NoCEO is subset of Mgr)",
        f"- `corr(UncPreCEO, UncPreMgr)`   = **{p.loc['UncPreCEO', 'UncPreMgr']:.3f}**",
        f"- `corr(UncPreCEO, UncPreNoCEO)` = **{p.loc['UncPreCEO', 'UncPreNoCEO']:.3f}**",
        f"- `corr(UncPreNoCEO, UncPreMgr)` = **{p.loc['UncPreNoCEO', 'UncPreMgr']:.3f}**",
        "",
        "Cross-context (QA↔Pres) correlations:",
        f"- `corr(UncAnsMgr,   UncPreMgr)`   = **{p.loc['UncAnsMgr', 'UncPreMgr']:.3f}**",
        f"- `corr(UncAnsCEO,   UncPreCEO)`   = **{p.loc['UncAnsCEO', 'UncPreCEO']:.3f}**",
        f"- `corr(UncAnsNoCEO, UncPreNoCEO)` = **{p.loc['UncAnsNoCEO', 'UncPreNoCEO']:.3f}**",
        "",
    ]

    (out_dir / "summary_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nDone. Outputs in {out_dir}")


if __name__ == "__main__":
    main()
