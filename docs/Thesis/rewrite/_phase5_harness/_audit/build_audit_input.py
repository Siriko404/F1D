# Build the single self-contained audit file: the flattened thesis (compiles to the verbatim 70pp PDF)
# with an AUDIT-AIDS header prepended as LaTeX comments -- a reference key (label->Table N, citekey->Author(Year),
# auto from the .aux + bibitems) and hand-authored column maps for the multi-panel tables. Comments don't compile,
# so the file still produces the identical PDF; the agents read ONE file and make ZERO external calls.
import re
from pathlib import Path
C = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\_uottawa_rewrite")
flat = (C / "_thesis_FLAT.tex").read_text(encoding="utf-8")
aux = (C / "thesis_draft_uottawa.aux").read_text(encoding="utf-8", errors="ignore")

# ---- auto reference key ----
labelnum = {m.group(1): m.group(2) for m in re.finditer(r"\\newlabel\{(tab:[^}]+)\}\{\{([^}]+)\}", aux)}
keyauth = {m.group(2): m.group(1).replace("~", " ") for m in re.finditer(r"\\bibitem\[([^\]]*)\]\{([^}]+)\}", flat)}
refkey = "% TABLE LABEL -> NUMBER (as the reader sees it):\n"
for k in sorted(labelnum, key=lambda x: [float(p) for p in labelnum[x].split(".")] if labelnum[x].replace(".", "").isdigit() else [99]):
    refkey += "%%   \\ref{%s} renders as 'Table %s'\n" % (k, labelnum[k])
refkey += "%\n% CITE KEY -> AUTHOR(YEAR) (as the reader sees it):\n"
for k in sorted(keyauth):
    refkey += "%%   \\citet{%s} -> %s\n" % (k, keyauth[k])

# ---- hand-authored column maps for the multi-panel tables (verified against the read tables) ----
COLMAPS = r"""%
% COLUMN MAPS for the multi-panel tables (so you never column-count raw LaTeX).
% Read 'value @ table : column-path' -- verify the prose attributes each number to THIS exact cell.
%
% Table 5.1 (tab:summary_stats) longtable: cols = Variable | Unit | N | Mean | SD | Min | P25 | Median | P75 | Max.
%   Panels: A. Independent Vars, B. Dependent Vars, C. Firm Controls.
%
% Table 5.2 (tab:empire_building_did), 8 data cols -- FIRST-DEAL only:
%   1=Cash/CashRatio 2=Cash/UncResCEO 3=Cash/CashScrutiny 4=Cash/HighCashScrutiny
%   5=Stock/CashRatio 6=Stock/UncResCEO 7=Stock/CashScrutiny 8=Stock/HighCashScrutiny
%   (rows: PreAnnounceQtr, CashRatio_{t-1} lag, controls, FE, N, R2)
%
% Table 5.3 (tab:empire_drop_matched), 2 cols: 1=UncResCEO 2=CashRatio  (matched universe, first-deal)
% Table 5.4 (tab:empire_drop_placebo), 2 cols: 1=Cash(UncResCEO) 2=Stock(UncResCEO)  (first-deal)
% Table 5.5 (tab:empire_cashspec), 3 cols: 1=UncResCEO(matched) 2=CashRatio(matched,+lag) 3=CashRatio(full,+lag)
%   key rows: 'Pre-announce qtr, Cash', 'Pre-announce qtr, Stock', 'Cash - Stock (Wald)'.
% Tables 5.6/5.7/5.8 (tab:h11_prisk_uncertainty / h24_us_epu / h24b_global_epu) convergent validity:
%   cols (1)(2)=Industry FE, (3)(4)=Firm FE; the PRisk/US_EPU_log/GEPU_log row is the headline.
% Table 5.9 (tab:cash_scrutiny_validity): DV=CashScrutiny; cols (1)-(4); CashRatio + HighCash rows headline.
% Table 5.10 (tab:cash_scrutiny_channel): 2 cols UncResCEO | UncAnsCEO; Panel A OLS, Panel B logit.
% Table 5.11 (tab:reason_gating): scrutiny x pre-announcement interaction.
% Table 5.12 (tab:h14c_ceo2_decomp): bid-ask spread, 12 specs; UncResCEO vs UncPreCEO vs ClarityCEO rows.
% Table 5.13 (tab:empire_drop_resolution) / 5.14 (tab:empire_drop_staticfe): robustness (withdrawal / static FE).
%
% Table 5.15 (tab:rob_runup), 16 data cols -- THESIS vs ALL-DEALS run-up:
%   1=Thesis/Cash/CashRatio  2=Thesis/Cash/UncResCEO  3=Thesis/Cash/CashScrutiny  4=Thesis/Cash/HighCashScrutiny
%   5=Thesis/Stock/CashRatio 6=Thesis/Stock/UncResCEO 7=Thesis/Stock/CashScrutiny 8=Thesis/Stock/HighCashScrutiny
%   9=AllDeals/Cash/CashRatio 10=AllDeals/Cash/UncResCEO 11=AllDeals/Cash/CashScrutiny 12=AllDeals/Cash/HighCashScrutiny
%   13=AllDeals/Stock/CashRatio 14=AllDeals/Stock/UncResCEO 15=AllDeals/Stock/CashScrutiny 16=AllDeals/Stock/HighCashScrutiny
%   (so the section-4.5 all-deals cash UncResCEO run-up 0.0391*** is col 10; first-deal 0.0461*** is col 2)
%
% Table 5.16 (tab:rob_timing_matched), 4 cols: 1=Thesis/UncRes 2=Thesis/CashR 3=AllDeals/UncRes 4=AllDeals/CashR
% Table 5.17 (tab:rob_timing_placebo), 4 cols: 1=Thesis/Cash 2=Thesis/Stock 3=AllDeals/Cash 4=AllDeals/Stock
% Table 5.18 (tab:rob_cashspec), 6 cols: 1=Thesis/UncRes 2=Thesis/CashR(m) 3=Thesis/CashR(f) 4=AllDeals/UncRes 5=AllDeals/CashR(m) 6=AllDeals/CashR(f)
%   (so the all-deals Cash-Stock Wald 0.1056** is col 4 'Cash - Stock (Wald)'; first-deal 0.0983** is col 1)
% Table 5.19 (tab:logit_dealnext) Logit A, 3 cols: 1=LPM 2=Logit 3=LPM+FE  (UncResCEO row headline)
% Table 5.20 (tab:logit_cashstock) Logit B, 3 cols: 1=LPM 2=Logit 3=LPM+FE
% Table 5.21 (tab:dwz_replication): cols = DWZ(2021) Table 3(2) | This study Baseline | This study Extended.
%"""

HEADER = ("% ============================================================================\n"
          "% AUDIT AIDS -- read this header, then audit the thesis body below. EVERYTHING is in THIS file;\n"
          "% resolve every \\ref/\\citet here, make NO external calls. (These comment lines do not compile.)\n"
          "% ============================================================================\n"
          + refkey + COLMAPS +
          "\n% ============================================================================\n"
          "% THESIS BODY (flattened; compiles verbatim to the final 70-page PDF) FOLLOWS:\n"
          "% ============================================================================\n")

out = C / "_thesis_AUDIT.tex"
out.write_text(HEADER + flat, encoding="utf-8")
print("wrote %s : %d chars (%d KB)" % (out.name, len(HEADER + flat), len(HEADER + flat) // 1024))
print("reference-key entries: %d tables, %d cites" % (len(labelnum), len(keyauth)))
