# REV22 adversarial audit

## Verdict

Do not present REV22 unchanged. There is no numerical or undeclared-slide blocker in the shipped PDF, but the timing limitation is underframed and the two intended spoken rebuttals claim more than the design can establish.

## Direct PDF diff

Method: PyMuPDF text-span/bounding-box comparison, 160-dpi pdftoppm rasterization and pixel comparison, plus metadata, drawings, image, link, outline, and page-box inspection.

- Page content differs on slides 8, 11, 12, and 13 only.
- The document /Title differs as declared by R22-06.
- No undeclared changed slide was found.
- Every declared edit was found in the artifact.

## Findings

### F01 - MAJOR

**Location:** REV22_CHANGE_LOG.md, section 'R22-10, the guard that defended the wrong direction': 'misflagged calls dilute a binary treatment indicator and drag the estimate toward zero, so the effect was found despite the flaw rather than because of it.'

**Falsifiable claim:** The design does not establish that unobserved negotiation-onset error must attenuate the PRE1 coefficient toward zero.

**Evidence:** thesis_main_analysis.tex states that SDC supplies announcement, completion or withdrawal dates and payment composition, and defines PRE1 only as the quarter before announcement; no supplied thesis file observes negotiation onset. The change log itself says that onset is unobserved.

**Examiner exploitation:** An examiner can ask whether late-starting negotiations are systematically associated with deal complexity, payment method, distress, call timing, or CEO uncertainty. Because true onset is unobserved, the candidate cannot show that the misclassification is nondifferential or that the bias has a known sign.

**Remedy:** Do not say the flaw necessarily drags the estimate toward zero. Say: 'Under classical, nondifferential contamination it would attenuate the estimate, but onset is unobserved, so I cannot sign the bias. The coefficient is an announcement-anchored average association, not an identified effect of being in negotiations.'

### F02 - MAJOR

**Location:** REV22_CHANGE_LOG.md, section 5: 'The PRE1 and PRE2 shape ... shows ... that the signal is tightly timed and has no pre-trend.' Also DEFENSE_LEDGER.md Q15 answer sketch.

**Falsifiable claim:** A single statistically insignificant PRE2 coefficient does not establish that there is no pre-trend or that the signal is tightly timed.

**Evidence:** thesis_main_analysis.tex reports PRE2 = 0.0068 with SE 0.0178 and explicitly calls it a validity check, not proof of identification. Its approximate 95% interval is about [-0.028, 0.042], which includes economically nontrivial earlier movement.

**Examiner exploitation:** An examiner can ask for an equivalence test, a joint test of multiple leads, or power against a smaller earlier effect. The phrase 'no pre-trend' then becomes an unsupported certainty claim.

**Remedy:** Use: 'There is no statistically detected elevation at PRE2. That is consistent with a concentrated PRE1 pattern, but it does not prove the absence of earlier drift and it says nothing about negotiations beginning after the PRE1 call.'

### F03 - MINOR

**Location:** Slide 12, box 03: 'The data mark the announcement date, not when negotiations began.'

**Falsifiable claim:** The sentence names the missing timestamp but does not state the inferential consequence, and it treats negotiation onset as though it were automatically the same as the onset of a material withholding state or CEO knowledge.

**Evidence:** thesis_main_analysis.tex defines event time from announcement, completion, and withdrawal dates; thesis_conclusion.tex says the measure is not a direct reading of what the CEO knows. The supplied thesis does not observe negotiation onset, materiality onset, or knowledge onset.

**Examiner exploitation:** An examiner can immediately ask how many PRE1 calls occurred before negotiations, whether the CEO knew, and why the result should be interpreted as a withholding-state trace. The slide raises the attack without bounding the answer.

**Remedy:** Either remove the point from the main deck and prepare it orally, or write: 'Event time is anchored on announcement; negotiation onset is unobserved, so PRE1 is a proxy for the possible withholding window, not proof that every flagged call occurred during negotiations.'

### F04 - MINOR

**Location:** Slide 12, box 04 heading: 'Imperfect instruments'.

**Falsifiable claim:** The heading uses 'instruments' for a word-count measure and a comparison group even though the thesis uses no instrumental-variable design.

**Evidence:** The box text discusses a finance-specific word count and stock deals as an imperfect comparison. thesis_conclusion.tex treats these as separate measurement and counterfactual limitations, not as instruments.

**Examiner exploitation:** A finance or econometrics examiner can ask what the instruments are and what exclusion restriction they satisfy, forcing the candidate to explain that the heading was using the term colloquially.

**Remedy:** Rename the box 'Measurement and comparison limits' or 'Imperfect measure and comparison'. The merged substantive sentence can remain.

### F05 - MINOR

**Location:** Slide 5, positioning claim: 'No prior work occupies this exact cell.'

**Falsifiable claim:** The deck converts the thesis's qualified literature-positioning claim into an unqualified universal claim.

**Evidence:** thesis_intro.tex says: 'To our knowledge no prior work reads uncertainty language...' and explicitly calls this a positioning claim. Slide 5 omits 'To our knowledge'.

**Examiner exploitation:** An examiner familiar with an adjacent paper can ask the candidate to prove exhaustive novelty. The candidate then has to retreat to the qualification that the thesis originally used.

**Remedy:** Restore the thesis register: 'To our knowledge, no prior work occupies this exact cell.'

### F06 - MINOR

**Location:** Slide 12, left panel: 'CEO Q&A uncertainty tracks the point when an acquisition moves from private to public.'

**Falsifiable claim:** The sentence drops 'residual' and implies exact-point timing, although the estimated outcome is residual CEO-answer uncertainty observed on quarterly calls and grouped into announcement-relative states.

**Evidence:** thesis_main_analysis.tex defines UncResCEO as residual CEO Q&A answer uncertainty and estimates PRE1 and GAP bins. thesis_conclusion.tex describes an operationalization, not a direct reading of knowledge or an exact instant.

**Examiner exploitation:** An examiner can ask whether raw CEO uncertainty shows the same pattern and how quarterly calls identify the exact point of transition. Neither claim is tested as stated.

**Remedy:** Use: 'Residual CEO Q&A uncertainty differs across the final pre-announcement and post-announcement disclosure states.'

### F07 - MINOR

**Location:** verify_rev22.py lines 180-187: comment says no drawing may 'appear, vanish, or move'; code compares only len(page.get_drawings()).

**Falsifiable claim:** The drawing check can pass when a chart, line, marker, or shape moves or changes, as long as the number of drawing objects stays constant.

**Evidence:** The function drawing_count returns only len(page.get_drawings()), and verify_edit_scope compares the two integers. It never compares drawing geometry, paths, fill, stroke, or coordinates.

**Examiner exploitation:** A chart point or axis can move while all named checks pass, allowing a numerically misleading slide to be accepted by the verifier.

**Remedy:** Compare canonicalized drawing dictionaries and image hashes, or perform a rendered-pixel diff on every page. Keep the text-span comparison as a separate check rather than treating it as full visual fidelity.

### F08 - MINOR

**Location:** verify_rev22.py lines 226-233, R22-04 check: '"SHOW - AND" not in label_12.replace(" ", " ")'.

**Falsifiable claim:** The R22-04 check cannot reliably detect the old ASCII dash in the letter-spaced section label.

**Evidence:** replace(' ', ' ') is a no-op. REV21 extracts the old label as 'W H AT I T DOE S NOT SHOW - AND ...', so the contiguous pattern 'SHOW - AND' is absent even while the dash is present. The global dash scan checks only em and en dashes, not ASCII hyphens.

**Examiner exploitation:** The old label, or a regression to it, can pass the named R22-04 check and the global em/en scan.

**Remedy:** Normalize the letter-spaced heading before matching, or search the heading region/source string for the exact old punctuation. Include the ASCII dash in the targeted check.

### F09 - MINOR

**Location:** REV22_CHANGE_LOG.md, 'What did not change': 'No ... citation ...'.

**Falsifiable claim:** The change log falsely states that no citation changed.

**Evidence:** R22-09 in the same log says slide 12's footer was expanded, and the shipped PDF changes it from 'Conclusion, limitations and evidence-boundary paragraphs' to that text plus 'event-study design, Section 2.4.'

**Examiner exploitation:** A reviewer relying on the change summary can skip source verification even though the source line was materially changed to support the new limitation.

**Remedy:** Correct the log to say that slide 12's source footer changed, while coefficients, standard errors, p-values, event labels, and chart points did not.

## Answers to the twelve questions

### Q1

I diffed the PDFs directly using three independent surfaces: PyMuPDF text spans and bounding boxes, 160-dpi pdftoppm rasterization with pixel comparison, and document-structure checks for metadata, drawings, images, links, page boxes, and outlines. Page content differs only on slides 8, 11, 12, and 13. The PDF title metadata also changes exactly as R22-06 declares. R22-01 appears on slide 8; R22-02 on slide 11; R22-03, R22-04, R22-07, R22-08, R22-09, and R22-10 on slide 12; R22-05 on slide 13; and R22-06 in /Title. I found no undeclared changed slide and no declared edit missing from the shipped artifact. Slide 12's vector-rule geometry also changes within the declared slide because the rewritten table reflows; that is accounted for by the slide-12 content edit, not an unexplained slide change.

### Q2

The relabelling is correct. thesis_controls_appendix.tex defines one seven-variable firm-financial control vector: Leverage, lnAssets, Tobin's Q, ROA, Capex, DivDummy, and sCFO. thesis_main_analysis.tex repeats the same catalog, states that MA1 uses the Section 2.4 design, that MA2 is otherwise the MA1 design, and that MA3 uses the pooled Section 2.4 model. No genuine specification difference was erased. 'ln(assets)' and 'dividend indicator' are the formal labels for the same controls previously called size and dividends.

### Q3

The narrowing to CEO Q&A is faithful and, relative to the thesis's broader closing prose, more closely matches what was estimated. The outcome is residual uncertainty in the CEO's Q&A answers, not all unscripted speakers or the entire earnings call. The slide could be even more precise by saying 'residual uncertainty in unscripted CEO Q&A', but the CEO-Q&A narrowing itself is not an overstatement and no change is required on that ground.

### Q4

The limitation is real and points in the correct direction: the event clock observes announcement, not the start of negotiations. One sentence is not enough because it does not state the consequence - some PRE1 calls may precede the relevant withholding state - and it does not distinguish negotiation onset from materiality or CEO knowledge. Volunteering it is wise only if the slide states the implication precisely and the oral answer does not claim a known attenuation bias. Otherwise it is strategically better kept in the Q&A preparation. The defensible wording is: 'Event time is anchored on announcement; negotiation onset is unobserved, so PRE1 is a proxy for the possible withholding window, not proof that every flagged call occurred during negotiations.'

### Q5

The merge retains both substantive limitations: the word count abstracts from context, and stock deals are an imperfect comparison. Four boxes remain a workable structure, and no thesis limitation was lost merely by putting those two clauses in one box. The defect is the heading 'Imperfect instruments': neither item is an instrumental variable, and the two failure modes remain conceptually distinct. Rename the box 'Measurement and comparison limits'; no fifth box is needed.

### Q6

The attenuation argument holds only under restrictive conditions: PRE1 must contain false positives but no outcome-correlated timing error; misclassification must be nondifferential conditional on the fixed effects and controls; truly unexposed flagged calls must have the same conditional outcome as ordinary quarters; the true effect must have a stable sign; and onset timing must not select deals or CEOs with systematically different uncertainty. Under those conditions the observed PRE1 coefficient is approximately a prevalence-weighted version of the true exposure effect and is attenuated. It can fail under differential timing, effect heterogeneity, false negatives in other bins, time-varying confounding, or onset related to deal complexity, stress, payment method, or call timing. The thesis observes no onset date, so it cannot test these conditions and cannot sign the bias. The safe answer is conditional, not 'found despite the flaw.'

### Q7

PRE2 = 0.0068 with SE 0.0178 licenses only this statement: the study does not statistically detect an average residual-uncertainty displacement at e=-2 relative to the baseline. Its approximate 95% interval is about [-0.028, 0.042], so it is not an equivalence result and does not rule out a smaller earlier effect. A single lead also cannot establish absence of a general pre-trend. Most importantly, PRE2 says nothing about negotiations beginning after the PRE1 call. The corrected argument is valid only when phrased as 'consistent with concentrated timing,' not 'shows tight timing with no pre-trend.'

### Q8

Several checks are correctly narrow: file presence, the locked-file hash, page counts, page size, distinct-file hashes, exact string presence or absence, standard metadata dash scanning, and outer-page span containment test what their labels say. The failures are: the environment and edit-scope decisions are based primarily on text spans, so nontext changes can pass; the drawing check compares only counts and cannot detect movement or changed geometry; the R22-04 check is broken by letter-spaced extraction and ignores the ASCII dash; the R22-08 'merge' check proves only that a heading exists and an old heading is absent, not that both substantive limitations survived; and the containment test cannot detect clipping inside CSS boxes, which the code acknowledges. The current PDF was independently raster-diffed and visually inspected, so these verifier defects do not create an unexplained current-page difference, but the script's green light is broader than its evidence.

### Q9

Yes. The change log says, under 'What did not change', 'No ... citation ...'. That is false. R22-09 explicitly changes the slide-12 source footer, and the shipped PDF adds 'event-study design, Section 2.4.' The log should distinguish unchanged numerical/chart content from the changed citation. Its statement that unchanged drawing counts show no chart moved is also an invalid inference in general, although the independent pixel diff found no undeclared chart change in this artifact.

### Q10

Overclaiming: slide 5 says 'No prior work occupies this exact cell,' while thesis_intro.tex says 'To our knowledge'; restore the hedge. Slide 12 says raw-sounding 'CEO Q&A uncertainty tracks the point' even though the estimated object is residual CEO-answer uncertainty observed in quarterly event states; that should be made more precise. Slide 13's CEO-Q&A narrowing is faithful. Needless self-harm: slide 12 volunteers the unobserved-onset problem without stating its consequence or a safe response, and 'Imperfect instruments' invites an irrelevant IV challenge. The causal, generalizability, word-count, and stock-comparison concessions themselves are warranted by thesis_conclusion.tex and should remain.

### Q11

The most dangerous unprepared question is: 'Your treatment is the quarter before announcement, but you never observe when negotiations began or when the CEO entered the withholding state. Why should PRE1 be treated as exposure, and what is the sign of the resulting timing-error bias?' It is not among the ledger's sixteen questions. The thesis cannot fully answer it because it has no onset or knowledge date. It can only concede the announcement-anchored proxy, describe the PRE2 and PRE1 pattern, and refuse to sign the bias without additional assumptions.

### Q12

Rewrite slide 12 box 3 to state the actual inferential boundary: 'Event time is anchored on announcement; negotiation onset is unobserved, so PRE1 is a proxy for the possible withholding window, not proof that every flagged call occurred during negotiations.' This removes the current half-concession and prevents the unsafe attenuation answer. The argument against making the change is strategic: it foregrounds a limitation the submitted thesis did not explicitly state and may invite the committee to pursue it. If the candidate cannot deliver the careful conditional answer, removing the box and keeping the issue in Q&A notes is safer than the current wording.

## Dimensions checked and found clean

- **Direct PDF page-diff scope:** All 13 pages were rendered at 160 dpi and pixel-compared; text spans and bounding boxes were also compared. Only slides 8, 11, 12, and 13 differ, matching the declared slide scope.
- **R22-01 control labels:** The seven controls on slides 8-10 were checked against thesis_controls_appendix.tex and the MA1/MA2/MA3 descriptions in thesis_main_analysis.tex. One shared control specification is used; the relabelling does not erase a specification difference.
- **R22-02 comparison grammar:** Slide 11 now compares cash acquisitions with stock acquisitions. The old mismatched comparison is absent.
- **R22-03 and R22-04 punctuation in the artifact:** The two slide-12 dash constructions were checked in extracted page text and in the rendered slide. Both were removed in REV22. The artifact is clean even though the R22-04 verifier is not.
- **R22-05 hedge and CEO-Q&A scope:** Slide 13 restores 'These patterns suggest that'. The CEO-Q&A scope was compared with the estimated outcome and is faithful.
- **R22-06 PDF title metadata:** The REV21 and REV22 /Title values were read directly. REV22 contains neither an em dash nor an en dash in the standard metadata fields, and no XMP stream, attachment, annotation, or form field was present.
- **R22-10 removal of the PRE2 guard:** The old PRE2 guard language is absent from slide 12. Removing it was correct because PRE2 cannot address negotiations beginning after the PRE1 call.
- **Changed-slide numerical fidelity:** The slide-8 estimate, SE, p-value, sample, and magnitude were checked against thesis_main_analysis.tex; slides 9 and 10 were unchanged from REV21 and their displayed main-analysis values were cross-checked against the supplied prose. No changed numerical claim was found.
- **Page readability and clipping:** Every REV22 page was rendered and inspected. No text clipping, overlap, or off-page content that changes meaning was found.

## Most dangerous unprepared question

> Your treatment is the quarter before announcement, but you never observe when negotiations began or when the CEO entered the withholding state. Why should PRE1 be treated as exposure, and what is the sign of the resulting timing-error bias?

The event clock is anchored on announcement because that is what SDC observes. PRE1 is therefore a proxy for the possible withholding window, not proof that every flagged call occurred during negotiations. The PRE2 null shows no detected average displacement two quarters earlier, but it does not identify onset. Under classical nondifferential contamination the estimate would attenuate, but onset is unobserved, so I cannot sign the bias. The defensible claim is the announcement-relative within-firm pattern, not a causal effect of negotiation exposure.
