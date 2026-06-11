#!/usr/bin/env python3
"""Query the f1d NotebookLM for the two MUST-cite papers; write answers to JSON.

Uses the `notebooklm` CLI (auth already saved via `notebooklm login`). Each
query is ISOLATED two ways:
  - `notebooklm clear`                     -> resets conversation (self-contained,
                                              no carry-over between questions)
  - `notebooklm ask -n <nb> -s <src> --json` -> scopes to ONE paper's source id
                                              (hard guarantee vs cross-paper mix)
                                              and returns structured JSON.

8 atomic, exploratory questions x 2 papers = 16 calls, CORE infos first.
Answers + citations are written INCREMENTALLY to tmp/nlm_verification.json, so a
partial run (quota / interrupt) keeps everything completed so far.

Run:  python tmp/nlm.py          # all 16, core-first
      python tmp/nlm.py --core   # core 5 x 2 = 10 only
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).with_name("nlm_verification.json")
NOTEBOOK = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
EXE = shutil.which("notebooklm")

SOURCES = {
    "thewissen_2024": "731d56ed-c42a-4280-84eb-eec23f8be9b3",        # ssrn-4900453.pdf
    "ragozzino_reuer_2024": "f84c6cd2-59a1-4879-a053-b798687fd03c",  # 1-s2.0-S0024630...
}
TITLES = {
    "thewissen_2024": "Thewissen et al. 2024 (stock-for-stock tone; SSRN 4900453)",
    "ragozzino_reuer_2024": "Ragozzino & Reuer 2024 (M&A earnings-call disclosures; LRP)",
}
CORE = {"measure", "language_dimension", "channel", "payment_type", "timing"}

INFOS = [
    ("measure",
     "what text-based or linguistic measures does it construct or use, and for "
     "each one, what dictionary, word list, or methodology defines it? Quote the "
     "sentence(s) that define each measure."),
    ("language_dimension",
     "does it characterize the disclosure language along any dimension of how "
     "confident, certain, vague, hedged, or uncertain it is? If so, how is that "
     "captured and what is it called? If the words 'residual', 'abnormal', or "
     "'expected' appear in relation to the text measure, what exactly is being "
     "decomposed or subtracted?"),
    ("channel",
     "what specific disclosure documents or communications are the unit of "
     "textual analysis (for example conference-call transcripts, earnings press "
     "releases, regulatory filings, analyst Q&A, management guidance)? Are any "
     "such channels explicitly included in or excluded from the sample?"),
    ("payment_type",
     "how does it treat the method of payment in the acquisitions it studies "
     "(cash, stock, or mixed)? Which payment types are in the sample, are results "
     "reported separately by payment type, and what does it report specifically "
     "for cash-financed deals?"),
    ("timing",
     "over what time window relative to the merger announcement is the disclosure "
     "measured (before, at, or after the announcement), and how does it describe "
     "the timing of the behavior it documents?"),
    ("mechanism",
     "what economic motive, incentive, or mechanism does it propose to explain "
     "the disclosure behavior it documents?"),
    ("design",
     "what is the empirical strategy and identification approach, and what "
     "comparison or control groups, if any, are used?"),
    ("scope",
     "what does it say about the boundaries of its contribution -- what it does "
     "not examine, does not measure, or does not claim, and what it leaves to "
     "future work?"),
]

PREFIX = "Reading only this paper, "


def cli(args, timeout):
    return subprocess.run([EXE, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def ask(source: str, question: str) -> dict:
    try:
        cli(["clear"], timeout=60)
    except Exception:
        pass  # clear is best-effort; a stale context is non-fatal
    try:
        r = cli(["ask", "-n", NOTEBOOK, "-s", source, "--json", PREFIX + question],
                timeout=360)
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    out = r.stdout or ""
    i = out.find("{")
    if i < 0:
        return {"error": "no JSON in output", "raw": (out + (r.stderr or ""))[:600]}
    try:
        j = json.loads(out[i:])
    except Exception as e:
        return {"error": f"json parse: {e}", "raw": out[i:i + 600]}
    refs = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text")}
            for x in j.get("references", [])]
    return {"answer": j.get("answer", ""), "references": refs}


def main() -> None:
    if not EXE:
        sys.exit("ERROR: `notebooklm` CLI not found on PATH. Run `notebooklm login` first.")
    core_only = "--core" in sys.argv
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}

    tasks = [(ik, q, pk) for ik, q in INFOS for pk in SOURCES
             if not core_only or ik in CORE]
    total = len(tasks)
    for n, (ikey, q, pkey) in enumerate(tasks, 1):
        print(f"[{n}/{total}] {pkey} / {ikey} ...", flush=True)
        res = ask(SOURCES[pkey], q)
        node = data.setdefault(pkey, {"title": TITLES[pkey], "infos": {}})
        node["infos"][ikey] = {"question": q, **res}
        OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"        -> {'OK' if 'answer' in res else 'ERR ' + str(res.get('error'))}",
              flush=True)
    print(f"\n[nlm.py] done -> {OUT}")


if __name__ == "__main__":
    main()
