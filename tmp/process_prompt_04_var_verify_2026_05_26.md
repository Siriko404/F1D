# Variable Verification — Prompt 04: Targeted verification of an existing variable inventory
**Stage**: Variables Round 2 — verify Claude-web's 88-variable inventory against the paper, return ONLY corrections
**Design principle**: Solution-free targeted verification. Don't re-enumerate; verify what's provided. Return ONLY what's wrong + corrected values.
**Run on**: NLM (Campello notebook + supplement), Claude-web fresh session OR Gemini/other — anyone with access to the paper
**Created**: 2026-05-26
**Why**: Round 1 cross-check found NLM hallucinated all 12 Table 1 cell values (0/12 anchor match) while Claude-web matched 12/12. Need an INDEPENDENT verification pass on Claude-web's full 88-variable inventory before locking. Sina will supply the inventory as a separate input to each AI.

---

## PROMPT (copy-paste below this line, identical to all AIs)

The paper is:
> **Campello, Cortes, d'Almeida, Kankanhalli** — "Exporting Uncertainty: The Impact of Brexit on Corporate America" — *Journal of Financial and Quantitative Analysis*, Vol. 57, No. 8, Dec. 2022, pp. 3178–3222 — DOI 10.1017/S0022109022000308
>
> Includes the published Internet Appendix (supplementary materials, Appendices A–E + Tables C.1–C.7 + Figures C.1, D.1, E.1 + Tables E.1, E.2).

**I am giving you a separate input**: a variable inventory produced by another AI. It contains numbered blocks `VAR_01:` through `VAR_NN:`, each with fields like `name_as_printed`, `role`, `primary_definition.page`, `primary_definition.section_or_table`, `definition_verbatim`, `data_source_or_formula`, `unit_or_transformation`, `reported_summary_stats` (with `found_in`, `N`, `mean`, `sd`, `median`, `p25`, `p75`, `other_stats`, `panel`), `uncertainty`.

### TASK
For each `VAR_NN` block in the provided inventory:

1. **Locate** the variable in the paper (or supplement).
2. **Verify every field** in that block against the paper.
3. **If every field is correct** → SKIP that variable. Do not output anything for it.
4. **If any field is wrong, missing, or imprecise** → output a correction block.

### OUTPUT FORMAT (one block per variable WITH AT LEAST ONE ERROR)

```
VAR_NN_CORRECTION:
  name_as_printed_in_input: "<name as printed in the inventory I was given, EXACTLY>"
  matched_paper_variable: "<the variable as actually named in the paper, EXACTLY — copied verbatim, including subscripts, capitalization, parentheses>"
  fields_with_errors:
    - <field name 1>
    - <field name 2>
    - ...
  per_field_corrections:
    <field_name>:
      input_value: "<value as in the inventory I was given>"
      correct_value: "<correct value per the paper, EXACTLY as it appears in the paper>"
      evidence:
        page: <printed page number>
        section_or_table: "<e.g. 'Table 1, Panel A, p. 3198' | '§IV.C.3 ¶2' | 'Internet Appendix p. 8'>"
        verbatim_quote: "<one-sentence verbatim quote from the paper showing the correct value, with relevant context. For cell values, quote the table header + row label + cell.>"
  severity: <"critical" | "moderate" | "minor">
  notes: <"none" | one sentence explaining the nature of the error if it is not obvious from the field correction>
```

**Severity guide**:
- `critical` = wrong cell value (mean/SD/median/IQR/N), wrong formula, wrong page off by 5+ pages, hallucinated definition that is not in the paper
- `moderate` = wrong section reference, wrong panel/table, wrong sign, wrong unit
- `minor` = formatting variance (e.g., `β_i^UK` vs `β^UK_i`), missing subscript, slightly off page number

### RULES

1. **Verbatim only** for `correct_value` and `verbatim_quote`. Reproduce the paper's text exactly. No paraphrase.
2. **DO NOT output any block for variables where every field is correct.** Silence = endorsement of the inventory's values.
3. **DO NOT compute** any new statistics. Only report what the paper EXPLICITLY prints.
4. **DO NOT invent** corrections. If you cannot find the variable or the correct value in the paper, do not output a correction block; instead, output an `UNVERIFIABLE` block (see below).
5. **DO NOT add** new variables that aren't in the inventory. This is verification, not enumeration.
6. **Compare cell values char-for-char** (e.g., 0.012 ≠ 0.01; 48,554 ≠ 76,094; "Table 1, p. 3186" ≠ "Table 1, p. 3198").

### UNVERIFIABLE BLOCK (when you cannot verify a variable)

If the variable cannot be located in the paper (e.g., the inventory references a variable that does not exist in the published paper), output:

```
VAR_NN_UNVERIFIABLE:
  name_as_printed_in_input: "<name from inventory>"
  reason: <"variable not found in paper" | "variable found but cell values unreadable due to PDF mojibake" | "supplement section not accessible" | other>
  what_I_searched: "<e.g. 'Table 1 Panel A on p. 3198, Table 2 on p. 3201, body text §IV.A.1–IV.C.3, IA Appendix E.1' — list what you checked>"
```

### HONESTY GUARD

- If your PDF text source strips minus signs, garbles math glyphs, or merges page numbers — STATE THAT in a `SOURCE_CAVEATS` block at the END of your response, listing affected pages/tables and the specific glyph corruption you observed. Do NOT silently propagate or correct mojibake.
- If you cannot access the Internet Appendix supplement, list the IA-referenced variables in a `SUPPLEMENT_INACCESSIBLE` block at the END.

### NO COMMENTARY

No introduction, no "I reviewed the inventory and found...", no "Hope this helps", no closing remarks. Only:
- `VAR_NN_CORRECTION` blocks (zero or more)
- `VAR_NN_UNVERIFIABLE` blocks (zero or more)
- Optional `SOURCE_CAVEATS` and `SUPPLEMENT_INACCESSIBLE` blocks
- A final `END_BLOCK`

### END_BLOCK (always include)

```
TOTAL_VARS_REVIEWED: <integer — should equal the highest VAR_NN in the input>
TOTAL_CORRECTIONS_ISSUED: <integer>
TOTAL_UNVERIFIABLE: <integer>
CRITICAL_COUNT: <integer>
MODERATE_COUNT: <integer>
MINOR_COUNT: <integer>
REVIEW_DATE: <YYYY-MM-DD>
PAPER_ACCESS_METHOD: <"NLM-notebook-with-supplement" | "NLM-notebook-without-supplement" | "PDF-attached" | "programmatic-PyMuPDF" | "other">
```

---

## Expected cross-check after Sina returns AI responses
- AI verifier outputs only corrections. Silence on a VAR_NN = endorsement.
- I compare AI verifier's corrections against my PyMuPDF Table 1 anchor (`tmp/campello_table1_anchor_2026_05_26.json`).
  - If AI verifier says Claude-web's stat is wrong AND my anchor agrees with AI verifier → confirm correction, update lock-in.
  - If AI verifier says Claude-web's stat is wrong but my anchor agrees with Claude-web → AI verifier's correction is itself wrong; flag for inspection.
- Multiple AI verifiers can be run; majority + anchor decides.


///////////////////
Claude web 1
///////////////////

VAR_08_CORRECTION:
  name_as_printed_in_input: "ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH (column header: 'ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH')"
  matched_paper_variable: "ESTABLISHMENT_LEVEL_ EMPLOYMENT_GROWTH"
  fields_with_errors:
    - reported_summary_stats.other_stats
  per_field_corrections:
    reported_summary_stats.other_stats:
      input_value: "Only regression coefficients reported (Table 5, cols 1–2, p. 3203)."
      correct_value: "Only regression coefficients reported (Table 5, cols 1–2, p. 3204). Table 5 is the landscape page that sits between Table 4 (p. 3203) and the resumed body text (p. 3205)."
      evidence:
        page: 3204
        section_or_table: "Table 5 (landscape), bounded by Table 4 on p. 3203 and body text on p. 3205"
        verbatim_quote: "Campello, Cortes, d'Almeida, and Kankanhalli 3203 — this footer belongs to the page carrying 'TABLE 4 … Investment of U.S.-Based and U.K.-Based Subsidiaries'; the next body page footer reads 'Campello, Cortes, d'Almeida, and Kankanhalli 3205', placing the landscape Table 5 on the intervening page 3204."
  severity: minor
  notes: "Only the other_stats Table 5 page is wrong; the primary_definition page (3202, §V.B.1.b 'We first repeat the analysis of Table 2 using establishment-level employment growth…') is correct. The same Table 5 page error also appears in the inventory's TABLES_FOUND end block ('Table 5: 3203')."

VAR_09_CORRECTION:
  name_as_printed_in_input: "ESTABLISHMENT_TURNOVER"
  matched_paper_variable: "ESTABLISHMENT_TURNOVER"
  fields_with_errors:
    - reported_summary_stats.other_stats
  per_field_corrections:
    reported_summary_stats.other_stats:
      input_value: "Only regression coefficients reported (Table 5, cols 3–4, p. 3203)."
      correct_value: "Only regression coefficients reported (Table 5, cols 3–4, p. 3204)."
      evidence:
        page: 3204
        section_or_table: "Table 5 (landscape), bounded by Table 4 on p. 3203 and body text on p. 3205"
        verbatim_quote: "Campello, Cortes, d'Almeida, and Kankanhalli 3203 is the footer of the Table 4 page; the following body page footer 'Campello, Cortes, d'Almeida, and Kankanhalli 3205' places Table 5 on p. 3204."
  severity: minor
  notes: "Primary_definition (Footnote 24, p. 3203, 'Establishment turnover is defined as the sum of establishment openings and closings…') is correct; only the Table 5 page in other_stats is off by one. Footnote 24 is genuinely on p. 3203 (same page as Table 4), confirming Table 5 is the next page, 3204."

VAR_26_CORRECTION:
  name_as_printed_in_input: "U.K. Offshoring Index (Input Only)"
  matched_paper_variable: "Treatment is > 5 on the U.K. Offshoring Index (Input Only)"
  fields_with_errors:
    - primary_definition.page
  per_field_corrections:
    primary_definition.page:
      input_value: 3205
      correct_value: 3206
      evidence:
        page: 3206
        section_or_table: "Table 6 notes, p. 3206"
        verbatim_quote: "In the fourth column, the treatment group consists of firms with scores of greater than 5 on the Hoberg–Moon U.K. Offshoring Index summed up over years 2010–2014, considering only input offshoring activities, whereas the control group is made of firms with scores of 0 on this index."
  severity: minor
  notes: "The quoted definition_verbatim is Table 6 notes language, and Table 6 is printed on p. 3206 (footer '3206 Journal of Financial and Quantitative Analysis'), not p. 3205. The §V.B.2 body text on p. 3205 describes Input/Output/Total but does not contain this verbatim sentence. The companion block VAR_27 (Output Only) correctly cites the same Table 6 notes block as p. 3206, so VAR_26 is internally inconsistent."

SOURCE_CAVEATS:
  minus_sign_stripping:
    affected: "Tables 2 (p. 3200), 3 (p. 3202), 7 (p. 3207), 8 (p. 3208), 9 (p. 3210), 10 (p. 3212), 11 (p. 3214), 12 (p. 3215), 13 (p. 3216), and IA Table C.6 (IA p. 11)."
    observation: "My PDF text layer strips leading minus signs from coefficient cells (e.g., the INVESTMENT POST·HIGH_βUK coefficient renders as '0.165***' with no minus). I verified the sign of every coefficient cited in the inventory's other_stats fields against the surrounding body-text discussion rather than the bare cell, and they are consistent. This endorses (does not contradict) the inventory's own sign-reconstruction caveat; I issue no sign corrections."
  landscape_table_footers:
    affected: "Tables 5, 9, 10, 11, 12 (landscape pages)."
    observation: "These landscape pages have collapsed multi-column alignment and truncated footers in my source ('… University Press' with no page number). I resolved each table's printed page from the footers of the adjacent portrait pages. This is the basis for the Table 5 = 3204 correction (Table 4 footer = 3203; next body page footer = 3205)."
  equation_glyph_mojibake:
    affected: "§III and Appendix B (pp. 3184–3220) display/inline equations."
    observation: "Heavy glyph corruption in the theoretical-model equations. This does not affect any variable summary-statistic field reviewed here; all flagged/skipped variables draw on prose definitions, table notes, or Table 1 cells, which were cleanly recoverable."
  supplement_access: "Full. Internet Appendix (Appendices A–E, Tables C.1–C.7, E.1–E.2, Figures C.1/D.1/E.1) was available; no SUPPLEMENT_INACCESSIBLE block needed. All IA page references in the inventory (IA pp. 11, 12–13, 15, 16, 17, 18) verified correct."

END_BLOCK:
  TOTAL_VARS_REVIEWED: 88
  TOTAL_CORRECTIONS_ISSUED: 3
  TOTAL_UNVERIFIABLE: 0
  CRITICAL_COUNT: 0
  MODERATE_COUNT: 0
  MINOR_COUNT: 3
  REVIEW_DATE: 2026-05-26
  PAPER_ACCESS_METHOD: "PDF-attached"


/////////////////////////////
Claude web 2
////////////////////////////


  VAR_01_CORRECTION:
  name_as_printed_in_input: "INVESTMENT"
  matched_paper_variable: "INVESTMENT"
  fields_with_errors:
    - data_source_or_formula
  per_field_corrections:
    data_source_or_formula:
      input_value: "INVESTMENT = capital expenditures / lagged total assets. COMPUSTAT Quarterly Fundamentals. Table 10/C.7 notes add '(quarterly)'."
      correct_value: "The '(quarterly)' qualifier on INVESTMENT appears in the Table 2 notes (p. 3200) and the Table C.7 notes; the companion table that restates INVESTMENT as '(quarterly)' is Table 2, not Table 10."
      evidence:
        page: 3200
        section_or_table: "Table 2 notes, p. 3200"
        verbatim_quote: "INVESTMENT is defined as capital expenditures divided by lagged total assets (quarterly)."
  severity: minor
  notes: "Table 10's landscape notes were partially unreadable in my source (see SOURCE_CAVEATS), so this correction asserts only the verifiable Table 2 attribution rather than claiming Table 10 lacks the qualifier; either way the inventory omits Table 2, the clearest source."

VAR_28_CORRECTION:
  name_as_printed_in_input: "asset redeployability index (Kim and Kung (2016)) / HIGH_INPUT_IRREVERSIBILITY (capital)"
  matched_paper_variable: "asset redeployability index of Kim and Kung (2016)"
  fields_with_errors:
    - primary_definition.page
  per_field_corrections:
    primary_definition.page:
      input_value: "3191"
      correct_value: "3192"
      evidence:
        page: 3192
        section_or_table: "§IV.A.3 'Capital and Labor Irreversibility Measures', p. 3192"
        verbatim_quote: "To empirically measure capital irreversibility, we use an index of capital redeployability proposed by Kim and Kung (2016)."
  severity: minor
  notes: "Section IV.A.3 and its full text (capital redeployability and unionization) sit on the page whose footer reads 3192; p. 3191 ends mid-sentence in §IV.A.2 ('...we arbitrarily set a cutoff for high'). The section label §IV.A.3 in the inventory is correct; only the page is off by one."

VAR_29_CORRECTION:
  name_as_printed_in_input: "labor unionization rate (BEA) / High labor irreversibility"
  matched_paper_variable: "labor unionization rate from the Bureau of Economic Analysis"
  fields_with_errors:
    - primary_definition.page
  per_field_corrections:
    primary_definition.page:
      input_value: "3191"
      correct_value: "3192"
      evidence:
        page: 3192
        section_or_table: "§IV.A.3, p. 3192"
        verbatim_quote: "we measure the percentage of total employees who are unionized at the 4-digit SIC level using data from the Bureau of Economic Analysis."
  severity: minor
  notes: "Same page boundary as VAR_28; the unionization proxy text is on p. 3192, not 3191."

SOURCE_CAVEATS:
  table_1_clean: "Table 1 (Panels A–E, pp. 3198–3199) rendered cleanly. All 12 variables × 5 panels × 5 statistics (Mean/SD/Median/IQR/N) were compared char-for-char against the inventory's per-panel other_stats and reported_summary_stats; 0 discrepancies. The inventory's Table 1 transcription is exact."
  minus_signs_stripped: "My PDF text layer strips leading minus signs from regression-table cells (observed in Tables 2, 3, 8, 9, 10, 13, C.6, C.7). I therefore verified coefficient MAGNITUDES and significance stars (all match the inventory), and confirmed signs only where the body text states direction (investment/employment/divestitures/NWC negative; R&D/cash positive). One sign I could NOT recover: Table 3 col 4 (linear-continuous βUKi, DIVESTITURES) — the inventory reports +0.012*** (positive); my stripped layer cannot confirm whether it is +0.012 or −0.012. Per RULE 4 I issue no correction; flagging only."
  landscape_tables_truncated: "Tables 5, 9, 10, 11, and 12 are landscape blocks; in my extraction their column headers collapse and the right-edge columns are cut off (e.g., Table 9 cols 5–6 FX-Hedging coefficients, Table 10 cols 5–6 syndicated-loan + discount-rate-news coefficients). The inventory makes no specific coefficient claims for those truncated columns, so nothing was correctable there; leftmost coefficient columns were legible and verified."
  table_10_notes: "Table 10's note text is partially garbled/truncated in my source ('all-d...', 'Each pair o[f]...'). This is why VAR_01's correction is framed conservatively."
  math_glyphs: "Equation glyphs in (1)–(13), (A.1)–(A.4), and the Appendix B proofs are heavily garbled (sub/superscripts, integrals). Not used for any cell or coefficient verification."

TOTAL_VARS_REVIEWED: 88
TOTAL_CORRECTIONS_ISSUED: 3
TOTAL_UNVERIFIABLE: 0
CRITICAL_COUNT: 0
MODERATE_COUNT: 0
MINOR_COUNT: 3
REVIEW_DATE: 2026-05-26
PAPER_ACCESS_METHOD: "PDF-attached"