# Panel Design — Defense Presentation Master Reference Hard Scrutiny

## S2 status

Drafted for verbatim prompt ratification. No expert may be launched until Sina ratifies
all five generated prompts. Five DeepSeek V4-Pro experts were selected by Sina on
2026-07-13 with the explicit instruction "go."

## Budget and execution envelope

- Panel: five independent DeepSeek V4-Pro experts.
- Initial execution: one background run per expert, started together.
- Per expert: at most 60 model/tool iterations and 120 minutes wall-clock time.
- No automatic substantive retry or follow-on panel. Crash recovery preserves sealed
  journals and re-fires only incomplete experts after the coordinator reports the state.
- The coordinator monitors status, may interrupt a malfunctioning run, and performs the
  mechanical read-back. It does not add findings or rewrite panel records.

## Independence and evidence acquisition

- Every expert receives only the audited master-reference file as assigned context.
- Experts independently explore local material under the Thesis_Bmad project tree and
  independently discover online material relevant to their own facet.
- Any local or online source discovered outside the manifest must be copied or downloaded
  as raw content into the active run's `downloads/` directory, registered in that expert's
  journal, and cited by its returned W-id.
- Search-result text is discovery-only and cannot be evidence.
- The archived master precollection is provenance-only, off-limits to experts, excluded
  from manifests, and uncitable.
- Experts cannot communicate with one another during the primary audit. Cross-facet
  observations become gap records rather than informal handoffs.

## Allowed tool boundary

The harness exposes only:

1. `bash`: Git Bash with read access to the Thesis_Bmad project tree; raw HTTP capture
   through curl/wget; local raw capture through plain copy or git show; text search and
   extraction through rg/find/sed/awk; PDF inspection/extraction through locally installed
   command-line tools; Node execution of the journal enforcer. Writes are restricted to
   the expert's journal and the run's active downloads directory. Model-provider secrets
   are removed from the shell environment.
2. `web_search`: discovery of candidate URLs only. Its returned text is never evidence;
   the expert must capture the underlying source through bash before registration/citation.

## Facet partition

### 1. Quantitative results and definitions

Owns every numerical, tabular, statistical, sample, variable-definition, and reported
result claim. It checks values against independently located thesis/result artifacts and
checks arithmetic relationships. It does not judge causal language or narrative design.

### 2. Empirical design, interpretation, and limitations

Owns identification, research design, generated-regressand caveats, timing evidence,
robustness and scrutiny tests, causal boundaries, mechanism claims, null-result language,
and limitations. It does not re-audit numerical transcription or slide aesthetics.

### 3. Narrative architecture and timing

Owns the defense story, 12-slide sequence, completeness, redundancy, transitions,
allocation of the 20-minute budget, and practical speakability. It does not re-audit
individual numerical values, institutional branding, or source authenticity.

### 4. Slide specification and internal consistency

Owns agreement among each slide's purpose, visible content, narration, takeaway, timing,
and transition; cross-section contradictions; terminology drift; file/deck status claims;
and alignment between the master reference and independently located current deck files.
It does not decide quantitative correctness or brand compliance.

### 5. Institutional, audience, and visual-production validity

Owns committee/audience claims, defense conventions, institutional links, Telfer/uOttawa
brand claims, typography, accessibility, visual-production instructions, and whether
subjective design judgments are mislabeled as facts. Perceptual claims that cannot be
verified with the available text/PDF command-line evidence must be recorded as gaps.

## Completion standard

Each expert must cover every assigned duty, append steps as work occurs, record atomic
findings/risks/recommendations and honest gaps, mark the assigned context read, and seal
its journal. The run advances to read-back only when every journal is sealed.

Ratification of panel count/model: Sina, 2026-07-13 (explicit instruction: "go")
Ratification of exact expert prompts: PENDING

