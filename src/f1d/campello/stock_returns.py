"""STOCK_RETURNS — VAR_43: quarterly buy-and-hold equity return.

Definition (verbatim from variable lockin):
> STOCK_RETURNS are defined as the quarterly buy-and-hold return.
> Quarterly buy-and-hold equity return (entered lagged as a firm control). CRSP.

Computation:
  daily RET → quarterly compound: ∏(1 + r_d) − 1 within (PERMNO, cal_yr_qtr).
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2016-12-31")


def _load_ccm(root: Path, gvkeys: set) -> pd.DataFrame:
    path = root / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
    ccm = pd.read_parquet(path, columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
    ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
    ccm = ccm[ccm["gvkey"].isin(gvkeys)]
    ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]
    ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
    ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
    ccm = ccm[(ccm["LINKENDDT"] >= START) & (ccm["LINKDT"] <= END)]
    ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
    ccm = ccm.dropna(subset=["LPERMNO"])
    return ccm


def _load_crsp_daily(root: Path, permnos: set) -> pd.DataFrame:
    frames = []
    for year in range(2010, 2017):
        for q in (1, 2, 3, 4):
            f = root / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
            if not f.exists():
                continue
            df = pd.read_parquet(f, columns=["PERMNO", "date", "RET"])
            df = df[df["PERMNO"].isin(permnos)]
            frames.append(df)
    crsp = pd.concat(frames, ignore_index=True)
    crsp["date"] = pd.to_datetime(crsp["date"])
    crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
    crsp = crsp.dropna(subset=["RET"])
    return crsp


def build_stock_returns(root: Path) -> pd.DataFrame:
    # Load sample
    out_root = root / "outputs" / "campello_v2"
    runs = sorted([d for d in out_root.iterdir()
                   if d.is_dir() and (d / "variables_panel.parquet").exists()], reverse=True)
    var_path = runs[0] / "variables_panel.parquet"
    panel = pd.read_parquet(var_path)
    gvkeys = set(panel["gvkey"].unique())
    logger.info("Sample gvkeys: %s", len(gvkeys))

    ccm = _load_ccm(root, gvkeys)
    permnos = set(ccm["LPERMNO"].dropna().astype(int).tolist())
    logger.info("Permnos: %s", len(permnos))

    crsp = _load_crsp_daily(root, permnos)
    logger.info("CRSP daily obs: %s", f"{len(crsp):,}")

    # Quarterly buy-and-hold per PERMNO
    crsp["cal_yr"] = crsp["date"].dt.year
    crsp["cal_qtr"] = crsp["date"].dt.quarter
    crsp["cal_yr_qtr"] = crsp["cal_yr"] * 10 + crsp["cal_qtr"]
    crsp["log1p_ret"] = np.log1p(crsp["RET"])
    bhr = crsp.groupby(["PERMNO", "cal_yr_qtr"]).agg(
        log_sum=("log1p_ret", "sum"), n=("RET", "count")
    ).reset_index()
    # require at least 40 trading days in the quarter (~63 typical)
    bhr = bhr[bhr["n"] >= 40]
    bhr["STOCK_RETURNS"] = np.expm1(bhr["log_sum"])
    bhr = bhr[["PERMNO", "cal_yr_qtr", "STOCK_RETURNS"]]
    logger.info("Permno-quarter BHR obs: %s", f"{len(bhr):,}")

    # Map PERMNO → gvkey via CCM (using cal_yr_qtr midpoint date)
    ccm_simple = ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]].rename(columns={"LPERMNO": "PERMNO"})
    ccm_simple["PERMNO"] = ccm_simple["PERMNO"].astype(int)

    bhr["yq_date"] = pd.to_datetime(
        (bhr["cal_yr_qtr"] // 10).astype(str) + "-"
        + ((bhr["cal_yr_qtr"] % 10) * 3).astype(str).str.zfill(2) + "-15"
    )

    merged = bhr.merge(ccm_simple, on="PERMNO")
    merged = merged[(merged["yq_date"] >= merged["LINKDT"]) & (merged["yq_date"] <= merged["LINKENDDT"])]
    merged = merged.drop(columns=["LINKDT", "LINKENDDT", "yq_date", "PERMNO"])
    merged = merged.drop_duplicates(subset=["gvkey", "cal_yr_qtr"], keep="first")
    logger.info("Gvkey-quarter STOCK_RETURNS obs: %s", f"{len(merged):,}")

    # Winsorize 1%/99% by cal_yr_qtr
    merged = merged.sort_values(["gvkey", "cal_yr_qtr"]).reset_index(drop=True)
    out = pd.Series(np.nan, index=merged.index, dtype="float64")
    for _q, idx in merged.groupby("cal_yr_qtr").groups.items():
        v = merged.loc[idx, "STOCK_RETURNS"]
        if v.notna().sum() < 10:
            out.loc[idx] = v
            continue
        lo, hi = v.quantile(0.01), v.quantile(0.99)
        out.loc[idx] = v.clip(lower=lo, upper=hi)
    merged["STOCK_RETURNS"] = out

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = root / "outputs" / "campello_v2" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(out_dir / "stock_returns.parquet", index=False)
    logger.info("Saved STOCK_RETURNS to %s", out_dir / "stock_returns.parquet")

    s = merged["STOCK_RETURNS"].dropna()
    print(f"\n--- STOCK_RETURNS (quarterly BHR, post-winsorization) ---")
    print(f"  N={len(s):,}  mean={s.mean():.4f}  sd={s.std():.4f}  median={s.median():.4f}")
    # Table 1 Panel A benchmark anchor
    print(f"  Anchor (Table 1 Panel A): N=72,762  mean=0.03  sd=0.27  median=0.03 [check json]")

    return merged


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    rp = Path(__file__).resolve().parent.parent.parent.parent
    build_stock_returns(rp)
