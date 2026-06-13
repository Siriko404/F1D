#!/usr/bin/env python3
"""NLM verification for Section 2.1, P5. Resolver + engine in nlm_common.py.

  python docs/Thesis/rewrite/nlm_p5.py            # capture answers -> ledger
  python docs/Thesis/rewrite/nlm_p5.py --identity / --audit / --finalize

P5.2 (Bates/Opler) was DROPPED on the scrutiny-channel guardrail -- Harford alone.
"""
import argparse
import nlm_common as C

PARA = "P5"

PROPS = [
    ("P5.1", "harford1999",
     '"Corporate Cash Reserves and Acquisitions" by Harford (1999, Journal of Finance)',
     "what does it conclude about whether firms accumulate cash reserves prior to making "
     "acquisitions, and whether cash-rich firms are more likely to attempt acquisitions?"),
]

PINS = []
VERDICTS = {
    "P5.1": ("SUPPORTED",
             "Harford (1999): firms with cash reserves accumulated above a baseline model "
             "('cash-rich') are more likely to make acquisitions -- verbatim spans n2 ('cash-rich "
             "firms are more likely to make acquisitions'), n3 (cash-rich = reserves above the "
             "model's predictions), n4 ('Cash-richness predicts that a firm will become a bidder'); "
             "located p.1995. DRAFTING CAVEAT: Harford finds this accumulation is free-cash-flow "
             "STOCKPILING, NOT deliberate saving to fund planned value-increasing deals -> P5 must "
             "claim only that an accumulated cash position EXISTS (the war chest), never that firms "
             "deliberately save to fund acquisitions."),
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
