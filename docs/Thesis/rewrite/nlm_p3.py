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

PINS = [
    ("P3.1", "hollander2010",
     '"Does Silence Speak? An Empirical Analysis of Disclosure Choices During Conference '
     'Calls" by Hollander, Pronk and Roelofsen (2010, Journal of Accounting Research)',
     "the results of our study suggest that silence speaks"),
]
VERDICTS = {
    "P3.1": ("SUPPORTED",
             "Hollander, Pronk & Roelofsen (2010): managers strategically manage call disclosure "
             "-- they decline/withhold requested information in ~6 of 10 calls (verbatim span n2: "
             "'managers withhold information from the public in approximately 6 out of 10 calls, "
             "with an average of two unanswered queries per call') -- and such silence is "
             "informative ('silence speaks', span_pin). PREMISE ONLY: the UP sign of our measure "
             "is H1 (one-tailed, tested), never from Hollander."),
}

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
