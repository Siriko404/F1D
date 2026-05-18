"""DIAG — verify Step-6 fit drops NO regressor (drop_absorbed silent-drop check).

Reloads the latest step6 saved panel, reconstructs the EXACT fit the
script runs (common A/B dropna sample, FIRM FE + IND×QTR FE, double-
clustered), and asserts every intended regressor has a finite coefficient.
Read-only diagnostic; writes nothing.
"""
from __future__ import annotations
import sys, warnings
from pathlib import Path
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
BASE_CTRL = ["brexit_stock_return", "brexit_tobins_q", "brexit_cash_flow",
             "brexit_sales_growth", "log_assets"]


def _latest(sub: str) -> Path:
    b = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in b.iterdir() if d.is_dir())[-1]


def main() -> None:
    d = _latest("step6_controls_did")
    df = pd.read_parquet(d / "did_panel_controls.parquet")
    print(f"panel: {d.name}  ({len(df):,} rows)")

    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)
    common = df.dropna(subset=["CASH", "indqtr_code"] + BASE_CTRL
                       + ["cons_fwd", "cons_lag1"]).copy()
    pcommon = common.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    print(f"common A/B sample: {len(common):,} fq / "
          f"{common['gvkey'].nunique():,} firms\n")

    from linearmodels.panel import PanelOLS
    ok = True
    for tag, ccons in (("A_forward", "cons_fwd"), ("B_lag1", "cons_lag1")):
        xcols = ["POST_x_HIGH"] + BASE_CTRL + [ccons]
        with warnings.catch_warnings(record=True) as wlist:
            warnings.simplefilter("always")
            mod = PanelOLS(pcommon["CASH"], pcommon[xcols],
                           entity_effects=True,
                           other_effects=pcommon["indqtr_code"],
                           drop_absorbed=True)
            res = mod.fit(cov_type="clustered", cluster_entity=True,
                          cluster_time=True)
        got = list(res.params.index)
        missing = [c for c in xcols if c not in got]
        extra = [c for c in got if c not in xcols]
        nan = [c for c in got if not pd.notna(res.params[c])]
        print(f"[{tag}] intended {len(xcols)}  fitted {len(got)}")
        for c in xcols:
            mark = "OK " if c in got and c not in nan else "MISSING"
            val = f"{res.params[c]:+.6f}" if c in got else "   ---   "
            se = f"{res.std_errors[c]:.6f}" if c in got else "  ---  "
            print(f"   {mark}  {c:<22} coef {val}  SE {se}")
        if missing:
            ok = False
            print(f"   !! DROPPED: {missing}")
        if extra:
            print(f"   ?? UNEXPECTED: {extra}")
        if nan:
            ok = False
            print(f"   !! NaN coef: {nan}")
        wmsgs = [str(w.message) for w in wlist
                 if "absorb" in str(w.message).lower()
                 or "drop" in str(w.message).lower()
                 or "collinear" in str(w.message).lower()]
        if wmsgs:
            print(f"   absorb/drop warnings: {wmsgs}")
        else:
            print(f"   absorb/drop warnings: none")
        print()
    print("VERDICT:", "ALL REGRESSORS RETAINED — no missing coefficient"
          if ok else "** A REGRESSOR WAS DROPPED / NaN — see above **")


if __name__ == "__main__":
    main()
