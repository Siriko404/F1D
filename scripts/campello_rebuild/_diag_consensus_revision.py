"""DIAG — CONSENSUS as FORECAST-ONLY standardized revision (2026-05-18).

Sina fidelity constraint (2026-05-18): the explicit Campello definition
"the standardized mean 1-quarter-ahead EPS forecast" contains NO
actual/surprise/realized — any `actual`-based SUE deviates from the
verbatim text. This test is forecast-only: the standardized consensus
REVISION, built entirely from IBES `MEANEST`/`STDEV` across the monthly
`STATPERS` series. NO ACTUAL is read.

Rationale: a plain z-score of the forecast LEVEL is SD≡1 (refuted by
Campello's own SD 3.51). The change in the standardized mean forecast
(consensus revision ÷ dispersion) is still purely a forecast object,
is symmetric (center≈0), peaked + fat-tailed (Campello SD/IQR≈1.7).

Source: `inputs/tr_ibes/ibes_statsum.zip` (IBES Summary, unextracted).
Filters EPS/FISCALP=QTR/FPI=6/CURCODE=USD/USFIRM=1. Per (gvkey,FPEDATS)
IBES emits monthly STATPERS rows; sort by STATPERS, compute revision,
then take the 1-quarter-ahead snapshot (snap_last = most recent
statpers ≤ fpe; snap_q = nearest ~90d before fpe).

Variants (forecast-only; ONE var = revision form; scopes/1%-winsor/
window fixed):
  rev_step_q   (MEANEST_t − MEANEST_{prev statpers}) / STDEV_t   @snap_q
  rev_step_last  same                                            @snap_last
  rev_cum_q    (MEANEST_snap − MEANEST_{first statpers,fpe}) / STDEV_snap @snap_q
  rev_step_q_f  −rev_step_q                                       (sign test)

1% winsor within cal_yr_qtr; scopes UNI/T/C (step1∩step3); window
2010Q1-2015Q4; Campello programmatic. Read-only; NO builder/spec
change (Sina-gated); NO replication verdict (gated).
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

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

ZIP = ROOT / "inputs" / "tr_ibes" / "ibes_statsum.zip"
T1 = ROOT / "tmp" / "campello_pdf_extract" / "table1_pdfpage21.txt"
OUT = ROOT / "tmp" / "campello_consensus_revision_2026_05_18.md"
QLO, QHI, WIN = 20101, 20154, 0.01
KEY = "CONSENSUS_EARNINGS_FORECAST"
PANELS = [("PanelA.COMPUSTAT", "Market-BasedApproach", "UNIVERSE (A)"),
          ("PanelB.TreatedFirms:", "Market-BasedApproach", "TREATED (B)"),
          ("PanelC.ControlFirms:", "(continuedonnextpage)", "CONTROL (C)")]
_ROW = re.compile(r"^([A-Z][A-Z0-9_&]+(?:\([^)]*\))?)\s+(-?\d+\.\d+)\s+"
                  r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+([\d,]+)\s*$")
VARS = ["rev_step_q", "rev_step_last", "rev_cum_q", "rev_step_q_f"]


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


def _load() -> pd.DataFrame:
    """statsum, forecast-only (NO ACTUAL column read)."""
    zf = zipfile.ZipFile(ZIP)
    mem = zf.namelist()[0]
    use = ["CUSIP", "OFTIC", "TICKER", "STATPERS", "MEASURE", "FISCALP",
           "FPI", "CURCODE", "MEANEST", "STDEV", "USFIRM", "FPEDATS"]
    with zf.open(mem) as fh:
        df = pd.read_csv(fh, usecols=use, low_memory=False)
    df = df[(df["MEASURE"] == "EPS") & (df["FISCALP"] == "QTR") &
            (pd.to_numeric(df["FPI"], errors="coerce") == 6) &
            (df["CURCODE"] == "USD") &
            (pd.to_numeric(df["USFIRM"], errors="coerce") == 1)].copy()
    df["fpe"] = pd.to_datetime(df["FPEDATS"], errors="coerce")
    df["sp"] = pd.to_datetime(df["STATPERS"], errors="coerce")
    df = df.dropna(subset=["fpe", "sp"])
    for c in ("MEANEST", "STDEV"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["MEANEST"])
    df["horizon"] = (df["fpe"] - df["sp"]).dt.days
    df = df[df["horizon"] >= 0].copy()
    df["cusip8"] = df["CUSIP"].astype(str).str.zfill(8).str[:8]
    df["cusip8"] = df["cusip8"].where(
        ~df["cusip8"].isin(["00000000", "nan", "NaN", "None", ""]))
    df["oftic_up"] = df["OFTIC"].astype(str).str.upper().str.strip()
    df["ticker_up"] = df["TICKER"].astype(str).str.upper().str.strip()
    cu = _load_cusip_to_gvkey_map(ROOT)
    tk = _load_ticker_to_gvkey_map(ROOT)
    gc = _timevar_lookup(df, "cusip8", cu, "cusip8", date_col="fpe")
    go = _timevar_lookup(df, "oftic_up", tk, "tic", date_col="fpe")
    gt = _timevar_lookup(df, "ticker_up", tk, "tic", date_col="fpe")
    df["gvkey"] = gc.fillna(go).fillna(gt)
    df = df.dropna(subset=["gvkey"]).copy()
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cal_yr_qtr"] = df["fpe"].apply(_fpedats_to_cal_yr_qtr)
    # revision across the monthly STATPERS series within (gvkey,fpe)
    df = df.sort_values(["gvkey", "fpe", "sp"], kind="stable")
    g = df.groupby(["gvkey", "fpe"], observed=True)["MEANEST"]
    df["rev_step"] = g.diff()                       # ΔMEANEST month-over-mo
    df["mean_first"] = g.transform("first")
    df["rev_cum"] = df["MEANEST"] - df["mean_first"]   # total revision
    return df


def _pick(df: pd.DataFrame, how: str) -> pd.DataFrame:
    if how == "snap_last":
        idx = df.groupby(["gvkey", "fpe"], observed=True)["horizon"].idxmin()
    else:
        d = df.assign(_d=(df["horizon"] - 90).abs())
        idx = d.groupby(["gvkey", "fpe"], observed=True)["_d"].idxmin()
    s = df.loc[idx].copy()
    sd = s["STDEV"].where(s["STDEV"] > 0)
    s["_rev_step"] = s["rev_step"] / sd
    s["_rev_cum"] = s["rev_cum"] / sd
    return s


def _wins(df, col):
    return df.groupby("cal_yr_qtr", observed=True)[col].transform(
        lambda x: x.clip(x.quantile(WIN), x.quantile(1 - WIN)))


def main() -> None:
    print("=== DIAG — CONSENSUS forecast-only standardized revision ===\n")
    camp = _camp()
    df = _load()
    print(f"statsum EPS/QTR/FPI6/USD/US + gvkey + horizon≥0: {len(df):,} "
          f"rows  firms {df['gvkey'].nunique():,}")
    snap_q = _pick(df, "snap_q")
    snap_last = _pick(df, "snap_last")
    snap_q["rev_step_q"] = snap_q["_rev_step"]
    snap_q["rev_cum_q"] = snap_q["_rev_cum"]
    snap_q["rev_step_q_f"] = -snap_q["_rev_step"]
    snap_last["rev_step_last"] = snap_last["_rev_step"]
    SRC = {"rev_step_q": snap_q, "rev_cum_q": snap_q,
           "rev_step_q_f": snap_q, "rev_step_last": snap_last}

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

    md = ["# CONSENSUS — forecast-only standardized revision (statsum)",
          "", "FORECAST-ONLY (no ACTUAL). Standardized consensus revision "
          "ΔMEANEST/STDEV across IBES monthly STATPERS. Honors verbatim "
          "'standardized mean 1-qtr-ahead forecast' (no surprise term). "
          "1% winsor within cal_yr_qtr, 2010Q1-2015Q4. Campello "
          "programmatic. NO spec change, NO verdict (Sina-gated).", ""]
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
        for v in VARS:
            r = scope(SRC[v], v, gs)
            si = (r["sd"] / r["iqr"]) if r["iqr"] else float("nan")
            md.append(f"| {v} | {r['mean']:+.3f} | {r['sd']:.3f} | "
                      f"{r['med']:+.3f} | {r['iqr']:.3f} | {r['n']:,} | "
                      f"{si:.2f} |")
            print(f"  {v:14s} mean {r['mean']:+.3f} SD {r['sd']:.3f} "
                  f"med {r['med']:+.3f} IQR {r['iqr']:.3f} N {r['n']:,}")
        md.append("")
    md += ["## Read (NO verdict — Sina-gated)",
           "Forecast-only, no deviation from explicit text. Match = "
           "Campello SHAPE all 3 panels: center≈0, SD 2.3-3.5, IQR~2. N "
           "differs (universe). Spec change Sina-gated; fingerprint "
           "evidence only."]
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nwritten → {OUT}")


if __name__ == "__main__":
    main()
