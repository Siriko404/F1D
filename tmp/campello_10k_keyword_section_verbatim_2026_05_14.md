# Campello et al. 2022 JFQA — 10-K Textual-Search Measure of Uncertainty (verbatim)

**Source**: PDF programmatic extraction via `pdftotext -layout` per-page.
**Pages**: PDF p.14 (journal p.3191) + PDF p.15 (journal p.3192).
**Extraction date**: 2026-05-14.
**Extractor**: pdftotext (Poppler 24.04 via MiKTeX) → `tmp/campello_pages/p14.txt`, `p15.txt`.
**Manipulation**: NONE. Plain text dump from PDF.

---

## PDF p.14 (j.3191) — Section IV.A.2

> **2. Textual-Search-Based Measure of Uncertainty**
>
> As an alternative measure of U.S. firms' exposure to Brexit-induced
> uncertainty, we develop a textual-search-based metric that is constructed by
> parsing firms' 2015 10-K filings. In particular, we look for the number of entries
> of keywords related to uncertainty about Brexit ("Brexit," "Great Britain," and
> "Uncertainty") in firms' disclosures, classifying firms with a "high" number of
> entries as HIGH_UK_EXPOSURE firms, and those with zero entries as control
> firms.¹⁴ Notably, the vast majority of firms file their 10-Ks with the SEC between
> March and June of each year. By computing these wordcounts from firms' 10-K
> disclosures (before the actual vote takes place, yet after the referendum is
> announced), we build a measure of exposure to the United Kingdom based on
> what firms consider relevant to communicate to their investors on the eve of the
> 2016 Brexit vote.
>
> Textual analysis reveals that most firms cite concerns about Brexit a half dozen
> times or more in their 10-Ks, or not at all. As such, we arbitrarily set a cutoff for high

**Footnote 14** (j.3191):

> ¹⁴ Entries like "Referendum," "Uncertain," "United Kingdom," "UK," "U.K.," and "G.B." are
> subsumed by the above wording.

---

## PDF p.15 (j.3192) — continuation

> Brexit cites at more than 5 entries. There are 807 firms citing Brexit more than
> 5 times in their 10-Ks. On the other hand, 433 do not cite any Brexit-related terms in
> their public filings. Although the heuristic cutoff we consider is naturally arbitrary,
> our results are robust to many sensible alternative choices.

---

## What the paper literally says (no interpretation, just enumeration)

1. **Main-text keyword list (3 terms)**: "Brexit," "Great Britain," and "Uncertainty".
2. **Footnote 14 secondary terms (6)**: "Referendum," "Uncertain," "United Kingdom," "UK," "U.K.," "G.B." — described as "subsumed by the above wording".
3. **Cutoff**: more than 5 entries → HIGH; zero entries → control; 1-5 → unclassified.
4. **Reported counts**: 807 HIGH firms; 433 zero-mention firms.
5. **Data scope**: 2015 10-K filings.
6. **Filing window**: most 10-Ks filed March-June 2015.
7. **Robustness claim**: "results are robust to many sensible alternative choices" (of cutoff, not of keyword list).

---

## Source files

- PDF: `docs/papers/Campello_2022_Brexit_JFQA.pdf` (45 pages).
- Page extracts: `tmp/campello_pages/p14.txt`, `tmp/campello_pages/p15.txt`.
- Adjacent context for cross-check: pp.13-16 (Section IV.A definitions).

---

## Tool discipline note

This file contains ONLY verbatim quotes from the paper plus a literal enumeration of what is on the page. No reverse-engineering, no methodology inference, no judgment about whether F1D's implementation matches. That belongs in a separate audit file.
