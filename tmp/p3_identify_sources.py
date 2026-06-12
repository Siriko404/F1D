#!/usr/bin/env python3
"""P3 pre-flight — title-anchored source identification (NLM-only, scripted, durable).

Maps each thesis bibitem to its NotebookLM source_id WITHOUT ever anchoring on a
filename (per AUDIT_PROTOCOL E5). For each known bibitem TITLE we ask the notebook
to locate that title and read the source_id back from NLM's own citation. This is
the single UNSCOPED step in P3 (you cannot `-s` a source you have not yet found);
every later attribution query is single-source scoped (E3/E4).

Deterministic + resumable: writes tmp/p3_source_identification.json after every
paper, so a partial/quota-limited run loses nothing. Re-running skips papers that
already resolved to a source_id.

Run:  python tmp/p3_identify_sources.py            # all unresolved
      python tmp/p3_identify_sources.py --only dwz # one key (proof / re-check)
      python tmp/p3_identify_sources.py --force     # re-ask even if resolved
"""
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).with_name("p3_source_identification.json")
NOTEBOOK = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
EXE = shutil.which("notebooklm")

# Exact titles copied verbatim from the thesis bibitems (thesis_draft.tex L199-236).
# 13 bibitem keys = the full P3 citation set. (thewissen/ragozzino source_ids are
# already known from tmp/nlm.py but are re-confirmed here by title for edition-pin.)
TITLES = {
    "baker2016":     "Measuring economic policy uncertainty",
    "bushee2018":    "Linguistic complexity in firm disclosures: Obfuscation or information?",
    "davis2016":     "An index of global economic policy uncertainty",
    "dwz":           "Straight talkers and vague talkers: The effects of managerial style in earnings conference calls",
    "everhart2025":  "The impact of M&A transactions on acquiring firm guidance",
    "gokkaya2025":   "Is there information in corporate acquisition plans?",
    "hassan2020":    "Firm-level political risk: Measurement and effects",
    "hoberg2010":    "Product market synergies and competition in mergers and acquisitions: A text-based analysis",
    "hoberg2016":    "Text-based network industries and endogenous product differentiation",
    "lerman2026":    "Earnings conference calls and the SEC comment letter process",
    "lm2011":        "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks",
    "ragozzino2024": "Implications of mergers and acquisitions for information disclosures in earnings calls",
    "thewissen2024": "Manipulating disclosure tone: Understanding acquiring firms' strategies in stock-for-stock mergers and acquisitions",
}


def cli(args, timeout):
    return subprocess.run([EXE, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def identify(title: str) -> dict:
    """One atomic, title-anchored, UNSCOPED lookup. Returns matched source_ids."""
    try:
        cli(["clear"], timeout=60)
    except Exception:
        pass
    q = (f'In this notebook, locate the source document whose title is: "{title}". '
         f'Quote that source’s title exactly as it appears in the document, and nothing else.')
    try:
        r = cli(["ask", "-n", NOTEBOOK, "--json", q], timeout=360)
    except subprocess.TimeoutExpired:
        return {"query": q, "error": "timeout"}
    out = r.stdout or ""
    i = out.find("{")
    if i < 0:
        return {"query": q, "error": "no JSON", "raw": (out + (r.stderr or ""))[:400]}
    try:
        j = json.loads(out[i:])
    except Exception as e:
        return {"query": q, "error": f"json parse: {e}", "raw": out[i:i + 400]}
    # Collect cited source_ids in citation order; the most-cited is the match.
    cites = [(x.get("source_id"), x.get("cited_text", "")) for x in j.get("references", [])
             if x.get("source_id")]
    counts = Counter(sid for sid, _ in cites)
    matches = []
    for sid, _n in counts.most_common():
        snippet = next((t for s, t in cites if s == sid), "")
        matches.append({"source_id": sid, "n_cites": _n, "cited_text": snippet[:200]})
    locked = matches[0]["source_id"] if len(matches) == 1 else None  # unambiguous only
    return {"query": q, "answer": j.get("answer", "")[:500], "matches": matches,
            "locked_source_id": locked}


def main() -> None:
    if not EXE:
        sys.exit("ERROR: `notebooklm` CLI not found on PATH. Run `notebooklm login` first.")
    args = sys.argv[1:]
    force = "--force" in args
    only = args[args.index("--only") + 1] if "--only" in args else None

    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    keys = [only] if only else list(TITLES)
    for n, key in enumerate(keys, 1):
        if key not in TITLES:
            print(f"  ?? unknown key {key}"); continue
        if not force and data.get(key, {}).get("locked_source_id"):
            print(f"[{n}/{len(keys)}] {key} -> already resolved, skip"); continue
        print(f"[{n}/{len(keys)}] identifying {key} ...", flush=True)
        res = identify(TITLES[key])
        data[key] = {"bibitem_title": TITLES[key], **res}
        OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tag = res.get("locked_source_id") or ("AMBIGUOUS:" + str(len(res.get("matches", []))) + " matches"
                                              if res.get("matches") else res.get("error", "NO MATCH"))
        print(f"        -> {tag}", flush=True)
    print(f"\n[p3_identify_sources] done -> {OUT}")


if __name__ == "__main__":
    main()
