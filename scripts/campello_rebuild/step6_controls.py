"""Campello et al. (2022 JFQA) replication — STEP 6: controls + cash DV.

From-scratch rebuild. Assembles the eq-14 regression panel: Step-4 window
firm-quarters + the cash dependent variable + the 11 lagged CONTROLS
(5 macro, 5 firm, +1-qtr-ahead consensus EPS) + the Hoberg-Phillips FIC-100
industry code. NO regression here (Step 7). NO comparison to any prior F1D
output. Strict-sequential.

Authoritative spec — §IV.C.3 (main_p20.txt) + Table 8 (main_p31.txt) verbatim:
  "CONTROLS_{i,t-1} ... Macro controls include the lagged U.S. dollar/British
   pound FX rate, the lagged VIX ... lagged mean GDP growth 1-year-ahead
   forecast from ... Livingstone Survey, the lagged Consumer Sentiment Index
   from ... Michigan, and the lagged Leading Economic Indicator from the
   Federal Reserve Bank of Philadelphia. Firm-level controls include lagged
   stock returns, Tobin's Q, cash flow, logged assets, and sales growth ...
   we add 1-quarter-ahead consensus earnings forecasts ... INDUSTRY_j is a
   dummy for each industry category j of the Hoberg and Phillips (2016)
   classification (FIC 100) ..."
  "CASH is defined as total cash holdings divided by lagged total assets net
   of cash holdings."  ->  CASH_t = cheq_t / (atq_{t-1} - cheq_{t-1}).

Operationalization (paper-SILENT -> locked here, advisor-ratified, logged to
metadata; NEVER changed to chase significance — Step-2-vol() discipline):
  Tobin's Q   = (prccq*cshoq + dlttq + dlcq) / atq          (at t-1)
  cash flow   = oibdpq / atq_{prev qtr}   (Campello Table 1 VERBATIM:
                "operating income before depreciation / lagged total
                assets"; fixed 2026-05-16 from prior non-verbatim
                (oibdpq-xintq-txtq)/atq_t improvisation)
  log assets  = ln(atq)                                     (at t-1)
  salesgrowth = saleq_{t-1} / saleq_{t-1 minus 1 year} - 1   (YoY, kills
                seasonality; QoQ would double-count the design)
  stock ret   = prod(1+RET)-1 over calendar quarter t-1 (CRSP DSF, RET)
  EPS         = IBES FPI=6 ("1-quarter-ahead"); mean(VALUE) per firm with
                review date <= end of quarter t-1 (latest vintage)
  macro       = mean over calendar quarter t-1 (FX/VIX/UMCSENT/ADS daily or
                monthly; Livingston RGDPX_1Y semi-annual -> ffill monthly)
  *** PhillyFed "Leading Economic Indicator": NO national series exists.
      Substituted with ADS_Index (PhillyFed). This is an explicit recipe
      DEVIATION, flagged in metadata; Step 7 runs a drop-ADS sensitivity. ***
  FIC-100     = icode100 from fic_data.txt, join (gvkey, year=year(datadate_t))

Output
------
outputs/campello_rebuild/step6_controls/<timestamp>/
    controls.parquet   gvkey, cal_yr_qtr, HIGH_BETA_UK, POST, CASH_DV,
                       + 11 *_lag controls + fic100
    metadata.json      every rule above, verbatim, coverage WATERFALL,
                       per-control missingness, deviation flags

Run:  python scripts/campello_rebuild/step6_controls.py
"""

from __future__ import annotations

import io
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
INP = ROOT / "inputs"
S1B = ROOT / "outputs" / "campello_rebuild" / "step1_sample"
S4B = ROOT / "outputs" / "campello_rebuild" / "step4_timeline"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step6_controls"

RAW = INP / "comp_na_daily_all" / "comp_na_daily_all.parquet"
CCM = INP / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
DSF = INP / "CRSP_DSF"
IBES = INP / "tr_ibes"
BX = INP / "Brexit_replication"
FICZIP = BX / "HobergPhillips_FIC" / "FIC_Data.zip"

# WINDOW_Q is derived at runtime from the Step-4 panel's actual quarters
# (full 2010Q1-2016Q4 eq-14 panel after the A4 correction), passed into the
# lag loaders — NOT hardcoded. COMP_Q_LO must reach the earliest YoY lag:
# earliest t = 2010Q1 -> t-1 = 2009Q4 -> YoY-of-t-1 = 2008Q4 = 20084.
COMP_Q_LO, COMP_Q_HI = 20084, 20164

# Campello 2022 JFQA, Table 1 variable-definitions note — VERBATIM
# (tmp/campello_v2/campello_paper_FULL.md L2527-2528):
#   "All variables are winsorized at the 1% level."
# The eq-14 DV (CASH) and the firm-level controls ARE Table 1 analysis
# variables, so they MUST be winsorized 1/99 before estimation. The prior
# rebuild OMITTED this on a FALSE premise ("paper Table 8 does not
# winsorize", step7) — leaving CASH_DV max=151.6 (17x p99) as high-leverage
# points that detonate the double-clustered SE ~3.7x while barely moving the
# OLS point estimate (the observed delta~=+0.231 / SE-3.7x-wide / NS
# signature). Grouping is paper-UNDERSPECIFIED ("at the 1% level", no
# qualifier): both are run as a sensitivity — within-cal_yr_qtr (this run)
# vs pooled (prior timestamp) — and reported side-by-side; the favorable
# one is NOT silently chosen. (Pooled can asymmetrically clip the
# treated x POST cash spikes the hypothesis predicts -> sign risk; the
# within-quarter vs pooled disambiguation is itself a debugging probe.)
# Winsorize ONCE (Campello §2E). Macro EXCLUDED: time-only, FE-absorbed,
# and not in Table 1's firm-variable winsor list.
WINSOR_VARS = ["CASH_DV", "tobinq_lag", "cf_lag", "logassets_lag",
               "salesgrowth_lag", "stockret_lag", "eps_fpi6_lag"]


def _abort(msg: str) -> None:
    print(f"\nABORT — {msg}")
    print("Step 6 controls NOT built. Resolve before proceeding.")
    sys.exit(1)


def _latest(base: Path, fname: str, runner: str) -> Path:
    if not base.exists():
        _abort(f"missing dir {base} (run {runner})")
    subs = sorted([d for d in base.iterdir() if d.is_dir()])
    if not subs:
        _abort(f"no timestamp dirs under {base}")
    p = subs[-1] / fname
    if not p.exists():
        _abort(f"{fname} missing in {subs[-1]}")
    return p


def _gv(s: pd.Series) -> pd.Series:
    """Canonical gvkey: 6-char zero-padded string (handles int / float / str
    sources uniformly — the _diag_s4 lesson)."""
    return (s.astype(str).str.split(".").str[0].str.zfill(6))


def _prev_q(cyq: int) -> int:
    y, q = divmod(cyq, 10)
    return y * 10 + (q - 1) if q > 1 else (y - 1) * 10 + 4


def _yoy_q(cyq: int) -> int:
    y, q = divmod(cyq, 10)
    return (y - 1) * 10 + q


def _next_q(cyq: int) -> int:
    y, q = divmod(cyq, 10)
    return y * 10 + (q + 1) if q < 4 else (y + 1) * 10 + 1


def _qbounds(cyq: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    y, q = divmod(cyq, 10)
    m0 = (q - 1) * 3 + 1
    start = pd.Timestamp(y, m0, 1)
    end = (start + pd.offsets.QuarterEnd(1))
    return start, end


def winsorize_1pct(df: pd.DataFrame, cols: list[str],
                   by: str | None = "cal_yr_qtr") -> dict:
    """Clip each column to [q01, q99], in place. Winsorize ONCE (Campello
    §2E). by='cal_yr_qtr' -> within calendar-quarter; by=None -> pooled.
    Paper underspecifies grouping -> both run as a sensitivity. Returns a
    summary for the metadata audit trail."""
    summary: dict = {"grouping": "pooled" if by is None else f"within {by}"}
    for c in cols:
        s = pd.to_numeric(df[c], errors="coerce")
        if by is None:
            lo, hi = s.quantile(0.01), s.quantile(0.99)
        else:
            grp = s.groupby(df[by])
            lo = grp.transform(lambda x: x.quantile(0.01))
            hi = grp.transform(lambda x: x.quantile(0.99))
        df[c] = s.clip(lower=lo, upper=hi)
        summary[c] = {"n_nonnull": int(s.notna().sum())}
    return summary


# ---------------------------------------------------------------- compustat
def load_compustat(panel_gv: set[str]) -> pd.DataFrame:
    cols = ["gvkey", "datadate", "cheq", "atq", "saleq", "dlttq", "dlcq",
            "oibdpq", "xintq", "txtq", "prccq", "cshoq"]
    df = pq.read_table(RAW, columns=cols).to_pandas()
    df["gvkey"] = _gv(df["gvkey"])
    df = df[df["gvkey"].isin(panel_gv)].copy()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    q = ((df["datadate"].dt.month - 1) // 3 + 1).astype(int)
    df["cyq"] = df["datadate"].dt.year * 10 + q
    df = df[(df["cyq"] >= COMP_Q_LO) & (df["cyq"] <= COMP_Q_HI)]
    for c in ("cheq", "atq", "saleq", "dlttq", "dlcq", "oibdpq",
              "xintq", "txtq", "prccq", "cshoq"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # per-row derived (paper-silent formulas, locked above)
    df["tobinq"] = ((df["prccq"] * df["cshoq"]
                     + df["dlttq"].fillna(0) + df["dlcq"].fillna(0))
                    / df["atq"].replace(0, np.nan))
    df["logassets"] = np.log(df["atq"].where(df["atq"] > 0))
    df = df.drop_duplicates(["gvkey", "cyq"], keep="last")
    # CASH_FLOW — Campello Table 1 VERBATIM: "operating income before
    # depreciation divided by LAGGED total assets" => oibdpq_t / atq_{t-1}.
    # Prior rebuild used (oibdpq - xintq - txtq)/atq_t (contemporaneous AT,
    # extra interest+tax subtraction) — a non-verbatim improvisation.
    # Corrected 2026-05-16 (systematic-debugging Phase 4, one variable).
    _lag = df[["gvkey", "cyq", "atq"]].rename(columns={"atq": "atq_lag1"})
    _lag["cyq"] = _lag["cyq"].map(_next_q)
    df = df.merge(_lag, on=["gvkey", "cyq"], how="left")
    df["cf"] = df["oibdpq"] / df["atq_lag1"].replace(0, np.nan)
    return df.set_index(["gvkey", "cyq"]).sort_index()


# --------------------------------------------------------------------- CCM
def load_ccm() -> pd.DataFrame:
    c = pq.read_table(CCM).to_pandas()
    c["gvkey"] = _gv(c["gvkey"])
    c = c[c["LINKPRIM"].isin(["P", "C"])
          & c["LINKTYPE"].isin(["LU", "LC"])].copy()
    c["LINKDT"] = pd.to_datetime(c["LINKDT"], errors="coerce")
    c["LINKENDDT"] = pd.to_datetime(c["LINKENDDT"], errors="coerce")
    c["LPERMNO"] = pd.to_numeric(c["LPERMNO"], errors="coerce")
    return c.dropna(subset=["LPERMNO"])


def crsp_qret(panel_gv: set[str], ccm: pd.DataFrame,
              window_q: list[int]) -> pd.DataFrame:
    """Compounded daily RET over each needed t-1 calendar quarter."""
    lagqs = sorted({_prev_q(t) for t in window_q})  # t-1 of every panel qtr
    files = []
    for cyq in lagqs:
        y, q = divmod(cyq, 10)
        f = DSF / f"CRSP_DSF_{y}_Q{q}.parquet"
        if not f.exists():
            _abort(f"CRSP DSF missing for lag quarter {cyq}: {f}")
        files.append((cyq, f))
    rows = []
    for cyq, f in files:
        d = pq.read_table(f, columns=["PERMNO", "date", "RET"]).to_pandas()
        d["date"] = pd.to_datetime(d["date"], errors="coerce")
        d["RET"] = pd.to_numeric(d["RET"], errors="coerce")
        s, e = _qbounds(cyq)
        d = d[(d["date"] >= s) & (d["date"] < e) & d["RET"].notna()]
        g = (d.groupby("PERMNO")["RET"]
             .apply(lambda r: np.prod(1.0 + r.values) - 1.0)
             .rename("stockret"))
        gg = g.reset_index()
        gg["cyq_lag"] = cyq
        rows.append(gg)
    ret = pd.concat(rows, ignore_index=True)
    # PERMNO -> gvkey via CCM, date-windowed on the lag-quarter end
    link = ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]].copy()
    out = []
    for cyq in lagqs:
        _, qe = _qbounds(cyq)
        qend = qe - pd.Timedelta(days=1)
        lk = link[(link["LINKDT"].isna() | (link["LINKDT"] <= qend))
                  & (link["LINKENDDT"].isna()
                     | (link["LINKENDDT"] >= qend))]
        m = (ret[ret["cyq_lag"] == cyq]
             .merge(lk, left_on="PERMNO", right_on="LPERMNO", how="inner"))
        out.append(m[["gvkey", "cyq_lag", "stockret"]])
    res = pd.concat(out, ignore_index=True)
    res = res[res["gvkey"].isin(panel_gv)]
    return res.drop_duplicates(["gvkey", "cyq_lag"], keep="last")


# -------------------------------------------------------------------- IBES
def load_ibes_consensus(panel_gv: set[str], ccm: pd.DataFrame,
                        window_q: list[int]) -> pd.DataFrame:
    """FPI=6 ('1-quarter-ahead') consensus = mean(VALUE) per firm with
    review date <= end of each needed t-1 quarter (latest vintage)."""
    lagqs = sorted({_prev_q(t) for t in window_q})
    lag_years = {divmod(c, 10)[0] for c in lagqs}
    # load each lag-quarter year plus the year before the earliest (catches
    # vintages reviewed in the prior year still valid at quarter-end) —
    # the full-panel generalization of the original 2014-2016 span.
    years = range(min(lag_years) - 1, max(lag_years) + 1)
    frames = []
    for y in years:
        f = IBES / f"tr_ibes_{y}.parquet"
        if f.exists():
            frames.append(pq.read_table(
                f, columns=["CUSIP", "FPI", "VALUE", "REVDATS",
                            "ANNDATS"]).to_pandas())
    if not frames:
        _abort(f"no IBES year files for {min(years)}-{max(years)}")
    ib = pd.concat(frames, ignore_index=True)
    ib = ib[ib["FPI"].astype(str) == "6"].copy()
    ib["VALUE"] = pd.to_numeric(ib["VALUE"], errors="coerce")
    rev = pd.to_datetime(ib["REVDATS"], errors="coerce")
    ann = pd.to_datetime(ib["ANNDATS"], errors="coerce")
    ib["asof"] = rev.fillna(ann)
    ib["cusip8"] = ib["CUSIP"].astype(str).str[:8]
    ib = ib.dropna(subset=["VALUE", "asof"])
    # IBES cusip8 -> gvkey via CCM cusip
    link = ccm[["gvkey", "cusip"]].dropna().copy()
    link["cusip8"] = link["cusip"].astype(str).str[:8]
    link = link.drop_duplicates("cusip8")
    ib = ib.merge(link[["cusip8", "gvkey"]], on="cusip8", how="inner")
    ib = ib[ib["gvkey"].isin(panel_gv)]
    out = []
    for cyq in lagqs:
        _, qe = _qbounds(cyq)
        qend = qe - pd.Timedelta(days=1)
        sub = ib[ib["asof"] <= qend]
        g = (sub.groupby("gvkey")["VALUE"].mean()
             .rename("eps_fpi6").reset_index())
        g["cyq_lag"] = cyq
        out.append(g)
    return pd.concat(out, ignore_index=True)


# ------------------------------------------------------------------- macro
def _macro_quarterly() -> pd.DataFrame:
    def daily(path, dcol, vcol, dfmt=None, **kw):
        d = pd.read_csv(path, **kw)
        d[dcol] = pd.to_datetime(d[dcol], format=dfmt, errors="coerce")
        d = d.dropna(subset=[dcol])
        d["cyq"] = d[dcol].dt.year * 10 + (d[dcol].dt.month - 1) // 3 + 1
        return d.groupby("cyq")[vcol].mean()

    fx = daily(BX / "BoE" / "USD_GBP_daily_2008-2018.csv",
               "DATE", "XUDLUSS", "%d %b %Y").rename("fx")
    vix = daily(BX / "CBOE" / "VIX_daily_1990-present.csv",
                "DATE", "CLOSE", "%m/%d/%Y").rename("vix")
    ads_raw = pd.read_excel(BX / "PhillyFed" / "ADS_Index_current.xlsx")
    ads_raw["Date"] = pd.to_datetime(ads_raw["Date"], format="%Y:%m:%d",
                                     errors="coerce")
    ads_raw = ads_raw.dropna(subset=["Date"])
    ads_raw["cyq"] = (ads_raw["Date"].dt.year * 10
                      + (ads_raw["Date"].dt.month - 1) // 3 + 1)
    ads = ads_raw.groupby("cyq")["ADS_Index"].mean().rename("ads")

    um = pd.read_csv(BX / "UMich" / "UMCSENT.csv")
    um["observation_date"] = pd.to_datetime(um["observation_date"],
                                            errors="coerce")
    um = um.dropna(subset=["observation_date"])
    um["cyq"] = (um["observation_date"].dt.year * 10
                 + (um["observation_date"].dt.month - 1) // 3 + 1)
    umc = um.groupby("cyq")["UMCSENT"].mean().rename("umcsent")

    lv = pd.read_excel(BX / "PhillyFed" / "Livingston_means.xlsx")
    lv["Date"] = pd.to_datetime(lv["Date"], errors="coerce")
    lv = lv.dropna(subset=["Date"]).sort_values("Date")
    lv = lv.set_index("Date")["RGDPX_1Y"].resample("MS").ffill()
    lvq = (lv.reset_index()
           .assign(cyq=lambda x: x["Date"].dt.year * 10
                   + (x["Date"].dt.month - 1) // 3 + 1)
           .groupby("cyq")["RGDPX_1Y"].mean().rename("livingston"))

    m = pd.concat([fx, vix, ads, umc, lvq], axis=1)
    m.index.name = "cyq"
    return m


# --------------------------------------------------------------------- FIC
def load_fic100(panel_gv: set[str]) -> pd.DataFrame:
    if not FICZIP.exists():
        _abort(f"FIC zip missing: {FICZIP}")
    with zipfile.ZipFile(FICZIP) as zf:
        with zf.open("fic_data.txt") as fh:
            f = pd.read_csv(io.TextIOWrapper(fh, "latin-1"), sep="\t",
                            usecols=["gvkey", "year", "icode100"])
    f["gvkey"] = _gv(f["gvkey"])
    f = f[f["gvkey"].isin(panel_gv)]
    return f.rename(columns={"icode100": "fic100"})


# ------------------------------------------------------------------- build
def main() -> None:
    print("Campello replication — STEP 6  controls + cash DV\n")
    s4 = _latest(S4B, "panel.parquet", "step4_timeline.py")
    panel = pq.read_table(s4).to_pandas()
    panel["gvkey"] = _gv(panel["gvkey"])
    panel["cal_yr_qtr"] = panel["cal_yr_qtr"].astype(int)
    panel["datadate"] = pd.to_datetime(panel["datadate"], errors="coerce")
    pgv = set(panel["gvkey"])
    window_q = sorted(int(q) for q in panel["cal_yr_qtr"].unique())
    wf = {"panel_rows": len(panel), "panel_firms": len(pgv),
          "panel_quarters": len(window_q),
          "panel_span": [window_q[0], window_q[-1]]}
    print(f"Step-4 panel: {len(panel):,} rows / {len(pgv):,} firms / "
          f"{len(window_q)} qtrs [{window_q[0]}..{window_q[-1]}]")

    comp = load_compustat(pgv)
    ccm = load_ccm()
    qret = crsp_qret(pgv, ccm, window_q)
    eps = load_ibes_consensus(pgv, ccm, window_q)
    macro = _macro_quarterly()
    fic = load_fic100(pgv)
    print("  loaded: compustat, ccm, crsp-qret, ibes, macro, fic100")

    def cget(g, cyq, col):
        try:
            return comp.loc[(g, cyq), col]
        except KeyError:
            return np.nan

    rec = []
    for r in panel.itertuples(index=False):
        g, t = r.gvkey, int(r.cal_yr_qtr)
        t1 = _prev_q(t)
        yoy1 = _yoy_q(t1)
        cheq_t = cget(g, t, "cheq")
        atq_l = cget(g, t1, "atq")
        cheq_l = cget(g, t1, "cheq")
        denom = (atq_l - cheq_l) if (pd.notna(atq_l)
                                     and pd.notna(cheq_l)) else np.nan
        cash_dv = (cheq_t / denom
                   if (pd.notna(cheq_t) and pd.notna(denom) and denom != 0)
                   else np.nan)
        sg_num, sg_den = cget(g, t1, "saleq"), cget(g, yoy1, "saleq")
        salesgrowth = ((sg_num / sg_den - 1.0)
                       if (pd.notna(sg_num) and pd.notna(sg_den)
                           and sg_den not in (0,)) else np.nan)
        mr = macro.loc[t1] if t1 in macro.index else pd.Series(dtype=float)
        rec.append({
            "gvkey": g, "cal_yr_qtr": t,
            "HIGH_BETA_UK": r.HIGH_BETA_UK, "POST": r.POST,
            "datadate": r.datadate,
            "CASH_DV": cash_dv,
            "tobinq_lag": cget(g, t1, "tobinq"),
            "cf_lag": cget(g, t1, "cf"),
            "logassets_lag": cget(g, t1, "logassets"),
            "salesgrowth_lag": salesgrowth,
            "_t1": t1,
        })
    df = pd.DataFrame(rec)

    df = df.merge(qret.rename(columns={"cyq_lag": "_t1",
                                       "stockret": "stockret_lag"}),
                  on=["gvkey", "_t1"], how="left")
    df = df.merge(eps.rename(columns={"cyq_lag": "_t1",
                                      "eps_fpi6": "eps_fpi6_lag"}),
                  on=["gvkey", "_t1"], how="left")
    mlong = macro.reset_index().rename(columns={"cyq": "_t1"})
    df = df.merge(mlong.rename(columns={
        "fx": "fx_lag", "vix": "vix_lag", "ads": "ads_lag",
        "umcsent": "umcsent_lag", "livingston": "livingston_lag"}),
        on="_t1", how="left")
    df["_yr"] = df["datadate"].dt.year
    df = df.merge(fic.rename(columns={"year": "_yr"}),
                  on=["gvkey", "_yr"], how="left")

    # Campello Table 1 note VERBATIM (paper L2527-2528): "All variables are
    # winsorized at the 1% level." Restored here — the prior rebuild's
    # omission (false premise "paper Table 8 does not winsorize") left
    # CASH_DV max~151.6 (17x p99) inflating the double-clustered SE ~3.7x.
    # Grouping paper-underspecified: this run = within cal_yr_qtr; pooled
    # variant = documented sensitivity (prior timestamp).
    WINSOR_BY = "cal_yr_qtr"
    winsor_summary = winsorize_1pct(
        df, [c for c in WINSOR_VARS if c in df.columns], by=WINSOR_BY)
    print(f"  winsorized 1/99 (within {WINSOR_BY}, once): "
          + ", ".join(c for c in WINSOR_VARS if c in df.columns))

    ctrl_cols = ["tobinq_lag", "cf_lag", "logassets_lag", "salesgrowth_lag",
                 "stockret_lag", "eps_fpi6_lag", "fx_lag", "vix_lag",
                 "umcsent_lag", "livingston_lag", "ads_lag"]
    miss = {c: int(df[c].isna().sum()) for c in ctrl_cols
            + ["CASH_DV", "fic100"]}

    wf["after_cash_DV_notna"] = int(df["CASH_DV"].notna().sum())
    core = ctrl_cols + ["CASH_DV", "fic100"]
    wf["complete_case_all_controls"] = int(df.dropna(subset=core).shape[0])
    wf["complete_case_ex_eps"] = int(
        df.dropna(subset=[c for c in core if c != "eps_fpi6_lag"]).shape[0])
    wf["complete_case_ex_eps_ex_ads"] = int(
        df.dropna(subset=[c for c in core
                          if c not in ("eps_fpi6_lag", "ads_lag")]).shape[0])

    out = df.drop(columns=["_t1", "_yr"]).sort_values(
        ["gvkey", "cal_yr_qtr"]).reset_index(drop=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_dir / "controls.parquet", index=False)

    metadata = {
        "step": "6 — controls + cash DV (Campello 2022 JFQA §IV.C.3 + Tbl 8)",
        "step4_input": str(s4),
        "cash_DV": "CASH_t = cheq_t / (atq_{t-1} - cheq_{t-1})  "
                   "[verbatim: total cash / lagged total assets net of cash]",
        "operationalization_locked": {
            "tobinq": "(prccq*cshoq + dlttq + dlcq)/atq  @ t-1",
            "cash_flow": "oibdpq / atq_{t-1}  (Campello Table 1 verbatim: "
                         "operating income before depreciation / lagged "
                         "total assets; fixed 2026-05-16 from non-verbatim "
                         "(oibdpq-xintq-txtq)/atq_t improvisation)",
            "log_assets": "ln(atq) @ t-1",
            "sales_growth": "saleq_{t-1}/saleq_{t-1 - 1yr} - 1  (YoY)",
            "stock_return": "prod(1+RET)-1 over calendar qtr t-1 (CRSP DSF)",
            "eps": "IBES FPI=6 mean(VALUE), review date <= end of qtr t-1; "
                   "IBES->gvkey via CUSIP8<->CCM.cusip",
            "macro_aggregation": "mean over calendar quarter t-1",
            "livingston": "RGDPX_1Y, semi-annual -> monthly ffill -> qtr mean",
        },
        "DEVIATION_phillyfed_lei": "Paper §IV.C.3 cites a national PhillyFed "
            "'Leading Economic Indicator'. NO such national series exists "
            "(only state-level State_Leading_Revised.xls). SUBSTITUTED with "
            "PhillyFed ADS_Index (ads_lag). Explicit recipe deviation; "
            "Step 7 runs a drop-ads sensitivity.",
        "fic100": "icode100 from fic_data.txt, join (gvkey, year(datadate_t))",
        "winsorization": {
            "rule": "Campello 2022 Table 1 note VERBATIM (campello_v2/"
                    "campello_paper_FULL.md L2527-2528): 'All variables are "
                    "winsorized at the 1% level.' Applied 1/99 ONCE "
                    "(Campello §2E) to the eq-14 DV + firm controls. "
                    "CORRECTION 2026-05-16: prior rebuild OMITTED "
                    "winsorization on the false premise 'paper Table 8 does "
                    "not winsorize' (step7) — that omission left "
                    "high-leverage DV outliers (CASH_DV max~151.6 = 17x "
                    "p99) inflating the double-clustered SE ~3.7x "
                    "(systematic-debugging, A6/A7).",
            "vars": WINSOR_VARS,
            "grouping_note": "Paper underspecifies grouping ('at the 1% "
                    "level', no qualifier). BOTH run as a sensitivity: this "
                    "output = within cal_yr_qtr; pooled = prior timestamp. "
                    "Reported side-by-side; favorable one NOT silently "
                    "chosen.",
            "winsor_summary": winsor_summary,
        },
        "coverage_waterfall": wf,
        "missingness_by_col": miss,
        "control_cols": ctrl_cols,
        "out_of_scope": "regression = Step 7 (NOT built here).",
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2,
                                                      default=str))

    print("\nCOVERAGE WATERFALL")
    for k, v in wf.items():
        if isinstance(v, int):
            print(f"  {k:<32s} {v:>8,d}")
        else:
            print(f"  {k:<32s} {v}")
    print("\nMISSINGNESS (of "
          f"{len(df):,} window rows)")
    for c, n in miss.items():
        print(f"  {c:<20s} missing {n:>6,d}  "
              f"({n / max(len(df),1) * 100:5.1f}%)")
    print(f"\n  -> {out_dir / 'controls.parquet'}")
    print(f"  -> {out_dir / 'metadata.json'}")
    print("\n  STOP — advisor gate: report this waterfall BEFORE Step 7. "
          "Regression NOT built here.")
    if wf["complete_case_ex_eps"] < len(df) * 0.30:
        print(f"\n  WARNING: complete-case (ex-EPS) "
              f"{wf['complete_case_ex_eps']:,} < 30% of {len(df):,} window "
              f"rows -- possible JOIN/coverage BUG on the full-panel span, "
              f"not just attrition. Investigate before Step 7.")


if __name__ == "__main__":
    main()
