#!/usr/bin/env python3
"""REP-2 data feed: run v1 cash lexicon on REAL analyst Q&A turns (2014).
Surface false positives (flagged snippets) + missed cash turns (FN candidates)
+ bare-'cash' cases, so real text drives lexicon curation.
"""
from __future__ import annotations
import random
import re
from pathlib import Path
import pandas as pd

random.seed(42)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "inputs" / "Earnings_Calls_Transcripts" / "speaker_data_2014.parquet"

# ---- v1 lexicon (regex, lowercased, word-boundary) ----
LEVEL = [r"cash holdings?", r"cash balances?", r"cash position", r"cash on hand",
         r"cash on the balance sheet", r"cash reserves?", r"cash and cash equivalents",
         r"cash and equivalents", r"cash and short-?term investments", r"net cash",
         r"cash pile", r"cash hoard", r"cash stockpile", r"war chest", r"dry powder",
         r"excess cash", r"idle cash", r"surplus cash"]
LIQ = [r"liquidity", r"liquid assets", r"short-?term investments", r"marketable securities"]
DEPLOY = [r"dividends?", r"share buybacks?", r"buybacks?", r"share repurchases?",
          r"repurchases?", r"return of capital", r"capital return", r"capital allocation",
          r"capital deployment", r"payout ratio", r"payouts?", r"special dividend",
          r"return cash to shareholders", r"uses? of cash", r"deploy (?:cash|capital)",
          r"cash deployment"]
EXCLUDE = [r"free cash flow", r"operating cash flow", r"cash flow statement",
           r"cash flows?", r"cash conversion cycle", r"cash conversion", r"cash basis",
           r"cash cow", r"cash compensation", r"non-?cash", r"cash register",
           r"cash crop", r"cash taxes", r"cash earnings", r"cash in on"]

def comp(terms): return re.compile(r"\b(?:" + "|".join(terms) + r")\b")
RX_LEVEL, RX_LIQ, RX_DEPLOY = comp(LEVEL), comp(LIQ), comp(DEPLOY)
RX_EXCL = comp(EXCLUDE)
RX_BARECASH = re.compile(r"\bcash\b")
RX_CASHFAM = re.compile(r"\b(?:cash|dividends?|buybacks?|repurchases?|liquidity|payouts?)\b")

def scrub(t): return RX_EXCL.sub(" __x__ ", t)

def analyze(t):
    tl = t.lower()
    sx = scrub(tl)
    lv = RX_LEVEL.findall(sx); lq = RX_LIQ.findall(sx); dp = RX_DEPLOY.findall(sx)
    # bare cash remaining after removing level phrases (which contain 'cash') + excludes
    sx_nolevel = RX_LEVEL.sub(" __l__ ", sx)
    bare = RX_BARECASH.findall(sx_nolevel)
    return {"lv": set(lv), "lq": set(lq), "dp": set(dp), "n_bare": len(bare),
            "flagged": bool(lv or lq or dp), "cashfam": bool(RX_CASHFAM.search(tl))}

def snip(t, n=220):
    t = re.sub(r"\s+", " ", t).strip()
    return (t[:n] + "...") if len(t) > n else t

def safe(s): return str(s).encode("ascii", "replace").decode()

def main():
    df = pd.read_parquet(SRC, columns=["file_name", "speaker_text", "context", "role"])
    a = df[(df["role"] == "Analyst") & (df["context"] == "qa")].copy()
    del df
    print(f"analyst Q&A turns 2014: {len(a):,}")

    res = a["speaker_text"].astype(str).map(analyze)
    a["flagged"] = [r["flagged"] for r in res]
    a["cashfam"] = [r["cashfam"] for r in res]
    a["nbare"] = [r["n_bare"] for r in res]
    a["lv"] = [r["lv"] for r in res]; a["lq"] = [r["lq"] for r in res]; a["dp"] = [r["dp"] for r in res]

    nf = int(a["flagged"].sum()); ncf = int(a["cashfam"].sum())
    print(f"flagged (LEVEL/LIQ/DEPLOY hit): {nf:,} ({100*nf/len(a):.1f}%)")
    print(f"contains cash-family token   : {ncf:,} ({100*ncf/len(a):.1f}%)")
    bybuck = {"LEVEL": int(a['lv'].map(bool).sum()), "LIQ": int(a['lq'].map(bool).sum()),
              "DEPLOY": int(a['dp'].map(bool).sum())}
    print("by bucket:", bybuck)
    # term frequency
    from collections import Counter
    cL, cQ, cD = Counter(), Counter(), Counter()
    for s in a["lv"]: cL.update(s)
    for s in a["lq"]: cQ.update(s)
    for s in a["dp"]: cD.update(s)
    print("LEVEL terms :", cL.most_common(20))
    print("LIQ terms   :", cQ.most_common(8))
    print("DEPLOY terms:", cD.most_common(20))

    flagged = a[a["flagged"]]
    fn = a[(~a["flagged"]) & (a["cashfam"])]          # cash-family but NOT flagged = FN candidates
    bareonly = a[(~a["flagged"]) & (a["nbare"] > 0)]  # bare cash only, no bucket hit

    print(f"\n===== 22 FLAGGED snippets (false-positive audit) =====")
    for _, r in flagged.sample(min(22, len(flagged))).iterrows():
        b = ",".join(k for k, v in [("L", r["lv"]), ("Q", r["lq"]), ("D", r["dp"])] if v)
        print(safe(f"[{b}] {snip(r['speaker_text'])}"))

    print(f"\n===== 22 CASH-FAMILY-but-UNFLAGGED (false-negative audit), n={len(fn):,} =====")
    for _, r in fn.sample(min(22, len(fn))).iterrows():
        print(safe(f"- {snip(r['speaker_text'])}"))

    print(f"\n===== 12 BARE-CASH-only (no bucket), n={len(bareonly):,} =====")
    for _, r in bareonly.sample(min(12, len(bareonly))).iterrows():
        print(safe(f"- {snip(r['speaker_text'])}"))

if __name__ == "__main__":
    main()
