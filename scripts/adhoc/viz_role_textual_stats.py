#!/usr/bin/env python3
"""
Visualizations for role_textual_summary_stats outputs (per-raw-role, no buckets).
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


def _load_density(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path, index_col=0)


def fig_heatmap_triptych(out_dir: Path):
    mgr = _load_density(out_dir / "t10_year_ff12_density.csv")
    ceo = _load_density(out_dir / "t10_year_ff12_density_ceo.csv")
    noceo = _load_density(out_dir / "t10_year_ff12_density_noceo.csv")

    def core(df):
        c = df.drop(index="col_mean", errors="ignore").drop(columns="row_mean", errors="ignore")
        c.columns = [f"{int(k)}:{FF12_NAMES.get(int(k), '?')}" for k in c.columns]
        return c

    mats = {"Mgr": core(mgr), "CEO": core(ceo), "NonCEO_Mgr": core(noceo)}
    flat_mgr = mats["Mgr"].values.flatten()
    flat_mgr = flat_mgr[~np.isnan(flat_mgr)]
    vmin, vmax = np.quantile(flat_mgr, [0.05, 0.95])

    fig, axes = plt.subplots(1, 3, figsize=(18, 7), sharey=True)
    for ax, (cohort, mat) in zip(axes, mats.items()):
        sns.heatmap(
            mat, ax=ax, cmap="YlOrRd", vmin=vmin, vmax=vmax,
            annot=True, fmt=".2f", annot_kws={"size": 7},
            cbar_kws={"label": "Pooled Unc %"},
            linewidths=0.3, linecolor="white",
        )
        ax.set_title(f"{cohort} — Uncertainty % (Year × FF12, Mgr-rank-locked)", fontsize=11)
        ax.set_xlabel("FF12 Industry (most→least uncertain)")
        ax.set_ylabel("Year (most→least uncertain)")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        ax.tick_params(axis="y", labelsize=8)

    fig.suptitle(
        "Year × FF12 uncertainty density (pooled Unc_count/tokens, 2002–2018)",
        fontsize=13, y=1.02,
    )
    fig.tight_layout()
    path = out_dir / "viz_t10_density_triptych.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")


def fig_top_roles_bar(out_dir: Path, top_n: int = 30):
    """Top-N raw roles (Mgr cohort) — turn share + uncertainty %."""
    mgr = pd.read_csv(out_dir / "T_roles_mgr.csv")
    top = mgr.head(top_n).iloc[::-1]  # reverse for horizontal bar (top at top)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10), sharey=True)
    y = np.arange(len(top))

    # Panel A: share of Mgr turns
    colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(top)))
    ax1.barh(y, top["share_turns_pct"].values, color=colors, edgecolor="white")
    ax1.set_yticks(y)
    labels = [(str(r) if str(r) != "nan" else "(empty)") for r in top["role"].values]
    ax1.set_yticklabels(labels, fontsize=9)
    ax1.set_xlabel("% of Mgr turns")
    ax1.set_title(f"Top {top_n} raw roles — turn share of Mgr pool")
    ax1.grid(axis="x", alpha=0.3)
    for i, v in enumerate(top["share_turns_pct"].values):
        ax1.annotate(f"{v:.2f}%", xy=(v, i), xytext=(4, 0),
                     textcoords="offset points", va="center", fontsize=8)

    # Panel B: pooled uncertainty %
    ax2.barh(y, top["pooled_uncertainty_pct"].values, color=colors, edgecolor="white")
    ax2.set_xlabel("Pooled Uncertainty %")
    ax2.set_title(f"Top {top_n} raw roles — pooled Unc %")
    ax2.grid(axis="x", alpha=0.3)
    # Vertical reference: Mgr overall pooled unc
    total_tokens = mgr["total_tokens"].sum()
    total_unc = mgr["Uncertainty_count_sum"].sum()
    overall = 100.0 * total_unc / max(total_tokens, 1)
    ax2.axvline(overall, color="red", linestyle="--", linewidth=1.2, alpha=0.7,
                label=f"Mgr overall: {overall:.3f}%")
    ax2.legend(loc="lower right", fontsize=9)
    for i, v in enumerate(top["pooled_uncertainty_pct"].values):
        ax2.annotate(f"{v:.2f}", xy=(v, i), xytext=(4, 0),
                     textcoords="offset points", va="center", fontsize=8)

    fig.tight_layout()
    path = out_dir / "viz_top_roles_mgr.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")


def fig_long_tail(out_dir: Path):
    """Lorenz-style cumulative curve — role-rank × cumulative share."""
    mgr = pd.read_csv(out_dir / "T_roles_mgr.csv")
    ceo = pd.read_csv(out_dir / "T_roles_ceo.csv")
    noceo = pd.read_csv(out_dir / "T_roles_nonceo_mgr.csv")

    fig, ax = plt.subplots(figsize=(11, 7))
    for label, df, color in [
        ("Mgr", mgr, "#2c3e50"),
        ("CEO", ceo, "#e67e22"),
        ("NonCEO_Mgr", noceo, "#16a085"),
    ]:
        df = df.sort_values("n_turns", ascending=False).reset_index(drop=True)
        cum = df["share_turns_pct"].cumsum()
        ax.plot(np.arange(1, len(df) + 1), cum.values, color=color, linewidth=2,
                label=f"{label} ({len(df):,} roles)")

    ax.set_xscale("log")
    ax.set_xlabel("Role rank (log scale)")
    ax.set_ylabel("Cumulative % of cohort turns")
    ax.set_title("Long-tail distribution: cumulative turn share by role rank\n(pooled 2002–2018)")
    ax.axhline(80, color="grey", linestyle=":", alpha=0.5, label="80% threshold")
    ax.axhline(95, color="grey", linestyle="--", alpha=0.5, label="95% threshold")
    ax.grid(alpha=0.3, which="both")
    ax.legend(loc="lower right", fontsize=10)

    # Annotate role-count-to-hit-80%
    for label, df, color in [
        ("Mgr", mgr, "#2c3e50"),
        ("CEO", ceo, "#e67e22"),
        ("NonCEO_Mgr", noceo, "#16a085"),
    ]:
        df = df.sort_values("n_turns", ascending=False).reset_index(drop=True)
        cum = df["share_turns_pct"].cumsum()
        try:
            n80 = (cum >= 80).idxmax() + 1
            ax.annotate(
                f"{label}: {n80} roles → 80%",
                xy=(n80, 80),
                xytext=(n80 * 1.3, 60 - ["Mgr", "CEO", "NonCEO_Mgr"].index(label) * 6),
                fontsize=9, color=color,
                arrowprops=dict(arrowstyle="->", color=color, alpha=0.6),
            )
        except Exception:
            pass

    fig.tight_layout()
    path = out_dir / "viz_long_tail.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")


def fig_distribution_box(out_dir: Path):
    t9 = pd.read_csv(out_dir / "t9_distribution_moments.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    ax = axes[0]
    cohorts = t9["cohort"].tolist()
    x = np.arange(len(cohorts))
    ax.vlines(x, t9["p5"], t9["p95"], color="lightgrey", linewidth=6, label="5-95%")
    ax.vlines(x, t9["p25"], t9["p75"], color="steelblue", linewidth=16, label="25-75%")
    ax.scatter(x, t9["p50"], color="white", marker="_", s=100, zorder=3, label="median")
    ax.scatter(x, t9["mean"], color="red", marker="D", s=40, zorder=4, label="mean")
    ax.set_xticks(x)
    ax.set_xticklabels(cohorts)
    ax.set_ylabel("Per-turn Uncertainty %")
    ax.set_title("A. Per-turn Uncertainty % (2018)\nwhiskers 5-95%, box 25-75%")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    ax2 = axes[1]
    ax2.axis("off")
    cells = []
    for _, r in t9.iterrows():
        cells.append([
            r["cohort"], f"{int(r['n']):,}", f"{r['mean']:.3f}", f"{r['sd']:.3f}",
            f"{r['p50']:.3f}", f"{r['p75']:.3f}", f"{r['p95']:.3f}", f"{r['p99']:.3f}",
            f"{r['skew']:.1f}", f"{r['kurtosis']:.0f}",
        ])
    hdr = ["Cohort", "n", "mean", "sd", "p50", "p75", "p95", "p99", "skew", "kurt"]
    tbl = ax2.table(cellText=cells, colLabels=hdr, loc="center", cellLoc="center")
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
        adhoc = REPO_ROOT / "outputs" / "adhoc"
        candidates = sorted(adhoc.glob("role_textual_stats_*"), reverse=True)
        if not candidates:
            print("No role_textual_stats_* dir found", file=sys.stderr)
            sys.exit(1)
        out_dir = candidates[0]

    print(f"Reading from: {out_dir}")
    sns.set_theme(style="whitegrid", context="paper")

    fig_heatmap_triptych(out_dir)
    fig_top_roles_bar(out_dir, top_n=30)
    fig_long_tail(out_dir)
    fig_distribution_box(out_dir)

    print(f"\nDone. 4 PNGs in {out_dir}")


if __name__ == "__main__":
    main()
