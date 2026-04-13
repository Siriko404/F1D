"""Phase F clone script: generate H7c/d/e and H14c/d/e from H7 and H14.

Reads the modified H7 and H14 runners and produces 6 new runner files
by string substitution. Uses literal-string substitutions to avoid breakage
from quoted characters or backslash escapes.

Run from F1D root: python scripts/clone_bgt_runners.py
"""
from pathlib import Path

ROOT = Path("src/f1d/econometric")

H7_SRC = (ROOT / "run_h7_illiquidity.py").read_text(encoding="utf-8")
H14_SRC = (ROOT / "run_h14_bidask_spread.py").read_text(encoding="utf-8")


def clone_amihud(src: str, dv: str, suite_id: str, out_dir_name: str,
                  table_filename: str, suite_name: str, label: str,
                  caption: str, window_note: str, out_filename: str) -> None:
    """Clone H7 runner -> H7c/d/e by swapping DV and labels."""
    out = src

    # ----- DV column substitutions (longest first to avoid prefix collisions)
    out = out.replace("DeltaILLIQ_lead1", dv + "_lead1")
    out = out.replace("DeltaILLIQ_lag", dv + "_lag")
    out = out.replace("DeltaILLIQ", dv)

    # ----- Output paths and filenames
    out = out.replace(
        '"econometric" / "h7_illiquidity"',
        '"econometric" / "' + out_dir_name + '"',
    )
    out = out.replace('"H7_Illiquidity"', '"' + suite_name + '"')
    out = out.replace('"h7_illiquidity_table.tex"', '"' + table_filename + '"')

    # ----- LaTeX caption + label
    old_caption_line = (
        r"\caption{Speech Uncertainty and Post-Call Illiquidity ($\Delta$Amihud, contemp + $t+1$ lead)}"
    )
    new_caption_line = "\\caption{" + caption + "}"
    out = out.replace(old_caption_line, new_caption_line)
    out = out.replace(r"\label{tab:h7_illiquidity}", "\\label{" + label + "}")

    # ----- Multicolumn DV header lines
    old_mc = (
        r" & \multicolumn{6}{c}{$\Delta$Amihud$_t$}"
        + "\n"
        + r" & \multicolumn{6}{c}{$\Delta$Amihud$_{t+1}$} \\"
    )
    new_mc = (
        " & \\multicolumn{6}{c}{" + dv + "$_t$}\n"
        " & \\multicolumn{6}{c}{" + dv + "$_{t+1}$} \\\\"
    )
    out = out.replace(old_mc, new_mc)

    # ----- Notes line in LaTeX caption block
    old_note_t = (
        r"$\Delta$Amihud$_t$ = post-call ([+1,+3] days) minus pre-call ([-3,-1] days) Amihud illiquidity (Lee 2016 window). "
    )
    new_note_t = dv + "$_t$ from BGT (2018, JAR) 25-day post-call window. "
    out = out.replace(old_note_t, new_note_t)
    old_note_t1 = (
        r"$\Delta$Amihud$_{t+1}$ = next-quarter call's $\Delta$Amihud (calendar quarter, strict consecutive). "
    )
    new_note_t1 = dv + "$_{t+1}$ = next-quarter call's " + dv + " (calendar quarter, strict consecutive). "
    out = out.replace(old_note_t1, new_note_t1)

    # ----- Markdown report filename + content
    out = out.replace("report_step4_H7.md", "report_step4_" + suite_id + ".md")
    out = out.replace("# H7 Illiquidity Report", "# " + suite_id + " Report")

    # ----- Summary stats label
    out = out.replace(
        'label="tab:summary_stats_h7"',
        'label="tab:summary_stats_' + suite_id.lower() + '"',
    )
    out = out.replace(
        'caption="Summary Statistics -- H7 Illiquidity (Main Sample)"',
        'caption="Summary Statistics -- ' + suite_id + ' ' + dv + ' (Main Sample)"',
    )
    out = out.replace('"H7 Illiquidity"', '"' + suite_id + ' ' + dv + '"')

    # ----- Top-of-file docstring header
    out = out.replace(
        "STAGE 4: Test H7 Post-Call Illiquidity Hypothesis (12-col 2-DV)",
        "STAGE 4: Test " + suite_id + " " + dv + " (12-col 2-DV)",
    )
    out = out.replace(
        "ID: econometric/test_h7_illiquidity",
        "ID: econometric/run_" + out_dir_name,
    )

    # ----- SUMMARY_STATS_VARS labels (these now reference the new DV after the
    # global DeltaILLIQ -> dv substitution above; re-pretty them)
    # The header label originally was DeltaILLIQ -> "$\\Delta$Amihud$_t$".
    # After substitution it became dv -> "$\\Delta$Amihud$_t$" which is wrong.
    # Re-replace with the dv name as the label.
    out = out.replace(
        '{"col": "' + dv + '", "label": "$\\\\Delta$Amihud$_t$"}',
        '{"col": "' + dv + '", "label": "' + dv + '$_t$"}',
    )
    out = out.replace(
        '{"col": "' + dv + '_lead1", "label": "$\\\\Delta$Amihud$_{t+1}$"}',
        '{"col": "' + dv + '_lead1", "label": "' + dv + '$_{t+1}$"}',
    )

    # ----- Add a window-construction banner near the top
    banner = (
        "\n# ----------------------------------------------------------------------\n"
        "# " + suite_id + " window construction:\n"
        "# " + window_note + "\n"
        "# ----------------------------------------------------------------------\n"
    )
    config_marker = (
        "# ==============================================================================\n"
        "# Configuration\n"
        "# =============================================================================="
    )
    out = out.replace(config_marker, banner + "\n" + config_marker)

    out_path = ROOT / out_filename
    out_path.write_text(out, encoding="utf-8")
    print("  Wrote:", out_filename, "(" + str(len(out)) + " chars)")


def clone_spread(src: str, dv: str, suite_id: str, out_dir_name: str,
                  table_filename: str, suite_name: str, label: str,
                  caption: str, window_note: str, out_filename: str) -> None:
    """Clone H14 runner -> H14c/d/e by swapping DV and labels."""
    out = src

    out = out.replace("DSPREAD_lead1", dv + "_lead1")
    out = out.replace("DSPREAD_lag", dv + "_lag")
    out = out.replace("DSPREAD", dv)

    out = out.replace(
        '"econometric" / "h14_bidask_spread"',
        '"econometric" / "' + out_dir_name + '"',
    )
    out = out.replace('"H14_BidAskSpread"', '"' + suite_name + '"')
    out = out.replace('"h14_bidask_spread_table.tex"', '"' + table_filename + '"')

    old_caption_line = (
        r"\caption{Speech Uncertainty and Bid-Ask Spread Changes (contemp + $t+1$ lead)}"
    )
    new_caption_line = "\\caption{" + caption + "}"
    out = out.replace(old_caption_line, new_caption_line)
    out = out.replace(r"\label{tab:h14_bidask_spread}", "\\label{" + label + "}")

    old_mc = (
        r" & \multicolumn{6}{c}{$\Delta$Spread$_t$}"
        + "\n"
        + r" & \multicolumn{6}{c}{$\Delta$Spread$_{t+1}$} \\"
    )
    new_mc = (
        " & \\multicolumn{6}{c}{" + dv + "$_t$}\n"
        " & \\multicolumn{6}{c}{" + dv + "$_{t+1}$} \\\\"
    )
    out = out.replace(old_mc, new_mc)

    old_note_t = (
        r"$\Delta$Spread$_t$ = mean(RelSpread[+1,+3]) $-$ mean(RelSpread[-3,-1]) (Lee 2016 closing-quote). "
    )
    new_note_t = dv + "$_t$ = BGT (2018) 25-day window applied to Lee (2016) closing-quote spread formula. "
    out = out.replace(old_note_t, new_note_t)
    old_note_t1 = (
        r"$\Delta$Spread$_{t+1}$ = next-quarter call's $\Delta$Spread (calendar quarter, strict consecutive). "
    )
    new_note_t1 = dv + "$_{t+1}$ = next-quarter call's " + dv + " (calendar quarter, strict consecutive). "
    out = out.replace(old_note_t1, new_note_t1)

    out = out.replace("report_step4_H14.md", "report_step4_" + suite_id + ".md")
    out = out.replace("# H14 Bid-Ask Spread Report", "# " + suite_id + " Report")

    out = out.replace(
        'label="tab:summary_stats_h14"',
        'label="tab:summary_stats_' + suite_id.lower() + '"',
    )
    out = out.replace(
        'caption="Summary Statistics -- H14 Bid-Ask Spread (Main Sample)"',
        'caption="Summary Statistics -- ' + suite_id + ' ' + dv + ' (Main Sample)"',
    )
    out = out.replace('"H14 Bid-Ask Spread"', '"' + suite_id + ' ' + dv + '"')

    out = out.replace(
        "STAGE 4: Test H14 Bid-Ask Spread Hypothesis (12-col 2-DV)",
        "STAGE 4: Test " + suite_id + " " + dv + " (12-col 2-DV)",
    )
    out = out.replace(
        "ID: econometric/test_h14_bidask_spread",
        "ID: econometric/run_" + out_dir_name,
    )

    # Summary stats labels: re-pretty after dv substitution
    out = out.replace(
        '{"col": "' + dv + '", "label": "$\\\\Delta$Spread$_t$"}',
        '{"col": "' + dv + '", "label": "' + dv + '$_t$"}',
    )
    out = out.replace(
        '{"col": "' + dv + '_lead1", "label": "$\\\\Delta$Spread$_{t+1}$"}',
        '{"col": "' + dv + '_lead1", "label": "' + dv + '$_{t+1}$"}',
    )

    banner = (
        "\n# ----------------------------------------------------------------------\n"
        "# " + suite_id + " window construction:\n"
        "# " + window_note + "\n"
        "# ----------------------------------------------------------------------\n"
    )
    config_marker = (
        "# ==============================================================================\n"
        "# Configuration\n"
        "# =============================================================================="
    )
    out = out.replace(config_marker, banner + "\n" + config_marker)

    out_path = ROOT / out_filename
    out_path.write_text(out, encoding="utf-8")
    print("  Wrote:", out_filename, "(" + str(len(out)) + " chars)")


# ============================================================================
# H7c/d/e: Amihud variants
# ============================================================================
clone_amihud(
    H7_SRC,
    dv="BGTLevel_Amihud",
    suite_id="H7c",
    out_dir_name="h7c_amihud_bgt_level",
    table_filename="h7c_amihud_bgt_level_table.tex",
    suite_name="H7c_BGTLevel_Amihud",
    label="tab:h7c_bgt_level_amihud",
    caption="H7c: Speech Uncertainty and BGT (2018) 25-Day Post-Call Amihud Illiquidity LEVEL (contemp + $t+1$ lead)",
    window_note="BGT (2018) 25-day post-call Amihud illiquidity LEVEL. Window = [0, +25] trading days, day 0 INCLUDED per BGT verbatim. Day-0 inclusion is mechanically biased relative to a strictly post-call window because day 0 is the highest-volume day of the firm-quarter (earnings call); BGT-faithful, not a bug.",
    out_filename="run_h7c_amihud_bgt_level.py",
)

clone_amihud(
    H7_SRC,
    dv="BGTDelta_Amihud",
    suite_id="H7d",
    out_dir_name="h7d_amihud_bgt_delta",
    table_filename="h7d_amihud_bgt_delta_table.tex",
    suite_name="H7d_BGTDelta_Amihud",
    label="tab:h7d_bgt_delta_amihud",
    caption="H7d: Speech Uncertainty and BGT-Window 25-Day Amihud DELTA (contemp + $t+1$ lead) [F1D extension]",
    window_note="F1D extension of BGT (2018): mean Amihud over [+1, +25] minus mean over [-25, -1]. Day 0 EXCLUDED from both sides. Window length is BGT-verbatim, shape is F1D-pipeline convention.",
    out_filename="run_h7d_amihud_bgt_delta.py",
)

clone_amihud(
    H7_SRC,
    dv="BGTAvg_Amihud",
    suite_id="H7e",
    out_dir_name="h7e_amihud_bgt_avg",
    table_filename="h7e_amihud_bgt_avg_table.tex",
    suite_name="H7e_BGTAvg_Amihud",
    label="tab:h7e_bgt_avg_amihud",
    caption="H7e: Speech Uncertainty and BGT-Window 25-Day Amihud AVERAGE (contemp + $t+1$ lead) [F1D extension]",
    window_note="F1D extension of BGT (2018): mean Amihud over symmetric [-25, +25] trading days, day 0 INCLUDED (51-day window). Window length is BGT-verbatim, symmetric shape is F1D-pipeline convention.",
    out_filename="run_h7e_amihud_bgt_avg.py",
)

# ============================================================================
# H14c/d/e: Spread variants
# ============================================================================
clone_spread(
    H14_SRC,
    dv="BGTLevel_Spread",
    suite_id="H14c",
    out_dir_name="h14c_spread_bgt_level",
    table_filename="h14c_spread_bgt_level_table.tex",
    suite_name="H14c_BGTLevel_Spread",
    label="tab:h14c_bgt_level_spread",
    caption="H14c: Speech Uncertainty and BGT-Window 25-Day Closing-Quote Bid-Ask Spread LEVEL (contemp + $t+1$ lead)",
    window_note="BGT (2018) 25-day post-call window applied to Lee (2016) closing-quote bid-ask spread formula. Window = [0, +25] trading days, day 0 INCLUDED per BGT verbatim. Hybrid construction (window from BGT, formula from Lee).",
    out_filename="run_h14c_spread_bgt_level.py",
)

clone_spread(
    H14_SRC,
    dv="BGTDelta_Spread",
    suite_id="H14d",
    out_dir_name="h14d_spread_bgt_delta",
    table_filename="h14d_spread_bgt_delta_table.tex",
    suite_name="H14d_BGTDelta_Spread",
    label="tab:h14d_bgt_delta_spread",
    caption="H14d: Speech Uncertainty and BGT-Window 25-Day Closing-Quote Bid-Ask Spread DELTA (contemp + $t+1$ lead) [F1D extension]",
    window_note="F1D extension: mean closing-quote spread over [+1, +25] minus mean over [-25, -1] trading days, day 0 excluded. Window length is BGT-verbatim, shape is F1D-pipeline convention.",
    out_filename="run_h14d_spread_bgt_delta.py",
)

clone_spread(
    H14_SRC,
    dv="BGTAvg_Spread",
    suite_id="H14e",
    out_dir_name="h14e_spread_bgt_avg",
    table_filename="h14e_spread_bgt_avg_table.tex",
    suite_name="H14e_BGTAvg_Spread",
    label="tab:h14e_bgt_avg_spread",
    caption="H14e: Speech Uncertainty and BGT-Window 25-Day Closing-Quote Bid-Ask Spread AVERAGE (contemp + $t+1$ lead) [F1D extension]",
    window_note="F1D extension: mean closing-quote spread over symmetric [-25, +25] trading days (51-day window), day 0 INCLUDED. Window length is BGT-verbatim, symmetric shape is F1D-pipeline convention.",
    out_filename="run_h14e_spread_bgt_avg.py",
)

print("\n[OK] Phase F: 6 new runners generated")
