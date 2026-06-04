"""Run the CASH DiD using treatments from the closest scope×keyword permutations
and compare delta to Campello textual Table 8 (delta=0.357***).

Builds a (gvkey, HIGH_UK_EXPOSURE) treatment from per_filing.json for each
chosen (scope, keyword-subset), classifying firms treated>5 / control==0 (drop
1-5 middle) via the SAME dedupe-latest + CCM time-map + gvkey-sum used in the
sweep, then feeds it to the runner's _build_and_fit (identical eq-14 panel/FE/
SE/controls/winsor as production). Read-only.

DIAGNOSTIC: keyword subsets are paper-VERBATIM (all 9 listed); a subset here is
evidence about Campello's effective counting, not a lockable spec.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))
OUTBASE = ROOT / "outputs" / "campello_rebuild" / "textual_keyword_decomp"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import step3b3_textual_treatment_sec17 as s3  # noqa: E402

_rp = ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did.py"
_rs = importlib.util.spec_from_file_location("_runner", _rp)
_runner = importlib.util.module_from_spec(_rs)
_rs.loader.exec_module(_runner)

CAMP_DELTA = 0.357


def _load_rows() -> list[dict]:
    d = sorted(p for p in OUTBASE.iterdir() if p.is_dir())[-1]
    return json.loads((d / "per_filing.json").read_text(encoding="utf-8"))


def _treatment(rows: list[dict], subset: list[str]) -> pd.DataFrame:
    """Whole-doc count over `subset`; classify gvkey treated>5 / control==0."""
    rec = [(r["cik"], r["filing_date"],
            sum(r["counts_whole"][t] for t in subset)) for r in rows]
    d = pd.DataFrame(rec, columns=["cik", "filing_date", "val"])
    d = (d.sort_values(["cik", "filing_date"], kind="stable")
           .drop_duplicates("cik", keep="last"))
    ccm = s3._load_ccm()
    mg = d.merge(ccm, on="cik", how="left")
    fd = pd.to_datetime(mg["filing_date"], format="%Y%m%d")
    ok = (fd >= mg["LINKDT"]) & (fd <= mg["LINKENDDT"])
    mp = (mg[ok].sort_values(["cik", "LINKDT"], kind="stable")
              .drop_duplicates("cik", keep="first"))
    g = mp.groupby("gvkey", as_index=False)["val"].sum()
    g["group"] = "_mid"
    g.loc[g["val"] > 5, "group"] = "treated"
    g.loc[g["val"] == 0, "group"] = "control"
    tc = g[g["group"].isin(["treated", "control"])].copy()
    tc["gvkey"] = tc["gvkey"].astype(str).str.zfill(6)
    tc["HIGH_UK_EXPOSURE"] = (tc["group"] == "treated").astype(int)
    return tc[["gvkey", "HIGH_UK_EXPOSURE"]]


def main() -> None:
    rows = _load_rows()
    perms = [
        ("P1 closest", ["great britain", "uncertainty", "referendum"]),
        ("P2 uncertainty-only", ["uncertainty"]),
        ("P3 gb+unc", ["great britain", "uncertainty"]),
        ("P4 all-9 (whole)", ["brexit", "great britain", "uncertainty",
                              "referendum", "uncertain", "united kingdom",
                              "uk", "u.k.", "g.b."]),
    ]
    print(f"{'permutation':<22} {'nT':>5} {'nC':>5} {'delta':>8} {'se':>7} "
          f"{'p':>7} {'N':>7}   [Campello delta=0.357***]")
    print("-" * 86)
    results = []
    for name, subset in perms:
        tc = _treatment(rows, subset)
        nT0 = int((tc["HIGH_UK_EXPOSURE"] == 1).sum())
        nC0 = int((tc["HIGH_UK_EXPOSURE"] == 0).sum())
        r = _runner._build_and_fit(tc, name)
        results.append((name, nT0, nC0, r))
        star = ("***" if r["pvalue"] < 0.01 else "**" if r["pvalue"] < 0.05
                else "*" if r["pvalue"] < 0.1 else "")
        print(f"{name:<22} {nT0:>5} {nC0:>5} {r['delta_hat']:>+8.4f} "
              f"{r['se']:>7.4f} {r['pvalue']:>7.4f} {r['nobs']:>7,} {star}")

    # current production textual (step3b3 §1+7, all-9) for reference
    prod = _runner._load_textual_treatment()
    prod = prod[["gvkey", "HIGH_UK_EXPOSURE"]].copy()
    prod["gvkey"] = prod["gvkey"].astype(str).str.zfill(6)
    rp = _runner._build_and_fit(prod, "PROD step3b3 §1+7")
    star = ("***" if rp["pvalue"] < 0.01 else "**" if rp["pvalue"] < 0.05
            else "*" if rp["pvalue"] < 0.1 else "")
    print(f"{'PROD step3b3 §1+7':<22} {'':>5} {'':>5} {rp['delta_hat']:>+8.4f} "
          f"{rp['se']:>7.4f} {rp['pvalue']:>7.4f} {rp['nobs']:>7,} {star}")
    print(f"\nCampello textual Table 8: delta=+0.357 se=0.062 N=24,195 ***")


if __name__ == "__main__":
    main()
