"""Generate sample attrition tables for paper submission.

Creates both CSV and LaTeX formats documenting sample size changes
through filter stages (e.g., master manifest → complete cases → min calls).

Usage:
    from f1d.shared.outputs import generate_attrition_table

    stages = [
        ("Master manifest", 112968),
        ("Main sample filter", 88205),
        ("After complete-case filter", 65432),
        ("After min-calls filter", 57845),
    ]
    generate_attrition_table(stages, out_dir, "H0.3 Extended Controls")
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pandas as pd


def generate_attrition_table(
    stages: List[Tuple[str, int]],
    output_dir: Path,
    suite_name: str,
) -> Tuple[Path, Path]:
    """Generate sample_attrition.csv and sample_attrition.tex.

    Args:
        stages: List of (stage_name, row_count) tuples in order of filtering
        output_dir: Directory to write output files
        suite_name: Hypothesis suite name for table caption

    Returns:
        Tuple of (csv_path, tex_path)
    """
    # Build DataFrame with derived columns
    df = pd.DataFrame(stages, columns=["Filter Stage", "N"])
    df["N Lost"] = df["N"].diff().fillna(0).astype(int)
    df["% Retained"] = (df["N"] / df["N"].iloc[0] * 100).round(1)

    # Save CSV
    csv_path = output_dir / "sample_attrition.csv"
    df.to_csv(csv_path, index=False)

    # Save LaTeX
    tex_path = output_dir / "sample_attrition.tex"
    _generate_tex(df, tex_path, suite_name)

    return csv_path, tex_path


def _generate_tex(df: pd.DataFrame, path: Path, suite_name: str) -> None:
    """Generate LaTeX table from attrition DataFrame.

    Creates a formatted table with proper column alignment and
    thousand separators for numbers.
    """
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        rf"\caption{{Sample Attrition: {suite_name}}}",
        rf"\label{{tab:sample_attrition_{_sanitize_label(suite_name)}}}",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Filter Stage & N & N Lost & \% Retained \\",
        r"\midrule",
    ]

    for _, row in df.iterrows():
        stage = _escape_latex(str(row["Filter Stage"]))
        n = int(row["N"])
        n_lost = int(row["N Lost"])
        pct_retained = row["% Retained"]
        lines.append(
            f"{stage} & {n:,} & {n_lost:,} & {pct_retained:.1f}\\% \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _sanitize_label(name: str) -> str:
    """Convert suite name to valid LaTeX label.

    Replaces spaces and special characters with underscores.
    """
    return (
        name.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
        .replace("(", "")
        .replace(")", "")
    )


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters in text."""
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


__all__ = ["generate_attrition_table"]
