# Process Extraction — Prompt 02: Internet Appendix E (Automation construction)
**Stage**: Round 2 — paragraph-level verbatim of the AUTOMATION variable construction procedure described in IA Appendix E
**Design principle**: Solution-free, paragraph-level, no prior text given to AIs
**Run on**: NLM (Campello notebook + Internet Appendix), Claude-web (Sina attaches supplement PDF), Claude Code (PyMuPDF on `campello_etal_2022_brexit_supplementary.pdf`)
**Created**: 2026-05-26
**Why**: Round 1 + 1b locked §IV of the MAIN paper. IA Appendix E is the only remaining piece of methodology under the Hybrid-scope decision because it describes the construction of a methodological variable (AUTOMATION) used in §VI.C robustness tests.
**NLM corpus caveat**: NLM's Campello notebook may not have the supplement PDF loaded. If your NLM notebook excludes the supplement, either (a) upload `docs/papers/campello_etal_2022_brexit_supplementary.pdf` to NLM before running this prompt, OR (b) accept that NLM will return INCOMPLETE for this round and we proceed with 2-AI cross-check (Claude-web + my PyMuPDF anchor).

---

## PROMPT (copy-paste below this line, identical to all 3 AIs)

The Internet Appendix companion paper is:
> **Internet Appendix to "Exporting Uncertainty: The Impact of Brexit on Corporate America"**, by Campello, Cortes, d'Almeida, Kankanhalli. Corresponds to JFQA paper DOI 10.1017/S0022109022000308.

The target section is:
> **Appendix E — Measures of Exposure to Automation**, sub-subsection **E.1 — Details on Automation Exposure Measures**

This section describes the procedure used to construct the firm-level AUTOMATION variable from 10-K filings via TextRank keyword analysis of an industrial-automation textbook.

### TASK
Return the COMPLETE VERBATIM TEXT of every body paragraph in Appendix E.1, in the order they appear, character-for-character.

A "body paragraph" is any block of running prose that constitutes a methodological step or substantive description. EXCLUDE:
- The section heading "Appendix E" or "E.1 Details on Automation Exposure Measures"
- Figure captions (e.g., "Figure E.1 ...")
- Table captions (e.g., "Table E.1 ...")
- Table content itself (the list of keywords in Table E.1)
- Footnote bodies (just include the footnote anchor number on the previous word)

### OUTPUT FORMAT (strict)

For each body paragraph, return a block:

```
IA_E_PARA_NN:
  paragraph_position: <integer — Nth body paragraph in E.1, counting from 1>
  pdf_page: <PDF page number in the supplementary PDF>
  first_word_verbatim: "<the first word of the paragraph, EXACTLY>"
  last_word_verbatim: "<the last word of the paragraph>"
  paragraph_text_verbatim: |
    <COMPLETE paragraph text. Preserve:
      - all sentences in order
      - all in-line and display equations (Unicode β, σ, ε, θ, ≈, etc. — NOT mojibake)
      - all parenthetical citations (e.g., "(Acemoglu and Restrepo (2020))", "(Loughran and McDonald (2011))", "(Mihalcea and Tarau (2004))")
      - all references to figures/tables (e.g., "in Table E.1")
      - all variable name spellings (e.g., AUTOMATION_i, AUTOMATION_KEYWORDS_i)
      - all capitalization, punctuation
    Collapse line breaks to single spaces. Collapse soft-hyphen wraps.>
  contains_equation: <"yes" | "no">
  contains_footnote_anchor: <"yes" | "no">
  references_other_paper: <"yes — list citations" | "no">
  uncertainty: <"none" | one verbatim sentence explaining boundary ambiguity, mojibake, etc.>
```

### RULES

1. **Verbatim only.** Reproduce the paper's text exactly. No paraphrase.
2. **Equation glyphs**: use Unicode (no `vol vitð$Þ≈βivol$` mojibake). If your source is corrupted, state so in `uncertainty:`.
3. **Soft-hyphen word wraps**: collapse `aggre-\ngate` → `aggregate`.
4. **Do not consolidate paragraphs** that the paper visually separates with indentation.
5. **Table E.1 contents are NOT a paragraph** — do not transcribe the keyword list.
6. **Order matters**: number paragraphs in the order they appear in the printed text.

### WHAT TO AVOID

- Do not assume how many paragraphs there are; enumerate every distinct one.
- Do not describe the procedure in your own words anywhere — only verbatim text.
- Do not skip a paragraph because it "seems methodologically trivial".
- Do not invent paragraphs not in the appendix.

### HONESTY GUARD

If you do NOT have access to the supplementary materials (or your text source is corrupted), STATE THIS EXPLICITLY in a single block:

```
ACCESS_FAILURE:
  reason: <one short sentence>
  what_you_have: <"only main paper" | "no Campello documents" | other>
```

Do NOT guess what Appendix E says. Do NOT reconstruct from main-paper §VI.C references to AUTOMATION. Do NOT hallucinate.

### NO COMMENTARY

No introduction, no caveats outside the formal blocks, no closing remarks.

### END BLOCK

```
TOTAL_PARAGRAPHS_RETURNED: <integer>
EXTRACTION_DATE: <YYYY-MM-DD>
PAPER_ACCESS_METHOD: <"NLM-notebook-with-supplement" | "NLM-notebook-without-supplement" | "PDF-attached" | "programmatic-PyMuPDF" | "other">
SUPPLEMENT_AVAILABLE: <"yes" | "no">
```

---

## Expected cross-check
- If NLM returns ACCESS_FAILURE: 2-AI cross-check (Claude-web + Claude Code anchor)
- If all 3 return paragraph blocks: 3-AI cross-check; lock paragraphs where ≥2 sources agree
- Anchor source: `tmp/campello_pdf_extract/full_supp_pdfpage16.txt` (and adjacent pages if E.1 wraps)


////////////////////////
NLM
////////////////////////

IA_E_PARA_01:
paragraph_position: 1
pdf_page: 16
first_word_verbatim: "For"
last_word_verbatim: "(2018)."
paragraph_text_verbatim: |
For more details on the geographic measure of exposure to automation for all commuting zones in the continental US, we refer the reader to Acemoglu and Restrepo (2020) and Leigh and Kraft (2018).
contains_equation: "no"
contains_footnote_anchor: "no"
references_other_paper: "yes — Acemoglu and Restrepo (2020), Leigh and Kraft (2018)"
uncertainty: "none"

IA_E_PARA_02:
paragraph_position: 2
pdf_page: 16
first_word_verbatim: "In"
last_word_verbatim: "universities."
paragraph_text_verbatim: |
In this appendix, we describe in more detail the procedure to construct our text-based measure of automation exposure at the firm level. We draw inspiration from an extensive literature in corporate finance that uses textual analysis (e.g., Loughran and McDonald (2011)) and define a dictionary of keywords that capture automation at the firm level. We first gather the syllabuses of many courses on “Industrial Automation and Integration” taught at top Engineering schools in North America (MIT, CalTech, University of Toronto, among others). Reading each syllabus, we identify the most frequently adopted textbook. This analysis points to Benhabib’s (2003) “Manufacturing: Design, Production, Automation, and Integration” as one of the most commonly required textbooks in these universities.
contains_equation: "no"
contains_footnote_anchor: "no"
references_other_paper: "yes — Loughran and McDonald (2011), Benhabib (2003)"
uncertainty: "none"

IA_E_PARA_03:
paragraph_position: 3
pdf_page: 16
first_word_verbatim: "With"
last_word_verbatim: "forms."
paragraph_text_verbatim: |
With the textbook in hand, we parse its full textual content and use a standard keyword ranking algorithm (“TextRank”, see Mihalcea and Tarau (2004)) to order the most distinctive keywords reflecting automation. Following the usual procedures in textual analysis (e.g., exclusion of “stop words”), we select the top 100 keywords that are closely related to automation and use them as a dictionary for parsing firms’ 10-Ks. The list of keywords is provided in Table E.1. Finally, we define AUTOMATION_i, which is a continuous variable (in logs) that measures how frequently the top 100 automation keywords appear in the firm’s business description (Section 1 of the 10-K form) and management discussion (Section 7 of the 10-K form). To capture cases in which a firm discusses automation efforts in only one year, we average the word count across all years in our sample. AUTOMATION_i = log(1 + AUTOMATION_KEYWORDS_i), where AUTOMATION_KEYWORDS_i is the number of mentions of the top 100 automation-related keywords in firm i’s 10-K forms.
contains_equation: "yes"
contains_footnote_anchor: "no"
references_other_paper: "yes — Mihalcea and Tarau (2004)"
uncertainty: "none"

IA_E_PARA_04:
paragraph_position: 4
pdf_page: 16
first_word_verbatim: "Figure"
last_word_verbatim: "variable."
paragraph_text_verbatim: |
Figure E.1 shows a histogram with the distribution of the AUTOMATION_i variable.
contains_equation: "no"
contains_footnote_anchor: "no"
references_other_paper: "no"
uncertainty: "none"

TOTAL_PARAGRAPHS_RETURNED: 4
EXTRACTION_DATE: 2026-05-26
PAPER_ACCESS_METHOD: "PDF-attached"
SUPPLEMENT_AVAILABLE: "yes"


////////////////////////
Claude Web
////////////////////////
```
IA_E_PARA_01:
  paragraph_position: 1
  pdf_page: 16
  first_word_verbatim: "For"
  last_word_verbatim: "universities."
  paragraph_text_verbatim: |
    For more details on the geographic measure of exposure to automation for all commuting zones in the continental US, we refer the reader to Acemoglu and Restrepo (2020) and Leigh and Kraft (2018). In this appendix, we describe in more detail the procedure to construct our text-based measure of automation exposure at the firm level. We draw inspiration from an extensive literature in corporate finance that uses textual analysis (e.g., Loughran and McDonald (2011)) and define a dictionary of keywords that capture automation at the firm level. We first gather the syllabuses of many courses on "Industrial Automation and Integration" taught at top Engineering schools in North America (MIT, CalTech, University of Toronto, among others). Reading each syllabus, we identify the most frequently adopted textbook. This analysis points to Benhabib's (2003) "Manufacturing: Design, Production, Automation, and Integration" as one of the most commonly required textbooks in these universities.
  contains_equation: "no"
  contains_footnote_anchor: "no"
  references_other_paper: "yes — Acemoglu and Restrepo (2020); Leigh and Kraft (2018); Loughran and McDonald (2011); Benhabib (2003)"
  uncertainty: "none"

IA_E_PARA_02:
  paragraph_position: 2
  pdf_page: 16
  first_word_verbatim: "With"
  last_word_verbatim: "variable."
  paragraph_text_verbatim: |
    With the textbook in hand, we parse its full textual content and use a standard keyword ranking algorithm ("TextRank", see Mihalcea and Tarau (2004)) to order the most distinctive keywords reflecting automation. Following the usual procedures in textual analysis (e.g., exclusion of "stop words"), we select the top 100 keywords that are closely related to automation and use them as a dictionary for parsing firms' 10-Ks. The list of keywords is provided in Table E.1. Finally, we define AUTOMATIONᵢ, which is a continuous variable (in logs) that measures how frequently the top 100 automation keywords appear in the firm's business description (Section 1 of the 10-K form) and management discussion (Section 7 of the 10-K form). To capture cases in which a firm discusses automation efforts in only one year, we average the word count across all years in our sample. AUTOMATIONᵢ = log(1 + AUTOMATION_KEYWORDSᵢ), where AUTOMATION_KEYWORDSᵢ is the number of mentions of the top 100 automation-related keywords in firm i's 10-K forms. Figure E.1 shows a histogram with the distribution of the AUTOMATIONᵢ variable.
  contains_equation: "yes"
  contains_footnote_anchor: "no"
  references_other_paper: "yes — Mihalcea and Tarau (2004)"
  uncertainty: "Subscript i on AUTOMATION and AUTOMATION_KEYWORDS appears as an italic subscript in the printed source (rendered here as ᵢ); the inline PDF text stream collides the subscript with the following word ('AUTOMATION_KEYWORDSiis'), but the proper reading 'AUTOMATION_KEYWORDSᵢ is the number' is confirmed by the Figure E.1 caption on PDF page 17, so the space is restored here."

TOTAL_PARAGRAPHS_RETURNED: 2
EXTRACTION_DATE: 2026-05-26
PAPER_ACCESS_METHOD: "PDF-attached"
SUPPLEMENT_AVAILABLE: "yes"
```