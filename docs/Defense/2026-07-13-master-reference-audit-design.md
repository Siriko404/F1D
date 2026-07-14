# Master Reference Audit Design

Date: 2026-07-13
Status: Approved audit approach

## Objective

Audit the complete `DEFENSE_PRESENTATION_MASTER_REFERENCE.txt` against the
complete `_thesis_FLAT.tex` and authoritative academic-presentation guidance.
Produce an evidence-backed audit report before modifying either the master
reference or the active HTML/CSS deck.

## Inputs and authority

1. Thesis content authority:
   `docs/Thesis/_uottawa_rewrite/_thesis_FLAT.tex`
2. Artifact under audit:
   `docs/Defense/DEFENSE_PRESENTATION_MASTER_REFERENCE.txt`
3. Presentation-standard authority, in descending order:
   - official uOttawa and Telfer requirements;
   - reputable university defense and research-presentation guidance;
   - reputable research-communication guidance.

External sources may define presentation standards only. Every empirical value,
claim, chart, and diagram proposed for the defense must be derived solely from
the flattened thesis. No dataset, analysis code, generated output, or other
repository evidence may supply presentation content.

## Scope

Everything in the master reference is auditable:

- overall story and slide architecture;
- slide count, order, additions, removals, merges, and splits;
- every factual, numerical, legal, and interpretive claim;
- timing allocations and the approximately 18-minute rehearsed target;
- suggested spoken content and transitions;
- visualizations, tables, slide density, typography, and accessibility;
- Q&A preparation and backup-slide plan;
- implementation and rendering standards;
- stale status statements and internal contradictions.

The existing four-slide HTML/CSS deck is excluded. It will be audited separately
after Sina approves the master-reference audit.

## Audit method

### Track 1: Thesis fidelity

Check each presentation claim against thesis prose, equations, tables, notes,
and appendices. Classify it as:

- `verified`;
- `defensible inference`;
- `unsupported/overstated`.

Check numerical values, units of observation, sample restrictions, statistical
significance, comparison groups, causal language, mechanism language, and all
stated limitations.

### Track 2: Academic presentation standards

Research and cite the governing or advisory source for each relevant standard.
Classify each recommendation as:

- `formal requirement`;
- `strong academic convention`;
- `design judgment`.

Determine rather than assume the appropriate use and amount of:

- conceptual diagrams;
- event timelines;
- coefficient and event-study plots;
- tables versus graphical summaries;
- citations and source footers;
- text density, font size, contrast, and accessibility;
- title, methods, results, limitations, conclusion, and backup slides.

No fixed visual quota is imposed in advance.

### Track 3: Whole-presentation architecture

Test whether the presentation:

- states the problem, question, contribution, design, results, and boundaries;
- gives each slide one clear job;
- avoids duplicated evidence and redundant visuals;
- devotes time in proportion to thesis importance;
- distinguishes main results from robustness and secondary analyses;
- represents the thesis as a whole without reproducing every chapter;
- preserves enough time for delivery variation within the 20-minute limit.

## Finding format

Only actionable findings appear in the visible report. Each finding contains:

1. severity: `critical`, `major`, or `minor`;
2. location in the master reference;
3. affected slide or cross-cutting section;
4. claim grade or standards-authority label;
5. thesis or web evidence;
6. why the issue matters;
7. exact recommended correction or replacement.

Passing claims are checked internally but are not enumerated unless needed to
establish that a slide is sound.

## Report structure

1. Executive verdict
2. Critical corrections
3. Whole-story and timing findings
4. Slide-by-slide actionable findings
5. Visualization and table recommendations
6. Q&A and backup-slide findings
7. Build-standard and accessibility findings
8. Proposed corrected architecture
9. Items that cannot be resolved from the two source files

## Severity definitions

- `critical`: could misstate the thesis, violate a formal requirement, or create
  a serious defense vulnerability.
- `major`: materially harms comprehension, evidentiary precision, timing, or
  professional presentation quality.
- `minor`: worthwhile correction with limited effect on the defense outcome.

## Verification and stopping rule

Before delivering the report:

- recheck every quoted number and unit against the thesis;
- confirm every external recommendation is supported by its cited source;
- distinguish requirements from conventions and design judgments;
- scan for contradictions between the executive verdict, slide findings, and
  proposed architecture;
- verify that no presentation content came from outside the flattened thesis;
- leave the master reference and HTML/CSS deck unchanged.

The audit ends with the report and waits for Sina's approval. Corrections to the
master reference begin only after that approval.
