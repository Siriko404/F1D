#!/usr/bin/env python3
"""
Time-series: Uncertainty % over years, one line per FF12 industry.
3-panel stacked (Mgr / CEO / NonCEO_Mgr), shared x-axis.

Reads pre-computed t10_year_ff12_density_*.csv matrices from the correlation
output dir (density CSVs were moved there from the role_textual_stats dir).
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

REPO_ROOT = Path(__file__).resolve().parents[2]

FF12_NAMES = {
    1: "NoDur", 2: "Durbl", 3: "Manuf", 4: "Enrgy", 5: "Chems",
    6: "BusEq", 7: "Telcm", 8: "Utils", 9: "Shops", 10: "Hlth",
    11: "Money", 12: "Other",
}


def load_long(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = df[df["year"] != "col_mean"].copy()
    df["year"] = df["year"].astype(int)
    if "row_mean" in df.columns:
        df = df.drop(columns="row_mean")
    df = df.sort_values("year").reset_index(drop=True)
    long = df.melt(id_vars="year", var_name="ff12_code", value_name="unc_pct")
    long["ff12_code"] = long["ff12_code"].astype(int)
    long["ff12_name"] = long["ff12_code"].map(FF12_NAMES)
    long["ff12_label"] = long["ff12_code"].astype(str) + ":" + long["ff12_name"]
    return long


def plot_panel(ax, long_df: pd.DataFrame, title: str, palette, ff12_order):
    for (code, name), color in zip(ff12_order, palette):
        sub = long_df[long_df["ff12_code"] == code].sort_values("year")
        ax.plot(sub["year"], sub["unc_pct"], marker="o", markersize=3,
                linewidth=1.4, color=color, label=f"{code}:{name}")
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Uncertainty %")
    ax.grid(alpha=0.3)
    ax.set_xlim(2001.5, 2018.5)
    ax.axvspan(2007.5, 2009.5, color="grey", alpha=0.12, zorder=0,
               label="GFC 2008-09" if title.startswith("Mgr") else None)


def main():
    if len(sys.argv) > 1:
        src_dir = Path(sys.argv[1])
    else:
        adhoc = REPO_ROOT / "outputs" / "adhoc"
        candidates = sorted(adhoc.glob("cohort_correlations_*"), reverse=True)
        if not candidates:
            print("No cohort_correlations_* dir found", file=sys.stderr)
            sys.exit(1)
        src_dir = candidates[0]

    print(f"Reading from: {src_dir}")
    sns.set_theme(style="whitegrid", context="paper")

    cohorts = [
        ("Mgr",        "t10_year_ff12_density.csv"),
        ("CEO",        "t10_year_ff12_density_ceo.csv"),
        ("NonCEO_Mgr", "t10_year_ff12_density_noceo.csv"),
    ]

    # Use Mgr column-mean ordering (most→least uncertain) to lock palette
    mgr_df = pd.read_csv(src_dir / cohorts[0][1])
    col_mean_row = mgr_df[mgr_df["year"] == "col_mean"].iloc[0].drop(["year"])
    if "row_mean" in col_mean_row.index:
        col_mean_row = col_mean_row.drop("row_mean")
    col_mean_row = col_mean_row.astype(float).sort_values(ascending=False)
    ff12_order = [(int(c), FF12_NAMES[int(c)]) for c in col_mean_row.index]
    palette = sns.color_palette("tab20", n_colors=12)

    fig, axes = plt.subplots(3, 1, figsize=(13, 11), sharex=True)
    for ax, (label, fname) in zip(axes, cohorts):
        long_df = load_long(src_dir / fname)
        plot_panel(ax, long_df, f"{label} — Uncertainty % by FF12 industry", palette, ff12_order)

    axes[-1].set_xlabel("Year")
    axes[0].legend(loc="center left", bbox_to_anchor=(1.005, 0.5),
                   fontsize=8, title="FF12 (ordered by Mgr col-mean, most→least uncertain)",
                   title_fontsize=8, frameon=True)

    fig.suptitle(
        "Uncertainty % time series by FF12 industry — pooled within (cohort × year × FF12), 2002–2018",
        fontsize=12, y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 0.86, 0.98))
    out_path = src_dir / "viz_ff12_timeseries.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path.name}")


if __name__ == "__main__":
    main()
