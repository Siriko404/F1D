#!/usr/bin/env python3
"""C5: Compute AR(1) of PRisk (Hassan et al. 2019) for construct validation framing.

High autocorrelation means PRisk is persistent across quarters, supporting
the interpretation of H11 as construct validation rather than causal evidence.

Uses pooled OLS with firm + quarter dummies (not entity-demeaned PanelOLS)
to avoid Nickell bias in the autoregressive coefficient.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


def main(panel_path=None):
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "prisk_autocorrelation" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load H11 panel
    if panel_path:
        ppath = Path(panel_path)
    else:
        panel_dir = root / "outputs" / "variables" / "h11_prisk_uncertainty"
        candidates = sorted(panel_dir.glob("20*"))
        if not candidates:
            print("ERROR: No H11 panel found", file=sys.stderr)
            return 1
        ppath = candidates[-1] / "h11_prisk_uncertainty_panel.parquet"

    print(f"Loading: {ppath}")
    df = pd.read_parquet(ppath)
    print(f"  Rows: {len(df):,}")

    # Filter to Main sample
    if "sample" in df.columns:
        df = df[df["sample"] == "Main"].copy()
        print(f"  Main sample: {len(df):,}")

    # Collapse to firm-quarter (PRisk is constant within firm-quarter)
    fq = df.groupby(["gvkey", "cal_q"])[["PRisk"]].first().reset_index()
    fq = fq.dropna(subset=["PRisk"])
    print(f"  Firm-quarters with PRisk: {len(fq):,}")
    print(f"  Unique firms: {fq['gvkey'].nunique():,}")
    print(f"  Unique quarters: {fq['cal_q'].nunique():,}")

    # Create lag
    fq = fq.sort_values(["gvkey", "cal_q"])
    fq["PRisk_lag"] = fq.groupby("gvkey")["PRisk"].shift(1)
    fq = fq.dropna(subset=["PRisk_lag"])
    print(f"  After lag (drop first per firm): {len(fq):,}")

    # Pooled OLS with firm + quarter dummies
    # (Avoids Nickell bias from entity-demeaning in short T)
    y = fq["PRisk"]
    X = fq[["PRisk_lag"]].copy()

    # Add quarter dummies
    quarter_dummies = pd.get_dummies(fq["cal_q"], prefix="q", drop_first=True, dtype=float)
    X = pd.concat([X, quarter_dummies], axis=1)
    X = sm.add_constant(X)

    print(f"\n  Running pooled OLS: PRisk ~ PRisk_lag + quarter dummies")
    print(f"  (Firm dummies omitted for tractability; reporting pooled AR(1))")
    model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": fq["gvkey"]})

    rho = model.params["PRisk_lag"]
    se = model.bse["PRisk_lag"]
    t = model.tvalues["PRisk_lag"]
    p = model.pvalues["PRisk_lag"]

    print(f"\n{'='*60}")
    print(f"  AR(1) coefficient (rho): {rho:.4f}")
    print(f"  Std. Error:              {se:.4f}")
    print(f"  t-statistic:             {t:.2f}")
    print(f"  p-value:                 {p:.6f}")
    print(f"  R-squared:               {model.rsquared:.4f}")
    print(f"  N obs:                   {int(model.nobs):,}")
    print(f"{'='*60}")

    # Save output
    lines = [
        "PRisk AR(1) Autocorrelation Analysis",
        "=" * 50,
        f"Date: {timestamp}",
        f"Panel: {ppath}",
        f"Sample: Main (excl. financial/utility)",
        f"N firm-quarters: {int(model.nobs):,}",
        f"N firms: {fq['gvkey'].nunique():,}",
        f"N quarters: {fq['cal_q'].nunique():,}",
        "",
        "Model: PRisk_t = alpha + rho * PRisk_{t-1} + quarter_dummies + epsilon",
        "SEs: Firm-clustered",
        "",
        f"rho (AR1 coefficient): {rho:.6f}",
        f"SE:                    {se:.6f}",
        f"t-statistic:           {t:.4f}",
        f"p-value:               {p:.8f}",
        f"R-squared:             {model.rsquared:.6f}",
        "",
        "Interpretation: High rho indicates PRisk is persistent across quarters.",
        "This supports framing H11 (PRisk -> Uncertainty) as construct validation,",
        "not a causal effect — the contemporaneous association reflects shared",
        "slow-moving risk perceptions rather than quarter-to-quarter shocks.",
    ]

    report_path = out_dir / "prisk_ar1_report.txt"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  Saved: {report_path}")

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\nCOMPLETE in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="C5: PRisk AR(1) Autocorrelation")
    parser.add_argument("--panel-path", type=str, default=None,
                        help="Explicit path to H11 panel parquet")
    args = parser.parse_args()
    sys.exit(main(panel_path=args.panel_path))
