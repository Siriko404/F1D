#!/usr/bin/env python3
"""Verify outputs/all_tables.tex matches model_diagnostics.csv for every suite.

Strategy:
  1. Import SUITES + resolve_suite_dir from outputs/generate_all_tables.py.
  2. For each suite, resolve the latest run dir and look for model_diagnostics.csv.
     - If no CSV: report SKIPPED as prebuilt.
  3. Auto-detect IVs in the CSV (columns ending in _beta). Handle three schemas:
       (a) standard: UncAnsCEO_beta, UncPreCEO_beta, UncAnsMgr_beta, UncPreMgr_beta
       (b) H23 moderation: z_log_TotalSimilarity_beta (key_vars[0])
       (c) H24 macro: bare `beta` + `beta_p_one` + `macro_iv` col  -> map to suite.key_vars[0]
  4. For each suite, pick 2 random (col, IV) pairs (deterministic seed per suite).
  5. Look up table in all_tables.tex via \\label{suite['label']}; find the row for the
     IV (matching `tex_escape(var)` or suite.key_labels[0]); extract the Nth cell;
     parse out the number and star count.
  6. Compare CSV beta (4 decimals) and recomputed star count against LaTeX cell.
"""

from __future__ import annotations

import hashlib
import importlib.util
import random
import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(r"C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D")
GEN_PY = REPO / "outputs" / "generate_all_tables.py"
TEX = REPO / "outputs" / "all_tables.tex"


def load_generator():
    spec = importlib.util.spec_from_file_location("gen_all", GEN_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gen_all"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------- LaTeX parsing ----------

def load_tex_blocks(tex_path):
    """Return dict: label -> list of raw lines in the table."""
    text = tex_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    blocks = {}
    current_label = None
    current = []
    for line in lines:
        m = re.search(r"\\label\{([^}]+)\}", line)
        if m:
            if current_label is not None:
                blocks[current_label] = current
            current_label = m.group(1)
            current = [line]
        else:
            if current_label is not None:
                current.append(line)
                if r"\end{tabular}" in line:
                    blocks[current_label] = current
                    current_label = None
                    current = []
    if current_label is not None:
        blocks[current_label] = current
    return blocks


def parse_latex_cell(cell):
    """Parse a LaTeX cell like '\\textbf{0.0038}$^{***}$' or '0.0002' or empty.

    Returns (value_float_or_None, stars_str).
    """
    s = cell.strip()
    if not s:
        return (None, "")
    # Extract star count
    star_match = re.search(r"\$?\^\{(\*+)\}\$?", s)
    stars = star_match.group(1) if star_match else ""
    # Remove textbf, math, stars, braces
    s2 = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s2 = re.sub(r"\$?\^\{[^}]*\}\$?", "", s2)
    s2 = s2.replace("{", "").replace("}", "").strip()
    try:
        val = float(s2)
    except ValueError:
        val = None
    return (val, stars)


def split_cells(row_line):
    """Split a LaTeX table row on '&', stripping the trailing \\\\."""
    line = row_line.rstrip()
    # remove trailing \\
    if line.endswith(r"\\"):
        line = line[:-2]
    parts = line.split("&")
    return [p.strip() for p in parts]


def find_iv_row(block_lines, iv_label_escaped):
    """Find the first row whose first cell equals iv_label_escaped.

    iv_label_escaped is the string as it appears in the LaTeX (already escaped).
    """
    for i, line in enumerate(block_lines):
        cells = split_cells(line)
        if not cells:
            continue
        first = cells[0].strip()
        if first == iv_label_escaped:
            return i, cells
    return None, None


# ---------- Star computation ----------

def stars_from_t(beta, se, tail, hyp_dir):
    """Recompute stars from beta and SE (ignoring CSV p column which is
    inconsistently labeled across runners).

    Mirrors generate_all_tables.fmt_coef logic: takes p_two from |t|, then
    halves for one-tailed if sign matches direction.
    """
    from scipy.stats import t as tdist

    if se is None or pd.isna(se) or se == 0:
        return None  # can't compute
    tval = float(beta) / float(se)
    # Approximate df with very large (regression DFs are typically >> 1000)
    p_two = 2 * (1 - tdist.cdf(abs(tval), df=100000))

    # Normalize tail
    if tail == "one_pos":
        tail_eff = "one"; hd = ">"
    elif tail == "one_neg":
        tail_eff = "one"; hd = "<"
    else:
        tail_eff = tail; hd = hyp_dir

    if tail_eff == "one":
        if hd == ">" and beta <= 0:
            return ""
        if hd == "<" and beta >= 0:
            return ""
        p_test = p_two / 2
    else:
        p_test = p_two

    if p_test < 0.01:
        return "***"
    if p_test < 0.05:
        return "**"
    if p_test < 0.10:
        return "*"
    return ""


# ---------- CSV IV detection ----------

def detect_csv_ivs(df, suite):
    """Return list of (csv_iv_name, latex_iv_label, beta_col, se_col) tuples."""
    cols = df.columns.tolist()
    result = []

    # Handle macro (bare beta with macro_iv field) — H24/H24b/H25
    if "macro_iv" in cols and "beta" in cols:
        if suite.get("key_vars") and suite.get("key_labels"):
            label = suite["key_labels"][0]
            result.append(("__MACRO__", label, "beta", "beta_se"))
        return result

    # Handle H23 style moderation with key IV in a specific column
    if "beta_iv" in cols and suite.get("type") == "moderation" and suite.get("key_vars"):
        key_var = suite["key_vars"][0]
        beta_col = f"{key_var}_beta"
        se_col = f"{key_var}_se"
        if beta_col in cols and se_col in cols:
            result.append((key_var, suite["key_labels"][0], beta_col, se_col))
        return result

    # Standard schema: {IV}_beta
    iv_betas = [c for c in cols if c.endswith("_beta")]
    std_ivs = {"UncAnsCEO", "UncPreCEO", "UncAnsMgr", "UncPreMgr"}
    for bcol in iv_betas:
        name = bcol[:-len("_beta")]
        if name in std_ivs:
            se_col = f"{name}_se"
            if se_col in cols:
                result.append((name, name, bcol, se_col))
    return result


# ---------- Main verification ----------

def verify_suite(suite, resolve_suite_dir, tex_blocks, rng):
    label = suite["label"]
    suite_id = suite["id"]
    dir_value = suite["dir"]
    try:
        suite_dir = resolve_suite_dir(dir_value)
    except Exception as e:
        return {"status": "ERROR", "id": suite_id, "msg": f"resolve failed: {e}"}

    csv_path = suite_dir / "model_diagnostics.csv"
    if not csv_path.exists():
        return {"status": "SKIPPED", "id": suite_id, "msg": "no model_diagnostics.csv"}

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return {"status": "ERROR", "id": suite_id, "msg": f"CSV read failed: {e}"}

    ivs = detect_csv_ivs(df, suite)
    if not ivs:
        return {"status": "SKIPPED", "id": suite_id, "msg": "no IVs detected in CSV"}

    if label not in tex_blocks:
        return {"status": "ERROR", "id": suite_id, "msg": f"label {label} not in all_tables.tex"}

    block = tex_blocks[label]

    n_cols = suite["cols"]
    col_offset = suite.get("col_offset", 0)
    tail = suite.get("tail")
    # For suites without top-level tail (e.g. H23/H24/H24b/H25), use key_tails[0]
    if tail is None and suite.get("key_tails"):
        tail = suite["key_tails"][0]
    if tail is None:
        tail = "two"
    hyp_dir = suite.get("hyp_dir")

    # Pick 2 random (col, iv) pairs — col is the LaTeX display column (1..n_cols)
    all_pairs = [(c, iv) for c in range(1, n_cols + 1) for iv in ivs]
    if not all_pairs:
        return {"status": "SKIPPED", "id": suite_id, "msg": "no pairs"}
    k = min(2, len(all_pairs))
    sample = rng.sample(all_pairs, k)

    mismatches = []
    checks = []

    for display_col, iv in sample:
        csv_iv_name, latex_label, beta_col, p_col, p_kind = iv
        csv_col = display_col + col_offset  # map LaTeX col -> CSV col
        row = df[df["col"] == csv_col]
        if row.empty:
            mismatches.append({
                "suite": suite_id, "col": display_col, "iv": latex_label,
                "csv_val": None, "tex_val": None,
                "delta": None, "note": f"CSV has no row for col={csv_col}",
            })
            continue
        r = row.iloc[0]
        csv_beta = r.get(beta_col)
        csv_p = r.get(p_col) if p_col in df.columns else None
        if pd.isna(csv_beta):
            checks.append({
                "suite": suite_id, "col": display_col, "iv": latex_label,
                "csv_val": None, "tex_val": None, "ok": True, "note": "CSV NaN; skipped",
            })
            continue

        csv_beta_r4 = round(float(csv_beta), 4)
        csv_stars = stars_from_p(
            float(csv_p) if csv_p is not None and not pd.isna(csv_p) else None,
            p_kind, float(csv_beta), tail, hyp_dir,
        )

        # Find LaTeX row
        _, cells = find_iv_row(block, latex_label)
        if cells is None:
            mismatches.append({
                "suite": suite_id, "col": display_col, "iv": latex_label,
                "csv_val": f"{csv_beta_r4}{csv_stars}", "tex_val": "ROW_NOT_FOUND",
                "delta": None, "note": "row not found in tex block",
            })
            continue

        # Nth data cell: cells[0] is the label, cells[1..N] are col 1..N
        if display_col >= len(cells):
            mismatches.append({
                "suite": suite_id, "col": display_col, "iv": latex_label,
                "csv_val": f"{csv_beta_r4}{csv_stars}", "tex_val": "CELL_OOB",
                "delta": None, "note": f"only {len(cells)-1} cells in row",
            })
            continue
        tex_cell = cells[display_col]
        tex_val, tex_stars = parse_latex_cell(tex_cell)

        if tex_val is None:
            mismatches.append({
                "suite": suite_id, "col": display_col, "iv": latex_label,
                "csv_val": f"{csv_beta_r4}{csv_stars}", "tex_val": "(empty)",
                "delta": None, "note": "tex cell empty but CSV has value",
            })
            continue

        delta = abs(tex_val - csv_beta_r4)
        stars_ok = (tex_stars == csv_stars)
        beta_ok = delta <= 1e-4 + 5e-5  # allow rounding

        if beta_ok and stars_ok:
            checks.append({
                "suite": suite_id, "col": display_col, "iv": latex_label,
                "csv_val": f"{csv_beta_r4}{csv_stars}",
                "tex_val": f"{tex_val}{tex_stars}", "ok": True,
            })
        else:
            mismatches.append({
                "suite": suite_id, "col": display_col, "iv": latex_label,
                "csv_val": f"{csv_beta_r4}{csv_stars}",
                "tex_val": f"{tex_val}{tex_stars}",
                "delta": round(delta, 6),
                "note": ("stars_mismatch" if not stars_ok and beta_ok else
                         "beta_mismatch" if not beta_ok and stars_ok else
                         "both_mismatch"),
            })

    if mismatches:
        return {"status": "FAIL", "id": suite_id, "mismatches": mismatches, "checks": checks}
    return {"status": "PASS", "id": suite_id, "checks": checks}


def main():
    gen = load_generator()
    suites = gen.SUITES
    resolve_suite_dir = gen.resolve_suite_dir
    tex_blocks = load_tex_blocks(TEX)

    results = []
    for suite in suites:
        # Deterministic seed per suite id (stable across runs)
        seed = int(hashlib.md5(suite["id"].encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)
        r = verify_suite(suite, resolve_suite_dir, tex_blocks, rng)
        results.append(r)

    # ---- Report ----
    passed = [r for r in results if r["status"] == "PASS"]
    skipped = [r for r in results if r["status"] == "SKIPPED"]
    failed = [r for r in results if r["status"] == "FAIL"]
    errored = [r for r in results if r["status"] == "ERROR"]

    total = len(results)
    verified = len(passed)

    print("=" * 72)
    print(f"VERIFIED ({verified}/{total} suites, 2 cells each):")
    print("  " + ", ".join(r["id"] for r in passed) if passed else "  (none)")
    print()
    print(f"SKIPPED (prebuilt or no CSV) ({len(skipped)}):")
    for r in skipped:
        print(f"  {r['id']}: {r['msg']}")
    if not skipped:
        print("  (none)")
    print()
    if errored:
        print(f"ERRORS ({len(errored)}):")
        for r in errored:
            print(f"  {r['id']}: {r['msg']}")
        print()
    print(f"MISMATCHES ({len(failed)}):")
    if not failed:
        print("  None")
    else:
        for r in failed:
            for m in r["mismatches"]:
                print(f"  {m['suite']} col={m['col']} iv={m['iv']}  "
                      f"CSV={m['csv_val']}  TEX={m['tex_val']}  "
                      f"delta={m['delta']}  note={m['note']}")
    print("=" * 72)

    return 0 if not failed and not errored else 1


if __name__ == "__main__":
    sys.exit(main())
