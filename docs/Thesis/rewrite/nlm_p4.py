#!/usr/bin/env python3
"""NLM verification for Section 2.1, P4. Resolver + engine in nlm_common.py.

  python docs/Thesis/rewrite/nlm_p4.py            # capture answers -> ledger
  python docs/Thesis/rewrite/nlm_p4.py --identity # confirm each source id is the right paper
  python docs/Thesis/rewrite/nlm_p4.py --audit
  python docs/Thesis/rewrite/nlm_p4.py --finalize

P4.2 (decomposition) GATES the prose; P4.3 (DWZ price-null) is a NON-GATING record
captured now for 2.3/3 -- it is NOT drafted into P4 (advisor 2026-06-12).
"""
import argparse
import nlm_common as C

PARA = "P4"

PROPS = [
    ("P4.1", "bertrand_schoar2003",
     '"Managing with Style: The Effect of Managers on Firm Policies" by Bertrand and '
     'Schoar (2003, Quarterly Journal of Economics)',
     "what does it conclude about whether individual managers have persistent, distinct "
     "styles that systematically affect the firm policies and outcomes they manage "
     "(manager fixed effects)?"),
    ("P4.2", "dwz2021",
     '"Straight Talkers and Vague Talkers: The Effects of Managerial Style in Earnings '
     'Conference Calls" by Dzielinski, Wagner and Zeckhauser (working paper)',
     "what does it conclude about decomposing managers' uncertainty or clarity language in "
     "earnings conference calls into a persistent manager-specific component (such as a CEO "
     "fixed effect) and a separate time-varying, call-level component?"),
    ("P4.3", "dwz2021",
     '"Straight Talkers and Vague Talkers: The Effects of Managerial Style in Earnings '
     'Conference Calls" by Dzielinski, Wagner and Zeckhauser (working paper)',
     "what does it conclude about whether the time-varying (residual) component of call "
     "uncertainty -- as distinct from the persistent manager component -- is related to "
     "stock-market or stock-price reactions?"),
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
