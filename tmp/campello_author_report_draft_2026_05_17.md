# DRAFT — note to the authors: CASH-denominator definitional inconsistency

**STATUS: DRAFT for Sina's review. NOT sent. No external contact without
Sina's explicit authorization.** Prepared per Sina 2026-05-17 ("this …
must be reported to the authors").

Paper: Campello, M.; Cortes, G. S.; d'Almeida, F.; Kankanhalli, G.
"Exporting Uncertainty: The Impact of Brexit on Corporate America."
*Journal of Financial and Quantitative Analysis*, Vol. 57, No. 8 (Dec.
2022), pp. 3185–3212. DOI: 10.1017/S0022109022000308.

## The inconsistency

The variable **CASH** is given two different denominators in two places:

- **Table 1 note** (p. 3198): "CASH is defined as cash and short-term
  investments divided by **lagged total assets**." ⇒ cheq_t / atq_{t-1}
- **Table 8 caption** (p. 3208): "CASH is defined as total cash holdings
  divided by **lagged total assets net of cash holdings**." ⇒
  cheq_t / (atq_{t-1} − cheq_{t-1})

The numerator is the same line item; only the denominator differs (the
Table 8 caption subtracts lagged cash).

## Which definition the reported numbers reflect

Every CASH summary statistic the paper reports is at the **plain
lagged-total-assets** magnitude (~0.16–0.23); none is at the net-of-cash
magnitude (a net-of-cash ratio, winsorized at the paper's stated 1%
level, has mean ≈ 0.6 and SD several-fold larger):

| Source | CASH (mean / by group) |
|---|---|
| Table 1, Panel A (universe) | mean 0.22, SD 0.25, med 0.12 |
| Table 1, Panel B (treated, top βᵁᴷ tercile) | mean 0.20, med 0.11 |
| Table 1, Panel C (control, bottom βᵁᴷ tercile) | mean 0.17, med 0.11 |
| Supplementary Table C.2, Panel A (matched, βᵁᴷ) | treated 0.175 / control 0.164 |
| Supplementary Table C.2, Panel B (matched, textual) | treated 0.232 / control 0.194 |

All four tables are mutually consistent with **CASH = cheq_t /
atq_{t-1}** (the Table 1 note). They are inconsistent with the Table 8
caption's "net of cash holdings" phrasing.

## Most likely explanation (suggested, not asserted)

The Table 8 caption defines three variables in sequence; the next
sentence reads: "NON_CASH_WORKING_CAPITAL (NWC) is defined as working
capital **(net of cash)** divided by lagged total assets." The
"net of cash" qualifier appears to belong to NWC's numerator and to have
been inadvertently attached to CASH's denominator in the Table 8 caption.
The reported results are internally consistent with the Table 1 note;
the Table 8 caption wording is the apparent slip.

## Why this matters for replication

A replicator following the Table 8 caption literally (net-of-cash
denominator) cannot reproduce the paper's reported CASH distribution; the
Table 1 note definition does reproduce it across all four tables above.
Confirmation of the intended CASH denominator from the authors would
remove this ambiguity for future replications.

## Verification basis (for the thesis appendix, not for the authors)

All paper figures above were extracted programmatically (pdfplumber) from
the published PDF + supplementary, not hand-transcribed:
`tmp/campello_pdf_extract/table1_pdfpage21.txt`, `table8_pdfpage31.txt`,
`supp_FULL.txt` (Table C.2, p. 7). Rebuild fingerprint + the
winsor-invariance argument: `tmp/campello_variable_audit_2026_05_17.md`
§A/§E/§F/§F.1.
