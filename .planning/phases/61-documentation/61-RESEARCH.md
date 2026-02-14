# Phase 61: Documentation - Research

**Researched:** 2026-02-11
**Domain:** Python project documentation, docstrings, API reference generation
**Confidence:** MEDIUM

## Summary

Phase 61 involves creating comprehensive documentation for the F1D (Financial Clarity) codebase, a PhD thesis project on managerial speech uncertainty and corporate financial policies. The project has just completed Phase 60 (Code Organization) which included:
- Archiving legacy files
- Creating READMEs for 6 directories
- Reorganizing observability package into 7 modules
- Ruff linting and formatting (830 issues fixed)
- Type checking with mypy (221 type errors documented) and dead code detection

**Key findings:**
1. **Sphinx** is the standard for academic/research Python projects due to LaTeX support and multi-format output
2. **NumPy-style docstrings** are preferred for scientific computing projects
3. **mkdocs-material** is a modern alternative with better aesthetics but less academic adoption
4. **pdoc** provides zero-config API docs but limited for comprehensive documentation
5. The codebase has good module-level documentation but inconsistent function docstrings

**Primary recommendation:** Use Sphinx with NumPy-style docstrings for API documentation, leveraging existing module headers and contract patterns. Keep README.md for user-facing documentation.

## User Constraints (from CONTEXT.md)

**IMPORTANT:** No CONTEXT.md exists for this phase. All areas are at Claude's discretion for research and recommendations.

### Project Context
- **Type:** PhD thesis research project on managerial speech uncertainty
- **Requirements:** Reproducibility is non-negotiable (bitwise-identical outputs)
- **Documentation goals:** Support future research, thesis writing, publication
- **Codebase:** Python for data processing and econometric analysis
- **Recent completion:** Phase 60 code organization (linting, type checking baseline)

## Standard Stack

### Core Documentation Tools

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **Sphinx** | 7.x+ | API documentation generator | Industry standard for Python; supports LaTeX/PDF output |
| **sphinx-autodoc-typehints** | 2.x | Type hints in docs | Integrates mypy type hints into documentation |
| **myst-parser** | 2.x+ | Markdown support in Sphinx | Allows Markdown alongside reStructuredText |
| **sphinx-rtd-theme** | 1.x | Documentation theme | ReadTheDocs standard, clean appearance |
| **numpydoc** | 1.x+ | NumPy-style docstring parser | Preferred for scientific computing projects |

### Alternative: MkDocs Stack

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **MkDocs** | 1.5+ | Static site generator | Prefer Markdown, want faster builds |
| **mkdocs-material** | 9.x+ | Modern theme | Want beautiful out-of-box styling |
| **mkdocstrings** | 0.24+ | API doc generation | Automatic docstring extraction |

### Lightweight Alternative

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **pdoc** | 14+ | API-only docs | Quick API reference, no manual content needed |

### Installation

**For Sphinx (recommended for academic research):**
```bash
pip install sphinx sphinx-autodoc-typehints myst-parser sphinx-rtd-theme numpydoc
```

**For MkDocs (modern alternative):**
```bash
pip install mkdocs mkdocs-material mkdocstrings
```

**For pdoc (lightweight):**
```bash
pip install pdoc
```

## Architecture Patterns

### Recommended Documentation Structure

```
docs/
├── source/
│   ├── index.rst           # Landing page
│   ├── api/                # API reference
│   │   ├── module1.rst
│   │   ├── module2.rst
│   │   └── shared.rst      # Shared utilities
│   ├── user_guide/         # How-to guides
│   │   ├── pipeline.rst
│   │   ├── reproducibility.rst
│   │   └── extending.rst
│   ├── development/        # Developer docs
│   │   ├── testing.rst
│   │   ├── contributing.rst
│   │   └── architecture.rst
│   └── _static/            # Custom assets
├── build/                  # Generated output (gitignored)
└── Makefile                # Build commands
```

### Pattern 1: Sphinx with autodoc (Recommended)

**What:** Automatically generate API documentation from docstrings.

**When to use:**
- Large codebase with many modules
- Need for API reference that stays in sync with code
- Academic projects requiring LaTeX/PDF output

**Example:**
```rst
.. _api-ref:

API Reference
=============

.. automodule:: shared.panel_ols
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: shared.iv_regression
    :members:
    :undoc-members:
```

**Source:** [Sphinx autodoc documentation](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)

### Pattern 2: NumPy-style Docstrings (Scientific Standard)

**What:** Structured docstring format used by NumPy, SciPy, scikit-learn.

**When to use:**
- Scientific computing projects
- Functions with many parameters
- Need for detailed parameter/return documentation

**Example:**
```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    entity_col: str = "gvkey",
    time_col: str = "year",
    cluster_col: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run panel OLS regression with fixed effects.

    Estimates a panel regression model using linearmodels.PanelOLS
    with entity and time fixed effects. Supports clustered standard
    errors and comprehensive diagnostics.

    Parameters
    ----------
    df : pd.DataFrame
        Panel data with entity and time identifiers.
    dependent : str
        Name of dependent variable column.
    exog : List[str]
        Names of independent/exogenous variable columns.
    entity_col : str, default "gvkey"
        Column name for entity identifier.
    time_col : str, default "year"
        Column name for time period.
    cluster_col : str, optional
        Column to cluster standard errors.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - model: Fitted PanelOLS object
        - coefficients: DataFrame with beta, SE, t-stat, p-value
        - summary: dict with R2, adj_R2, N, F-stat
        - diagnostics: dict with VIF, condition number
        - warnings: list of warning messages

    Raises
    ------
    CollinearityError
        If perfect collinearity detected.
    MulticollinearityError
        If VIF threshold exceeded.

    Examples
    --------
    >>> result = run_panel_ols(
    ...     df=data,
    ...     dependent="returns",
    ...     exog=["size", "leverage"],
    ...     cluster_col="gvkey"
    ... )
    >>> print(result["summary"]["r2"])

    Notes
    -----
    Fixed effects are absorbed using the linearmodels package.
    The function requires linearmodels to be installed.

    See Also
    --------
    iv_regression.twosls : Instrumental variables regression
    shared.regression_utils : OLS regression utilities

    References
    ----------
    .. [1] Cameron, A. C., & Miller, D. L. (2015). A practitioner's
       guide to cluster-robust inference.
    """
    # Implementation...
```

### Pattern 3: Existing Contract Headers

**What:** The project already uses a standardized contract header format.

**When to preserve:** Maintain existing pattern for consistency.

**Example:**
```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Panel OLS with Fixed Effects
================================================================================
ID: shared/panel_ols
Description: Panel OLS regression with firm + year + industry fixed effects

Purpose: Phases 33-35 (H1/H2/H3 Regressions) need standardized panel regression
         infrastructure with proper fixed effects, interaction terms, and
         multicollinearity diagnostics.

Inputs:
    - pandas DataFrame with panel data
    - linearmodels.PanelOLS for fixed effects estimation

Outputs:
    - Fitted PanelOLS model with coefficients and standard errors
    - Summary statistics (R2, N, F-stat, fixed effects used)

Deterministic: true
================================================================================
"""
```

### Anti-Patterns to Avoid

- **Out-of-sync docs:** API documentation that doesn't match code (use autodoc)
- **Hand-written API docs:** Manual duplication of docstring content
- **Only docstrings, no narrative:** Users need guides, not just API reference
- **Inline comments as docs:** Docstrings should be primary documentation source
- **Over-documenting legacy code:** Don't document code that will be removed

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| API reference | Manual HTML/Markdown | Sphinx autodoc | Stays in sync with code |
| Docstring parsing | Custom regex | numpydoc parser | Handles all edge cases |
| Type hints in docs | Manual formatting | sphinx-autodoc-typehints | Automatic from mypy |
| Navigation | Manual links | Sphinx toctree | Auto-generated |
| Code highlighting | Custom CSS | Pygments | Language-aware highlighting |

**Key insight:** Documentation maintenance overhead grows with codebase size. Automation through autodoc keeps docs synchronized without manual updates.

## Common Pitfalls

### Pitfall 1: Docstring Style Inconsistency

**What goes wrong:** Mix of Google, NumPy, and reST styles across modules.

**Why it happens:** Different developers, copied code, evolving standards.

**How to avoid:**
1. Choose ONE style (NumPy recommended for this project)
2. Configure Sphinx with numpydoc extension
3. Add linting rule for docstring format

**Warning signs:** Visual inconsistency in generated docs, parser errors.

### Pitfall 2: Missing or Useless Docstrings

**What goes wrong:** Functions without docstrings or docstrings that just repeat the function name.

**Why it happens:** "I'll add docs later" mentality, focus on implementation.

**How to avoid:**
1. Write docstrings when writing functions
2. Use docstring coverage tool (e.g., interrogate)
3. Make docstring-first development part of workflow

**Warning signs:** Generated docs with empty sections, "TODO" in docstrings.

### Pitfall 3: Over-Engineering Documentation

**What goes wrong:** Complex build system, custom themes, excessive content.

**Why it happens:** Treating docs as a separate project instead of supporting code.

**How to avoid:**
1. Start simple (Sphinx with rtd-theme)
2. Use standard configurations
3. Focus on API reference first, add guides incrementally

**Warning signs:** Build times >5 minutes, custom theme maintenance burden.

### Pitfall 4: Documentation Builds Fail

**What goes wrong:** CI breaks due to doc build failures, type errors in docs.

**Why it happens:** Docs imported but not tested, type hints missing.

**How to avoid:**
1. Test doc builds in CI
2. Use `autodoc-process-docstring` for validation
3. Keep type hints updated

**Warning signs:** Docs not updated with code, broken links.

## Code Examples

### Sphinx Configuration (conf.py)

```python
# docs/source/conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('../../2_Scripts'))

project = 'F1D Data Processing Pipeline'
copyright = '2026, Thesis Author'
author = 'Thesis Author'

extensions = [
    'sphinx.ext.autodoc',           # Core autodoc
    'sphinx.ext.napoleon',           # NumPy/Google style support
    'sphinx.ext.autosummary',        # Auto summaries
    'sphinx.ext.viewcode',           # Source links
    'sphinx.ext.intersphinx',        # Cross-project links
    'myst_parser',                   # Markdown support
    'sphinx_autodoc_typehints',      # Type hints
]

# Napoleon settings (NumPy style)
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Type hints settings
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True

# Intersphinx mapping (external links)
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

# HTML theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
```

### Makefile for Documentation

```makefile
# docs/Makefile
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

help:
	@echo "Please use 'make <target>' where <target> is one of..."
	@echo "  html       to make standalone HTML files"
	@echo "  pdf        to make LaTeX files and PDF"
	@echo "  livehtml   to run auto-reloading server"

html:
	@$(SPHINXBUILD) -b html $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

pdf:
	@$(SPHINXBUILD) -b latex $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/latex
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/latex all-pdf
	@echo "PDF finished: $(BUILDDIR)/latex/*.pdf"

livehtml:
	sphinx-autobuild $(SOURCEDIR) $(BUILDDIR)/html
```

### NumPy Docstring Template

```python
def function_name(
    param1: type,
    param2: type,
    optional_param: type = default,
) -> return_type:
    """
    Brief one-line description.

    Extended description spanning multiple lines if needed.
    Explain the function's purpose, algorithm, or important notes.

    Parameters
    ----------
    param1 : type
        Description of param1.
    param2 : type
        Description of param2.
    optional_param : type, default=default
        Description of optional parameter.

    Returns
    -------
    return_type
        Description of return value.

    Raises
    ------
    ExceptionType
        Description of when this exception is raised.

    See Also
    --------
    related_function : Description of relation.

    Examples
    --------
    >>> result = function_name(arg1, arg2)
    >>> print(result)
    expected_output

    Notes
    -----
    Additional implementation notes or algorithm references.

    References
    ----------
    .. [1] Author, A. (Year). Title. Journal.
    """
```

### MkDocs Configuration (Alternative)

```yaml
# docs/mkdocs.yml
site_name: F1D Data Processing Pipeline
site_description: Research data processing pipeline for empirical finance
theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [../2_Scripts]
          options:
            docstring_style: numpy
            show_root_heading: true

nav:
  - Home: index.md
  - API Reference:
    - Shared Utilities: api/shared.md
    - Observability: api/observability.md
  - User Guide:
    - Pipeline Overview: guide/pipeline.md
    - Reproducibility: guide/reproducibility.md
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hand-written HTML | Sphinx autodoc | 2010s | Auto-sync with code |
| reST only | Markdown support (MyST) | 2020 | Wider author accessibility |
| Google style | NumPy style dominant in science | Ongoing | Scientific Python standard |
| Static docs only | Live-reload tools | 2020+ | Faster iteration |

**Current best practices (2025-2026):**
- NumPy-style docstrings for scientific code
- Sphinx with MyST parser for Markdown + reST
- Type hints automatically included in docs
- GitHub Actions auto-deployment to GitHub Pages

## Open Questions

1. **Docstring migration scope**
   - What we know: 221 type errors documented, 17 dead code candidates
   - What's unclear: How many functions currently have NO docstrings
   - Recommendation: Run docstring coverage tool (e.g., interrogate) to assess

2. **LaTeX/PDF requirements**
   - What we know: This is a PhD thesis project
   - What's unclear: Are PDF docs needed for thesis submission?
   - Recommendation: Confirm if Sphinx PDF output is required

3. **Documentation hosting**
   - What we know: Project is in git repo
   - What's unclear: Should docs be public (GitHub Pages) or private?
   - Recommendation: Depends on thesis publication status

4. **Legacy code documentation**
   - What we know: .___archive/ contains legacy code
   - What's unclear: Should archived code be documented?
   - Recommendation: Skip archived code documentation

## Sources

### Primary (HIGH confidence)
- [Sphinx Documentation](https://www.sphinx-doc.org/en/master/) - Core autodoc, configuration
- [Sphinx autodoc extension](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) - Auto API generation
- [Napoleon extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) - NumPy/Google style support
- [NumPydoc Validation](https://numpydoc.readthedocs.io/en/latest/) - Docstring validation

### Secondary (MEDIUM confidence)
- [Build Your Python Project Documentation With MkDocs - Real Python](https://realpython.com/python-project-documentation-with-mkdocs/) - MkDocs tutorial
- [Effective Docstrings: Google vs. NumPy vs. reStructuredText Styles](https://mcginniscommawill.com/posts/2025-03-06-writing-effective-docstrings/) - Style comparison (March 2025)
- [Switching From Sphinx to MkDocs Documentation - Towards Data Science](https://towardsdatascience.com/switching-from-sphinx-to-mkdocs-documentation-what-did-i-gain-and-lose-04080338ad38/) - Tool comparison (Feb 2024)
- [MkDocs vs Sphinx - PythonBiellaGroup](https://pythonbiellagroup.it/en/learning/mkdocs_tutorial/mkdocs_vs_sphinx/) - Feature comparison
- [Python Documentation Best Practices: A Comprehensive Guide](https://www.docuwriter.ai/posts/python-documentation-best-practices-guide) - Best practices overview

### Tertiary (LOW confidence)
- [10 Python-Powered Ways to Document Your Project](https://medium.com/@connect.hashblock/10-python-powered-ways-to-document-your-project-c0608f5a5f8f) (Sep 2025) - Modern approaches

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Sphinx is well-established, versions current
- Architecture: MEDIUM - Sphinx conf.py well-documented, but project-specific needs unclear
- Pitfalls: MEDIUM - Based on general documentation experience, not project-specific

**Research date:** 2026-02-11
**Valid until:** 90 days (documentation tools evolve slowly, but Sphinx 8.x may introduce changes)
