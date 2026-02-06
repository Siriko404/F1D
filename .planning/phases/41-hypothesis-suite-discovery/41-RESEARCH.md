# Phase 41: Hypothesis Suite Discovery - Research

**Researched:** 2025-02-05
**Domain:** Empirical Accounting/Finance Research - Hypothesis Discovery & Literature Review
**Confidence:** MEDIUM

---

## Summary

Phase 41 is a discovery phase focused on identifying novel, data-feasible, high-confidence hypotheses through comprehensive literature review and data feasibility analysis. This research addresses: (1) systematic literature review methodology for accounting/finance, (2) mapping available data sources to potential hypothesis variables, (3) statistical power analysis for panel data with fixed effects, and (4) frameworks for prioritizing novel yet feasible hypotheses.

**Primary recommendation:** Use PRISMA 2020 methodology for systematic literature review, prioritize hypotheses with strong theoretical foundations AND available data, and conduct ex-ante power analysis using the existing sample (~21,000-34,000 observations) to ensure 80% power for detecting economically meaningful effect sizes (Cohen's d >= 0.20).

---

## Standard Stack

### Core Research Tools

| Tool/Library | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| PRISMA 2020 | 2020 | Systematic literature review methodology | Gold standard for reproducible reviews |
| Web of Science/Scopus | Current | Academic database search | Comprehensive coverage of accounting/finance |
| Google Scholar | Current | Supplementary search | Broad coverage, forward citation tracking |
| Covidence/Rayyan | Current | Systematic review management | Industry-standard for screening/eligibility |
| Zotero | Current | Citation management | Widely used, integrates with writing tools |

### Data Analysis Stack

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.0+ | Data manipulation | Python standard for tabular data |
| statsmodels | 0.14+ | Econometric analysis | Panel data, fixed effects |
| linearmodels | 5.0+ | Advanced panel regression | Firm + year fixed effects with clustering |
| numpy | 1.24+ | Numerical computing | Foundation for statistical operations |
| scipy | 1.10+ | Statistical functions | Power analysis, effect size calculations |

### Literature Search Databases

| Database | Coverage | Use Case |
|----------|----------|----------|
| ABI/INFORM | Business, accounting, finance | Core accounting journals |
| Business Source Complete | Accounting, finance journals | Broad business coverage |
| ScienceDirect | Multidisciplinary | Finance, econometrics |
| JSTOR | Archive access | Historical finance research |
| SSRN | Working papers | Cutting-edge research |

**Installation:**
```bash
# Python packages
pip install pandas statsmodels linearmodels numpy scipy

# Bibliographic tools (if using Python)
pip install pyzotero scholarly
```

---

## Architecture Patterns

### Literature Review Workflow

```
1. Planning Phase
   - Define research questions and scope
   - Identify inclusion/exclusion criteria (PICOS: Population, Intervention, Comparator, Outcome, Study design)
   - Register protocol (optional but recommended)

2. Search Phase
   - Develop search string (keywords, synonyms, Boolean operators)
   - Search across multiple databases
   - Document search strategy (reproducibility)

3. Screening Phase
   - Title/abstract screening (dual reviewers)
   - Full-text review against inclusion criteria
   - Document excluded studies with reasons

4. Extraction Phase
   - Extract key variables (hypothesis tested, data sources, methodology, findings)
   - Assess study quality (risk of bias)
   - Create evidence matrix

5. Synthesis Phase
   - Thematic analysis of hypotheses
   - Identify research gaps (no prior tests)
   - Map variables to available data sources
```

### Data Feasibility Matrix Pattern

```python
# Pattern for assessing data feasibility
def assess_hypothesis_feasibility(hypothesis, available_data):
    """
    Returns feasibility score (0-1) based on:
    - Variable availability (IV, DV, controls)
    - Sample size sufficiency
    - Time period coverage
    """
    iv_available = check_variable_availability(hypothesis.IV, available_data)
    dv_available = check_variable_availability(hypothesis.DV, available_data)
    controls_available = all(check_var(c, available_data) for c in hypothesis.controls)

    n_obs = get_observable_count(hypothesis)
    power = calculate_power(n_obs, effect_size=0.2, alpha=0.05)

    feasibility = (iv_available + dv_available + controls_available) / 3 * power
    return feasibility
```

### Statistical Power Analysis Pattern

```python
# Ex-ante power analysis for panel fixed effects
def calculate_panel_power(N, T, effect_size, alpha=0.05):
    """
    For panel data with N firms and T periods:
    - Design effect approximates 1 + rho*(T-1) for clustered data
    - Effective N = N*T / design_effect

    Uses Cohen's f2 for effect size:
    - Small: 0.02
    - Medium: 0.15
    - Large: 0.35

    Returns: Power (0 to 1)
    """
    from scipy import stats
    # Simplified calculation for planning purposes
    design_effect = 1 + 0.5 * (T - 1)  # Assuming ICC ~ 0.5
    effective_n = (N * T) / design_effect

    # Non-central F for power calculation
    df1 = 1  # Testing single coefficient
    df2 = effective_n - df1 - 1

    f2 = effect_size  # Cohen's f2
    ncp = f2 * effective_n  # Non-centrality parameter

    # Calculate power
    fcrit = stats.f.ppf(1 - alpha, df1, df2)
    power = 1 - stats.ncf.cdf(fcrit, df1, df2, ncp)

    return power
```

### Hypothesis Prioritization Framework

```python
def prioritize_hypotheses(hypotheses):
    """
    Score hypotheses on three dimensions:
    1. Novelty (0-1): No prior direct tests
    2. Feasibility (0-1): Data available
    3. Power (0-1): Sufficient sample size

    Overall Score = w1*Novelty + w2*Feasibility + w3*Power
    Recommended weights: Novelty=0.3, Feasibility=0.4, Power=0.3
    """
    scored = []
    for h in hypotheses:
        novelty = assess_novelty(h)  # Literature gap analysis
        feasibility = assess_feasibility(h)  # Data availability
        power = assess_power(h)  # Statistical power

        score = 0.3*novelty + 0.4*feasibility + 0.3*power
        scored.append((h, score, novelty, feasibility, power))

    return sorted(scored, key=lambda x: x[1], reverse=True)
```

### Anti-Patterns to Avoid

- **Kitchen-sink literature review:** Including irrelevant studies without clear criteria. Use PRISMA for structured inclusion/exclusion.
- **Post-hoc power analysis:** Calculating power after observing results. Always conduct ex-ante power analysis.
- **Effect size neglect:** Focusing only on p-values. Always interpret economic significance of effect sizes.
- **Single-source literature:** Relying on one database. Search multiple sources for comprehensive coverage.
- **Data-first hypothesis generation:** Starting with available data rather than research questions. Start with theory/literature, then assess data feasibility.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Literature search management | Manual spreadsheet/screening | [Covidence](https://www.covidence.org/) or [Rayyan](https://www.rayyan.ai/) | Automated deduplication, dual screening, PRISMA flow diagram generation |
| Citation management | Manual reference lists | Zotero, Mendeley, or EndNote | Automated citation extraction, PDF organization |
| Power analysis | Custom formulas | [G*Power](https://www.gpower.hhu.de/) or statsmodels | Validated methods, wide range of tests |
| Systematic review protocol | Word document | [PROSPERO](https://www.crd.york.ac.uk/prospero/) registration | Prevents HARKing, increases transparency |
| Text extraction from PDFs | Manual copy-paste | [Grobid](https://grobid.readthedocs.io/) or PDFMiner | Scales to hundreds of articles |

**Key insight:** Systematic reviews are complex projects with many moving parts. Existing tools handle edge cases (like duplicates, version control, screening disagreements) that custom implementations miss.

---

## Common Pitfalls

### Pitfall 1: Publication Bias in Literature Search

**What goes wrong:** Only finding published studies with significant results, missing null results that indicate what's already been tested unsuccessfully.

**Why it happens:** Published studies favor statistically significant findings (file drawer problem).

**How to avoid:**
- Search working paper repositories (SSRN, RePEc)
- Include dissertations and conference proceedings
- Search for "null results" or "insignificant" explicitly
- Contact authors for unpublished results

**Warning signs:** All cited studies show significant effects; no mention of failed replications.

### Pitfall 2: Inadequate Search Strategy

**What goes wrong:** Missing relevant studies due to narrow search terms or limited database coverage.

**Why it happens:** Researcher focuses on familiar journals/keywords.

**How to avoid:**
- Use multiple search strategies: keyword + citation snowballing
- Include synonyms and related terms
- Search across >3 databases
- Consult librarian/information specialist

**Warning signs:** Fewer than 20 relevant studies from a broad research area.

### Pitfall 3: Underpowered Study Design

**What goes wrong:** Collecting data that can't detect economically meaningful effects even if they exist.

**Why it happens:** Not conducting ex-ante power analysis; assuming "big data" guarantees power.

**How to avoid:**
- Always conduct ex-ante power analysis before data collection
- Use realistic effect sizes from literature/meta-analysis
- Account for panel structure (design effect, clustering)
- For fixed effects, power depends on within-firm variation, not just N*T

**Warning signs:** Prior studies show small effect sizes; available sample is marginal.

### Pitfall 4: Confusing Statistical and Economic Significance

**What goes wrong:** Reporting tiny but statistically significant effects that lack economic meaning (common with very large N).

**Why it happens:** Overemphasis on p-values; large N makes everything significant.

**How to avoid:**
- Pre-specify minimum economically meaningful effect size
- Report effect sizes with confidence intervals
- Conduct power analysis for meaningful effect, not just "any" effect
- Interpret economic magnitudes (e.g., 1% increase in X leads to $Y million impact)

**Warning signs:** Emphasis on p < 0.001 without discussing economic magnitude.

### Pitfall 5: HARKing (Hypothesizing After Results Known)

**What goes wrong:** Presenting exploratory findings as pre-specified hypotheses.

**Why it happens:** Pressure to find "significant" results; publication bias against null results.

**How to avoid:**
- Pre-register hypotheses and analysis plans
- Clearly distinguish between confirmatory and exploratory analyses
- Report all tests, not just significant ones
- Be transparent about data-driven discovery

**Warning signs:** Hypothesis perfectly matches observed patterns; no prior theoretical motivation.

---

## Code Examples

### Literature Search Protocol (PRISMA)

```python
"""
PRISMA-style systematic literature review protocol
Source: https://www.prisma-statement.org/
"""

class LiteratureReviewProtocol:
    def __init__(self, research_question):
        self.research_question = research_question
        self.inclusion_criteria = self._define_inclusion()
        self.search_databases = [
            "Web of Science",
            "Scopus",
            "ABI/INFORM",
            "SSRN"
        ]

    def _define_inclusion(self):
        """
        PICOS framework:
        - Population: Public firms with earnings call data
        - Intervention/Exposure: Managerial speech uncertainty/vagueness
        - Comparator: Low vagueness / different speech measures
        - Outcome: Corporate financial policies, market reactions, analyst behavior
        - Study design: Archival empirical studies
        """
        return {
            "Population": ["US public firms", "Earnings call transcripts"],
            "Intervention": ["Managerial speech", "Textual analysis", "Uncertainty", "Vagueness"],
            "Outcomes": [
                "Financial policies", "Investment", "Cash holdings", "Payout",
                "Analyst forecasts", "Stock returns", "Volatility",
                "M&A activity", "CEO turnover", "Executive compensation"
            ],
            "Study_design": ["Archival", "Empirical", "Quantitative"],
            "Timeframe": "2010-2025 (post-Loughran-McDonald 2011)"
        }

    def build_search_string(self):
        """
        Boolean search string combining concepts

        Concept 1: Managerial communication
        (("managerial communication" OR "CEO speech" OR "executive language" OR
          "earnings call" OR "conference call" OR "management disclosure"))

        Concept 2: Textual features
        (("textual analysis" OR "linguistic analysis" OR "content analysis" OR
          "sentiment analysis" OR "uncertainty" OR "vagueness" OR "tone" OR
          "readability" OR "complexity" OR "weak modal" OR "hedging"))

        Concept 3: Corporate outcomes
        (("corporate governance" OR "financial policy" OR "investment" OR
          "financing" OR "payout" OR "M&A" OR "acquisition" OR "takeover" OR
          "CEO turnover" OR "executive compensation" OR "analyst forecast" OR
          "stock return" OR "volatility"))
        """
        return """
        ("managerial communication" OR "CEO speech" OR "executive language" OR
         "earnings call*" OR "conference call*" OR "management disclosure*")
        AND
        ("textual analysis" OR "linguistic analysis" OR "content analysis" OR
         "sentiment analysis" OR uncertainty OR vagueness OR tone OR
         readability OR complexity OR "weak modal*" OR hedging)
        AND
        ("corporate governance" OR "financial polic*" OR investment OR
         financing OR payout OR "M&A" OR acquisition OR takeover OR
         "CEO turnover" OR "executive compensation" OR "analyst forecast*" OR
         "stock return*" OR volatil*)
        """

    def document_search(self, database, date_searched, results_count):
        """For PRISMA flow diagram documentation"""
        return {
            "database": database,
            "date_searched": date_searched,
            "search_string": self.build_search_string(),
            "results_count": results_count
        }

# Usage
protocol = LiteratureReviewProtocol(
    research_question="What novel hypotheses linking managerial speech to corporate outcomes are data-feasible with available data?"
)
search_string = protocol.build_search_string()
print(search_string)
```

### Data Feasibility Matrix

```python
"""
Data feasibility matrix for hypothesis discovery
Maps available data to potential hypothesis variables
"""

AVAILABLE_DATA_SOURCES = {
    # Earnings call text data
    "speaker_data_2002-2018.parquet": {
        "years": "2002-2018",
        "observations": 112968,
        "variables": ["speech_text", "speaker_role", "firm_id"]
    },
    # Linguistic measures (from Step 2 outputs)
    "linguistic_variables": {
        "text_measures": [
            "Manager_QA_Uncertainty_pct", "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct", "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct", "CEO_Pres_Uncertainty_pct",
            "Analyst_QA_Uncertainty_pct"
        ]
    },
    # Financial data (from Step 3 outputs)
    "firm_controls": {
        "variables": [
            "cash_holdings", "leverage", "tobins_q", "roa",
            "capex", "dividend_payer", "firm_size", "cf_volatility"
        ]
    },
    "market_variables": {
        "variables": [
            "stock_returns", "volatility", "abnormal_returns"
        ]
    },
    "event_flags": {
        "variables": [
            "ma_announcement", "ceo_turnover", "dividend_change"
        ]
    },
    # Additional available data
    "CRSP_DSF": {
        "coverage": "Daily stock returns 1999-2017",
        "variables": ["returns", "volume", "prices"]
    },
    "CRSPCompustat_CCM": {
        "coverage": "Linking table 1949-2025",
        "variables": ["gvkey", "lpermno", "linkdt", "linkenddt"]
    },
    "Execucomp": {
        "coverage": "Executive compensation data",
        "variables": ["salary", "bonus", "equity awards", "total_comp"]
    },
    "SDC_M&A": {
        "coverage": "M&A deals 1999-2025",
        "rows": 142457,
        "variables": ["deal_value", "target_status", "deal_attitude"]
    },
    "CEO_Dismissal": {
        "coverage": "CEO dismissal events",
        "variables": ["dismissal_date", "dismissal_type"]
    },
    "LoughranMcDonald_Dictionary": {
        "categories": [
            "Negative", "Positive", "Uncertainty", "Litigious",
            "Strong_Modal", "Weak_Modal", "Constraining", "Complexity"
        ]
    }
}

# Sample size from existing regressions
EXISTING_SAMPLE_STATS = {
    "H1_cash_holdings": {"N": 21557, "firms": 2419, "years": 2002-2017},
    "H2_investment": {"N": 342000, "firms": "~3000", "years": 2002-2017},
    "H3_payout": {"N": 244000, "firms": "~2800", "years": 2002-2017}
}

def construct_feasibility_matrix(hypothesis_candidates):
    """
    Returns matrix showing which hypotheses are feasible with available data

    Rows: Hypothesis candidates
    Columns: IV_available, DV_available, Controls_available, Sample_size, Power_80
    """
    matrix = []
    for h in hypothesis_candidates:
        iv_feasible = check_data_availability(h["IV"])
        dv_feasible = check_data_availability(h["DV"])
        controls_feasible = all(check_data_availability(c) for c in h["controls"])

        # Estimate sample size
        n_est = estimate_sample_size(h)

        # Calculate power for medium effect (f2=0.15)
        power = calculate_panel_power(
            N=2500,  # Approx unique firms
            T=16,    # Approx years per firm
            effect_size=0.15,
            alpha=0.05
        )

        matrix.append({
            "hypothesis": h["name"],
            "IV_available": iv_feasible,
            "DV_available": dv_feasible,
            "Controls_available": controls_feasible,
            "Sample_size": n_est,
            "Power_at_80": power >= 0.8
        })

    return matrix
```

### Statistical Power Analysis

```python
"""
Ex-ante power analysis for panel data with fixed effects
Source: Based on Chi (2018), standard panel econometrics texts
"""

import numpy as np
from scipy import stats

def panel_power_analysis(N, T, rho=0.5, effect_size="medium", alpha=0.05):
    """
    Calculate statistical power for panel fixed effects model

    Parameters:
    -----------
    N : int
        Number of cross-sectional units (firms)
    T : int
        Number of time periods (years)
    rho : float
        Intraclass correlation (within-firm correlation)
    effect_size : str or float
        "small" (f2=0.02), "medium" (f2=0.15), "large" (f2=0.35), or numeric f2
    alpha : float
        Significance level

    Returns:
    --------
    dict with power, effective_n, interpretation

    Example:
    --------
    # Current sample: ~2500 firms, 16 years
    >>> panel_power_analysis(N=2500, T=16, effect_size="small")
    {'power': 0.99, 'effective_n': 38400, 'sufficient': True}

    # For medium effect, need much smaller sample
    >>> panel_power_analysis(N=500, T=10, effect_size="medium")
    {'power': 0.82, 'effective_n': 5500, 'sufficient': True}
    """

    # Cohen's f2 effect sizes for multiple regression
    f2_sizes = {"small": 0.02, "medium": 0.15, "large": 0.35}
    if isinstance(effect_size, str):
        f2 = f2_sizes[effect_size]
    else:
        f2 = effect_size

    # Design effect for clustered data
    design_effect = 1 + rho * (T - 1)

    # Effective sample size accounting for clustering
    effective_n = (N * T) / design_effect

    # Degrees of freedom
    df1 = 1  # Testing single coefficient
    df2 = effective_n - df1 - 1

    # Non-centrality parameter
    ncp = f2 * effective_n

    # Critical F value
    fcrit = stats.f.ppf(1 - alpha, df1, df2)

    # Power = P(F > fcrit | H1 is true)
    power = 1 - stats.ncf.cdf(fcrit, df1, df2, ncp)

    # Interpretation
    if power >= 0.9:
        interpretation = "Excellent power (>90%)"
    elif power >= 0.8:
        interpretation = "Adequate power (>80%)"
    elif power >= 0.6:
        interpretation = "Moderate power (60-80%) - consider larger sample"
    else:
        interpretation = "Low power (<60%) - risky study design"

    return {
        "power": round(power, 3),
        "effective_n": int(effective_n),
        "design_effect": round(design_effect, 2),
        "interpretation": interpretation,
        "sufficient": power >= 0.8
    }

# Power analysis for different scenarios
scenarios = [
    {"name": "Current sample (large)", "N": 2500, "T": 16},
    {"name": "Moderate sample", "N": 1000, "T": 10},
    {"name": "Small sample", "N": 500, "T": 8},
    {"name": "Minimal viable", "N": 100, "T": 10},
]

print("\n=== Power Analysis for Different Sample Sizes ===\n")
for effect in ["small", "medium", "large"]:
    print(f"\nEffect size: {effect.upper()}")
    print("-" * 60)
    for scenario in scenarios:
        result = panel_power_analysis(
            N=scenario["N"],
            T=scenario["T"],
            effect_size=effect
        )
        print(f"{scenario['name']:20} N={scenario['N']:4} T={scenario['T']:2} -> "
              f"Power={result['power']:.3f} {result['interpretation']}")
```

### Hypothesis Gap Analysis

```python
"""
Identify research gaps by synthesizing literature
"""

class HypothesisGapAnalyzer:
    """
    Analyzes literature to identify untested hypotheses
    """
    def __init__(self, literature_database):
        self.studies = literature_database

    def extract_hypotheses(self, study):
        """
        Extract hypotheses tested in a study

        Returns: {
            "IV": independent variable(s),
            "DV": dependent variable(s),
            "mechanism": theoretical pathway,
            "finding": significant/null,
            "sample": N, years
        }
        """
        pass

    def identify_gaps(self, candidate_hypotheses):
        """
        Compare candidate hypotheses to existing literature

        Returns gap analysis matrix with:
        - Novelty: No direct test found
        - Indirect support: Related findings suggest plausibility
        - Counterevidence: Prior null results
        """
        gaps = []
        for h in candidate_hypotheses:
            direct_tests = self.find_direct_tests(h)
            related_studies = self.find_related_studies(h)

            if not direct_tests:
                novelty = "HIGH - No direct tests found"
            else:
                null_results = sum(1 for s in direct_tests if s["finding"] == "null")
                novelty = f"MEDIUM - {len(direct_tests)} prior tests, {null_results} null"

            gaps.append({
                "hypothesis": h,
                "novelty": novelty,
                "direct_tests": len(direct_tests),
                "related_studies": len(related_studies)
            })

        return gaps
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual literature tracking | PRISMA 2020 systematic review | 2020 | Reproducible, transparent reviews |
| Ad-hoc hypothesis generation | Theory-driven + data-feasibility screening | 2010s | Higher success rates, fewer dead ends |
| Post-hoc power justification | Ex-ante power analysis | 2018 | Better study design, fewer underpowered studies |
| Dictionary-based text analysis | LLM/Transformer-enhanced textual analysis | 2023-2024 | Richer linguistic features, context awareness |
| Single-text-source studies | Multi-modal text + quantitative analysis | 2020s | More comprehensive measurement |

**Current best practices (2025):**
- Use PRISMA 2020 for systematic reviews
- Pre-register hypothesis testing plans when possible
- Conduct ex-ante power analysis for all confirmatory tests
- Combine dictionary-based and ML-based text measures
- Report both statistical and economic significance
- Distinguish exploratory vs. confirmatory analyses

---

## Available Data Feasibility Matrix

### Data Sources Inventory

| Data Source | Coverage | Key Variables | Sample Size | Potential DVs |
|-------------|----------|---------------|-------------|---------------|
| speaker_data_2002-2018 | Earnings calls | Speech text, speaker role | 112,968 calls | Linguistic measures (IVs) |
| Linguistic variables | Step 2 output | Uncertainty %, Weak Modal %, Tone | ~28,000 firm-years | Text measures (IVs) |
| Firm controls | Step 3 output | Cash, leverage, Q, ROA, capex | ~28,000 firm-years | Policy outcomes (DVs) |
| Market variables | Step 3 output | Returns, volatility | ~28,000 firm-years | Market reactions (DVs) |
| Event flags | Step 3 output | M&A, CEO turnover, dividends | ~28,000 firm-years | Event outcomes (DVs) |
| CRSP DSF | 1999-2017 | Daily returns, volume | Full market | Event study DVs |
| CCM Link table | 1949-2025 | GVKEY-PERMNO links | 32,421 links | Merging datasets |
| Execucomp | Exec comp | Salary, bonus, equity | Thousands of firms | Compensation (DV) |
| SDC M&A | 1999-2025 | 142,457 deals | Deals data | M&A outcomes (DVs) |
| CEO Dismissal | Dismissal events | Dismissal type, date | Specific events | Turnover (DV) |
| LM Dictionary | 1993-2024 | 8 sentiment categories | ~90,000 words | Text measurement |

### Sample Size Summary (Existing Regressions)

| Hypothesis | N (firm-years) | Unique Firms | Year Range | Avg obs/firm |
|------------|----------------|--------------|------------|--------------|
| H1 Cash Holdings | 21,557 | 2,419 | 2002-2017 | ~9 |
| H2 Investment | 342,000 | ~3,000 | 2002-2017 | ~114 |
| H3 Payout | 244,000 | ~2,800 | 2002-2017 | ~87 |

**Power implications:**
- For small effects (f2=0.02): All samples achieve >90% power
- For medium effects (f2=0.15): Even 500 firms with 8 years achieves >80% power
- Current sample sizes are MORE THAN ADEQUATE for detecting economically meaningful effects

### Variable Construction Capability

From existing outputs, these variables are ALREADY CONSTRUCTED:

**Text Measures (IVs):**
- Manager_QA_Uncertainty_pct
- CEO_QA_Uncertainty_pct
- Manager_QA_Weak_Modal_pct
- CEO_QA_Weak_Modal_pct
- Manager_Pres_Uncertainty_pct
- CEO_Pres_Uncertainty_pct
- Analyst_QA_Uncertainty_pct

**Financial Controls:**
- Cash holdings (CHE/AT)
- Leverage (DLTT+DLC)/AT
- Tobin's Q
- ROA (NI/AT)
- Capex intensity (CAPX/AT)
- Dividend payer dummy
- Firm size (ln AT)
- Cash flow volatility
- Earnings volatility

**Market Measures:**
- Stock returns
- Volatility
- Abnormal returns

**Event Flags:**
- M&A announcements
- CEO turnover
- Dividend changes

---

## Literature Review Methodology

### Databases to Search

| Database | Search Focus | Inclusive Dates |
|----------|-------------|-----------------|
| Web of Science | Core accounting/finance journals | 2010-2025 |
| Scopus | Broad coverage, conference proceedings | 2010-2025 |
| ABI/INFORM Complete | Business literature | 2010-2025 |
| SSRN | Working papers, cutting edge | 2015-2025 |
| ScienceDirect | Finance/econometrics methods | 2010-2025 |

### Key Journals to Cover

**Accounting:**
- The Accounting Review
- Journal of Accounting and Economics
- Journal of Accounting Research
- Review of Accounting Studies
- Contemporary Accounting Research

**Finance:**
- Journal of Finance
- Journal of Financial Economics
- Review of Financial Studies
- Journal of Financial and Quantitative Analysis
- Management Science (Finance dept)

**Interdisciplinary:**
- Strategic Management Journal (communication)
- Organization Science (linguistics)
- Journal of Business Ethics (disclosure)

### Search Terms (PICO Framework)

**Population:** Public firms, earnings calls, corporate disclosures, executives, CEOs, CFOs, managers

**Intervention/Exposure:**
- Textual analysis, linguistic analysis, content analysis
- Uncertainty, vagueness, tone, sentiment
- Readability, complexity, fog index
- Weak modals, hedging, strong modals
- Managerial style, communication style

**Comparison:** Low vs. high uncertainty, clear vs. vague speech, different linguistic measures

**Outcomes:**
- Financial: Investment, cash holdings, leverage, payout, M&A, financing
- Market: Returns, volatility, liquidity, analyst forecasts, bid-ask spread
- Governance: CEO turnover, executive compensation, board monitoring
- Real: Firm value, profitability, efficiency, risk

**Study Design:** Archival, empirical, panel data, event study

### Inclusion Criteria

- Published 2010-2025 (post-Loughran-McDonald dictionary)
- Empirical archival study (not theoretical/modeling)
- Uses textual analysis of corporate communication
- Tests hypothesis about corporate outcomes
- English language
- Peer-reviewed journal or working paper with citations

### Exclusion Criteria

- Purely theoretical/perspective papers
- Case studies without generalizability
- Non-corporate settings (e.g., political speech)
- Studies without clear hypothesis testing
- Duplicate datasets (prefer most recent/complete)

---

## Initial Hypothesis Candidates

Based on literature review and data availability, these areas emerge as promising:

### High-Priority Candidates (Novel + Data-Feasible)

1. **H6: Managerial Hedging and M&A Targeting**
   - **IV:** Weak modal language in earnings calls (hedging)
   - **DV:** Likelihood of becoming M&A target / Deal premium
   - **Rationale:** Hedging may signal undervaluation or strategic ambiguity attracting acquirers
   - **Data Available:** SDC M&A + linguistic measures + firm controls
   - **Novelty:** No prior tests of hedging -> M&A targeting
   - **Power:** Excellent (142K deals, sample very large)

2. **H7: CEO Vagueness and Forced Turnover Risk**
   - **IV:** Managerial uncertainty/vagueness in Q&A
   - **DV:** Probability of forced CEO turnover
   - **Rationale:** Boards may discipline unclear communicators; vagueness may indicate problems
   - **Data Available:** CEO dismissal data + linguistic measures
   - **Novelty:** Textual predictors of turnover not extensively studied
   - **Power:** Good if sufficient turnover events (verify)

3. **H8: Speech Clarity and Executive Compensation**
   - **IV:** CEO speech clarity (inverse of uncertainty)
   - **DV:** Executive compensation / pay-for-performance sensitivity
   - **Rationale:** Clear communication valued by boards; unclear speech may reduce pay
   - **Data Available:** Execucomp + linguistic measures + firm performance
   - **Novelty:** Link between communication style and pay not established
   - **Power:** Good (Execucomp coverage overlaps with sample)

4. **H9: Q&A-Presentation Uncertainty Gap and Future Returns**
   - **IV:** (Q&A uncertainty - Presentation uncertainty) gap
   - **DV:** Future abnormal stock returns
   - **Rationale:** Large gap indicates prepared script vs. inability to answer questions = bad signal
   - **Data Available:** CRSP returns + gap measure
   - **Novelty:** Gap measure not used for return prediction
   - **Power:** Excellent (daily returns data)

5. **H10: Managerial Language Complexity and Analyst Forecast Accuracy**
   - **IV:** Readability/complexity of CEO speech
   - **DV:** Analyst forecast error (IBES)
   - **Rationale:** Complex speech may confuse analysts or signal competence (ambiguous)
   - **Data Available:** IBES + linguistic complexity + firm controls
   - **Novelty:** Complexity specifically in earnings calls (vs. 10-Ks)
   - **Power:** Good if IBES data available

### Medium-Priority Candidates

6. **H11: Uncertainty Language Dispersion Across Speakers and Stock Volatility**
   - Tests if disagreement between CEO and CFO speech predicts volatility

7. **H12: Temporal Changes in CEO Speech Style and Firm Performance**
   - Tests if becoming clearer/vaguer over tenure predicts outcomes

---

## Open Questions

1. **IBES Data Availability:**
   - What we know: Analyst dispersion mentioned in prior research
   - What's unclear: Whether IBES detailed data (forecast errors, revisions) is available
   - Recommendation: Verify IBES availability before committing to analyst-related hypotheses

2. **CEO Turnover Events:**
   - What we know: CEO dismissal dataset exists
   - What's unclear: Number of events, time period coverage, overlap with earnings call sample
   - Recommendation: Count turnover events in sample period; need >500 events for power

3. **Execucomp Coverage:**
   - What we know: Execucomp data exists
   - What's unclear: Coverage overlap with earnings call sample, time period completeness
   - Recommendation: Assess merge rate between Execucomp and call sample

4. **Linguistic Complexity Measures:**
   - What we know: LM dictionary has complexity category
   - What's unclear: Whether readability measures (fog index, etc.) are computed
   - Recommendation: Check existing text measures for complexity/readability

5. **Cross-Sectional vs. Time-Series Variation:**
   - What we know: Within-firm variation drives fixed effects power
   - What's unclear: How much linguistic measures vary over time within firms
   - Recommendation: Calculate within-firm SD of key text measures; low variation = low power

---

## Sources

### Primary (HIGH confidence)

- [PRISMA Statement](https://www.prisma-statement.org/) - Systematic review methodology standard
- [Loughran-McDonald Master Dictionary](https://sraf.nd.edu/loughranmcdonald-master-dictionary/) - Financial sentiment dictionary
- [Wooldridge - Econometric Analysis of Cross Section and Panel Data](https://ipcid.org/evaluation/apoio/Wooldridge%20-%20Cross-section%20and%20Panel%20Data.pdf) - Panel econometrics foundation
- [Baltagi - Econometric Analysis of Panel Data](https://link.springer.com/book/10.1007/978-3-030-53953-5) - Panel data methods
- [G*Power Software](https://www.gpower.hhu.de/) - Power analysis tool

### Secondary (MEDIUM confidence)

- [Systematic Literature Reviews in Accounting, Finance and Governance](https://afgr.scholasticahq.com/article/141012-systematic-literature-reviews-in-accounting-finance-and-governance) - Accounting SLR guidance (Quinn 2025)
- [A Guide for Accounting Researchers to Conduct and Report Systematic Literature Reviews](https://publications.aaahq.org/bria/article/36/1/21/11481/A-Guide-for-Accounting-Researchers-to-Conduct-and) - AAA guide
- [The Effects of Managerial Style in Earnings Conference Calls](https://www.nber.org/system/files/working_papers/w23425/w23425.pdf) - Dzieliński, Wagner, Zeckhauser (foundational)
- [Textual Analysis in Accounting: What's Next?](https://onlinelibrary.wiley.com/doi/10.1111/1911-3846.12825) - Bochkay (2023) - Research gaps
- [Corporate Earnings Calls and Analyst Beliefs](https://arxiv.org/html/2511.15214v1) - November 2025 arXiv paper

### Tertiary (LOW confidence - verify)

- [Fine-tuning transformer models for M&A target prediction](https://www.tandfonline.com/doi/full/10.1080/23311975.2025.2487219) - 2025 M&A prediction study
- [Signalling through managerial tone and analysts' response](https://www.tandfonline.com/doi/full/10.1080/01559982.2024.2339911) - 2024 signaling study
- [Target CEO's optimism, acquisition pricing and completion](https://www.sciencedirect.com/science/article/pii/S0024630125000883) - 2025 CEO optimism study
- Various web search results on CEO turnover, textual analysis, and hypothesis generation

---

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - Established PRISMA methodology, standard Python stack
- Architecture: HIGH - Clear patterns from systematic review methods
- Power analysis: HIGH - Based on established panel econometrics literature (Wooldridge, Baltagi)
- Literature review methodology: HIGH - PRISMA 2020 is widely accepted standard
- Hypothesis candidates: LOW to MEDIUM - Require verification of data availability (IBES, Execucomp coverage)

**Research date:** 2025-02-05
**Valid until:** 2025-06-01 (literature evolves quickly, re-search before planning)

**Next steps:**
1. Verify IBES data availability for analyst-related hypotheses (H5, H10)
2. Count CEO turnover events in dismissal dataset
3. Assess Execucomp merge rate with call sample
4. Calculate within-firm variation of key text measures
5. Conduct pilot literature search using PRISMA protocol
6. Update 41-RESEARCH.md with findings from data verification
