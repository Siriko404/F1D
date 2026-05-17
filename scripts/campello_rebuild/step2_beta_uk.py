"""STEP 2 — β^UK first stage (Campello et al. 2022 JFQA, equation (13)).

Built FRESH from the paper (Sina supervised rebuild). Archived β^UK code is
NOT used as authority.

Verbatim eq-(13)  (Sina-pasted 2026-05-17, image-confirmed):

    vol(r_it) = α_i + β^UK_i · vol(FTSE100_t) + θ·CONTROLS_t + ε_it
    CONTROLS_t = { vol(SP500_t), vol(FX$£_t) }

  • estimated PER FIRM ("for each firm i")              — verbatim
  • β^UK_i = coefficient on vol(FTSE100)                — verbatim
  • monthly data 2010:M1 → 2014:M12 (≤60 monthly obs)   — verbatim
  • LEVEL form (linear in vol, not log)                 — verbatim printed eq

`vol(·)` construction — the one paper-silent element. Campello defers it to
"Following Bloom (2014)"; Bloom (2014) is absent from both the repo and the
NLM corpus, so no primary text is obtainable. Sina-RATIFIED convention
(2026-05-17, established paper-silent-operationalization channel; corroborated
paper-faithful by single-operator consistency — the same vol(·) is applied to
firm returns, precluding an implied-vol reading — and by the cited eq-(13)
data being CRSP prices + Bloomberg index/currency, i.e. return/price data):

    vol(X_t) = sample std-dev (ddof=1) of DAILY returns of X within
               calendar month t

Forced vendor substitutions (no Bloomberg license; data-availability-forced,
documented — same class as the Sina-ratified CRSP stock-return sub):
    firm returns  = CRSP_DSF `RET`            (daily holding-period return)
    FTSE100       = Yahoo_FTSE100 daily Close
    SP500         = CRSP_DSF `sprtrn`         (S&P500 composite daily return)
    USD/GBP       = BoE `XUDLUSS`             (USD per 1 GBP, daily)

Flagged micro-defaults (paper-silent, low-materiality, revisitable like the
consensus-EPS lag flag):
    MIN_DAYS_PER_MONTH = 15   (daily obs required to form a monthly vol)
    MIN_MONTHS_PER_FIRM = 24  (monthly obs required to estimate a firm OLS)

β^UK is estimated on the full CRSP universe (paper: "firm by firm"), then the
Step-1 sample is inner-joined (Table C.1 filter 9 = "match between COMPUSTAT
Quarterly NA and the estimated β^UK sample"); BOTH distributions are reported.

Output: outputs/campello_rebuild/step2_beta_uk/<ts>/
    beta_uk.parquet            (gvkey, beta_uk, se, t, nobs, r2)
    summary.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from f1d.shared.variables.brexit_stock_return import _load_ccm_permno_map  # verified

WIN_START = pd.Timestamp("2010-01-01")
WIN_END = pd.Timestamp("2014-12-31")
MIN_DAYS_PER_MONTH = 15      # flagged paper-silent micro-default
MIN_MONTHS_PER_FIRM = 24     # flagged paper-silent micro-default


def _ym(s: pd.Series) -> pd.Series:
    """Calendar year-month key: YYYY*100 + MM."""
    dt = pd.to_datetime(s)
    return (dt.dt.year * 100 + dt.dt.month).astype("int64")


def _monthly_vol(daily: pd.DataFrame, ret_col: str, by: list[str]) -> pd.DataFrame:
    """Sample std (ddof=1) of daily `ret_col` within each (by..., ym), with a
    minimum daily-obs gate. Returns columns by... + ['ym', vol_col]."""
    g = daily.groupby(by + ["ym"])[ret_col]
    out = g.agg(_n="count", _sd=lambda x: x.std(ddof=1)).reset_index()
    out = out[out["_n"] >= MIN_DAYS_PER_MONTH].copy()
    return out.rename(columns={"_sd": f"vol_{ret_col}"}).drop(columns="_n")


def _firm_daily_returns() -> pd.DataFrame:
    """CRSP_DSF daily firm RET + S&P500 sprtrn over 2010M1–2014M12."""
    dsf = ROOT / "inputs" / "CRSP_DSF"
    frames = []
    for yr in range(2010, 2015):
        for q in range(1, 5):
            p = dsf / f"CRSP_DSF_{yr}_Q{q}.parquet"
            d = pd.read_parquet(p, columns=["PERMNO", "date", "RET", "sprtrn"])
            frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d["date"] = pd.to_datetime(d["date"])
    d = d[(d["date"] >= WIN_START) & (d["date"] <= WIN_END)]
    for c in ("RET", "sprtrn"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["PERMNO"] = pd.to_numeric(d["PERMNO"], errors="coerce")
    d = d.dropna(subset=["PERMNO"])
    d["PERMNO"] = d["PERMNO"].astype("int64")
    d["ym"] = _ym(d["date"])
    return d


def _market_monthly_vol(firm_daily: pd.DataFrame) -> pd.DataFrame:
    """vol(SP500) from CRSP sprtrn (unique per date); vol(FTSE100) from Yahoo
    daily Close; vol(FX$£) from BoE XUDLUSS. Merged on ym."""
    # S&P500: sprtrn is one value per trading date (repeated across PERMNOs).
    sp = (
        firm_daily[["date", "sprtrn", "ym"]]
        .dropna(subset=["sprtrn"])
        .drop_duplicates(subset=["date"])
        .sort_values("date")
    )
    sp_vol = _monthly_vol(sp, "sprtrn", by=[])

    # FTSE100 (Yahoo daily Close → simple daily return).
    ft = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
    ft["date"] = pd.to_datetime(ft["Date"])
    ft = ft[(ft["date"] >= WIN_START) & (ft["date"] <= WIN_END)].sort_values("date")
    ft["ftse_ret"] = pd.to_numeric(ft["Close"], errors="coerce").pct_change()
    ft = ft.dropna(subset=["ftse_ret"])
    ft["ym"] = _ym(ft["date"])
    ft_vol = _monthly_vol(ft, "ftse_ret", by=[])

    # USD/GBP (BoE XUDLUSS = USD per 1 GBP → simple daily return).
    fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
    fx["date"] = pd.to_datetime(fx["DATE"], format="%d %b %Y")
    fx = fx[(fx["date"] >= WIN_START) & (fx["date"] <= WIN_END)].sort_values("date")
    fx["fx_ret"] = pd.to_numeric(fx["XUDLUSS"], errors="coerce").pct_change()
    fx = fx.dropna(subset=["fx_ret"])
    fx["ym"] = _ym(fx["date"])
    fx_vol = _monthly_vol(fx, "fx_ret", by=[])

    mkt = ft_vol.merge(sp_vol, on="ym", how="inner").merge(fx_vol, on="ym", how="inner")
    return mkt.rename(
        columns={
            "vol_ftse_ret": "vol_ftse",
            "vol_sprtrn": "vol_sp500",
            "vol_fx_ret": "vol_fx",
        }
    )


def _permno_month_to_gvkey(pm: pd.DataFrame) -> pd.DataFrame:
    """Attach gvkey to (PERMNO, ym) via CCM, valid at month-END
    (LINKDT ≤ month-end ≤ LINKENDDT). On a multi-link month keep the
    earliest-started link (parallels the verified quarterly mapper)."""
    ccm = _load_ccm_permno_map(ROOT)  # LPERMNO, gvkey, LINKDT, LINKENDDT
    pm = pm.copy()
    yy = pm["ym"] // 100
    mm = pm["ym"] % 100
    pm["mend"] = pd.to_datetime(dict(year=yy, month=mm, day=1)) + pd.offsets.MonthEnd(0)
    m = pm.merge(ccm, left_on="PERMNO", right_on="LPERMNO", how="left")
    m = m[(m["LINKDT"] <= m["mend"]) & (m["mend"] <= m["LINKENDDT"])].copy()
    m = m.sort_values("LINKDT").drop_duplicates(subset=["PERMNO", "ym"], keep="first")
    return m


def _ols_beta_uk(g: pd.DataFrame) -> tuple[float, float, float, int, float]:
    """Per-firm OLS  vol_r ~ 1 + vol_ftse + vol_sp500 + vol_fx.
    Returns (beta_uk, se, t, nobs, r2); beta_uk = coef on vol_ftse."""
    y = g["vol_r"].to_numpy(float)
    X = np.column_stack(
        [np.ones(len(g)), g["vol_ftse"].to_numpy(float),
         g["vol_sp500"].to_numpy(float), g["vol_fx"].to_numpy(float)]
    )
    n, k = X.shape
    if n < MIN_MONTHS_PER_FIRM or np.linalg.matrix_rank(X) < k:
        return (np.nan, np.nan, np.nan, n, np.nan)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = n - k
    sigma2 = float(resid @ resid) / dof
    xtx_inv = np.linalg.inv(X.T @ X)
    se = float(np.sqrt(sigma2 * xtx_inv[1, 1]))
    b = float(beta[1])
    tss = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(resid @ resid) / tss if tss > 0 else np.nan
    return (b, se, b / se if se > 0 else np.nan, n, r2)


def _dist(b: pd.Series) -> dict:
    return {
        "n_firms": int(b.size),
        "mean": float(b.mean()),
        "median": float(b.median()),
        "std": float(b.std(ddof=1)),
        "pct_negative": float((b < 0).mean()),
        "p01": float(b.quantile(0.01)), "p10": float(b.quantile(0.10)),
        "p25": float(b.quantile(0.25)), "p33": float(b.quantile(1 / 3)),
        "p50": float(b.quantile(0.50)), "p67": float(b.quantile(2 / 3)),
        "p75": float(b.quantile(0.75)), "p90": float(b.quantile(0.90)),
        "p99": float(b.quantile(0.99)),
    }


def main() -> None:
    print("=== STEP 2 — β^UK first stage (eq-13, fresh from paper) ===\n")

    fd = _firm_daily_returns()
    print(f"CRSP_DSF daily rows 2010M1–2014M12: {len(fd):,}; "
          f"PERMNOs: {fd['PERMNO'].nunique():,}")

    fd = fd[fd["RET"].notna() & (fd["RET"] > -1.0)]
    firm_vol = _monthly_vol(fd[["PERMNO", "ym", "RET"]], "RET", by=["PERMNO"]) \
        .rename(columns={"vol_RET": "vol_r"})
    print(f"firm (PERMNO,month) vols (≥{MIN_DAYS_PER_MONTH} days): {len(firm_vol):,}")

    mkt = _market_monthly_vol(fd)
    print(f"market months (FTSE∩SP500∩FX): {len(mkt):,}  "
          f"(expect ≤60; 2010M1–2014M12)")

    fm = firm_vol.merge(mkt, on="ym", how="inner")
    fm = _permno_month_to_gvkey(fm)
    # One firm (gvkey) can carry >1 PERMNO in a month (share classes); keep the
    # PERMNO contributing the most firm-months for that gvkey (primary security).
    pick = (fm.groupby(["gvkey", "PERMNO"]).size().reset_index(name="cnt")
              .sort_values("cnt", ascending=False)
              .drop_duplicates("gvkey", keep="first")[["gvkey", "PERMNO"]])
    fm = fm.merge(pick, on=["gvkey", "PERMNO"], how="inner")
    print(f"firm-months mapped to gvkey: {len(fm):,}; "
          f"gvkeys: {fm['gvkey'].nunique():,}")

    recs = []
    for gv, g in fm.groupby("gvkey", sort=False):
        b, se, t, n, r2 = _ols_beta_uk(g)
        if np.isfinite(b):
            recs.append((gv, b, se, t, n, r2))
    beta = pd.DataFrame(recs, columns=["gvkey", "beta_uk", "se", "t", "nobs", "r2"])
    print(f"\nβ^UK estimated (≥{MIN_MONTHS_PER_FIRM} months, full-rank): "
          f"{len(beta):,} firms")

    # Step-1 sample inner-join (Table C.1 filter 9 fold-in).
    s1_base = ROOT / "outputs" / "campello_rebuild" / "step1_sample"
    s1_dir = sorted(d for d in s1_base.iterdir() if d.is_dir())[-1]
    s1 = pd.read_parquet(s1_dir / "sample.parquet", columns=["gvkey"])
    s1_gv = set(s1["gvkey"].astype(str).str.zfill(6).unique())
    matched = beta[beta["gvkey"].isin(s1_gv)].copy()

    full_d = _dist(beta["beta_uk"])
    match_d = _dist(matched["beta_uk"])
    print("\n--- β^UK distribution: FULL CRSP universe ---")
    for k, v in full_d.items():
        print(f"  {k:>12}: {v:,.4f}" if k != "n_firms" else f"  {k:>12}: {v:,}")
    print("\n--- β^UK distribution: STEP-1 matched (filter-9 fold-in) ---")
    for k, v in match_d.items():
        print(f"  {k:>12}: {v:,.4f}" if k != "n_firms" else f"  {k:>12}: {v:,}")
    print(f"\nfilter-9: step-1 firms={len(s1_gv):,}  "
          f"with estimable β^UK={matched['gvkey'].nunique():,}  "
          f"({matched['gvkey'].nunique()/len(s1_gv):.1%})")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = ROOT / "outputs" / "campello_rebuild" / "step2_beta_uk" / ts
    odir.mkdir(parents=True, exist_ok=True)
    beta.to_parquet(odir / "beta_uk.parquet", index=False)
    matched.to_parquet(odir / "beta_uk_step1_matched.parquet", index=False)
    summary = {
        "equation": "vol(r_it) = a_i + beta_uk_i*vol(FTSE100) + th1*vol(SP500) + th2*vol(FX$/£) + e",
        "window": "2010M1-2014M12 monthly; vol = std(ddof=1) of daily returns within month",
        "vol_convention": "Sina-ratified 2026-05-17 (Bloom 2014 unobtainable; paper-silent channel)",
        "vendors": {
            "firm_return": "CRSP_DSF RET", "sp500": "CRSP_DSF sprtrn",
            "ftse100": "Yahoo_FTSE100 daily Close", "usd_gbp": "BoE XUDLUSS",
            "note": "vendor subs forced — no Bloomberg license; documented deviation",
        },
        "micro_defaults": {"min_days_per_month": MIN_DAYS_PER_MONTH,
                           "min_months_per_firm": MIN_MONTHS_PER_FIRM},
        "dist_full_crsp": full_d,
        "dist_step1_matched": match_d,
        "filter9": {"step1_firms": len(s1_gv),
                    "with_beta_uk": int(matched["gvkey"].nunique())},
        "step1_dir": s1_dir.name,
    }
    (odir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nwritten → {odir}")


if __name__ == "__main__":
    main()
