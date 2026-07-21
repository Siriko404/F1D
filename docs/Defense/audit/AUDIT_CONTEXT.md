# Audit context supplied by the operator

This file tells you what already exists, what the operator can and cannot do, and who will be
in the room. It is context for designing the plan. It is not itself an audit.

## 1. What is being audited

`thesis_defense_main_deck_slides_01-13_standardized_v2.pdf`. Thirteen pages, every page
1152 x 648 points, three embedded font subsets of the Nimbus Roman Standardized family
(regular, bold, italic). SHA-256 matches the value recorded in the ledger, so the attached
artifact is confirmed to be the locked production deck.

It is an MSc thesis defense presentation at the Telfer School of Management, University of
Ottawa. The talk is 18 minutes with a 2-minute buffer inside a hard 20-minute limit, followed
by a substantial examiner question period.

The attached `deck_text_extracted.json` is the PDF text layer pulled programmatically page by
page with PyMuPDF. It is a faithful mechanical extraction, not a transcription, so it is safe
to treat as ground truth for wording. Note that letter-spaced headings appear in it with
inserted spaces, which is an artifact of the extraction, not of the deck.

## 2. Two deliverables

1. Audit the deck systematically and fix genuine defects.
2. Produce speaker notes for all 13 main-deck slides. The appendix is a separate, later
   deliverable and is out of scope here.

## 3. Operator environment, verified

| Capability | State |
|---|---|
| Deterministic PDF text extraction | Working, PyMuPDF |
| Rasterizing the locked PDF at any DPI for visual inspection | Working, PyMuPDF |
| Reading rasterized pages as images | Working |
| Reading the thesis LaTeX sources and table files | Working |
| Programmatic search across all thesis sources | Working |
| WeasyPrint, the renderer the ledger designates as canonical | **Installed but broken.** The GTK dependency `libgobject-2.0-0` will not load on this Windows machine |
| Google Chrome | Present, but a different layout engine. Re-rendering the locked HTML in Chrome would reflow all 13 slides and destroy the value of the standardized-v2 lock |

Consequence: the audit is fully executable today. Applying a fix to the deck is currently
blocked on restoring WeasyPrint. The plan should therefore treat "record the finding" and
"fix the finding" as separable outcomes, and should be executable end to end even if no fix
is ever applied.

## 4. Work the operator has already completed

- Read the REV21 ledger and confirmed the deck hash and the thesis hash both match it.
- Extracted the full deck text layer.
- Confirmed page geometry and embedded fonts are uniform across all 13 pages.
- Spot-checked four load-bearing coefficients against the byte-exact thesis table file and
  found agreement.
- Begun visual inspection of the rasterized pages.

A small number of candidate findings have already surfaced. They are listed here only so the
plan does not have to rediscover them, and so that you can judge whether the plan's dimension
set would have caught them:

- Two dash-based sentence constructions on slide 12, which the ledger's language rule prohibits.
- A citation-style question on slide 2, where a legal authority is listed inline among academic
  papers.
- An apparent counterintuitive sample fact on slide 10, where the stock-acquirer panel is larger
  than the cash-acquirer panel, which an examiner is likely to probe.

## 5. Thesis source files available locally for verification

The ledger's authoritative flattened thesis is available and hash-verified. In addition the
operator holds the newer per-section build files: the byte-exact tables file, the abstract,
introduction, main-analysis body, conclusion, robustness tables, the replication table, and two
appendix table files. Where the flattened file and the newer body files could disagree, the
newer build files are the safer verification target. Any check the plan specifies can therefore
be grounded in a named file and line.

## 6. Committee, and why it changes the audit weighting

The ledger records committee composition as an open item. It is in fact known.

- Co-advisors: Dr. Ali Akyol and Dr. Harshit Rajaiya.
- Examiner Dr. Shantanu Dutta. Full Professor of finance. Works on M&A, method of payment,
  media coverage, textual and NLP methods, private in-house meetings, and insider trading. He
  is the closest domain expert to this thesis. Separately sourced intelligence, treated as
  reliable: he prefers quick defenses. This favors a tight, findings-forward talk that finishes
  inside the limit.
- Examiner Dr. Rengong (Alex) Zhang. Accounting, big data and machine learning, disclosure, and
  uncertainty in prices. Expect pressure on the data pipeline, on speaker attribution in the
  transcripts, on the choice of a word list over modern NLP, and on why there is no price
  reaction.

## 7. Known unresolved substantive gaps

Two questions the operator expects and cannot yet answer from the thesis:

- The exact CEO speaker-attribution procedure in the transcript data.
- Why the sample stops in 2018. The thesis gives no stated rationale.

The plan should say where gaps like these belong in the audit and how they should be recorded,
since they are not deck defects but they are defense exposure.

## 8. Constraints on the plan itself

- The operator executes every check. The plan must be executable without further interpretation.
- Checks that touch numbers must be grounded in a named source file, never in recall.
- The deck is locked. A finding is not a licence to edit. The plan must make the fix decision
  explicit and conservative.
- Reply length matters to the end user. The plan should be dense and skimmable, not discursive.
