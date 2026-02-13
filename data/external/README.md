# External Reference Data

**This directory contains third-party reference data. Do not modify external data files.**

This directory follows the Cookiecutter Data Science convention for external data storage.
Files here are reference data from third-party sources.

---

## Purpose

- Store reference data from external sources
- Provide lookup tables and mappings
- Document provenance and versions

## Current External Data

| Directory | Source | Description |
|-----------|--------|-------------|
| `ff_factors/` | Kenneth French Data Library | Fama-French factor returns |
| `gvkey_cik/` | Compustat/CRSP | GVKEY to CIK mappings |
| `sic_codes/` | SEC | SIC code definitions |

## Mutability Rules

| Rule | Description |
|------|-------------|
| DO NOT modify | External data should remain as received |
| Document source | Include README in each subdirectory |
| Track version | Note data version and download date |
| License aware | Respect data licensing terms |

## Adding External Data

When adding external reference data:

1. Create subdirectory with descriptive name
2. Include README.md documenting:
   - Data source and URL
   - Download date
   - Version information
   - License/terms of use
3. Keep data in original format when possible

---

**Last Updated:** 2026-02-13
