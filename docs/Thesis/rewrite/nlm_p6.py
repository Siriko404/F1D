#!/usr/bin/env python3
"""NLM verification for Section 2.1, P6. Resolver + engine in nlm_common.py.

  python docs/Thesis/rewrite/nlm_p6.py            # capture answers -> ledger
  python docs/Thesis/rewrite/nlm_p6.py --identity / --audit / --finalize

P6.4 (the 'to our knowledge' gap) is framing-nonverifiable -> NOT queried here.
P6.3 (Keown): cite the pre-announcement price run-up FACT only, NOT the insider-trading
mechanism (advisor 2026-06-12).
"""
import argparse
import nlm_common as C

PARA = "P6"

PROPS = [
    ("P6.1", "thewissen2024",
     'the working paper by Thewissen and coauthors (2024) on managerial tone around '
     'acquisitions (this single notebook source, ssrn-4900453)',
     "what does it study regarding firms' management of tone or language in earnings press "
     "releases around stock-for-stock acquisitions, and what does it find?"),
    ("P6.2", "ragozzino2024",
     'the paper by Ragozzino and Reuer (2024) on strategy vocabulary in conference calls '
     'around deal activity (this single notebook source, S0024630123001000)',
     "what does it study regarding the volume or use of strategy-related vocabulary on "
     "earnings conference calls around firms' acquisition or deal activity?"),
    ("P6.3", "keown1981",
     '"Merger Announcements and Insider Trading Activity: An Empirical Investigation" by '
     'Keown and Pinkerton (1981, Journal of Finance)',
     "what does it conclude about whether abnormal stock-price movements or returns occur "
     "before the public announcement of a merger (a pre-announcement price run-up)?"),
]

PINS = []
VERDICTS = {}

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
