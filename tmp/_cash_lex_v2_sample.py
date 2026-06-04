#!/usr/bin/env python3
"""REP-3: v1 vs v2 matchers + stratified gold sample for non-circular P/R.
Prints snippets (ID + text only, NO predictions) for blind labeling.
Stores preds+strata+weights to JSON for scoring after labels assigned.
"""
from __future__ import annotations
import json, random, re
from pathlib import Path
import pandas as pd

random.seed(7)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "inputs" / "Earnings_Calls_Transcripts" / "speaker_data_2014.parquet"
OUTJSON = ROOT / "tmp" / "_cash_lex_gold_meta.json"

# ---------- v1 (rep-1) ----------
v1_LEVEL = [r"cash holdings?", r"cash balances?", r"cash position", r"cash on hand",
            r"cash on the balance sheet", r"cash reserves?", r"cash and cash equivalents",
            r"cash and equivalents", r"cash and short-?term investments", r"net cash",
            r"cash pile", r"cash hoard", r"cash stockpile", r"war chest", r"dry powder",
            r"excess cash", r"idle cash", r"surplus cash"]
v1_LIQ = [r"liquidity", r"liquid assets", r"short-?term investments", r"marketable securities"]
v1_DEPLOY = [r"dividends?", r"share buybacks?", r"buybacks?", r"share repurchases?",
             r"repurchases?", r"return of capital", r"capital return", r"capital allocation",
             r"capital deployment", r"payout ratio", r"payouts?", r"special dividend",
             r"return cash to shareholders", r"uses? of cash", r"deploy (?:cash|capital)",
             r"cash deployment"]
v1_EXCL = [r"free cash flow", r"operating cash flow", r"cash flow statement", r"cash flows?",
           r"cash conversion cycle", r"cash conversion", r"cash basis", r"cash cow",
           r"cash compensation", r"non-?cash", r"cash register", r"cash crop", r"cash taxes",
           r"cash earnings", r"cash in on"]
def _c(t): return re.compile(r"\b(?:" + "|".join(t) + r")\b")
RX1L, RX1Q, RX1D, RX1X = _c(v1_LEVEL), _c(v1_LIQ), _c(v1_DEPLOY), _c(v1_EXCL)
def v1_flag(tl):
    s = RX1X.sub(" __x__ ", tl)
    return bool(RX1L.search(s) or RX1Q.search(s) or RX1D.search(s))

# ---------- v2 (rep-2: split, FCF-conditional, bare-cash window) ----------
STOCK_P = v1_LEVEL + v1_LIQ
DISP_P  = [r"dividends?", r"share buybacks?", r"buybacks?", r"share repurchases?",
           r"repurchases?", r"return of capital", r"capital return", r"capital allocation",
           r"capital deployment", r"payout ratio", r"payouts?", r"special dividend",
           r"return cash to shareholders", r"uses? of cash", r"deploy (?:cash|capital)",
           r"cash deployment", r"return cash"]
# excludes EXCEPT cash-flow family (handled conditionally)
HARD_EXCL = [r"cash basis", r"cash cow", r"cash compensation", r"non-?cash", r"cash register",
             r"cash crop", r"cash taxes", r"cash earnings", r"cash in on", r"cash costs?"]
CF = [r"free cash flows?", r"operating cash flows?", r"cash flow statement", r"cash flows?",
      r"cash conversion cycle", r"cash conversion"]
DISPVERB = r"(?:deploy\w*|us(?:e|ing|es)|return\w*|allocat\w+|distribut\w+|give\s+back|giving\s+back|put\b.{0,15}\bto work)"
STOCK_CUE = r"(?:balance sheet|on hand|sitting|sit on|flush|pile|hoard|generat\w+|of cash|in cash|do with|put .{0,12}to work)"
RX2S, RX2D, RX2HX = _c(STOCK_P), _c(DISP_P), _c(HARD_EXCL)
RX_CF = _c(CF)
RX_DV = re.compile(DISPVERB)
RX_BARE = re.compile(r"\bcash\b")
RX_BARE_STOCK = re.compile(STOCK_CUE + r"\W+(?:\w+\W+){0,3}?cash\b|\bcash\b\W+(?:\w+\W+){0,3}?" + STOCK_CUE)
RX_BARE_DISP  = re.compile(DISPVERB + r"\W+(?:\w+\W+){0,3}?cash\b|\bcash\b\W+(?:\w+\W+){0,3}?" + DISPVERB)

def v2_eval(tl):
    s = RX2HX.sub(" __x__ ", tl)
    # cash-flow family: keep as DISPOSITION only if a disposition verb is within ~6 tokens
    disp_cf = False
    out = []
    last = 0
    for m in RX_CF.finditer(s):
        a, b = m.start(), m.end()
        ctx = s[max(0, a-40):b+40]
        if RX_DV.search(ctx):
            disp_cf = True
            out.append(s[last:a]); out.append(" __cfdisp__ "); last = b
        else:
            out.append(s[last:a]); out.append(" __x__ "); last = b
    out.append(s[last:])
    s = "".join(out)
    stock = bool(RX2S.search(s)) or bool(RX_BARE_STOCK.search(s))
    disp = bool(RX2D.search(s)) or disp_cf or bool(RX_BARE_DISP.search(s))
    return stock, disp

def snip(t, n=300):
    t = re.sub(r"\s+", " ", str(t)).strip()
    return (t[:n] + "...") if len(t) > n else t
def safe(s): return str(s).encode("ascii", "replace").decode()

def main():
    df = pd.read_parquet(SRC, columns=["file_name", "speaker_text", "context", "role"])
    a = df[(df["role"] == "Analyst") & (df["context"] == "qa")].reset_index(drop=True)
    del df
    txt = a["speaker_text"].astype(str)
    tl = txt.str.lower()
    cashfam = tl.str.contains(r"\b(?:cash|dividends?|buybacks?|repurchases?|liquidity|payouts?)\b", regex=True)
    v1 = tl.map(v1_flag)
    v2 = tl.map(lambda x: any(v2_eval(x)))
    n = len(a)
    n_flag = int(v2.sum()); n_uf_cf = int(((~v2) & cashfam).sum()); n_uf_nc = int(((~v2) & ~cashfam).sum())
    print(f"2014 analyst-qa: {n:,} | v2-flag {n_flag:,} | v2-unflag&cashfam {n_uf_cf:,} | v2-unflag&no-cashfam {n_uf_nc:,}")
    print(f"v1-flag {int(v1.sum()):,}")

    idx_flag = list(a.index[v2])
    idx_ufcf = list(a.index[(~v2) & cashfam])
    idx_ufnc = list(a.index[(~v2) & ~cashfam])
    random.shuffle(idx_flag); random.shuffle(idx_ufcf); random.shuffle(idx_ufnc)
    samp = {"flag": idx_flag[:30], "ufcf": idx_ufcf[:45], "ufnc": idx_ufnc[:15]}
    weights = {"flag": n_flag, "ufcf": n_uf_cf, "ufnc": n_uf_nc}

    meta = {"weights": weights, "rows": {}}
    print("\n########## LABEL THESE (1=attention to cash holdings/disposition, 0=not) ##########")
    gid = 0
    for stratum, ids in samp.items():
        print(f"\n----- stratum {stratum} -----")
        for i in ids:
            gid += 1
            meta["rows"][str(gid)] = {"stratum": stratum,
                                      "v1": int(bool(v1.iloc[i])), "v2": int(bool(v2.iloc[i]))}
            print(safe(f"#{gid}: {snip(txt.iloc[i])}"))
    OUTJSON.write_text(json.dumps(meta, indent=0), encoding="utf-8")
    print(f"\nwrote {OUTJSON}  ({gid} rows)")

if __name__ == "__main__":
    main()
