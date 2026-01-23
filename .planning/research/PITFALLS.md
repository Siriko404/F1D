# Domain Pitfalls: Academic Replication Packages

**Domain:** Empirical Finance Research Pipeline Documentation
**Researched:** 2026-01-22
**Confidence:** HIGH (based on AEA Data Editor guidance, DCAS v1.0, TIER Protocol 4.0)

## Overview

This document catalogs pitfalls specific to academic replication packages in empirical finance research. These are the actual reasons packages get rejected, require revisions, or fail verification by journal data editors. Sources include AEA Data and Code Availability Policy, Social Science Data Editors' guidance, and TIER Protocol standards.

---

## Critical Pitfalls

Mistakes that cause outright rejection or major revision requests from data editors.

### Pitfall 1: Missing or Inadequate Data Availability Statement

**What goes wrong:** Authors provide data files or code but fail to document how an independent researcher can obtain the original data. For CRSP/Compustat/earnings call data, this is especially common because authors assume "everyone knows" how to get WRDS data.

**Why it happens:** 
- Authors conflate "I have the data" with "the data is documented"
- Assumption that commercial database access is self-explanatory
- Focus on code rather than data provenance

**Consequences:**
- Immediate revision request from AEA Data Editor
- Verification cannot proceed until resolved
- Delays acceptance by weeks or months

**Prevention:**
1. For each data source, document in README:
   - Full name of data provider (e.g., "Center for Research in Security Prices (CRSP)")
   - Access mechanism (e.g., "via WRDS subscription")
   - Monetary and time cost to obtain access
   - Specific tables/datasets used with identifiers
   - Date range of data extract
   - Any filters applied during download
2. Include even for data you cannot redistribute

**Detection (warning signs):**
- README mentions data files without explaining their origin
- Code references input files with no corresponding provenance documentation
- "Data available upon request" without explaining the request process

**Phase to address:** Documentation/README phase
**DCAS Reference:** Rules #1, #2, #3

---

### Pitfall 2: Undocumented Sample Selection Criteria

**What goes wrong:** The paper reports "our sample consists of 15,847 firm-quarters" but the replication package doesn't document exactly how that number was derived. Reviewers cannot trace from raw data to final sample.

**Why it happens:**
- Sample construction evolved over drafts; final criteria not consolidated
- Filters scattered across multiple scripts without summary
- "Obvious" exclusions (e.g., financials, utilities) not explicitly stated
- Missing firms due to merge failures not quantified

**Consequences:**
- Reviewers question whether results are cherry-picked
- Cannot verify sample is as described in paper
- Thesis committee may require sample reconstruction demonstration
- Journal editors flag as reproducibility concern

**Prevention:**
1. Create explicit sample construction documentation showing:
   - Starting universe (e.g., "all CRSP common stocks, share codes 10/11")
   - Each filter applied with observation counts before/after
   - Merge success rates between datasets
   - Final sample count matching paper exactly
2. Every script should output observation counts at each stage
3. README should include "Sample Construction" section with cascade table

**Detection (warning signs):**
- Scripts apply filters without logging how many observations dropped
- No single place documents all exclusion criteria
- Sample size in paper doesn't match what code produces
- Merge operations don't report match rates

**Phase to address:** Statistics instrumentation phase (add to every script)
**DCAS Reference:** Rule #7 (data transformation code)

---

### Pitfall 3: Non-Reproducible Outputs (Bitwise Non-Identical Results)

**What goes wrong:** Running the same code twice produces different results, or results differ from what's in the paper. Common in finance research due to floating-point operations, random seeds, and parallel processing.

**Why it happens:**
- Random number generators not seeded
- Parallel processing introduces non-determinism
- Floating-point operations accumulate differently across runs
- Sort order not guaranteed for ties
- Package versions changed between paper draft and submission

**Consequences:**
- Data editor cannot verify results match paper
- Raises suspicion about result validity
- May require complete re-analysis with documented environment

**Prevention:**
1. Set explicit random seeds at script start (project uses seed 42)
2. Pin thread count to 1 for deterministic parallel operations
3. Use stable sort algorithms; break ties explicitly
4. Document exact package versions in requirements.txt
5. Log computational environment at runtime (Python version, package versions)
6. Re-run entire pipeline before submission and verify outputs match paper

**Detection (warning signs):**
- Scripts use `np.random` or `random` without setting seed
- Parallel operations without fixed worker counts
- No requirements.txt or environment specification
- Results in 4_Outputs don't match paper tables exactly

**Phase to address:** Statistics phase (add environment logging) + pre-submission verification
**DCAS Reference:** Rule #8 (analysis code must reproduce results)

---

### Pitfall 4: Missing Code for Data Transformations

**What goes wrong:** Replication package includes analysis code and final datasets but omits the code that transformed raw data into analysis-ready format. AEA policy explicitly requires transformation code even when raw data cannot be shared.

**Why it happens:**
- Authors think "I can't share the data, so why include the code?"
- Data cleaning was done interactively and never scripted
- Transformations happened in Excel or GUI tools
- Legacy code from early project stages was lost

**Consequences:**
- Explicit policy violation (DCAS Rule #7)
- Cannot verify data manipulations are as described
- Revision request to provide all transformation code

**Prevention:**
1. Include ALL code from raw data to final analysis, even if data is confidential
2. Never do transformations manually or in GUI tools
3. Maintain complete script chain: raw -> cleaned -> merged -> analysis
4. This project's 4-stage structure (Sample -> Text -> Financial -> Econometric) naturally supports this

**Detection (warning signs):**
- Scripts read from "cleaned" or "processed" files with no corresponding cleaning code
- Gaps in the step numbering (e.g., scripts 2.1, 2.3, 2.5 exist but not 2.2, 2.4)
- README describes transformations that have no corresponding code

**Phase to address:** Code audit before documentation
**DCAS Reference:** Rule #7 (data transformation code required even without data)

---

### Pitfall 5: Hardcoded Paths Breaking Portability

**What goes wrong:** Code contains absolute paths like `C:\Users\researcher\thesis\data\` that only work on the author's machine. Replicator must manually edit dozens of files to run the code.

**Why it happens:**
- Development convenience (paths worked for author)
- Not tested on clean machine
- Path handling differs across operating systems

**Consequences:**
- Replicator frustration and errors
- AEA Data Editor notes as "not one-click reproducible"
- Revision request to fix all paths

**Prevention:**
1. Use configuration file for all paths (project.yaml)
2. All paths relative to project root
3. Use pathlib for cross-platform compatibility
4. Test on fresh clone before submission
5. README documents single config change needed

**Detection (warning signs):**
- Grep for `C:\`, `/Users/`, `/home/` in code
- Paths defined inside scripts rather than config
- Different scripts use different base directories

**Phase to address:** Code standardization (verify all scripts read from project.yaml)
**DCAS Reference:** TIER Protocol portability standard

---

### Pitfall 6: Missing Computational Requirements

**What goes wrong:** README doesn't specify software versions, required packages, hardware requirements, or expected runtime. Replicator installs wrong versions and gets different results or errors.

**Why it happens:**
- Assumed "everyone uses the same setup"
- Requirements evolved during project without tracking
- Runtime never measured (author's machine is fast)

**Consequences:**
- Replicator cannot recreate environment
- Version mismatches cause silent failures or different results
- AEA Data Editor cannot plan verification resources

**Prevention:**
1. Generate requirements.txt with pinned versions: `pip freeze > requirements.txt`
2. Document in README:
   - Python version (e.g., 3.11.x)
   - Operating system tested on
   - RAM requirements (especially for large merges)
   - Disk space needed
   - Expected runtime per script and total
3. Include setup instructions

**Detection (warning signs):**
- No requirements.txt in repository
- README mentions "Python" without version
- No runtime estimates anywhere
- Scripts import packages not in requirements

**Phase to address:** Documentation/README phase
**DCAS Reference:** Rule #13 (README must list all dependencies and requirements)

---

## Moderate Pitfalls

Mistakes that cause revision requests but don't block verification.

### Pitfall 7: Incomplete Variable Documentation

**What goes wrong:** Dataset contains variables like `ret_adj`, `clarity_score`, `sue_rank` without documentation of their construction, allowed values, or meaning.

**Why it happens:**
- Variable names seem "self-explanatory" to author
- Documentation created early and not updated
- Variables added during revisions without updating codebook

**Consequences:**
- Replicator cannot verify variable construction is correct
- Reviewers question whether variables match paper description
- Data editor requests metadata improvement

**Prevention:**
1. Create codebook/data dictionary for each output dataset
2. Include for each variable:
   - Name, type, allowed values
   - Construction formula or source
   - Missing value treatment
   - Reference to paper section using it
3. Statistics output should include variable summaries automatically

**Detection (warning signs):**
- Output datasets have no accompanying documentation
- Variable names are cryptic abbreviations
- Statistics show unexpected missing values or ranges

**Phase to address:** Statistics instrumentation + data appendix creation
**DCAS Reference:** Rule #5 (metadata for variables)

---

### Pitfall 8: Missing Data Citations

**What goes wrong:** Paper uses CRSP, Compustat, I/B/E/S, earnings call transcripts but doesn't cite them as data sources in the references section.

**Why it happens:**
- Data citations are newer requirement (post-2019 emphasis)
- Authors cite academic papers but not data sources
- Confusion about how to cite commercial databases

**Consequences:**
- AEA Data Editor revision request
- Delays during copyediting
- Violates DCAS Rule #6

**Prevention:**
1. Cite every data source in paper's reference section
2. Use proper data citation format (see AEA Sample References)
3. Include data citations in README as well
4. Example: `Center for Research in Security Prices (CRSP). 2020. "CRSP US Stock Database." Wharton Research Data Services. https://wrds-www.wharton.upenn.edu/`

**Detection (warning signs):**
- Paper mentions data sources only in text, not references
- README lists data sources without formal citations
- In-text mentions like "we use CRSP data" without citation

**Phase to address:** Documentation/README phase
**DCAS Reference:** Rule #6 (all data must be cited)

---

### Pitfall 9: No Master Script / Unclear Execution Order

**What goes wrong:** Replication package contains 15 scripts but no documentation of which order to run them, or which can be skipped if data is unavailable.

**Why it happens:**
- Author knows the order from memory
- Scripts have dependencies that aren't documented
- Some scripts are obsolete but still in package

**Consequences:**
- Replicator runs scripts in wrong order, gets errors
- Hours wasted figuring out dependencies
- AEA Data Editor notes as "not minimal intervention"

**Prevention:**
1. README includes explicit numbered execution order
2. Create master script that runs all steps (or document why not possible)
3. Document which outputs each script produces
4. Map scripts to paper tables/figures
5. This project's naming convention (1.0, 1.1, 2.1, etc.) helps but needs README explanation

**Detection (warning signs):**
- README says "run the scripts" without specifying order
- Scripts in package that don't appear in any documentation
- No mapping from scripts to paper exhibits

**Phase to address:** Documentation/README phase
**DCAS Reference:** Rule #13 (README must explain how to reproduce)

---

### Pitfall 10: Statistics Don't Match Paper Tables

**What goes wrong:** Replication package produces Table 1 with N=15,234 but paper says N=15,847. Or means/standard deviations differ in second decimal place.

**Why it happens:**
- Paper revised after tables generated but code not re-run
- Copy-paste errors when transferring to paper
- Sample changed but old numbers in paper
- Rounding differences

**Consequences:**
- Data editor flags discrepancy
- Must investigate whether code or paper is correct
- Delays while regenerating and matching

**Prevention:**
1. Re-run entire pipeline before final submission
2. Generate tables programmatically (LaTeX output from code)
3. Include output verification step that compares to expected values
4. Statistics phase should produce machine-readable outputs for comparison

**Detection (warning signs):**
- Tables in paper were manually formatted
- Last pipeline run was months before submission
- No automated comparison between outputs and paper

**Phase to address:** Statistics phase + pre-submission verification
**DCAS Reference:** Rule #8 (code must reproduce paper results)

---

## Minor Pitfalls

Mistakes that cause delays or annoyance but are quickly fixable.

### Pitfall 11: Platform-Specific Code Issues

**What goes wrong:** Code works on Windows but fails on Linux/Mac due to path separators, line endings, or platform-specific commands.

**Why it happens:**
- Only tested on author's platform
- Used backslashes for paths
- Shell commands only work on one OS

**Prevention:**
1. Use `pathlib.Path` for all path operations
2. Avoid shell commands in Python; use libraries instead
3. Document tested platform in README
4. Test on second platform if possible

**Phase to address:** Code review before documentation

---

### Pitfall 12: Confusing File Structure

**What goes wrong:** Replicator cannot find files mentioned in README, or folder structure is too deep/complex to navigate.

**Why it happens:**
- Structure evolved organically
- Archive/backup folders left in package
- Naming conventions inconsistent

**Prevention:**
1. Clean package before submission (remove __pycache__, .DS_Store, backups)
2. Use consistent naming convention (this project's Stage.Step_Name pattern)
3. Keep structure flat enough to be understandable
4. README describes structure explicitly

**Phase to address:** Package cleanup before submission

---

### Pitfall 13: Missing Runtime Estimates

**What goes wrong:** Replicator allocates 2 hours but job runs for 3 days. Or expects long run but it finishes in 5 minutes (makes them worry something failed).

**Why it happens:**
- Author never timed the runs
- Runtime varies dramatically by machine
- Individual scripts timed but not total

**Prevention:**
1. Time each script during final run
2. Document in README: individual script times and total
3. Note hardware used for timing
4. Flag long-running steps (>1 hour) prominently

**Phase to address:** Statistics phase (add timing output) + README

---

## Finance-Specific Pitfalls

Issues particular to empirical finance research with CRSP/Compustat data.

### Pitfall 14: WRDS Data Redistribution Violation

**What goes wrong:** Author includes CRSP or Compustat extracts in replication package, violating WRDS terms of service.

**Why it happens:**
- Author wants to be "complete"
- Doesn't realize redistribution is prohibited
- Confused about what can/cannot be shared

**Consequences:**
- Data editor requires removal
- Potential licensing issues
- Delays for package revision

**Prevention:**
1. NEVER include raw CRSP/Compustat/IBES data in deposit
2. Provide code that works with WRDS access
3. Document exact WRDS query to recreate data
4. May provide synthetic example data for code testing

**Phase to address:** Package preparation (audit for restricted data)

---

### Pitfall 15: Undocumented Link Table Methodology

**What goes wrong:** Paper merges CRSP with Compustat, earnings calls with ExecuComp, etc., but doesn't document the linking methodology or success rates.

**Why it happens:**
- Link tables are "standard" (CRSP-Compustat Merged)
- But link quality varies; authors don't report match rates
- Ambiguous matches resolved silently

**Consequences:**
- Reviewers cannot assess sample attrition due to linking
- Different link methods yield different samples
- Core reproducibility concern for finance papers

**Prevention:**
1. Document link table source and version
2. Report match rates at each merge
3. Document how ties/ambiguities are resolved
4. Statistics phase should output merge diagnostics automatically

**Phase to address:** Statistics instrumentation (add merge diagnostics)

---

### Pitfall 16: Text Data Processing Not Reproducible

**What goes wrong:** Paper analyzes earnings call transcripts but text preprocessing (tokenization, cleaning) is not fully documented or reproducible.

**Why it happens:**
- NLP preprocessing has many implicit choices
- Dictionaries updated without versioning
- Regular expressions not documented
- Encoding issues across platforms

**Consequences:**
- Different preprocessing yields different measures
- Cannot verify text variable construction
- Raises questions about robustness

**Prevention:**
1. Version and include all dictionaries used
2. Document every text preprocessing step
3. Log tokenization choices (lowercase, stemming, stopwords)
4. Include character encoding handling explicitly
5. This project's C++ tokenizer should have documented behavior

**Phase to address:** Text processing documentation + statistics

---

## Phase-Specific Warnings

| Phase/Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Sample Construction (1_Sample) | Undocumented selection criteria | Add cascade table to every script output |
| Text Processing (2_Text) | Non-reproducible tokenization | Version dictionaries, document all choices |
| Financial Features (3_Financial) | Missing link methodology | Document merge success rates |
| Econometric (4_Econometric) | Results don't match paper | Re-run before submission, automate table generation |
| README Creation | Incomplete Data Availability Statement | Use Social Science Data Editors' template |
| Statistics Addition | Missing variable documentation | Add codebook generation to each script |
| Package Preparation | Includes restricted data | Audit for CRSP/Compustat before deposit |

---

## Pre-Submission Checklist

Based on AEA Data Editor requirements and common rejection reasons:

### Data Documentation
- [ ] Data Availability Statement for every data source
- [ ] Access instructions including cost and time
- [ ] All data sources cited in references
- [ ] Sample selection fully documented with counts
- [ ] No restricted data (CRSP/Compustat) in deposit

### Code Documentation  
- [ ] All transformation code included (even without data)
- [ ] No hardcoded paths (all from config)
- [ ] Execution order documented
- [ ] Script-to-table/figure mapping provided
- [ ] Package versions in requirements.txt

### Reproducibility
- [ ] Random seeds set
- [ ] Deterministic outputs verified
- [ ] Re-run produces same results as paper
- [ ] Runtime estimates documented
- [ ] Platform requirements stated

### README Completeness (per DCAS #13)
- [ ] Data Availability Statement
- [ ] Computational requirements
- [ ] Software and hardware specifications
- [ ] Step-by-step instructions
- [ ] Expected outputs described
- [ ] All data cited

---

## Sources

| Source | Type | Confidence |
|--------|------|------------|
| [AEA Data and Code Availability Policy](https://www.aeaweb.org/journals/data/data-code-policy) | Official | HIGH |
| [Data and Code Availability Standard v1.0](https://datacodestandard.org/) | Official | HIGH |
| [TIER Protocol 4.0](https://www.projecttier.org/tier-protocol/protocol-4-0/) | Official | HIGH |
| [AEA Data Editor Preparation Guide](https://aeadataeditor.github.io/aea-de-guidance/preparing-for-data-deposit.html) | Official | HIGH |
| [Social Science Data Editors' Template README](https://social-science-data-editors.github.io/template_README/) | Official | HIGH |
| [AEA Data Editor FAQ](https://aeadataeditor.github.io/aea-de-guidance/FAQ.html) | Official | HIGH |

---

*This pitfalls catalog should be consulted when instrumenting statistics, creating README documentation, and preparing the final replication package.*
