"""DIAG — programmatic moment fingerprint: rebuild vs Campello Table 1.

Computes the rebuild's actual mean/median/SD/N on Campello's exact
window (2010Q1-2015Q4) for every built variable (CASH under BOTH
denominators + the 6 controls), and tabulates against the Campello
numbers PARSED from the pdfplumber extract (tmp/campello_pdf_extract/
table1_pdfpage21.txt) — neither side is hand-typed.

Scopes:
  UNIVERSE  = step1 sample (our COMPUSTAT-screened set)  ~ Campello Panel A
  TREATED   = step3 group==treated                       ~ Campello Panel B
  CONTROL   = step3 group==control                       ~ Campello Panel C

All vars winsorized 1% within cal_yr_qtr (Campello: "All variables are
winsorized at the 1% level") so moments are comparable to the reported
(winsorized) Table 1. Read-only; prints only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
T1_EXTRACT = ROOT / "tmp" / "campello_pdf_extract" / "table1_pdfpage21.txt"
QLO, QHI = 20101, 20154          # Campello Table 1 window 2010Q1-2015Q4
WIN = 0.01


def _latest(sub: str) -> Path:
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def _prev_q(yq: int) -> int:
    yr, q = yq // 10, yq % 10
    return (yr - 1) * 10 + 4 if q == 1 else yr * 10 + (q - 1)


def _wins(s: pd.Series) -> pd.Series:
    return s.clip(s.quantile(WIN), s.quantile(1 - WIN))


def _wins_within(df: pd.DataFrame, col: str) -> pd.Series:
    return df.groupby("cal_yr_qtr", observed=True)[col].transform(_wins)


def _mom(s: pd.Series) -> str:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) == 0:
        return "  n=0"
    return (f"mean {s.mean():+.3f}  SD {s.std():.3f}  "
            f"med {s.median():+.3f}  N {len(s):,}")


def _build(cls_name: str) -> pd.DataFrame:
    import importlib
    mod = {
        "BrexitStockReturnBuilder": "brexit_stock_return",
        "BrexitTobinsQBuilder": "brexit_tobins_q",
        "BrexitCashFlowBuilder": "brexit_cash_flow",
        "BrexitSalesGrowthBuilder": "brexit_sales_growth",
        "BrexitConsensusEPSBuilder": "brexit_consensus_eps",
    }[cls_name]
    m = importlib.import_module(f"f1d.shared.variables.{mod}")
    d = getattr(m, cls_name)().build(range(2009, 2017), root_path=ROOT).data.copy()
    d["gvkey"] = d["gvkey"].astype(str).str.zfill(6)
    d["cal_yr_qtr"] = d["cal_yr_qtr"].astype("int64")
    col = [c for c in d.columns if c not in ("gvkey", "cal_yr_qtr")][0]
    return d[["gvkey", "cal_yr_qtr", col]].rename(columns={col: "v"})


def _cash_both() -> pd.DataFrame:
    """CASH under Table-1 (cheq/atq_l1) and Table-8 (cheq/(atq_l1-cheq_l1))
    denominators, same rows / screens as step7 _cash_dv."""
    df = pq.read_table(COMP, columns=["gvkey", "datadate", "curcdq", "loc",
                       "consol", "indfmt", "datafmt", "atq", "cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= pd.Timestamp("2008-01-01"))
            & (df["datadate"] <= pd.Timestamp("2016-12-31"))]
    df = df[(df["curcdq"] == "USD") & (df["loc"] == "USA")
            & (df["consol"] == "C") & (df["indfmt"] == "INDL")
            & (df["datafmt"] == "STD")].copy()
    for c in ("atq", "cheq"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10
                        + df["datadate"].dt.quarter).astype("int64")
    df = (df.sort_values(["gvkey", "cal_yr_qtr", "datadate"], kind="stable")
            .drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last"))
    src = df[["gvkey", "cal_yr_qtr", "atq", "cheq"]].rename(
        columns={"cal_yr_qtr": "_pq", "atq": "atq_l1", "cheq": "cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")
    df = df[df["cheq"].notna()].copy()
    df["CASH_T1"] = np.where(df["atq_l1"] > 0, df["cheq"] / df["atq_l1"], np.nan)
    d8 = df["atq_l1"] - df["cheq_l1"]
    df["CASH_T8"] = np.where(d8 > 0, df["cheq"] / d8, np.nan)
    return df[["gvkey", "cal_yr_qtr", "CASH_T1", "CASH_T8"]]


def _parse_campello_panelA() -> dict:
    """Parse Panel A var rows from the pdfplumber Table-1 extract.
    Lines look like: 'CASH 0.22 0.25 0.12 0.27 78,044' (after Panel A.)."""
    txt = T1_EXTRACT.read_text(encoding="utf-8")
    seg = txt.split("PanelA.COMPUSTAT")[-1].split("Market-BasedApproach")[0]
    pat = re.compile(
        r"^([A-Z][A-Z0-9_&]+(?:\([^)]*\))?)\s+"
        r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+"
        r"([\d,]+)\s*$")
    out = {}
    for ln in seg.splitlines():
        m = pat.match(ln.strip())
        if m:
            out[m.group(1)] = dict(mean=float(m.group(2)),
                                   sd=float(m.group(3)),
                                   med=float(m.group(4)),
                                   iqr=float(m.group(5)),
                                   n=int(m.group(6).replace(",", "")))
    return out


def main() -> None:
    print("=== MOMENT FINGERPRINT — rebuild vs Campello Table 1 "
          "(2010Q1-2015Q4, 1% winsor) ===\n")
    camp = _parse_campello_panelA()
    print("Campello Panel A parsed from pdfplumber extract (NOT typed):")
    for k in ("CASH", "TOBIN_Q", "CASH_FLOW", "SIZE(LogAssets)",
              "SALES_GROWTH", "CONSENSUS_EARNINGS_FORECAST", "STOCK_RETURNS"):
        if k in camp:
            c = camp[k]
            print(f"  {k:28s} mean {c['mean']:+.3f}  SD {c['sd']:.3f}  "
                  f"med {c['med']:+.3f}  N {c['n']:,}")
    print()

    s1d = _latest("step1_sample")
    s3d = _latest("step3_treatment")
    s1 = pd.read_parquet(s1d / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    s1["cal_yr_qtr"] = s1["cal_yr_qtr"].astype("int64")
    s1 = s1[(s1.cal_yr_qtr >= QLO) & (s1.cal_yr_qtr <= QHI)].copy()
    trt = pd.read_parquet(s3d / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    trt = trt[trt["in_step1"]]
    g_t = set(trt[trt.group == "treated"].gvkey)
    g_c = set(trt[trt.group == "control"].gvkey)
    uni = set(s1.gvkey)
    print(f"step1={s1d.name}  step3={s3d.name}  "
          f"universe gvkeys={len(uni):,}  treated={len(g_t):,}  "
          f"control={len(g_c):,}\n")

    def scope_rows(df):
        d = df[(df.cal_yr_qtr >= QLO) & (df.cal_yr_qtr <= QHI)].copy()
        return d[d.gvkey.isin(uni)]

    # ---- CASH both denominators ----
    cash = _cash_both()
    cash = cash[(cash.cal_yr_qtr >= QLO) & (cash.cal_yr_qtr <= QHI)]
    cash = cash[cash.gvkey.isin(uni)].copy()
    for col in ("CASH_T1", "CASH_T8"):
        cash[col + "_w"] = _wins_within(cash.dropna(subset=[col]), col) \
            if cash[col].notna().any() else np.nan
    cw = cash.copy()
    cw["CASH_T1_w"] = _wins_within(cw, "CASH_T1")
    cw["CASH_T8_w"] = _wins_within(cw, "CASH_T8")
    print("CASH (rebuild rows, winsor within qtr):")
    print(f"  Table-1 denom cheq/atq_l1       UNIVERSE {_mom(cw['CASH_T1_w'])}")
    print(f"  Table-8 denom cheq/(atq-cheq)   UNIVERSE {_mom(cw['CASH_T8_w'])}")
    for nm, gs in (("TREATED", g_t), ("CONTROL", g_c)):
        sub = cw[cw.gvkey.isin(gs)]
        print(f"  Table-1 {nm:8s} {_mom(sub['CASH_T1_w'])}")
        print(f"  Table-8 {nm:8s} {_mom(sub['CASH_T8_w'])}")
    if "CASH" in camp:
        print(f"  >> Campello CASH Panel A med {camp['CASH']['med']:+.3f} "
              f"mean {camp['CASH']['mean']:+.3f}  | B med 0.11 | C med 0.11")
    print()

    # ---- SIZE = ln(atq) contemporaneous, universe ----
    sz = s1[s1.atq > 0].copy()
    sz["v"] = np.log(sz["atq"])
    sz["v"] = _wins_within(sz, "v")
    print(f"SIZE ln(atq)  UNIVERSE {_mom(sz['v'])}"
          f"   >> Campello {('mean %+.3f med %+.3f' % (camp['SIZE(LogAssets)']['mean'], camp['SIZE(LogAssets)']['med'])) if 'SIZE(LogAssets)' in camp else 'n/a'}")

    # ---- 6 builder controls ----
    jobs = [
        ("brexit_stock_return", "BrexitStockReturnBuilder", "STOCK_RETURNS"),
        ("brexit_tobins_q", "BrexitTobinsQBuilder", "TOBIN_Q"),
        ("brexit_cash_flow", "BrexitCashFlowBuilder", "CASH_FLOW"),
        ("brexit_sales_growth", "BrexitSalesGrowthBuilder", "SALES_GROWTH"),
        ("brexit_consensus_eps", "BrexitConsensusEPSBuilder",
         "CONSENSUS_EARNINGS_FORECAST"),
    ]
    for label, cls, cname in jobs:
        try:
            d = _build(cls)
        except Exception as e:
            print(f"{label}: BUILD ERROR {e}")
            continue
        d = scope_rows(d)
        if d.empty:
            print(f"{label}: no rows in window/universe")
            continue
        d["vw"] = _wins_within(d, "v")
        cc = camp.get(cname)
        ctxt = (f"   >> Campello mean {cc['mean']:+.3f} SD {cc['sd']:.3f} "
                f"med {cc['med']:+.3f}" if cc else "   >> Campello n/a")
        print(f"{label:22s} UNIVERSE {_mom(d['vw'])}{ctxt}")

    print("\n[Programmatic. Decisive check: does Table-1 or Table-8 CASH "
          "denominator reproduce Campello CASH med 0.12 / mean 0.22? "
          "Controls: do builder moments match their Campello fingerprint? "
          "No verdict — evidence for Sina.]")


if __name__ == "__main__":
    main()
