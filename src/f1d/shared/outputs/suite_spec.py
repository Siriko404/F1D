"""Write canonical suite_spec.json files from runner state.

Every field in a suite_spec.json file traces back to a single runtime source
in the runner. The helper derives footer-note prose from structured fields
(clustering booleans, tail direction), escapes LaTeX labels, and validates
the result via pydantic before writing to disk.

Public API:
    write_suite_spec(...)       — emit one or more suite_spec_<id>.json files
    extract_coefs_panelols(...) — pull coefs from a linearmodels PanelOLS result
    extract_coefs_logit(...)    — pull AMEs from a statsmodels Logit mfx frame
    load_suite_spec(...)        — read + validate a suite_spec.json file

Multi-sub-table runners (H4, H11-Lag) pass a list with multiple entries in
`sub_tables`, and the helper emits one JSON file per entry.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional

from .suite_spec_schema import (
    Clustering,
    Coef,
    Column,
    Controls,
    HeaderCell,
    IV,
    RenderHints,
    SuiteSpec,
    TailSpec,
)


# ---------------------------------------------------------------------------
# LaTeX helpers
# ---------------------------------------------------------------------------


def _latex_escape_label(name: str) -> str:
    """LaTeX-escape underscores in a variable name for rendering."""
    if "\\_" in name or "$" in name:
        return name  # already escaped or math-mode
    return name.replace("_", r"\_")


# ---------------------------------------------------------------------------
# Footer-note derivation (single source: structured fields → prose)
# ---------------------------------------------------------------------------


def _clustering_footer_note(entity: bool, time: bool) -> str:
    if entity and time:
        return (
            "Standard errors (in parentheses) two-way clustered "
            "(firm, calendar quarter)."
        )
    if entity and not time:
        return "Standard errors (in parentheses) clustered at firm level."
    if not entity and time:
        return (
            "Standard errors (in parentheses) clustered at "
            "calendar-quarter level."
        )
    return (
        "Standard errors (in parentheses) heteroskedasticity-robust "
        "(no clustering)."
    )


def _tail_footer_note(direction: str, applies_to: str) -> str:
    if direction == "none":
        return r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed)."
    sign = ">" if direction == "positive" else "<"
    if applies_to == "ivs_only":
        return (
            r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ "
            rf"(one-tailed for IVs, $\beta {sign} 0$; two-tailed for controls)."
        )
    return (
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ "
        rf"(one-tailed, $\beta {sign} 0$)."
    )


def _build_indicator_rows(
    fe_entity: str,
    fe_time: str,
    control_vars: list[str],
    extended_controls: list[str],
) -> dict[str, str]:
    """Compose Extended Controls / Industry FE / Firm FE / Year FE / Year-Quarter FE cells.

    All five row keys are emitted for every column regardless of which FE the
    column actually uses. Empty values ("") let the renderer suppress rows
    where no column has "Yes" (standard has_firm/has_ind guard pattern).
    """
    has_extended = bool(extended_controls) and any(
        v in control_vars for v in extended_controls
    )
    is_year_fe = fe_time in ("year", "calendar_year")
    is_yq_fe = fe_time in ("year_quarter", "calendar_year_quarter")
    return {
        "Extended Controls": "Yes" if has_extended else "",
        "Industry FE": "Yes" if fe_entity == "industry" else "",
        "Firm FE": "Yes" if fe_entity == "firm" else "",
        "Year FE": "Yes" if is_year_fe else "",
        "Year-Quarter FE": "Yes" if is_yq_fe else "",
    }


# ---------------------------------------------------------------------------
# write_suite_spec
# ---------------------------------------------------------------------------


def write_suite_spec(
    output_dir: Path,
    runner_id: str,
    sub_tables: list[dict[str, Any]],
    coefs_per_col: list[dict[str, dict]],
    col_metadata: list[dict[str, Any]],
    sample_label: str,
    clustering: dict[str, bool],
    tail: dict[str, str],
    ivs: list[dict[str, str]],
    controls: dict[str, Any],
    model_family: str = "PanelOLS",
    render_hints: Optional[dict[str, Any]] = None,
) -> list[Path]:
    """Emit one suite_spec_<suite_id>.json file per entry in sub_tables.

    Args:
        output_dir: Runner's timestamped output directory.
        runner_id: Snake-case runner identifier (e.g. "h1_cash_holdings").
            Used as default `dir_name` for each sub-table.
        sub_tables: One dict per logical sub-table. Required keys per dict:
            suite_id, title, caption, label, col_range, header_rows.
            Optional keys: dir_name (defaults to runner_id), suite_type
            (defaults to "standard"). `col_range` is a 1-based range or list
            of column numbers into the runner's full col_metadata/coefs_per_col.
            `header_rows` is a list of lists of {label, span} dicts.
        coefs_per_col: One dict per column (full runner cols, not sub-table).
            Each dict maps variable name to {beta, se, p_two, p_one}.
        col_metadata: One dict per column. Required keys: col, dv, fe_entity,
            fe_time, control_vars, n_obs, r2. Optional: n_firms, adj_r2,
            dv_mean, cluster_fallback.
        sample_label: Human-readable sample description (e.g. "Main sample
            (excludes financial and utility firms)").
        clustering: {"entity": bool, "time": bool}. Helper derives footer_note.
        tail: {"direction": "positive"|"negative"|"none",
               "applies_to": "ivs_only"|"all"}. Helper derives footer_note.
        ivs: Top-of-table variables. Each dict: {"name": str, "label": str,
            "tail": "one_pos"|"one_neg"|"two"}.
        controls: {"base": [...], "extended_only": [...], "labels": {...}}.
            Any variable listed in base/extended_only without an entry in
            labels gets its name LaTeX-escaped (underscore → \\_).
        model_family: "PanelOLS" / "Logit" / "LPM" / "OLS".
        render_hints: Optional overrides — decimal_places, skip_adj_r2,
            r2_label, scaling_note, time_fe_label, row_order.

    Returns:
        Absolute paths of written JSON files (one per sub-table).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    clustering_full = Clustering(
        entity=clustering["entity"],
        time=clustering["time"],
        footer_note=_clustering_footer_note(
            clustering["entity"], clustering["time"]
        ),
    )

    tail_applies_to = tail.get("applies_to", "ivs_only")
    tail_full = TailSpec(
        direction=tail["direction"],  # type: ignore[arg-type]
        applies_to=tail_applies_to,  # type: ignore[arg-type]
        footer_note=_tail_footer_note(tail["direction"], tail_applies_to),
    )

    ivs_full = [IV(**iv) for iv in ivs]

    # Auto-escape any control variable without an explicit label.
    controls_labels = dict(controls.get("labels", {}))
    for var in controls["base"] + controls.get("extended_only", []):
        controls_labels.setdefault(var, _latex_escape_label(var))
    controls_full = Controls(
        base=list(controls["base"]),
        extended_only=list(controls.get("extended_only", [])),
        labels=controls_labels,
    )

    render_hints_full = RenderHints(**(render_hints or {}))
    extended_names = controls_full.extended_only

    written_paths: list[Path] = []

    for sub in sub_tables:
        col_range = list(sub["col_range"])  # 1-based col numbers

        # Build Column objects, renumbering sub-table columns to 1..N.
        columns: list[Column] = []
        for renumber_idx, absolute_col in enumerate(col_range, start=1):
            cm = col_metadata[absolute_col - 1]
            cf = coefs_per_col[absolute_col - 1]

            control_vars = list(cm["control_vars"])
            indicator_rows = _build_indicator_rows(
                fe_entity=cm["fe_entity"],
                fe_time=cm["fe_time"],
                control_vars=control_vars,
                extended_controls=extended_names,
            )
            coefs_dict = {var: Coef(**coef_data) for var, coef_data in cf.items()}

            columns.append(
                Column(
                    col=renumber_idx,
                    dv=cm["dv"],
                    fe_entity=cm["fe_entity"],
                    fe_time=cm["fe_time"],
                    control_vars=control_vars,
                    n_obs=int(cm["n_obs"]),
                    n_firms=(int(cm["n_firms"]) if cm.get("n_firms") is not None else None),
                    r2=float(cm["r2"]),
                    adj_r2=(float(cm["adj_r2"]) if cm.get("adj_r2") is not None else None),
                    dv_mean=(
                        float(cm["dv_mean"]) if cm.get("dv_mean") is not None else None
                    ),
                    cluster_fallback=bool(cm.get("cluster_fallback", False)),
                    indicator_rows=indicator_rows,
                    coefs=coefs_dict,
                )
            )

        header_rows = [
            [HeaderCell(**cell) for cell in row] for row in sub["header_rows"]
        ]

        spec = SuiteSpec(
            schema_version="1.0",
            suite_id=sub["suite_id"],
            dir_name=sub.get("dir_name", runner_id),
            title=sub["title"],
            caption=sub["caption"],
            label=sub["label"],
            sample_label=sample_label,
            model_family=model_family,  # type: ignore[arg-type]
            suite_type=sub.get("suite_type", "standard"),
            clustering=clustering_full,
            tail=tail_full,
            ivs=ivs_full,
            controls=controls_full,
            header_rows=header_rows,
            columns=columns,
            render_hints=render_hints_full,
        )

        json_path = output_dir / f"suite_spec_{sub['suite_id']}.json"
        json_path.write_text(
            spec.model_dump_json(indent=2, exclude_none=False),
            encoding="utf-8",
        )
        written_paths.append(json_path)

    return written_paths


# ---------------------------------------------------------------------------
# Extraction helpers for runner use
# ---------------------------------------------------------------------------


def _compute_p_one(p_two: float, beta: float, hyp_dir: str) -> Optional[float]:
    if hyp_dir == "none":
        return None
    if hyp_dir == "positive":
        return p_two / 2.0 if beta > 0 else 1.0 - p_two / 2.0
    if hyp_dir == "negative":
        return p_two / 2.0 if beta < 0 else 1.0 - p_two / 2.0
    raise ValueError(f"Unknown hyp_dir: {hyp_dir!r}")


def extract_coefs_panelols(
    model: Any,
    key_ivs: Iterable[str],
    all_vars: Iterable[str],
    hyp_dir: str,
) -> dict[str, dict[str, Optional[float]]]:
    """Extract per-variable {beta, se, p_two, p_one} from a linearmodels PanelOLS result.

    Args:
        model: Fitted linearmodels result with .params / .std_errors / .pvalues.
        key_ivs: IV names that get direction-aware p_one (controls get p_one=None).
        all_vars: All variables to extract (IVs + controls for this column).
        hyp_dir: "positive", "negative", or "none".
    """
    key_iv_set = set(key_ivs)
    result: dict[str, dict[str, Optional[float]]] = {}
    for var in all_vars:
        if var not in model.params.index:
            continue
        beta = float(model.params[var])
        se = float(model.std_errors[var])
        p_two = float(model.pvalues[var])
        p_one = _compute_p_one(p_two, beta, hyp_dir) if var in key_iv_set else None
        result[var] = {
            "beta": beta,
            "se": se,
            "p_two": p_two,
            "p_one": p_one,
        }
    return result


def extract_coefs_logit(
    mfx_df: Any,
    key_ivs: Iterable[str],
    all_vars: Iterable[str],
    hyp_dir: str,
) -> dict[str, dict[str, Optional[float]]]:
    """Extract AMEs from a statsmodels Logit margeff `summary_frame()` DataFrame.

    The frame is indexed by variable name with columns dy/dx, Std. Err.,
    Pr(>|z|).
    """
    key_iv_set = set(key_ivs)
    result: dict[str, dict[str, Optional[float]]] = {}
    for var in all_vars:
        if var not in mfx_df.index:
            continue
        beta = float(mfx_df.loc[var, "dy/dx"])
        se = float(mfx_df.loc[var, "Std. Err."])
        p_two = float(mfx_df.loc[var, "Pr(>|z|)"])
        p_one = _compute_p_one(p_two, beta, hyp_dir) if var in key_iv_set else None
        result[var] = {
            "beta": beta,
            "se": se,
            "p_two": p_two,
            "p_one": p_one,
        }
    return result


def load_suite_spec(path: Path) -> SuiteSpec:
    """Load + validate a suite_spec.json from disk."""
    return SuiteSpec.model_validate_json(Path(path).read_text(encoding="utf-8"))


__all__ = [
    "extract_coefs_logit",
    "extract_coefs_panelols",
    "load_suite_spec",
    "write_suite_spec",
]
