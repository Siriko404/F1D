# Phase 57: V1 LaTeX Thesis Draft - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

## Phase Boundary

Create a comprehensive LaTeX thesis document that academically documents the V1 hypothesis testing results with publication-quality tables and exhibits. The thesis follows the template at `draft template.md` and focuses on three analyses: CEO Clarity replication (4.1.1), H1 Liquidity (4.2), and H2 Takeover Probability (4.3), with the causal narrative that speech uncertainty → illiquidity → takeover opportunities.

---

## Implementation Decisions

### Document Structure

- **Template:** Follow the exact 6-chapter structure from `draft template.md` (Title, Abstract, Chapters 1-6, References, Appendices)
- **Chapter organization:**
  - Chapter 1: Introduction
  - Chapter 2: Conceptual Framework and Empirical Strategy
  - Chapter 3: Data, Sample Construction, and Variable Definitions
  - Chapter 4: Main Results (sequential H1→H2 narrative)
  - Chapter 5: Additional Analyses, Robustness, and Extensions
  - Chapter 6: Conclusion

- **Three analyses integration:**
  - **CEO Clarity (4.1.1):** Supporting validation - brief mention in Chapter 3 descriptive statistics, full replication results in Appendix. Validates that speech uncertainty measures capture intended construct by replicating Dzieliński, Wagner, Zeckhauser (2017/2021).
  - **H1 Liquidity (4.2):** First main result - establishes mechanism (speech uncertainty → stock illiquidity → undervaluation)
  - **H2 Takeover (4.3):** Second main result - consequence of illiquidity mechanism (undervaluation attracts acquirers)

- **Chapter 4 structure (sequential story):**
  - Section 4.1: H1 Liquidity Results (primary specifications, robustness, economic magnitude)
  - Section 4.2: H2 Takeover Results (primary specifications, robustness, economic magnitude)
  - Section 4.3: Combined Discussion (how illiquidity pathway enables takeover exploitation)
  - Emphasizes causal chain: Uncertainty → Illiquidity (H1) → Undervaluation → Takeover (H2)

- **Chapter 3 CEO Clarity placement:**
  - Brief validation in Section 3.4 (Descriptive Statistics): "CEO Clarity measure behaves as expected"
  - Full replication details in Appendix: comparison tables with Dzieliński et al. (2017) results

### Table Formatting

- **Journal style:** JFE/RFS journal style formatting
- **Significance stars:** Standard thresholds (* p<0.1, ** p<0.05, *** p<0.01)
- **Statistics reporting:** Both t-statistics (in parentheses) and standard errors (in brackets) below coefficients
  - Format: `coefficient (t-stat) [std.error]`
- **Table organization:** Separate numbered tables (not multi-panel)
  - Each hypothesis/specification type gets its own table number
  - Easier to reference in text ("Table 2 shows..." vs "Table 2 Panel A")

- **Additional tables required:**
  1. **Specification columns:** Include specification details (yes/no for variables, FE included, clustering level, sample N)
  2. **Control summary table:** Separate table showing all control variables with means, SDs, correlations, VIFs (supports multicollinearity discussion)
  3. **Sample selection flow table:** Showing sample reduction steps (Compustat → CRSP → intersection → exclusions → final)
  4. **Construction details table:** Exact formulas, winsorization rules, data sources for each variable (supports Chapter 3)

- **Table notes:** Comprehensive notes including:
  - Dependent variable transformations
  - Full list of control variables (even if coefficients suppressed)
  - Standard error clustering level
  - Fixed effects included
  - Sample period
  - Any sample restrictions

### Writing Conventions

- **Citation style:** APA 7th edition (Author, Year) in text, alphabetical reference list
- **Mathematical notation:** Standard financial economics notation
  - Greek letters (β, α) for coefficients
  - Subscripts for variables (β₁, X_{i,t})
  - Full LaTeX math formatting throughout

- **Regression equation format:**
  - Full LaTeX equation format with `begin{equation}...end{equation}`
  - Example: `Y_{i,t+1} = α + β X_{i,t} + γ Controls_{i,t} + Firm_FE + Year_FE + ε_{i,t}`

- **Variable names:** Exact code names from scripts used consistently
  - Example: `Manager_QA_Uncertainty_pct`, `Illiquidity_Amihud`, `takeover_completed`
  - No simplified descriptive names - use exact variable names for precision

- **Terminology:** Use "speech uncertainty" as the primary construct term
  - Not "managerial vagueness" (Dzieliński term) or "communication clarity" (broader)
  - Consistent use of "speech uncertainty" throughout

### Result Integration

- **Conversion method:** Python automation - scripts read Phase 55 outputs and generate LaTeX code
- **Script structure:** Separate scripts per hypothesis/table
  - `generate_H1_illiquidity_primary.py` → H1_primary.tex
  - `generate_H1_illiquidity_robustness.py` → H1_robustness.tex
  - `generate_H2_takeover_primary.py` → H2_primary.tex
  - `generate_H2_takeover_robustness.py` → H2_robustness.tex
  - One script per table allows independent debugging and formatting

- **LaTeX generation approach:** Claude's discretion
  - Can choose Jinja2 templates, f-strings, or pandas.to_latex()
  - Implement what works best for the required JFE/RFS formatting

- **Output location:** `4_Outputs/5_LaTeX/YYYY-MM-DD_HHMMSS/tables/`
  - Follows project convention of timestamped output directories
  - Separate folder for LaTeX generation outputs

- **Additional outputs to integrate:**
  1. **Figure generation:** Convert Phase 55 plots to PDF/EPS for LaTeX inclusion
  2. **Summary stats table:** Generate from Phase 55 parquet files (means, SDs, min, max, N)
  3. **Correlation table:** Generate variable correlation matrix from Phase 55 data
  4. **Sample flow diagram:** Create table/diagram showing sample construction steps

### Claude's Discretion

- **LaTeX generation implementation:** Choose the technical approach (Jinja2/f-strings/pandas) that best achieves JFE/RFS formatting requirements
- **Table formatting details:** Spacing, decimal precision, column widths, line breaks within the journal style guidelines
- **Figure format:** Decide between PDF, EPS, or PNG based on LaTeX compilation workflow
- **Table numbering:** Assign table numbers sequentially or by chapter (Table 1 vs Table 3.1) - choose what fits thesis conventions

---

## Specific Ideas

- **Template reference:** Must follow exact structure from `draft template.md` - this is non-negotiable
- **V1 script locations:**
  - CEO Clarity: `2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py`
  - H1 Liquidity: `2_Scripts/4_Econometric/4.2_LiquidityRegressions.py`
  - H2 Takeover: `2_Scripts/4_Econometric/4.3_TakeoverHazards.py`
- **V1 output locations:**
  - CEO Clarity: Outputs in `4_Outputs/4.1_CeoClarity/`
  - H1 Liquidity: `4_Outputs/4.2_LiquidityRegressions/2026-01-22_225401/` (most recent)
  - H2 Takeover: `4_Outputs/4.3_TakeoverHazards/2026-01-22_225409/` (most recent)
- **Replication target:** Dzieliński, Wagner, Zeckhauser (2021) "Straight talkers and vague talkers: CEO Clarity" - paper at `papers/FWP_2017_02_v2.txt`
- **Causal narrative:** Emphasize that H1 creates the mechanism (illiquidity → undervaluation) that enables H2 (takeover opportunities) - this is the story thread

---

## Deferred Ideas

None - discussion stayed within phase scope.

---

*Phase: 57-v1-latex-draft*
*Context gathered: 2026-02-07*
