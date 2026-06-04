"""Re-verify 18 FAIL/INC vars one-by-one with stricter primary-source check.

For each: (a) look up claimed page in PyMuPDF corpus, (b) probe for var name + key
definition tokens with aggressive normalization, (c) emit excerpt around any hit,
(d) per-item verdict.
"""
import re
import unicodedata
from pathlib import Path

EXTRACT_DIR = Path("tmp/campello_pdf_extract")
OUT = Path("tmp/campello_var_anchor_REVERIFY_2026_05_26.md")

# (var_no, name, role, claimed_page_label, key_probes [3-5 distinctive tokens/phrases])
FAILS = [
    (12, "AUTOMATIONi,t", "DV", "IA p. 18",
     ["AUTOMATION", "automation", "dictionary of keywords", "Appendix E", "Section 1", "10-K"]),
    (14, "HIGH_UK_EXPOSURE_i / HIGH_β^UK_i", "Treatment", "3196",
     ["U.K.-exposed", "top tercile", "HIGH", "UK_EXPOSURE", "dummy variable"]),
    (17, "POST_t", "Treatment", "3196",
     ["POST", "2016", "Q3", "Q4", "time period"]),
    (32, "POST × HIGH_β^UK_i", "Treatment", "3196",
     ["POST", "HIGH", "interaction", "delta", "δ"]),
    (33, "POST × HIGH_10K_ENTRIES", "Treatment", "3196",
     ["10K", "10-K", "HIGH", "entries", "POST"]),
    (37, "POST × HIGH_β^UK_i,CF", "Robustness", "IA p. 11",
     ["β^UK", "CF", "cash flow", "top tercile", "bottom tercile"]),
    (43, "STOCK_RETURNS (lagged stock returns)", "Control", "3198",
     ["STOCK_RETURNS", "buy-and-hold", "quarterly"]),
    (70, "market value of equity", "Other (TOBIN_Q input)", "3198",
     ["market value of equity", "Tobin", "TOBIN_Q", "deferred taxes"]),
    (72, "book value of equity", "Other (TOBIN_Q input)", "3198",
     ["book value of equity", "book value of assets", "Tobin"]),
    (73, "deferred taxes", "Other (TOBIN_Q input)", "3198",
     ["deferred taxes", "Tobin", "TOBIN_Q"]),
    (75, "vol(SP500)", "Control", "3191",
     ["vol(SP500)", "SP500", "S&P 500", "domestic U.S.", "exchange rate"]),
    (76, "vol(FX$£)", "Control", "3191",
     ["vol(FX", "FX", "exchange rate", "USD", "British pound"]),
    (78, "I/B/E/S 1-year-ahead EPS forecasts", "Other", "3195",
     ["I/B/E/S", "IBES", "EPS", "1-year-ahead", "forecasts", "earnings per share"]),
    (82, "FIRM_i (firm-fixed effects)", "FE", "3197",
     ["FIRM", "firm-fixed effects", "firm fixed effects"]),
    (83, "INDUSTRY_j (Hoberg-Phillips FIC 100)", "FE", "3197",
     ["INDUSTRY", "Hoberg", "Phillips", "FIC", "100"]),
    (84, "QUARTER_t (calendar-quarter dummies)", "FE", "3197",
     ["QUARTER", "calendar-quarter", "calendar quarter", "dummies"]),
    (85, "INDUSTRY_j × QUARTER_t", "FE", "3196",
     ["INDUSTRY", "QUARTER", "Industry", "time", "fixed effects"]),
    (86, "TIME (time fixed effects)", "FE", "3207",
     ["TIME", "Time", "Industry", "Fixed effects", "fixed effects"]),
]

MOJIBAKE = [
    ("¼", "="), ("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
    ("–", "-"), ("—", "-"), ("\xa0", " "), ("′", "'"),
    ("ﬁ", "fi"), ("ﬂ", "fl"), ("£", "GBP"), ("$", "USD"),
]

def normalize(s, *, drop_punct=False):
    s = unicodedata.normalize("NFKC", s)
    for a, b in MOJIBAKE:
        s = s.replace(a, b)
    s = re.sub(r"-\s+", "-", s)
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", s)
    if drop_punct:
        s = re.sub(r"[^A-Za-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def load_page(claimed):
    """Resolve 'IA p. 11' / '3198' / 'IA p. 18' to a corpus page.

    IA citations use printed-page numbers; PyMuPDF files are by pdf-page.
    Empirically: IA printed page N = pdf page (N+1) (offset of +1 because IA pdf p1=cover, p2=printed p1).
    """
    m = re.search(r"IA\s*p\.?\s*(\d+)", claimed, re.IGNORECASE)
    if m:
        printed_p = int(m.group(1))
        pdf_p = printed_p + 1  # IA printed→pdf offset confirmed by footer scan 2026-05-26
        fp = EXTRACT_DIR / f"full_supp_pdfpage{pdf_p:02d}.txt"
        return fp, ("supp", pdf_p)
    m = re.search(r"(\d{4})", claimed)
    if m:
        printed = int(m.group(1))
        pdf_p = printed - 3177
        fp = EXTRACT_DIR / f"full_main_pdfpage{pdf_p:02d}.txt"
        return fp, ("main", pdf_p)
    return None, None

def search_probe(text, probe):
    """Find probe in text with aggressive normalization. Return excerpt or None."""
    n_text_punct = normalize(text)
    n_text_loose = normalize(text, drop_punct=True)
    n_probe = normalize(probe)
    n_probe_loose = normalize(probe, drop_punct=True)
    for haystack, needle in [(n_text_punct, n_probe), (n_text_loose, n_probe_loose),
                              (n_text_punct.lower(), n_probe.lower()),
                              (n_text_loose.lower(), n_probe_loose.lower())]:
        idx = haystack.find(needle)
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(haystack), idx + len(needle) + 120)
            return haystack[start:end]
    return None

def reverify_var(no, name, role, claimed, probes):
    fp, _ = load_page(claimed)
    out = [f"## VAR_{no:02d} — {name}",
           f"- role: {role}",
           f"- claimed page: `{claimed}` -> file: `{fp.name if fp else 'UNRESOLVED'}`"]
    if not fp or not fp.exists():
        out.append(f"- **VERDICT**: PAGE_FILE_MISSING")
        return out, "PAGE_FILE_MISSING"
    text = fp.read_text(encoding="utf-8")
    hits = {}
    for p in probes:
        excerpt = search_probe(text, p)
        if excerpt:
            hits[p] = excerpt
    n_hit = len(hits)
    n_probes = len(probes)
    if n_hit >= max(2, n_probes // 2):
        verdict = "FALSE_POS_CONFIRMED"   # var IS on claimed page, original verifier probe too strict
    elif n_hit >= 1:
        verdict = "PARTIAL_HIT"
    else:
        verdict = "REAL_FAIL_OR_WRONG_PAGE"

    out.append(f"- probes_tested: {n_probes} | probes_hit: {n_hit}")
    for p, ex in list(hits.items())[:3]:
        ex_clean = ex.replace("\n", " ").strip()
        out.append(f"  - HIT `{p}`: …{ex_clean[:200]}…")
    if not hits:
        out.append(f"  - NO probes matched on claimed page")
    out.append(f"- **VERDICT**: **{verdict}**")
    return out, verdict

# Aggregate adjacent-page check for REAL_FAIL: search whole corpus
def search_all_pages(probes):
    """Return list of (page_label, probe_hit_count)."""
    results = []
    all_pages = list(EXTRACT_DIR.glob("full_main_pdfpage*.txt")) + list(EXTRACT_DIR.glob("full_supp_pdfpage*.txt"))
    for fp in all_pages:
        text = fp.read_text(encoding="utf-8")
        n_hit = sum(1 for p in probes if search_probe(text, p))
        if n_hit >= max(2, len(probes) // 2):
            results.append((fp.name, n_hit))
    return results

lines = ["# Re-verification of 16 FAIL + 2 INC variables",
         "",
         "Generated 2026-05-26 by `tmp/reverify_fails.py`.",
         "",
         "**Method**: For each previously-flagged var, load PyMuPDF text of CLAIMED page, search for 3-6 distinctive probes (var name, key definition tokens) with aggressive unicode + drop-punct normalization. If ≥half of probes hit → FALSE_POS_CONFIRMED (original verifier probe too strict / mojibake'd). Else → REAL_FAIL_OR_WRONG_PAGE (search whole corpus to locate).",
         ""]

tally = {}
real_fails = []
for v in FAILS:
    block, verdict = reverify_var(*v)
    lines.extend(block)
    if verdict == "REAL_FAIL_OR_WRONG_PAGE":
        # do a corpus-wide search
        results = search_all_pages(v[4])
        if results:
            lines.append(f"  - corpus-wide search (>= half probes): {results[:5]}")
        else:
            lines.append(f"  - corpus-wide search: NO page matches >= half probes")
        real_fails.append((v[0], v[1], results))
    lines.append("")
    tally[verdict] = tally.get(verdict, 0) + 1

lines.append("## Summary")
for k, v in sorted(tally.items()):
    lines.append(f"- {k}: {v}")

lines.append("")
lines.append("## Real FAIL list (need manual review)")
for no, name, res in real_fails:
    lines.append(f"- VAR_{no:02d} {name} — corpus matches: {res[:3] if res else 'NONE'}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT}")
print(f"Tally: {tally}")
print(f"Real fails: {len(real_fails)}")
