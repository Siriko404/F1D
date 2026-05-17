"""Step 6+7 data-inventory probe (advisor-mandated) — EVIDENCE ONLY.

NOT a builder. NO regression. NO fix. NO memory edit. NO commit. Verifies
that every input the real eq-14 cash build needs actually exists on THIS
machine, covers 2015-2016, and is readable — before any builder code is
written. One JSON report + printed verdict. Tier-0.

Inputs interrogated (paths discovered, not assumed):
  raw Compustat   inputs/comp_na_daily_all/        cheq/atq/saleq/dlttq/dlcq/
                                                   oibdpq/xintq/txtq/prccq/
                                                   cshoq/niq/ibq
  OCF extended    inputs/Compustat_Quarterly_OCF_Extended/   oancfq candidate
  CRSP DSF        inputs/CRSP_DSF/                 2015-2016 daily returns
  CCM link        inputs/CRSPCompustat_CCM/        gvkey<->permno
  IBES            inputs/tr_ibes/                  consensus EPS, FPI
  FIC-100         inputs/Brexit_replication/HobergPhillips_FIC/FIC_Data.zip
  macro: BoE FX, CBOE VIX, UMich UMCSENT, PhillyFed Livingston + LEI/ADS

Window quarters needed: 2015Q3/Q4, 2016Q3/Q4 (regression) + 2015Q2, 2016Q2
(the t-1 lag of CONTROLS) -> cal_yr_qtr {20152,20153,20154,20162,20163,20164}.

zip read in-place (never extract — per feedback_zip_in_place_data_access).
"""
from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
INP = ROOT / "inputs"
S4 = ROOT / "outputs" / "campello_rebuild" / "step4_timeline"
OUT = ROOT / "outputs" / "campello_rebuild" / "s67_inventory"

NEED_Q = {20152, 20153, 20154, 20162, 20163, 20164}
rep: dict = {"generated": datetime.now().isoformat(timespec="seconds"),
             "checks": {}, "critical_missing": [], "flags": []}


def crit(msg: str) -> None:
    rep["critical_missing"].append(msg)


def flag(msg: str) -> None:
    rep["flags"].append(msg)


def latest(b: Path, f: str) -> Path | None:
    if not b.exists():
        return None
    s = sorted(d for d in b.iterdir() if d.is_dir())
    return (s[-1] / f) if s else None


# ---- 0. panel firms -----------------------------------------------------
s4 = latest(S4, "panel.parquet")
panel_gv: set[str] = set()
if s4 and s4.exists():
    pg = pq.read_table(s4, columns=["gvkey"]).to_pandas()
    panel_gv = set(pg["gvkey"].astype(str))
    rep["checks"]["panel"] = {"path": str(s4), "n_firms": len(panel_gv)}
else:
    crit("step4 panel.parquet not found (run step4_timeline.py)")
rep["checks"]["panel"] = rep["checks"].get("panel", {"n_firms": 0})


# ---- 1. raw Compustat coverage -----------------------------------------
def chk_compustat() -> None:
    raw = INP / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    if not raw.exists():
        crit(f"raw Compustat missing: {raw}")
        return
    cols = ["gvkey", "datadate", "cheq", "atq", "saleq", "dlttq", "dlcq",
            "oibdpq", "xintq", "txtq", "prccq", "cshoq", "niq", "ibq"]
    sch = {f.name for f in pq.read_schema(raw)}
    miss = [c for c in cols if c not in sch]
    df = pq.read_table(raw, columns=[c for c in cols if c in sch]).to_pandas()
    df["gvkey"] = df["gvkey"].astype(str)
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    q = ((df["datadate"].dt.month - 1) // 3 + 1).astype("Int64")
    df["cyq"] = (df["datadate"].dt.year * 10 + q).astype("Int64")
    sub = df[df["gvkey"].isin(panel_gv) & df["cyq"].isin(NEED_Q)]
    nn = {c: int(sub[c].notna().sum()) for c in cols
          if c in sub.columns and c not in ("gvkey", "datadate")}
    rep["checks"]["compustat_raw"] = {
        "missing_cols": miss,
        "panel_firmqtrs_in_need_window": int(len(sub)),
        "firms_covered": int(sub["gvkey"].nunique()),
        "nonnull_by_col": nn,
        "qtrs_present": sorted(int(x) for x in sub["cyq"].dropna().unique()),
    }
    if "cheq" in miss:
        crit("raw Compustat lacks cheq — cash DV impossible")
    if sub["gvkey"].nunique() < 0.5 * max(len(panel_gv), 1):
        flag("Compustat covers <50% of panel firms in 2015-16 window")


# ---- 2. OCF extended ----------------------------------------------------
def chk_ocf() -> None:
    d = INP / "Compustat_Quarterly_OCF_Extended"
    f = next(iter(d.glob("*.parquet")), None) if d.exists() else None
    if not f:
        flag("OCF_Extended parquet absent — cash-flow control must use a "
             "derived def (oibdpq-based), not oancfq")
        rep["checks"]["ocf_extended"] = {"present": False}
        return
    sch = {x.name for x in pq.read_schema(f)}
    has_ocf = "oancfq" in sch or "oancf" in sch
    rep["checks"]["ocf_extended"] = {
        "path": str(f), "has_oancfq": has_ocf,
        "cols_sample": sorted(list(sch))[:25],
    }
    if not has_ocf:
        flag("OCF_Extended lacks oancfq — cash-flow def will be derived")


# ---- 3. CRSP DSF 2015-2016 ---------------------------------------------
def chk_crsp() -> None:
    d = INP / "CRSP_DSF"
    want = [f"CRSP_DSF_{y}_Q{q}.parquet" for y in (2015, 2016)
            for q in (1, 2, 3, 4)]
    have = [w for w in want if (d / w).exists()]
    miss = [w for w in want if w not in have]
    cols = None
    if have:
        cols = sorted(x.name for x in pq.read_schema(d / have[0]))
    rep["checks"]["crsp_dsf"] = {
        "have": have, "missing": miss, "cols": cols,
    }
    if miss:
        crit(f"CRSP DSF missing 2015-16 quarters: {miss}")


# ---- 4. CCM link --------------------------------------------------------
def chk_ccm() -> None:
    f = INP / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
    if not f.exists():
        crit("CCM link parquet missing — cannot map gvkey<->permno for CRSP")
        return
    sch = sorted(x.name for x in pq.read_schema(f))
    rep["checks"]["ccm"] = {"path": str(f), "cols": sch[:30]}


# ---- 5. IBES 2015-2016 --------------------------------------------------
def chk_ibes() -> None:
    d = INP / "tr_ibes"
    files = {y: d / f"tr_ibes_{y}.parquet" for y in (2015, 2016)}
    pres = {y: p.exists() for y, p in files.items()}
    info: dict = {"present": pres}
    if pres.get(2015):
        sch = sorted(x.name for x in pq.read_schema(files[2015]))
        info["cols"] = sch
        fpi_col = next((c for c in ("fpi", "FPI") if c in sch), None)
        if fpi_col:
            t = pq.read_table(files[2015], columns=[fpi_col]).to_pandas()
            info["fpi_values"] = sorted(
                str(v) for v in t[fpi_col].dropna().unique()[:20])
    rep["checks"]["ibes"] = info
    if not all(pres.values()):
        crit(f"IBES missing year(s): "
             f"{[y for y, v in pres.items() if not v]}")


# ---- 6. FIC-100 zip (in-place) -----------------------------------------
def chk_fic() -> None:
    z = INP / "Brexit_replication" / "HobergPhillips_FIC" / "FIC_Data.zip"
    if not z.exists():
        crit(f"Hoberg-Phillips FIC zip missing: {z}")
        return
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist()
        fic100 = [n for n in names if "100" in n]
        head = ""
        tgt = fic100[0] if fic100 else (names[0] if names else None)
        if tgt:
            with zf.open(tgt) as fh:
                head = fh.read(400).decode("latin-1", "replace")
    rep["checks"]["fic100"] = {
        "zip": str(z), "members": names[:10],
        "fic100_members": fic100, "first_bytes": head[:300],
    }
    if not fic100:
        flag("no obvious FIC-100 member in zip — inspect members manually")


# ---- 7. macro files -----------------------------------------------------
def _range(df: pd.DataFrame, dcol: str) -> list[str]:
    s = pd.to_datetime(df[dcol], errors="coerce").dropna()
    return ["", ""] if s.empty else [str(s.min().date()),
                                     str(s.max().date())]


def chk_macro() -> None:
    B = INP / "Brexit_replication"
    m: dict = {}

    def note(key, path, ok, extra):
        m[key] = {"path": str(path), "exists": path.exists(),
                  "readable": ok, **extra}
        if not path.exists():
            crit(f"macro file missing: {key} ({path})")

    # BoE FX
    p = B / "BoE" / "USD_GBP_daily_2008-2018.csv"
    try:
        d = pd.read_csv(p, nrows=20000)
        note("boe_usdgbp", p, True,
             {"cols": list(d.columns)[:6], "n": len(d)})
    except Exception as e:
        note("boe_usdgbp", p, False, {"err": str(e)[:120]})
    # CBOE VIX
    p = B / "CBOE" / "VIX_daily_1990-present.csv"
    try:
        d = pd.read_csv(p, nrows=20000)
        note("cboe_vix", p, True,
             {"cols": list(d.columns)[:6], "n": len(d)})
    except Exception as e:
        note("cboe_vix", p, False, {"err": str(e)[:120]})
    # UMich
    p = B / "UMich" / "UMCSENT.csv"
    try:
        d = pd.read_csv(p, nrows=5000)
        note("umich_umcsent", p, True,
             {"cols": list(d.columns)[:6], "n": len(d)})
    except Exception as e:
        note("umich_umcsent", p, False, {"err": str(e)[:120]})
    # PhillyFed Livingston (xlsx)
    p = B / "PhillyFed" / "Livingston_means.xlsx"
    try:
        d = pd.read_excel(p, nrows=10)
        note("phillyfed_livingston", p, True,
             {"cols": list(d.columns)[:10]})
    except Exception as e:
        note("phillyfed_livingston", p, False, {"err": str(e)[:120]})
    # PhillyFed LEI (state-level, .xls) + ADS substitute (.xlsx)
    p = B / "PhillyFed" / "State_Leading_Revised.xls"
    note("phillyfed_state_leading", p, p.exists(), {})
    p2 = B / "PhillyFed" / "ADS_Index_current.xlsx"
    note("phillyfed_ads", p2, p2.exists(), {})
    flag("PhillyFed 'Leading Economic Indicator' is STATE-level "
         "(State_Leading_Revised.xls); NO national PhillyFed LEI exists. "
         "Paper §IV.C.3 cites a national series. ADS_Index_current.xlsx is "
         "the closest national PhillyFed activity proxy but using it is an "
         "explicit operationalization DEVIATION — must be flagged in "
         "step6 metadata, not silently substituted.")
    rep["checks"]["macro"] = m


for fn in (chk_compustat, chk_ocf, chk_crsp, chk_ccm, chk_ibes,
           chk_fic, chk_macro):
    try:
        fn()
    except Exception as e:  # probe must never half-die — record and go on
        rep["checks"][fn.__name__] = {"PROBE_ERROR": str(e)[:200]}
        flag(f"{fn.__name__} raised: {str(e)[:120]}")

rep["verdict"] = ("CRITICAL — inputs missing, cannot build"
                  if rep["critical_missing"]
                  else "OK — all critical inputs present "
                       "(operationalization flags remain)")

OUT.mkdir(parents=True, exist_ok=True)
ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
outf = OUT / f"{ts}_inventory.json"
outf.write_text(json.dumps(rep, indent=2, default=str))

print("STEP 6+7 DATA-INVENTORY PROBE")
print(f"  panel firms needing coverage : "
      f"{rep['checks'].get('panel', {}).get('n_firms', 0)}")
cr = rep["checks"].get("compustat_raw", {})
print(f"  Compustat firms covered      : {cr.get('firms_covered','?')} "
      f"/ qtrs {cr.get('qtrs_present','?')}")
print(f"  CRSP DSF 2015-16 missing     : "
      f"{rep['checks'].get('crsp_dsf', {}).get('missing', '?')}")
print(f"  IBES 2015/2016 present       : "
      f"{rep['checks'].get('ibes', {}).get('present', '?')}")
print(f"  FIC-100 members              : "
      f"{rep['checks'].get('fic100', {}).get('fic100_members', '?')}")
print(f"\n  CRITICAL MISSING ({len(rep['critical_missing'])}):")
for c in rep["critical_missing"]:
    print(f"    - {c}")
print(f"\n  FLAGS ({len(rep['flags'])}):")
for f in rep["flags"]:
    print(f"    - {f}")
print(f"\n  VERDICT: {rep['verdict']}")
print(f"  -> {outf}")
