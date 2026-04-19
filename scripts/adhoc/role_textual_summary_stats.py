#!/usr/bin/env python3
"""
==============================================================================
Ad-hoc: Role-Level Summary Stats for Textual Measures
==============================================================================
ID: adhoc/role_textual_summary_stats
Purpose: Descriptive-stats pack on the textual Loughran-McDonald measures,
         cut by speaker role within the Mgr pool (+ CEO and NonCEO-Mgr
         sub-cohorts). Feeds §3.2 footnote defense + descriptive appendix.

Plan: C:\\Users\\sinas\\.claude\\plans\\i-want-you-to-snappy-iverson.md
Red-team audit: i-want-you-to-snappy-iverson-agent-a5c1ed1df0fc2d58a.md

No pipeline changes. Single-shot. Reuses production flag_speakers /
load_executive_map / parse_ff_industries. Per-year aggregation to avoid
concat-all-turns OOM (9.8M rows across 17 years).
==============================================================================
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Add src/ to path so we can import f1d modules without installing
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from f1d.text.build_linguistic_variables import (  # noqa: E402
    flag_speakers,
    load_executive_map,
)
from f1d.shared.industry_utils import parse_ff_industries  # noqa: E402


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
LM_CATEGORIES = [
    "Uncertainty",
    "Negative",
    "Positive",
    "Litigious",
    "Strong_Modal",
    "Weak_Modal",
    "Constraining",
]

# Role bucket regex cascade — first match wins. Applied to role.str.lower().strip().
# Red-team M1: dropped (?!.*research) negative-lookahead from Director pattern.
BUCKET_PATTERNS = [
    ("Empty", re.compile(r"^\s*$")),
    ("CEO-title", re.compile(r"\bceo\b|chief executive")),
    ("CFO-title", re.compile(r"\bcfo\b|chief financial")),
    ("COO-title", re.compile(r"\bcoo\b|chief operating")),
    ("Pres/Chair", re.compile(r"\bpresident\b|\bchairman\b|\bchair\b")),
    ("VP-exec", re.compile(r"\bevp\b|\bsvp\b|\bvp\b|vice.president|exec.*vice")),
    ("Director", re.compile(r"\bdirector\b")),
    ("Treasurer", re.compile(r"\btreasurer\b")),
    ("IR", re.compile(r"\bir\b|investor.relations")),
    ("GeneralCounsel", re.compile(r"counsel|secretary")),
    ("OtherExec", re.compile(r"\bmd\b|managing.director|head of|chief")),
]
BUCKET_ORDER = [name for name, _ in BUCKET_PATTERNS] + ["Unmatched"]


def bucket_role_series(role_series: pd.Series) -> pd.Series:
    """Vectorized cascade: assign each role string to first matching bucket."""
    lowered = role_series.fillna("").str.lower().str.strip()
    out = pd.Series("Unmatched", index=role_series.index, dtype="object")
    assigned = pd.Series(False, index=role_series.index)
    for bucket_name, pat in BUCKET_PATTERNS:
        mask = (~assigned) & lowered.str.contains(pat, regex=True, na=False)
        out.loc[mask] = bucket_name
        assigned |= mask
    return out


# -----------------------------------------------------------------------------
# Per-year aggregation
# -----------------------------------------------------------------------------
COHORTS = ["Mgr", "CEO", "NonCEO_Mgr"]


def build_cohort_masks(df_flagged: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "Mgr": df_flagged["is_manager"].astype(bool),
        "CEO": df_flagged["is_ceo"].astype(bool),
        "NonCEO_Mgr": df_flagged["is_manager"].astype(bool)
        & (~df_flagged["is_ceo"].astype(bool)),
    }


def aggregate_year(
    df_flagged: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """
    For one year's turn-level flagged df, compute per-group aggregates:
    rows = (cohort, role_bucket, context, ff12_code), cols = {n_turns, tokens, 7 LM sums}.
    """
    count_cols = [f"{cat}_count" for cat in LM_CATEGORIES]
    cohort_masks = build_cohort_masks(df_flagged)

    pieces = []
    for cohort, mask in cohort_masks.items():
        sub = df_flagged.loc[mask, ["role_bucket", "context", "ff12_code", "total_tokens"] + count_cols]
        if sub.empty:
            continue
        agg = (
            sub.groupby(["role_bucket", "context", "ff12_code"], dropna=False)
            .agg(
                n_turns=("total_tokens", "size"),
                total_tokens=("total_tokens", "sum"),
                **{f"{cat}_count_sum": (f"{cat}_count", "sum") for cat in LM_CATEGORIES},
            )
            .reset_index()
        )
        agg.insert(0, "year", year)
        agg.insert(0, "cohort", cohort)
        pieces.append(agg)

    return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame()


# -----------------------------------------------------------------------------
# Tabulations from master aggregate
# -----------------------------------------------------------------------------
def _pct_cols(agg_df: pd.DataFrame) -> pd.DataFrame:
    """Add pooled_*_pct columns via ratio-of-sums; safe-divide by total_tokens."""
    out = agg_df.copy()
    for cat in LM_CATEGORIES:
        num = out[f"{cat}_count_sum"]
        den = out["total_tokens"].replace(0, np.nan)
        out[f"pooled_{cat.lower()}_pct"] = 100.0 * num / den
    return out


def rollup(
    master: pd.DataFrame,
    group_cols: list[str],
) -> pd.DataFrame:
    """Sum numerators + denominators along group_cols, then compute pooled pcts."""
    count_sum_cols = [f"{cat}_count_sum" for cat in LM_CATEGORIES]
    agg = (
        master.groupby(group_cols, dropna=False)
        .agg(
            n_turns=("n_turns", "sum"),
            total_tokens=("total_tokens", "sum"),
            **{c: (c, "sum") for c in count_sum_cols},
        )
        .reset_index()
    )
    return _pct_cols(agg)


def table_t1_raw_roles_topk(
    flagged_2018: pd.DataFrame, k: int = 50
) -> dict[str, pd.DataFrame]:
    """Top-k raw role strings per cohort, with metrics. 2018 only per plan step 7."""
    count_cols = [f"{cat}_count" for cat in LM_CATEGORIES]
    cohort_masks = build_cohort_masks(flagged_2018)
    outs = {}
    for cohort, mask in cohort_masks.items():
        sub = flagged_2018.loc[mask].copy()
        sub["role"] = sub["role"].fillna("")
        if sub.empty:
            outs[cohort] = pd.DataFrame()
            continue
        agg = (
            sub.groupby("role", dropna=False)
            .agg(
                n_turns=("total_tokens", "size"),
                total_tokens=("total_tokens", "sum"),
                **{f"{c}_sum": (c, "sum") for c in count_cols},
            )
            .reset_index()
        )
        tot = agg["n_turns"].sum()
        agg["share_turns_pct"] = 100.0 * agg["n_turns"] / tot
        for cat in LM_CATEGORIES:
            agg[f"pooled_{cat.lower()}_pct"] = (
                100.0 * agg[f"{cat}_count_sum"] / agg["total_tokens"].replace(0, np.nan)
            )
        agg = agg.sort_values("n_turns", ascending=False).head(k).reset_index(drop=True)
        outs[cohort] = agg
    return outs


def density_matrix(
    master: pd.DataFrame,
    cohort: str,
    metric: str = "pooled_uncertainty_pct",
    row_order: list | None = None,
    col_order: list | None = None,
) -> tuple[pd.DataFrame, list, list]:
    """Wide year × ff12 matrix for one cohort. Returns (matrix, row_order, col_order)."""
    sub = master[master["cohort"] == cohort].copy()
    pooled = rollup(sub, ["year", "ff12_code"])
    mat = pooled.pivot(index="year", columns="ff12_code", values=metric)
    if row_order is None:
        row_order = mat.mean(axis=1).sort_values(ascending=False).index.tolist()
    if col_order is None:
        col_order = mat.mean(axis=0).sort_values(ascending=False).index.tolist()
    mat = mat.loc[row_order, col_order]
    mat.loc["col_mean"] = mat.mean(axis=0)
    mat["row_mean"] = mat.mean(axis=1)
    return mat, row_order, col_order


def shade(val: float, quartiles: list[float]) -> str:
    """Map a value to unicode density shading by quartile."""
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
# Main
# -----------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("Ad-hoc: role-level summary stats for textual measures")
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
    print("\n[1/7] Loading executive manifest...")
    manifest_df = load_executive_map(root)
    print(f"  manifest rows: {len(manifest_df):,}  unique file_name: {manifest_df['file_name'].nunique():,}")
    assert manifest_df["file_name"].is_unique, "manifest file_name not unique — aborting"

    # 2. FF12 crosswalk
    print("\n[2/7] Loading FF12 crosswalk...")
    ff12_zip = root / "inputs" / "FF1248" / "Siccodes12.zip"
    ff12_map = parse_ff_industries(ff12_zip, 12)
    ff12_catchall = ff12_map.get("_catchall") or (12, "Other")
    print(f"  FF12 SIC map size: {sum(1 for k in ff12_map if isinstance(k,int)):,}  catchall: {ff12_catchall}")

    # manifest-side sic → ff12 crosswalk (red-team H2: use manifest sic directly)
    def sic_to_ff12(sic_val):
        if pd.isna(sic_val):
            return ff12_catchall[0]
        try:
            key = int(float(sic_val))
        except (TypeError, ValueError):
            return ff12_catchall[0]
        mapped = ff12_map.get(key)
        if mapped is None:
            return ff12_catchall[0]
        return mapped[0]

    manifest_df["ff12_code"] = manifest_df["sic"].apply(sic_to_ff12)

    # 3. Snapshot intersection pre-filter (red-team H1)
    print("\n[3/7] Snapshot intersection pre-filter...")
    stage21_files = list(stage21_dir.glob("linguistic_counts_*.parquet"))
    years = sorted(int(f.stem.split("_")[-1]) for f in stage21_files)
    print(f"  Stage 2.1 years: {years[0]}–{years[-1]} ({len(years)} files)")

    # Read all file_names from stage 2.1 for intersection
    all_21_files = set()
    for f in stage21_files:
        df_peek = pd.read_parquet(f, columns=["file_name"])
        all_21_files.update(df_peek["file_name"].unique())
    valid_files = all_21_files & set(manifest_df["file_name"].unique())
    print(f"  Stage 2.1 unique calls: {len(all_21_files):,}")
    print(f"  Manifest unique calls:  {manifest_df['file_name'].nunique():,}")
    print(f"  Intersection (valid):   {len(valid_files):,}")
    missing_in_21 = set(manifest_df["file_name"].unique()) - all_21_files
    print(f"  Manifest calls NOT in Stage 2.1: {len(missing_in_21):,}  (expected ~1,720 per red-team H1)")

    manifest_lookup = manifest_df[["file_name", "ff12_code"]].set_index("file_name")

    # 4. Per-year loop: flag_speakers → filter → bucket → aggregate
    print("\n[4/7] Per-year loop (flag_speakers + aggregate)...")
    per_year_aggs = []
    yearly_cohort_sizes = []
    flagged_2018 = None  # keep for T1 / T9 quantiles
    reconcile_per_call = None  # keep 2018 Mgr QA call-level sums for verification

    for year in years:
        t_yr = datetime.now()
        path = stage21_dir / f"linguistic_counts_{year}.parquet"
        df = pd.read_parquet(path)

        df_flagged = flag_speakers(df, manifest_df)
        df_flagged = df_flagged[df_flagged["file_name"].isin(valid_files)].copy()

        # ff12 per turn via manifest join (red-team H2 — use manifest sic, not 2.2)
        df_flagged["ff12_code"] = df_flagged["file_name"].map(manifest_lookup["ff12_code"])

        # Role bucket
        df_flagged["role_bucket"] = bucket_role_series(df_flagged["role"])

        # Per-year aggregate
        agg_year = aggregate_year(df_flagged, year)
        per_year_aggs.append(agg_year)

        # Yearly cohort sizes (T8)
        cm = build_cohort_masks(df_flagged)
        yearly_cohort_sizes.append(
            {
                "year": year,
                "total_turns": len(df_flagged),
                "n_mgr": int(cm["Mgr"].sum()),
                "n_ceo": int(cm["CEO"].sum()),
                "n_noceo_mgr": int(cm["NonCEO_Mgr"].sum()),
            }
        )

        # Keep 2018 raw for T1 / T9 + per-call reconcile
        if year == 2018:
            flagged_2018 = df_flagged.copy()
            rec = (
                df_flagged[df_flagged["is_manager"] & (df_flagged["context"] == "qa")]
                .groupby("file_name")
                .agg(
                    our_unc_sum=("Uncertainty_count", "sum"),
                    our_tok_sum=("total_tokens", "sum"),
                )
                .reset_index()
            )
            rec["our_mgr_qa_unc_pct"] = (
                100.0 * rec["our_unc_sum"] / rec["our_tok_sum"].replace(0, np.nan)
            )
            reconcile_per_call = rec

        elapsed = (datetime.now() - t_yr).total_seconds()
        print(f"  {year}: {len(df_flagged):,} turns  Mgr={cm['Mgr'].sum():,}  CEO={cm['CEO'].sum():,}  ({elapsed:.1f}s)")

    master = pd.concat(per_year_aggs, ignore_index=True)
    print(f"\n  master aggregate rows: {len(master):,}")

    # 5. Verification step 2 — per-call bit-exact reconcile
    print("\n[5/7] Verification — per-call reconcile vs Stage 2.2 (2018)...")
    df22 = pd.read_parquet(
        stage22_dir / "linguistic_variables_2018.parquet",
        columns=["file_name", "Manager_QA_Uncertainty_pct"],
    )
    rec = reconcile_per_call.merge(df22, on="file_name", how="inner")
    rec["diff"] = (rec["our_mgr_qa_unc_pct"] - rec["Manager_QA_Uncertainty_pct"]).abs()
    rec["reldiff"] = rec["diff"] / rec["Manager_QA_Uncertainty_pct"].replace(0, np.nan).abs()
    sample = rec.sample(n=min(5, len(rec)), random_state=42)
    print("  Sample of 5 file_names:")
    for _, r in sample.iterrows():
        print(f"    {r['file_name']}: ours={r['our_mgr_qa_unc_pct']:.10f}  "
              f"theirs={r['Manager_QA_Uncertainty_pct']:.10f}  diff={r['diff']:.2e}")
    max_abs_diff = rec["diff"].max()
    print(f"  Max |diff| across all reconcilable 2018 calls (n={len(rec):,}): {max_abs_diff:.6e}")
    if max_abs_diff > 1e-12:
        print(f"  WARNING: exceeds 1e-12 tolerance. Check flag_speakers wiring.")

    # 6. Tabulations
    print("\n[6/7] Computing T1–T10 tabulations...")

    # T1 — top-50 raw roles per cohort (2018 only for compactness, per plan)
    t1 = table_t1_raw_roles_topk(flagged_2018, k=50)
    for cohort, df_t1 in t1.items():
        df_t1.to_csv(out_dir / f"t1_raw_roles_{cohort.lower()}.csv", index=False)

    # T2 — bucket × cohort (pooled across years, contexts, industries)
    t2 = rollup(master, ["cohort", "role_bucket"])
    # Stable bucket order
    t2["role_bucket"] = pd.Categorical(t2["role_bucket"], categories=BUCKET_ORDER, ordered=True)
    t2 = t2.sort_values(["cohort", "role_bucket"]).reset_index(drop=True)
    t2.to_csv(out_dir / "t2_bucket_by_cohort.csv", index=False)

    # T3 — bucket × year × cohort
    t3 = rollup(master, ["cohort", "role_bucket", "year"])
    t3["role_bucket"] = pd.Categorical(t3["role_bucket"], categories=BUCKET_ORDER, ordered=True)
    t3 = t3.sort_values(["cohort", "role_bucket", "year"]).reset_index(drop=True)
    t3.to_csv(out_dir / "t3_bucket_by_year.csv", index=False)

    # T4 — bucket × ff12 × cohort
    t4 = rollup(master, ["cohort", "role_bucket", "ff12_code"])
    t4["role_bucket"] = pd.Categorical(t4["role_bucket"], categories=BUCKET_ORDER, ordered=True)
    t4 = t4.sort_values(["cohort", "role_bucket", "ff12_code"]).reset_index(drop=True)
    t4.to_csv(out_dir / "t4_bucket_by_ff12.csv", index=False)

    # T5 — context × bucket × cohort
    t5 = rollup(master, ["cohort", "role_bucket", "context"])
    t5["role_bucket"] = pd.Categorical(t5["role_bucket"], categories=BUCKET_ORDER, ordered=True)
    t5 = t5.sort_values(["cohort", "role_bucket", "context"]).reset_index(drop=True)
    t5.to_csv(out_dir / "t5_bucket_by_context.csv", index=False)

    # T6 — leak check (is_manager=True AND role matches \banalyst\b)
    analyst_pat = re.compile(r"\banalyst\b", re.IGNORECASE)
    leaks = flagged_2018[
        flagged_2018["is_manager"]
        & flagged_2018["role"].fillna("").apply(lambda s: bool(analyst_pat.search(s)))
    ]
    leaks.head(100).to_csv(out_dir / "t6_leak_check.csv", index=False)
    print(f"  T6 leak count (2018 only): {len(leaks):,} (expected 0)")

    # T7 — null-role audit within Mgr (2018)
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
    t7 = pd.DataFrame(t7_rows)
    t7.to_csv(out_dir / "t7_null_role_audit.csv", index=False)

    # T8 — yearly cohort sizes
    t8 = pd.DataFrame(yearly_cohort_sizes)
    t8.to_csv(out_dir / "t8_yearly_cohort_sizes.csv", index=False)

    # T9 — distribution moments (2018 only; per-turn quantiles)
    t9_rows = []
    flagged_2018["per_turn_unc_pct"] = (
        100.0 * flagged_2018["Uncertainty_count"] / flagged_2018["total_tokens"].replace(0, np.nan)
    )
    for cohort, mask in build_cohort_masks(flagged_2018).items():
        sub = flagged_2018.loc[mask, "per_turn_unc_pct"].dropna()
        if sub.empty:
            continue
        t9_rows.append({
            "cohort": cohort,
            "n": len(sub),
            "mean": sub.mean(),
            "sd": sub.std(),
            "skew": sub.skew(),
            "kurtosis": sub.kurtosis(),
            "p1": sub.quantile(0.01),
            "p5": sub.quantile(0.05),
            "p25": sub.quantile(0.25),
            "p50": sub.quantile(0.50),
            "p75": sub.quantile(0.75),
            "p95": sub.quantile(0.95),
            "p99": sub.quantile(0.99),
        })
    t9 = pd.DataFrame(t9_rows)
    t9.to_csv(out_dir / "t9_distribution_moments.csv", index=False)

    # T10 — year × FF12 density matrix (Mgr primary; CEO/NonCEO rank-locked)
    mat_mgr, row_order, col_order = density_matrix(master, "Mgr")
    mat_mgr.to_csv(out_dir / "t10_year_ff12_density.csv")

    mat_ceo, _, _ = density_matrix(master, "CEO", row_order=row_order, col_order=col_order)
    mat_ceo.to_csv(out_dir / "t10_year_ff12_density_ceo.csv")

    mat_noceo, _, _ = density_matrix(
        master, "NonCEO_Mgr", row_order=row_order, col_order=col_order
    )
    mat_noceo.to_csv(out_dir / "t10_year_ff12_density_noceo.csv")

    # 7. Summary report
    print("\n[7/7] Writing summary report...")
    ff12_names = {}
    for k, v in ff12_map.items():
        if isinstance(k, int) and isinstance(v, tuple):
            ff12_names[v[0]] = v[1]
    ff12_names[ff12_catchall[0]] = ff12_catchall[1]

    report_lines = [
        "# Role-Level Summary Stats — Textual Measures",
        f"",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Stage 2.1 snapshot:** `2026-02-27_195750`",
        f"**Stage 2.2 snapshot:** `2026-04-09_223627`",
        f"**Output dir:** `{out_dir.relative_to(root)}`",
        "",
        "## Context",
        "",
        "Descriptive characterization of the Mgr pool used in `UncAnsMgr` / `UncPreMgr`. "
        "Three cohorts: **Mgr** (all BGT-style managers), **CEO** (name-matched to manifest), "
        "**NonCEO_Mgr** (Mgr & ~CEO).",
        "",
        "## CAVEAT — CEO cohort semantics",
        "",
        "`is_ceo` is **name-matched** against the Execucomp manifest, NOT role-string matched. "
        "Consequence: some `is_ceo=True` turns carry non-CEO-title roles (e.g. 'Executive Chairman' "
        "at firms where the incumbent CEO is a Chairman) and some role=CEO-title turns carry "
        "`is_ceo=False` (mid-year CEO turnover where Execucomp's incumbent differs from the speaker). "
        "Red-team 2018 baseline: 1.4% of `is_ceo=True` turns have non-CEO-title role; "
        "10,661 role=CEO-title turns in 2018 carry `is_ceo=False`. Expected; not a bug.",
        "",
        "## Snapshot residual (red-team H1)",
        "",
        f"Manifest has **{len(missing_in_21):,} file_names NOT in Stage 2.1** `2026-02-27_195750` "
        f"— these calls were added to Stage 2.2 via a newer 2.1 snapshot not reachable from the "
        f"path used here. They are excluded from this analysis.",
        "",
        "## Verification",
        "",
        f"- **Per-call Mgr_QA_Uncertainty_pct reconcile** (5-sample): max abs diff = **{max_abs_diff:.2e}**",
        f"  (red-team expected ≤1e-16; tolerance 1e-12).",
        f"- **T6 leak check (2018)**: {len(leaks):,} turns with is_manager=True AND role~/analyst/ (expected 0).",
        f"- **Master aggregate rows**: {len(master):,}",
        "",
        "## T2 summary — bucket × cohort (pooled Uncertainty %)",
        "",
    ]

    # T2 pivot for readability
    piv = t2.pivot(index="role_bucket", columns="cohort", values="pooled_uncertainty_pct")
    piv = piv.reindex(BUCKET_ORDER)
    piv_turns = t2.pivot(index="role_bucket", columns="cohort", values="n_turns")
    piv_turns = piv_turns.reindex(BUCKET_ORDER)
    report_lines.append("| Bucket | Mgr turns | Mgr Unc % | CEO turns | CEO Unc % | NonCEO turns | NonCEO Unc % |")
    report_lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for b in BUCKET_ORDER:
        def fmt(v, kind="pct"):
            if pd.isna(v):
                return "—"
            if kind == "int":
                return f"{int(v):,}"
            return f"{v:.3f}"
        report_lines.append(
            "| {b} | {mt} | {mp} | {ct} | {cp} | {nt} | {np_} |".format(
                b=b,
                mt=fmt(piv_turns.loc[b, "Mgr"] if b in piv_turns.index and "Mgr" in piv_turns.columns else np.nan, "int"),
                mp=fmt(piv.loc[b, "Mgr"] if b in piv.index and "Mgr" in piv.columns else np.nan),
                ct=fmt(piv_turns.loc[b, "CEO"] if b in piv_turns.index and "CEO" in piv_turns.columns else np.nan, "int"),
                cp=fmt(piv.loc[b, "CEO"] if b in piv.index and "CEO" in piv.columns else np.nan),
                nt=fmt(piv_turns.loc[b, "NonCEO_Mgr"] if b in piv_turns.index and "NonCEO_Mgr" in piv_turns.columns else np.nan, "int"),
                np_=fmt(piv.loc[b, "NonCEO_Mgr"] if b in piv.index and "NonCEO_Mgr" in piv.columns else np.nan),
            )
        )
    report_lines.append("")

    # T10 — Mgr density matrix with unicode shading
    report_lines.append("## T10 — Year × FF12 uncertainty density (Mgr cohort, ordered)")
    report_lines.append("")
    # Compute quartiles from the non-marginal cells
    core = mat_mgr.drop(index="col_mean", errors="ignore").drop(columns="row_mean", errors="ignore")
    flat = core.stack().dropna().values
    quartiles = list(np.quantile(flat, [0.25, 0.5, 0.75])) if len(flat) else [0, 0, 0]
    # Header
    cols_no_rowmean = [c for c in mat_mgr.columns if c != "row_mean"]
    hdr = ["Year"] + [f"FF{c}:{ff12_names.get(c, '?')[:6]}" for c in cols_no_rowmean] + ["row_mean"]
    report_lines.append("| " + " | ".join(hdr) + " |")
    report_lines.append("|" + "|".join(["---"] * len(hdr)) + "|")
    for idx in mat_mgr.index:
        vals = [mat_mgr.loc[idx, c] for c in cols_no_rowmean]
        row_mean = mat_mgr.loc[idx, "row_mean"] if "row_mean" in mat_mgr.columns else np.nan
        cells = [
            (shade(v, quartiles) + f" {v:.2f}") if not pd.isna(v) else "—"
            for v in vals
        ]
        row_str = f" {row_mean:.3f}" if not pd.isna(row_mean) else "—"
        report_lines.append(f"| {idx} | " + " | ".join(cells) + f" | {row_str} |")
    report_lines.append("")
    report_lines.append(f"*Shading: `▓` ≥ p75 ({quartiles[2]:.3f}), `▒` ≥ p50 ({quartiles[1]:.3f}), `░` ≥ p25 ({quartiles[0]:.3f}).*")
    report_lines.append("")

    # Footer
    elapsed_min = (datetime.now() - t0).total_seconds() / 60.0
    report_lines.append(f"---")
    report_lines.append(f"Runtime: {elapsed_min:.1f} min.")
    (out_dir / "summary_report.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(f"\nDone in {elapsed_min:.1f} min.")
    print(f"Outputs: {out_dir}")


if __name__ == "__main__":
    main()
