"""DIAG — random-tercile placebo (Sina-authorized 2026-05-17 "go").

The discriminating test for §D (campello_variable_audit_2026_05_17.md):
the βᵁᴷ-tercile DiD gives δ̂ ≈ −0.033 on the canonical step7 spec. Is that
because the βᵁᴷ PARTITION carries signal, or would ANY partition of the
same firms on the same panel/FE/DV give ≈ −0.03?

Design = label permutation, NOT a spec deviation. Clone step7's EXACT
panel/DV (CASH = cheq_t/atq_{t-1}, canonical Table-1, §F.2)/controls/
FIRM+IND×QTR FE/double-clustered SE (imports step7._cash_dv directly,
so it tracks the current canonical DV automatically).
Build the estimation sample ONCE (POST_x_HIGH is never NaN ⇒ the dropna
sample is invariant to the labels). Anchor-fit with the REAL βᵁᴷ labels
(must reproduce step7's on-record δ̂ — programmatic sanity gate, no
hardcode). Then ×N: shuffle the firm-level HIGH_UK label among the SAME
firms preserving the exact treated/control firm counts, recompute
POST_x_HIGH, re-fit. Same rows, same FE, same SE — only the partition
changes.

Decision rule (ledger §D):
  • real δ̂ in the extreme tail of the placebo dist (perm-p small),
    placebo centered ≈ 0  ⇒ βᵁᴷ partition carries signal ⇒ NOT pure
    noise (selection-on-confounder or real effect).
  • placebo ALSO ≈ −0.03 / frequently significant ⇒ panel/FE/DV
    artifact, not βᵁᴷ at all.
  • placebo centered ≈ 0, WIDE, real δ̂ NOT extreme (perm-p large) ⇒
    consistent with βᵁᴷ ≈ noise (a random split is just as likely).

Read-only. No spec change. No verdict (gated on Sina). Off-ramp forbidden.
Writes tmp/campello_random_tercile_placebo_2026_05_17.md + console.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from step7_fullpanel_hypothesis import (  # EXACT clone — reuse, no drift
    FIRM_BUILDERS, POST_Q, ROOT, WINSOR, _build, _calendar_lag1, _cash_dv,
    _latest,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

N_PERM = 200
SEED = 20260517
OUT_MD = ROOT / "tmp" / "campello_random_tercile_placebo_2026_05_17.md"


def _build_estimation_sample():
    """Replicates step7.main() panel block VERBATIM up to (sub, pdat, cols).
    Returns (sub, cols) with real HIGH_UK_EXPOSURE attached."""
    s1_dir = _latest("step1_sample")
    s3_dir = _latest("step3_treatment")
    s1 = pd.read_parquet(s1_dir / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    trt = pd.read_parquet(s3_dir / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    tc = trt[trt["in_step1"] & trt["group"].isin(["treated", "control"])].copy()
    tc["HIGH_UK_EXPOSURE"] = (tc["group"] == "treated").astype(int)

    panel = s1.merge(tc[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey",
                     how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)

    cash = _cash_dv()
    df = panel.merge(cash, on=["gvkey", "cal_yr_qtr"], how="inner")
    df = df[df["atq"] > 0].copy()
    df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls)
        col = [c for c in b.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey", "cal_yr_qtr"],
                      how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(df[["gvkey", "cal_yr_qtr", "log_assets"]],
                                 "log_assets").rename(
                  columns={"log_assets": "log_assets_l1"}),
                  on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    cons = _build("BrexitConsensusEPSBuilder")
    cons = (cons.sort_values(["gvkey", "cal_yr_qtr"], kind="stable")
                .drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last"))
    ccol = [c for c in cons.columns if c not in ("gvkey", "cal_yr_qtr")][0]
    df = df.merge(cons.rename(columns={ccol: "cons_fwd"}),
                  on=["gvkey", "cal_yr_qtr"], how="left")

    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)

    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH", "indqtr_code"] + cols).copy()
    return sub, cols


def _fit(pdat, cols):
    from linearmodels.panel import PanelOLS
    res = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True,
                         cluster_time=True)
    return (float(res.params["POST_x_HIGH"]),
            float(res.std_errors["POST_x_HIGH"]),
            float(res.pvalues["POST_x_HIGH"]), int(res.nobs))


def main() -> None:
    print("=== DIAG — random-tercile placebo (canonical step7 spec) ===\n")
    sub, cols = _build_estimation_sample()
    n_obs = len(sub)
    firm_high = (sub[["gvkey", "HIGH_UK_EXPOSURE"]]
                 .drop_duplicates().reset_index(drop=True))
    n_firms = len(firm_high)
    n_t = int((firm_high.HIGH_UK_EXPOSURE == 1).sum())
    n_c = n_firms - n_t
    print(f"estimation sample: {n_obs:,} fq / {n_firms:,} firms "
          f"(real T={n_t:,}, C={n_c:,})")

    base = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    gv_idx = base.index.get_level_values("gvkey")  # row→gvkey

    # ---- anchor: REAL βᵁᴷ labels (must reproduce step7 on-record δ̂) ----
    b0, se0, p0, nobs0 = _fit(base, cols)
    s7 = _latest("step7_fullpanel_hypothesis")
    ref = json.loads((s7 / "summary.json").read_text(
        encoding="utf-8"))["results"][0]["delta_hat"]
    gate = abs(b0 - ref) < 5e-3
    print(f"\nANCHOR (real βᵁᴷ): δ̂ {b0:+.5f} SE {se0:.5f} p {p0:.4f} "
          f"N {nobs0:,}")
    print(f"  step7 on-record δ̂ = {ref:+.5f}  |Δ|={abs(b0-ref):.5f}  "
          f"clone-fidelity gate: {'PASS' if gate else 'FAIL'}")
    if not gate:
        print("  ⚠ CLONE FIDELITY FAIL — anchor ≠ step7; interpretation "
              "UNSAFE. Reporting placebo dist but flagging clone defect.")

    # ---- placebo: shuffle firm HIGH labels, exact counts, same rows ----
    rng = np.random.default_rng(SEED)
    hi = firm_high.HIGH_UK_EXPOSURE.to_numpy()
    deltas, sigs, sig_neg, fails = [], 0, 0, 0
    for i in range(N_PERM):
        perm = rng.permutation(hi)  # preserves exact n_t / n_c
        m = dict(zip(firm_high.gvkey.to_numpy(), perm))
        high_row = pd.Series(gv_idx, index=base.index).map(m).to_numpy()
        pdat = base.copy()
        pdat["POST_x_HIGH"] = (base.index.get_level_values("cal_yr_qtr")
                               .isin(POST_Q).astype(float) * high_row)
        try:
            bi, sei, pi, _ = _fit(pdat, cols)
        except Exception as e:  # noqa: BLE001
            fails += 1
            if fails <= 3:
                print(f"  draw {i}: fit error {type(e).__name__}: {e}")
            continue
        deltas.append(bi)
        if pi < 0.05:
            sigs += 1
            if bi < 0:
                sig_neg += 1
        if (i + 1) % 50 == 0:
            print(f"  …{i+1}/{N_PERM} draws")

    d = np.array(deltas, float)
    k = len(d)
    # one-sided perm-p: P(placebo δ̂ ≤ real δ̂)  (real is negative)
    perm_p = float((d <= b0).mean()) if k else float("nan")
    q = (lambda x: float(np.quantile(d, x)) if k else float("nan"))
    stats = dict(
        n_draws=k, fails=fails, real_delta=b0, real_p=p0,
        placebo_mean=float(d.mean()) if k else float("nan"),
        placebo_sd=float(d.std(ddof=1)) if k else float("nan"),
        placebo_min=float(d.min()) if k else float("nan"),
        placebo_max=float(d.max()) if k else float("nan"),
        p05=q(.05), p50=q(.50), p95=q(.95),
        perm_p_le_real=perm_p,
        pct_sig=sigs / k if k else float("nan"),
        pct_sig_and_neg=sig_neg / k if k else float("nan"),
        clone_gate="PASS" if gate else "FAIL",
    )
    print("\n--- PLACEBO DISTRIBUTION (random partitions, same panel) ---")
    print(f"  draws ok {k}/{N_PERM} (fails {fails})")
    print(f"  placebo δ̂: mean {stats['placebo_mean']:+.5f} "
          f"SD {stats['placebo_sd']:.5f}  "
          f"[min {stats['placebo_min']:+.4f}, max {stats['placebo_max']:+.4f}]")
    print(f"  placebo δ̂ p05/p50/p95: {stats['p05']:+.4f} / "
          f"{stats['p50']:+.4f} / {stats['p95']:+.4f}")
    print(f"  real δ̂ {b0:+.5f}  perm-p P(placebo ≤ real) = {perm_p:.4f}")
    print(f"  placebo significant @5%: {stats['pct_sig']:.1%}  "
          f"(sig & negative: {stats['pct_sig_and_neg']:.1%})")

    interp = (
        "real δ̂ in extreme tail (perm-p ≤ .10) AND placebo ≈ 0 ⇒ βᵁᴷ "
        "partition carries SIGNAL — NOT pure noise (selection / real)"
        if perm_p <= 0.10 and abs(stats["placebo_mean"]) < 0.01 else
        "placebo ALSO ≈ −0.03 / often significant ⇒ panel/FE/DV ARTIFACT, "
        "not βᵁᴷ" if stats["placebo_mean"] < -0.015 or stats["pct_sig"] > 0.30
        else
        "placebo centered ≈ 0, WIDE; real δ̂ NOT extreme (perm-p large) ⇒ "
        "consistent with βᵁᴷ ≈ NOISE (random split as likely as βᵁᴷ split)")
    print(f"\n  READ (rule-based, NOT a verdict — gated on Sina):\n    {interp}")

    md = [
        "# Random-tercile placebo — canonical step7 spec (Sina GO 2026-05-17)",
        "",
        f"Clone of step7 (CASH = cheq_t/atq_(t-1) canonical Table-1 DV "
        f"§F.2, 5 firm controls + cons_fwd, "
        f"FIRM FE + IND(FIC100)×QTR FE, double-clustered SE). "
        f"Estimation sample {n_obs:,} fq / {n_firms:,} firms "
        f"(T={n_t:,}, C={n_c:,}); held invariant across draws. "
        f"{N_PERM} firm-label permutations, seed {SEED}, exact counts.",
        "",
        f"**Clone-fidelity gate:** anchor δ̂ {b0:+.5f} vs step7 on-record "
        f"{ref:+.5f} (|Δ|={abs(b0-ref):.5f}) → **{stats['clone_gate']}**"
        + ("" if gate else "  ⚠ interpretation UNSAFE — clone defect"),
        "",
        "| metric | value |",
        "|---|---|",
        f"| real βᵁᴷ δ̂ | {b0:+.5f} (SE {se0:.5f}, p {p0:.4f}) |",
        f"| placebo mean δ̂ | {stats['placebo_mean']:+.5f} |",
        f"| placebo SD | {stats['placebo_sd']:.5f} |",
        f"| placebo [min, max] | [{stats['placebo_min']:+.4f}, "
        f"{stats['placebo_max']:+.4f}] |",
        f"| placebo p05 / p50 / p95 | {stats['p05']:+.4f} / "
        f"{stats['p50']:+.4f} / {stats['p95']:+.4f} |",
        f"| perm-p  P(placebo ≤ real) | {perm_p:.4f} |",
        f"| placebo sig @5% | {stats['pct_sig']:.1%} "
        f"(sig & neg {stats['pct_sig_and_neg']:.1%}) |",
        f"| draws ok / fails | {k}/{N_PERM} / {fails} |",
        "",
        f"**Rule-based read (NOT a verdict — gated on Sina):** {interp}",
        "",
        "Cross-ref campello_variable_audit_2026_05_17.md §D/§E. "
        "No spec change; off-ramp forbidden.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nwritten → {OUT_MD}")


if __name__ == "__main__":
    main()
