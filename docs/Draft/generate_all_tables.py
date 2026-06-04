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

import subprocess
from pathlib import Path

import yaml

from f1d.shared.outputs import load_suite_spec, render_suite

REPO_ROOT = Path(__file__).resolve().parents[2]  # docs/Draft/<script> → repo root
ECONOMETRIC = REPO_ROOT / "outputs" / "econometric"
RENDER_ORDER = REPO_ROOT / "config" / "suite_render_order.yaml"
PER_SUITE_DIR = Path(__file__).resolve().parent / "per_suite"

# Hand-curated benchmark/replication tables that appear in thesis_tables.tex but
# are NOT produced by the suite-spec render path. Each is a standalone fragment
# emitted by its own gen_*.py (see per-fragment comments below). They were
# previously appended to thesis_tables.tex by hand — which a regen silently
# dropped. Listing them here makes the generated thesis_tables.tex complete and
# reproducible. The block starts with its own \clearpage (separates it from the
# last rendered suite). Keep in sync with the gen_*.py fragment outputs.
THESIS_FRAGMENT_BLOCK = [
    r"\clearpage",
    r"% Campello Table-8 rebuild — generated from step6 summary.json by",
    r"% scripts/campello_rebuild/gen_thesis_t8_table.py (NOT hand-edited).",
    r"% Regenerate: python scripts/campello_rebuild/gen_thesis_t8_table.py",
    r"\input{_campello_rebuild_t8}",
    r"\clearpage",
    r"% Campello variable forensic audit — summary-stats compare (3 panels),",
    r"% generated from tmp/campello_summary_stats_compare_2026_05_17.md by",
    r"% scripts/campello_rebuild/gen_summary_stats_tex.py (NOT hand-edited).",
    r"% Regenerate: python scripts/campello_rebuild/gen_summary_stats_tex.py",
    r"\input{_campello_summary_stats}",
    r"\clearpage",
    r"% Disclosure-Law DiD — compact 3-col (Boasiako published benchmark |",
    r"% our cash clone | our UncResCEO DV), canonical industry+state+year spec.",
    r"% Generated from the latest run's suite_spec JSON by",
    r"% scripts/gen_disclosure_law_compact_table.py (NOT hand-edited).",
    r"% Regenerate: python scripts/gen_disclosure_law_compact_table.py",
    r"\input{_disclosure_law_compact}",
    r"",
    r"\newpage",
    r"\input{_boasiako_summary_stats}",
    r"\clearpage",
    r"% Empire-Building reverse-causality probe — pre-acquisition cash war-chest +",
    r"% CEO uncertainty run-up test (two-way FE OLS; within-firm pre-window mean",
    r"% shift, NOT a pre/post DiD). Generated from SDC + H1 panel by",
    r"% scripts/gen_empire_did_table.py (NOT hand-edited).",
    r"% Regenerate: python scripts/gen_empire_did_table.py",
    r"\clearpage",
    r"\input{_empire_building_spec}",
    r"\clearpage",
    r"\input{_empire_building_did}",
    r"\clearpage",
    r"% Cash-Scrutiny external validity (Link 1). Regenerate: python scripts/gen_cash_scrutiny_validity_table.py",
    r"\input{_cash_scrutiny_validity}",
    r"\clearpage",
    r"% Cash-Scrutiny channel test (Link 2). Regenerate: python scripts/gen_cash_scrutiny_channel_table.py",
    r"\input{_cash_scrutiny_channel}",
]


def suite_to_slug(suite_id: str) -> str:
    """Filename-safe slug for suite IDs (H11-Lag1 → h11_lag1, H1.1 → h1_1)."""
    return suite_id.lower().replace(".", "_").replace("-", "_")


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
    # All suites (including DiDs) emit canonical SuiteSpec via write_suite_spec().
    # Per-suite failures are tolerated: skip the failed suite + leave its existing
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
    # Thesis pass re-renders with names_only=True so every variable shows its
    # literal pipeline identifier (naming-consistency audit). Re-reads the same
    # on-disk specs — no estimation re-run. Fishing-deck render (tex_by_suite)
    # is left with display labels.
    # H1.5.brexit_did / H1.5.disclosure_law_did are in thesis_suites for main.tex's
    # per_suite \input, but in thesis_tables.tex they appear as the purpose-built
    # comparison fragments (_campello_rebuild_t8 / _disclosure_law_compact) below —
    # skip the generic render here to avoid duplicating them.
    thesis_tables_skip = {"H1.5.brexit_did", "H1.5.disclosure_law_did"}
    # Minimal thesis-table captions: each says ONLY the test (LaTeX prepends "Table N").
    # Overrides the verbose suite_spec caption at render time -> reproducible, no re-run.
    thesis_short_caption = {
        "H1.ceo2.decomp":    "CEO Uncertainty and Cash Holdings",
        "H1.2.ceo2.decomp":  "Cash Holdings: Financial-Constraint Moderation",
        "H1.3.cfvol":        "Cash Holdings: Cash-Flow-Volatility Moderation",
        "H11":               "Political Risk and Call Uncertainty",
        "H11-Lag2":          "Political Risk and Call Uncertainty (Two-Quarter Lag)",
        "H23":               "Product-Market Competition and Call Uncertainty",
        "H24":               "US Policy Uncertainty and Call Uncertainty",
        "H24b":              "Global Policy Uncertainty and Call Uncertainty",
        "H14c.ceo2.decomp":  "CEO Uncertainty and the Bid-Ask Spread",
        "H18.ceo2.decomp":   "CEO Uncertainty and SEC Comment-Letter Receipt",
    }
    # Thesis exhibit shows only the first N columns of a suite (drops robustness
    # variants); the full column set stays in the fishing deck + suite_spec JSON.
    thesis_keep_cols = {"H1.3.cfvol": 8}  # keep CashRatio + CashRatio_lead; drop Robust-FE cols 9-14

    def _thesis_spec(sid):
        spec = load_suite_spec(resolved[sid])
        if sid in thesis_short_caption:
            spec.caption = thesis_short_caption[sid]
        keep = thesis_keep_cols.get(sid)
        if keep and len(spec.columns) > keep:
            spec.columns = spec.columns[:keep]
            trimmed = []
            for row in spec.header_rows:          # keep leading group cells up to `keep` span
                cells, acc = [], 0
                for cell in row:
                    if acc >= keep:
                        break
                    cells.append(cell)
                    acc += cell.span
                trimmed.append(cells)
            spec.header_rows = trimmed
        return spec

    thesis_rendered = [
        render_suite(_thesis_spec(sid), names_only=True)
        for sid in thesis_suite_ids
        if sid in tex_by_suite and sid not in thesis_tables_skip
    ]
    for i, tex in enumerate(thesis_rendered):
        thesis_master.append(tex)
        if i < len(thesis_rendered) - 1:
            thesis_master.append(r"\clearpage")
    # Benchmark fragments (block starts with its own \clearpage) so the
    # generated thesis_tables.tex is complete + reproducible (no hand-append).
    thesis_master.extend(THESIS_FRAGMENT_BLOCK)
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
