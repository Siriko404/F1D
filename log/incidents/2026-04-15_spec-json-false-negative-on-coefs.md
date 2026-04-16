# Lessons Learned: Claimed Spec JSON Has No Coefficients — Read 80/700 Lines Then Declared

**Date:** 2026-04-15
**Severity:** Medium
**Status:** Resolved (same session)

## Incident Summary

**What happened:** While designing a programmatic extraction approach to replace error-prone LLM cell transcription, I read 80 lines of a ~700-line `suite_spec_H1.json` file and declared "spec JSON is the CONFIGURATION spec — NOT the regression results. It does NOT contain the actual regression coefficients." The user challenged this ("are you sure?"). On full read, the JSON contains EVERY coefficient (IVs AND controls) with beta, se, p_two, p_one per variable per column — exactly the complete machine-readable data needed. My false claim nearly derailed the programmatic-extraction approach toward unnecessary .txt file parsing.

**When:** 2026-04-15, during the post-red-team architectural discussion

**Impact:** Would have sent the project down a wrong path (parsing linearmodels .txt files instead of reading clean JSON). User caught it with one question. If unchallenged, would have wasted a full session building an unnecessary parser.

**Resolution:** User asked "are you sure?" → re-read full file → found complete coef data at lines 116-189 (col 1) repeating for all 12 columns.

**Time to resolution:** ~2 minutes (one user pushback + one re-read)

## Timeline

| Step | Action | Actor | Outcome |
|------|--------|-------|---------|
| 1 | Read suite_spec_H1.json with `limit=80` | Claude | Saw metadata, IVs list, controls list, header_rows. No coefs in first 80 lines. |
| 2 | Declared "spec JSON does NOT contain coefficients" | Claude | **False claim.** Presented to user as fact with a confident data-flow diagram. |
| 3 | Built alternative proposal around model_diagnostics.csv + .txt parsing | Claude | Wasted analysis time on wrong architecture. |
| 4 | User asked "are you sure?" | User | Direct challenge. |
| 5 | Re-read from line 80 with limit=120 | Claude | Found `"coefs": { "UncAnsCEO": { "beta": ..., "se": ..., "p_two": ..., "p_one": ... }, ... }` for EVERY variable including all controls. |
| 6 | Acknowledged error | Claude | "You were right. I was wrong." |

## Root Cause (5 Whys)

1. Why did I claim the JSON had no coefficients?
   → Because I only read the first 80 lines of a ~700-line file.

2. Why did I only read 80 lines?
   → Because the Read tool defaults to 2000 lines but I set `limit=80` due to token budget concerns from prior token-limit errors in this session.

3. Why didn't I read more after seeing only metadata?
   → Because the first 80 lines showed a complete-looking structure (schema_version, suite_id, title, IVs, controls, header_rows) and I assumed the file was a "config spec" not a "results spec" — the name "suite_spec" reinforced "specification" = "configuration" framing.

4. Why did I present the partial read as a definitive conclusion?
   → **Because I violated Pattern A (don't delegate understanding).** I read a fraction of the file, formed an interpretation, and stated it as fact without qualifying that I'd only seen 80/700 lines.

5. Why didn't I qualify the claim?
   → **Overconfidence from context.** I had just correctly identified model_diagnostics.csv (IVs-only) and regression_results_col*.txt (full output), and the "suite_spec = config" interpretation fit a clean mental model of the data flow. The mental model was wrong, but it felt coherent.

**Root cause:** Partial file read + overconfident conclusion. The same Pattern A failure that produced the Phase 5 audit errors: claiming "verified" without complete evidence.

## Contributing Factors

| Category | Factor | Contribution |
|----------|--------|--------------|
| **Technical** | Token limit on Read tool forced smaller chunks | Created the partial-read constraint |
| **Process** | No rule requiring "read the FULL file before declaring its contents" | Left room for partial-read conclusions |
| **Context** | model_diagnostics.csv (IVs-only) was read first | Primed the expectation that "separate files = separate data types" |
| **Human** | Name-based inference ("spec" = "specification" = "config") | Anchored on filename semantics instead of file contents |
| **Communication** | Stated as fact ("does NOT contain") not hypothesis ("first 80 lines show no coefs, need to check further") | User had to actively challenge rather than being presented with uncertainty |

## Fixes Implemented

| Fix | Type | Location | Status |
|-----|------|----------|--------|
| Update Pattern A in MEMORY.md with this incident as additional evidence | Documentation | `memory/MEMORY.md` Pattern A | Done (below) |
| Update feedback_no_llm_cell_transcription.md to confirm spec JSON IS the complete source | Documentation | `memory/feedback_no_llm_cell_transcription.md` | Done (below) |
| Incident report | Documentation | This file | Done |

## Prevention

**When claiming a file "does not contain X"**: if the file is larger than what was read, say "the first N lines don't show X — need to read further" instead of "the file does not contain X." Absence of evidence in a partial read is not evidence of absence.

**When a user challenges a factual claim with "are you sure?"**: that is a signal to RE-VERIFY, not to defend. The user's skepticism saved a full session of wrong-path work here. Cost of re-reading: 30 seconds. Cost of being wrong unchallenged: hours.

## Lessons

1. **"Are you sure?" is the cheapest verification there is.** The user's one question prevented a full wrong-path session. I should ask myself "am I sure?" before every factual declaration about file contents — especially after partial reads.

2. **Partial reads produce partial conclusions.** 80/700 lines = 11% of the file. Declaring the file's contents from 11% is the same class of error as declaring a regression's significance from 1 of 12 columns. Both are premature pattern closure.

3. **Filename semantics are unreliable.** "suite_spec" could mean "specification for what to run" (config) or "specification of what was found" (results). The file contains both. Reading beats naming.

4. **This is Pattern A again.** The 2026-04-15 cell-transcription failure and this false-negative-on-coefs failure share the same root: I claim to know something I haven't fully read. The transcription failure was "I read the LaTeX but mis-copied values." This failure was "I partially read the JSON and declared its contents." Both are forms of "claimed verified without complete evidence."
