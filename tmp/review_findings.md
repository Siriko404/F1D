# Thesis paragraph-by-paragraph review — findings ledger

**Started:** 2026-04-29
**Audit order:** §2 → §3 → §4 → §1 → §5 → Abstract + Appendix C
**Unit grain:** subsection (subsubsection for §4); ~38 audit units total across 81 paragraphs
**Branch:** master
**Evidence base:** `tmp/suite_spec_index.json`, `docs/Draft/CANONICAL_FACT_SHEET.md`, `docs/Draft/references.bib`, content `.tex` files

## Rubric (12 + 3 writing checks, trigger-based)

Triggered checks (fire only when ¶ contains the trigger):

| # | Trigger | Check |
|---|---|---|
| 1 | numbers (β, p, n, "X of Y") | numerical fact-check vs `tmp/suite_spec_index.json` |
| 2 | `\cite{}` | citation appropriateness — claim supported by primary source |
| 3 | quoted phrase `''...''` | verbatim integrity (≥2 word drift = BREAK) |
| 4 | `\ref{}` | target resolution + targeted-table cell match |
| 5 | `\texttt{Var}` | pipeline-name fidelity |
| 6 | variable named | no-mention-unreported (estimated AND reported in body table) |
| 7 | theory-anchor claim | theory ↔ result alignment |
| 8 | hedge word | hedging calibration vs evidence |
| 9 | one-tailed test | tail logic — sign predicted ex-ante |
| 10 | mechanism claim | alternative mechanisms disclosed |

Always-fire (every ¶):

| # | Always | Check |
|---|---|---|
| 11 | — | intra-¶ logic (sentence chain) |
| 12 | — | cross-¶ consistency (same/other section) |
| W1 | — | topic sentence — opens with claim? |
| W2 | — | claim-evidence-warrant chain visible inside ¶? |
| W3 | — | signposting — ends pointing forward? |

## Severity gates

- **BREAK** = number ≠ suite_spec; verbatim drift ≥2 words; `\ref{}` wrong target; pipeline-name typo; variable cited not in any reported table → fix on-spot (same ¶) OR defer to Phase 9 (cross-¶)
- **FLAG** = citation appropriateness; hedging miscalibration; mechanism alternative undisclosed; cross-¶ inconsistency; W1/W2/W3 → accumulate to end-of-phase report

## Phase 0 — pre-audit findings (informational)

### F0.1 — comment-only stale ¶ count in section_4_additional.tex
File: `docs/Draft/sections/section_4_additional.tex` line 8
Comment claims `H23 TSIMM: n 12,061–18,492` but actual H23 latest spec gives `n=12,728-18,492`
Impact: comment-only, no PDF impact. Body-prose §4.1 does NOT cite this n range.
Severity: COMMENT-DRIFT (cleanup)
Fix: update comment to match actual.

### F0.2 — 6 unused bib entries
References.bib contains 6 entries cited nowhere in content sections:
- `aguerrevere2009`, `caldara2022`, `cassell2013`, `grenadier2002`, `hambrick1984`, `larcker2012`
Severity: BIB-CLEANUP (informational; doesn't break)
Fix: defer to Phase 9; remove or document why kept.

### F0.3 — 13 orphan labels
Labels defined in content sections but not `\ref`'d from anywhere in content. Most are subsection labels not linked elsewhere in body — OK by design (labels exist for safety, not for required cross-refs). Listing for completeness:
- `\label{app:robustness}`, `app:robustness:methods`, `app:robustness:rated`
- `\label{sec:additional:endo:framing}`, `sec:additional:reaction:asymmetry`
- `\label{sec:conclusion:asymmetry}`, `sec:conclusion:future`, `sec:conclusion:limitations`, `sec:conclusion:mechanism`, `sec:conclusion:summary`
- `\label{sec:framework:conceptual}`, `sec:intro`, `sec:main:robustness`
Severity: INFORMATIONAL (no fix needed unless we want to wire them up).

## Phase 0 — coverage confirmed

- 15 suites dumped to `tmp/suite_spec_index.json` (all body-cited tables covered)
- 81 paragraphs counted across 38 audit units
- 0 broken `\ref{}`; 0 broken `\cite{}`

---

# Phase 1 — §2 Framework

(pending — start on user "go phase 1")

---

# Phase 2 — §3 Main

(pending)

---

# Phase 3 — §4 Additional

(pending)

---

# Phase 4 — §1 Intro

(pending)

---

# Phase 5 — §5 Conclusion

(pending)

---

# Phase 6 — Abstract + Appendix C

(pending)

---

# Phase 9 — Consolidated fix-list

(pending)
