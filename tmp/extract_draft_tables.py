"""Generate docs/Thesis/_tables_from_bible.tex — BYTE-EXACT table blocks pulled from
the bible (docs/Draft/thesis_tables.tex + its \\input fragment files). Never hand-edit
the output; rerun this script after any bible change.

Ordering = first \\ref occurrence in docs/Thesis/thesis_draft.tex.
The empire deal-specification page (_empire_building_spec.tex) is inserted immediately
before tab:empire_building_did so the draft's "page preceding Table X" sentence stays true.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs" / "Thesis" / "thesis_draft.tex"
BIBLE_DIR = ROOT / "docs" / "Draft"
BIBLE = BIBLE_DIR / "thesis_tables.tex"
OUT = ROOT / "docs" / "Thesis" / "_tables_from_bible.tex"

# label -> fragment file (the \input constituents ARE the bible). Labels not listed
# here are extracted from thesis_tables.tex's own body.
FRAGMENT = {
    # 2026-06-14: Table 1 is the whole-thesis all-universe summary stats emitted by
    # docs/Draft/generate_summary_stats.py (replaces the hand-built _summary_stats.tex).
    "tab:summary_stats": "summary_stats.tex",
    "tab:empire_building_did": "_empire_building_did.tex",
    "tab:empire_drop_matched": "_empire_drop_matched.tex",
    "tab:empire_drop_placebo": "_empire_drop_placebo.tex",
    "tab:empire_cashspec": "_empire_cashspec.tex",
    "tab:cash_scrutiny_validity": "_cash_scrutiny_validity.tex",
    "tab:cash_scrutiny_channel": "_cash_scrutiny_channel.tex",
    "tab:reason_gating": "_reason_gating.tex",
    "tab:empire_drop_resolution": "_empire_drop_resolution.tex",
    "tab:empire_drop_staticfe": "_empire_drop_staticfe.tex",
}

# 2026-06-14: the thesis table set is LOCKED (user-ratified: 11 tables, empire thesis).
# 2026-06-15: +tab:h14c_ceo2_decomp (Section 4.2 spread reaction re-added) -> 12 tables.
# 2026-06-15: +tab:empire_drop_resolution (§4.3) +tab:empire_drop_staticfe (§4.4) -> 14 tables.
# Order is EXPLICIT here, not driven by a \ref scan of thesis_draft.tex -- §2 (the only
# written section) cites no result tables, and the set/order is fixed. summary_stats is
# Table 1 (corporate-finance convention). Re-running is always safe.
THESIS_TABLES = [
    "tab:summary_stats",
    "tab:empire_building_did",
    "tab:empire_drop_matched",
    "tab:empire_drop_placebo",
    "tab:empire_cashspec",
    "tab:h11_prisk_uncertainty",
    "tab:h24_us_epu",
    "tab:h24b_global_epu",
    "tab:cash_scrutiny_validity",
    "tab:cash_scrutiny_channel",
    "tab:reason_gating",
    "tab:h14c_ceo2_decomp",   # 2026-06-15: Section 4.2 bid-ask spread reaction (re-added)
    "tab:empire_drop_resolution",  # 2026-06-15: Section 4.3 resolution robustness
    "tab:empire_drop_staticfe",    # 2026-06-15: Section 4.4 static-FE robustness
]
order = list(THESIS_TABLES)

# 2026-06-15: standardized table notes (user). One structure for every table:
# [what it reports]. [fixed effects]. Standard errors clustered by firm, in
# parentheses; significant coefficients in bold. <stars> (<tail per table>).
# The tail label per table is left at the convention its stars were computed under
# (two-tailed for the Section 3 timing tables; one-tailed for the directional IVs in
# the validity / spread tables). Injection swaps ONLY the note text, never the data.
_STAR = r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$"
_SE = r"Standard errors clustered by firm, in parentheses; significant coefficients in \textbf{bold}."
_FE_FQ = r"Firm and calendar year-quarter fixed effects."
NOTE_BY_LABEL = {
    "tab:summary_stats": r"\textit{Notes:} Summary statistics for the main estimation sample (United States public, non-financial, non-utility firms, 2002--2018). Each variable is summarized on the complete cases of its own estimation universe, so the number of observations varies by row; never-acquirer firm-quarters are included as the fixed-effects baseline and treated firms' post-announcement quarters are excluded. All variables are defined in the main text and in Appendices~I and~II.",
    "tab:empire_building_did": r"\textit{Notes:} Pre-announcement run-up test. $\mathrm{PreAnnounceQtr}$ marks the quarter before a firm's first qualifying acquisition; post-announcement quarters are dropped and never-acquirers form the baseline. The cash arm is acquisitions at least half in cash; the stock arm is the at-least-half-in-stock placebo. " + _FE_FQ + " " + _SE + " " + _STAR + r" (two-tailed).",
    "tab:empire_drop_matched": r"\textit{Notes:} Disclosure-window event study on the matched universe, where $\mathrm{UncResCEO}$ and $\mathrm{CashRatio}$ are defined on the identical firm-quarters. Bins: $\mathrm{PRE2}$ ($e{=}{-}2$), $\mathrm{PRE1}$ ($e{=}{-}1$), $\mathrm{GAP}$ (announced, not yet closed), $\mathrm{POST}$ (completed); the omitted baseline is $e\le-3$ with never-acquirers. " + _FE_FQ + " " + _SE + " " + _STAR + r" (two-tailed).",
    "tab:empire_drop_placebo": r"\textit{Notes:} Disclosure-window event study estimated separately for cash acquirers and, as a placebo, stock acquirers, each on its own complete-case universe. Bins and baseline as in the matched event study. " + _FE_FQ + " " + _SE + " " + _STAR + r" (two-tailed).",
    "tab:empire_cashspec": r"\textit{Notes:} Pooled cash-specificity test: both treatments enter one regression and the cash-minus-stock difference is evaluated by a Wald test; the baseline is firms making neither a cash nor a stock acquisition. " + _FE_FQ + " " + _SE + " " + _STAR + r" (two-tailed).",
    "tab:empire_drop_resolution": r"\textit{Notes:} Robustness for the matched event study with the post bin redefined to count any resolution, completion or withdrawal (quarters at and after a withdrawal enter $\mathrm{POST}$). Bins, baseline, and estimator as in the matched event study. " + _FE_FQ + " " + _SE + " " + _STAR + r" (two-tailed).",
    "tab:empire_drop_staticfe": r"\textit{Notes:} Robustness for the cash column with static fixed effects, dropping the lagged dependent variable; the residual column is unchanged, since it carries no lag, and without the lag the coefficients describe the cash-ratio level rather than its change. " + _FE_FQ + " " + _SE + " " + _STAR + r" (two-tailed).",
    "tab:h11_prisk_uncertainty": r"\textit{Notes:} Convergent-validity check: residual CEO uncertainty regressed on firm-level political risk. Columns (1)--(2) use industry (FF12) and calendar-year fixed effects; columns (3)--(4) use firm and calendar-year fixed effects. " + _SE + " " + _STAR + r" (one-tailed for the independent variable, $\beta>0$; two-tailed for controls).",
    "tab:h24_us_epu": r"\textit{Notes:} Convergent-validity check: residual CEO uncertainty regressed on United States economic policy uncertainty. Columns (1)--(2) use industry (FF12) and calendar-year fixed effects; columns (3)--(4) use firm and calendar-year fixed effects. " + _SE + " " + _STAR + r" (one-tailed for the independent variable, $\beta>0$; two-tailed for controls).",
    "tab:h24b_global_epu": r"\textit{Notes:} Convergent-validity check: residual CEO uncertainty regressed on global economic policy uncertainty. Columns (1)--(2) use industry (FF12) and calendar-year fixed effects; columns (3)--(4) use firm and calendar-year fixed effects. " + _SE + " " + _STAR + r" (one-tailed for the independent variable, $\beta>0$; two-tailed for controls).",
    "tab:cash_scrutiny_validity": r"\textit{Notes:} Validity check that a firm's cash position predicts analyst cash scrutiny. " + _FE_FQ + " " + _SE + " " + _STAR + r" (one-tailed for the cash coefficient, $\beta>0$; two-tailed for controls).",
    "tab:cash_scrutiny_channel": r"\textit{Notes:} Analyst cash scrutiny as a candidate driver of residual CEO uncertainty. Panel~A is OLS on the continuous measure; Panel~B is a logit on an above-median indicator. " + _FE_FQ + " " + _SE + " " + _STAR + r" (two-tailed).",
    "tab:reason_gating": r"\textit{Notes:} The pre-announcement run-up estimated with analyst cash scrutiny and its interaction with the pre-announcement window, on the matched universe (calls with both $\mathrm{CashScrutiny}$ and $\mathrm{UncResCEO}$). " + _FE_FQ + " " + _SE + " " + _STAR + r" (one-tailed for the directional terms, $\beta>0$; two-tailed otherwise).",
    "tab:h14c_ceo2_decomp": r"\textit{Notes:} Post-call bid-ask spread regressed on the three speech components across twelve specifications; the fixed-effect grid (industry or firm, by year or year-quarter) and the contemporaneous-versus-one-quarter-ahead window vary by column as indicated, and a lagged dependent variable is included. " + _SE + " " + _STAR + r" (one-tailed for the speech components, $\beta>0$; two-tailed for controls).",
}

def inject_note(body: str, lab: str) -> str:
    """Replace the table's existing Notes text with the standardized note (text only;
    the data rows are untouched). Matches '\\textit{Notes:} ... ' up to the closing
    \\end{minipage}. Tables not in NOTE_BY_LABEL are returned unchanged."""
    if lab not in NOTE_BY_LABEL:
        return body
    new, n = re.subn(r"\\textit\{Notes:\}.*?(?=\s*\\end\{minipage\})",
                     NOTE_BY_LABEL[lab].replace("\\", "\\\\"), body, count=1, flags=re.DOTALL)
    if n != 1:
        sys.exit(f"ERROR: note minipage for {lab} not found (matched {n})")
    return new

bible = BIBLE.read_text(encoding="utf-8")

def block_from_bible(label: str) -> str:
    """Byte-exact \\begin{table}...\\end{table} block containing \\label{label}."""
    i = bible.find("\\label{%s}" % label)
    if i < 0:
        sys.exit(f"ERROR: label {label} not found in thesis_tables.tex")
    start = bible.rfind("\\begin{table}", 0, i)
    end = bible.find("\\end{table}", i)
    if start < 0 or end < 0:
        sys.exit(f"ERROR: table environment for {label} not delimited")
    return bible[start : end + len("\\end{table}")]

def shrink_wide_tabulars(s: str) -> str:
    """Wrap each \\begin{tabular}...\\end{tabular} in adjustbox max-width so wide tables
    (built for the bible's landscape geometry) shrink to fit the thesis text block; tables
    that already fit are unchanged. longtable (summary_stats) is a different env -> untouched.
    Content stays byte-exact; only a width wrapper is added."""
    # max width=\linewidth (NOT \textwidth): \linewidth tracks the current line width, so
    # landscape-wrapped tables fit the ROTATED width (full size) while portrait tables fit the
    # text block; \textwidth would wrongly shrink landscape tables to the portrait width.
    s = s.replace("\\begin{tabular}", "\\begin{adjustbox}{max width=\\linewidth}\n\\begin{tabular}")
    s = s.replace("\\end{tabular}", "\\end{tabular}\n\\end{adjustbox}")
    return s

parts = [
    "% AUTO-GENERATED by tmp/extract_draft_tables.py — table CONTENT byte-exact from the bible",
    "% (docs/Draft/thesis_tables.tex + fragments), each tabular adjustbox-wrapped to fit width.",
    "% DO NOT HAND-EDIT. Regenerate instead.",
    "",
]
# Widest tables -> landscape (full-size, rotated) instead of heavy portrait shrink (user 2026-06-14).
# The deal-spec page rides with the run-up table. pdflscape's landscape env issues its own
# \clearpage at both ends, so no extra \clearpage is added around landscaped blocks.
LANDSCAPE = {"tab:empire_building_did"}
# 2026-06-15: the "Empire-Building Run-Up Test -- Regression Specification" page
# (_empire_building_spec.tex) is no longer inserted -- it duplicated Section 2.4's
# equations and carried stale framing (empire-building, war-chest, one-tailed,
# call-level). Control-variable formulas moved to Appendix II.
for lab in order:
    if lab in FRAGMENT:
        body = (BIBLE_DIR / FRAGMENT[lab]).read_text(encoding="utf-8").rstrip()
    else:
        body = block_from_bible(lab)
    if lab == "tab:cash_scrutiny_validity":
        # 2026-06-14: the "Variable Construction (Link 1)" page that trails this fragment was
        # relocated to docs/Thesis/appendix_I_cash_scrutiny.tex (Appendix I; user will edit it).
        # Drop it from the generated tables so it is not duplicated. Bible fragment untouched.
        _m = "\\begin{center}\\large\\textbf{Cash-Scrutiny Measure: Variable Construction"
        _c = body.find(_m)
        if _c >= 0:
            body = body[:_c].rstrip()
            if body.endswith("\\clearpage"):
                body = body[: -len("\\clearpage")].rstrip()
    body = shrink_wide_tabulars(body)
    body = inject_note(body, lab)
    if lab in LANDSCAPE:
        parts += [f"% --- {lab} (landscape)", "\\begin{landscape}", body, "\\end{landscape}", ""]
    else:
        parts += [f"% --- {lab}", body, "\\clearpage", ""]

OUT.write_text("\n".join(parts), encoding="utf-8")
labs_out = re.findall(r"\\label\{(tab:[^}]+)\}", OUT.read_text(encoding="utf-8"))
print("draft cite order :", order)
print("labels in output :", labs_out)
missing = [l for l in order if l not in labs_out]
print("missing:", missing if missing else "NONE")
sys.exit(1 if missing else 0)
