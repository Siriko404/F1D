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
    all_tex: list[str] = []
    for suite_id in suite_ids:
        print(f"Generating {suite_id}...")
        try:
            spec = load_suite_spec(resolved[suite_id])
            tex = render_suite(spec)
            all_tex.append(tex)
            print("  OK")
        except Exception as exc:
            print(f"  FAILED: {exc}")
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
    for i, tex in enumerate(all_tex):
        master.append(tex)
        if i < len(all_tex) - 1:
            master.append(r"\clearpage")
    master.append(r"\end{document}")

    tex_path = out_dir / "all_tables.tex"
    tex_path.write_text("\n".join(master), encoding="utf-8")
    print(f"\nWrote {tex_path}")

    # Compile PDF.
    print("Compiling PDF...")
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
        cwd=str(out_dir),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"SUCCESS: {out_dir / 'all_tables.pdf'}")
    else:
        print("FAILED:")
        for line in result.stdout.split("\n"):
            if "!" in line or "Error" in line:
                print(f"  {line}")
        return 1

    # Clean up pdflatex auxiliary files.
    for ext in (".aux", ".log"):
        aux_file = out_dir / f"all_tables{ext}"
        if aux_file.exists():
            aux_file.unlink()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
