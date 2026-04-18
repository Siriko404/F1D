"""Generate Appendix A: Variable Definitions from config/variables.yaml.

Reads the rebuilt variable registry (Step 8.4 output) and emits an
\\input-able LaTeX fragment + standalone PDF for spot-checking.

Outputs:
  - outputs/variable_definitions.tex            \\input fragment for main.tex
  - outputs/variable_definitions_standalone.tex standalone preview
  - outputs/variable_definitions_standalone.pdf compiled preview

Layout: longtable per stage subsection. 4 columns:
  Name | Formula/Description | Source | Reference

Reference cells use natbib \\citet{key} when possible, else escaped fallback.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "config" / "variables.yaml"
OUT_FRAG = ROOT / "outputs" / "variable_definitions.tex"
OUT_STANDALONE = ROOT / "outputs" / "variable_definitions_standalone.tex"
OUT_PDF = ROOT / "outputs" / "variable_definitions_standalone.pdf"

STAGE_TITLES = {
    1: "Sample Manifest",
    2: "Text/Linguistic Variables",
    3: "Financial / Market Variables",
    4: "Econometric / Indicator Variables",
    5: "Runtime Derivatives (Lead/Lag/Centered/Interaction)",
}

# Known bib keys present in docs/Draft/references.bib (22 entries).
# Keys not in this set fall back to plain text rendering instead of \citet{}.
BIB_KEYS = {
    "bates2009", "opler1999", "minton2001", "faulkender2006", "dzielinski2021",
    "bushee2018", "grenadier2002", "hoberg2016", "hassan2020", "baker2016",
    "davis2016", "caldara2022", "amihud2002", "wang2020", "chang2006",
    "larcker2012", "aguerrevere2009", "biddle2009", "leary2010", "amiram2016",
    "duong2025", "cassell2013",
}


def tex_escape(s: str) -> str:
    """Escape LaTeX special chars + transform non-ASCII chars to LaTeX commands.

    Without this transform, source chars like × and — render as placeholder
    glyphs (inverted ??) in PDF even with utf8 inputenc + T1 fontenc, because
    newtxtext/newtxmath's font tables don't always include them.
    """
    if s is None:
        return ""
    s = str(s)
    # Step 1: replace non-ASCII chars with sentinel-wrapped LaTeX commands.
    # Sentinel \x00...\x01 survives subsequent escape pass; restored at end.
    SENT_OPEN, SENT_CLOSE = "\x00", "\x01"
    unicode_map = {
        "\u2014": "---",
        "\u2013": "--",
        "\u00d7": SENT_OPEN + r"$\times$" + SENT_CLOSE,
        "\u00b1": SENT_OPEN + r"$\pm$" + SENT_CLOSE,
        "\u00b7": SENT_OPEN + r"$\cdot$" + SENT_CLOSE,
        "\u2022": SENT_OPEN + r"$\bullet$" + SENT_CLOSE,
        "\u2018": "`",
        "\u2019": "'",
        "\u201c": "``",
        "\u201d": "''",
        "\u00a7": SENT_OPEN + r"\S{}" + SENT_CLOSE,
        "\u00a9": SENT_OPEN + r"\copyright{}" + SENT_CLOSE,
        "\u2026": SENT_OPEN + r"\ldots{}" + SENT_CLOSE,
        "\u00e9": SENT_OPEN + r"\'e" + SENT_CLOSE,
        "\u00e8": SENT_OPEN + r"\`e" + SENT_CLOSE,
        "\u00ed": SENT_OPEN + r"\'i" + SENT_CLOSE,
        "\u00f1": SENT_OPEN + r"\~n" + SENT_CLOSE,
        "\u00fc": SENT_OPEN + r'\"u' + SENT_CLOSE,
        "\u00f6": SENT_OPEN + r'\"o' + SENT_CLOSE,
        "\u00e4": SENT_OPEN + r'\"a' + SENT_CLOSE,
        "\u0142": SENT_OPEN + r"\l{}" + SENT_CLOSE,
        "\u00ad": "",
    }
    for u, latex in unicode_map.items():
        s = s.replace(u, latex)
    # Step 2: standard LaTeX escape pass (only touches non-sentinel content).
    parts = []
    i = 0
    while i < len(s):
        if s[i] == SENT_OPEN:
            # Pass through sentinel content unchanged
            j = s.index(SENT_CLOSE, i)
            parts.append(s[i + 1:j])
            i = j + 1
        else:
            c = s[i]
            replacement = {
                "\\": r"\textbackslash{}",
                "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
                "_": r"\_", "{": r"\{", "}": r"\}",
                "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
            }.get(c, c)
            parts.append(replacement)
            i += 1
    return "".join(parts)


def render_reference(ref_str: str) -> str:
    """Convert reference string to LaTeX. Substitute \\citet{key} for any known
    bib key found at the start of a clause; preserve descriptive trailing text.

    Examples:
      'bates2009 (Section II, p.1991)' → '\\citet{bates2009} (Section II, p.1991)'
      'dzielinski2021 (Eqn 1); bushee2018 (segment split)' →
         '\\citet{dzielinski2021} (Eqn 1); \\citet{bushee2018} (segment split)'
      'thesis (magnitude control)' → 'thesis (magnitude control)'  [no key match]
    """
    if not ref_str:
        return ""
    # Match: leading [a-z][a-z0-9]+ followed by a space/paren/semicolon
    def sub_key(m):
        key = m.group(1)
        if key in BIB_KEYS:
            return f"\\citet{{{key}}}"
        return key
    rendered = re.sub(r"\b([a-z][a-z0-9]{3,15})(?=\s|\(|;|,|$)", sub_key, ref_str)
    # Now escape LaTeX specials in remaining text WITHOUT touching \citet{} commands
    parts = re.split(r"(\\citet\{[^}]+\})", rendered)
    out_parts = []
    for p in parts:
        if p.startswith("\\citet{"):
            out_parts.append(p)
        else:
            out_parts.append(tex_escape(p))
    return "".join(out_parts)


def render_formula(formula_str: str) -> str:
    """Render formula text. Wrap full formula in \\texttt{...} as it's quasi-code.

    Conservative: escape underscores + special chars, preserve readable form.
    Future: detect math expressions and wrap in $...$.
    """
    if not formula_str:
        return ""
    return tex_escape(formula_str)


def shorten_source(source: str) -> str:
    """Compress source paths to a short tag. Keeps last 1-2 components for context."""
    if not source:
        return ""
    s = source.strip()
    # Strip leading parenthetical comments
    if "(" in s:
        s = s.split("(", 1)[0].strip()
    # Compress paths: src/f1d/shared/variables/foo.py → shared/variables/foo.py
    if "/" in s:
        parts = s.split("/")
        if len(parts) > 3:
            s = ".../" + "/".join(parts[-2:])
    return s


def split_long_token(s: str) -> str:
    """Allow LaTeX to break long tokens at underscores/slashes by inserting
    `\seqsplit{}` markers. Without this, file paths and snake_case names
    overflow narrow columns."""
    return r"\seqsplit{" + s + "}"


def build_appendix_body(variables: Dict[str, Dict]) -> str:
    """Emit the body LaTeX (for inclusion in main.tex via \\input).

    Layout: landscape orientation, longtable with tabularx-style flexible
    description column, scriptsize font, ragged-right wrapping.
    """
    by_stage: Dict[int, List[Tuple[str, Dict]]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for entry_name, entry in variables.items():
        if not isinstance(entry, dict):
            continue
        stage = entry.get("stage", 9)
        try:
            stage = int(stage)
        except (TypeError, ValueError):
            stage = 9
        col = entry.get("column")
        cols = entry.get("columns")
        if col:
            display = col
        elif cols:
            display = ", ".join(cols)
        else:
            display = entry_name
        by_stage.setdefault(stage, []).append((display, entry))

    # Body emits \section + \subsection (auto-numbered when caller wraps in \appendix).
    # main.tex must include `\appendix` BEFORE `\input{outputs/variable_definitions.tex}`.
    # Standalone wrapper handles \appendix automatically.
    lines = []
    lines.append(r"\section{Variable Definitions}")
    lines.append(r"\label{app:vardefs}")
    lines.append("")
    lines.append(
        r"This appendix lists every variable used in the empirical analyses, with construction "
        r"formula, data source, and originating reference. Variable names follow paper-standard "
        r"conventions where available (Dzieli{\'n}ski et al.\ 2021 for speech measures, "
        r"Bates et al.\ 2009 for cash-holdings controls); deviations from source-paper "
        r"frequency or sample are documented in the formula column."
    )
    lines.append("")
    lines.append(r"\begin{landscape}")
    lines.append(r"\scriptsize")
    lines.append(r"\setlength{\LTpre}{0pt}\setlength{\LTpost}{0pt}")
    lines.append(r"\renewcommand{\arraystretch}{1.15}")
    lines.append("")

    # Column spec: name (3cm) | description (flex 12cm) | source (4cm) | reference (5cm)
    # Total ~24cm fits A4 landscape (~25.7cm text width).
    col_spec = r">{\raggedright\arraybackslash\ttfamily\footnotesize}p{3.8cm} >{\raggedright\arraybackslash}p{11.5cm} >{\raggedright\arraybackslash}p{3.7cm} >{\raggedright\arraybackslash}p{5cm}"

    for stage in sorted(by_stage.keys()):
        if not by_stage[stage]:
            continue
        title = STAGE_TITLES.get(stage, f"Stage {stage}")
        # Auto-numbered subsection (becomes A.1, A.2, ... when wrapped in \appendix)
        lines.append(rf"\subsection{{{tex_escape(title)}}}")
        lines.append("")
        lines.append(rf"\begin{{longtable}}{{{col_spec}}}")
        lines.append(r"\toprule")
        lines.append(r"\textbf{Name} & \textbf{Description / Formula} & \textbf{Source} & \textbf{Reference} \\")
        lines.append(r"\midrule")
        lines.append(r"\endfirsthead")
        lines.append(rf"\multicolumn{{4}}{{l}}{{\textit{{(continued from previous page)}}}} \\")
        lines.append(r"\toprule")
        lines.append(r"\textbf{Name} & \textbf{Description / Formula} & \textbf{Source} & \textbf{Reference} \\")
        lines.append(r"\midrule")
        lines.append(r"\endhead")
        lines.append(r"\midrule")
        lines.append(rf"\multicolumn{{4}}{{r}}{{\textit{{(continued on next page)}}}} \\")
        lines.append(r"\endfoot")
        lines.append(r"\bottomrule")
        lines.append(r"\endlastfoot")

        for display, entry in sorted(by_stage[stage], key=lambda x: x[0].lower()):
            # Name column is already \ttfamily via col_spec; just escape + comma-join
            if "," in display:
                name_cell = ", ".join(tex_escape(p.strip()) for p in display.split(","))
            else:
                name_cell = tex_escape(display)
            desc = entry.get("description", "")
            formula = entry.get("formula", "")
            if desc and formula and desc.strip() != formula.strip():
                cell = f"{tex_escape(desc)}\\par\\smallskip\\textit{{Formula:}} {render_formula(formula)}"
            elif formula:
                cell = render_formula(formula)
            else:
                cell = tex_escape(desc)
            # Source: shortened + seqsplit-wrapped to allow break inside long paths
            source_short = shorten_source(entry.get("source", ""))
            source_cell = split_long_token(tex_escape(source_short)) if source_short else ""
            ref = render_reference(entry.get("reference", ""))
            lines.append(f"{name_cell} & {cell} & {source_cell} & {ref} \\\\")
            lines.append(r"\addlinespace[2pt]")

        lines.append(r"\end{longtable}")
        lines.append("")

    lines.append(r"\end{landscape}")
    return "\n".join(lines)


def build_standalone(body: str) -> str:
    """Wrap body in standalone preamble matching main.tex typography."""
    preamble = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[a4paper,margin=1.5cm]{geometry}
\usepackage{newtxtext}
\usepackage{newtxmath}
\usepackage{amsmath}
\usepackage{textcomp}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{ragged2e}
\usepackage{seqsplit}
\usepackage{pdflscape}
\usepackage[round,authoryear]{natbib}
\usepackage{hyperref}
\bibliographystyle{chicago}

\begin{document}
\appendix
"""
    closing = r"""

\bibliography{../docs/Draft/references}

\end{document}
"""
    return preamble + body + closing


def compile_pdf(tex_path: Path) -> bool:
    """Compile standalone .tex → .pdf via pdflatex+bibtex+pdflatex+pdflatex."""
    cwd = tex_path.parent
    stem = tex_path.stem
    cmds = [
        ["pdflatex", "-interaction=batchmode", tex_path.name],
        ["bibtex", stem],
        ["pdflatex", "-interaction=batchmode", tex_path.name],
        ["pdflatex", "-interaction=batchmode", tex_path.name],
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, cwd=cwd, capture_output=True, check=False, timeout=60)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"  WARN: {' '.join(cmd)} failed: {e}")
            return False
    return (cwd / f"{stem}.pdf").exists()


def main():
    raw = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    variables = raw.get("variables", {})
    body = build_appendix_body(variables)
    OUT_FRAG.write_text(body, encoding="utf-8")
    print(f"WROTE {OUT_FRAG.relative_to(ROOT)} ({len([v for v in variables.values() if isinstance(v, dict)])} entries, {len(body.splitlines())} lines)")

    standalone = build_standalone(body)
    OUT_STANDALONE.write_text(standalone, encoding="utf-8")
    ok = compile_pdf(OUT_STANDALONE)
    if ok:
        print(f"WROTE {OUT_PDF.relative_to(ROOT)} (preview)")
    else:
        print(f"WARN: PDF compile failed; standalone .tex available at {OUT_STANDALONE.relative_to(ROOT)}")
        sys.exit(0)  # non-fatal: fragment still emitted


if __name__ == "__main__":
    main()
