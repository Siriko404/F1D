#!/usr/bin/env python3
"""Print abstracts of the CLOSEST candidate priors for hand-screening.

Our phenomenon = ACQUIRER's earnings-call linguistic uncertainty rises
ANTICIPATING an undisclosed deal, resolves at announcement. Screen the
citation-net hits whose titles touch (earnings/conference call OR disclosure
tone) x (M&A/acquir/merger/corporate development).
"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

hits = json.loads(Path('tmp/litcheck_citenet_results.json').read_text(encoding='utf-8'))

KEYS = ['earnings call', 'conference call', 'disclosure tone', 'corporate development',
        'acquisition plans', 'voluntary disclosure', 'tone management', 'acquiring firm',
        'information disclosures in earnings']


def close(t):
    t = t.lower()
    has_chan = any(k in t for k in ['earnings call', 'conference call', 'disclosure tone',
                                     'voluntary disclosure', 'tone management', 'press release',
                                     'information disclosure'])
    has_deal = any(k in t for k in ['m&a', 'merger', 'acquisi', 'acquir', 'takeover',
                                     'corporate development', 'deal'])
    return has_chan and has_deal


sel = [w for w in hits if close(w['title'])]
print(f"{len(sel)} closest candidates (channel x deal in title):\n")
for w in sorted(sel, key=lambda x: -x['cited']):
    ab = w['abstract'].strip() or '(no abstract in OpenAlex)'
    print(f"{'='*78}")
    print(f"[{w['cited']}c {w['year']}] {w['title']}")
    print(f"venue: {w['venue']} | doi: {w['doi']} | via: {', '.join(sorted(set(w['via'])))}")
    print(f"ABSTRACT: {ab[:900]}")
    print()
