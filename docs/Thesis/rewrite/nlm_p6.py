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

PINS = [
    ("P6.1", "thewissen2024",
     'the working paper by Thewissen and coauthors (2024) on managerial tone around '
     'acquisitions (this single notebook source, ssrn-4900453)',
     "15% in the year preceding the M&A announcement"),
]
VERDICTS = {
    "P6.1": ("SUPPORTED",
             "Thewissen et al. (2024): stock bidders strategically inflate the tone of earnings "
             "press releases before stock-for-stock M&A -- verbatim spans n2 (stock as the form of "
             "payment), n3 (shares issued to purchase the target), n6 (press-release tone increases "
             "by 15% in the year preceding the M&A announcement, span_pin). Nearest-work cell: "
             "managed tone, stock deals, press releases."),
    "P6.2": ("SUPPORTED",
             "Ragozzino & Reuer (2024): strategy-vocabulary volume on earnings calls rises with "
             "M&A activity -- verbatim spans n3 (analysts use ~9% more corporate-strategy terms at "
             "M&A-active firms, p<0.0001) + n4 (executives discuss strategy 7.2% more); located "
             "p.9. Nearest-work cell: managed strategy vocabulary on calls."),
    "P6.3": ("SUPPORTED",
             "Keown & Pinkerton (1981): abnormal pre-announcement price run-up -- verbatim span n3 "
             "('approximately half of the market reaction occurs before the first public "
             "announcement date', p.866). Cited for the PRICE-RUN-UP FACT only; the insider-trading "
             "mechanism is NOT cited (advisor). Splits our LANGUAGE signal from the known PRICE "
             "signal."),
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
