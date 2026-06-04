"""Per-keyword decomposition of our textual Brexit count (whole-10-K scope).

Campello (verbatim) parses the WHOLE 2015 10-K, 9 terms, >5=treated / 0=control,
and gets 807 treated / 433 control. Our whole-filing build (step3b) gets
3037 / 278 — 3.8x too many treated, too FEW zero-mention controls. Since scope
matches the paper, the over-count must be in WHICH terms fire.

This re-streams the 2015 10-K zip and counts EACH of the 9 terms separately per
filing (same regexes/word-boundaries as step3b3), then reports, per term:
  - total occurrences (sum over filings)
  - mean per filing
  - # filings where THAT TERM ALONE exceeds 5 (would treat on its own)
  - # filings with >=1 of that term  (=> can't be a zero-mention control)

Reveals whether generic "uncertainty"/"uncertain"/"uk" dominate. Filing-level
(no CCM map needed to see the driver). Read-only.
"""
from __future__ import annotations

import re
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "inputs" / "10-X_C_2015_10Konly.zip"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FNAME = re.compile(
    r"\d{4}/QTR\d/(\d{8})_([A-Z0-9-]+)_edgar_data_(\d+)_([A-Za-z0-9-]+)\.txt")

# Each of the 9 terms as its own regex (word-boundary, matching step3b3 logic).
TERMS = {
    "brexit":         re.compile(r"\bbrexit\b", re.I),
    "great britain":  re.compile(r"\bgreat britain\b", re.I),
    "uncertainty":    re.compile(r"\buncertainty\b", re.I),
    "referendum":     re.compile(r"\breferendum\b", re.I),
    "uncertain":      re.compile(r"\buncertain\b", re.I),
    "united kingdom": re.compile(r"\bunited kingdom\b", re.I),
    "uk":             re.compile(r"\buk\b", re.I),
    "u.k.":           re.compile(r"(?<![A-Za-z])u\.k\.(?![A-Za-z])", re.I),
    "g.b.":           re.compile(r"(?<![A-Za-z])g\.b\.(?![A-Za-z])", re.I),
}


def main() -> None:
    t0 = time.time()
    tot = defaultdict(int)            # term -> total occurrences
    alone_gt5 = defaultdict(int)      # term -> #filings where term alone >5
    present = defaultdict(int)        # term -> #filings with >=1
    n_filings = 0
    # also: how many filings are zero across ALL 9, and zero if we DROP a term
    zero_all = 0
    zero_drop = defaultdict(int)      # term -> #filings that become zero if term removed

    with zipfile.ZipFile(ZIP, "r") as zf:
        infos = zf.infolist()
        print(f"zip entries: {len(infos):,}")
        for i, info in enumerate(infos, 1):
            if info.is_dir() or info.file_size == 0:
                continue
            if not FNAME.match(info.filename):
                continue
            try:
                with zf.open(info, "r") as f:
                    text = f.read().decode("utf-8", errors="replace")
            except Exception:
                continue
            n_filings += 1
            counts = {term: len(rx.findall(text)) for term, rx in TERMS.items()}
            del text
            total = sum(counts.values())
            for term, c in counts.items():
                if c:
                    tot[term] += c
                    present[term] += 1
                    if c > 5:
                        alone_gt5[term] += 1
            if total == 0:
                zero_all += 1
            else:
                for term, c in counts.items():
                    if total - c == 0:        # removing this term -> zero
                        zero_drop[term] += 1
            if i % 1500 == 0:
                print(f"  …{i:,}/{len(infos):,}  ({time.time()-t0:.0f}s)")

    print(f"\nparsed {n_filings:,} filings  ({time.time()-t0:.0f}s)")
    print(f"filings with ZERO of all 9 terms (control candidates): {zero_all:,}"
          f"   [Campello control = 433]\n")
    rows = []
    for term in TERMS:
        rows.append((term, tot[term], tot[term] / max(n_filings, 1),
                     present[term], alone_gt5[term], zero_drop[term]))
    df = pd.DataFrame(rows, columns=["term", "total_occ", "mean/filing",
                                     "filings>=1", "alone>5", "sole_term"])
    df = df.sort_values("total_occ", ascending=False)
    print(df.to_string(index=False,
          formatters={"total_occ": "{:,}".format,
                      "mean/filing": "{:.2f}".format,
                      "filings>=1": "{:,}".format,
                      "alone>5": "{:,}".format,
                      "sole_term": "{:,}".format}))
    print("\nLegend:")
    print("  total_occ   = total matches of that term across all filings")
    print("  alone>5     = #filings where THIS TERM ALONE exceeds the >5 cutoff")
    print("  filings>=1  = #filings containing the term (>=1) -> blocks zero-control")
    print("  sole_term   = #filings whose ENTIRE Brexit count is just this term")
    print("\nRead: which terms drive treated>5? Which terms block the zero-")
    print("      mention control bucket (Campello has 433; we have far fewer)?")


if __name__ == "__main__":
    main()
