#!/usr/bin/env python3
"""Fetch abstracts for the no-abstract closest candidates via Crossref."""
import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DOIS = {
    'Implications of M&A for info disclosures in earnings calls (2023 LRP)': '10.1016/j.lrp.2023.102393',
    'Impact of M&A on Acquiring Firm Voluntary Disclosure (2025)': '10.2139/ssrn.5016980',
    'Manipulating Disclosure Tone: Acquiring Firms Stock-for-Stock (2024)': '10.2139/ssrn.4900453',
    'Voluntary Disclosure w/ Uncertainty of Investor Response: M&A calls (2021)': '10.2139/ssrn.3837666',
    'Is There Information in Corporate Acquisition Plans? (2024)': None,  # find via title if needed
}

import re
def strip(h):
    return re.sub('<[^>]+>', '', h or '').strip()

for name, doi in DOIS.items():
    if not doi:
        continue
    url = f"https://api.crossref.org/works/{doi}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'litcheck/1.0 (mailto:sinasoleimanipour@gmail.com)'})
        with urllib.request.urlopen(req, timeout=20) as r:
            m = json.load(r)['message']
        ab = strip(m.get('abstract', ''))
        print(f"{'='*76}\n{name}\n  DOI {doi} | {m.get('container-title',[''])[0]}")
        print(f"  ABSTRACT: {ab[:1100] if ab else '(no abstract in Crossref either)'}\n")
    except Exception as e:
        print(f"{'='*76}\n{name}\n  DOI {doi} -> FETCH FAILED: {e}\n")
