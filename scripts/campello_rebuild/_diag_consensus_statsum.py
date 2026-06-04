"""DIAG — CONSENSUS via IBES Summary Statistics (statsum), 2026-05-18.

systematic-debugging Phase 3 / root-cause path (§G.3). Sina obtained the
IBES Summary file (`inputs/tr_ibes/ibes_statsum.zip`, unextracted, 10.4M
rows) — the canonical consensus source. statsum carries IBES's OWN
precomputed consensus (MEANEST), dispersion (STDEV), MEDEST, ACTUAL, at
its OWN monthly statistical period (STATPERS). This removes the two
unclosable problems of the Detail reconstruction: the consensus-snapshot
ambiguity and the σ deflator.

Verbatim Campello (table1_pdfpage21 L195-197): "CONSENSUS_EARNINGS_
FORECAST is defined as the standardized mean 1-quarter ahead earnings
per share forecast." Target (programmatic, 3 panels):
  A mean 0.07 SD 3.51 med 0.09 IQR 2.05 | B 0.01 3.40 0.01 1.83
  | C 0.07 2.33 0.04 2.40 ; center≈0, SD 2.3-3.5, IQR~2.

Filters: MEASURE=EPS (all), FISCALP=QTR, FPI=6 (1-qtr-ahead fiscal
quarter), CURCODE=USD (foreign rows = the garbage tails), USFIRM=1.
Snapshot: per (gvkey,FPEDATS) IBES emits monthly STATPERS rows; pick the
"1-quarter-ahead" consensus snapshot two ways (vagueness ⇒ test both):
  snap_last : most recent STATPERS with horizon=(FPEDATS−STATPERS)≥0
  snap_q    : STATPERS nearest ~90d before FPEDATS (literal "1-qtr ahead")
Candidates ("standardized" = surprise ÷ native STDEV — the IBES SUE):
  sue_mean  (ACTUAL−MEANEST)/STDEV     [primary literal reading]
  sue_med   (ACTUAL−MEDEST)/STDEV
  sue_mean_f(MEANEST−ACTUAL)/STDEV     [sign test]
each × {snap_last, snap_q}. 1% winsor within cal_yr_qtr; scopes
UNI/T/C (step1 ∩ step3); window 2010Q1-2015Q4; Campello programmatic.
Memory-aware (usecols + early row filter). Read-only; NO builder/spec
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
OUT = ROOT / "tmp" / "campello_consensus_statsum_2026_05_18.md"
QLO, QHI, WIN = 20101, 20154, 0.01
KEY = "CONSENSUS_EARNINGS_FORECAST"
PANELS = [("PanelA.COMPUSTAT", "Market-BasedApproach", "UNIVERSE (A)"),
          ("PanelB.TreatedFirms:", "Market-BasedApproach", "TREATED (B)"),
          ("PanelC.ControlFirms:", "(continuedonnextpage)", "CONTROL (C)")]
_ROW = re.compile(r"^([A-Z][A-Z0-9_&]+(?:\([^)]*\))?)\s+(-?\d+\.\d+)\s+"
                  r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+([\d,]+)\s*$")
VARS = ["sue_mean", "sue_med", "sue_mean_f"]
SNAPS = ["snap_last", "snap_q"]


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
    zf = zipfile.ZipFile(ZIP)
    mem = zf.namelist()[0]
    use = ["CUSIP", "OFTIC", "TICKER", "STATPERS", "MEASURE", "FISCALP",
           "FPI", "CURCODE", "MEDEST", "MEANEST", "STDEV", "USFIRM",
           "FPEDATS", "ACTUAL"]
    with zf.open(mem) as fh:
        df = pd.read_csv(fh, usecols=use, low_memory=False)
    df = df[(df["MEASURE"] == "EPS") & (df["FISCALP"] == "QTR") &
            (pd.to_numeric(df["FPI"], errors="coerce") == 6) &
            (df["CURCODE"] == "USD") &
            (pd.to_numeric(df["USFIRM"], errors="coerce") == 1)].copy()
    df["fpe"] = pd.to_datetime(df["FPEDATS"], errors="coerce")
    df["sp"] = pd.to_datetime(df["STATPERS"], errors="coerce")
    df = df.dropna(subset=["fpe", "sp"])
    for c in ("MEANEST", "MEDEST", "STDEV", "ACTUAL"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["horizon"] = (df["fpe"] - df["sp"]).dt.days
    df = df[df["horizon"] >= 0].copy()             # consensus before period
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
    df = df.dropna(subset=["gvkey", "MEANEST", "ACTUAL"]).copy()
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cal_yr_qtr"] = df["fpe"].apply(_fpedats_to_cal_yr_qtr)
    return df


def _pick(df: pd.DataFrame, how: str) -> pd.DataFrame:
    if how == "snap_last":                          # smallest horizon ≥0
        idx = df.groupby(["gvkey", "fpe"], observed=True)["horizon"].idxmin()
    else:                                           # nearest ~90d
        d = df.assign(_d=(df["horizon"] - 90).abs())
        idx = d.groupby(["gvkey", "fpe"], observed=True)["_d"].idxmin()
    s = df.loc[idx].copy()
    sd = s["STDEV"].where(s["STDEV"] > 0)
    s["sue_mean"] = (s["ACTUAL"] - s["MEANEST"]) / sd
    s["sue_med"] = (s["ACTUAL"] - s["MEDEST"]) / sd
    s["sue_mean_f"] = (s["MEANEST"] - s["ACTUAL"]) / sd
    return s


def _wins(df, col):
    return df.groupby("cal_yr_qtr", observed=True)[col].transform(
        lambda x: x.clip(x.quantile(WIN), x.quantile(1 - WIN)))


def main() -> None:
    print("=== DIAG — CONSENSUS via IBES statsum ===\n")
    camp = _camp()
    df = _load()
    print(f"statsum rows after EPS/QTR/FPI6/USD/US + gvkey + horizon≥0: "
          f"{len(df):,}  firms {df['gvkey'].nunique():,}")
    snaps = {h: _pick(df, h) for h in SNAPS}

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

    md = ["# CONSENSUS via IBES Summary Statistics (statsum)", "",
          "Root-cause path (§G.3): IBES native MEANEST/STDEV/ACTUAL at "
          "its own STATPERS. EPS/QTR/FPI=6/USD/US, horizon≥0. SUE = "
          "(ACTUAL−consensus)/STDEV. 1% winsor within cal_yr_qtr, "
          "2010Q1-2015Q4. Campello programmatic. NO spec change, NO "
          "verdict (Sina-gated).", ""]
    for gs, lab in ((UNI, "UNIVERSE (A)"), (G_T, "TREATED (B)"),
                    (G_C, "CONTROL (C)")):
        c = camp.get(lab, {})
        md += [f"## {lab}",
               f"Campello: mean {c.get('mean'):+.3f} SD {c.get('sd'):.3f} "
               f"med {c.get('med'):+.3f} IQR {c.get('iqr'):.3f} N "
               f"{c.get('n'):,}", "",
               "| snapshot | cand | mean | SD | med | IQR | N | SD/IQR |",
               "|--|--|--|--|--|--|--|--|"]
        print(f"\n{lab}  Campello mean {c.get('mean')} SD {c.get('sd')} "
              f"med {c.get('med')} IQR {c.get('iqr')} N {c.get('n')}")
        for h in SNAPS:
            for v in VARS:
                r = scope(snaps[h], v, gs)
                si = (r["sd"] / r["iqr"]) if r["iqr"] else float("nan")
                md.append(f"| {h} | {v} | {r['mean']:+.3f} | "
                          f"{r['sd']:.3f} | {r['med']:+.3f} | "
                          f"{r['iqr']:.3f} | {r['n']:,} | {si:.2f} |")
                print(f"  {h:10s} {v:11s} mean {r['mean']:+.3f} SD "
                      f"{r['sd']:.3f} med {r['med']:+.3f} IQR "
                      f"{r['iqr']:.3f} N {r['n']:,}")
        md.append("")
    md += ["## Read (NO verdict — Sina-gated)",
           "Match = Campello SHAPE on ALL 3 panels: center≈0, SD 2.3-3.5, "
           "IQR~2. N differs (universe: ours step1∩βᵁᴷ-estimable, not "
           "full COMPUSTAT). This is IBES's native consensus+σ — the "
           "canonical source Campello almost certainly used. Spec change "
           "Sina-gated; fingerprint evidence only."]
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nwritten → {OUT}")


if __name__ == "__main__":
    main()
