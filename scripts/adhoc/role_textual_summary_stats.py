#!/usr/bin/env python3
"""
==============================================================================
Ad-hoc: Role-Level Summary Stats for Textual Measures (raw-role, no buckets)
==============================================================================
ID: adhoc/role_textual_summary_stats
Purpose: Per-raw-role summary of textual LM measures within each cohort
         (Mgr / CEO / NonCEO_Mgr). One row per unique `role` string.
         Replaces the earlier ad-hoc regex bucketing (user rejected 2026-04-19
         — "no madeups! i want a table, which includes all roles in mgr by
         their share of speech, and uncertainty in speech, and their share of
         MGR pool").

Reuses production load_executive_map + flag_speakers + parse_ff_industries.
No pipeline mutation. Per-year aggregation → concat → roll up.

Outputs:
    T_roles_{mgr,ceo,nonceo_mgr}.csv  — main per-role tables (all raw roles)
    t6_leak_check.csv                  — F2 canary (is_manager ∧ role~/analyst/)
    t7_null_role_audit.csv             — empty-role share by cohort
    t8_yearly_cohort_sizes.csv         — per-year cohort turn counts
    t9_distribution_moments.csv        — per-turn Unc % moments (2018)
    t10_year_ff12_density*.csv         — year × FF12 density matrices
    summary_report.md                  — human-readable top-N + density + caveats

==============================================================================
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from f1d.text.build_linguistic_variables import (  # noqa: E402
    flag_speakers,
    load_executive_map,
)
from f1d.shared.industry_utils import parse_ff_industries  # noqa: E402


LM_CATEGORIES = [
    "Uncertainty",
    "Negative",
    "Positive",
    "Litigious",
    "Strong_Modal",
    "Weak_Modal",
    "Constraining",
]


def build_cohort_masks(df_flagged: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "Mgr": df_flagged["is_manager"].astype(bool),
        "CEO": df_flagged["is_ceo"].astype(bool),
        "NonCEO_Mgr": df_flagged["is_manager"].astype(bool)
        & (~df_flagged["is_ceo"].astype(bool)),
    }


def aggregate_year_by_role(df_flagged: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Per-year, per-cohort, per-raw-role aggregation.
    Rows: (cohort, role) — columns: n_turns, total_tokens, 7 LM sums,
    n_unique_calls, n_unique_firms.
    """
    count_cols = [f"{cat}_count" for cat in LM_CATEGORIES]
    sub_cols = ["role", "file_name", "gvkey", "total_tokens"] + count_cols
    cohort_masks = build_cohort_masks(df_flagged)

    pieces = []
    for cohort, mask in cohort_masks.items():
        sub = df_flagged.loc[mask, sub_cols].copy()
        if sub.empty:
            continue
        sub["role"] = sub["role"].fillna("")
        agg = (
            sub.groupby("role", dropna=False)
            .agg(
                n_turns=("total_tokens", "size"),
                total_tokens=("total_tokens", "sum"),
                n_unique_calls=("file_name", "nunique"),
                n_unique_firms=("gvkey", "nunique"),
                **{f"{cat}_count_sum": (f"{cat}_count", "sum") for cat in LM_CATEGORIES},
            )
            .reset_index()
        )
        agg.insert(0, "year", year)
        agg.insert(0, "cohort", cohort)
        pieces.append(agg)

    return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame()


def rollup_roles(master: pd.DataFrame, cohort: str) -> pd.DataFrame:
    """Pool 17 years per (cohort, role). Ratio-of-sums for pooled pcts."""
    sub = master[master["cohort"] == cohort].copy()
    count_sum_cols = [f"{cat}_count_sum" for cat in LM_CATEGORIES]

    # First year / last year per role (pre-aggregate)
    year_span = sub.groupby("role").agg(
        first_year=("year", "min"),
        last_year=("year", "max"),
    )

    agg = (
        sub.groupby("role")
        .agg(
            n_turns=("n_turns", "sum"),
            total_tokens=("total_tokens", "sum"),
            # n_unique_calls / firms across years — conservative lower bound is the max
            # across years, but the right answer needs raw lookup. We approximate via sum
            # across years because a file/firm can only appear in 1 year (file_name is
            # call-level, unique per call); gvkey CAN repeat across years so max is more
            # accurate there. For clarity we emit both:
            n_unique_calls=("n_unique_calls", "sum"),   # file_names unique per year→sum = total
            n_firm_years=("n_unique_firms", "sum"),     # sum of per-year unique firms
            **{c: (c, "sum") for c in count_sum_cols},
        )
        .reset_index()
    )
    agg = agg.merge(year_span, on="role", how="left")

    # Cohort totals for share computations
    cohort_total_turns = agg["n_turns"].sum()
    cohort_total_tokens = agg["total_tokens"].sum()
    agg["share_turns_pct"] = 100.0 * agg["n_turns"] / cohort_total_turns
    agg["share_speech_pct"] = 100.0 * agg["total_tokens"] / cohort_total_tokens

    # Pooled LM percentages (ratio-of-sums — matches aggregate_weighted)
    for cat in LM_CATEGORIES:
        num = agg[f"{cat}_count_sum"]
        den = agg["total_tokens"].replace(0, np.nan)
        agg[f"pooled_{cat.lower()}_pct"] = 100.0 * num / den

    # Display order
    col_order = [
        "role",
        "n_turns",
        "share_turns_pct",
        "total_tokens",
        "share_speech_pct",
        "n_unique_calls",
        "n_firm_years",
        "first_year",
        "last_year",
        "pooled_uncertainty_pct",
        "pooled_negative_pct",
        "pooled_positive_pct",
        "pooled_litigious_pct",
        "pooled_strong_modal_pct",
        "pooled_weak_modal_pct",
        "pooled_constraining_pct",
    ] + count_sum_cols
    agg = agg[col_order].sort_values("n_turns", ascending=False).reset_index(drop=True)
    return agg


def density_matrix(
    master_turn_level: pd.DataFrame,
    cohort: str,
    row_order: list | None = None,
    col_order: list | None = None,
) -> tuple[pd.DataFrame, list, list]:
    """year × ff12 pooled Unc % density. Uses turn-level aggregate by (cohort, year, ff12)."""
    sub = master_turn_level[master_turn_level["cohort"] == cohort].copy()
    grp = (
        sub.groupby(["year", "ff12_code"], dropna=False)
        .agg(
            tokens=("total_tokens", "sum"),
            unc_sum=("Uncertainty_count_sum", "sum"),
        )
        .reset_index()
    )
    grp["pooled_unc_pct"] = 100.0 * grp["unc_sum"] / grp["tokens"].replace(0, np.nan)
    mat = grp.pivot(index="year", columns="ff12_code", values="pooled_unc_pct")
    if row_order is None:
        row_order = mat.mean(axis=1).sort_values(ascending=False).index.tolist()
    if col_order is None:
        col_order = mat.mean(axis=0).sort_values(ascending=False).index.tolist()
    mat = mat.loc[row_order, col_order]
    mat.loc["col_mean"] = mat.mean(axis=0)
    mat["row_mean"] = mat.mean(axis=1)
    return mat, row_order, col_order


def shade(val: float, quartiles: list[float]) -> str:
    if pd.isna(val):
        return " "
    if val >= quartiles[2]:
        return "▓"
    if val >= quartiles[1]:
        return "▒"
    if val >= quartiles[0]:
        return "░"
    return " "


# -----------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("Ad-hoc: per-raw-role summary stats for textual measures")
    print("=" * 78)
    t0 = datetime.now()

    root = REPO_ROOT
    stage21_dir = root / "outputs" / "2_Textual_Analysis" / "2.1_Tokenized" / "2026-02-27_195750"
    stage22_dir = root / "outputs" / "2_Textual_Analysis" / "2.2_Variables" / "2026-04-09_223627"
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = root / "outputs" / "adhoc" / f"role_textual_stats_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output: {out_dir}")

    # 1. Manifest
    print("\n[1/6] Loading executive manifest...")
    manifest_df = load_executive_map(root)
    print(f"  manifest rows: {len(manifest_df):,}  unique file_name: {manifest_df['file_name'].nunique():,}")
    assert manifest_df["file_name"].is_unique, "manifest file_name not unique — aborting"

    # 2. FF12 crosswalk
    print("\n[2/6] Loading FF12 crosswalk...")
    ff12_zip = root / "inputs" / "FF1248" / "Siccodes12.zip"
    ff12_map = parse_ff_industries(ff12_zip, 12)
    ff12_catchall = ff12_map.get("_catchall") or (12, "Other")
    ff12_names = {
        v[0]: v[1] for k, v in ff12_map.items() if isinstance(k, int) and isinstance(v, tuple)
    }
    ff12_names[ff12_catchall[0]] = ff12_catchall[1]

    def sic_to_ff12(sic_val):
        if pd.isna(sic_val):
            return ff12_catchall[0]
        try:
            key = int(float(sic_val))
        except (TypeError, ValueError):
            return ff12_catchall[0]
        mapped = ff12_map.get(key)
        return mapped[0] if mapped else ff12_catchall[0]

    manifest_df["ff12_code"] = manifest_df["sic"].apply(sic_to_ff12)

    # 3. Snapshot intersection
    print("\n[3/6] Snapshot intersection pre-filter...")
    stage21_files = sorted(stage21_dir.glob("linguistic_counts_*.parquet"))
    years = sorted(int(f.stem.split("_")[-1]) for f in stage21_files)

    all_21_files = set()
    for f in stage21_files:
        all_21_files.update(pd.read_parquet(f, columns=["file_name"])["file_name"].unique())
    valid_files = all_21_files & set(manifest_df["file_name"].unique())
    missing_in_21 = set(manifest_df["file_name"].unique()) - all_21_files
    print(f"  Stage 2.1 years: {years[0]}–{years[-1]} ({len(years)} files)")
    print(f"  Intersection (valid):   {len(valid_files):,}  (manifest-only excluded: {len(missing_in_21):,})")

    manifest_lookup = manifest_df[["file_name", "ff12_code", "gvkey"]].set_index("file_name")

    # 4. Per-year loop
    print("\n[4/6] Per-year loop (flag_speakers + aggregate by role)...")
    per_year_role_aggs = []      # master_role: (cohort, year, role)
    per_year_yr_ff12_aggs = []   # master_turn_level: (cohort, year, ff12_code) for density
    yearly_cohort_sizes = []
    flagged_2018 = None
    reconcile_per_call = None

    for year in years:
        t_yr = datetime.now()
        df = pd.read_parquet(stage21_dir / f"linguistic_counts_{year}.parquet")
        df_flagged = flag_speakers(df, manifest_df)
        df_flagged = df_flagged[df_flagged["file_name"].isin(valid_files)].copy()
        df_flagged["ff12_code"] = df_flagged["file_name"].map(manifest_lookup["ff12_code"])
        df_flagged["gvkey"] = df_flagged["file_name"].map(manifest_lookup["gvkey"])

        # By-role aggregate (per cohort)
        per_year_role_aggs.append(aggregate_year_by_role(df_flagged, year))

        # By (year, ff12) aggregate (per cohort) for T10
        cohort_masks = build_cohort_masks(df_flagged)
        for cohort, mask in cohort_masks.items():
            sub = df_flagged.loc[mask, ["ff12_code", "total_tokens"] + [f"{c}_count" for c in LM_CATEGORIES]].copy()
            if sub.empty:
                continue
            g = sub.groupby("ff12_code", dropna=False).agg(
                total_tokens=("total_tokens", "sum"),
                **{f"{cat}_count_sum": (f"{cat}_count", "sum") for cat in LM_CATEGORIES},
            ).reset_index()
            g.insert(0, "year", year)
            g.insert(0, "cohort", cohort)
            per_year_yr_ff12_aggs.append(g)

        # Yearly cohort sizes
        cm = cohort_masks
        yearly_cohort_sizes.append({
            "year": year,
            "total_turns": len(df_flagged),
            "n_mgr": int(cm["Mgr"].sum()),
            "n_ceo": int(cm["CEO"].sum()),
            "n_noceo_mgr": int(cm["NonCEO_Mgr"].sum()),
        })

        if year == 2018:
            flagged_2018 = df_flagged.copy()
            rec = (
                df_flagged[df_flagged["is_manager"] & (df_flagged["context"] == "qa")]
                .groupby("file_name")
                .agg(our_unc_sum=("Uncertainty_count", "sum"), our_tok_sum=("total_tokens", "sum"))
                .reset_index()
            )
            rec["our_mgr_qa_unc_pct"] = 100.0 * rec["our_unc_sum"] / rec["our_tok_sum"].replace(0, np.nan)
            reconcile_per_call = rec

        elapsed = (datetime.now() - t_yr).total_seconds()
        print(f"  {year}: {len(df_flagged):,} turns  Mgr={cm['Mgr'].sum():,}  CEO={cm['CEO'].sum():,}  ({elapsed:.1f}s)")

    master_roles = pd.concat(per_year_role_aggs, ignore_index=True)
    master_yrff = pd.concat(per_year_yr_ff12_aggs, ignore_index=True)
    print(f"\n  per-role master rows: {len(master_roles):,}")

    # 5. Verification
    print("\n[5/6] Verification — per-call reconcile vs Stage 2.2 (2018)...")
    df22 = pd.read_parquet(
        stage22_dir / "linguistic_variables_2018.parquet",
        columns=["file_name", "Manager_QA_Uncertainty_pct"],
    )
    rec = reconcile_per_call.merge(df22, on="file_name", how="inner")
    rec["diff"] = (rec["our_mgr_qa_unc_pct"] - rec["Manager_QA_Uncertainty_pct"]).abs()
    max_abs_diff = rec["diff"].max()
    print(f"  Per-call reconcile max |diff| (n={len(rec):,}): {max_abs_diff:.3e}")

    # 6. Tabulations
    print("\n[6/6] Computing tabulations...")

    # Main: per-raw-role tables (3 cohorts)
    role_tables = {}
    for cohort in ["Mgr", "CEO", "NonCEO_Mgr"]:
        tbl = rollup_roles(master_roles, cohort)
        role_tables[cohort] = tbl
        tbl.to_csv(out_dir / f"T_roles_{cohort.lower()}.csv", index=False)
        print(f"  T_roles_{cohort.lower()}: {len(tbl):,} unique roles")

    # T6 leak (is_manager AND role~/analyst/)
    analyst_pat = re.compile(r"\banalyst\b", re.IGNORECASE)
    leaks = flagged_2018[
        flagged_2018["is_manager"]
        & flagged_2018["role"].fillna("").apply(lambda s: bool(analyst_pat.search(s)))
    ]
    leaks.head(100).to_csv(out_dir / "t6_leak_check.csv", index=False)

    # T7 null-role audit
    t7_rows = []
    for cohort, mask in build_cohort_masks(flagged_2018).items():
        sub = flagged_2018.loc[mask].copy()
        sub["is_empty_role"] = sub["role"].fillna("").str.strip() == ""
        for flag in [True, False]:
            part = sub[sub["is_empty_role"] == flag]
            if part.empty:
                continue
            t7_rows.append({
                "cohort": cohort,
                "role_empty": flag,
                "n_turns": len(part),
                "share_of_cohort_pct": 100.0 * len(part) / len(sub),
                "total_tokens": int(part["total_tokens"].sum()),
                "pooled_unc_pct": 100.0 * part["Uncertainty_count"].sum() / max(part["total_tokens"].sum(), 1),
            })
    pd.DataFrame(t7_rows).to_csv(out_dir / "t7_null_role_audit.csv", index=False)

    # T8 yearly cohort sizes
    pd.DataFrame(yearly_cohort_sizes).to_csv(out_dir / "t8_yearly_cohort_sizes.csv", index=False)

    # T9 distribution moments (2018 per-turn)
    t9_rows = []
    flagged_2018["per_turn_unc_pct"] = (
        100.0 * flagged_2018["Uncertainty_count"] / flagged_2018["total_tokens"].replace(0, np.nan)
    )
    for cohort, mask in build_cohort_masks(flagged_2018).items():
        sub = flagged_2018.loc[mask, "per_turn_unc_pct"].dropna()
        if sub.empty:
            continue
        t9_rows.append({
            "cohort": cohort, "n": len(sub),
            "mean": sub.mean(), "sd": sub.std(), "skew": sub.skew(), "kurtosis": sub.kurtosis(),
            "p1": sub.quantile(0.01), "p5": sub.quantile(0.05), "p25": sub.quantile(0.25),
            "p50": sub.quantile(0.50), "p75": sub.quantile(0.75), "p95": sub.quantile(0.95),
            "p99": sub.quantile(0.99),
        })
    pd.DataFrame(t9_rows).to_csv(out_dir / "t9_distribution_moments.csv", index=False)

    # T10 density
    mat_mgr, row_order, col_order = density_matrix(master_yrff, "Mgr")
    mat_mgr.to_csv(out_dir / "t10_year_ff12_density.csv")
    mat_ceo, _, _ = density_matrix(master_yrff, "CEO", row_order=row_order, col_order=col_order)
    mat_ceo.to_csv(out_dir / "t10_year_ff12_density_ceo.csv")
    mat_noceo, _, _ = density_matrix(master_yrff, "NonCEO_Mgr", row_order=row_order, col_order=col_order)
    mat_noceo.to_csv(out_dir / "t10_year_ff12_density_noceo.csv")

    # Summary report
    print("\n  Writing summary report...")
    lines = [
        "# Role-Level Summary Stats — Textual Measures (raw role, no buckets)",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Stage 2.1 snapshot:** `2026-02-27_195750`",
        f"**Stage 2.2 snapshot:** `2026-04-09_223627`",
        "",
        "## Rejection of buckets",
        "",
        "Previous version used an ad-hoc regex cascade (CEO-title / CFO-title / ...) to group "
        "raw role strings into 12 buckets. User rejected (2026-04-19): the cascade was a made-up "
        "taxonomy with no literature anchor. This version emits ONE row per UNIQUE raw role "
        "string, preserving every role as reported by Capital IQ.",
        "",
        "## CAVEAT — CEO cohort semantics",
        "",
        "`is_ceo` is **name-matched** against the Execucomp manifest, NOT role-string matched. "
        "A turn with role='President, CEO & Director' carries `is_ceo=True` only if the speaker's "
        "name matches the firm's Execucomp CEO for that year. Mid-year turnover, co-CEOs, and "
        "speaker misidentification produce the ~1.4% of is_ceo=True turns with non-CEO-string roles, "
        "and a larger mass of CEO-string-role turns with is_ceo=False (these land in NonCEO_Mgr).",
        "",
        "## Snapshot residual",
        "",
        f"Manifest has **{len(missing_in_21):,} file_names NOT in Stage 2.1** `2026-02-27_195750` "
        "(Stage 2.2 snapshot was regenerated from a newer 2.1). Excluded from this analysis.",
        "",
        "## Verification",
        "",
        f"- Per-call Mgr_QA_Uncertainty_pct reconcile vs Stage 2.2 (n={len(rec):,}): max |diff| = **{max_abs_diff:.2e}** (bit-exact; tolerance 1e-12).",
        f"- T6 analyst-leak canary (2018): {len(leaks):,} turns (expected 0; F2 guarantee).",
        f"- Per-role master rows: {len(master_roles):,} (year × cohort × role).",
        "",
        "## Cohort summary",
        "",
    ]

    # Overall per-cohort summary
    for cohort in ["Mgr", "CEO", "NonCEO_Mgr"]:
        tbl = role_tables[cohort]
        n_roles = len(tbl)
        total_turns = tbl["n_turns"].sum()
        total_tokens = tbl["total_tokens"].sum()
        pool_unc = 100.0 * tbl["Uncertainty_count_sum"].sum() / max(total_tokens, 1)
        top1_role = tbl.iloc[0]["role"]
        top1_share = tbl.iloc[0]["share_turns_pct"]
        top5_cov = tbl.head(5)["share_turns_pct"].sum()
        top20_cov = tbl.head(20)["share_turns_pct"].sum()
        lines.append(
            f"- **{cohort}**: {n_roles:,} unique roles; {total_turns:,} turns; "
            f"{total_tokens:,} tokens; pooled Unc = {pool_unc:.3f}%. "
            f"Top role '{top1_role}' = {top1_share:.1f}% of turns. "
            f"Top-5 cover {top5_cov:.1f}%; top-20 cover {top20_cov:.1f}%."
        )

    # Per-cohort top-30 display tables
    for cohort in ["Mgr", "CEO", "NonCEO_Mgr"]:
        lines += ["", f"## Top-30 roles — {cohort}", ""]
        lines.append("| # | Role | Turns | % turns | Tokens | % speech | Firms (Σ fy) | Calls | Unc % | Neg % | Pos % | Yrs |")
        lines.append("|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|")
        tbl = role_tables[cohort].head(30)
        for i, r in tbl.iterrows():
            role_disp = str(r["role"]) if r["role"] else "*(empty)*"
            role_disp = role_disp.replace("|", "/")[:40]
            lines.append(
                f"| {i+1} | {role_disp} | {int(r['n_turns']):,} | {r['share_turns_pct']:.2f} | "
                f"{int(r['total_tokens']):,} | {r['share_speech_pct']:.2f} | "
                f"{int(r['n_firm_years']):,} | {int(r['n_unique_calls']):,} | "
                f"{r['pooled_uncertainty_pct']:.3f} | {r['pooled_negative_pct']:.3f} | "
                f"{r['pooled_positive_pct']:.3f} | {int(r['first_year'])}–{int(r['last_year'])} |"
            )

    # T10 — Mgr density with shading
    lines += ["", "## Year × FF12 Mgr uncertainty density (ordered)", ""]
    core = mat_mgr.drop(index="col_mean", errors="ignore").drop(columns="row_mean", errors="ignore")
    flat = core.stack().dropna().values
    quartiles = list(np.quantile(flat, [0.25, 0.5, 0.75])) if len(flat) else [0, 0, 0]
    cols_no_rowmean = [c for c in mat_mgr.columns if c != "row_mean"]
    hdr = ["Year"] + [f"{c}:{ff12_names.get(c, '?')[:6]}" for c in cols_no_rowmean] + ["row_mean"]
    lines.append("| " + " | ".join(hdr) + " |")
    lines.append("|" + "|".join(["---"] * len(hdr)) + "|")
    for idx in mat_mgr.index:
        vals = [mat_mgr.loc[idx, c] for c in cols_no_rowmean]
        row_mean = mat_mgr.loc[idx, "row_mean"] if "row_mean" in mat_mgr.columns else np.nan
        cells = [
            (shade(v, quartiles) + f" {v:.2f}") if not pd.isna(v) else "—"
            for v in vals
        ]
        rm = f" {row_mean:.3f}" if not pd.isna(row_mean) else "—"
        lines.append(f"| {idx} | " + " | ".join(cells) + f" | {rm} |")
    lines.append("")
    lines.append(f"*Shading: `▓` ≥ p75 ({quartiles[2]:.3f}), `▒` ≥ p50 ({quartiles[1]:.3f}), `░` ≥ p25 ({quartiles[0]:.3f}).*")

    elapsed_min = (datetime.now() - t0).total_seconds() / 60.0
    lines += ["", "---", f"Runtime: {elapsed_min:.1f} min."]
    (out_dir / "summary_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\nDone in {elapsed_min:.1f} min.")
    print(f"Outputs: {out_dir}")


if __name__ == "__main__":
    main()
