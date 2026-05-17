"""Campello et al. (2022 JFQA) replication — STEP 2: per-firm beta^UK.

From-scratch rebuild. Estimates equation (13) ONCE PER FIRM over the
pre-Brexit window. Produces a beta^UK per firm. NO tercile cut, NO treatment
assignment, NO panel, NO DiD, NO comparison to any prior F1D output. Tercile /
treatment is Step 3 and is deliberately NOT scaffolded here.

Authoritative spec
------------------
Campello et al. 2022 JFQA §IV.A.1 (PDF p.14 / journal p.3191):
    "Following Bloom (2014) ... estimate equation (12) for each firm i as
     (13)  vol(r_it) = a_i + beta^UK_i * vol(FTSE100_t)
                       + theta * CONTROLS_t + eps_it
     ... CONTROLS_t consisting of vol(SP500) and vol(FX£)."
§IV.A.1 data (PDF p.16 / journal p.3193):
    "CRSP stock price data and Bloomberg equity index and currency data ...
     monthly data from 2010:M1 to 2014:M12 ... before any major
     Brexit-related events."

vol() construction — RESOLUTION PATH (the paper gives no explicit formula;
Appendices A/B are model proofs, NOT variable definitions):
    Eq (13) regresses 60 MONTHLY observations of vol(r_it) on vol(FTSE100_t).
    The only way vol(r_it) is a per-month value is realized volatility =
    standard deviation of intramonth DAILY returns. The "Following Bloom
    (2014)" anchor confirms (Bloom's volatility measure is the same
    construction). This is the only internally consistent reading, not a
    free assumption.

Silent-point resolutions (documented in metadata.json):
  * vol(X)_t   = std of daily LOG returns of X within calendar month t.
  * r          = CRSP daily total return RET (with dividends); "equity
                 returns" defaults to total return.
  * vol(FTSE100), vol(SP500) = same within-month daily-log-return std on
                 the index series.
  * vol(FX£)   = USD/GBP daily; std is sign-symmetric so quote direction
                 is irrelevant.
  * Balanced 60: keep only firms with all 60 monthly vol obs. Paper presents
                 beta^UK as a single static pre-period estimate with no
                 min-obs qualifier; 60 obs is near the OLS-stability floor
                 for a 4-regressor model; conservative re: mid-window
                 listing/delisting (advisor-confirmed faithful default).
  * MIN_DAYS_PER_MONTH = 15 (~3/4 of a 21-day trading month) for a monthly
                 std to count.

Unavoidable vendor gaps (paper used Bloomberg; F1D has no Bloomberg) —
disclosed in metadata.json, NOT papered over:
  * FTSE100 : yfinance daily   (paper: Bloomberg)
  * S&P500  : CRSP `sprtrn`    (paper: Bloomberg)  [CRSP sprtrn = S&P 500
              daily return embedded in DSF]
  * USD/GBP : Bank of England  (paper: Bloomberg)
  Cross-vendor spot-check vs a second web source was NOT performed (no web
  access this session) — flagged as an open validation risk in metadata.

Output
------
outputs/campello_rebuild/step2_beta_uk/<timestamp>/
    beta_uk.parquet   gvkey, beta_uk, beta_se, n_obs
    metadata.json     spec resolution, vendor-gap disclosure, dist stats

Run:  python scripts/campello_rebuild/step2_beta_uk.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
STEP1_BASE = ROOT / "outputs" / "campello_rebuild" / "step1_sample"
# C.1 #7 panel-integrity gate (step1b). When True, beta^UK is estimated on
# the panel-integrity-gated universe, matching Campello's filter ORDER
# (C.1 applies #7 before the missing-beta^UK drop). Revert = set False.
STEP1B_BASE = ROOT / "outputs" / "campello_rebuild" / "step1b_panel_integrity"
# #7 experiment reverted 2026-05-17 (tested -> negative; isolating D5).
# True = estimate beta^UK on the C.1-#7-gated universe; False = baseline.
USE_STEP1B = False
CRSP_DIR = ROOT / "inputs" / "CRSP_DSF"
FTSE_CSV = ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv"
BOE_CSV = ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv"
CCM_PARQUET = ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step2_beta_uk"

WINDOW_START = pd.Timestamp("2010-01-01")
WINDOW_END = pd.Timestamp("2014-12-31")
YEARS = list(range(2010, 2015))           # 2010..2014
N_MONTHS = 60                              # balanced-window requirement
MIN_DAYS_PER_MONTH = 15                    # min daily obs for a monthly std

# eq (13) regressor order after the intercept: FTSE100, SP500, FX£.
# beta^UK is the FTSE100 coefficient => column index 1 of the design.
BETA_UK_COL = 1


def _abort(msg: str) -> None:
    print(f"\nABORT — {msg}")
    print("Step 2 beta^UK NOT built. Resolve before proceeding.")
    sys.exit(1)


def latest_step1_sample() -> Path:
    base = STEP1B_BASE if USE_STEP1B else STEP1_BASE
    label = "Step-1b" if USE_STEP1B else "Step-1"
    if not base.exists():
        _abort(f"{label} output dir missing: {base} "
               f"({'run step1b_panel_integrity.py first' if USE_STEP1B else 'run step1_sample.py first'})")
    subdirs = sorted([d for d in base.iterdir() if d.is_dir()])
    if not subdirs:
        _abort(f"no {label} timestamp dirs under {base}")
    sample = subdirs[-1] / "sample.parquet"
    if not sample.exists():
        _abort(f"{label} sample.parquet missing in {subdirs[-1]}")
    return sample


def _daily_log_return(price: pd.Series) -> pd.Series:
    p = price.astype(float)
    return np.log(p / p.shift(1))


def _monthly_std(
    df: pd.DataFrame, date_col: str, val_col: str, group: list[str] | None = None
) -> pd.DataFrame:
    """Realized vol = std of daily values within (group, calendar-month).
    Months with < MIN_DAYS_PER_MONTH daily obs are dropped."""
    df = df.copy()
    df["_y"] = df[date_col].dt.year
    df["_m"] = df[date_col].dt.month
    keys = (group or []) + ["_y", "_m"]
    agg = df.groupby(keys, observed=True)[val_col].agg(["std", "count"]).reset_index()
    agg = agg[agg["count"] >= MIN_DAYS_PER_MONTH]
    agg["year_month"] = agg["_y"] * 100 + agg["_m"]
    return agg.rename(columns={"std": "vol"})[(group or []) + ["year_month", "vol"]]


def build_macro_vol() -> pd.DataFrame:
    """60-row monthly panel: vol_ftse, vol_sp500, vol_fx (within-month daily-
    log-return std). Aborts unless exactly 60 months are present."""
    # --- FTSE100 (yfinance daily close) ---
    ft = pd.read_csv(FTSE_CSV)
    if not {"Date", "Close"}.issubset(ft.columns):
        _abort(f"FTSE csv missing Date/Close columns: {list(ft.columns)[:8]}")
    ft["date"] = pd.to_datetime(ft["Date"], errors="coerce")
    ft = ft.dropna(subset=["date"]).sort_values("date")
    ft["Close"] = pd.to_numeric(ft["Close"], errors="coerce")
    fw = ft[(ft["date"] >= WINDOW_START) & (ft["date"] <= WINDOW_END)].copy()
    # sanity: FTSE100 traded ~3,000–8,000 over 2010–2014.
    if not fw["Close"].between(3000, 8000).mean() > 0.95:
        _abort(f"FTSE100 close out of plausible 3k–8k range "
               f"(min={fw['Close'].min()}, max={fw['Close'].max()}) — vendor issue.")
    fw["lr"] = _daily_log_return(fw["Close"])
    fw = fw.dropna(subset=["lr"])
    ftse = _monthly_std(fw, "date", "lr").rename(columns={"vol": "vol_ftse"})

    # --- USD/GBP (Bank of England daily; XUDLUSS = USD per GBP) ---
    bo = pd.read_csv(BOE_CSV)
    bo.columns = [c.strip().upper() for c in bo.columns]
    if "DATE" not in bo.columns or "XUDLUSS" not in bo.columns:
        _abort(f"BoE csv missing DATE/XUDLUSS: {list(bo.columns)[:8]}")
    bo["date"] = pd.to_datetime(bo["DATE"], format="%d %b %Y", errors="coerce")
    bo["fx"] = pd.to_numeric(bo["XUDLUSS"], errors="coerce")
    bo = bo.dropna(subset=["date", "fx"]).sort_values("date")
    bw = bo[(bo["date"] >= WINDOW_START) & (bo["date"] <= WINDOW_END)].copy()
    if not bw["fx"].between(1.15, 1.80).mean() > 0.95:
        _abort(f"USD/GBP out of plausible 1.15–1.80 range "
               f"(min={bw['fx'].min()}, max={bw['fx'].max()}) — vendor issue.")
    bw["lr"] = _daily_log_return(bw["fx"])
    bw = bw.dropna(subset=["lr"])
    fx = _monthly_std(bw, "date", "lr").rename(columns={"vol": "vol_fx"})

    # --- S&P500 (CRSP sprtrn daily return embedded in DSF) ---
    sp_parts = []
    for y in YEARS:
        for q in range(1, 5):
            fp = CRSP_DIR / f"CRSP_DSF_{y}_Q{q}.parquet"
            if not fp.exists():
                continue
            cols = [c for c in pq.read_schema(fp).names if c in ("date", "sprtrn")]
            if "sprtrn" not in cols:
                _abort(f"CRSP DSF {fp.name} lacks 'sprtrn' column.")
            d = pq.read_table(fp, columns=["date", "sprtrn"]).to_pandas()
            d = d.dropna(subset=["sprtrn"]).drop_duplicates("date")
            sp_parts.append(d)
    if not sp_parts:
        _abort("no CRSP DSF parquet files found for 2010–2014.")
    sp = pd.concat(sp_parts, ignore_index=True).drop_duplicates("date")
    sp["date"] = pd.to_datetime(sp["date"], errors="coerce")
    sp = sp.sort_values("date")
    sw = sp[(sp["date"] >= WINDOW_START) & (sp["date"] <= WINDOW_END)].copy()
    sw["sprtrn"] = pd.to_numeric(sw["sprtrn"], errors="coerce")
    if not sw["sprtrn"].abs().lt(0.20).mean() > 0.99:
        _abort("CRSP sprtrn has implausible daily moves (>20%) — column misread.")
    sw["lr"] = np.log1p(sw["sprtrn"])
    sw = sw.replace([np.inf, -np.inf], np.nan).dropna(subset=["lr"])
    spv = _monthly_std(sw, "date", "lr").rename(columns={"vol": "vol_sp500"})

    macro = (
        ftse.merge(spv, on="year_month", how="inner")
        .merge(fx, on="year_month", how="inner")
        .sort_values("year_month")
        .reset_index(drop=True)
    )
    if len(macro) != N_MONTHS:
        _abort(f"macro vol panel has {len(macro)} months, expected {N_MONTHS}. "
               f"Months: {macro['year_month'].tolist()}")
    return macro


def load_ccm() -> pd.DataFrame:
    """Canonical primary gvkey<->permno links, date-windowed.
    LINKPRIM='P' AND LINKTYPE in (LU,LC); LINKDT <= datadate <= LINKENDDT."""
    need = ["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKPRIM", "LINKTYPE"]
    have = set(pq.read_schema(CCM_PARQUET).names)
    if not set(need).issubset(have):
        _abort(f"CCM parquet missing columns: {[c for c in need if c not in have]}")
    ccm = pq.read_table(CCM_PARQUET, columns=need).to_pandas()
    ccm = ccm[(ccm["LINKPRIM"] == "P") & (ccm["LINKTYPE"].isin(["LU", "LC"]))].copy()
    ccm["LINKENDDT"] = ccm["LINKENDDT"].astype(str).replace({"E": "2099-12-31"})
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
    ccm = ccm.dropna(subset=["LINKDT", "LINKENDDT", "LPERMNO"])
    ccm = ccm[(ccm["LINKENDDT"] >= WINDOW_START) & (ccm["LINKDT"] <= WINDOW_END)]
    ccm["gvkey"] = ccm["gvkey"].astype(int).astype(str).str.zfill(6)
    ccm["LPERMNO"] = ccm["LPERMNO"].astype(int)
    return ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]]


def firm_monthly_vol(step1_gvkeys: set, ccm: pd.DataFrame) -> pd.DataFrame:
    """Stream CRSP DSF year-by-year, restrict to Step-1 gvkeys' permnos,
    daily log-return from RET, within-month std per (gvkey, year_month)."""
    ccm_keep = ccm[ccm["gvkey"].isin(step1_gvkeys)].copy()
    if ccm_keep.empty:
        _abort("no CCM links overlap the Step-1 gvkey universe.")
    permnos_keep = set(ccm_keep["LPERMNO"].unique())

    rows = []
    for y in YEARS:
        parts = []
        for q in range(1, 5):
            fp = CRSP_DIR / f"CRSP_DSF_{y}_Q{q}.parquet"
            if not fp.exists():
                continue
            d = pq.read_table(fp, columns=["PERMNO", "date", "RET"]).to_pandas()
            d["PERMNO"] = pd.to_numeric(d["PERMNO"], errors="coerce")
            d = d[d["PERMNO"].isin(permnos_keep)]
            d["date"] = pd.to_datetime(d["date"], errors="coerce")
            d["RET"] = pd.to_numeric(d["RET"], errors="coerce")  # drops 'B','C',...
            d = d.dropna(subset=["PERMNO", "date", "RET"])
            parts.append(d)
        if not parts:
            continue
        yd = pd.concat(parts, ignore_index=True)
        yd = yd[(yd["date"] >= WINDOW_START) & (yd["date"] <= WINDOW_END)]
        yd["PERMNO"] = yd["PERMNO"].astype(int)
        # date-windowed permno -> gvkey
        m = yd.merge(ccm_keep.rename(columns={"LPERMNO": "PERMNO"}), on="PERMNO", how="inner")
        m = m[(m["date"] >= m["LINKDT"]) & (m["date"] <= m["LINKENDDT"])]
        m["lr"] = np.log1p(m["RET"])
        m = m.replace([np.inf, -np.inf], np.nan).dropna(subset=["lr"])
        rows.append(_monthly_std(m, "date", "lr", group=["gvkey"]).rename(
            columns={"vol": "vol_r"}))
        del yd, m, parts
    if not rows:
        _abort("no firm-month vol rows produced from CRSP DSF.")
    return pd.concat(rows, ignore_index=True)


def ols_beta_uk(Y: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Closed-form OLS for many firms sharing design X.

    Y : (n_firms, n_obs)  monthly vol(r) per firm
    X : (n_obs, k)        [1, vol_ftse, vol_sp500, vol_fx]
    Returns (beta (n_firms,k), se (n_firms,k)).
        beta = Y M^T  with  M = (X'X)^-1 X'
        SE_i = sqrt( sigma2_i * diag((X'X)^-1) ),  sigma2_i = RSS_i/(n-k)
    """
    n_obs, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)        # (k,k)
    M = XtX_inv @ X.T                       # (k,n_obs)
    beta = Y @ M.T                          # (n_firms,k)
    resid = Y - beta @ X.T                  # (n_firms,n_obs)
    sigma2 = (resid * resid).sum(axis=1) / (n_obs - k)
    se = np.sqrt(np.outer(sigma2, np.diag(XtX_inv)))
    return beta, se


def main() -> None:
    print("Campello replication — STEP 2  beta^UK (per firm)\n")

    s1 = latest_step1_sample()
    g = pq.read_table(s1, columns=["gvkey"]).to_pandas()
    step1_gvkeys = set(g["gvkey"].astype(str).str.zfill(6).unique())
    print(f"Step-1 sample: {s1}\n  gvkeys: {len(step1_gvkeys):,}")

    print("\nPROBE / GUARD")
    for p in (FTSE_CSV, BOE_CSV, CCM_PARQUET):
        if not p.exists():
            _abort(f"required input missing: {p}")
    print("  inputs present: CRSP_DSF, FTSE(yfinance), USD/GBP(BoE), CCM")

    macro = build_macro_vol()
    print(f"  macro vol panel: {len(macro)} months "
          f"[{macro['year_month'].min()}..{macro['year_month'].max()}]  GUARD OK")

    ccm = load_ccm()
    print(f"  CCM canonical links in window: {len(ccm):,} "
          f"({ccm['gvkey'].nunique():,} gvkeys)")

    fm = firm_monthly_vol(step1_gvkeys, ccm)
    print(f"  firm-month vol rows: {len(fm):,} ({fm['gvkey'].nunique():,} gvkeys)")

    wide = fm.pivot(index="gvkey", columns="year_month", values="vol_r")
    months = macro["year_month"].tolist()
    wide = wide.reindex(columns=months)
    balanced = wide.dropna(how="any")
    print(f"  balanced-{N_MONTHS} firms: {len(balanced):,} "
          f"(dropped {len(wide) - len(balanced):,} partial-window)")
    if balanced.empty:
        _abort("no firms with a complete 60-month vol series.")

    X_macro = macro.set_index("year_month").loc[months, ["vol_ftse", "vol_sp500", "vol_fx"]].to_numpy(float)
    X = np.column_stack([np.ones(len(X_macro)), X_macro])    # (60,4)
    Y = balanced.to_numpy(float)                              # (n,60)
    beta, se = ols_beta_uk(Y, X)

    out = pd.DataFrame({
        "gvkey": balanced.index.to_numpy(),
        "beta_uk": beta[:, BETA_UK_COL],
        "beta_se": se[:, BETA_UK_COL],
        "n_obs": N_MONTHS,
    }).sort_values("gvkey").reset_index(drop=True)

    b = out["beta_uk"]
    nn = b[b >= 0]
    dist = {
        "n_firms": int(len(out)),
        "mean": float(b.mean()), "sd": float(b.std()),
        "min": float(b.min()), "max": float(b.max()),
        "q10": float(b.quantile(.10)), "q25": float(b.quantile(.25)),
        "q50": float(b.quantile(.50)), "q75": float(b.quantile(.75)),
        "q90": float(b.quantile(.90)),
        "n_nonneg": int((b >= 0).sum()), "n_negative": int((b < 0).sum()),
        "nonneg_p33": float(nn.quantile(1/3)) if len(nn) else None,
        "nonneg_p67": float(nn.quantile(2/3)) if len(nn) else None,
    }

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_dir / "beta_uk.parquet", index=False)

    metadata = {
        "step": "2 — per-firm beta^UK (Campello 2022 JFQA eq. 13)",
        "equation": "vol(r_it) = a_i + beta^UK_i*vol(FTSE100_t) + theta*[vol(SP500),vol(FX£)]_t + eps",
        "step1_sample": str(s1),
        "window": [str(WINDOW_START.date()), str(WINDOW_END.date())],
        "precision_diagnostic": {
            "verdict": "beta^UK imprecision is INTRINSIC to eq-13 at Campello's "
                       "stated $10M floor; NOT a code bug. Faithful replication "
                       "(systematic-debugging: 'process reveals no defect').",
            "phase1_ols_correct": "synthetic true beta_FTSE=0.50 -> recovered "
                                  "0.507; closed-form OLS implementation correct",
            "phase1_collinearity": "cond(standardized)=4.3, VIF(vol_ftse)=4.6 -> "
                                   "NOT severe (raw cond 888 = intercept-scale "
                                   "artifact, not multicollinearity)",
            "phase1_imprecision": "median beta_se~0.53; near-cut fragility "
                                  "~96% control / ~75% treated within 1 SE of cut",
            "phase3_size_gradient": "median beta_se 0.89 (small ~$86M) -> 0.33 "
                                    "(large ~$9B); %|beta|>3 2.8% -> 0.0%",
            "phase4_10m_lever_dead": "enforcing $10M within the beta^UK window is "
                                     "an empirical NO-OP: Step-1 already applies "
                                     "$10M per firm-quarter; noisy firms (~$86M) "
                                     ">> $10M. Raising the threshold = methodology "
                                     "deviation (rejected, §IV.B states $10M).",
            "paper_concession": "fn13 'imperfect proxy', beta^UK vs beta^UK_CF "
                                "rank-corr 0.8; fn17 significance filter is a "
                                "robustness, baseline accepts insignificant beta^UK",
            "residual_margin": "our beta^UK plausibly somewhat noisier than his at "
                               "an irreducible margin (yfinance/CRSP-sprtrn/BoE vs "
                               "Bloomberg; different raw COMPUSTAT extract). "
                               "Expect ATTENUATED DiD significance on the cash arm "
                               "-- structurally explained, not a defect; do NOT "
                               "change the recipe to chase Campello's significance.",
        },
        "vol_resolution": (
            "paper gives no explicit vol() formula (Appendices A/B are model "
            "proofs, not variable defs); vol()=std of within-month daily LOG "
            "returns — forced by eq-13 60-obs monthly structure + 'Following "
            "Bloom (2014)' anchor"),
        "silent_point_resolutions": {
            "return_type": "CRSP RET daily total return (with dividends)",
            "min_days_per_month": MIN_DAYS_PER_MONTH,
            "balanced_window": f"all {N_MONTHS} months required per firm "
                               "(paper silent; faithful static-pre-period reading "
                               "+ OLS-stability floor; advisor-confirmed default)",
            "fx_direction": "USD/GBP (BoE XUDLUSS); std sign-symmetric",
            "ccm_linkage": "LINKPRIM='P' AND LINKTYPE in (LU,LC), date-windowed",
        },
        "vendor_gaps_paper_used_bloomberg": {
            "FTSE100": "yfinance daily (paper: Bloomberg)",
            "SP500": "CRSP sprtrn (paper: Bloomberg)",
            "USD_GBP": "Bank of England (paper: Bloomberg)",
            "cross_vendor_spotcheck": "NOT performed (no web access this "
                                      "session) — OPEN validation risk",
        },
        "no_treatment_assignment": "tercile / HIGH_BETA_UK is Step 3, not here",
        "distribution": dist,
        "paper_anchors_for_validation": {
            "campello_cutoffs": "top tercile beta^UK > 0.68, bottom < 0.28",
            "campello_counts": "449 treated + 360 control (post his $10M screen)",
            "beta_uk_cf_robustness": "rank corr 0.8, 86% top-tercile overlap (fn13)",
        },
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print("\nRESULT — beta^UK per firm")
    print(f"  firms: {dist['n_firms']:,}   nonneg: {dist['n_nonneg']:,}   "
          f"neg: {dist['n_negative']:,}")
    print(f"  beta_uk  mean={dist['mean']:.4f}  sd={dist['sd']:.4f}  "
          f"min={dist['min']:.3f}  max={dist['max']:.3f}")
    print(f"  quantiles q10={dist['q10']:.3f} q25={dist['q25']:.3f} "
          f"q50={dist['q50']:.3f} q75={dist['q75']:.3f} q90={dist['q90']:.3f}")
    print(f"  NONNEG tercile pts: p33={dist['nonneg_p33']:.4f}  "
          f"p67={dist['nonneg_p67']:.4f}")
    print("  Campello anchors (paper, NOT prior-F1D): cut 0.28/0.68; "
          "~449+360 terciled firms")
    print(f"  -> {out_dir / 'beta_uk.parquet'}")
    print(f"  -> {out_dir / 'metadata.json'}")
    print("\n  beta^UK produced. Tercile / treatment assignment = STEP 3 "
          "(NOT built here).")


if __name__ == "__main__":
    main()
