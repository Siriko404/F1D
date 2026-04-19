#!/usr/bin/env python3
"""
Visualizations for role_textual_summary_stats outputs.
Reads CSVs produced by role_textual_summary_stats.py and emits PNG figures.
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

BUCKET_ORDER = [
    "Empty", "CEO-title", "CFO-title", "COO-title", "Pres/Chair",
    "VP-exec", "Director", "Treasurer", "IR", "GeneralCounsel",
    "OtherExec", "Unmatched",
]


def _load_density(csv_path: Path) -> pd.DataFrame:
    """Load a t10 density matrix; first col is year index, last col is row_mean."""
    df = pd.read_csv(csv_path, index_col=0)
    return df


def fig_heatmap_triptych(out_dir: Path):
    """3-panel year×FF12 heatmap: Mgr / CEO / NonCEO_Mgr."""
    mgr = _load_density(out_dir / "t10_year_ff12_density.csv")
    ceo = _load_density(out_dir / "t10_year_ff12_density_ceo.csv")
    noceo = _load_density(out_dir / "t10_year_ff12_density_noceo.csv")

    # Drop marginal row/col from display matrices
    def core(df):
        core = df.drop(index="col_mean", errors="ignore")
        core = core.drop(columns="row_mean", errors="ignore")
        # Rename columns to FF12 short names
        core.columns = [f"{int(c)}:{FF12_NAMES.get(int(c), '?')}" for c in core.columns]
        return core

    mats = {"Mgr": core(mgr), "CEO": core(ceo), "NonCEO_Mgr": core(noceo)}

    # Shared color scale: use percentile bounds for Mgr (primary)
    flat_mgr = mats["Mgr"].values.flatten()
    flat_mgr = flat_mgr[~np.isnan(flat_mgr)]
    vmin, vmax = np.quantile(flat_mgr, [0.05, 0.95])

    fig, axes = plt.subplots(1, 3, figsize=(18, 7), sharey=True)
    for ax, (cohort, mat) in zip(axes, mats.items()):
        sns.heatmap(
            mat,
            ax=ax,
            cmap="YlOrRd",
            vmin=vmin,
            vmax=vmax,
            annot=True,
            fmt=".2f",
            annot_kws={"size": 7},
            cbar_kws={"label": "Pooled Unc %"},
            linewidths=0.3,
            linecolor="white",
        )
        ax.set_title(f"{cohort} — Pooled Uncertainty % by Year × FF12\n(rank-locked to Mgr ordering)", fontsize=11)
        ax.set_xlabel("FF12 Industry (most→least uncertain, Mgr-ordered)")
        ax.set_ylabel("Year (most→least uncertain, Mgr-ordered)")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        ax.tick_params(axis="y", labelsize=8)

    fig.suptitle(
        "Uncertainty % density: Year × Industry × Cohort (2002–2018, pooled Uncertainty_count/total_tokens)",
        fontsize=13, y=1.02,
    )
    fig.tight_layout()
    path = out_dir / "viz_t10_density_triptych.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")


def fig_bucket_bar(out_dir: Path):
    """T2 bucket × cohort: pooled Unc % + turn share."""
    t2 = pd.read_csv(out_dir / "t2_bucket_by_cohort.csv")
    # pivot
    unc = t2.pivot(index="role_bucket", columns="cohort", values="pooled_uncertainty_pct").reindex(BUCKET_ORDER)
    turns = t2.pivot(index="role_bucket", columns="cohort", values="n_turns").reindex(BUCKET_ORDER)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)

    # Panel A: pooled Unc %
    unc_plot = unc[["Mgr", "CEO", "NonCEO_Mgr"]]
    unc_plot.plot(kind="bar", ax=ax1, color=["#2c3e50", "#e67e22", "#16a085"], width=0.8)
    ax1.set_ylabel("Pooled Uncertainty %")
    ax1.set_title("A. Uncertainty % by role bucket × cohort (pooled 2002–2018)")
    ax1.axhline(
        y=unc.loc[BUCKET_ORDER, "Mgr"].mean() if "Mgr" in unc.columns else 0,
        color="grey", linestyle="--", linewidth=0.8, alpha=0.5,
        label="Mgr bucket mean",
    )
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(axis="y", alpha=0.3)

    # Panel B: Mgr turn share (log scale)
    turns_mgr = turns["Mgr"].fillna(0)
    turns_mgr.plot(kind="bar", ax=ax2, color="#34495e", width=0.6)
    ax2.set_ylabel("Mgr turns (log scale)")
    ax2.set_yscale("log")
    ax2.set_title("B. Mgr turn count by bucket")
    ax2.set_xlabel("Role bucket")
    ax2.grid(axis="y", alpha=0.3, which="both")
    # Annotate turns on top
    for i, v in enumerate(turns_mgr.values):
        if v > 0:
            ax2.annotate(f"{int(v):,}", xy=(i, v), xytext=(0, 3), textcoords="offset points",
                         ha="center", fontsize=7)
    plt.setp(ax2.get_xticklabels(), rotation=40, ha="right")

    fig.tight_layout()
    path = out_dir / "viz_t2_bucket_bar.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")


def fig_year_trend(out_dir: Path):
    """T3 bucket × year × Mgr cohort time series for top-N buckets by turn volume."""
    t3 = pd.read_csv(out_dir / "t3_bucket_by_year.csv")
    mgr = t3[t3["cohort"] == "Mgr"].copy()
    # Rank buckets by total Mgr turns → pick top 8 by volume for legibility
    vols = mgr.groupby("role_bucket")["n_turns"].sum().sort_values(ascending=False)
    top8 = vols.head(8).index.tolist()
    sub = mgr[mgr["role_bucket"].isin(top8)]

    piv = sub.pivot(index="year", columns="role_bucket", values="pooled_uncertainty_pct")
    piv = piv[top8]  # preserve volume-rank order

    fig, ax = plt.subplots(figsize=(12, 7))
    # Sensible palette
    cmap = plt.get_cmap("tab10")
    for i, col in enumerate(piv.columns):
        ax.plot(piv.index, piv[col], marker="o", linewidth=1.8, markersize=5,
                color=cmap(i), label=col)

    # Overlay Mgr overall (aggregate)
    total = mgr.groupby("year").apply(
        lambda g: 100.0 * g["Uncertainty_count_sum"].sum() / max(g["total_tokens"].sum(), 1)
    )
    ax.plot(total.index, total.values, color="black", linewidth=2.5, linestyle="--",
            marker="s", markersize=5, label="Mgr (all buckets)")

    ax.set_xlabel("Year")
    ax.set_ylabel("Pooled Uncertainty %")
    ax.set_title("Uncertainty % trend by role bucket (Mgr cohort, 2002–2018)\nTop-8 buckets by turn volume + overall Mgr")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", ncol=2, fontsize=9)
    ax.set_xticks(list(piv.index))
    plt.setp(ax.get_xticklabels(), rotation=45)

    # Shade GFC
    ax.axvspan(2008, 2009, alpha=0.08, color="red", label=None)
    ax.annotate("GFC", xy=(2008.5, ax.get_ylim()[1] * 0.97), ha="center", fontsize=8, color="red")

    fig.tight_layout()
    path = out_dir / "viz_t3_year_trend.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")


def fig_distribution_box(out_dir: Path):
    """T9 distribution moments — violin-style sampling from 2018 raw data."""
    # We don't persist per-turn data, but T9 has quantile moments. Build a box from moments.
    t9 = pd.read_csv(out_dir / "t9_distribution_moments.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    # Panel A: mean + sd bars + p-quantile whiskers
    ax = axes[0]
    cohorts = t9["cohort"].tolist()
    means = t9["mean"].values
    sds = t9["sd"].values
    p5 = t9["p5"].values
    p95 = t9["p95"].values
    p25 = t9["p25"].values
    p75 = t9["p75"].values
    med = t9["p50"].values

    x = np.arange(len(cohorts))
    # Whiskers p5–p95
    ax.vlines(x, p5, p95, color="lightgrey", linewidth=6, label="5-95%")
    # Box p25–p75
    ax.vlines(x, p25, p75, color="steelblue", linewidth=16, label="25-75%")
    # Median
    ax.scatter(x, med, color="white", marker="_", s=100, zorder=3, label="median")
    # Mean
    ax.scatter(x, means, color="red", marker="D", s=40, zorder=4, label="mean")
    ax.set_xticks(x)
    ax.set_xticklabels(cohorts)
    ax.set_ylabel("Per-turn Uncertainty %")
    ax.set_title("A. Per-turn Uncertainty % distribution (2018)\nwhiskers 5-95%, box 25-75%")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Panel B: compare means/sd as table-style annotations
    ax2 = axes[1]
    ax2.axis("off")
    cells = []
    for _, r in t9.iterrows():
        cells.append([
            r["cohort"],
            f"{int(r['n']):,}",
            f"{r['mean']:.3f}",
            f"{r['sd']:.3f}",
            f"{r['p50']:.3f}",
            f"{r['p75']:.3f}",
            f"{r['p95']:.3f}",
            f"{r['p99']:.3f}",
            f"{r['skew']:.1f}",
            f"{r['kurtosis']:.0f}",
        ])
    hdr = ["Cohort", "n", "mean", "sd", "p50", "p75", "p95", "p99", "skew", "kurt"]
    tbl = ax2.table(
        cellText=cells,
        colLabels=hdr,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.6)
    ax2.set_title("B. Distribution moments (2018 per-turn Uncertainty %)", pad=20)

    fig.tight_layout()
    path = out_dir / "viz_t9_distributions.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")


def main():
    if len(sys.argv) > 1:
        out_dir = Path(sys.argv[1])
    else:
        # Default to latest
        adhoc = REPO_ROOT / "outputs" / "adhoc"
        candidates = sorted(adhoc.glob("role_textual_stats_*"), reverse=True)
        if not candidates:
            print("No role_textual_stats_* dir found", file=sys.stderr)
            sys.exit(1)
        out_dir = candidates[0]

    print(f"Reading from: {out_dir}")
    sns.set_theme(style="whitegrid", context="paper")

    fig_heatmap_triptych(out_dir)
    fig_bucket_bar(out_dir)
    fig_year_trend(out_dir)
    fig_distribution_box(out_dir)

    print(f"\nDone. 4 PNGs in {out_dir}")


if __name__ == "__main__":
    main()
