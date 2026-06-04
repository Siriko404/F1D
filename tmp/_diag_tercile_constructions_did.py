"""Test alternative β^UK tercile CONSTRUCTIONS through the real DiD machinery.

Motivated by the verbatim audit (auditor note #5): the 449>360 asymmetry +
cutpoint ratio 0.28:0.68 are reconciled if terciles are equal-count over the
FULL β^UK distribution (incl. negatives), with the bottom third then losing
its β<0 members to the control-exclusion (B3). The paper is SILENT on the
tercile base population (B5), so we test the constructions explicitly.

Each construction produces a treated/control labeling; we feed it through the
runner's own _build_and_fit (same DV=T8 net-of-cash, controls, FE, SE, window)
and report T/C counts + δ̂. Compares directly to current (nonneg equal-count).

Constructions (all restricted to step1 firms for the panel):
  C0  nonneg equal-count terciles            [CURRENT: treated=top, control=bottom]
  C1  FULL-dist equal-count, control∩(β≥0)   [auditor #5: cuts over all β, drop neg from control]
  C2  FULL-UNIVERSE equal-count, control∩(β≥0)[B5 full-universe cuts + drop neg from control]

Read-only on data; writes nothing. Prints cutpoints, T/C, δ̂ per construction.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_rp = ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did.py"
_rs = importlib.util.spec_from_file_location("_runner", _rp)
_runner = importlib.util.module_from_spec(_rs)
_rs.loader.exec_module(_runner)
_build_and_fit = _runner._build_and_fit

from step7_fullpanel_hypothesis import _latest


def _load_beta() -> tuple[pd.DataFrame, set]:
    s2 = _latest("step2_beta_uk")
    beta = pd.read_parquet(s2 / "beta_uk.parquet", columns=["gvkey", "beta_uk"])
    beta["gvkey"] = beta["gvkey"].astype(str).str.zfill(6)
    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet", columns=["gvkey"])
    s1_gv = set(s1["gvkey"].astype(str).str.zfill(6).unique())
    return beta, s1_gv


def _assign(beta: pd.DataFrame, s1_gv: set, cut_pool: str) -> tuple[pd.DataFrame, float, float]:
    """Return treated/control labeling (gvkey, HIGH_UK_EXPOSURE) + cutpoints.

    cut_pool:
      'nonneg_step1' : equal-count terciles over step1 ∩ (β>=0)   [C0 current]
      'full_step1'   : equal-count terciles over step1 ∩ all β    [C1]
      'full_universe': equal-count terciles over FULL est. ∩ all β[C2]
    control always excludes β<0 (B3); treated = top third.
    """
    b = beta.copy()
    b["in_s1"] = b["gvkey"].isin(s1_gv)
    if cut_pool == "nonneg_step1":
        pool = b[b["in_s1"] & (b["beta_uk"] >= 0)]["beta_uk"]
    elif cut_pool == "full_step1":
        pool = b[b["in_s1"]]["beta_uk"]
    elif cut_pool == "full_universe":
        pool = b["beta_uk"]
    else:
        raise ValueError(cut_pool)
    q33 = float(pool.quantile(1 / 3)); q67 = float(pool.quantile(2 / 3))

    panel = b[b["in_s1"]].copy()
    treated = panel["beta_uk"] >= q67
    control = (panel["beta_uk"] <= q33) & (panel["beta_uk"] >= 0)  # B3: drop neg
    lab = panel[treated | control].copy()
    lab["HIGH_UK_EXPOSURE"] = np.where(lab["beta_uk"] >= q67, 1, 0)
    return lab[["gvkey", "HIGH_UK_EXPOSURE"]], q33, q67


def main() -> None:
    beta, s1_gv = _load_beta()
    print("=" * 72)
    print("β^UK TERCILE CONSTRUCTION SWEEP — market DiD (DV=T8 net-of-cash)")
    print("=" * 72)
    print(f"full est. β firms={len(beta):,}  step1∩β firms={beta['gvkey'].isin(s1_gv).sum():,}")
    print(f"Campello: cuts 0.28/0.68 | T/C 449/360 | δ=+0.231***\n")

    specs = [
        ("C0 nonneg-step1 (CURRENT)", "nonneg_step1"),
        ("C1 full-dist-step1  (#5)", "full_step1"),
        ("C2 full-universe    (B5)", "full_universe"),
    ]
    print(f"{'construction':<28} {'p33':>7} {'p67':>7} {'T':>5} {'C':>5} "
          f"{'δ̂':>9} {'SE':>7} {'p':>7} {'N':>7}")
    print("-" * 72)
    for name, pool in specs:
        lab, q33, q67 = _assign(beta, s1_gv, pool)
        t = int((lab.HIGH_UK_EXPOSURE == 1).sum())
        c = int((lab.HIGH_UK_EXPOSURE == 0).sum())
        try:
            r = _build_and_fit(lab, name)
            print(f"{name:<28} {q33:>7.3f} {q67:>7.3f} {t:>5,} {c:>5,} "
                  f"{r['delta_hat']:>+9.4f} {r['se']:>7.4f} {r['pvalue']:>7.4f} "
                  f"{r['nobs']:>7,}")
        except KeyError as e:
            print(f"{name:<28} {q33:>7.3f} {q67:>7.3f} {t:>5,} {c:>5,} "
                  f"  FIT FAILED: {e} (interaction absorbed/collinear)")
    print("-" * 72)
    print("Watch: does any construction give T>C (like 449>360) AND move δ̂>0?")


if __name__ == "__main__":
    main()
