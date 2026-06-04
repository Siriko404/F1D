"""DIAG — CONSENSUS_EARNINGS_FORECAST 'standardized' candidate sweep.

systematic-debugging Phase 3 instrument (2026-05-18, Sina /goal: match
Campello Table-1 moments). Verbatim def (programmatic, table1_pdfpage21
L195-197): "CONSENSUS_EARNINGS_FORECAST is defined as the standardized
mean 1-quarter ahead earnings per share forecast." The word
'standardized' appears EXACTLY ONCE in the whole extracted paper +
supplement corpus (Table-1 caption only) — no formula, no citation, no
appendix def. Genuine vagueness ⇒ Sina rule "test all possible ways".

Campello fingerprint (programmatic, 3 panels):
  A Universe  mean 0.07 SD 3.51 med 0.09 IQR 2.05  N 42,031
  B Treated   mean 0.01 SD 3.40 med 0.01 IQR 1.83  N  8,963
  C Control   mean 0.07 SD 2.33 med 0.04 IQR 2.40  N 10,720
Signature: center ≈ 0, SD 2.3-3.5, IQR ~2, SD ≫ IQR (heavy tails),
IQR/median ≈ 20+ (NOT a positive level). raw-$ (level, med 0.46) and
within-firm z (SD≈1) both REFUTED by shape. This holds ONE variable —
the standardization operator — and varies only it; everything else
(data, scopes, 1% winsor, universe) fixed. Read-only, NO builder/spec
change (Sina-gated), NO verdict (gated). Writes a moment table per
candidate vs Campello.

Candidates (IBES-only, no external price; price-deflated = round 2 only
if all fail):
  raw          mean_eps ($), no transform                 [baseline]
  zfirm        within-firm z over full IBES sample         [builder; baseline]
  zxsec        cross-sectional z within cal_yr_qtr         [analytically SD≈1]
  f_over_disp  mean_eps / sd(analyst estimates)            [literal "standardized fcst"]
  sue_abs      (actual - mean_eps) / |actual|              [SUE, |actual| deflator]
  sue_disp     (actual - mean_eps) / sd(analyst estimates) [textbook SUE]
  rev_disp     (mean_eps_t - mean_eps_{t-1}) / sd(analyst) [scaled fcst revision]

Speed/memory (Sina standing rule): IBES 2009-2016 only, vectorized
groupby, loaders reused. Window 2010Q1-2015Q4 (Campello Table-1 period).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.dataset as ds

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from f1d.shared.variables.brexit_consensus_eps import (  # validated loaders
    _fpedats_to_cal_yr_qtr, _load_cusip_to_gvkey_map,
    _load_ticker_to_gvkey_map, _timevar_lookup,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

T1_EXTRACT = ROOT / "tmp" / "campello_pdf_extract" / "table1_pdfpage21.txt"
OUT = ROOT / "tmp" / "campello_consensus_standardized_sweep_2026_05_18.md"
QLO, QHI, WIN = 20101, 20154, 0.01
KEY = "CONSENSUS_EARNINGS_FORECAST"
PANELS = [("PanelA.COMPUSTAT", "Market-BasedApproach", "UNIVERSE (A)"),
          ("PanelB.TreatedFirms:", "Market-BasedApproach", "TREATED (B)"),
          ("PanelC.ControlFirms:", "(continuedonnextpage)", "CONTROL (C)")]
_ROW = re.compile(r"^([A-Z][A-Z0-9_&]+(?:\([^)]*\))?)\s+(-?\d+\.\d+)\s+"
                  r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+([\d,]+)\s*$")
CAND = ["raw", "zfirm", "zxsec", "f_over_disp", "sue_abs", "sue_disp",
        "rev_disp"]


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


def _load(cu: pd.DataFrame, tk: pd.DataFrame) -> pd.DataFrame:
    """IBES Detail EPS/FPI=6, per-analyst rows → gvkey resolved, with
    per-firm-period consensus mean, analyst-estimate dispersion, and
    actual. 2009-2016 files only (memory-aware)."""
    files = sorted((ROOT / "inputs" / "tr_ibes").glob("tr_ibes_*.parquet"))
    cols = ["CUSIP", "OFTIC", "TICKER", "VALUE", "ACTUAL", "PDF",
            "MEASURE", "FPI", "FPEDATS"]
    chunks = []
    for yf in files:
        y = int(yf.stem.split("_")[-1])
        if y < 2009 or y > 2016:
            continue
        dset = ds.dataset(yf, format="parquet")
        have = [c for c in cols if c in dset.schema.names]
        flt = (pc.field("MEASURE") == "EPS") & (pc.field("FPI") == "6")
        d = dset.to_table(columns=have, filter=flt).to_pandas()
        if not len(d):
            continue
        d = d.dropna(subset=["VALUE", "FPEDATS"])
        d["fpedats"] = pd.to_datetime(d["FPEDATS"], errors="coerce")
        d = d.dropna(subset=["fpedats"])
        d["cusip8"] = d["CUSIP"].astype(str).str[:8]
        d["cusip8"] = d["cusip8"].where(
            ~d["cusip8"].isin(["00000000", "nan", "NaN", "None", ""]))
        d["oftic_up"] = d["OFTIC"].astype(str).str.upper().str.strip()
        d["ticker_up"] = d["TICKER"].astype(str).str.upper().str.strip()
        gc = _timevar_lookup(d, "cusip8", cu, "cusip8")
        go = _timevar_lookup(d, "oftic_up", tk, "tic")
        gt = _timevar_lookup(d, "ticker_up", tk, "tic")
        d["gvkey"] = gc.fillna(go).fillna(gt)
        d = d.dropna(subset=["gvkey"]).copy()
        d["VALUE"] = pd.to_numeric(d["VALUE"], errors="coerce")
        d["ACTUAL"] = pd.to_numeric(d["ACTUAL"], errors="coerce")
        d = d.dropna(subset=["VALUE"])
        chunks.append(d[["gvkey", "fpedats", "VALUE", "ACTUAL"]])
    raw = pd.concat(chunks, ignore_index=True)
    # consensus mean + analyst dispersion + actual, per (gvkey, fpedats)
    g = raw.groupby(["gvkey", "fpedats"], observed=True)
    out = g.agg(mean_eps=("VALUE", "mean"),
                disp=("VALUE", "std"),
                actual=("ACTUAL", "first")).reset_index()
    out = out.sort_values(["gvkey", "fpedats"], kind="stable")
    out = out.drop_duplicates(["gvkey", "fpedats"], keep="last")
    out["gvkey"] = out["gvkey"].astype(str).str.zfill(6)
    out["cal_yr_qtr"] = out["fpedats"].apply(_fpedats_to_cal_yr_qtr)
    return out


def _candidates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # within-firm z over full loaded sample
    gf = df.groupby("gvkey")["mean_eps"]
    mu, sd = gf.transform("mean"), gf.transform("std")
    df["raw"] = df["mean_eps"]
    df["zfirm"] = np.where(sd > 0, (df["mean_eps"] - mu) / sd, np.nan)
    gq = df.groupby("cal_yr_qtr")["mean_eps"]
    qm, qs = gq.transform("mean"), gq.transform("std")
    df["zxsec"] = np.where(qs > 0, (df["mean_eps"] - qm) / qs, np.nan)
    disp = df["disp"].where(df["disp"] > 0)
    df["f_over_disp"] = df["mean_eps"] / disp
    aa = df["actual"].abs().where(df["actual"].abs() > 0)
    df["sue_abs"] = (df["actual"] - df["mean_eps"]) / aa
    df["sue_disp"] = (df["actual"] - df["mean_eps"]) / disp
    rev = df.sort_values(["gvkey", "fpedats"]).groupby("gvkey")["mean_eps"]
    df["_rev"] = rev.diff()
    df["rev_disp"] = df["_rev"] / disp
    return df


def _wins(df: pd.DataFrame, col: str) -> pd.Series:
    return df.groupby("cal_yr_qtr", observed=True)[col].transform(
        lambda x: x.clip(x.quantile(WIN), x.quantile(1 - WIN)))


def main() -> None:
    print("=== DIAG — CONSENSUS 'standardized' candidate sweep ===\n")
    camp = _camp()
    cu = _load_cusip_to_gvkey_map(ROOT)
    tk = _load_ticker_to_gvkey_map(ROOT)
    df = _load(cu, tk)
    df = _candidates(df)

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    trt = pd.read_parquet(_latest("step3_treatment") / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    trt = trt[trt["in_step1"]]
    UNI = set(s1.gvkey)
    G_T = set(trt[trt.group == "treated"].gvkey)
    G_C = set(trt[trt.group == "control"].gvkey)

    def scope(col: str, gs: set) -> dict:
        d = df[(df.cal_yr_qtr >= QLO) & (df.cal_yr_qtr <= QHI)].copy()
        d = d[d.gvkey.isin(gs)].dropna(subset=[col])
        if d.empty:
            return _mom(pd.Series(dtype=float))
        d["w"] = _wins(d, col)
        return _mom(d["w"])

    md = ["# CONSENSUS_EARNINGS_FORECAST — 'standardized' candidate sweep",
          "", "systematic-debugging Phase 3. ONE variable = the "
          "standardization operator; data/scopes/1%-winsor/window fixed. "
          "IBES Detail EPS/FPI=6 2009-2016, consensus = mean across "
          "analysts per (gvkey,fpedats). Campello programmatic from "
          "table1_pdfpage21. NO spec change, NO verdict (Sina-gated).",
          ""]
    for gs, lab in ((UNI, "UNIVERSE (A)"), (G_T, "TREATED (B)"),
                    (G_C, "CONTROL (C)")):
        c = camp.get(lab, {})
        md += [f"## {lab}",
               f"Campello target: mean {c.get('mean'):+.3f} | SD "
               f"{c.get('sd'):.3f} | med {c.get('med'):+.3f} | IQR "
               f"{c.get('iqr'):.3f} | N {c.get('n'):,}", "",
               "| candidate | mean | SD | med | IQR | N | SD/IQR |",
               "|--|--|--|--|--|--|--|"]
        print(f"\n{lab}  Campello SD {c.get('sd')} med {c.get('med')} "
              f"IQR {c.get('iqr')}")
        for cand in CAND:
            r = scope(cand, gs)
            sdiqr = (r["sd"] / r["iqr"]) if r["iqr"] else float("nan")
            md.append(f"| {cand} | {r['mean']:+.3f} | {r['sd']:.3f} | "
                      f"{r['med']:+.3f} | {r['iqr']:.3f} | {r['n']:,} | "
                      f"{sdiqr:.2f} |")
            print(f"  {cand:12s} mean {r['mean']:+.3f} SD {r['sd']:.3f} "
                  f"med {r['med']:+.3f} IQR {r['iqr']:.3f} N {r['n']:,}")
        md.append("")

    md += ["## Read (NO verdict — Sina-gated)",
           "Match = same SHAPE as Campello (center≈0, SD 2.3-3.5, IQR~2, "
           "SD/IQR≈1.5-1.7), not exact N (universe differs: ours = step1 "
           "∩ βᵁᴷ-estimable, not full COMPUSTAT). A candidate that "
           "reproduces center+SD+IQR+SD/IQR on ALL THREE panels is the "
           "operationalization. If none: round 2 adds price-deflated "
           "(Compustat prccq join). Spec change Sina-gated; this is "
           "fingerprint evidence only."]
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nwritten → {OUT}")


if __name__ == "__main__":
    main()
