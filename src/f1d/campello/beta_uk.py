"""Phase 2: β^UK estimation — STEP 01-05, 23-24 of method lockin.

Equation (13) [verbatim from lockin PARA_02]:
    vol(r_it) = α_i + β_i^UK · vol(FTSE100)_t + θ · CONTROLS_t + ε_it

CONTROLS_t = vol(SP500), vol(FX$£)  [lockin PARA_03 verbatim]

Estimation:
  - Monthly data 2010:M1–2014:M12 (60 months) [STEP 24]
  - Per-firm OLS over its 60 monthly obs [STEP 05]
  - β_i^UK = coefficient on vol(FTSE100)
  - vol() computed Bloom-2014-style: within-month std of daily returns

Data sources:
  - FTSE100 daily: inputs/Brexit_replication/Yahoo_FTSE100/FTSE100_yfinance_daily.csv
  - USD/GBP daily: inputs/Brexit_replication/BoE/USD_GBP_daily_2008-2018.csv
  - CRSP DSF (RET, sprtrn): inputs/CRSP_DSF/CRSP_DSF_YYYY_QN.parquet
  - Compustat→CRSP link: inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2014-12-31")


def _monthly_vol(daily: pd.Series, date: pd.Series) -> pd.DataFrame:
    """Compute monthly realized volatility = within-month std of daily values.

    Args:
        daily: daily return series (already in returns form, not prices).
        date: aligned datetime series.

    Returns:
        DataFrame [ym, vol] where ym = year-month integer (YYYYMM).
    """
    df = pd.DataFrame({"ret": daily.values, "date": pd.to_datetime(date).values})
    df["ym"] = df["date"].dt.year * 100 + df["date"].dt.month
    g = df.groupby("ym")["ret"].agg(["std", "count"]).reset_index()
    g = g[g["count"] >= 10].rename(columns={"std": "vol"})
    return g[["ym", "vol"]]


def _load_ftse100_vol(root: Path) -> pd.DataFrame:
    path = root / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv"
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[(df["Date"] >= START) & (df["Date"] <= END)].sort_values("Date")
    df["ret"] = df["Close"].pct_change()
    df = df.dropna(subset=["ret"])
    out = _monthly_vol(df["ret"], df["Date"]).rename(columns={"vol": "vol_FTSE"})
    logger.info("FTSE100 monthly vol: %s months", len(out))
    return out


def _load_fx_vol(root: Path) -> pd.DataFrame:
    path = root / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv"
    df = pd.read_csv(path)
    df["DATE"] = pd.to_datetime(df["DATE"], format="%d %b %Y", errors="coerce")
    df = df[(df["DATE"] >= START) & (df["DATE"] <= END)].sort_values("DATE")
    df["ret"] = df["XUDLUSS"].pct_change()
    df = df.dropna(subset=["ret"])
    out = _monthly_vol(df["ret"], df["DATE"]).rename(columns={"vol": "vol_FX"})
    logger.info("USD/GBP monthly vol: %s months", len(out))
    return out


def _load_crsp_returns(root: Path, permnos: set) -> pd.DataFrame:
    """Load daily RET + sprtrn for 2010-2014, filtered to sample permnos."""
    dsf_dir = root / "inputs" / "CRSP_DSF"
    frames = []
    for year in range(2010, 2015):
        for q in (1, 2, 3, 4):
            f = dsf_dir / f"CRSP_DSF_{year}_Q{q}.parquet"
            if not f.exists():
                continue
            df = pd.read_parquet(f, columns=["PERMNO", "date", "RET", "sprtrn"])
            df = df[df["PERMNO"].isin(permnos)]
            frames.append(df)
    crsp = pd.concat(frames, ignore_index=True)
    crsp["date"] = pd.to_datetime(crsp["date"])
    crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
    crsp["sprtrn"] = pd.to_numeric(crsp["sprtrn"], errors="coerce")
    crsp = crsp.dropna(subset=["RET"])
    logger.info("CRSP daily obs: %s", f"{len(crsp):,}")
    return crsp


def _load_sp500_vol_from_crsp(crsp: pd.DataFrame) -> pd.DataFrame:
    """SP500 monthly vol from sprtrn (one row per day across stocks → dedup)."""
    sp = crsp[["date", "sprtrn"]].dropna().drop_duplicates(subset=["date"]).sort_values("date")
    out = _monthly_vol(sp["sprtrn"], sp["date"]).rename(columns={"vol": "vol_SP500"})
    logger.info("SP500 monthly vol: %s months", len(out))
    return out


def _build_ccm_link(root: Path, gvkeys) -> pd.DataFrame:
    path = root / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
    ccm = pd.read_parquet(path, columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
    ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
    ccm = ccm[ccm["gvkey"].isin(gvkeys)]
    # Keep primary links (LU, LC) — standard CCM convention
    ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]
    ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
    # E = still active → set to far future
    ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
    # filter links overlapping with estimation window
    ccm = ccm[(ccm["LINKENDDT"] >= START) & (ccm["LINKDT"] <= END)]
    ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
    ccm = ccm.dropna(subset=["LPERMNO"])
    logger.info("CCM links: %s gvkey-permno pairs", len(ccm))
    return ccm


def _firm_monthly_vol(crsp: pd.DataFrame) -> pd.DataFrame:
    """Monthly vol of daily RET per PERMNO."""
    df = crsp.copy()
    df["ym"] = df["date"].dt.year * 100 + df["date"].dt.month
    g = df.groupby(["PERMNO", "ym"])["RET"].agg(["std", "count"]).reset_index()
    g = g[g["count"] >= 10].rename(columns={"std": "vol_r"})
    return g[["PERMNO", "ym", "vol_r"]]


def _ols_per_firm(firm_panel: pd.DataFrame) -> dict:
    """Run OLS per gvkey, return dict gvkey -> (beta_uk, n, r2).

    panel cols: gvkey, ym, vol_r, vol_FTSE, vol_SP500, vol_FX
    """
    results = {}
    for gvkey, grp in firm_panel.groupby("gvkey"):
        g = grp.dropna(subset=["vol_r", "vol_FTSE", "vol_SP500", "vol_FX"])
        if len(g) < 24:  # min 24/60 months
            continue
        X = np.column_stack([
            np.ones(len(g)),
            g["vol_FTSE"].values,
            g["vol_SP500"].values,
            g["vol_FX"].values,
        ])
        y = g["vol_r"].values
        try:
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            y_pred = X @ beta
            ss_res = ((y - y_pred) ** 2).sum()
            ss_tot = ((y - y.mean()) ** 2).sum()
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
            results[gvkey] = (beta[1], len(g), r2)  # beta[1] = β^UK
        except np.linalg.LinAlgError:
            continue
    return results


def build_beta_uk(root: Path) -> pd.DataFrame:
    # Load sample to know which gvkeys we need
    out_root = root / "outputs" / "campello_v2"
    runs = sorted([d for d in out_root.iterdir()
                   if d.is_dir() and (d / "variables_panel.parquet").exists()], reverse=True)
    if not runs:
        raise FileNotFoundError("No variables panel found. Run variables.py first.")
    var_path = runs[0] / "variables_panel.parquet"
    logger.info("Loading variables panel from %s", var_path)
    panel = pd.read_parquet(var_path)
    sample_gvkeys = set(panel["gvkey"].unique())
    logger.info("Sample gvkeys: %s", len(sample_gvkeys))

    # Load index/FX monthly vol
    vol_ftse = _load_ftse100_vol(root)
    vol_fx = _load_fx_vol(root)

    # Map gvkey → permno via CCM
    ccm = _build_ccm_link(root, sample_gvkeys)
    permnos = set(ccm["LPERMNO"].dropna().astype(int).tolist())
    logger.info("Permnos to query: %s", len(permnos))

    # Load CRSP daily returns
    crsp = _load_crsp_returns(root, permnos)

    # SP500 vol (from sprtrn)
    vol_sp = _load_sp500_vol_from_crsp(crsp)

    # Per-firm monthly vol
    firm_vol = _firm_monthly_vol(crsp)
    logger.info("Firm-month obs: %s", f"{len(firm_vol):,}")

    # Join all on ym
    market = vol_ftse.merge(vol_sp, on="ym").merge(vol_fx, on="ym")
    logger.info("Market months with all 3 vols: %s", len(market))

    firm_panel = firm_vol.merge(market, on="ym")
    # Attach gvkey via ccm (need to filter ccm to valid permno-window pairs)
    ccm["LPERMNO"] = ccm["LPERMNO"].astype(int)
    ccm_simple = ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]].rename(columns={"LPERMNO": "PERMNO"})

    # date validity: ym → first-of-month date for link-window check
    firm_panel["ym_date"] = pd.to_datetime(
        (firm_panel["ym"] // 100).astype(str) + "-"
        + (firm_panel["ym"] % 100).astype(str).str.zfill(2) + "-15"
    )

    merged = firm_panel.merge(ccm_simple, on="PERMNO")
    merged = merged[
        (merged["ym_date"] >= merged["LINKDT"]) & (merged["ym_date"] <= merged["LINKENDDT"])
    ]
    merged = merged.drop(columns=["LINKDT", "LINKENDDT", "ym_date"])
    merged = merged.drop_duplicates(subset=["gvkey", "ym"], keep="first")
    logger.info("Firm-month obs after CCM merge: %s", f"{len(merged):,}")

    # Run OLS per firm
    results = _ols_per_firm(merged)
    logger.info("Firms with β^UK estimate: %s", len(results))

    beta_df = pd.DataFrame([
        {"gvkey": gv, "beta_uk": b, "n_months": n, "r2": r}
        for gv, (b, n, r) in results.items()
    ])

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = root / "outputs" / "campello_v2" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    beta_df.to_parquet(out_dir / "beta_uk.parquet", index=False)
    logger.info("Saved β^UK to %s", out_dir / "beta_uk.parquet")

    # Distribution summary
    b = beta_df["beta_uk"]
    print(f"\n--- β^UK distribution ({len(b):,} firms) ---")
    print(f"  mean={b.mean():.3f}  sd={b.std():.3f}  min={b.min():.3f}  max={b.max():.3f}")
    print(f"  p25={b.quantile(0.25):.3f}  p50={b.median():.3f}  p75={b.quantile(0.75):.3f}")
    print(f"  β<0: {(b<0).sum():,}  β≥0: {(b>=0).sum():,}")
    print(f"\nPaper benchmark (lockin PARA_07 verbatim):")
    print(f"  treated tercile β > 0.68 → 449 firms")
    print(f"  control tercile β < 0.28 → 360 firms")

    # Compute terciles among β≥0
    pos = b[b >= 0]
    if len(pos) > 0:
        t1 = pos.quantile(1/3)
        t2 = pos.quantile(2/3)
        print(f"\nMy positive-β terciles: t1={t1:.3f} t2={t2:.3f}")
        print(f"  treated (β > t2): {(b > t2).sum():,}")
        print(f"  control (0 ≤ β < t1): {((b >= 0) & (b < t1)).sum():,}")

    return beta_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    rp = Path(__file__).resolve().parent.parent.parent.parent
    build_beta_uk(rp)
