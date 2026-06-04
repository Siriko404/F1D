"""DIAG — CONSENSUS SUE round 2: clean 1Q-ahead snapshot (2026-05-18).

systematic-debugging Phase 3 (Sina-authorized 2026-05-18 "try the
surprise formula"). Round-1 sweep (_diag_consensus_standardized_sweep.py)
found SUE=(actual-consensus)/σ_analyst reproduces Campello's SD/IQR but
center was +0.6-0.9 (Campello ≈0). Phase-1 data inspection ROOT CAUSE:
IBES `ACTUAL` is period-aligned (1 value per (gvkey,fpedats), verified)
— NOT an annual mismatch; the offset was an ARTIFACT of averaging ALL
analyst rows per period incl. ultra-stale (horizon up to 1671d) and
post-period (horizon<0) estimates. Clean A−F surprise median = +$0.009
≈ 0 (matches Campello center). Fix tested here: build consensus + σ from
each analyst's LATEST estimate issued BEFORE period end (true
"1-quarter-ahead consensus"), then SUE.

Campello target (programmatic table1_pdfpage21):
  A mean 0.07 SD 3.51 med 0.09 IQR 2.05 | B 0.01 3.40 0.01 1.83
  | C 0.07 2.33 0.04 2.40 ; center≈0, SD 2.3-3.5, IQR~2.

Variants (ONE variable = the snapshot/sign; data/scopes/1%-winsor/window
fixed): per (gvkey,fpedats,analyst) keep the analyst's LAST estimate with
horizon=fpedats−anndats in the stated window; consensus F=mean over
analysts, σ=std over analysts; A=ACTUAL (period-aligned).
  sue_pre    horizon>=0 (any pre-period), SUE=(A−F)/σ
  sue_pre_f  horizon>=0,                  SUE=(F−A)/σ  (sign test)
  sue_120    horizon in [0,120]d,         SUE=(A−F)/σ
  sue_120f   horizon in [0,120]d,         SUE=(F−A)/σ
  fcst_z120  horizon in [0,120]d, standardized FORECAST (F−μ_xsec)/σ_xsec
             within cal_yr_qtr  (Sina's "standardized=z-score" reading,
             clean snapshot — included for completeness/fairness)

IBES Detail EPS/FPI=6 2009-2016 (memory-aware), loaders reused.
Read-only; NO builder/spec change (Sina-gated); NO verdict (gated).
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

from f1d.shared.variables.brexit_consensus_eps import (
    _fpedats_to_cal_yr_qtr, _load_cusip_to_gvkey_map,
    _load_ticker_to_gvkey_map, _timevar_lookup,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

T1 = ROOT / "tmp" / "campello_pdf_extract" / "table1_pdfpage21.txt"
OUT = ROOT / "tmp" / "campello_consensus_sue_round2_2026_05_18.md"
QLO, QHI, WIN = 20101, 20154, 0.01
KEY = "CONSENSUS_EARNINGS_FORECAST"
PANELS = [("PanelA.COMPUSTAT", "Market-BasedApproach", "UNIVERSE (A)"),
          ("PanelB.TreatedFirms:", "Market-BasedApproach", "TREATED (B)"),
          ("PanelC.ControlFirms:", "(continuedonnextpage)", "CONTROL (C)")]
_ROW = re.compile(r"^([A-Z][A-Z0-9_&]+(?:\([^)]*\))?)\s+(-?\d+\.\d+)\s+"
                  r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+([\d,]+)\s*$")
VARIANTS = ["sue_pre", "sue_120", "fcst_z120", "sue_ts", "sue_absF",
            "sue_ts_f"]


def _camp() -> dict:
    txt = T1.read_text(encoding="utf-8")
    out = {}
    for s, e, lab in PANELS:
        seg = txt.split(s)[-1].split(e)[0]
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


def _load(cu, tk) -> pd.DataFrame:
    files = sorted((ROOT / "inputs" / "tr_ibes").glob("tr_ibes_*.parquet"))
    cols = ["CUSIP", "OFTIC", "TICKER", "ANALYS", "VALUE", "ACTUAL",
            "MEASURE", "FPI", "FPEDATS", "ANNDATS"]
    out = []
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
        d = d.dropna(subset=["VALUE", "FPEDATS", "ANNDATS"])
        d["fpe"] = pd.to_datetime(d["FPEDATS"], errors="coerce")
        d["ann"] = pd.to_datetime(d["ANNDATS"], errors="coerce")
        d = d.dropna(subset=["fpe", "ann"])
        d["cusip8"] = d["CUSIP"].astype(str).str[:8]
        d["cusip8"] = d["cusip8"].where(
            ~d["cusip8"].isin(["00000000", "nan", "NaN", "None", ""]))
        d["oftic_up"] = d["OFTIC"].astype(str).str.upper().str.strip()
        d["ticker_up"] = d["TICKER"].astype(str).str.upper().str.strip()
        gc = _timevar_lookup(d, "cusip8", cu, "cusip8", date_col="fpe")
        go = _timevar_lookup(d, "oftic_up", tk, "tic", date_col="fpe")
        gt = _timevar_lookup(d, "ticker_up", tk, "tic", date_col="fpe")
        d["gvkey"] = gc.fillna(go).fillna(gt)
        d = d.dropna(subset=["gvkey"]).copy()
        d["VALUE"] = pd.to_numeric(d["VALUE"], errors="coerce")
        d["ACTUAL"] = pd.to_numeric(d["ACTUAL"], errors="coerce")
        d = d.dropna(subset=["VALUE"])
        d["horizon"] = (d["fpe"] - d["ann"]).dt.days
        out.append(d[["gvkey", "fpe", "ANALYS", "VALUE", "ACTUAL",
                      "horizon"]])
    return pd.concat(out, ignore_index=True)


def _consensus(raw: pd.DataFrame, hmin, hmax) -> pd.DataFrame:
    """Per (gvkey,fpe,analyst) take the analyst's LATEST pre-period
    estimate within [hmin,hmax] horizon days; then consensus mean + σ
    across analysts; ACTUAL is period-aligned (first)."""
    d = raw[(raw.horizon >= hmin)]
    if hmax is not None:
        d = d[d.horizon <= hmax]
    # latest estimate per analyst = smallest horizon (closest to period end)
    d = d.sort_values("horizon").drop_duplicates(
        ["gvkey", "fpe", "ANALYS"], keep="first")
    g = d.groupby(["gvkey", "fpe"], observed=True)
    c = g.agg(F=("VALUE", "mean"), disp=("VALUE", "std"),
              A=("ACTUAL", "first"), nest=("VALUE", "size")).reset_index()
    c["gvkey"] = c["gvkey"].astype(str).str.zfill(6)
    c["cal_yr_qtr"] = c["fpe"].apply(_fpedats_to_cal_yr_qtr)
    return c


def _wins(df, col):
    return df.groupby("cal_yr_qtr", observed=True)[col].transform(
        lambda x: x.clip(x.quantile(WIN), x.quantile(1 - WIN)))


def main() -> None:
    print("=== DIAG — CONSENSUS SUE round 2 (clean 1Q snapshot) ===\n")
    camp = _camp()
    cu = _load_cusip_to_gvkey_map(ROOT)
    tk = _load_ticker_to_gvkey_map(ROOT)
    raw = _load(cu, tk)

    pre = _consensus(raw, 0, None)
    w120 = _consensus(raw, 0, 120)
    for c in (pre, w120):
        dd = c["disp"].where(c["disp"] > 0)
        c["_sA"] = (c["A"] - c["F"]) / dd
        c["_sF"] = (c["F"] - c["A"]) / dd
    pre["sue_pre"] = pre["_sA"]
    pre["sue_pre_f"] = pre["_sF"]
    w120["sue_120"] = w120["_sA"]
    w120["sue_120f"] = w120["_sF"]
    gq = w120.groupby("cal_yr_qtr")["F"]
    w120["fcst_z120"] = (w120["F"] - gq.transform("mean")) / gq.transform(
        "std").where(gq.transform("std") > 0)
    # Foster-Olsen-Shevlin SUE: surprise ÷ firm time-series std of
    # surprise (the textbook "standardized unexpected earnings"
    # deflator), and a forecast-magnitude deflator complement.
    pre["_surp"] = pre["A"] - pre["F"]
    ts = pre.sort_values(["gvkey", "fpe"]).groupby("gvkey")["_surp"]
    ts_sd = ts.transform("std")
    pre["sue_ts"] = np.where(ts_sd > 0, pre["_surp"] / ts_sd, np.nan)
    pre["sue_ts_f"] = -pre["sue_ts"]
    fa = pre["F"].abs().where(pre["F"].abs() > 0)
    pre["sue_absF"] = pre["_surp"] / fa
    SRC = {"sue_pre": pre, "sue_120": w120, "fcst_z120": w120,
           "sue_ts": pre, "sue_absF": pre, "sue_ts_f": pre}

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    trt = pd.read_parquet(_latest("step3_treatment") / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    trt = trt[trt["in_step1"]]
    UNI = set(s1.gvkey)
    G_T = set(trt[trt.group == "treated"].gvkey)
    G_C = set(trt[trt.group == "control"].gvkey)

    def scope(src, col, gs):
        d = src[(src.cal_yr_qtr >= QLO) & (src.cal_yr_qtr <= QHI)].copy()
        d = d[d.gvkey.isin(gs)].dropna(subset=[col])
        if d.empty:
            return _mom(pd.Series(dtype=float))
        d["w"] = _wins(d, col)
        return _mom(d["w"])

    md = ["# CONSENSUS SUE round 2 — clean 1Q-ahead snapshot", "",
          "Root cause (Phase-1 data inspect): round-1 +0.6 offset = "
          "averaging stale+post-period analyst rows. Here consensus+σ "
          "use each analyst's LATEST pre-period estimate. ACTUAL "
          "period-aligned (verified 1/(gvkey,fpedats)). NO spec change, "
          "NO verdict (Sina-gated).", ""]
    for gs, lab in ((UNI, "UNIVERSE (A)"), (G_T, "TREATED (B)"),
                    (G_C, "CONTROL (C)")):
        c = camp.get(lab, {})
        md += [f"## {lab}",
               f"Campello: mean {c.get('mean'):+.3f} SD {c.get('sd'):.3f} "
               f"med {c.get('med'):+.3f} IQR {c.get('iqr'):.3f} N "
               f"{c.get('n'):,}", "",
               "| variant | mean | SD | med | IQR | N | SD/IQR |",
               "|--|--|--|--|--|--|--|"]
        print(f"\n{lab}  Campello mean {c.get('mean')} SD {c.get('sd')} "
              f"med {c.get('med')} IQR {c.get('iqr')}")
        for v in VARIANTS:
            r = scope(SRC[v], v, gs)
            si = (r["sd"] / r["iqr"]) if r["iqr"] else float("nan")
            md.append(f"| {v} | {r['mean']:+.3f} | {r['sd']:.3f} | "
                      f"{r['med']:+.3f} | {r['iqr']:.3f} | {r['n']:,} | "
                      f"{si:.2f} |")
            print(f"  {v:10s} mean {r['mean']:+.3f} SD {r['sd']:.3f} "
                  f"med {r['med']:+.3f} IQR {r['iqr']:.3f} N {r['n']:,}")
        md.append("")
    md += ["## Read (NO verdict — Sina-gated)",
           "Match = Campello SHAPE on ALL 3 panels: center≈0, SD 2.3-3.5, "
           "IQR~2. N differs (universe: ours step1∩βᵁᴷ-estimable). "
           "fcst_z120 included to fairly test Sina's literal "
           "'standardized=z-score of the forecast' on a clean snapshot. "
           "Spec change Sina-gated; fingerprint evidence only."]
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nwritten → {OUT}")


if __name__ == "__main__":
    main()
