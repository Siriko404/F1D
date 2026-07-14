# Panel Design — Two-File Defense Reference Audit

## S2 status

Drafted for verbatim prompt ratification under the revised S1. No expert may launch until
Sina ratifies all five regenerated prompts.

## Ratified scope

- Five independent DeepSeek V4-Pro experts.
- Exactly two local content files are visible to every expert: the audited master reference
  and the authoritative flattened thesis.
- Experts may search the public web and independently raw-download web sources.
- No other repository file, directory listing, archive, prompt, manifest, journal, report,
  source file, deck, handoff, ledger, code file, or other expert artifact is readable.
- The audit includes evidence-grounded recommendations about where visualizations should
  appear, what they should communicate, and when they would be unnecessary or misleading.

## Budget and execution envelope

- One background run per expert, started together.
- At most 60 model/tool iterations and 120 minutes wall-clock time per expert.
- No automatic substantive retry or follow-on panel. Crash recovery preserves sealed
  journals and re-fires only incomplete experts after their state is reported.
- The Codex coordinator monitors, may interrupt operational failure, and performs the
  mechanical read-back. It adds no findings and rewrites no panel records.

## Mechanical access boundary

Each expert receives a separate policy-enforced Bash proxy and private download subtree.
The proxy permits only:

1. text extraction against the exact two manifest files;
2. text extraction against raw web snapshots inside that expert's private download subtree;
3. raw HTTP capture into that private download subtree; and
4. the exact journal-enforcer append command against that expert's journal.

Repository enumeration, arbitrary filesystem commands, path traversal, reads of the
enforcement implementation, reads of other agents' files, and access to provider secrets
are denied by the tool host. The separate `web_search` tool returns discovery leads only;
its output cannot be cited.

## Facet partition

### 1. Quantitative results and definitions

Owns every numerical, statistical, sample, variable-definition, table, figure, and reported
result claim. It verifies against the flattened thesis and does not judge causal language,
story sequencing, or visual strategy.

### 2. Empirical design, interpretation, and limitations

Owns identification, research design, generated-regressand caveats, timing evidence,
robustness and scrutiny tests, causal boundaries, mechanisms, null-result language, and
limitations. It does not re-audit transcription, timing, or visualization placement.

### 3. Narrative architecture and timing

Owns the defense story, sequence, completeness, redundancy, transitions, emphasis, and
feasibility of the 20-minute budget. It does not decide empirical truth, formal visual
standards, or institutional requirements.

### 4. Slide specification and internal consistency

Owns agreement among each proposed slide's purpose, visible content, narration, takeaway,
timing, and transition, plus contradictions and terminology drift within the master
reference. It checks thesis support but cannot inspect or make claims about deck files.

### 5. Visualization strategy and institutional standards

Owns formal defense requirements, general presentation and visualization best practices,
committee/audience claims, brand/typography/accessibility claims, and evidence-grounded
visualization recommendations. It distinguishes formal rules, research-supported practice,
and professional judgment; it cannot make perceptual claims about an unavailable deck.

## Completion standard

Every expert reads both assigned files, independently captures and registers every cited
web source, covers all duties, records atomic findings/recommendations and honest gaps, and
seals its journal. Read-back begins only after all five journals seal.

Ratification of revised S1 and access boundary: Sina, 2026-07-13 (explicit "go")
Ratification of exact regenerated expert prompts: Sina, 2026-07-13 (explicit "go" after
the five restricted prompts were generated, verified, and opened verbatim)

