"""
Variables Round 1 cross-check.

Inputs:
- tmp/process_prompt_03_variable_inventory_2026_05_26.md (NLM + Claude-web)
- tmp/campello_table1_anchor_2026_05_26.json (PyMuPDF anchor Table 1)

For each AI-reported variable:
  - Match against Table 1 anchor by variable name (normalized)
  - Compare reported mean/SD/median/IQR/N to anchor Panel A (the universe stats)
  - Classify: ANCHOR_MATCH | ANCHOR_DRIFT | NO_ANCHOR (not in Table 1)
  - Cross-check NLM vs Claude-web on overlapping variables

Output: tmp/campello_variable_crosscheck_v1_2026_05_26.md
"""
import re
import json
from pathlib import Path

PROMPT = Path("tmp/process_prompt_03_variable_inventory_2026_05_26.md")
ANCHOR = Path("tmp/campello_table1_anchor_2026_05_26.json")
OUT = Path("tmp/campello_variable_crosscheck_v1_2026_05_26.md")

# Anchor lookup: normalize variable names for matching
def norm_var(s):
    s = s.upper().strip()
    s = re.sub(r"[\s_\-]+", "", s)
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s

anchor_data = json.loads(ANCHOR.read_text(encoding="utf-8"))
# Flatten anchor by variable: {normalized_name: {original_name, panels: {A: {...}}}}
anchor_index = {}
for panel, vars_dict in anchor_data.items():
    for var_name, stats in vars_dict.items():
        n = norm_var(var_name)
        if n not in anchor_index:
            anchor_index[n] = {"original_name": var_name, "panels": {}}
        anchor_index[n]["panels"][panel] = stats

# Parse VAR blocks from the response file
text = PROMPT.read_text(encoding="utf-8")
chunks = re.split(r"/{5,}\s*\n", text)
nlm_text = cw_text = ""
for i, c in enumerate(chunks):
    s = c.strip()
    if s == "NLM" and i + 1 < len(chunks):
        nlm_text = chunks[i + 1]
    elif re.match(r"^claude\s*web\s*$", s, re.IGNORECASE) and i + 1 < len(chunks):
        cw_text = chunks[i + 1]

# Pull VAR_NN blocks with their fields. AI YAML-ish format; permissive parser.
VAR_RE = re.compile(
    r"VAR_(\d+):\s*\n(.*?)(?=\nVAR_\d+:|\nTOTAL_VARIABLES|\n/{3,}|\nACCESS_LIMITATIONS|\Z)",
    re.DOTALL,
)

def get_field(body, key):
    m = re.search(rf"\b{key}:\s*\"?(.+?)\"?\s*(?=\n\s*[a-zA-Z_]+:|\Z)", body)
    return m.group(1).strip() if m else ""

def get_stats_block(body):
    """Extract reported_summary_stats subblock."""
    m = re.search(r"reported_summary_stats:\s*\n(.*?)(?=\n\s*uncertainty:|\n\s*data_source|\Z)",
                  body, re.DOTALL)
    if not m:
        return {}
    block = m.group(1)
    out = {}
    for key in ["found_in", "N", "mean", "sd", "SD", "median", "p25", "p75", "IQR", "other_stats", "panel"]:
        mm = re.search(rf"\b{key}:\s*\"?([^\n\"]+?)\"?\s*\n", block)
        if mm:
            out[key.lower()] = mm.group(1).strip()
    return out

def parse_blocks(section_text, ai_label):
    out = []
    for m in VAR_RE.finditer(section_text):
        no = int(m.group(1))
        body = m.group(2)
        name = re.search(r"name_as_printed:\s*\"?([^\n\"]+?)\"?\s*\n", body)
        role = re.search(r"role:\s*\"?([^\n\"]+?)\"?\s*\n", body)
        defin = re.search(r"definition_verbatim:\s*\"?(.+?)(?=\n\s*[a-zA-Z_]+:)", body, re.DOTALL)
        stats = get_stats_block(body)
        out.append({
            "ai": ai_label,
            "var_no": no,
            "name": (name.group(1) if name else "").strip(),
            "role": (role.group(1) if role else "").strip(),
            "defin": (defin.group(1).strip() if defin else "")[:300],
            "stats": stats,
        })
    return out

nlm_vars = parse_blocks(nlm_text, "NLM")
cw_vars = parse_blocks(cw_text, "ClaudeWeb")
print(f"NLM vars parsed: {len(nlm_vars)}")
print(f"Claude-web vars parsed: {len(cw_vars)}")

# Build normalized lookup
def by_name(blocks):
    out = {}
    for b in blocks:
        n = norm_var(b["name"])
        if n:
            out.setdefault(n, []).append(b)
    return out

nlm_by = by_name(nlm_vars)
cw_by = by_name(cw_vars)

# Union of all variable names (normalized)
all_names = set(nlm_by.keys()) | set(cw_by.keys()) | set(anchor_index.keys())

# Per-variable cross-check
def compare_stats(reported, anchor_stats):
    """Return (match_count, total_compared, mismatches list).

    Compare normalized: strip 'Panel X:' prefixes, commas, lowercase.
    """
    def norm_val(x):
        if x is None:
            return ""
        s = str(x).strip()
        # Strip "Panel X:" prefix that Claude-web adds
        s = re.sub(r"^Panel\s+[A-E]:\s*", "", s, flags=re.IGNORECASE)
        s = s.replace(",", "").lower().strip()
        return s
    keys = [("mean", "mean"), ("sd", "SD"), ("median", "median"), ("iqr", "IQR"), ("n", "N")]
    match = 0
    total = 0
    mismatches = []
    for r_key, a_key in keys:
        r_val = norm_val(reported.get(r_key))
        a_val = norm_val(anchor_stats.get(a_key))
        if not r_val or not a_val:
            continue
        total += 1
        if r_val == a_val:
            match += 1
        else:
            mismatches.append(f"{a_key}: AI={reported.get(r_key)} | anchor={anchor_stats.get(a_key)}")
    return match, total, mismatches

# Render report
lines = [
    "# Campello Variables — Round 1 Cross-Check",
    "",
    f"Generated: 2026-05-26 by `tmp/var_crosscheck_v1.py`",
    f"Sources: NLM ({len(nlm_vars)} vars) + Claude-web ({len(cw_vars)} vars) responses in `process_prompt_03_variable_inventory_2026_05_26.md`",
    f"Anchor: programmatic PyMuPDF extraction of Table 1 (5 panels × 12 variables × 5 stats = 300 cells) in `campello_table1_anchor_2026_05_26.json`",
    "",
    "## Summary",
    "",
    f"- Variables in **both AIs**: {len(set(nlm_by.keys()) & set(cw_by.keys()))}",
    f"- Variables only in **Claude-web**: {len(set(cw_by.keys()) - set(nlm_by.keys()))}",
    f"- Variables only in **NLM**: {len(set(nlm_by.keys()) - set(cw_by.keys()))}",
    f"- Variables with **Table 1 anchor**: {len(anchor_index)} (the 12 Table 1 variables)",
    "",
    "## Table 1 anchor cross-check (the 12 variables with Panel A reported moments)",
    "",
    "For each Table 1 variable, compare AI's reported_summary_stats vs PyMuPDF anchor Panel A (universe).",
    "",
    "| Variable | NLM (anchor match) | Claude-web (anchor match) | Anchor (Panel A, mean/SD/median/IQR/N) |",
    "|---|---|---|---|",
]
for n, info in sorted(anchor_index.items()):
    a_pa = info["panels"].get("A", {})
    anchor_str = f"{a_pa.get('mean','?')}/{a_pa.get('SD','?')}/{a_pa.get('median','?')}/{a_pa.get('IQR','?')}/{a_pa.get('N','?')}"
    def cell(ai_blocks):
        if not ai_blocks:
            return "_(not found)_"
        b = ai_blocks[0]
        m, t, mis = compare_stats(b["stats"], a_pa)
        status = "✓ all match" if t > 0 and m == t else (f"⚠ {m}/{t} match" if t > 0 else "_(no stats reported)_")
        return f"{status} (VAR_{b['var_no']:02d})"
    lines.append(f"| **{info['original_name']}** | {cell(nlm_by.get(n))} | {cell(cw_by.get(n))} | {anchor_str} |")

lines += [
    "",
    "## Table 1 anchor — detailed AI stat comparison",
    "",
]
for n, info in sorted(anchor_index.items()):
    a_pa = info["panels"].get("A", {})
    lines.append(f"### {info['original_name']}")
    lines.append(f"  Anchor Panel A: mean={a_pa.get('mean')}, SD={a_pa.get('SD')}, median={a_pa.get('median')}, IQR={a_pa.get('IQR')}, N={a_pa.get('N')}")
    for ai_label, ai_by in [("NLM", nlm_by), ("Claude-web", cw_by)]:
        blocks = ai_by.get(n, [])
        if not blocks:
            lines.append(f"  - {ai_label}: _(variable not in inventory)_")
            continue
        b = blocks[0]
        m, t, mis = compare_stats(b["stats"], a_pa)
        if t == 0:
            lines.append(f"  - {ai_label} VAR_{b['var_no']:02d}: _(no stats reported)_  | found_in: {b['stats'].get('found_in','?')}")
        elif m == t:
            lines.append(f"  - {ai_label} VAR_{b['var_no']:02d}: ✓ {m}/{t} cell match  | found_in: {b['stats'].get('found_in','?')}")
        else:
            lines.append(f"  - {ai_label} VAR_{b['var_no']:02d}: ⚠ {m}/{t} cell match  | found_in: {b['stats'].get('found_in','?')}")
            for ms in mis:
                lines.append(f"      - mismatch: {ms}")
    lines.append("")

# Variables in CW but NOT in anchor and NOT in NLM
cw_only = sorted(set(cw_by.keys()) - set(nlm_by.keys()) - set(anchor_index.keys()))
lines += [
    "",
    f"## Claude-web-only variables (not in NLM, not in Table 1 anchor) — {len(cw_only)} variables",
    "",
    "These are variables Claude-web caught but NLM missed (NLM enumerated only Table-1 vars + a few). Most are from Tables 2-12, IA Tables C.1-C.7, IA E.2, equation (14) controls, robustness specs.",
    "",
]
for n in cw_only:
    b = cw_by[n][0]
    lines.append(f"- **{b['name']}** (CW VAR_{b['var_no']:02d}, role: {b['role']})")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT}")
