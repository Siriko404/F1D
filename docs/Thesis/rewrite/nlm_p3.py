#!/usr/bin/env python3
"""NLM verification for Section 2.1, P3. Resolver + engine in nlm_common.py.

  python docs/Thesis/rewrite/nlm_p3.py            # capture answers -> ledger
  python docs/Thesis/rewrite/nlm_p3.py --identity # confirm the source id is the right paper
  python docs/Thesis/rewrite/nlm_p3.py --audit    # substring-audit located vs verbatim spans
  python docs/Thesis/rewrite/nlm_p3.py --finalize # pin decisive spans + record verdicts
"""
import argparse
import nlm_common as C

PARA = "P3"

# (prop_id, paper_key in C.SOURCES, paper label named in the query, atomic non-leading question)
PROPS = [
    ("P3.1", "hollander2010",
     '"Does Silence Speak? An Empirical Analysis of Disclosure Choices During Conference '
     'Calls" by Hollander, Pronk and Roelofsen (2010, Journal of Accounting Research)',
     "what does it conclude about whether managers strategically manage their disclosures "
     "during conference calls -- including choosing not to answer questions -- and whether "
     "such silence or non-answers are informative to investors?"),
]

PINS = []        # (prop_id, paper_key, paper_label, decisive_verbatim_sentence) -- fill after --audit
VERDICTS = {}    # prop_id: (verdict, note) -- fill after reviewing captured spans

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--finalize", action="store_true")
    a = ap.parse_args()
    if a.audit:
        C.audit(PARA)
    elif a.identity:
        C.identity(sorted({pk for _, pk, _, _ in PROPS}))
    elif a.finalize:
        C.finalize(PARA, PINS, VERDICTS)
    else:
        if not C.EXE:
            raise SystemExit("notebooklm CLI not found on PATH; run `notebooklm login` first.")
        C.capture(PARA, PROPS)
