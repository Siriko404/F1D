"""One-shot patcher that adds write_suite_spec wiring to liquidity runners.

Each runner receives 4 text edits (import, constants, function, main-call).
Designed for H7c/H7d/H7e/H14/H14b/H14c/H14d/H14e only — single-purpose
migration helper, not reusable infrastructure.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
RUNNERS = ROOT / "src" / "f1d" / "econometric"


# Per-runner (file_stem, suite_id, dv_name, dv_lead_name, caption, hyp_dir)
CONFIGS = [
    ("run_h7c_amihud_bgt_level", "H7c", "BGTLevel_Amihud", r"BGTLevel\_Amihud\_lead1",
     r"H7c: Speech Uncertainty and BGT (2018) 25-Day Post-Call Amihud Level ($[0,+25]$, day 0 included)",
     "positive"),
    ("run_h7d_amihud_bgt_delta", "H7d", "BGTDelta_Amihud", r"BGTDelta\_Amihud\_lead1",
     r"H7d: Speech Uncertainty and BGT-Window 25-Day Amihud Delta ($[+1,+25]-[-25,-1]$)",
     "positive"),
    ("run_h7e_amihud_bgt_avg", "H7e", "BGTAvg_Amihud", r"BGTAvg\_Amihud\_lead1",
     r"H7e: Speech Uncertainty and BGT-Window 25-Day Amihud Average ($[-25,+25]$, 51-day symmetric)",
     "positive"),
    ("run_h14_bidask_spread", "H14", "DSPREAD", r"DSPREAD\_lead1",
     r"H14: Speech Uncertainty and Lee (2016) 3-Day Bid-Ask Spread Change ($\Delta$DSPREAD, $[+1,+3]-[-3,-1]$)",
     "positive"),
    ("run_h14b_spread_level", "H14b", "PostCallSpread", r"PostCallSpread\_lead1",
     r"H14b: Speech Uncertainty and Lee (2016) 3-Day Post-Call Bid-Ask Spread Level ($[+1,+3]$)",
     "positive"),
    ("run_h14c_spread_bgt_level", "H14c", "BGTLevel_Spread", r"BGTLevel\_Spread\_lead1",
     r"H14c: Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Level ($[0,+25]$, day 0 included)",
     "positive"),
    ("run_h14d_spread_bgt_delta", "H14d", "BGTDelta_Spread", r"BGTDelta\_Spread\_lead1",
     r"H14d: Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Delta ($[+1,+25]-[-25,-1]$)",
     "positive"),
    ("run_h14e_spread_bgt_avg", "H14e", "BGTAvg_Spread", r"BGTAvg\_Spread\_lead1",
     r"H14e: Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Average ($[-25,+25]$, 51-day symmetric)",
     "positive"),
]


IMPORT_OLD = "from f1d.shared.outputs import generate_manifest, generate_attrition_table"
IMPORT_NEW = dedent("""\
    from f1d.shared.outputs import (
        build_col_data_from_panelols,
        generate_attrition_table,
        generate_manifest,
        write_suite_spec,
    )""").rstrip()


def make_constants_block(suite_id: str, dv: str, caption: str, hyp_dir: str) -> str:
    dir_name = _dir_name_for_suite(suite_id)
    return dedent(f"""\

        EXTENDED_ONLY_CONTROLS = [c for c in EXTENDED_CONTROLS if c not in BASE_CONTROLS]

        # ------------------------------------------------------------------
        # Suite metadata for suite_spec.json emission.
        # ------------------------------------------------------------------
        SUITE_ID = "{suite_id}"
        SUITE_DIR_NAME = "{dir_name}"
        SUITE_TITLE = {_title_from_caption(caption)!r}
        SUITE_CAPTION = r{caption!r}
        SUITE_LABEL = "tab:{suite_id.lower()}"
        SAMPLE_LABEL = "Main sample (excludes financial and utility firms)."
        HYP_DIR = "{hyp_dir}"
        CLUSTERING = {{"entity": True, "time": False}}
        TAIL = {{"direction": HYP_DIR, "applies_to": "ivs_only"}}
        """).rstrip("\n")


def _dir_name_for_suite(suite_id: str) -> str:
    # Maps suite id to output directory under outputs/econometric/.
    table = {
        "H7c": "h7c_amihud_bgt_level",
        "H7d": "h7d_amihud_bgt_delta",
        "H7e": "h7e_amihud_bgt_avg",
        "H14": "h14_bidask_spread",
        "H14b": "h14b_spread_level",
        "H14c": "h14c_spread_bgt_level",
        "H14d": "h14d_spread_bgt_delta",
        "H14e": "h14e_spread_bgt_avg",
    }
    return table[suite_id]


def _title_from_caption(caption: str) -> str:
    # Strip LaTeX math/formatting from caption to produce a plain title.
    import re

    plain = re.sub(r"\$[^$]*\$", "", caption)
    plain = plain.replace(r"\_", "_").replace(r"\&", "&").replace(r"\\", "")
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain


def make_function_block(suite_id: str, dv_label: str, dv_lead_label: str) -> str:
    return dedent(f'''

        def _write_suite_spec_json(
            all_results: List[Dict[str, Any]],
            out_dir: Path,
        ) -> None:
            """Emit canonical suite_spec_{suite_id}.json from runner state."""
            col_metadata, coefs_per_col = build_col_data_from_panelols(
                all_results=all_results,
                model_specs=MODEL_SPECS,
                key_ivs=KEY_IVS,
                base_controls=BASE_CONTROLS,
                extended_controls=EXTENDED_CONTROLS,
                hyp_dir=HYP_DIR,
            )
            header_rows = [
                [
                    {{"label": "{dv_label}", "span": 6}},
                    {{"label": r"{dv_lead_label}", "span": 6}},
                ]
            ]
            paths = write_suite_spec(
                output_dir=out_dir,
                runner_id=SUITE_DIR_NAME,
                sub_tables=[
                    {{
                        "suite_id": SUITE_ID,
                        "dir_name": SUITE_DIR_NAME,
                        "title": SUITE_TITLE,
                        "caption": SUITE_CAPTION,
                        "label": SUITE_LABEL,
                        "col_range": [s["col"] for s in MODEL_SPECS],
                        "header_rows": header_rows,
                        "suite_type": "standard",
                    }}
                ],
                coefs_per_col=coefs_per_col,
                col_metadata=col_metadata,
                sample_label=SAMPLE_LABEL,
                clustering=CLUSTERING,
                tail=TAIL,
                ivs=[{{"name": iv, "label": iv, "tail": "one_pos"}} for iv in KEY_IVS],
                controls={{
                    "base": list(BASE_CONTROLS),
                    "extended_only": list(EXTENDED_ONLY_CONTROLS),
                }},
                model_family="PanelOLS",
            )
            for path in paths:
                print(f"  Saved: {{path.name}}")


        ''').rstrip("\n")


def patch_runner(path: Path, suite_id: str, dv: str, dv_lead: str, caption: str, hyp_dir: str) -> None:
    text = path.read_text(encoding="utf-8")

    # 1. Import rewrite
    if IMPORT_OLD in text:
        text = text.replace(IMPORT_OLD, IMPORT_NEW)
    else:
        print(f"  [{suite_id}] WARNING: expected import not found")

    # 2. Constants block: insert right after the EXTENDED_CONTROLS closing ]
    # Find "EXTENDED_CONTROLS = BASE_CONTROLS + [" block and the closing "]"
    import re

    pattern = re.compile(
        r"(EXTENDED_CONTROLS\s*=\s*BASE_CONTROLS\s*\+\s*\[[^\]]*\])",
        re.DOTALL,
    )
    m = pattern.search(text)
    if not m:
        print(f"  [{suite_id}] WARNING: EXTENDED_CONTROLS block not found")
    else:
        constants_block = make_constants_block(suite_id, dv, caption, hyp_dir)
        text = text[: m.end()] + "\n" + constants_block + text[m.end():]

    # 3. Function block: insert before `def main(`
    fn_block = make_function_block(suite_id, dv, dv_lead)
    def_main_idx = text.find("def main(panel_path")
    if def_main_idx == -1:
        print(f"  [{suite_id}] WARNING: def main not found")
    else:
        # Find the "# =====..." banner above def main and insert function before it
        # Simpler: insert just before def main, but we want double-newline separation
        text = text[:def_main_idx] + fn_block + "\n\n\n" + text[def_main_idx:]

    # 4. Call after save_outputs
    call_marker = "diag_df = save_outputs(all_results, out_dir)"
    call_replacement = (
        "diag_df = save_outputs(all_results, out_dir)\n\n"
        "    # Emit canonical suite_spec.json (consumed by generate_all_tables.py)\n"
        "    _write_suite_spec_json(all_results, out_dir)"
    )
    if call_marker in text:
        text = text.replace(call_marker, call_replacement, 1)
    else:
        print(f"  [{suite_id}] WARNING: save_outputs call not found")

    path.write_text(text, encoding="utf-8")
    print(f"  [{suite_id}] patched {path.name}")


def main() -> None:
    for file_stem, suite_id, dv, dv_lead, caption, hyp_dir in CONFIGS:
        path = RUNNERS / f"{file_stem}.py"
        if not path.exists():
            print(f"  [{suite_id}] SKIP: {path} not found")
            continue
        patch_runner(path, suite_id, dv, dv_lead, caption, hyp_dir)


if __name__ == "__main__":
    main()
