# Lessons Learned: Pres-Leak False Positive — Wrong Population Diagnostic

**Date:** 2026-04-09
**Severity:** High
**Status:** Resolved

## Incident Summary

I ran a bank-analyst-in-presentation-section diagnostic directly against the raw Capital IQ file `inputs/Earnings_Calls_Transcripts/speaker_data_2014.parquet` and concluded that 9.6% of calls had contamination in `context='pres'` — named individuals like "Spencer Rogers – Goldman Sachs", "Ben Reitzes – Barclays Capital" appearing in presentation sections. I wrote this as a "CRITICAL" finding in `memory/project_capiq_pres_leak.md`, updated the master classifier plan's STATUS SNAPSHOT to mark Manager/CompRep as UNSETTLED, and designed a three-architecture fix plan that included a brokerage-employer exclusion filter on the pres side. I was about to start implementing it before the user challenged the claim.

The user directed me to investigate whether the pipeline already filters non-earnings events. I found that `src/f1d/sample/clean_metadata.py:317` filters `event_type=='1'` at step 1.1, producing `metadata_cleaned.parquet` which flows through `assemble_manifest.py` → `master_sample_manifest.parquet` → `tokenize_transcripts.py::load_speaker_data_batch`, which filters raw `speaker_data_{year}.parquet` to the manifest `file_name` set before `build_linguistic_variables.py::flag_speakers()` ever sees a row.

I re-ran the contamination diagnostic on the manifest-filtered 2014 subset: 6,605 calls instead of 27,627, and 32 bank-in-pres calls instead of 2,664 — **0.48% not 9.6%, a 20x reduction**. Further decomposition showed 16 of those 32 are legitimate self-matches (JPM/GS/Citi/BAC/Piper/Stifel executives on their own bank's earnings call, where the substring "JPMorgan" matches both analyst-employer and issuer). The true residual contamination is 16 / 6,605 = 0.24%. BGT verbatim rule works. No brokerage filter needed.

## Timeline

| Time | Action | Actor | Outcome |
|------|--------|-------|---------|
| ~14:00 | User asks for deep lit review for manager measure | User | Framed the task |
| ~14:30 | Found Ian Gow's BGT replication code; BGT becomes procedural precedent for pres | Claude | Real finding (valid) |
| ~15:00 | Ran top-employer diagnostic on raw `speaker_data_2014.parquet` | Claude | Saw Goldman/Morgan Stanley/DB in pres |
| ~15:15 | Computed "9.6% of calls have bank-in-pres" on raw file | Claude | **False-positive born** |
| ~15:30 | Wrote `project_capiq_pres_leak.md` as "CRITICAL" | Claude | Persisted false claim to memory |
| ~15:45 | Updated master plan STATUS SNAPSHOT with Manager/CompRep "UNSETTLED" blocker | Claude | Amplified false claim |
| ~16:00 | Proposed three architectures including brokerage filter | Claude | Built fix plan around false claim |
| ~16:30 | Session compaction; false finding survived into summary | System | Wrong claim entrenched |
| ~17:00 | Post-compaction: began investigating Unified-info.parquet per user direction | Claude | Started pipeline tracing |
| ~17:05 | Found event_type column in Unified-info; checked event distribution | Claude | 70.3% event_type='1', 29.7% other |
| ~17:08 | Grepped src/ for `event_type`; found `clean_metadata.py:317` filter | Claude | Identified upstream filter |
| ~17:10 | User interrupted: "we already are excluding the non earnings calls... investigate it thoroughly!" | User | Critical redirection |
| ~17:15 | Re-ran diagnostic on manifest-filtered 2014 subset | Claude | **0.48%, not 9.6%** |
| ~17:20 | Decomposed the 32 residual calls: 16 self-matches, 16 true contamination | Claude | Real residual = 0.24% |
| ~17:30 | Started retrospective and memory corrections | Claude | This report |

**Point of no return:** 15:30, when I wrote the false claim to persistent memory without first verifying that the classifier sees the population I measured.

## Root Cause

**Skipped upstream-pipeline tracing when diagnosing a data-quality issue.** I characterized the raw input file instead of the effective sample that the classifier consumes. In a multi-step pipeline with filtering stages between raw input and the target consumer, a diagnostic on the raw input measures a different population than the classifier ever sees. I had no procedural rule enforcing "trace from raw input to the point of consumption, test on the consumed population" before persisting empirical claims.

5 Whys:
1. Why did I write a wrong "CRITICAL" memory? Because I measured bank-in-pres on the raw `speaker_data_2014.parquet`.
2. Why did I measure on the raw file? Because I didn't verify what population the classifier actually consumes.
3. Why didn't I verify the consumption set? Because I treated the classifier file in isolation from its upstream pipeline, assuming raw speaker_data_YYYY.parquet was its direct input.
4. Why did I assume that? Because a prior-session memory (`project_speaker_data_empirical.md`) characterized the raw files directly, anchoring me to the raw-file frame.
5. Why did I let that anchor drive a contamination claim? Because there was no procedural rule requiring me to trace data flow before claiming empirical pipeline properties.

## Contributing Factors

| Category | Factor | Contribution |
|----------|--------|--------------|
| Process | No "trace the consumption set" pre-check before persisting empirical claims | Direct cause — a 5-minute grep would have caught it |
| Context | Prior-session memory anchored me to the raw-file frame | Made the raw file feel like the natural unit of analysis |
| Technical | Two layers of indirection (clean_metadata → assemble_manifest → tokenize_transcripts → build_linguistic_variables) between raw input and the classifier | Easy to lose track of intermediate filter steps |
| Human | Dramatic-result bias — 9.6% felt like a major finding worth writing up immediately | Rushed to memorialize before sanity-checking |
| Human | Self-claim vs user-claim asymmetry — global CLAUDE.md tells me to challenge the user's claims but has no symmetric rule for my own claims | Skipped adversarial mode on my own output |
| Communication | Persistent memory + session compaction amplified the wrong claim into the summary | Hard to question on resumption |

## Fixes Implemented

| Fix | Type | Location | Status |
|-----|------|----------|--------|
| Rewrote `project_capiq_pres_leak.md` with the true 0.48% / 0.24% finding and the upstream-filter explanation | Documentation | `memory/project_capiq_pres_leak.md` | Updated |
| Updated master plan STATUS SNAPSHOT: Manager/CompRep → LOCKED; replaced 3 architectures with the single locked 4-layer classifier plan | Documentation | `memory/project_manager_classifier_audit_and_plan.md` | Updated |
| Updated MEMORY.md index descriptions for pres-leak and master plan | Documentation | `memory/MEMORY.md` | Updated |
| Created durable rule: measure contamination on consumed population, not raw input | Rule (as feedback memory) | `memory/feedback_pipeline_consumption_trace.md` | Created |
| Added feedback entry to MEMORY.md index | Documentation | `memory/MEMORY.md` | Updated |
| Wrote this incident report | Documentation | `log/incidents/2026-04-09_pres-leak-false-positive.md` | Created |

## Prevention

The new `feedback_pipeline_consumption_trace.md` rule is loaded via MEMORY.md on every session. It encodes a 4-step procedure:

1. Identify the target consumer (which module/function)
2. Grep backwards from the target to find its input sources, iteratively up to raw inputs
3. List every filter/drop step along the way
4. Run the diagnostic on the post-filter population, not the raw file

It also lists red flags that should trigger this check before writing a "CRITICAL" or "BLOCKER" claim — in particular the raw-file-diagnostic smell.

## Verification

**Test scenario:** Next time I'm about to diagnose a data-quality property of what a downstream module sees, the memory entry for `feedback_pipeline_consumption_trace.md` should surface as relevant. I should grep for filter steps before measuring, and load the filtered output (e.g., `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`) before computing the statistic.

**Success criteria:** Any future contamination claim in a memory file or incident report must include the explicit line "measured on population X (defined as [...])" where X is the downstream-consumed population, not the raw input file.

**Review date:** 2026-04-23 (2 weeks). On review, check whether the rule has been followed in any intervening data-quality diagnostics, and whether any new "CRITICAL" memory files have been written against raw inputs.

## Lessons

1. **In a multi-step pipeline, the "data" is not a file — it's the population that reaches the consumer after all upstream filtering.** A diagnostic on the raw file measures a different thing than a diagnostic on the consumed population. For this project, raw file != manifest-filtered != tokenized output.

2. **Persistence amplifies errors.** A wrong claim written to memory survives compaction, shapes the fix plan, and poisons future sessions. The cost of a 5-minute upstream-grep check before persisting is trivial compared to the cost of unwinding a persisted wrong finding (this retrospective + 5 memory edits + plan redesign).

3. **Dramatic results deserve MORE scrutiny, not less.** A 9.6% contamination rate that would invalidate a well-known paper's method on a vendor should have raised my adversarial-mode flags rather than lowered them. If a finding would invalidate prior work, the prior work probably had a reason for being considered correct, and my diagnostic should be checked before my plan is rewritten.

4. **The adversarial-mode rule in CLAUDE.md is asymmetric and it shouldn't be.** It tells me to challenge the user's claims. It should also tell me to challenge my own empirical claims with the same skepticism, especially before writing them to persistent memory.

5. **When a prior memory characterizes raw data, it's describing the raw schema — not the effective sample.** Memories like `project_speaker_data_empirical.md` correctly document what's in the raw parquet file, but they are not a substitute for tracing what the pipeline keeps.
