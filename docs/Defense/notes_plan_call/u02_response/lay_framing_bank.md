# Lay framing bank

Counting convention: whitespace-delimited words; hyphenated compounds count as one word. The framing is used only on first spoken use. `Q&A-FIRST` terms should normally stay out of the podium notes unless an examiner forces the concept.

| Term | Shortest honest framing | Words | First slide | Use | Claim ceiling |
|---|---|---:|---:|---|---|
| material information | Information important enough to matter to investors. | 7 | 2 | PODIUM | none applies |
| disclosure state | Whether the deal is private or public. | 7 | 2 | PODIUM | Section 3.6: describes the quarterly disclosure state, not the exact moment knowledge changed. |
| estimand | The exact quantity the model targets. | 6 | 4 | PODIUM | None applies; the thesis defines a descriptive within-firm mean shift. |
| descriptive result | A measured pattern, not a causal effect. | 7 | 4 | PODIUM | Sections 3.6 and 5: no causal identification or mechanism. |
| within-firm comparison | Each firm is compared with itself. | 6 | 4 | PODIUM | Sections 3.6 and 5: descriptive comparison only. |
| fixed effects | Absorb stable firm traits and shared quarter shocks. | 8 | 4 | PODIUM | None applies; matches the thesis's firm and year-quarter fixed-effect description. |
| clustered standard errors | Allow observations within a firm to move together. | 8 | 4 | PODIUM | None applies. |
| identification | The variation used to estimate the quantity. | 7 | 4 | PODIUM | Sections 3.6 and 5: must not be upgraded to causal identification. |
| event study | Compares outcomes across stages around an event. | 7 | 4 | PODIUM | Section 3.2: PRE2 is a check, not proof of no pre-trend. |
| generalizability | How far the result travels beyond this sample. | 8 | 6 | PODIUM | Section 2.1 and thesis limitations: sample tilts toward larger, better-covered U.S. public firms. |
| firm-quarter | One firm observed in one quarter. | 6 | 6 | PODIUM | None applies. |
| cash ratio | Cash and equivalents divided by total assets. | 7 | 6 | PODIUM | None applies. |
| residual | What remains after predictable parts are removed. | 7 | 6 | PODIUM | Section 3.6: residual call-level uncertainty, not raw uncertainty or private knowledge. |
| residualization | Removing predictable parts before the main analysis. | 7 | 7 | PODIUM | Section 3.6: does not imply exact timing or direct knowledge measurement. |
| word share | Listed words divided by all answer words. | 7 | 7 | PODIUM | Thesis limitation: word counts abstract from context. |
| uncertainty word list | A fixed finance-specific list of uncertainty terms. | 7 | 7 | PODIUM | Thesis limitation: one operationalization, not a direct reading of knowledge. |
| generated regressand | An outcome estimated before the main regression. | 7 | 7 | PODIUM | Thesis two-step caveat: conventional standard errors may be understated. |
| R-squared | The share of variation the model explains. | 7 | 7 | CUTTABLE | None applies. |
| coefficient | The estimated change linked to one variable. | 7 | 8 | PODIUM | Sections 3.6 and 5: 'linked' must not become 'caused'. |
| standard error | How uncertain the estimate is. | 5 | 8 | PODIUM | None applies. |
| confidence interval | A plausible range around the estimate. | 6 | 8 | PODIUM | Section 2.3: deck intervals are approximate derivations, not thesis-reported intervals. |
| p-value | Chance of results this extreme under no effect. | 8 | 8 | PODIUM | None applies; do not describe it as the probability the null is true. |
| statistical significance | The result is unlikely under the no-effect benchmark. | 8 | 8 | PODIUM | Sections 3.2-3.4: insignificance is not proof of no effect or equivalence. |
| one standard deviation | One usual unit of variation. | 5 | 8 | PODIUM | None applies. |
| two-tailed test | Tests departures in either direction. | 5 | 9 | PODIUM | None applies; matches the thesis's stated reading of focal results. |
| omitted baseline | The reference periods every estimate is compared with. | 8 | 9 | PODIUM | Design parameter: e<=-3 plus never-acquirers for the event study. |
| parallel trends | Without the event, groups would move similarly. | 7 | 9 | Q&A-FIRST | Section 3.2: the thesis makes no parallel-trends assumption; PRE2 is only a check. |
| Wald test | A direct test of whether two estimates differ. | 8 | 9 | PODIUM | Sections 3.3-3.4: direct difference, not separate significance results. |
| partial-adjustment lag | Last quarter's cash helps predict this quarter's cash. | 8 | 9 | CUTTABLE | Section 3.4: cash persistence rests on the adjacent-stage difference, not a significant GAP level. |
| cash persistence through GAP | Cash shows no detected drop after announcement. | 7 | 9 | PODIUM | Section 3.4: does not claim a significantly elevated GAP level. |
| pooled model | One regression containing both cash and stock. | 7 | 10 | PODIUM | Section 3.3: supports concentration, not a cash-only effect. |
| complete-case sample | Only rows with every required variable observed. | 7 | 10 | CUTTABLE | Section 7 open row: do not infer which Slide 10 panel specification generated post-announcement bins. |
| counterfactual | The unobserved outcome under another condition. | 6 | 12 | PODIUM | Thesis limitation: stock is an imperfect comparison, not a clean counterfactual. |
| endogeneity | Deal timing may move with unobserved factors. | 7 | 12 | Q&A-FIRST | Sections 3.6 and 5: no causal claim; deal timing is chosen. |
| nondifferential | It means error unrelated to deal timing. | 7 | 12 | Q&A-FIRST | Section 3.1: a condition, not an established fact in this design. |
| attenuation | Under that condition, bias would move toward zero. | 8 | 12 | Q&A-FIRST | Section 3.1: direction cannot be signed because negotiation onset is unobserved. |

## Gloss precedence rule

Apply this sequence in order: (1) if the term was glossed earlier, spend zero words and use it unglossed; (2) if not, move its first use and gloss to the earliest earlier slide that already introduces the concept and has at least the gloss's counted words of slack; (3) if no such slide exists, replace the technical term on the current slide with the lay framing; (4) if that replacement exceeds the slide ceiling, delete items from that slide's cut_order from the bottom upward until it fits; (5) if all cuttable items are gone, omit the technical term and keep only the lay framing. Never exceed the ceiling and never leave an unglossed first use.

**Worked example.** Example: if 'Wald test' first arrives on Slide 9 with no room, first check whether Slide 4 has eight words of genuine slack and already introduces direct difference testing. If yes, gloss it there once. If not, use 'a direct test of whether two estimates differ' on Slide 9 and remove the last-ranked Slide 9 element, the point-by-point coefficient walk, until the slide is back within 265 words.
