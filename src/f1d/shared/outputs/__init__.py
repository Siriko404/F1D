"""Output utilities for Stage 3/4 pipeline runs.

Provides:
- manifest_generator: Generate run_manifest.json for reproducibility
- attrition_table: Generate sample_attrition tables for paper submission
- suite_spec: Canonical per-suite metadata for LaTeX table rendering
"""

from .manifest_generator import generate_manifest
from .attrition_table import generate_attrition_table
from .suite_spec import (
    extract_coefs_logit,
    extract_coefs_panelols,
    load_suite_spec,
    write_suite_spec,
)
from .suite_spec_schema import SuiteSpec

__all__ = [
    "SuiteSpec",
    "extract_coefs_logit",
    "extract_coefs_panelols",
    "generate_attrition_table",
    "generate_manifest",
    "load_suite_spec",
    "write_suite_spec",
]
