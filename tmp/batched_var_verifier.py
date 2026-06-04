"""
Programmatic batched verifier for Claude-web's 88-variable inventory.

For each variable (5 at a time), check against PyMuPDF anchor:
  1. definition_verbatim: does it exist somewhere in the paper?
  2. primary_definition.page: does the verbatim text actually appear on the claimed page?
  3. reported_summary_stats: do cell values match the Table 1 anchor (for the 12 Table 1 vars)?

Usage:
  python tmp/batched_var_verifier.py 1   # batch 1 (VAR_01 to VAR_05)
  python tmp/batched_var_verifier.py 2   # batch 2 (VAR_06 to VAR_10)
  ...
  python tmp/batched_var_verifier.py all # all 18 batches

Output: tmp/campello_var_anchor_check_batch_{NN}.md
"""
import re
import sys
import json
import unicodedata
from pathlib import Path

INVENTORY = Path("tmp/campello_claudeweb_88vars_2026_05_26.md")
TABLE1_ANCHOR = Path("tmp/campello_table1_anchor_2026_05_26.json")
EXTRACT_DIR = Path("tmp/campello_pdf_extract")
OUT_DIR = Path("tmp")
BATCH_SIZE = 5

MOJIBAKE = [
    ("¼", "="), ("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
    ("–", "-"), ("—", "-"), ("\xa0", " "), ("′", "'"),
    ("ﬁ", "fi"), ("ﬂ", "fl"),
]

def normalize(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in MOJIBAKE:
        s = s.replace(a, b)
    # bridge soft-hyphen line wraps
    s = re.sub(r"-\s+", "-", s)
    # strip control chars
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", s)
    # collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()

def normalize_aggressive(s):
    """Drop all whitespace for missing-space-at-wrap matching."""
    return re.sub(r"\s+", "", normalize(s))

# Load corpus: full main paper pages 1-45 + supplement 1-19, indexed by printed page
print_to_pdf_main = lambda printed: printed - 3178 + 1  # main paper: printed 3178 = pdf p1
def load_corpus():
    pages = {}  # key: ("main"|"supp", pdf_page_int) -> normalized text
    page_to_printed = {}
    for fp in sorted(EXTRACT_DIR.glob("full_main_pdfpage*.txt")):
        m = re.search(r"full_main_pdfpage(\d+)\.txt", fp.name)
        if not m: continue
        pdf_page = int(m.group(1))
        text = fp.read_text(encoding="utf-8")
        body = "\n".join(text.splitlines()[3:])
        pages[("main", pdf_page)] = (normalize(body), normalize_aggressive(body), body)
        page_to_printed[("main", pdf_page)] = pdf_page + 3177
    for fp in sorted(EXTRACT_DIR.glob("full_supp_pdfpage*.txt")):
        m = re.search(r"full_supp_pdfpage(\d+)\.txt", fp.name)
        if not m: continue
        pdf_page = int(m.group(1))
        text = fp.read_text(encoding="utf-8")
        body = "\n".join(text.splitlines()[3:])
        pages[("supp", pdf_page)] = (normalize(body), normalize_aggressive(body), body)
        page_to_printed[("supp", pdf_page)] = pdf_page  # IA uses internal page numbering
    return pages, page_to_printed

corpus, page_to_printed = load_corpus()

# Load Table 1 anchor
table1_anchor = json.loads(TABLE1_ANCHOR.read_text(encoding="utf-8"))
def norm_var_name(s):
    s = s.upper()
    s = re.sub(r"[\s_\-()]+", "", s)
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s
table1_by_norm = {}
for panel, vars_dict in table1_anchor.items():
    for var, stats in vars_dict.items():
        n = norm_var_name(var)
        table1_by_norm.setdefault(n, {})[panel] = (stats, var)

# Parse VAR blocks from inventory
text = INVENTORY.read_text(encoding="utf-8")
VAR_RE = re.compile(
    r"VAR_(\d+):\s*\n(.*?)(?=\nVAR_\d+:|\nTOTAL_VARIABLES|\nACCESS_LIMITATIONS|\Z)",
    re.DOTALL,
)
def parse_field(body, key, multiline=False):
    if multiline:
        m = re.search(rf"\b{re.escape(key)}:\s*\"?(.+?)(?=\n\s*[a-zA-Z_]+:|\Z)", body, re.DOTALL)
    else:
        m = re.search(rf"\b{re.escape(key)}:\s*\"?([^\n\"]+?)\"?\s*\n", body)
    return m.group(1).strip().strip('"') if m else ""

def parse_stats(body):
    m = re.search(r"reported_summary_stats:\s*\n(.*?)(?=\n\s*uncertainty:|\n\s*data_source|\nVAR_|\Z)",
                  body, re.DOTALL)
    if not m: return {}
    out = {}
    for k in ["found_in", "N", "mean", "sd", "SD", "median", "p25", "p75", "IQR", "other_stats", "panel"]:
        mm = re.search(rf"\b{re.escape(k)}:\s*\"?([^\n\"]+?)\"?\s*\n", m.group(1))
        if mm: out[k.lower()] = mm.group(1).strip()
    return out

variables = []
for m in VAR_RE.finditer(text):
    no = int(m.group(1))
    body = m.group(2)
    page = parse_field(body, "page")
    sect = parse_field(body, "section_or_table")
    name = parse_field(body, "name_as_printed")
    role = parse_field(body, "role")
    defin = parse_field(body, "definition_verbatim", multiline=True)
    formula = parse_field(body, "data_source_or_formula", multiline=True)
    unit = parse_field(body, "unit_or_transformation")
    stats = parse_stats(body)
    variables.append({
        "no": no, "name": name, "role": role,
        "page": page, "section_or_table": sect,
        "defin": defin[:400], "formula": formula[:400],
        "unit": unit, "stats": stats,
    })

# Verifier checks
def check_def_verbatim(v):
    """Does the definition_verbatim text exist in the paper?"""
    d = v["defin"]
    if not d or d.upper().startswith("NOT DEFINED"):
        return {"status": "N/A", "detail": "no definition text to check"}
    # Take a distinctive prose substring: drop math + take first 40-60 chars
    probe = normalize(d)
    if len(probe) < 30:
        return {"status": "SHORT_PROBE", "detail": probe}
    # Try a 60-char probe and an 80-char probe
    for probe_len in [80, 60, 40]:
        sub = probe[:probe_len]
        for key, (norm_text, aggr_text, _) in corpus.items():
            if sub in norm_text or sub in aggr_text:
                src, pdf_p = key
                printed_p = page_to_printed[key]
                return {"status": "FOUND", "where": f"{src} pdf p{pdf_p} (printed p{printed_p})",
                        "src": src, "pdf_page": pdf_p, "printed_page": printed_p}
    return {"status": "NOT_FOUND", "detail": "definition probe not located in main+supp corpus"}

def check_page(v, def_result):
    """Does the claimed page match where definition was found?"""
    claimed = v["page"]
    if def_result["status"] != "FOUND":
        return {"status": "N/A", "detail": "no found page to compare"}
    if not claimed or claimed.lower() in ("n/a", ""):
        return {"status": "N/A", "detail": "no claimed page"}
    # claimed may be "3198", "3198-3199", "IA p. 7", etc.
    nums = re.findall(r"\d{2,5}", claimed)
    found_p = def_result["printed_page"]
    if any(int(n) == found_p for n in nums):
        return {"status": "MATCH", "detail": f"claimed={claimed}, found=p{found_p}"}
    # Off-by-one tolerance (PyMuPDF landscape table page drops, soft-page-boundary)
    for n in nums:
        if abs(int(n) - found_p) <= 1:
            return {"status": "MATCH_±1", "detail": f"claimed={claimed}, found=p{found_p}"}
    return {"status": "MISMATCH", "detail": f"claimed={claimed}, found=p{found_p}"}

def check_table1_stats(v):
    """If variable is in Table 1, do the reported stats match the anchor?"""
    stats = v["stats"]
    found_in = stats.get("found_in", "").lower()
    if "table 1" not in found_in:
        return {"status": "NOT_TABLE_1", "detail": f"found_in={stats.get('found_in')}"}
    n = norm_var_name(v["name"])
    matched_n = None
    if n in table1_by_norm:
        matched_n = n
    else:
        # substring-tolerant match (inventory may say "EMPLOYMENT_GROWTH", anchor "EMPLOYMENT_GROWTH (Annual)")
        for anchor_n in table1_by_norm:
            if (n and (n in anchor_n or anchor_n in n)) and abs(len(n) - len(anchor_n)) <= 15:
                matched_n = anchor_n
                break
    if not matched_n:
        return {"status": "NAME_MISMATCH", "detail": f"normalized={n}, no anchor variant matched"}
    n = matched_n
    # Compare against Panel A by default
    anchor_pa, anchor_name = table1_by_norm[n].get("A", (None, None))
    if not anchor_pa:
        return {"status": "PANEL_A_MISSING", "detail": ""}
    def strip_panel(x):
        return re.sub(r"^Panel\s+[A-E]:\s*", "", str(x or ""), flags=re.IGNORECASE).replace(",", "").strip()
    cells = []
    keys = [("mean", "mean"), ("sd", "SD"), ("median", "median"), ("iqr", "IQR"), ("n", "N")]
    for r, a in keys:
        rep = strip_panel(stats.get(r))
        anc = strip_panel(anchor_pa.get(a))
        if not rep or not anc:
            continue
        cells.append((a, rep, anc, rep == anc))
    n_match = sum(1 for _, _, _, ok in cells if ok)
    n_total = len(cells)
    if n_total == 0:
        return {"status": "NO_PANEL_A", "detail": "no Panel A cells in inventory"}
    if n_match == n_total:
        return {"status": "PANEL_A_MATCH", "detail": f"{n_match}/{n_total} cells", "cells": cells}
    return {"status": "PANEL_A_MISMATCH", "detail": f"{n_match}/{n_total} cells match",
            "cells": cells, "mismatches": [(a, r, an) for a, r, an, ok in cells if not ok]}

def verdict(def_r, page_r, stat_r):
    if def_r["status"] == "NOT_FOUND":
        return "FAIL (definition not in paper)"
    if page_r["status"] == "MISMATCH":
        return "FAIL (page mismatch)"
    if stat_r["status"] == "PANEL_A_MISMATCH":
        return "FAIL (stat cells)"
    if def_r["status"] == "FOUND" and page_r["status"] in ("MATCH", "MATCH_±1"):
        if stat_r["status"] in ("NOT_TABLE_1", "PANEL_A_MATCH", "N/A"):
            return "PASS"
    return "INCONCLUSIVE"

def run_batch(batch_no):
    start = (batch_no - 1) * BATCH_SIZE + 1
    end = min(start + BATCH_SIZE - 1, 88)
    out = OUT_DIR / f"campello_var_anchor_check_batch_{batch_no:02d}.md"
    lines = [
        f"# Variable Anchor Check — Batch {batch_no} (VAR_{start:02d} – VAR_{end:02d})",
        "",
        f"Generated: 2026-05-26 by `tmp/batched_var_verifier.py {batch_no}`",
        f"Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).",
        "",
        "Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?",
        "",
    ]
    summary = {"PASS": 0, "FAIL": 0, "INCONCLUSIVE": 0, "OTHER": 0}
    for v in variables:
        if not (start <= v["no"] <= end):
            continue
        def_r = check_def_verbatim(v)
        page_r = check_page(v, def_r)
        stat_r = check_table1_stats(v)
        vd = verdict(def_r, page_r, stat_r)
        if "PASS" in vd: summary["PASS"] += 1
        elif "FAIL" in vd: summary["FAIL"] += 1
        elif "INCONCLUSIVE" in vd: summary["INCONCLUSIVE"] += 1
        else: summary["OTHER"] += 1
        lines.append(f"## VAR_{v['no']:02d} — {v['name']}")
        lines.append(f"- **role**: {v['role']}")
        lines.append(f"- **claimed**: §{v['section_or_table']}, page {v['page']}")
        lines.append(f"- **definition (first 200ch)**: {v['defin'][:200]}…")
        lines.append(f"- **CHECK 1 — definition in paper**: `{def_r['status']}` — {def_r.get('detail', def_r.get('where', ''))}")
        lines.append(f"- **CHECK 2 — page match**: `{page_r['status']}` — {page_r.get('detail','')}")
        lines.append(f"- **CHECK 3 — Table 1 stats**: `{stat_r['status']}` — {stat_r.get('detail','')}")
        if stat_r.get("mismatches"):
            for a, r, an in stat_r["mismatches"]:
                lines.append(f"    - {a}: inventory={r}, anchor={an}")
        elif stat_r.get("cells"):
            for a, r, an, ok in stat_r["cells"]:
                mark = "✓" if ok else "✗"
                lines.append(f"    - {mark} {a}: inventory={r}, anchor={an}")
        lines.append(f"- **VERDICT**: **{vd}**")
        lines.append("")
    lines += [
        "## Batch summary",
        f"- PASS: {summary['PASS']}",
        f"- FAIL: {summary['FAIL']}",
        f"- INCONCLUSIVE: {summary['INCONCLUSIVE']}",
        f"- OTHER: {summary['OTHER']}",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    msg = f"Batch {batch_no} ({start}-{end}): PASS={summary['PASS']} FAIL={summary['FAIL']} INC={summary['INCONCLUSIVE']} -> {out.name}"
    print(msg)
    return summary

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    if arg == "all":
        n_batches = (88 + BATCH_SIZE - 1) // BATCH_SIZE
        for b in range(1, n_batches + 1):
            run_batch(b)
    else:
        run_batch(int(arg))
