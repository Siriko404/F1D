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

PINS = [
    ("P4.1", "bertrand_schoar2003",
     '"Managing with Style: The Effect of Managers on Firm Policies" by Bertrand and '
     'Schoar (2003, Quarterly Journal of Economics)',
     "a manager's residual in his last job and his residual in his first job"),
    ("P4.2", "dwz2021",
     '"Straight Talkers and Vague Talkers: The Effects of Managerial Style in Earnings '
     'Conference Calls" by Dzielinski, Wagner and Zeckhauser (working paper)',
     "the first to explicitly decompose"),
    ("P4.3", "dwz2021",
     '"Straight Talkers and Vague Talkers: The Effects of Managerial Style in Earnings '
     'Conference Calls" by Dzielinski, Wagner and Zeckhauser (working paper)',
     "neither UncPreCEO nor UncResCEO is significantly"),
]
VERDICTS = {
    "P4.1": ("SUPPORTED",
             "Bertrand & Schoar (2003): managers carry persistent fixed-effect styles across the "
             "firm policies they manage -- verbatim span n4 (a manager's residual in his last job "
             "vs his first job is positive and statistically significant for ALL policy variables, "
             "t-stats 4-16) + n2 (the investment / financial / organizational policy variables). "
             "PREMISE ONLY (persistent components are real, in POLICIES); NOT the language "
             "decomposition (DWZ's), NOT a residual-is-signal claim."),
    "P4.2": ("SUPPORTED",
             "DWZ 'Straight Talkers and Vague Talkers' (working paper): CEO uncertainty/clarity "
             "language decomposes into a persistent manager-specific component ('CEO clarity', a "
             "CEO fixed effect, distinct from firm-level uncertainty / industry / size -- verbatim "
             "fragments n2/n3/n4) and a time-varying call-level residual; decisive decomposition "
             "sentence span_pinned ('the first to explicitly decompose'). Cited ONLY for the "
             "decomposition's existence -- the residual-is-where-the-signal-must-live logic is "
             "OURS, never attributed to DWZ."),
    "P4.3": ("SUPPORTED",
             "NON-GATING record (for 2.3 defensive + 3 contrast). DWZ: the time-varying residual "
             "component is NOT significantly related to price reactions -- span_pin 'neither "
             "UncPreCEO nor UncResCEO is significantly [associated]' (p.26). This is the null our "
             "cash-positive result CONTRASTS with; do NOT draft it into P4."),
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
