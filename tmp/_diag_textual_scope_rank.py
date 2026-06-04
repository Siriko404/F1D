"""Rank textual-scope permutations by closeness to Campello 807 treated / 433
control. Reuses the saved per-filing per-section counts (no re-parse).

DEFENSIBLE ONLY because the paper is SILENT on which 10-K section(s) the Brexit
text measure reads (verbatim Q2 = NOT STATED). This reverse-engineers that
underdetermined choice. The winner is a HYPOTHESIS to verify against the paper,
NOT an auto-locked spec (symptom-chasing a target is otherwise forbidden — see
step3_treatment docstring).

Scope candidates (term count = sum over the chosen section spans):
  whole          whole filing
  item1          Item 1 (Business) only
  item7          Item 7 (MD&A) only
  item1+7        Item 1 + Item 7
Each section-based scope in two missing-section treatments:
  strict   filings lacking a required section are EXCLUDED (step3b3 behavior)
  lenient  missing section counts as 0 (firm stays, contributes 0)

Firm-level: dedupe latest filing/CIK -> CCM time-map to gvkey -> sum -> classify
>5 treated / ==0 control. Ranks by relative-L1 distance to (807,433). Read-only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))
OUTBASE = ROOT / "outputs" / "campello_rebuild" / "textual_keyword_decomp"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import step3b3_textual_treatment_sec17 as s3  # noqa: E402

CAMP_T, CAMP_C = 807, 433


def _load_latest() -> list[dict]:
    d = sorted(p for p in OUTBASE.iterdir() if p.is_dir())[-1]
    print(f"per_filing source: {d.name}")
    return json.loads((d / "per_filing.json").read_text(encoding="utf-8"))


def _sec_total(rec: dict, label: str):
    """Total Brexit-term count in one section span, or None if section absent."""
    s = rec["sections"].get(label)
    return None if s is None else sum(s["counts"].values())


def _build(rows: list[dict]) -> pd.DataFrame:
    out = []
    for r in rows:
        i1 = _sec_total(r, "1")
        i7 = _sec_total(r, "7")
        out.append({
            "cik": r["cik"], "filing_date": r["filing_date"],
            "whole": r["total_whole"],
            "item1": i1, "item7": i7,
            "item1+7": (i1 + i7) if (i1 is not None and i7 is not None) else None,
        })
    return pd.DataFrame(out)


def _tc(df: pd.DataFrame, ccm: pd.DataFrame, col: str, strict: bool) -> tuple:
    d = df[["cik", "filing_date", col]].copy()
    if strict:
        d = d[d[col].notna()]
    else:
        d[col] = d[col].fillna(0)
    d = (d.sort_values(["cik", "filing_date"], kind="stable")
           .drop_duplicates("cik", keep="last"))
    mg = d.merge(ccm, on="cik", how="left")
    fd = pd.to_datetime(mg["filing_date"], format="%Y%m%d")
    ok = (fd >= mg["LINKDT"]) & (fd <= mg["LINKENDDT"])
    mp = (mg[ok].sort_values(["cik", "LINKDT"], kind="stable")
              .drop_duplicates("cik", keep="first"))
    g = mp.groupby("gvkey", as_index=False)[col].sum()
    t = int((g[col] > 5).sum())
    c = int((g[col] == 0).sum())
    return t, c, int(len(g))


def main() -> None:
    rows = _load_latest()
    df = _build(rows)
    ccm = s3._load_ccm()

    candidates = [
        ("whole", "whole", True),       # whole has no missing concept
        ("item1", "item1", True), ("item1", "item1", False),
        ("item7", "item7", True), ("item7", "item7", False),
        ("item1+7", "item1+7", True), ("item1+7", "item1+7", False),
    ]
    res = []
    for name, col, strict in candidates:
        t, c, nf = _tc(df, ccm, col, strict)
        rel = abs(t - CAMP_T) / CAMP_T + abs(c - CAMP_C) / CAMP_C
        res.append({"scope": name,
                    "missing": "strict" if strict else "lenient",
                    "treated": t, "control": c, "firms": nf,
                    "dT": t - CAMP_T, "dC": c - CAMP_C,
                    "relL1": round(rel, 3)})
    rk = pd.DataFrame(res).sort_values("relL1").reset_index(drop=True)

    pd.set_option("display.width", 200)
    print(f"\nTarget: Campello treated={CAMP_T}  control={CAMP_C}\n")
    print("=== scope permutations ranked by closeness (relL1, lower=better) ===")
    print(rk.to_string(index=False))
    best = rk.iloc[0]
    print(f"\nclosest: scope={best['scope']} ({best['missing']}) -> "
          f"T={best['treated']} C={best['control']}  "
          f"(dT={best['dT']:+d}, dC={best['dC']:+d}, relL1={best['relL1']})")
    print("\nNOTE: closeness != correctness. Treat the leader as a hypothesis "
          "to check against the paper, not an auto-locked spec.")


if __name__ == "__main__":
    main()
