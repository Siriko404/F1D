#!/usr/bin/env python3
"""GATE-1 builder: cache call-level STOCK-score (analyst attention to cash LEVEL/liquidity).

STOCK sub-score only (locked lexicon v1: LEVEL + LIQUIDITY, exclusions applied).
DISPOSITION deliberately excluded (its 'dividend' loads on size/maturity -> would
correlate with CashRatio spuriously, not via the channel).

Per call: share of analyst Q&A turns whose text hits a STOCK term (turn binary -> mean).
Memory-safe: one year at a time, keep only call-level aggregates, concat, write once.

Out: tmp/_cash_stock_score_call.parquet  cols [file_name, stock_score, n_qa_turns, n_qa_stock_turns]
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRCDIR = ROOT / "inputs" / "Earnings_Calls_Transcripts"
OUT = ROOT / "tmp" / "_cash_stock_score_call.parquet"
YEARS = range(2002, 2019)

# ---- locked v1 STOCK lexicon (LEVEL + LIQUIDITY) ----
LEVEL = [r"cash holdings?", r"cash balances?", r"cash position", r"cash on hand",
         r"cash on the balance sheet", r"cash reserves?", r"cash and cash equivalents",
         r"cash and equivalents", r"cash and short-?term investments", r"net cash",
         r"cash pile", r"cash hoard", r"cash stockpile", r"war chest", r"dry powder",
         r"excess cash", r"idle cash", r"surplus cash"]
LIQ = [r"liquidity", r"liquid assets", r"short-?term investments", r"marketable securities"]
EXCL = [r"free cash flow", r"operating cash flow", r"cash flow statement", r"cash flows?",
        r"cash conversion cycle", r"cash conversion", r"cash basis", r"cash cow",
        r"cash compensation", r"non-?cash", r"cash register", r"cash crop", r"cash taxes",
        r"cash earnings", r"cash in on"]

def _c(t): return re.compile(r"\b(?:" + "|".join(t) + r")\b")
RX_STOCK = _c(LEVEL + LIQ)
RX_EXCL = _c(EXCL)

def stock_hit(tl: str) -> bool:
    s = RX_EXCL.sub(" __x__ ", tl)
    return bool(RX_STOCK.search(s))

def main():
    parts = []
    for yr in YEARS:
        f = SRCDIR / f"speaker_data_{yr}.parquet"
        if not f.exists():
            print(f"  SKIP {yr} (missing)"); continue
        df = pd.read_parquet(f, columns=["file_name", "speaker_text", "context", "role"])
        a = df[(df["role"] == "Analyst") & (df["context"] == "qa")]
        del df
        hit = a["speaker_text"].astype(str).str.lower().map(stock_hit)
        g = pd.DataFrame({"file_name": a["file_name"].values, "hit": hit.values})
        agg = g.groupby("file_name")["hit"].agg(["mean", "size", "sum"]).reset_index()
        agg.columns = ["file_name", "stock_score", "n_qa_turns", "n_qa_stock_turns"]
        parts.append(agg)
        print(f"  {yr}: {len(a):,} analyst-qa turns | {len(agg):,} calls | "
              f"mean stock_score {agg['stock_score'].mean():.4f} | "
              f"calls w/ any stock {int((agg['n_qa_stock_turns']>0).sum()):,}")
        del a, g, agg, hit
    out = pd.concat(parts, ignore_index=True)
    # file_name should be unique per year; guard against cross-year dups
    dups = int(out["file_name"].duplicated().sum())
    if dups:
        print(f"  WARN {dups} dup file_name across years -> summing")
        out = out.groupby("file_name", as_index=False).agg(
            stock_score=("stock_score", "mean"),
            n_qa_turns=("n_qa_turns", "sum"),
            n_qa_stock_turns=("n_qa_stock_turns", "sum"))
    out.to_parquet(OUT, index=False)
    print(f"\nwrote {OUT}")
    print(f"  total calls: {len(out):,}")
    print(f"  stock_score: mean {out['stock_score'].mean():.4f} | "
          f"median {out['stock_score'].median():.4f} | "
          f"calls>0 {int((out['n_qa_stock_turns']>0).sum()):,} "
          f"({100*(out['n_qa_stock_turns']>0).mean():.1f}%)")

if __name__ == "__main__":
    main()
