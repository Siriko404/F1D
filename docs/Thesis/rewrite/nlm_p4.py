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
             "DWZ 'Straight Talkers and Vague Talkers' (working paper): the persistent/time-varying "
             "decomposition this paper follows. EVIDENCE BASIS -- DWZ's PDF chunks badly, so NO "
             "single clean cited_text span carries the full decomposition; the basis is CONVERGENT: "
             "(1) the decisive sentence is reproduced VERBATIM and IDENTICALLY across TWO "
             "independent NLM queries + round-trip pinned -- 'Our analysis is the first to "
             "explicitly decompose an important feature of CEO communication into two components: "
             "personal style and the potentially strategic component (the residual), and then to "
             "separately examine their impacts' (p.6 sec 1; see verification.requery); (2) verbatim "
             "cited_text FRAGMENTS n2 ('...we operationalize CEOs' [clarity]') + n4 ('neither does "
             "it differ systematically across industries, firm size') back the persistent "
             "(manager-specific) half. Cited ONLY for the decomposition's EXISTENCE; the "
             "residual-is-where-the-signal-must-live logic is OURS, never DWZ's. NB: DWZ themselves "
             "call the residual 'the potentially strategic component'."),
    "P4.3": ("SUPPORTED",
             "NON-GATING record (for 2.3 defensive + 3 contrast). EVIDENCE BASIS is ANSWER-LEVEL "
             "ONLY -- NO clean cited_text span (DWZ chunks badly; the structured spans are "
             "fragments/off-claim). DWZ report the time-varying residual is NOT significantly "
             "related to price reactions: answer-reproduced 'By contrast, neither UncPreCEO nor "
             "UncResCEO is significantly associated with stock price or volume [reactions]' "
             "(located p.26 + p.29; span_pin p.26 sec 5.2). NOT 'evidence-locked' -- re-verify with "
             "a clean span when 3 drafts the cash-positive CONTRAST. Do NOT draft into P4."),
}

# Targeted re-query (advisor): ONE DWZ call seeking CLEAN spans for the decomposition +
# residual + price-null, which first chunked into fragments. (attach-prop, key, label, question)
REQUERY = ("P4.2", "dwz2021",
           '"Straight Talkers and Vague Talkers: The Effects of Managerial Style in Earnings '
           'Conference Calls" by Dzielinski, Wagner and Zeckhauser (working paper)',
           "Quote verbatim, exactly as printed, the sentence(s) where the paper: (a) states that "
           "it decomposes managers' uncertainty or clarity language into a persistent "
           "manager-specific component and a separate time-varying residual component; and (b) "
           "reports whether that time-varying residual component is or is not significantly "
           "related to stock-price or stock-market reactions. Reproduce each sentence exactly.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--finalize", action="store_true")
    ap.add_argument("--requery", action="store_true")
    ap.add_argument("--verdicts", action="store_true")
    a = ap.parse_args()
    if a.audit:
        C.audit(PARA)
    elif a.identity:
        C.identity(sorted({pk for _, pk, _, _ in PROPS}))
    elif a.requery:
        C.requery(PARA, *REQUERY)
    elif a.verdicts:
        C.record_verdicts(PARA, VERDICTS)
    elif a.finalize:
        C.finalize(PARA, PINS, VERDICTS)
    else:
        if not C.EXE:
            raise SystemExit("notebooklm CLI not found on PATH; run `notebooklm login` first.")
        C.capture(PARA, PROPS)
