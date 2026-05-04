"""Generate Appendix A: Variable Definitions, deterministically scoped to the
v7 thesis suites.

Pipeline (no hand-edits to variable_definitions.tex anywhere):

1. THESIS_DIRS lists the 12 thesis-body suite directories under
   outputs/econometric/.  Edit this list when the thesis suite roster changes.
2. For each, the latest suite_spec_*.json is read; IVs, DVs, controls,
   and `coefs` keys (centered + interaction terms) are unioned into
   `used_vars` — the authoritative set of variable names that actually appear
   in the thesis tables.
3. The variable registry is built by merging `config/variables.yaml`
   (auto-rebuilt by tools/rebuild_variables_yaml.py) with HAND_STUBS — entries
   that don't live in the YAML because they come from a separate residualization
   engine (DWZ Eq.4/5 outputs + their centered/interaction derivatives).
4. Entries are filtered to those whose `column` is in `used_vars` plus
   `ALWAYS_KEEP` (vars referenced by name inside another entry's formula).
5. The filtered registry is rendered into one longtable per stage subsection
   and written to docs/Draft/variable_definitions.tex (consumed by main.tex).

Outputs:
  - docs/Draft/variable_definitions.tex            \\input fragment for main.tex
  - docs/Draft/variable_definitions_standalone.tex standalone preview
  - docs/Draft/variable_definitions_standalone.pdf compiled preview
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
YAML_PATH = ROOT / "config" / "variables.yaml"
SUITE_RENDER_ORDER = ROOT / "config" / "suite_render_order.yaml"
ECONOMETRIC_DIR = ROOT / "outputs" / "econometric"
OUT_FRAG = HERE / "variable_definitions.tex"
OUT_STANDALONE = HERE / "variable_definitions_standalone.tex"
OUT_PDF = HERE / "variable_definitions_standalone.pdf"


def load_thesis_suite_ids() -> List[str]:
    """Read thesis_suites: from suite_render_order.yaml — single source of truth.
    Replaces the previously-hardcoded THESIS_DIRS list to eliminate drift between
    the YAML registry and the dir-name list used here.
    """
    cfg = yaml.safe_load(SUITE_RENDER_ORDER.read_text(encoding="utf-8"))
    suite_ids = cfg.get("thesis_suites") or []
    if not suite_ids:
        raise RuntimeError(f"No thesis_suites: list in {SUITE_RENDER_ORDER}")
    return list(suite_ids)


def suite_id_to_dir(suite_id: str) -> str:
    """Find the econometric output dir_name for a given suite_id by globbing
    for the latest suite_spec_<id>.json under outputs/econometric/.
    """
    matches = sorted(ECONOMETRIC_DIR.glob(f"*/*/suite_spec_{suite_id}.json"))
    if not matches:
        raise RuntimeError(
            f"No suite_spec_{suite_id}.json found under {ECONOMETRIC_DIR} "
            f"(suite registered in thesis_suites but never run)."
        )
    return matches[-1].parent.parent.name


def derive_thesis_dirs() -> List[str]:
    """Derive THESIS_DIRS from suite_render_order.yaml `thesis_suites:` list.
    Single source of truth — eliminates the 3-parallel-list drift risk.
    """
    return [suite_id_to_dir(sid) for sid in load_thesis_suite_ids()]


THESIS_DIRS = derive_thesis_dirs()  # derived at import; YAML is the spec

# Vars referenced by name inside another vardef's formula — must stay even if
# they are not directly used in any spec (would create dangling references).
ALWAYS_KEEP = {
    "UncAnsCEO",  # ClarityCEO + UncResCEO formulas reference UncAnsCEO (DWZ Eq.4/5 input)
    "SurpDec",    # AbsSurpDec formula = abs(SurpDec)
}

STAGE_TITLES = {
    1: "Sample Manifest",
    2: "Text/Linguistic Variables",
    3: "Financial / Market Variables",
    4: "Econometric / Indicator Variables",
    5: "Runtime Derivatives (Lead/Lag/Centered/Interaction)",
    9: "Macro / Regulatory Variables",
}

# Bib keys present in docs/Draft/references.bib.  Keys not in this set fall
# back to plain text (no \citet wrapper).
BIB_KEYS = {
    "bates2009", "opler1999", "minton2001", "faulkender2006", "dzielinski2021",
    "bushee2018", "grenadier2002", "hoberg2016", "hassan2020", "baker2016",
    "davis2016", "caldara2022", "amihud2002", "wang2020", "chang2006",
    "larcker2012", "aguerrevere2009", "biddle2009", "leary2010", "amiram2016",
    "duong2025", "cassell2013", "almeida2004", "hanqiu2007", "lerman2026",
    "ghafoor2023", "bennedsen2020", "bertrand2003", "bertrand2004",
}

# Bare-tag aliases used in older variables.yaml entries.  Rewrite to their
# canonical bib keys before render_reference resolves \citet{}.
TAG_REWRITES = {
    "dwz2021": "dzielinski2021",
    "bks2009": "bates2009",
    "bgt2018": "bushee2018",
    "bbd2016": "baker2016",
    "hhlt2019": "hassan2020",
    "hp2016": "hoberg2016",
}

# ---------------------------------------------------------------------------
# HAND_STUBS — vardef entries for variables that come from the speech-uncertainty
# residualization engine (outputs/econometric/ceo_clarity_extended/) and are not
# present in config/variables.yaml.  Centered/interaction derivatives also live
# here because they are constructed at runtime in the spec runners.
# ---------------------------------------------------------------------------
HAND_STUBS: Dict[str, Dict] = {
    "clarity_ceo": {
        "stage": 2,
        "column": "ClarityCEO",
        "source": "outputs/econometric/ceo_clarity_extended/",
        "formula": (
            r"ClarityCEO$_i$ = $-\widehat{\mathrm{FE}}_i$ where "
            r"$\widehat{\mathrm{FE}}_i$ is the CEO-$i$ fixed-effect estimate from the "
            r"panel regression UncAnsCEO$_{ic}$ = $\alpha + \sum_i \mathrm{FE}_i \cdot "
            r"\mathbb{1}[\text{CEO}=i] + \mathbf{X}_{ic}\boldsymbol\gamma + "
            r"\varepsilon_{ic}$ over the call-level Q\&A uncertainty panel; "
            r"controls $\mathbf{X}$ are the DWZ extended-controls vector. "
            r"The sign flip on $\widehat{\mathrm{FE}}_i$ makes higher ClarityCEO "
            r"mean ``CEO speaks more clearly'' (lower mean uncertainty). "
            r"Persistent CEO trait."
        ),
        "reference": "dzielinski2021 (Section 4.4 Eqn 5, p.16)",
        "description": "CEO clarity persistent-style component (DWZ Eqn 5).",
    },
    "clarity_ceo_qtrexp": {
        "stage": 2,
        "column": "ClarityCEO_QtrExp",
        "source": "outputs/econometric/ceo_clarity_expanding/",
        "formula": (
            "As ClarityCEO, but the CEO fixed-effect regression is re-estimated "
            "on an expanding within-CEO window using only calls of CEO $i$ "
            "available up to and including focal call $c$. Strictly look-ahead-free."
        ),
        "reference": "thesis QtrExp variant of dzielinski2021 Eqn 5",
        "description": "ClarityCEO under within-tenure expanding window.",
    },
    "unc_res_ceo": {
        "stage": 2,
        "column": "UncResCEO",
        "source": "outputs/econometric/ceo_clarity_extended/",
        "formula": (
            r"$\widehat\varepsilon_{ic}$ = the residual from the panel regression "
            r"UncAnsCEO$_{ic}$ = $\alpha + \sum_i \mathrm{FE}_i \cdot "
            r"\mathbb{1}[\text{CEO}=i] + \mathbf{X}_{ic}\boldsymbol\gamma + "
            r"\varepsilon_{ic}$ that produces ClarityCEO. By OLS first-order "
            r"conditions, the within-CEO mean of UncResCEO is exactly zero by "
            r"construction. Captures call-level deviation in CEO Q\&A uncertainty "
            r"after stripping out the persistent CEO mean."
        ),
        "reference": "dzielinski2021 (Section 4.4 Eqn 4, p.16)",
        "description": "CEO Q\\&A residual call-state uncertainty component (DWZ Eqn 4).",
    },
    "unc_res_ceo_qtrexp": {
        "stage": 2,
        "column": "UncResCEO_QtrExp",
        "source": "outputs/econometric/ceo_clarity_expanding/",
        "formula": (
            "As UncResCEO, but the residualization regression is re-estimated "
            "on an expanding within-CEO window. Strictly look-ahead-free."
        ),
        "reference": "thesis QtrExp variant of dzielinski2021 Eqn 4",
        "description": "UncResCEO under within-tenure expanding window.",
    },
    "high_cfvol": {
        "stage": 4,
        "column": "HighCFvol",
        "source": "runtime",
        "formula": (
            "Binary = 1 if firm-quarter Han-Qiu (2007) cash-flow-volatility "
            "(16-quarter rolling std of OCF / $|$mean$|$ of OCF) is at or above "
            "the within-Fama-French-12-industry-year median; 0 otherwise."
        ),
        "reference": "hanqiu2007; thesis (H1.3 split convention)",
        "description": "High cash-flow-volatility moderator (H1.3).",
    },
    "clarity_ceo_c": {
        "stage": 5,
        "column": "ClarityCEO_c",
        "source": "runtime",
        "formula": "ClarityCEO minus its sample mean (mean-centered for interaction interpretability).",
        "reference": "thesis (interaction interpretability)",
        "description": "Mean-centered ClarityCEO.",
    },
    "clarity_ceo_qtrexp_c": {
        "stage": 5,
        "column": "ClarityCEO_QtrExp_c",
        "source": "runtime",
        "formula": "ClarityCEO_QtrExp minus its sample mean.",
        "reference": "thesis (interaction interpretability)",
        "description": "Mean-centered ClarityCEO_QtrExp.",
    },
    "unc_res_ceo_c": {
        "stage": 5,
        "column": "UncResCEO_c",
        "source": "runtime",
        "formula": "UncResCEO minus its sample mean (mean-centered for interaction interpretability).",
        "reference": "thesis (interaction interpretability)",
        "description": "Mean-centered UncResCEO.",
    },
    "unc_res_ceo_qtrexp_c": {
        "stage": 5,
        "column": "UncResCEO_QtrExp_c",
        "source": "runtime",
        "formula": "UncResCEO_QtrExp minus its sample mean.",
        "reference": "thesis (interaction interpretability)",
        "description": "Mean-centered UncResCEO_QtrExp.",
    },
    "unc_pre_ceo_c": {
        "stage": 5,
        "column": "UncPreCEO_c",
        "source": "runtime",
        "formula": "UncPreCEO minus its sample mean (mean-centered for interaction interpretability).",
        "reference": "thesis (interaction interpretability)",
        "description": "Mean-centered UncPreCEO.",
    },
    "unc_res_ceo_c_x_unrated": {
        "stage": 5,
        "column": "UncResCEO_c_x_Unrated",
        "source": "runtime",
        "formula": "Product: UncResCEO_c * Unrated.",
        "reference": "thesis (HFC interaction)",
        "description": "Interaction: UncResCEO_c $\\times$ Unrated (HFC).",
    },
    "unc_res_ceo_qtrexp_c_x_unrated": {
        "stage": 5,
        "column": "UncResCEO_QtrExp_c_x_Unrated",
        "source": "runtime",
        "formula": "Product: UncResCEO_QtrExp_c * Unrated.",
        "reference": "thesis (HFC QtrExp interaction)",
        "description": "Interaction: UncResCEO_QtrExp_c $\\times$ Unrated (HFC QtrExp).",
    },
    "unc_pre_ceo_c_x_unrated": {
        "stage": 5,
        "column": "UncPreCEO_c_x_Unrated",
        "source": "runtime",
        "formula": "Product: UncPreCEO_c * Unrated.",
        "reference": "thesis (HFC interaction)",
        "description": "Interaction: UncPreCEO_c $\\times$ Unrated (HFC).",
    },
    "unc_res_ceo_c_x_high_cfvol": {
        "stage": 5,
        "column": "UncResCEO_c_x_HighCFvol",
        "source": "runtime",
        "formula": "Product: UncResCEO_c * HighCFvol.",
        "reference": "thesis (CFvol moderator interaction)",
        "description": "Interaction: UncResCEO_c $\\times$ HighCFvol (H1.3).",
    },
    "unc_pre_ceo_c_x_high_cfvol": {
        "stage": 5,
        "column": "UncPreCEO_c_x_HighCFvol",
        "source": "runtime",
        "formula": "Product: UncPreCEO_c * HighCFvol.",
        "reference": "thesis (CFvol moderator interaction)",
        "description": "Interaction: UncPreCEO_c $\\times$ HighCFvol (H1.3).",
    },
}


# ---------------------------------------------------------------------------
# Spec-walking helpers
# ---------------------------------------------------------------------------

def latest_spec(dir_name: str) -> Optional[Path]:
    cands = sorted((ECONOMETRIC_DIR / dir_name).rglob("suite_spec_*.json"))
    return cands[-1] if cands else None


def vars_from_spec(spec_path: Path) -> set:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out: set = set()
    for iv in spec.get("ivs", []):
        out.add(iv["name"])
    ctrls = spec.get("controls", {})
    if isinstance(ctrls, dict):
        out.update(ctrls.get("base", []))
        out.update(ctrls.get("extended_only", []))
    for col in spec.get("columns", []):
        if col.get("dv"):
            out.add(col["dv"])
        out.update(col.get("control_vars", []))
        out.update(col.get("coefs", {}).keys())
    return out


def collect_used_vars() -> set:
    used: set = set()
    for d in THESIS_DIRS:
        spec = latest_spec(d)
        if spec is None:
            print(f"  WARN: no spec for {d}", file=sys.stderr)
            continue
        used |= vars_from_spec(spec)
    used |= ALWAYS_KEEP
    return used


# ---------------------------------------------------------------------------
# LaTeX rendering (preserved from earlier auto-gen)
# ---------------------------------------------------------------------------

def tex_escape(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    SENT_OPEN, SENT_CLOSE = "\x00", "\x01"
    unicode_map = {
        "—": "---",
        "–": "--",
        "×": SENT_OPEN + r"$\times$" + SENT_CLOSE,
        "±": SENT_OPEN + r"$\pm$" + SENT_CLOSE,
        "·": SENT_OPEN + r"$\cdot$" + SENT_CLOSE,
        "•": SENT_OPEN + r"$\bullet$" + SENT_CLOSE,
        "‘": "`",
        "’": "'",
        "“": "``",
        "”": "''",
        "§": SENT_OPEN + r"\S{}" + SENT_CLOSE,
        "©": SENT_OPEN + r"\copyright{}" + SENT_CLOSE,
        "…": SENT_OPEN + r"\ldots{}" + SENT_CLOSE,
        "é": SENT_OPEN + r"\'e" + SENT_CLOSE,
        "è": SENT_OPEN + r"\`e" + SENT_CLOSE,
        "í": SENT_OPEN + r"\'i" + SENT_CLOSE,
        "ñ": SENT_OPEN + r"\~n" + SENT_CLOSE,
        "ü": SENT_OPEN + r'\"u' + SENT_CLOSE,
        "ö": SENT_OPEN + r'\"o' + SENT_CLOSE,
        "ä": SENT_OPEN + r'\"a' + SENT_CLOSE,
        "ł": SENT_OPEN + r"\l{}" + SENT_CLOSE,
        "­": "",
    }
    for u, latex in unicode_map.items():
        s = s.replace(u, latex)
    parts: List[str] = []
    i = 0
    while i < len(s):
        if s[i] == SENT_OPEN:
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
    if not ref_str:
        return ""
    # Rewrite legacy bare tags to canonical bib keys before resolving \citet{}.
    for old, new in TAG_REWRITES.items():
        ref_str = re.sub(r"\b" + re.escape(old) + r"\b", new, ref_str)

    def sub_key(m: re.Match) -> str:
        key = m.group(1)
        if key in BIB_KEYS:
            return f"\\citet{{{key}}}"
        return key
    rendered = re.sub(r"\b([a-z][a-z0-9]{3,15})(?=\s|\(|;|,|$)", sub_key, ref_str)
    parts = re.split(r"(\\citet\{[^}]+\})", rendered)
    out_parts: List[str] = []
    for p in parts:
        if p.startswith("\\citet{"):
            out_parts.append(p)
        else:
            out_parts.append(tex_escape(p))
    return "".join(out_parts)


def render_formula(formula_str: str) -> str:
    if not formula_str:
        return ""
    # Math-mode segments and LaTeX commands inside HAND_STUBS formulas pass through;
    # the YAML-side formulas stay tex_escaped for safety.
    return formula_str if (r"\(" in formula_str or "$" in formula_str or r"\mathrm" in formula_str) else tex_escape(formula_str)


def shorten_source(source: str) -> str:
    if not source:
        return ""
    s = source.strip()
    if "(" in s:
        s = s.split("(", 1)[0].strip()
    if "/" in s:
        parts = s.split("/")
        if len(parts) > 3:
            s = ".../" + "/".join(parts[-2:])
    return s


def split_long_token(s: str) -> str:
    return r"\seqsplit{" + s + "}"


def build_appendix_body(variables: Dict[str, Dict]) -> str:
    by_stage: Dict[int, List[Tuple[str, Dict]]] = {1: [], 2: [], 3: [], 4: [], 5: [], 9: []}
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

    lines: List[str] = []
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

    col_spec = (
        r">{\raggedright\arraybackslash\ttfamily\footnotesize}p{3.8cm} "
        r">{\raggedright\arraybackslash}p{11.5cm} "
        r">{\raggedright\arraybackslash}p{3.7cm} "
        r">{\raggedright\arraybackslash}p{5cm}"
    )

    for stage in sorted(by_stage.keys()):
        if not by_stage[stage]:
            continue
        title = STAGE_TITLES.get(stage, f"Stage {stage}")
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

\bibliography{references}

\end{document}
"""
    return preamble + body + closing


def compile_pdf(tex_path: Path) -> bool:
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


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def column_of(entry: Dict) -> Optional[str]:
    col = entry.get("column")
    if col:
        return col
    cols = entry.get("columns")
    if cols and isinstance(cols, list) and cols:
        return cols[0]
    return None


def filter_to_used(variables: Dict[str, Dict], used: set) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    for k, v in variables.items():
        if not isinstance(v, dict):
            continue
        # Manifest entry has columns list; always keep.
        if k == "manifest":
            out[k] = v
            continue
        col = column_of(v)
        if col is None:
            continue
        if col in used:
            out[k] = v
    return out


def main() -> int:
    raw = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    yaml_vars = raw.get("variables", {})

    # Merge HAND_STUBS into the registry; HAND_STUBS wins on key collision.
    merged: Dict[str, Dict] = {**yaml_vars, **HAND_STUBS}

    used = collect_used_vars()
    print(f"Used vars from {len(THESIS_DIRS)} thesis specs: {len(used)} (incl. ALWAYS_KEEP).")

    # RAISE-GUARD: every used var MUST have a registry entry or HAND_STUB.
    # Catches "spec adds a new variable but registry/HAND_STUBS not updated"
    # silent-skip drift that would leave readers seeing a regression cell with
    # no appendix definition.
    registered_cols = set()
    for v in merged.values():
        if not isinstance(v, dict):
            continue
        c = column_of(v)
        if c:
            registered_cols.add(c)
        for c2 in (v.get("columns") or []):
            registered_cols.add(c2)
    unmatched = used - registered_cols
    if unmatched:
        raise ValueError(
            f"Used vars not in variables.yaml or HAND_STUBS: {sorted(unmatched)}\n"
            f"Add a HAND_STUB entry in this file or extend config/variables.yaml."
        )

    filtered = filter_to_used(merged, used)
    print(f"Filtered registry: {len(filtered)} entries (from {len(merged)}).")

    body = build_appendix_body(filtered)
    OUT_FRAG.write_text(body, encoding="utf-8")
    print(f"WROTE {OUT_FRAG.relative_to(ROOT)} ({len(body.splitlines())} lines)")

    standalone = build_standalone(body)
    OUT_STANDALONE.write_text(standalone, encoding="utf-8")
    ok = compile_pdf(OUT_STANDALONE)
    if ok:
        print(f"WROTE {OUT_PDF.relative_to(ROOT)} (preview)")
    else:
        print(f"WARN: PDF compile failed; standalone .tex available at {OUT_STANDALONE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
