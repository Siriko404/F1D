"""Byte-exact verification of every result number in docs/Thesis/thesis_draft.tex
against the bible (docs/Draft/thesis_tables.tex + its \\input constituent tables).

Each CHECK = (claim_id, file, row_regex, col_index_1based, expected_string).
The script parses the named table row, strips LaTeX wrappers, and compares the
cell's literal numeric string with the expected string. Exit code 1 on any FAIL.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRAFT_DIR = ROOT / "docs" / "Draft"

def cell(fname: str, row_regex: str, col: int, anchor: str | None = None) -> str:
    """Return the literal numeric token of column `col` (1-based, after the row label)
    in the first table line whose label matches row_regex. If `anchor` is given,
    scanning starts after the first line containing it (scopes to one table)."""
    text = (DRAFT_DIR / fname).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if anchor:
        for i, ln in enumerate(lines):
            if anchor in ln:
                lines = lines[i:]
                break
    for line in lines:
        if "&" not in line:
            continue
        label = line.split("&")[0]
        if re.search(row_regex, label):
            cells = [c.strip() for c in line.split("&")[1:]]
            if col > len(cells):
                return f"<col {col} missing, row has {len(cells)}>"
            raw = cells[col - 1]
            m = re.search(r"-?\d+[\d,]*\.?\d*", raw)
            return m.group(0) if m else f"<no number in '{raw}'>"
    return f"<row '{row_regex}' not found>"

CHECKS = [
    # --- SIII.1 run-up (tab:empire_building_did) ---
    ("runup cash UncRes",        "_empire_building_did.tex", r"^PreAnnounceQtr",            2, "0.0461"),
    ("runup cash UncRes SE",     "_empire_building_did.tex", r"^\s*&",                       0, None),  # SE handled below
    ("runup cash CashRatio",     "_empire_building_did.tex", r"^PreAnnounceQtr",            1, "0.0051"),
    ("runup stock UncRes",       "_empire_building_did.tex", r"^PreAnnounceQtr",            6, "-0.0429"),
    ("runup stock CashRatio",    "_empire_building_did.tex", r"^PreAnnounceQtr",            5, "-0.0036"),
    ("runup N cash UncRes",      "_empire_building_did.tex", r"^N \(firm-quarters\)",       2, "27,622"),
    ("runup firms cash UncRes",  "_empire_building_did.tex", r"^Firms",                     2, "1,248"),
    ("runup N cash CashRatio",   "_empire_building_did.tex", r"^N \(firm-quarters\)",       1, "67,590"),
    ("runup firms cash CashR",   "_empire_building_did.tex", r"^Firms",                     1, "2,232"),
    ("runup lag cash",           "_empire_building_did.tex", r"^CashRatio\$_\{t-1\}\$",     1, "0.7990"),
    ("runup lag stock",          "_empire_building_did.tex", r"^CashRatio\$_\{t-1\}\$",     5, "0.8013"),
    ("runup R2 cash CashRatio",  "_empire_building_did.tex", r"^\$R\^2\$",                  1, "0.665"),
    ("runup R2 cash UncRes",     "_empire_building_did.tex", r"^\$R\^2\$",                  2, "0.001"),
    # --- Table 1 summary stats (tab:summary_stats) used in SIII.2 prose ---
    ("t1 UncRes SD (B)",         "_summary_stats.tex",       r"^UncResCEO",                 3, "0.3072"),
    ("t1 CashRatio mean (A)",    "_summary_stats.tex",       r"^CashRatio(?!\$)",           2, "0.1573"),
    # --- SIII.2 drop-matched (tab:empire_drop_matched) ---
    ("match PRE2 UncRes",        "_empire_drop_matched.tex", r"^PRE2",                      1, "0.0068"),
    ("match PRE1 UncRes",        "_empire_drop_matched.tex", r"^PRE1",                      1, "0.0473"),
    ("match GAP UncRes",         "_empire_drop_matched.tex", r"^GAP",                       1, "0.0018"),
    ("match POST UncRes",        "_empire_drop_matched.tex", r"^POST",                      1, "-0.0250"),
    ("match drop PRE1-GAP U",    "_empire_drop_matched.tex", r"^Drop: PRE1 \$-\$ GAP",      1, "0.0455"),
    ("match drop PRE1-POST U",   "_empire_drop_matched.tex", r"^Drop: PRE1 \$-\$ POST",     1, "0.0723"),
    ("match PRE1 Cash",          "_empire_drop_matched.tex", r"^PRE1",                      2, "0.0061"),
    ("match drop PRE1-GAP C",    "_empire_drop_matched.tex", r"^Drop: PRE1 \$-\$ GAP",      2, "0.0006"),
    ("match drop GAP-POST C",    "_empire_drop_matched.tex", r"^Drop: GAP \$-\$ POST",      2, "0.0210"),
    ("match PRE2 Cash",          "_empire_drop_matched.tex", r"^PRE2",                      2, "0.0008"),
    ("match POST Cash",          "_empire_drop_matched.tex", r"^POST",                      2, "-0.0155"),
    ("match lag Cash",           "_empire_drop_matched.tex", r"^CashRatio\$_\{t-1\}\$",     2, "0.7547"),
    ("match N",                  "_empire_drop_matched.tex", r"^N \(firm-quarters\)",       1, "28,102"),
    ("match firms",              "_empire_drop_matched.tex", r"^Firms",                     1, "1,320"),
    # --- SIII.3 drop-placebo (tab:empire_drop_placebo) ---
    ("plac cash PRE1",           "_empire_drop_placebo.tex", r"^PRE1",                      1, "0.0486"),
    ("plac cash GAP",            "_empire_drop_placebo.tex", r"^GAP",                       1, "0.0058"),
    ("plac cash PRE1-POST",      "_empire_drop_placebo.tex", r"^Drop: PRE1 \$-\$ POST",     1, "0.0681"),
    ("plac stock PRE1",          "_empire_drop_placebo.tex", r"^PRE1",                      2, "-0.0404"),
    ("plac stock PRE1-GAP",      "_empire_drop_placebo.tex", r"^Drop: PRE1 \$-\$ GAP",      2, "-0.0756"),
    ("plac cash PRE2",           "_empire_drop_placebo.tex", r"^PRE2",                      1, "0.0105"),
    ("plac stock PRE2",          "_empire_drop_placebo.tex", r"^PRE2",                      2, "-0.0056"),
    ("plac N cash",              "_empire_drop_placebo.tex", r"^N \(firm-quarters\)",       1, "29,535"),
    ("plac N stock",             "_empire_drop_placebo.tex", r"^N \(firm-quarters\)",       2, "39,819"),
    # --- SIII.3 cashspec (tab:empire_cashspec) ---
    ("spec cash UncRes",         "_empire_cashspec.tex",     r"^Pre-announce qtr, Cash",    1, "0.0459"),
    ("spec stock UncRes",        "_empire_cashspec.tex",     r"^Pre-announce qtr, Stock",   1, "-0.0524"),
    ("spec formal UncRes",       "_empire_cashspec.tex",     r"^Cash \$-\$ Stock",          1, "0.0983"),
    ("spec formal Cash full",    "_empire_cashspec.tex",     r"^Cash \$-\$ Stock",          3, "0.0092"),
    ("spec cause matched diff",  "_empire_cashspec.tex",     r"^Cash \$-\$ Stock",          2, "0.0064"),
    ("spec N",                   "_empire_cashspec.tex",     r"^N \(firm-quarters\)",       1, "25,600"),
    # --- SIV.1 scrutiny trio ---
    ("valid CashRatio",          "_cash_scrutiny_validity.tex", r"^CashRatio",              1, "0.7530"),
    ("valid CashRatio ctrl",     "_cash_scrutiny_validity.tex", r"^CashRatio",              2, "0.8519"),
    ("valid HighCash",           "_cash_scrutiny_validity.tex", r"^HighCash",               3, "0.1754"),
    ("valid N",                  "_cash_scrutiny_validity.tex", r"^N \(calls\)",            1, "75,087"),
    ("chan OLS UncRes",          "_cash_scrutiny_channel.tex",  r"^CashScrutiny(?! \()",    1, "-0.0000"),
    ("chan logit UncRes",        "_cash_scrutiny_channel.tex",  r"^CashScrutiny \(log-odds\)", 1, "-0.0003"),
    ("chan N",                   "_cash_scrutiny_channel.tex",  r"^\$N\$ \(calls\)",        1, "41,512"),
    ("gate PreAnn col1",         "_reason_gating.tex",       r"^PreAnnounceQtr",            1, "0.0413"),
    ("gate PreAnn col2",         "_reason_gating.tex",       r"^PreAnnounceQtr",            2, "0.0439"),
    ("gate interaction",         "_reason_gating.tex",       r"^CashScrutiny \$\\times\$",  2, "-0.0056"),
    ("gate N",                   "_reason_gating.tex",       r"^N \(firm-quarters\)",       1, "26,216"),
]

# Spread + SEC rows live inside thesis_tables.tex among several tables with the
# same row labels — anchor each lookup to the right table's \label.
ANCHORED_CHECKS = [
    ("spread UncRes c1",  "thesis_tables.tex", "tab:h14c_ceo2_decomp", r"^UncResCEO", 1, "-0.0594"),
    ("spread UncPre c1",  "thesis_tables.tex", "tab:h14c_ceo2_decomp", r"^UncPreCEO", 1, "0.1664"),
    ("spread UncPre c2",  "thesis_tables.tex", "tab:h14c_ceo2_decomp", r"^UncPreCEO", 2, "0.3496"),
    ("spread UncPre c5",  "thesis_tables.tex", "tab:h14c_ceo2_decomp", r"^UncPreCEO", 5, "0.0108"),
    ("spread UncPre c6",  "thesis_tables.tex", "tab:h14c_ceo2_decomp", r"^UncPreCEO", 6, "0.1644"),
    ("spread N c1",       "thesis_tables.tex", "tab:h14c_ceo2_decomp", r"^N ",        1, "42,625"),
    ("sec UncRes c1",     "thesis_tables.tex", "tab:h18_ceo2_decomp",  r"^UncResCEO", 1, "-0.0003"),
    ("sec UncPre c3",     "thesis_tables.tex", "tab:h18_ceo2_decomp",  r"^UncPreCEO", 3, "0.0016"),
    ("sec N c1",          "thesis_tables.tex", "tab:h18_ceo2_decomp",  r"^N ",        1, "44,113"),
    ("t1 PreAnn mean PanelB", "_summary_stats.tex", "Panel B",         r"^PreAnnounceQtr", 2, "0.0143"),
]

# Derived-ratio claims in SIII.2 prose (arithmetic on locked cells, tolerance-checked).
DERIVED_CHECKS = [
    # (claim_id, value, claim_test)
    ("derived: 0.0461 = ~15% of SD 0.3072",  lambda: abs(0.0461 / 0.3072 - 0.15) < 0.005),
    ("derived: 0.0051 = ~3% of mean 0.1573", lambda: round(0.0051 / 0.1573 * 100) == 3),
    ("derived: 0.0051 = ~half a pp",          lambda: 0.45 <= 0.0051 * 100 <= 0.55),
    ("derived: PreAnn share = 1.4%",          lambda: round(0.0143 * 100, 1) == 1.4),
    # SIII.2 (Main Analysis 2) magnitude claims
    ("derived: 0.0473 = ~15% of SD 0.3072",   lambda: abs(0.0473 / 0.3072 - 0.15) < 0.01),
    ("derived: 0.0723 = half again 0.0473",   lambda: 1.45 <= 0.0723 / 0.0473 <= 1.55),
    # SIII.3 (Main Analysis 3) magnitude claim
    ("derived: 0.0983 = ~third of SD 0.3072", lambda: abs(0.0983 / 0.3072 - 0.33) < 0.02),
    # SIV.1 scrutiny CI (added by G2): interaction -0.0056 +/- 1.96*0.0111
    ("derived: CI low -0.027 = -0.0056-1.96*0.0111",  lambda: round(-0.0056 - 1.96 * 0.0111, 3) == -0.027),
    ("derived: CI high +0.016 = -0.0056+1.96*0.0111", lambda: round(-0.0056 + 1.96 * 0.0111, 3) == 0.016),
]

# SE checks need the line AFTER a coefficient row; handle separately.
def se_after(fname: str, row_regex: str, col: int, anchor: str | None = None) -> str:
    text = (DRAFT_DIR / fname).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if anchor:
        for i, ln in enumerate(lines):
            if anchor in ln:
                lines = lines[i:]
                break
    for i, line in enumerate(lines):
        if "&" in line and re.search(row_regex, line.split("&")[0]):
            nxt = lines[i + 1]
            cells = [c.strip() for c in nxt.split("&")[1:]]
            raw = cells[col - 1] if col <= len(cells) else ""
            m = re.search(r"-?\d+\.?\d*", raw)
            return m.group(0) if m else f"<no number in '{raw}'>"
    return "<row not found>"

SE_CHECKS = [
    ("runup cash UncRes SE",  "_empire_building_did.tex", r"^PreAnnounceQtr", 2, "0.0172"),
    ("runup stock UncRes SE", "_empire_building_did.tex", r"^PreAnnounceQtr", 6, "0.0307"),
    ("chan OLS SE",           "_cash_scrutiny_channel.tex", r"^CashScrutiny(?! \()", 1, "0.0013"),
    ("gate interaction SE",   "_reason_gating.tex", r"^CashScrutiny \$\\times\$", 2, "0.0111"),
    # added by G2 coverage gate (prose SEs that lacked a CHECK):
    ("runup cash CashRatio SE", "_empire_building_did.tex", r"^PreAnnounceQtr",        1, "0.0017"),
    ("runup cash lag SE",       "_empire_building_did.tex", r"^CashRatio\$_\{t-1\}\$", 1, "0.0070"),
]

def main():
    fails = 0
    for cid, f, rx, col, exp in CHECKS:
        if exp is None:
            continue
        got = cell(f, rx, col)
        ok = got == exp
        fails += (not ok)
        print(f"{'PASS' if ok else 'FAIL'}  {cid:26s} expected={exp:>10s} got={got}")
    for cid, f, anchor, rx, col, exp in ANCHORED_CHECKS:
        got = cell(f, rx, col, anchor=anchor)
        ok = got == exp
        fails += (not ok)
        print(f"{'PASS' if ok else 'FAIL'}  {cid:26s} expected={exp:>10s} got={got}")
    for cid, f, rx, col, exp in SE_CHECKS:
        got = se_after(f, rx, col)
        ok = got == exp
        fails += (not ok)
        print(f"{'PASS' if ok else 'FAIL'}  {cid:26s} expected={exp:>10s} got={got}")
    got = se_after("thesis_tables.tex", r"^UncResCEO", 1, anchor="tab:h14c_ceo2_decomp")
    ok = got == "0.1068"
    fails += (not ok)
    print(f"{'PASS' if ok else 'FAIL'}  {'spread UncRes SE c1':26s} expected=    0.1068 got={got}")
    for cid, test in DERIVED_CHECKS:
        ok = test()
        fails += (not ok)
        print(f"{'PASS' if ok else 'FAIL'}  {cid}")

    print(f"\n{fails} FAIL(s)" if fails else "\nALL CHECKS PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
