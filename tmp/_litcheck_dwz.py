#!/usr/bin/env python3
"""Find ALL DWZ-variant OpenAlex records (our own measure) + screen their
citers for M&A. The 2017 working paper had only 14 citers -> check for a
higher-cited published record we may have under-screened."""
import sys, time
import pyalex
from pyalex import Works
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pyalex.config.email = "sinasoleimanipour@gmail.com"

DEAL = ['acquisition', 'acquisitions', 'acquirer', 'acquiring', 'merger', 'mergers',
        ' m&a', 'takeover', 'bidder', 'tender offer', 'target firm', 'deal']


def recon(inv):
    if not inv:
        return ''
    pos = {}
    for w, ixs in inv.items():
        for i in ixs:
            pos[i] = w
    return ' '.join(pos[i] for i in sorted(pos))


def sid(u):
    return (u or '').rsplit('/', 1)[-1]


print("=== DWZ-variant records ===")
cand = {}
for q in ['Straight Talkers and Vague Talkers Managerial Style Earnings Conference Calls',
          'Dzielinski Wagner Zeckhauser uncertain managers speech',
          'speech uncertainty CEO earnings call residual style']:
    for w in Works().search(q).get(per_page=8):
        t = (w.get('title') or '').lower()
        if 'talker' in t or 'dzielinski' in str(w.get('authorships', '')).lower() or (
                'uncertain' in t and 'manager' in t):
            cand[sid(w.get('id'))] = (w.get('title'), w.get('publication_year'),
                                      w.get('cited_by_count'))
    time.sleep(0.2)
for wid, (t, y, c) in sorted(cand.items(), key=lambda x: -(x[1][2] or 0)):
    print(f"  [{c}c {y}] {(t or '')[:80]} ({wid})")

# screen citers of EVERY DWZ-variant for deals
print("\n=== deal-mentioning citers across ALL DWZ variants ===")
found = {}
for wid in cand:
    try:
        for page in Works().filter(cites=wid).paginate(per_page=200, n_max=1000):
            for w in page:
                blob = (w.get('title') or '') + ' ' + recon(w.get('abstract_inverted_index'))
                if any(k in blob.lower() for k in DEAL):
                    found[sid(w.get('id'))] = (w.get('title'), w.get('publication_year'),
                                               w.get('cited_by_count'))
            time.sleep(0.1)
    except Exception as e:
        print(f"  ERR {wid}: {e}")
if not found:
    print("  NONE — no DWZ-citing paper mentions M&A/deal terms.")
for wid, (t, y, c) in sorted(found.items(), key=lambda x: -(x[1][2] or 0)):
    print(f"  [{c}c {y}] {(t or '')[:88]}")
