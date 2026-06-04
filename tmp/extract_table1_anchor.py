"""
Programmatically extract Table 1 Summary Statistics from Campello 2022 PDF.
Anchor for cross-checking AI-reported stats per `feedback_no_llm_cell_transcription`.

Output: tmp/campello_table1_anchor_2026_05_26.json (machine-readable)
        tmp/campello_table1_anchor_2026_05_26.md   (human-readable table)

Table 1 structure (5 panels × 12 variables × 5 stat columns):
  Panel A: COMPUSTAT Universe
  Panel B: Treated firms (market-based — top tercile of β_i^UK)
  Panel C: Control firms (market-based — bottom tercile of β_i^UK)
  Panel D: Treated firms (textual-search — > 5 Brexit entries in 10-Ks)
  Panel E: Control firms (textual-search — zero entries)
  Stats: mean, SD, median, IQR, N
"""
import re
import json
from pathlib import Path

EXTRACT_DIR = Path("tmp/campello_pdf_extract")
OUT_JSON = Path("tmp/campello_table1_anchor_2026_05_26.json")
OUT_MD = Path("tmp/campello_table1_anchor_2026_05_26.md")

VARIABLES = [
    "INVESTMENT",
    "EMPLOYMENT_GROWTH (Annual)",
    "R&D",
    "DIVESTITURES (100)",
    "CASH",
    "NON_CASH_WORKING_CAPITAL",
    "TOBIN_Q",
    "CASH_FLOW",
    "SIZE (Log Assets)",
    "SALES_GROWTH",
    "CONSENSUS_EARNINGS_FORECAST",
    "STOCK_RETURNS",
]
STATS = ["mean", "SD", "median", "IQR", "N"]
PANELS = ["A", "B", "C", "D", "E"]

# Read pages 21 and 22 (printed 3198 and 3199)
pages_text = []
for p in [21, 22]:
    body = Path(EXTRACT_DIR / f"full_main_pdfpage{p:02d}.txt").read_text(encoding="utf-8")
    body = "\n".join(body.splitlines()[3:])  # strip header
    pages_text.append((p, body))

# Concatenate body lines from both pages (page 22 follows page 21)
all_lines = []
for p, body in pages_text:
    for line in body.splitlines():
        # Strip ASCII control chars (PyMuPDF leaks \x06 etc. from PDF font encodings)
        s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", line).strip()
        if s:
            all_lines.append((p, s))

# Find panel boundaries
panel_starts = {}
for i, (p, s) in enumerate(all_lines):
    m = re.match(r"^Panel ([A-E])\.\s", s)
    if m:
        panel_starts[m.group(1)] = i

# Extract each panel: 12 variables × 5 stats following the panel header
def parse_panel(start_idx, end_idx):
    """Return {var_name: {stat: value}} for one panel."""
    out = {}
    i = start_idx + 1  # skip panel header line
    while i < end_idx:
        p, s = all_lines[i]
        # Match variable name (must be one of VARIABLES)
        matched = None
        for v in VARIABLES:
            if s == v:
                matched = v
                break
        if matched:
            # Next 5 lines should be the 5 stats
            stats = {}
            for j, stat in enumerate(STATS):
                if i + 1 + j >= len(all_lines):
                    break
                _, val = all_lines[i + 1 + j]
                stats[stat] = val
            out[matched] = stats
            i += 1 + len(STATS)
        else:
            i += 1
    return out

# Define panel ranges
panels = {}
sorted_starts = sorted(panel_starts.items(), key=lambda x: x[1])
for k, (panel, idx) in enumerate(sorted_starts):
    end = sorted_starts[k + 1][1] if k + 1 < len(sorted_starts) else len(all_lines)
    panels[panel] = parse_panel(idx, end)

# Validate: each panel should have all 12 variables
for panel, vars_dict in panels.items():
    missing = [v for v in VARIABLES if v not in vars_dict]
    if missing:
        print(f"Panel {panel} missing: {missing}")

# Write JSON
OUT_JSON.write_text(json.dumps(panels, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {OUT_JSON}")

# Write MD
lines = [
    "# Campello 2022 — Table 1 Summary Statistics (PyMuPDF anchor)",
    "",
    "Source: programmatic PyMuPDF extraction from `docs/papers/campello_etal_2022_brexit_jfqa.pdf` PDF pages 21-22 (printed pages 3198-3199).",
    "Per `feedback_no_llm_cell_transcription` — these values are NOT LLM-typed.",
    "",
    "## Panel labels",
    "- **A**: COMPUSTAT Universe (all firms 2010:Q1–2015:Q4)",
    "- **B**: Treated firms — market-based (top tercile of β_i^UK)",
    "- **C**: Control firms — market-based (bottom tercile of β_i^UK)",
    "- **D**: Treated firms — textual-search (>5 Brexit entries in 2015 10-K)",
    "- **E**: Control firms — textual-search (zero entries)",
    "",
    "## Variables × Panels × Stats",
    "",
]
for v in VARIABLES:
    lines.append(f"### {v}")
    lines.append("")
    lines.append("| Panel | Mean | SD | Median | IQR | N |")
    lines.append("|---|---|---|---|---|---|")
    for panel in PANELS:
        stats = panels.get(panel, {}).get(v, {})
        row = [stats.get(s, "—") for s in STATS]
        lines.append(f"| {panel} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |")
    lines.append("")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT_MD}")
