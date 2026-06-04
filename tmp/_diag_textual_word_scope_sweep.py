"""Vectorized scope × keyword sweep — rank (section-scope, keyword-subset)
combos by closeness to Campello 807 treated / 433 control.

DIAGNOSTIC ONLY. Scope is paper-SILENT (legit to reverse-engineer). Keywords are
VERBATIM-STATED (all 9 listed) — so dropping keywords to hit the target is a
DEVIATION, not a lockable spec. The winning subset is EVIDENCE about Campello's
effective counting (what "Uncertainty"/fn14-"subsumed" must mean), to verify
against the paper — never an auto-locked construct.

Vectorized: per scope variant, map CIK->gvkey ONCE, sum to a gvkey×term matrix
G, then evaluate ALL 255 keyword subsets at once via G @ masks.T (no per-subset
loop). Memory-flat: G is ~4k×8; totals ~4k×255 int. Reuses saved per_filing.json
(no re-parse) + step3b3 CCM loader. Read-only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
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
# brexit excluded from subsets: it is 0 everywhere, so adding it never changes a
# total. 8 effective terms -> 2^8-1 = 255 non-empty subsets.
NONBREXIT = ["great britain", "uncertainty", "referendum", "uncertain",
             "united kingdom", "uk", "u.k.", "g.b."]
K = len(NONBREXIT)


def _load_latest() -> list[dict]:
    d = sorted(p for p in OUTBASE.iterdir() if p.is_dir())[-1]
    print(f"per_filing source: {d.name}")
    return json.loads((d / "per_filing.json").read_text(encoding="utf-8"))


def _build(rows: list[dict]) -> pd.DataFrame:
    """Filing-level per-scope per-term counts (+presence). Missing section
    counts = 0 with present=False (lenient uses 0; strict filters present)."""
    out = []
    for r in rows:
        s1 = r["sections"].get("1")
        s7 = r["sections"].get("7")
        c1 = s1["counts"] if s1 else None
        c7 = s7["counts"] if s7 else None
        d = {"cik": r["cik"], "filing_date": r["filing_date"],
             "p_i1": c1 is not None, "p_i7": c7 is not None,
             "p_s17": (c1 is not None and c7 is not None)}
        cw = r["counts_whole"]
        for t in NONBREXIT:
            d[f"whole_{t}"] = cw[t]
            d[f"item1_{t}"] = c1[t] if c1 else 0
            d[f"item7_{t}"] = c7[t] if c7 else 0
            d[f"item1+7_{t}"] = ((c1[t] if c1 else 0) + (c7[t] if c7 else 0))
        out.append(d)
    return pd.DataFrame(out)


def _gvkey_matrix(df: pd.DataFrame, ccm: pd.DataFrame, scope: str,
                  pcol: str | None, strict: bool) -> np.ndarray:
    """Dedupe latest filing/CIK -> CCM time-map -> gvkey-sum. Returns
    (n_gvkey × K) term matrix for the chosen scope."""
    cols = [f"{scope}_{t}" for t in NONBREXIT]
    d = df[["cik", "filing_date", *( [pcol] if pcol else [] ), *cols]].copy()
    if strict and pcol:
        d = d[d[pcol]]
    d = (d.sort_values(["cik", "filing_date"], kind="stable")
           .drop_duplicates("cik", keep="last"))
    mg = d.merge(ccm, on="cik", how="left")
    fd = pd.to_datetime(mg["filing_date"], format="%Y%m%d")
    ok = (fd >= mg["LINKDT"]) & (fd <= mg["LINKENDDT"])
    mp = (mg[ok].sort_values(["cik", "LINKDT"], kind="stable")
              .drop_duplicates("cik", keep="first"))
    g = mp.groupby("gvkey", as_index=False)[cols].sum()
    return g[cols].to_numpy(dtype=np.int32)


def _sweep(G: np.ndarray, masks: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """totals[g,s] = sum_t G[g,t]*mask[s,t]; treated/control per subset."""
    totals = G @ masks.T                       # (n_gvkey × 255)
    treated = (totals > 5).sum(axis=0)
    control = (totals == 0).sum(axis=0)
    return treated, control


def main() -> None:
    rows = _load_latest()
    df = _build(rows)
    ccm = s3._load_ccm()

    masks = ((np.arange(1, 1 << K)[:, None] >> np.arange(K)) & 1).astype(np.int32)
    labels = [",".join(t for t, b in zip(NONBREXIT, m) if b) for m in masks]

    variants = [
        ("whole", None, True),
        ("item1", "p_i1", True), ("item1", "p_i1", False),
        ("item7", "p_i7", True), ("item7", "p_i7", False),
        ("item1+7", "p_s17", True), ("item1+7", "p_s17", False),
    ]
    recs = []
    for scope, pcol, strict in variants:
        G = _gvkey_matrix(df, ccm, scope, pcol, strict)
        tre, con = _sweep(G, masks)
        miss = "n/a" if pcol is None else ("strict" if strict else "lenient")
        rel = np.abs(tre - CAMP_T) / CAMP_T + np.abs(con - CAMP_C) / CAMP_C
        for i in range(len(masks)):
            recs.append((scope, miss, labels[i], int(tre[i]), int(con[i]),
                         int(tre[i] - CAMP_T), int(con[i] - CAMP_C),
                         round(float(rel[i]), 3)))
    rk = pd.DataFrame(recs, columns=["scope", "missing", "keywords", "treated",
                       "control", "dT", "dC", "relL1"]).sort_values("relL1")

    ts = sorted(p for p in OUTBASE.iterdir() if p.is_dir())[-1]
    out_csv = ts / "scope_keyword_sweep_ranked.csv"
    rk.to_csv(out_csv, index=False)

    pd.set_option("display.width", 240)
    pd.set_option("display.max_colwidth", 60)
    print(f"\nTarget: treated={CAMP_T} control={CAMP_C} | "
          f"{len(rk):,} combos ({len(variants)} scopes × {len(masks)} subsets)")
    print("\n=== TOP 25 closest (relL1) ===")
    print(rk.head(25).to_string(index=False))
    print(f"\nfull ranking → {out_csv}")
    print("\nNOTE: keywords are paper-VERBATIM; a winning SUBSET = evidence about "
          "Campello's effective counting, NOT a lockable spec. Verify vs fn14.")


if __name__ == "__main__":
    main()
