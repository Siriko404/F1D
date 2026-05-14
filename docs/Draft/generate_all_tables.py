#!/usr/bin/env python3
"""Consolidate all 37 thesis regression tables from suite_spec_*.json files.

Post-Phase-8 architecture: iterates `config/suite_render_order.yaml` and
finds the newest suite_spec_<id>.json for each suite via filesystem glob.
No hardcoded SUITES dict, no parse_txt, no IV display maps — everything
is driven by the runner-written canonical JSON spec.

Pipeline:
    runner.py  ──writes──▶  suite_spec_<id>.json
                                    │
                                    ▼
                        load_suite_spec() (pydantic)
                                    │
                                    ▼
                        render_suite(spec) → LaTeX chunk
                                    │
                                    ▼
                    all_tables.tex (master doc) + pdflatex
"""

import json
import subprocess
from pathlib import Path

import yaml

from f1d.shared.outputs import load_suite_spec, render_suite

REPO_ROOT = Path(__file__).resolve().parents[2]  # docs/Draft/<script> → repo root
ECONOMETRIC = REPO_ROOT / "outputs" / "econometric"
RENDER_ORDER = REPO_ROOT / "config" / "suite_render_order.yaml"
PER_SUITE_DIR = Path(__file__).resolve().parent / "per_suite"


def suite_to_slug(suite_id: str) -> str:
    """Filename-safe slug for suite IDs (H11-Lag1 → h11_lag1, H1.1 → h1_1)."""
    return suite_id.lower().replace(".", "_").replace("-", "_")


def _parse_md_table(md_text: str) -> tuple[list[str], list[list[str]]]:
    """Parse the FIRST GitHub-style markdown table out of md_text."""
    headers: list[str] | None = None
    rows: list[list[str]] = []
    in_table = False
    for ln in md_text.splitlines():
        ln = ln.strip()
        if ln.startswith("|") and ln.endswith("|"):
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if headers is None:
                headers = cells
                in_table = True
            elif all(set(c) <= set("-:") for c in cells if c):
                continue
            else:
                rows.append(cells)
        elif in_table and not ln.startswith("|"):
            break
    return headers or [], rows


def _sig_stars(p_one_str: str) -> str:
    try:
        p = float(p_one_str)
    except (ValueError, TypeError):
        return ""
    if p < 0.01:
        return r"$^{***}$"
    if p < 0.05:
        return r"$^{**}$"
    if p < 0.10:
        return r"$^{*}$"
    return ""


def _render_did_stub(suite_spec_path: Path) -> str | None:
    """Fallback renderer for DiD suites whose suite_spec.json is a stub
    (no `columns` array). Reads the report_step4_*.md sibling and produces a
    landscape LaTeX table block. Returns None if the suite is not a recognised
    stub (so the caller can fall through to the normal failure branch).
    """
    try:
        spec_obj = json.loads(suite_spec_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if "columns" in spec_obj or ("treatments" not in spec_obj and "treatment" not in spec_obj):
        return None  # not a DiD stub — let caller handle as a real failure

    out_dir = suite_spec_path.parent
    md_candidates = list(out_dir.glob("report_step4_*.md"))
    if not md_candidates:
        return None
    headers, rows = _parse_md_table(md_candidates[0].read_text(encoding="utf-8"))
    if not headers or not rows:
        return None

    suite_id = spec_obj.get("suite_id", "?")
    title = spec_obj.get("title", suite_id)
    label = spec_obj.get("label", f"tab:{suite_to_slug(suite_id)}")
    n_cells = len(rows)

    # Locate columns by header name (resilient to extra columns like `block`).
    def col_idx(name: str) -> int | None:
        for i, h in enumerate(headers):
            if h.lower() == name:
                return i
        return None

    i_col, i_dv, i_tr, i_fe, i_n, i_beta, i_p = (
        col_idx("col"), col_idx("dv"), col_idx("treatment"),
        col_idx("fe"), col_idx("n"), col_idx("beta"), col_idx("p_one"),
    )
    if None in (i_col, i_dv, i_tr, i_fe, i_n, i_beta, i_p):
        return None

    cspec = "".join(["c"] * n_cells)
    col_nums = " & ".join(f"({r[i_col]})" for r in rows)
    dv_row = " & ".join(r[i_dv].replace("_", r"\_") for r in rows)
    tr_row = " & ".join(r[i_tr].replace("_", r"\_") for r in rows)
    fe_row = " & ".join(r[i_fe].replace("_", r"\_") for r in rows)
    n_row = " & ".join(f"{int(r[i_n].replace(',','')):,}" for r in rows)

    beta_cells, p_cells = [], []
    for r in rows:
        beta_s = r[i_beta]
        p_one = r[i_p]
        stars = _sig_stars(p_one)
        wrapped = f"\\textbf{{{beta_s}}}{stars}" if stars else beta_s
        beta_cells.append(wrapped)
        p_cells.append(f"[{p_one}]" if p_one not in ("nan", "") else "[--]")

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{0.9}",
        r"\centering",
        r"\caption{" + title.replace("_", r"\_") + "}",
        r"\label{" + label + "}",
        r"\scriptsize",
        r"\begin{tabular}{l" + cspec + "}",
        r"\toprule",
        r" & " + col_nums + r" \\",
        r"Dependent var & " + dv_row + r" \\",
        r"Treatment & " + tr_row + r" \\",
        r"FE specification & " + fe_row + r" \\",
        r"\midrule",
        r"Treatment $\times$ Post (DiD) & " + " & ".join(beta_cells) + r" \\",
        r" & " + " & ".join(p_cells) + r" \\",
        r"\midrule",
        r"N (obs) & " + n_row + r" \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\\[2pt]",
        r"\scriptsize\textit{Note: One-tailed $p$-values in brackets. Sig: $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$. SEs not surfaced in stub-schema runners; full per-cell output in \texttt{regression\_results\_col*.txt}.}",
        r"\end{table}",
        "",
    ])


def to_main_chunk(chunk: str) -> str:
    """Wrap chunk in pdflscape landscape env so the PDF page itself rotates 90°.

    Unlike `sidewaystable` (which rotates *content* on a portrait page — viewer
    must be rotated by the reader), `pdflscape`'s `\\begin{landscape}` env emits
    a /Rotate directive into the PDF that auto-rotates the page in the viewer.
    Tables display right-side-up in landscape orientation when scrolling.

    `[H]` (from `float` pkg) forces the table inline within the landscape block
    instead of floating outside it. `\\tabcolsep=3pt` keeps the widest table
    (H13.2 16-col) within landscape textwidth.

    Standalone all_tables.tex is unchanged (already landscape geometry).
    """
    swapped = chunk.replace(
        r"\begin{table}[htbp]",
        "\\begin{table}[H]\n\\setlength{\\tabcolsep}{3pt}\n"
        "\\renewcommand{\\arraystretch}{0.85}",
    )
    return "\\begin{landscape}\n" + swapped + "\n\\end{landscape}"


def find_latest_spec_path(suite_id: str) -> Path | None:
    """Return the newest suite_spec_<id>.json across all timestamped dirs.

    Dir structure: outputs/econometric/<runner_dir>/<YYYY-MM-DD_HHMMSS>/suite_spec_<id>.json
    The newest is picked by lexicographic sort of timestamp dir names.
    Returns None if no matching spec file exists.
    """
    pattern = f"**/suite_spec_{suite_id}.json"
    matches = sorted(ECONOMETRIC.glob(pattern), reverse=True)
    return matches[0] if matches else None


def main() -> int:
    out_dir = Path(__file__).resolve().parent

    if not RENDER_ORDER.exists():
        print(f"[error] render order config missing: {RENDER_ORDER}")
        return 1
    render_cfg = yaml.safe_load(RENDER_ORDER.read_text(encoding="utf-8"))
    suite_ids: list[str] = render_cfg["suites"]
    thesis_suite_ids: list[str] = render_cfg.get("thesis_suites", suite_ids)
    # Validate thesis subset is a subset of full list
    unknown = [sid for sid in thesis_suite_ids if sid not in suite_ids]
    if unknown:
        print(f"[error] thesis_suites contains IDs not in suites: {unknown}")
        return 1

    # Resolve every suite's spec file up-front so the user sees any missing
    # specs before rendering starts.
    print("Resolving latest suite_spec files:")
    resolved: dict[str, Path] = {}
    for suite_id in suite_ids:
        spec_path = find_latest_spec_path(suite_id)
        marker = "" if spec_path is not None else "  [MISSING]"
        rel = spec_path.relative_to(REPO_ROOT) if spec_path else "n/a"
        print(f"  {suite_id:<10} -> {rel}{marker}")
        if spec_path is not None:
            resolved[suite_id] = spec_path
    print()

    missing = [sid for sid in suite_ids if sid not in resolved]
    if missing:
        print(f"[error] Missing spec files for: {', '.join(missing)}")
        print("        Run the corresponding runner(s) to emit suite_spec_<id>.json.")
        return 1

    # Generate per-suite LaTeX chunks.
    # Per-suite failures (e.g., non-canonical schemas in DiD/IV/FD endogeneity
    # suites) are tolerated: we skip the failed suite + leave its existing
    # per_suite/<slug>_table.tex fragment in place. Hard-fail only if EVERY
    # suite fails (likely a schema-wide regression).
    tex_by_suite: dict[str, str] = {}
    failed_suites: list[str] = []
    for suite_id in suite_ids:
        print(f"Generating {suite_id}...")
        try:
            spec = load_suite_spec(resolved[suite_id])
            tex = render_suite(spec)
            tex_by_suite[suite_id] = tex
            print("  OK")
        except Exception as exc:
            # Fallback: DiD stub-schema suites (Brexit, Boasiako disclosure-law)
            # emit minimal suite_spec.json without `columns`. Render directly from
            # their report_step4_*.md sibling.
            stub_tex = _render_did_stub(resolved[suite_id])
            if stub_tex is not None:
                tex_by_suite[suite_id] = stub_tex
                print("  OK (DiD stub fallback)")
            else:
                first_line = str(exc).split("\n", 1)[0]
                print(f"  FAILED: {first_line}")
                failed_suites.append(suite_id)

    if failed_suites:
        print(
            f"\n[warning] {len(failed_suites)} suite(s) failed to render: "
            f"{', '.join(failed_suites)}. Their per_suite/<slug>_table.tex "
            f"fragments retain their previous content."
        )
    if not tex_by_suite:
        print("[error] All suites failed to render.")
        return 1

    # Assemble master document.
    master = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[margin=1.2cm,landscape]{geometry}",
        r"\usepackage{booktabs}",
        r"\usepackage{amsmath}",
        r"\usepackage{newtxtext,newtxmath}",
        r"\usepackage{graphicx}",
        r"\usepackage{float}",
        r"\pagestyle{plain}",
        r"\pagenumbering{arabic}",
        r"\begin{document}",
    ]
    rendered_in_order = [tex_by_suite[sid] for sid in suite_ids if sid in tex_by_suite]
    for i, tex in enumerate(rendered_in_order):
        master.append(tex)
        if i < len(rendered_in_order) - 1:
            master.append(r"\clearpage")
    master.append(r"\end{document}")

    tex_path = out_dir / "all_tables.tex"
    tex_path.write_text("\n".join(master), encoding="utf-8")
    print(f"\nWrote {tex_path}")

    # Parallel emit: thesis_tables.tex — identical preamble as all_tables.tex
    # but filtered to thesis_suite_ids only. Compiled in same pass below.
    thesis_master = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[margin=1.2cm,landscape]{geometry}",
        r"\usepackage{booktabs}",
        r"\usepackage{amsmath}",
        r"\usepackage{newtxtext,newtxmath}",
        r"\usepackage{graphicx}",
        r"\usepackage{float}",
        r"\pagestyle{plain}",
        r"\pagenumbering{arabic}",
        r"\begin{document}",
    ]
    thesis_rendered = [tex_by_suite[sid] for sid in thesis_suite_ids if sid in tex_by_suite]
    for i, tex in enumerate(thesis_rendered):
        thesis_master.append(tex)
        if i < len(thesis_rendered) - 1:
            thesis_master.append(r"\clearpage")
    thesis_master.append(r"\end{document}")
    thesis_tex_path = out_dir / "thesis_tables.tex"
    thesis_tex_path.write_text("\n".join(thesis_master), encoding="utf-8")
    print(f"Wrote {thesis_tex_path} ({len(thesis_rendered)} thesis suites)")

    # Per-suite content-only fragments (Step 8.5): for inclusion via
    # \input{per_suite/<slug>_table.tex} into main.tex. Each fragment swaps
    # `\begin{table}` → `\begin{sidewaystable*}[p]` so it rotates to landscape
    # and spans both columns of the twocolumn portrait master document.
    PER_SUITE_DIR.mkdir(exist_ok=True)
    print(f"\nWriting per-suite fragments to {PER_SUITE_DIR.relative_to(REPO_ROOT)}/")

    # Render every fragment to disk regardless of inclusion scope (so any suite
    # is available for body \input even before being added to thesis_suites).
    # Failed suites are skipped — their pre-existing fragment files are kept.
    n_written = 0
    for suite_id in suite_ids:
        if suite_id not in tex_by_suite:
            continue
        slug = suite_to_slug(suite_id)
        fragment_path = PER_SUITE_DIR / f"{slug}_table.tex"
        fragment_path.write_text(to_main_chunk(tex_by_suite[suite_id]), encoding="utf-8")
        n_written += 1

    # Two include files: full fishing deck (all suites) + thesis-only subset.
    def _write_include(out_name: str, scope_ids: list[str], header_note: str) -> None:
        lines = [
            r"% Auto-generated by docs/Draft/generate_all_tables.py — DO NOT EDIT",
            f"% {header_note}",
            r"% pdflscape's \begin{landscape} env issues \clearpage at start + end of each block.",
        ]
        for sid in scope_ids:
            slug = suite_to_slug(sid)
            lines.append(f"\\input{{per_suite/{slug}_table.tex}}")
        (PER_SUITE_DIR / out_name).write_text("\n".join(lines) + "\n", encoding="utf-8")

    _write_include(
        "_fishing_deck_input.tex",
        suite_ids,
        f"Fishing deck: ALL {len(suite_ids)} suites. Inclusion target: standalone reference doc.",
    )
    _write_include(
        "_thesis_input.tex",
        thesis_suite_ids,
        f"Thesis subset: {len(thesis_suite_ids)} suites cited in main.pdf body / appendices.",
    )
    print(f"  {n_written}/{len(suite_ids)} fragments regenerated + 2 include files written "
          f"(_fishing_deck_input.tex={len(suite_ids)} + _thesis_input.tex={len(thesis_suite_ids)}).")

    # Compile PDFs (all_tables.pdf + thesis_tables.pdf).
    for label, target in [("all_tables", tex_path), ("thesis_tables", thesis_tex_path)]:
        print(f"Compiling {label}.pdf...")
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", str(target)],
            cwd=str(out_dir),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"SUCCESS: {out_dir / (label + '.pdf')}")
        else:
            print(f"FAILED ({label}):")
            for line in result.stdout.split("\n"):
                if "!" in line or "Error" in line:
                    print(f"  {line}")
            return 1
        # Clean up pdflatex auxiliary files.
        for ext in (".aux", ".log"):
            aux_file = out_dir / f"{label}{ext}"
            if aux_file.exists():
                aux_file.unlink()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
