"""DIAG — CONSENSUS_EPS raw-$ fingerprint test (Sina-chosen §G, 2026-05-17).

Hypothesis: Campello's "standardized mean 1-quarter-ahead EPS forecast"
(Table 1: mean 0.07 / SD 3.51 / med 0.09 / IQR 2.05) is NOT a statistical
z-score (our builder) — a within-firm z-score has SD≈1 by construction and
cannot produce SD 3.51. Candidate consistent with SD≫1 = the RAW consensus
EPS in dollars (mean across analysts), or the IBES standardized-basis EPS
estimate; "standardized" may name the IBES estimate basis, not a transform.

Test: reconstruct raw mean_eps per (gvkey,cal_yr_qtr) via the builder's
OWN validated loaders (CUSIP/OFTIC/TICKER time-varying CCM, FPI=6 EPS,
mean across analysts) but SKIP `_within_firm_zscore`. Moments on the
rebuild scopes (Universe/Treated/Control ≈ Campello Panel A/B/C), 1%
winsor within cal_yr_qtr, window 2010Q1-2015Q4. Compare raw-$ vs the
z-score (current builder) vs Campello — all sides programmatic.

Speed: raw-$ needs no full 2000-2025 history (z-score did); load IBES
2009-2016 only. Read-only; no spec change; no verdict (gated on Sina).
Writes tmp/campello_consensus_raw_test_2026_05_17.md + console.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from f1d.shared.variables.brexit_consensus_eps import (  # validated loaders
    _fpedats_to_cal_yr_qtr, _load_cusip_to_gvkey_map,
    _load_ticker_to_gvkey_map, _load_yearly_ibes_fpi6, _within_firm_zscore,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

T1_EXTRACT = ROOT / "tmp" / "campello_pdf_extract" / "table1_pdfpage21.txt"
OUT = ROOT / "tmp" / "campello_consensus_raw_test_2026_05_17.md"
QLO, QHI, WIN = 20101, 20154, 0.01
KEY = "CONSENSUS_EARNINGS_FORECAST"
PANELS = [("PanelA.COMPUSTAT", "Market-BasedApproach", "UNIVERSE (A)"),
          ("PanelB.TreatedFirms:", "Market-BasedApproach", "TREATED (B)"),
          ("PanelC.ControlFirms:", "(continuedonnextpage)", "CONTROL (C)")]
_ROW = re.compile(r"^([A-Z][A-Z0-9_&]+(?:\([^)]*\))?)\s+(-?\d+\.\d+)\s+"
                  r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+([\d,]+)\s*$")


def _camp() -> dict:
    txt = T1_EXTRACT.read_text(encoding="utf-8")
    out = {}
    for start, end, lab in PANELS:
        seg = txt.split(start)[-1].split(end)[0]
        for ln in seg.splitlines():
            m = _ROW.match(ln.strip())
            if m and m.group(1) == KEY:
                out[lab] = dict(mean=float(m.group(2)), sd=float(m.group(3)),
                                med=float(m.group(4)), iqr=float(m.group(5)),
                                n=int(m.group(6).replace(",", "")))
    return out


def _latest(sub: str) -> Path:
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def _mom(s: pd.Series) -> dict:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf],
                                                  np.nan).dropna()
    if s.empty:
        return dict(n=0, mean=np.nan, sd=np.nan, med=np.nan, iqr=np.nan)
    return dict(n=int(s.size), mean=float(s.mean()), sd=float(s.std(ddof=1)),
                med=float(s.median()),
                iqr=float(s.quantile(.75) - s.quantile(.25)))


def _wins_within(df, col):
    return df.groupby("cal_yr_qtr", observed=True)[col].transform(
        lambda x: x.clip(x.quantile(WIN), x.quantile(1 - WIN)))


def main() -> None:
    print("=== DIAG — CONSENSUS_EPS raw-$ vs z-score vs Campello ===\n")
    camp = _camp()
    cu = _load_cusip_to_gvkey_map(ROOT)
    tk = _load_ticker_to_gvkey_map(ROOT)
    ibes = sorted((ROOT / "inputs" / "tr_ibes").glob("tr_ibes_*.parquet"))
    chunks = []
    for yf in ibes:
        y = int(yf.stem.split("_")[-1])
        if y < 2009 or y > 2016:               # raw-$ needs no full history
            continue
        c = _load_yearly_ibes_fpi6(yf, cu, tk)
        if c is not None and len(c):
            chunks.append(c)
    raw = pd.concat(chunks, ignore_index=True)
    raw = (raw.sort_values(["gvkey", "fpedats"], kind="stable")
              .drop_duplicates(["gvkey", "fpedats"], keep="last"))
    z = _within_firm_zscore(raw.copy())        # builder's transform, same data
    raw["cal_yr_qtr"] = raw["fpedats"].apply(_fpedats_to_cal_yr_qtr)
    z["cal_yr_qtr"] = z["fpedats"].apply(_fpedats_to_cal_yr_qtr)
    raw["gvkey"] = raw["gvkey"].astype(str).str.zfill(6)
    z["gvkey"] = z["gvkey"].astype(str).str.zfill(6)

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    s1["cal_yr_qtr"] = s1["cal_yr_qtr"].astype("int64")
    trt = pd.read_parquet(_latest("step3_treatment") / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    trt = trt[trt["in_step1"]]
    UNI = set(s1.gvkey)
    G_T = set(trt[trt.group == "treated"].gvkey)
    G_C = set(trt[trt.group == "control"].gvkey)

    def scope(df, col, gs):
        d = df[(df.cal_yr_qtr >= QLO) & (df.cal_yr_qtr <= QHI)].copy()
        d = d[d.gvkey.isin(gs)].dropna(subset=[col])
        if d.empty:
            return _mom(pd.Series(dtype=float))
        d["w"] = _wins_within(d, col)
        return _mom(d["w"])

    md = ["# CONSENSUS_EPS raw-$ test — raw vs z-score vs Campello", "",
          "Builder loaders reused (FPI=6 EPS, mean-across-analysts, "
          "4-layer CCM); raw = mean_eps ($) NO z-score; z = builder's "
          "within-firm z-score (same rows). 1% winsor within qtr, "
          "2010Q1-2015Q4. Campello programmatic from table1_pdfpage21.",
          "", "| scope | metric | raw-$ | z-score (builder) | Campello |",
          "|--|--|--|--|--|"]
    for gs, lab in ((UNI, "UNIVERSE (A)"), (G_T, "TREATED (B)"),
                    (G_C, "CONTROL (C)")):
        r = scope(raw, "mean_eps", gs)
        zz = scope(z, "consensus_eps_z", gs)
        c = camp.get(lab, {})
        for k in ("mean", "sd", "med", "iqr", "n"):
            rv = f"{r[k]:,}" if k == "n" else f"{r[k]:+.3f}"
            zv = f"{zz[k]:,}" if k == "n" else f"{zz[k]:+.3f}"
            cv = (f"{c.get('n'):,}" if k == "n" else f"{c.get(k):+.3f}") \
                if c else "—"
            md.append(f"| {lab} | {k} | {rv} | {zv} | {cv} |")
            if k == "sd":
                print(f"  {lab:14s} SD  raw-$ {r['sd']:.3f} | "
                      f"z {zz['sd']:.3f} | Campello {c.get('sd')} ")
            if k == "med":
                print(f"  {lab:14s} med raw-$ {r['med']:+.3f} | "
                      f"z {zz['med']:+.3f} | Campello {c.get('med')} ")

    md += ["", "## Read (NO verdict — gated on Sina)",
           "Decisive moment = **SD**. Campello A/B/C SD = 3.51/3.40/2.33 "
           "(≫1). A within-firm z-score ⇒ SD≈1 (cannot match). If raw-$ "
           "SD ≈ 3.5/3.4/2.3 AND med ≈ 0.09/0.01/0.04 ⇒ Campello's "
           "'standardized' = the raw consensus (mean) EPS in $, NOT a "
           "statistical standardization; our z-score is the defect. If "
           "raw-$ also misses ⇒ next candidate (IBES standardized-basis "
           "estimate type, or small-denominator deflation). Spec change "
           "Sina-gated; this is the fingerprint evidence only."]
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nwritten → {OUT}")


if __name__ == "__main__":
    main()
