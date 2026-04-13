#!/usr/bin/env python3
"""Bootstrap helper: parse the current outputs/findings.txt into a template +
a metadata map used by generate_findings.py.

Run ONCE (or whenever the prose in findings.txt changes) to refresh the
template file. The template has every coefficient cell replaced by a unique
placeholder token of the form `__<suite_id>__<iv_name>__col<N>__`.

The metadata map lists every placeholder's provenance (suite, IV, column)
so generate_findings.py can locate the corresponding model_diagnostics.csv
row without re-parsing.

Outputs:
    scripts/findings_template.txt     -- prose + placeholders
    scripts/findings_placeholders.json -- dict of placeholder -> {suite, iv, col, spec}

The bracket spec label on each coefficient line is preserved in the template
(it is part of the fixed prose, not the value being substituted).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "outputs" / "findings.txt"
TEMPLATE_OUT = ROOT / "scripts" / "findings_template.txt"
MAP_OUT = ROOT / "scripts" / "findings_placeholders.json"

SUITE_HEADER_RE = re.compile(r"^(H[0-9A-Za-z\.\-]+):")
# IV header = 2 leading spaces, then a name that may contain letters, digits,
# underscores, parentheses (possibly nested), and suffix tokens like `_t`.
# Matches: "UncAnsCEO:", "PRisk_lag:", "log(US EPU)_t:", "z(log(TSIMM)):".
IV_HEADER_RE = re.compile(r"^  ([A-Za-z0-9_()\s]+):\s*$")
# Coefficient lines: 6 leading spaces, "col<N>", value, optional stars, bracket spec.
COEF_LINE_RE = re.compile(
    r"^(\s+col\d+\s+)([^\s\[][^\[]*?)(\s+\[.*\])\s*$"
)


def parse_and_template() -> None:
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")

    text = SRC.read_text(encoding="utf-8")
    lines = text.split("\n")

    template_lines: List[str] = []
    placeholders: Dict[str, Dict[str, Any]] = {}

    current_suite: str | None = None
    current_iv: str | None = None

    for line in lines:
        # Detect suite header line (e.g., "H1: SPEECH UNCERTAINTY...")
        m_suite = SUITE_HEADER_RE.match(line)
        if m_suite:
            current_suite = m_suite.group(1)
            current_iv = None
            template_lines.append(line)
            continue

        # Detect IV header line (e.g., "  UncAnsCEO:")
        m_iv = IV_HEADER_RE.match(line)
        if m_iv:
            current_iv = m_iv.group(1)
            template_lines.append(line)
            continue

        # Detect coefficient row
        m_coef = COEF_LINE_RE.match(line)
        if m_coef and current_suite and current_iv:
            prefix, value, bracket = m_coef.group(1), m_coef.group(2), m_coef.group(3)
            col_num = int(re.search(r"col(\d+)", prefix).group(1))
            key = f"__{current_suite}__{current_iv}__col{col_num}__"
            placeholders[key] = {
                "suite": current_suite,
                "iv": current_iv,
                "col": col_num,
                "bracket": bracket.strip(),
                "orig_value": value.rstrip(),
            }
            # Strip leading whitespace from the bracket group so the generator
            # can control the exact width of the value field via ljust(16).
            # Without this, the original trailing whitespace (which depended
            # on the original value's length) gets double-counted when the
            # generator emits a new padded value.
            bracket_stripped = bracket.lstrip()
            template_lines.append(f"{prefix}{key}{bracket_stripped}")
            continue

        # Everything else is fixed prose (preamble, ==== lines, DV formulas,
        # headers, blank lines, etc.)
        template_lines.append(line)

    TEMPLATE_OUT.write_text("\n".join(template_lines), encoding="utf-8")
    MAP_OUT.write_text(
        json.dumps(placeholders, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    n_suites = len({p["suite"] for p in placeholders.values()})
    print(f"Wrote {TEMPLATE_OUT.name} ({len(template_lines):,} lines)")
    print(f"Wrote {MAP_OUT.name} ({len(placeholders):,} placeholders across {n_suites} suites)")


if __name__ == "__main__":
    parse_and_template()
