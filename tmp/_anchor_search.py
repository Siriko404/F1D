#!/usr/bin/env python3
"""Strict literature-anchor DISCOVERY search across the whole F1D NotebookLM
notebook (63e3b970...), for the §II the angle mechanism + cash/stock placebo.

We are NOT verifying a known paper here (that was nlm.py, source-scoped). We are
DISCOVERING whether ANY source in the notebook cleanly anchors three gaps:

  A  legal gag        : pending deal = MNPI, selective disclosure barred
  B  talk-but-hedge   : gagged manager fields Q&A -> vaguer/hedged/uncertain
  C  cash != stock    : payment method flips PRE-ANNOUNCEMENT disclosure behavior
                        (must explain the stock NULL, not only the cash positive)
                        split into 3 angles: direct / leakage / behavior

Prompt design (Sina's NLM rules, adapted for discovery):
  1. ONE prompt per gap chunk
  2. SELF-CONTAINED (notebooklm `clear` between calls)
  3. exploratory / solution-free / unbiased -> explicitly allows answer "NONE"
  4. (inverted) we do NOT -s scope; we ask NLM to NAME the source + quote verbatim
     so discovery can surface any of the ~60 papers.

Strictness is applied when READING results, not in the prompt wording.
Writes incrementally to tmp/anchor_search_results.json for Claude to read.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOTEBOOK = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
OUT = Path("tmp/anchor_search_results.json")

NLM = shutil.which("notebooklm")
if not NLM:
    print("ERROR: notebooklm CLI not on PATH")
    sys.exit(1)

QUERIES = {
    "A_legal_gag": (
        "Across all sources in this notebook, is there a paper that establishes "
        "-- for public firms -- that an unannounced or pending merger or "
        "acquisition constitutes material non-public information whose selective "
        "disclosure by the firm's managers is legally prohibited (for example "
        "under insider-trading law, Regulation Fair Disclosure, or merger "
        "confidentiality)? If yes, name the specific source and quote the exact "
        "sentence(s) that establish this. If no source in this notebook "
        "establishes it, answer exactly: NONE."
    ),
    "B_talk_but_hedge": (
        "Across all sources in this notebook, is there a paper providing evidence "
        "that corporate managers who hold material information they are not "
        "permitted to disclose respond to analysts' questions during earnings "
        "conference calls with more vague, more hedged, less specific, or more "
        "uncertain language -- as opposed to simply declining to answer? If yes, "
        "name the specific source and quote the exact sentence(s). If no source "
        "establishes this, answer exactly: NONE."
    ),
    "C_direct_payment_disclosure": (
        "Across all sources in this notebook, is there a paper showing that the "
        "method of payment in an acquisition (cash versus stock/equity) is "
        "associated with a difference in the ACQUIRER's voluntary disclosure or "
        "communication behavior in the period BEFORE the deal is announced? I am "
        "asking specifically about pre-announcement disclosure behavior, not "
        "announcement-period stock returns. If yes, name the source and quote the "
        "exact sentence(s). If no source establishes this, answer exactly: NONE."
    ),
    "C_leakage_stock_earlier": (
        "Across all sources in this notebook, is there a paper establishing that "
        "stock-financed (equity) acquisitions become publicly known or disclosed "
        "EARLIER than cash-financed acquisitions -- for instance because equity "
        "deals require registration statements (Form S-4), shareholder votes, or "
        "other regulatory filings -- so that less non-public deal information "
        "remains by the time of a pre-announcement earnings call? If yes, name "
        "the source and quote the exact sentence(s). If no source establishes "
        "this, answer exactly: NONE."
    ),
    "C_behavior_stock_manages_up": (
        "Across all sources in this notebook, is there a paper showing that "
        "acquirers paying with STOCK actively increase or manage their voluntary "
        "disclosure or communication before announcing the deal (for example to "
        "support their share price), whereas cash acquirers do not? If yes, name "
        "the source and quote the exact sentence(s). If no source establishes "
        "this, answer exactly: NONE."
    ),
}


def run(args, timeout=240):
    return subprocess.run(
        [NLM, *args], capture_output=True, text=True, timeout=timeout,
        encoding="utf-8", errors="replace",
    )


def ask(query):
    # self-contained: reset conversation context first
    run(["clear", "-n", NOTEBOOK])
    r = run(["ask", "-n", NOTEBOOK, "--json", query])
    out = r.stdout or ""
    i = out.find("{")
    if i < 0:
        return {"_error": "no JSON in output", "_raw": out[:800], "_stderr": (r.stderr or "")[:400]}
    try:
        return json.loads(out[i:])
    except json.JSONDecodeError as e:
        return {"_error": f"json decode: {e}", "_raw": out[i:i + 800]}


results = {}
if OUT.exists():
    try:
        results = json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        results = {}

for key, q in QUERIES.items():
    print(f"\n=== {key} ===")
    ans = ask(q)
    results[key] = {"query": q, "result": ans}
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    a = ans.get("answer", ans.get("_error", ""))
    print(a[:500] if isinstance(a, str) else a)
    refs = ans.get("references", [])
    print(f"   [{len(refs)} references]")

print(f"\nDONE -> {OUT}")
