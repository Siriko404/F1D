"""Extract Campello Table 1 Panel A from PDF → JSON.
PyMuPDF (fitz) programmatic extraction — NO LLM transcription, NO string matching.
Layout is fixed: variable name line, then 5 lines (mean, SD, median, IQR, N).
"""
import json, re, sys
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "docs" / "papers" / "campello_etal_2022_brexit_jfqa.pdf"
OUT = ROOT / "tmp" / "campello_table1_panel_a.json"

# Variables to extract — exact PDF labels
WANTED = {
    "CASH",
    "TOBIN_Q",
    "CASH_FLOW",
    "SIZE (Log Assets)",
    "SALES_GROWTH",
    "CONSENSUS_EARNINGS_FORECAST",
    "STOCK_RETURNS",
}


def _is_number(s: str) -> bool:
    """Check if string is a number (handles commas in N values)."""
    return bool(re.match(r'^-?\d[\d,]*\.?\d*$', s.strip()))


def _parse_n(s: str) -> int:
    return int(s.strip().replace(",", ""))


def _parse_float(s: str) -> float:
    return float(s.strip())


def main():
    doc = fitz.open(str(PDF))
    # Table 1 spans pages 21-22 (0-indexed: 20-21)
    lines = []
    for pg in [20, 21]:
        text = doc[pg].get_text("text")
        lines.extend(text.split("\n"))
    doc.close()

    # Find Panel A start
    panel_a_idx = None
    for i, ln in enumerate(lines):
        if "Panel A. COMPUSTAT" in ln:
            panel_a_idx = i
            break

    if panel_a_idx is None:
        sys.exit("Panel A not found")

    # Parse: variable name line, then 5 numeric lines
    variables = {}
    i = panel_a_idx + 1
    while i < len(lines):
        ln = lines[i].strip()
        # Stop at next panel
        if "Panel B." in ln or "Panel B " in ln:
            break
        # Skip empty lines and header-like lines
        if not ln:
            i += 1
            continue
        if ln in WANTED:
            # Collect next 5 non-empty lines as numbers
            vals = []
            j = i + 1
            while j < len(lines) and len(vals) < 5:
                candidate = lines[j].strip()
                if candidate and _is_number(candidate):
                    vals.append(candidate)
                j += 1
            if len(vals) == 5:
                variables[ln] = {
                    "mean": _parse_float(vals[0]),
                    "SD": _parse_float(vals[1]),
                    "med": _parse_float(vals[2]),
                    "IQR": _parse_float(vals[3]),
                    "N": _parse_n(vals[4]),
                }
            i = j
            continue
        i += 1

    result = {
        "source": "PyMuPDF extraction from campello_etal_2022_brexit_jfqa.pdf pp.21-22",
        "panel": "A — COMPUSTAT Universe",
        "variables": variables,
    }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Extracted {len(variables)} variables:")
    for name, stats in variables.items():
        print(f"  {name:35s}  mean={stats['mean']:+.2f}  SD={stats['SD']:.2f}  "
              f"med={stats['med']:+.2f}  IQR={stats['IQR']:.2f}  N={stats['N']:,}")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
