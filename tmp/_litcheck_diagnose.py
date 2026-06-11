#!/usr/bin/env python3
"""Validate the OpenAlex sweep before trusting Tier1=0.

Checks: (a) abstract coverage (missing abstracts blind the classifier);
(b) recall of KNOWN call-language papers (DWZ/Bushee/Mayew/Larcker/LM);
(c) title-only re-tier (catches relevant papers with missing abstracts);
(d) deal x language bucket WITHOUT requiring 'call' (M&A-tone priors anywhere).
"""
import json
from pathlib import Path

works = json.loads(Path('tmp/litcheck_openalex_results.json').read_text(encoding='utf-8'))
n = len(works)
empty = sum(1 for w in works if not w['abstract'].strip())
print(f"abstract coverage: {n-empty}/{n} have abstracts  ({empty} EMPTY = {100*empty//n}% blind to classifier)")

DEAL = ['acquisition', 'acquisitions', 'acquirer', 'acquiring', 'merger', 'mergers',
        'm&a', 'takeover', 'takeovers', 'bidder', 'tender offer', 'target firm']
CALL = ['earnings call', 'conference call', 'earnings conference', 'quarterly call',
        'earnings-call', 'conference-call', 'analyst call']
LANG = ['uncertainty', 'tone', 'linguistic', 'obfuscation', 'readability', 'fog',
        'hedging', 'sentiment', 'textual', 'speech', 'vague', 'wording', 'narrative', 'language']


def has(t, terms):
    t = t.lower()
    return any(k in t for k in terms)


# (b) recall of known anchors anywhere in title/abstract
ANCHORS = ['dzielinski', 'zeckhauser', 'bushee', 'mayew', 'venkatachalam', 'larcker',
           'zakolyukina', 'loughran', 'mcdonald', 'speech uncertain', 'vocal cue',
           'deceptive', 'linguistic complexity']
print("\n--- recall of KNOWN call-language papers (match in title/abstract) ---")
for a in ANCHORS:
    hits = [w for w in works if a in (w['title'] + ' ' + w['abstract']).lower()]
    if hits:
        h = max(hits, key=lambda x: x['cited'])
        print(f"  FOUND '{a}': {len(hits)}x | top: [{h['cited']}c {h['year']}] {h['title'][:70]}")
    else:
        print(f"  MISSING '{a}'")

# (c) TITLE-ONLY re-tier — catches missing-abstract relevant papers
print("\n--- TITLE-ONLY screen (abstract-independent) ---")
t_dcl = [w for w in works if has(w['title'], DEAL) and has(w['title'], CALL) and has(w['title'], LANG)]
t_dc = [w for w in works if has(w['title'], DEAL) and has(w['title'], CALL)]
t_dl = [w for w in works if has(w['title'], DEAL) and has(w['title'], LANG)]
print(f"title deal+call+lang: {len(t_dcl)} | title deal+call: {len(t_dc)} | title deal+lang(no-call-req): {len(t_dl)}")

# (d) deal x language bucket (full text/abstract) WITHOUT requiring call — M&A-tone priors anywhere
dl = sorted([w for w in works if has(w['title'] + ' ' + w['abstract'], DEAL)
             and has(w['title'] + ' ' + w['abstract'], LANG)], key=lambda x: -x['cited'])
print(f"\n--- deal x language (abstract, call NOT required) : {len(dl)} works ; top 18 ---")
for w in dl[:18]:
    flag = 'CALL' if has(w['title'] + ' ' + w['abstract'], CALL) else '    '
    print(f"  [{flag}][{w['cited']:>5}c {w['year']}] {w['title'][:92]} | {w['venue'][:30]}")

# show the 20 Tier-3 (call+lang) titles to eyeball recall of the call-text lit
t3 = sorted([w for w in works if w['tier'] == 3], key=lambda x: -x['cited'])
print(f"\n--- TIER 3 call+language ({len(t3)}) — the call-text lit we DID surface ---")
for w in t3:
    print(f"  [{w['cited']:>5}c {w['year']}] {w['title'][:92]} | {w['venue'][:30]}")
