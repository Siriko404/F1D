"""Rebuild config/variables.yaml from specs + module docstrings + engine
column lists. NEVER overwrites the source file — outputs to tmp/yaml_repair/
for human review and splice.

Inputs:
  - outputs/econometric/*/<latest_ts>/suite_spec_*.json  (37 specs)
  - src/f1d/shared/variables/*.py                        (84 modules)
  - src/f1d/shared/variables/_*_engine.py                (engine *_COLS lists)
  - config/variables.yaml                                (existing, preserve refs/comments)
  - config/summary_stats_config.yaml                     (extra_vars in scope)

Outputs:
  - tmp/yaml_repair/proposed_variables.yaml   ready-to-splice replacement
  - tmp/yaml_repair/diff_report.md            ADD/UPDATE/DEAD breakdown
  - tmp/yaml_repair/dead_review.md            50 dead entries with KEEP/DROP suggestion
  - tmp/yaml_repair/hand_stub_residual.md     TODO list for manual completion

Idempotent: rerun produces identical output if source files unchanged.
"""

from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

ROOT = Path(__file__).resolve().parent.parent
ECON_DIR = ROOT / "outputs" / "econometric"
VAR_MODULES = ROOT / "src" / "f1d" / "shared" / "variables"
YAML_PATH = ROOT / "config" / "variables.yaml"
SS_CONFIG = ROOT / "config" / "summary_stats_config.yaml"
OUT_DIR = ROOT / "tmp" / "yaml_repair"

LEAD_RE = re.compile(r"^(.+?)_lead(\d*)(_qtr)?$")
LAG_RE = re.compile(r"^(.+?)_lag(\d*)$")
MEAN_C_RE = re.compile(r"^(.+?)_c$")
INTERACTION_RE = re.compile(r"^(.+?)_x_(.+)$")

# Hand-stub registry. Source-of-truth for vars no programmatic extraction can supply.
# Speech IVs (formulas live in src/f1d/text/build_linguistic_variables.py),
# runtime indicators, transformations, and Lagged_DV.
# Verified paper attributions for module-backed controls where neither the module
# metadata nor existing YAML carries a reference. NotebookLM-verified verbatim per
# session 319f8fdd (2026-04-18) — each entry has the paper key + section/page.
# NOTE: references marked "NEEDS_BIB_ADD" are not yet in docs/Draft/references.bib
# and must be added before the appendix compiles with full bibliography.
MANUAL_REFERENCES: Dict[str, str] = {
    "CashRatio": "bates2009 (Section II, p.1991; BKS use annual che/at — we use quarterly cheq/atq for panel alignment)",
    "DivDummy": "bates2009 (Section IV, p.2000; dividend payout dummy based on common dividends)",
    "Turnover": "amihud2002 (Section 2.1, p.33; alt rolling-window def in chang2006 Appendix B p.3045)",
    "sCFO": "biddle2009 (Appendix A, p.130; 5-year rolling std of CFO/avg assets)",
    "SalesGrowth": "biddle2009 (Section 3.2, p.117; pct change in sales)",
    "EarnVol": "duong2025 (Appendix B, p.30; 3-year rolling std of qoq asset-scaled earnings)",
    "FirmMat": "biddle2009 (Appendix A, p.130; years since first CRSP appearance); alt leary2010 (App.~A p.354)",
    "Loss": "biddle2009 (Appendix A, p.131; indicator for negative net income before extraordinary items)",
    "StockPrice": "amiram2016 (Appendix A, p.137; daily CRSP stock price; justification cites Stoll 1978)",
}


HAND_STUBS: Dict[str, Dict] = {
    "UncAnsMgr": {
        "stage": 2,
        "source": "outputs/2_Textual_Analysis/2.2_Variables",
        "file_pattern": "linguistic_variables_{year}.parquet",
        "column": "UncAnsMgr",
        "formula": "Manager Q&A uncertainty (%) = (count of LM 2011 uncertainty-wordlist words spoken by managers in Q&A segment) / (total words spoken by managers in Q&A segment). Construction strategy follows DWZ 2021 Eqn (2); manager-pool identification follows BGT 2018 segment-split code (iangow/bgt replication). 'Manager' pool includes CEO plus other managerial speakers, extending DWZ which separates CEO/CFO.",
        "reference": "dzielinski2021 (measurement strategy, Eqn 2); bushee2018 (manager-pool identification via iangow/bgt); thesis extension to pooled manager speakers",
        "role": "iv",
        "description": "Manager Q&A uncertainty percentage (all managers including CEO).",
    },
    "UncPreMgr": {
        "stage": 2,
        "source": "outputs/2_Textual_Analysis/2.2_Variables",
        "file_pattern": "linguistic_variables_{year}.parquet",
        "column": "UncPreMgr",
        "formula": "Manager Presentation uncertainty (%) = (count of LM 2011 uncertainty-wordlist words by managers in Presentation segment) / (total manager words in Presentation segment). Construction strategy follows DWZ 2021 Eqn (1); manager-pool identification and Pres/Ans segment split follow BGT 2018 via iangow/bgt replication code.",
        "reference": "dzielinski2021 (measurement strategy, Eqn 1); bushee2018 (segment split + manager pool); thesis extension to pooled manager speakers",
        "role": "iv",
        "description": "Manager presentation uncertainty percentage.",
    },
    "UncAnsCEO": {
        "stage": 2,
        "source": "outputs/2_Textual_Analysis/2.2_Variables",
        "file_pattern": "linguistic_variables_{year}.parquet",
        "column": "UncAnsCEO",
        "formula": "CEO Q&A uncertainty (%) = UnctWordsAnsCEO / WordsAnsCEO (DWZ 2021 Eqn 2). Uncertainty wordlist = LM 2011 Master Dictionary 'uncertainty' list (297 words, Aug 2014 version). CEO identified via Execucomp ceoann field.",
        "reference": "dzielinski2021 (Section 4.2, Eqn 2, p.13; Appendix Table A.1, p.54)",
        "role": "iv",
        "description": "CEO-only Q&A uncertainty percentage.",
    },
    "UncPreCEO": {
        "stage": 2,
        "source": "outputs/2_Textual_Analysis/2.2_Variables",
        "file_pattern": "linguistic_variables_{year}.parquet",
        "column": "UncPreCEO",
        "formula": "CEO Presentation uncertainty (%) = UnctWordsPreCEO / WordsPreCEO (DWZ 2021 Eqn 1). Uncertainty wordlist = LM 2011 (297 words).",
        "reference": "dzielinski2021 (Section 4.2, Eqn 1, p.13; Appendix Table A.1, p.54)",
        "role": "iv",
        "description": "CEO-only presentation uncertainty percentage.",
    },
    "UncQue": {
        "stage": 2,
        "source": "outputs/2_Textual_Analysis/2.2_Variables",
        "file_pattern": "linguistic_variables_{year}.parquet",
        "column": "UncQue",
        "formula": "Analyst Q&A uncertainty (%) = UnctWordsQue / WordsQue (DWZ 2021 Eqn 3). Uncertainty wordlist = LM 2011 (297 words).",
        "reference": "dzielinski2021 (Section 4.2, Eqn 3, p.13; Appendix Table A.1, p.54)",
        "role": "iv",
        "description": "Analyst Q&A uncertainty percentage.",
    },
    "NegCall": {
        "stage": 2,
        "source": "outputs/2_Textual_Analysis/2.2_Variables",
        "file_pattern": "linguistic_variables_{year}.parquet",
        "column": "NegCall",
        "formula": "Ratio of negative words to total words in the entire call, based on LM 2011 negative-words list. Per DWZ 2021 Appendix Table A.1: 'percentage of negative words in all words spoken by the CEO, CFO and analysts attending the call.'",
        "reference": "dzielinski2021 (Section 4.4, p.18; Appendix Table A.1, p.54)",
        "role": "iv",
        "description": "Entire-call negative sentiment percentage.",
    },
    "SurpDec": {
        "stage": 3,
        "source": "src/f1d/shared/variables/earnings_surprise.py (via IbesEngine)",
        "file_pattern": "firm_controls_{year}.parquet",
        "column": "SurpDec",
        "formula": "Signed quintile rank of percentage earnings surprise per DWZ 2021 Appendix Table A.1: raw surprise = (actual - consensus forecast earnings) / share price 5 trading days before announcement, x 100. Firms grouped into 5 bins of positive surprise (+5 largest through +1 smallest positive), 0 for zero surprises, and 5 bins of negative surprise (-1 smallest negative through -5 largest negative). DWZ footnote 32 notes this decile convention follows Hirshleifer, Lim & Teoh (2009) and DellaVigna & Pollet (2009).",
        "reference": "dzielinski2021 (Appendix Table A.1, p.55; convention cites DellaVigna-Pollet 2009 + Hirshleifer-Lim-Teoh 2009)",
        "role": "control",
        "description": "Signed-quintile earnings surprise rank (-5 to +5) within calendar quarter.",
    },
    "Lagged_DV": {
        "stage": 4,
        "source": "runtime (runner-constructed via .shift(1) within gvkey)",
        "column": "Lagged_DV",
        "formula": "1-quarter lag of the dependent variable, constructed at runtime per spec (DV varies per suite). Always included as base control to absorb persistence.",
        "reference": "thesis convention (per feedback_lagged_dv.md)",
        "role": "control",
        "description": "Generic lagged-DV control (1Q lag of suite-specific DV).",
    },
    "BelowIG": {
        "stage": 4,
        "source": "runtime (S&P credit rating subsample indicator)",
        "column": "BelowIG",
        "formula": "Binary = 1 if firm's S&P long-term issuer credit rating is below investment grade (BB+ and below) at call date; 0 otherwise. Rated firms only (Unrated firms get separate indicator).",
        "reference": "thesis (H1.2 rating subsample)",
        "role": "moderator",
        "description": "Below-IG credit rating subsample indicator (H1.2).",
    },
    "IG": {
        "stage": 4,
        "source": "runtime (S&P credit rating subsample indicator)",
        "column": "IG",
        "formula": "Binary = 1 if firm has investment-grade S&P rating (BBB- or above) at call date; 0 otherwise.",
        "reference": "thesis (H1.2 rating subsample)",
        "role": "moderator",
        "description": "Investment-grade rating subsample indicator (H1.2).",
    },
    "Unrated": {
        "stage": 4,
        "source": "runtime (S&P credit rating subsample indicator)",
        "column": "Unrated",
        "formula": "Binary = 1 if firm has no S&P rating at call date; 0 otherwise.",
        "reference": "thesis (H1.2 rating subsample)",
        "role": "moderator",
        "description": "No-rating subsample indicator (H1.2).",
    },
    "HighTSIMM": {
        "stage": 4,
        "source": "runtime (within-year median split of TotalSimilarity)",
        "column": "HighTSIMM",
        "formula": "Binary = 1 if firm-year TotalSimilarity (HP 2016 product market similarity) is above the within-year median; 0 otherwise.",
        "reference": "hp2016 (TSIMM construction); thesis (H1.1 split convention)",
        "role": "moderator",
        "description": "High product-market-similarity indicator (H1.1).",
    },
    "z_log_TotalSimilarity": {
        "stage": 4,
        "source": "runtime (transformation of HP 2016 TSIMM)",
        "column": "z_log_TotalSimilarity",
        "formula": "z-score of log(1 + TotalSimilarity) computed within year. TotalSimilarity = HP 2016 firm-year product market similarity score (sum of pairwise cosine similarities × 100).",
        "reference": "hp2016",
        "role": "moderator",
        "description": "z-scored log of HP 2016 TotalSimilarity (continuous moderator, H1.1).",
    },
    "BGTAvg_Amihud": {
        "stage": 3,
        "source": "src/f1d/shared/variables/bgt_long_window_amihud.py (BGTLongWindowAmihudBuilder, 3-col output)",
        "column": "BGTAvg_Amihud",
        "formula": "Mean daily Amihud illiquidity over [-25, +25] trading days around call (51-day symmetric window, day 0 INCLUDED). F1D extension to BGT 2018.",
        "reference": "bgt2018 (window); F1D extension (symmetric average shape)",
        "role": "dv",
        "description": "BGT 25-day symmetric average Amihud illiquidity (H7e).",
    },
    "BGTDelta_Amihud": {
        "stage": 3,
        "source": "src/f1d/shared/variables/bgt_long_window_amihud.py (BGTLongWindowAmihudBuilder, 3-col output)",
        "column": "BGTDelta_Amihud",
        "formula": "Mean Amihud over post window [+1, +25] minus mean over pre window [-25, -1] trading days (day 0 EXCLUDED). F1D extension to BGT 2018.",
        "reference": "bgt2018 (window); F1D extension (delta shape)",
        "role": "dv",
        "description": "BGT 25-day post-pre Amihud illiquidity change (H7d).",
    },
    "BGTAvg_Spread": {
        "stage": 3,
        "source": "src/f1d/shared/variables/bgt_long_window_spread.py (BGTLongWindowSpreadBuilder, 3-col output)",
        "column": "BGTAvg_Spread",
        "formula": "Mean daily relative bid-ask spread over [-25, +25] trading days around call (51-day symmetric window, day 0 INCLUDED). Spread = (ASK - BID) / ((ASK + BID) / 2). F1D extension to BGT 2018.",
        "reference": "bgt2018 (window); F1D extension (symmetric average shape)",
        "role": "dv",
        "description": "BGT 25-day symmetric average bid-ask spread (H14e).",
    },
    "BGTDelta_Spread": {
        "stage": 3,
        "source": "src/f1d/shared/variables/bgt_long_window_spread.py (BGTLongWindowSpreadBuilder, 3-col output)",
        "column": "BGTDelta_Spread",
        "formula": "Mean spread over [+1, +25] minus mean over [-25, -1] trading days (day 0 EXCLUDED). F1D extension to BGT 2018.",
        "reference": "bgt2018 (window); F1D extension (delta shape)",
        "role": "dv",
        "description": "BGT 25-day post-pre bid-ask spread change (H14d).",
    },
    "PostCallAmihud": {
        "stage": 5,
        "source": "runtime (panel-time computation in H7b runner)",
        "column": "PostCallAmihud",
        "formula": "Panel-time mean daily Amihud illiquidity over the post-call period (call quarter + N following quarters per H7b runner spec). Computed on panel structure with two-way clustering.",
        "reference": "thesis (H7b panel-time post-call construction)",
        "role": "dv",
        "description": "Panel-time post-call Amihud illiquidity level (H7b).",
    },
    "PostCallSpread": {
        "stage": 5,
        "source": "runtime (panel-time computation in H14b runner)",
        "column": "PostCallSpread",
        "formula": "Panel-time mean daily relative bid-ask spread over the post-call period (call quarter + N following quarters per H14b runner spec). Computed on panel structure with two-way clustering.",
        "reference": "thesis (H14b panel-time post-call construction)",
        "role": "dv",
        "description": "Panel-time post-call bid-ask spread level (H14b).",
    },
    "EquityDelayCon": {
        "stage": 3,
        "source": "inputs/Hoberg_Maksimovic/ (pre-computed) merged to panel",
        "column": "EquityDelayCon",
        "formula": "Hoberg-Maksimovic (2015) firm-year equity-market financing constraint measure. Higher values = more constrained firm. Panel column is lowercase `equitydelaycon`; CamelCase name is the spec convention. See docs/provenance/h22.md for merge details.",
        "reference": "hm2015",
        "role": "dv",
        "description": "Hoberg-Maksimovic (2015) equity-market financing constraint index (H22).",
    },
    "AbsSurpDec": {
        "stage": 5,
        "source": "runtime (runner computes |SurpDec|; see run_h14c/d/e)",
        "column": "AbsSurpDec",
        "formula": "abs(SurpDec) — unsigned magnitude of signed-quintile earnings surprise rank, values 0-5.",
        "reference": "thesis (magnitude control independent of sign)",
        "role": "control",
        "description": "Absolute earnings surprise quintile magnitude.",
    },
}


# ============================================================================
# Spec scan
# ============================================================================

def latest_spec_dirs(econ_dir: Path) -> List[Path]:
    out = []
    for suite_dir in sorted(econ_dir.iterdir()):
        if not suite_dir.is_dir() or suite_dir.name.startswith("_"):
            continue
        ts_dirs = sorted(
            [d for d in suite_dir.iterdir() if d.is_dir()],
            key=lambda x: x.name,
            reverse=True,
        )
        for ts in ts_dirs:
            specs = list(ts.glob("suite_spec_*.json"))
            if specs:
                out.extend(specs)
                break
    return out


def base_of_derivative(var: str) -> Optional[str]:
    """Return the base variable name if var is a naming-convention derivative, else None."""
    if m := LEAD_RE.match(var):
        return m.group(1)
    if m := LAG_RE.match(var):
        return m.group(1)
    if m := MEAN_C_RE.match(var):
        return m.group(1)
    # Interactions have TWO bases; handle separately
    return None


def scan_specs(spec_paths: List[Path]) -> Dict[str, Dict]:
    canonical: Dict[str, Dict] = {}
    for sp in spec_paths:
        try:
            spec = json.loads(sp.read_text(encoding="utf-8"))
        except Exception:
            continue
        sid = spec.get("suite_id", sp.stem.replace("suite_spec_", ""))

        def add(name: str, role: str):
            entry = canonical.setdefault(name, {"role": role, "suites": set()})
            entry["suites"].add(sid)
            # IV beats DV beats control
            order = {"iv": 3, "dv": 2, "moderator": 2, "control": 1}
            if order.get(role, 0) > order.get(entry["role"], 0):
                entry["role"] = role

        for iv in spec.get("ivs", []):
            add(iv["name"], "iv")
        for ctrl in spec.get("controls", {}).get("base", []):
            add(ctrl, "control")
        for ctrl in spec.get("controls", {}).get("extended_only", []):
            add(ctrl, "control")
        for col in spec.get("columns", []):
            dv = col.get("dv")
            if dv:
                add(dv, "dv")

    # Auto-promote derivative bases to canonical (e.g., EquityDelayCon_lead → EquityDelayCon)
    # so base entries aren't flagged DEAD when only the derivative is in spec.
    # NOTE: interaction components NOT auto-promoted — they're either real vars
    # (already in canonical) or shorthand (e.g., zlogTSIMM) that shouldn't have entries.
    derivatives = list(canonical.keys())
    for var in derivatives:
        base = base_of_derivative(var)
        if base and base not in canonical:
            canonical[base] = {"role": canonical[var]["role"],
                               "suites": set(canonical[var]["suites"])}
    return canonical


# ============================================================================
# Module + engine scan
# ============================================================================

def parse_module(py: Path) -> Dict:
    info = {
        "file": str(py.relative_to(ROOT)).replace("\\", "/"),
        "module_doc": None,
        "module_doc_line1": None,
        "class_doc_line1": None,
        "metadata_source": None,
        "metadata_column": None,
        "metadata_reference": None,
    }
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except Exception:
        return info
    info["module_doc"] = ast.get_docstring(tree)
    if info["module_doc"]:
        info["module_doc_line1"] = info["module_doc"].split("\n", 1)[0].strip()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and info["class_doc_line1"] is None:
            cd = ast.get_docstring(node)
            if cd:
                info["class_doc_line1"] = cd.split("\n", 1)[0].strip()
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "metadata" and isinstance(kw.value, ast.Dict):
                    for k, v in zip(kw.value.keys, kw.value.values):
                        if not isinstance(k, ast.Constant):
                            continue
                        key = k.value
                        val = v.value if isinstance(v, ast.Constant) else None
                        if key == "source" and val and not info["metadata_source"]:
                            info["metadata_source"] = val
                        if key == "column" and val and not info["metadata_column"]:
                            info["metadata_column"] = val
                        if key == "reference" and val and not info["metadata_reference"]:
                            info["metadata_reference"] = val
    return info


def scan_modules(var_dir: Path) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    for py in sorted(var_dir.glob("*.py")):
        if py.name in ("__init__.py", "base.py", "winsorization.py"):
            continue
        out[py.stem] = parse_module(py)
    return out


def scan_engine_cols(var_dir: Path) -> Dict[str, Tuple[str, str]]:
    """Return {col_name: (engine_file, list_var_name)}."""
    out: Dict[str, Tuple[str, str]] = {}
    for py in sorted(var_dir.glob("_*_engine.py")):
        txt = py.read_text(encoding="utf-8")
        for list_name, body in re.findall(
            r"^([A-Z][A-Z_]*?_COLS)\s*=\s*\[(.+?)\]", txt, re.MULTILINE | re.DOTALL
        ):
            if "REQUIRED" in list_name or "RAW" in list_name or "BIDASK" in list_name:
                continue  # skip raw input lists
            for col in re.findall(r'"([^"]+)"', body):
                if col not in out:
                    out[col] = (str(py.relative_to(ROOT)).replace("\\", "/"), list_name)
    return out


def build_module_col_index(modules: Dict[str, Dict], engine_cols: Dict[str, Tuple[str, str]]) -> Dict[str, Dict]:
    """Return {col_name: module_meta}. Combines metadata-dict columns + engine COLS lists.

    Module file is preferred when metadata explicitly names the column. For engine-output
    columns the entry points at the engine file. Single col_name → first source wins
    (deterministic via sorted iteration order).
    """
    by_col: Dict[str, Dict] = {}
    for stem, m in modules.items():
        if m.get("metadata_column"):
            by_col.setdefault(m["metadata_column"], m)
    for col, (engine_file, _list) in engine_cols.items():
        if col not in by_col:
            by_col[col] = {
                "file": engine_file,
                "module_doc_line1": None,  # engine doc is generic; var-specific docs absent
                "class_doc_line1": None,
                "metadata_source": None,
                "metadata_column": col,
                "metadata_reference": None,
                "_from_engine_list": True,
            }
    return by_col


# ============================================================================
# Existing YAML
# ============================================================================

def load_existing_yaml(path: Path) -> Tuple[Dict, Dict[str, Dict]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    by_col: Dict[str, Dict] = {}
    for entry_name, entry in raw.get("variables", {}).items():
        if not isinstance(entry, dict):
            continue
        col = entry.get("column")
        if col:
            by_col[col] = {"_entry_name": entry_name, **entry}
        for c in entry.get("columns", []) or []:
            by_col[c] = {"_entry_name": entry_name, **entry}
    return raw, by_col


# ============================================================================
# Derivative naming-rule entries
# ============================================================================

def derivative_entry(var: str, base_lookup: Dict[str, Dict]) -> Optional[Dict]:
    """Return YAML entry derived from naming convention. Returns None if not a derivative."""
    if m := LEAD_RE.match(var):
        base, n_str, qtr = m.group(1), m.group(2), m.group(3)
        n = int(n_str) if n_str else 1
        base_meta = base_lookup.get(base, {})
        return {
            "stage": 5,
            "source": "runtime (runner .shift in gvkey group)",
            "column": var,
            "formula": f"{n}-quarter lead of {base}" + (" (calendar-quarter aligned)" if qtr else ""),
            "reference": base_meta.get("reference", "see base var"),
            "role": "dv",
            "description": f"{n}Q lead of {base}" + (" (qtr-aligned)" if qtr else "") + ".",
            "_base": base,
        }
    if m := LAG_RE.match(var):
        base, n_str = m.group(1), m.group(2)
        n = int(n_str) if n_str else 1
        base_meta = base_lookup.get(base, {})
        return {
            "stage": 5,
            "source": "runtime (runner .shift in gvkey group)",
            "column": var,
            "formula": f"{n}-quarter lag of {base}",
            "reference": base_meta.get("reference", "see base var"),
            "role": "control",
            "description": f"{n}Q lag of {base}.",
            "_base": base,
        }
    if m := INTERACTION_RE.match(var):
        a, b = m.group(1), m.group(2)
        return {
            "stage": 5,
            "source": "runtime (product of two predictors)",
            "column": var,
            "formula": f"Product: {a} * {b}",
            "reference": "thesis (interaction term)",
            "role": "interaction",
            "description": f"Interaction term: {a} x {b}.",
            "_components": [a, b],
        }
    if m := MEAN_C_RE.match(var):
        base = m.group(1)
        return {
            "stage": 5,
            "source": "runtime (sample mean subtracted)",
            "column": var,
            "formula": f"{base} minus its sample mean (mean-centered for interaction interpretability)",
            "reference": "thesis (interaction interpretability)",
            "role": "iv",
            "description": f"Mean-centered {base}.",
            "_base": base,
        }
    return None


# ============================================================================
# Module-derived entry
# ============================================================================

def module_entry(var: str, mod: Dict, role: str, suites: Set[str]) -> Dict:
    desc = mod.get("class_doc_line1") or mod.get("module_doc_line1") or f"{var} (description not in module docstring)"
    formula = "see module: " + mod["file"]
    if mod.get("metadata_source"):
        formula = f"{mod['metadata_source']} (see module: {mod['file']})"
    return {
        "stage": 3 if "_engine" not in mod["file"] else 3,
        "source": mod.get("metadata_source") or mod["file"],
        "column": var,
        "formula": formula,
        "reference": mod.get("metadata_reference"),  # may be None — fill from existing or TODO
        "role": role,
        "description": desc,
    }


# ============================================================================
# Assembly
# ============================================================================

def assemble(
    canonical: Dict[str, Dict],
    extra_vars: List[Dict],
    modules_by_col: Dict[str, Dict],
    existing: Dict[str, Dict],
) -> Tuple[Dict[str, Dict], List[str], List[str]]:
    """Return (entries_by_col, missing_after_all_sources, todo_items)."""
    proposed: Dict[str, Dict] = {}
    todo: List[str] = []

    all_vars = set(canonical.keys()) | {e["name"] for e in extra_vars}

    # Build base-lookup for derivatives (use existing + modules + hand-stubs)
    base_lookup: Dict[str, Dict] = {}
    for col, e in existing.items():
        base_lookup[col] = e
    for col, m in modules_by_col.items():
        base_lookup.setdefault(col, {"reference": m.get("metadata_reference")})
    for col, e in HAND_STUBS.items():
        base_lookup.setdefault(col, e)

    for var in sorted(all_vars):
        meta = canonical.get(var, {})
        role = meta.get("role", "control")
        suites = sorted(meta.get("suites", set()))

        # 1. Hand-stub takes priority for known runtime/speech vars
        if var in HAND_STUBS:
            entry = dict(HAND_STUBS[var])
            entry["suites"] = suites or entry.get("suites", [])
            entry["role"] = role if role else entry["role"]
            proposed[var] = entry
            continue

        # 2. Derivative naming-rule
        deriv = derivative_entry(var, base_lookup)
        if deriv:
            deriv["suites"] = suites
            deriv["role"] = role  # spec-tagged role wins
            proposed[var] = deriv
            continue

        # 3. Module-backed
        if var in modules_by_col:
            mod = modules_by_col[var]
            entry = module_entry(var, mod, role, suites)
            # Reference precedence: module metadata > MANUAL_REFERENCES > existing YAML > TODO
            if entry.get("reference") is None:
                if var in MANUAL_REFERENCES:
                    entry["reference"] = MANUAL_REFERENCES[var]
                else:
                    existing_ref = existing.get(var, {}).get("reference")
                    entry["reference"] = existing_ref or "TODO_REFERENCE"
            entry["suites"] = suites
            if entry["reference"] == "TODO_REFERENCE":
                todo.append(f"{var}: missing reference (module={mod['file']})")
            proposed[var] = entry
            continue

        # 4. Existing YAML entry without module — preserve
        if var in existing:
            e = dict(existing[var])
            e.pop("_entry_name", None)
            e["suites"] = suites
            e["role"] = role
            if "formula" not in e or not e["formula"]:
                e["formula"] = "TODO_FORMULA"
                todo.append(f"{var}: missing formula (preserved from YAML, no module)")
            proposed[var] = e
            continue

        # 5. Extra-vars supplemental (TotalSimilarity etc.)
        ev = next((e for e in extra_vars if e["name"] == var), None)
        if ev:
            proposed[var] = {
                "stage": 3,
                "source": "external (HP 2016 raw TSIMM, panel-merged)",
                "column": var,
                "formula": "TODO_FORMULA",
                "reference": "TODO_REFERENCE",
                "role": "supplementary",
                "description": ev.get("note", f"Supplementary substantive var {var}."),
                "suites": [ev.get("anchor")] if ev.get("anchor") else [],
            }
            todo.append(f"{var}: extra_var supplemental (formula+reference TODO)")
            continue

        # 6. Truly missing — record
        todo.append(f"{var}: NO source found (no module, no existing entry, no hand-stub)")

    # Final sweep: log any entry containing TODO markers (catches hand-stub TODO_REFERENCE
    # that wasn't logged during assembly)
    already_flagged = {t.split(":")[0].strip() for t in todo}
    for var, e in proposed.items():
        if var in already_flagged:
            continue
        for field in ("formula", "reference"):
            val = e.get(field)
            if isinstance(val, str) and "TODO" in val:
                todo.append(f"{var}: {field} = {val} (hand-stub)")
                break
    return proposed, [v for v in all_vars if v not in proposed], sorted(todo)


# ============================================================================
# Dead entry triage
# ============================================================================

MANIFEST_COLS = {"file_name", "ceo_id", "ceo_name", "gvkey", "ff12_code", "ff12_name", "start_date"}

def triage_dead(dead: List[str], existing: Dict[str, Dict], modules_by_col: Dict[str, Dict]) -> List[Dict]:
    """Return per-entry triage suggestion."""
    out = []
    for col in sorted(dead):
        e = existing.get(col, {})
        rec = "DROP"  # default
        reason = "Not used by any current spec; no module exporting it."
        if col in MANIFEST_COLS:
            rec = "KEEP"
            reason = "Manifest identifier column, not a regression variable."
        elif col in modules_by_col:
            rec = "REVIEW"
            reason = f"Module {modules_by_col[col]['file']} still exports this column — may be archived suite or future use."
        elif col.endswith("_pct") and "Manager" in col or "Analyst" in col or "CEO" in col:
            rec = "DROP"
            reason = "Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused)."
        out.append({"col": col, "entry_name": e.get("_entry_name", "?"),
                    "ref": e.get("reference"), "rec": rec, "reason": reason})
    return out


# ============================================================================
# YAML emit (preserve existing structure where possible)
# ============================================================================

def yaml_dump_entry(name: str, entry: Dict) -> str:
    """Emit one entry in stable order, matching existing style."""
    order = ["stage", "source", "file_name", "file_pattern", "column", "columns",
             "formula", "reference", "role", "suites", "description"]
    lines = [f"  {name}:"]
    for k in order:
        if k not in entry:
            continue
        v = entry[k]
        if v is None:
            continue
        if k == "suites" and isinstance(v, list):
            if not v:
                lines.append(f"    suites: []")
            else:
                lines.append(f"    suites: [{', '.join(v)}]")
        elif isinstance(v, list):
            lines.append(f"    {k}:")
            for item in v:
                lines.append(f"      - {item}")
        elif isinstance(v, str):
            # YAML-safe quoting; use double quotes if contains : or starts with special
            if any(c in v for c in [":", "#", "&", "*", "?", "|", ">", "!", "%", "@", "`"]) or v.strip() != v:
                v_quoted = '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'
                lines.append(f"    {k}: {v_quoted}")
            else:
                lines.append(f"    {k}: {v}")
        else:
            lines.append(f"    {k}: {v}")
    return "\n".join(lines)


def emit_proposed_yaml(proposed: Dict[str, Dict], header: str,
                        manifest_entry: Optional[Dict] = None,
                        review_entries: Optional[List[Tuple[str, Dict]]] = None) -> str:
    lines = [header, "", "variables:"]
    # Preserved manifest (Stage 1 — identifier columns, not regression vars)
    if manifest_entry is not None:
        lines.append("")
        lines.append("  # ===========================================================================")
        lines.append("  # Stage 1: Sample Manifest (preserved — identifier columns, not regression vars)")
        lines.append("  # ===========================================================================")
        lines.append("")
        lines.append("  manifest:")
        order = ["stage", "source", "file_name", "columns", "description"]
        for k in order:
            if k not in manifest_entry:
                continue
            v = manifest_entry[k]
            if isinstance(v, list):
                lines.append(f"    {k}:")
                for item in v:
                    lines.append(f"      - {item}")
            else:
                lines.append(f"    {k}: {v}")
    # Group by stage for readability
    by_stage = defaultdict(list)
    for col, e in proposed.items():
        s = e.get("stage", 9)
        try:
            s = int(s)
        except (TypeError, ValueError):
            s = 9
        e["stage"] = s
        by_stage[s].append((col, e))
    stage_titles = {
        1: "Stage 1: Sample Manifest",
        2: "Stage 2: Text/Linguistic Variables",
        3: "Stage 3: Financial / Market Variables",
        4: "Stage 4: Econometric / Indicator Variables",
        5: "Stage 5: Runtime Derivatives (lead/lag/centered/interaction)",
        9: "Other / Unclassified",
    }
    for stage in sorted(by_stage.keys()):
        lines.append("")
        lines.append(f"  # {'='*75}")
        lines.append(f"  # {stage_titles.get(stage, f'Stage {stage}')}")
        lines.append(f"  # {'='*75}")
        for col, e in sorted(by_stage[stage]):
            entry_name = re.sub(r"([a-z])([A-Z])", r"\1_\2", col).lower()
            lines.append("")
            lines.append(yaml_dump_entry(entry_name, e))

    # REVIEW entries: in YAML but no current spec uses them; module still exports.
    # Kept commented-out (NOT live entries) pending user decision per dead_review.md.
    if review_entries:
        lines.append("")
        lines.append("  # ===========================================================================")
        lines.append("  # REVIEW: Module-exported but no current spec consumes (12 entries)")
        lines.append("  # Pending user decision (per tmp/yaml_repair/dead_review.md). Kept here as")
        lines.append("  # commented-out reference — uncomment if a future spec adds them.")
        lines.append("  # ===========================================================================")
        for col, e in sorted(review_entries):
            entry_name = re.sub(r"([a-z])([A-Z])", r"\1_\2", col).lower()
            entry_block = yaml_dump_entry(entry_name, e)
            lines.append("")
            for ln in entry_block.split("\n"):
                lines.append("  # " + ln.lstrip(" "))
    return "\n".join(lines) + "\n"


# ============================================================================
# Main
# ============================================================================

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    spec_paths = latest_spec_dirs(ECON_DIR)
    canonical = scan_specs(spec_paths)
    modules = scan_modules(VAR_MODULES)
    engine_cols = scan_engine_cols(VAR_MODULES)
    modules_by_col = build_module_col_index(modules, engine_cols)
    raw_existing, existing = load_existing_yaml(YAML_PATH)
    extra = yaml.safe_load(SS_CONFIG.read_text(encoding="utf-8")).get("extra_vars", []) or []

    all_canonical = set(canonical.keys()) | {e["name"] for e in extra}
    in_yaml = set(existing.keys())

    proposed, missing_after, todo = assemble(canonical, extra, modules_by_col, existing)
    dead = sorted(in_yaml - all_canonical)
    dead_triage = triage_dead(dead, existing, modules_by_col)

    # --- Emit proposed_variables.yaml ---
    header = (
        "# =============================================================================\n"
        "# F1D Variable Registry — Authoritative Source (REBUILT)\n"
        "# =============================================================================\n"
        "# Generated by: tools/rebuild_variables_yaml.py\n"
        f"# Total entries: {len(proposed)}\n"
        f"# From: {len(spec_paths)} specs + {len(modules)} modules + hand-stubs\n"
        "#\n"
        "# DO NOT manually edit this generated file directly. Workflow:\n"
        "#   1. Edit upstream sources (specs / modules / engines / hand-stubs in tools/rebuild)\n"
        "#   2. Rerun tools/rebuild_variables_yaml.py\n"
        "#   3. Diff candidate vs config/variables.yaml; splice if approved\n"
        "# =============================================================================\n"
    )
    # Preserve manifest entry from existing YAML
    manifest_entry = raw_existing.get("variables", {}).get("manifest")
    # REVIEW entries: dead but module-exported (kept commented in final YAML)
    review_entries = [(d["col"], existing[d["col"]]) for d in dead_triage if d["rec"] == "REVIEW"]

    proposed_yaml = emit_proposed_yaml(proposed, header,
                                        manifest_entry=manifest_entry,
                                        review_entries=review_entries)
    (OUT_DIR / "proposed_variables.yaml").write_text(proposed_yaml, encoding="utf-8")

    # --- Emit diff_report.md ---
    diff_lines = ["# YAML rebuild diff report\n"]
    diff_lines.append(f"- Specs scanned: {len(spec_paths)}")
    diff_lines.append(f"- Modules scanned: {len(modules)}")
    diff_lines.append(f"- Engine COLS lists: {len(engine_cols)} columns indexed")
    diff_lines.append(f"- Existing YAML entries (by column): {len(in_yaml)}")
    diff_lines.append(f"- Canonical scope (specs + extra_vars): {len(all_canonical)}")
    diff_lines.append(f"- **Proposed entries:** {len(proposed)}")
    diff_lines.append(f"- **Missing-after-all-sources:** {len(missing_after)} (should be 0)")
    diff_lines.append(f"- **Dead entries (drop candidates):** {len(dead)}")
    diff_lines.append(f"- **TODO items needing manual completion:** {len(todo)}")
    diff_lines.append("\n## Missing after all sources (should be 0)\n")
    for v in missing_after:
        diff_lines.append(f"- `{v}`")
    (OUT_DIR / "diff_report.md").write_text("\n".join(diff_lines), encoding="utf-8")

    # --- Emit dead_review.md ---
    dr_lines = ["# Dead entry triage\n",
                "Recommendations for the 50 entries in YAML but not in any current spec.",
                "Manual review required before pruning.\n",
                "| Column | YAML entry | Ref | Recommend | Reason |",
                "|---|---|---|---|---|"]
    for d in dead_triage:
        dr_lines.append(f"| `{d['col']}` | `{d['entry_name']}` | {d['ref'] or '—'} | "
                        f"**{d['rec']}** | {d['reason']} |")
    (OUT_DIR / "dead_review.md").write_text("\n".join(dr_lines), encoding="utf-8")

    # --- Emit hand_stub_residual.md ---
    hs_lines = ["# Hand-stub residual TODO list\n",
                "Items that need manual completion before splice. "
                "Rerunning the script will regenerate the same TODO markers.\n"]
    for item in todo:
        hs_lines.append(f"- {item}")
    (OUT_DIR / "hand_stub_residual.md").write_text("\n".join(hs_lines), encoding="utf-8")

    # --- Validate ---
    try:
        reparsed = yaml.safe_load(proposed_yaml)
        n_entries = len(reparsed.get("variables", {}))
        validation = f"OK — re-parsed {n_entries} entries"
    except Exception as e:
        validation = f"FAIL — {e}"

    print(f"WROTE {OUT_DIR.relative_to(ROOT)}/proposed_variables.yaml ({len(proposed)} entries)")
    print(f"WROTE {OUT_DIR.relative_to(ROOT)}/diff_report.md")
    print(f"WROTE {OUT_DIR.relative_to(ROOT)}/dead_review.md ({len(dead)} entries)")
    print(f"WROTE {OUT_DIR.relative_to(ROOT)}/hand_stub_residual.md ({len(todo)} TODO)")
    print(f"Validation: {validation}")


if __name__ == "__main__":
    main()
