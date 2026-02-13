# Processed Data (Source of Truth)

**This directory contains FINAL cleaned datasets used for analysis. Changes require documentation.**

This directory follows the Cookiecutter Data Science convention for processed data storage.
Files here are the authoritative source for all analyses.

---

## Purpose

- Store final, cleaned, validated datasets
- Provide single source of truth for analysis
- Enable reproducible research

## Quality Requirements

All files in this directory MUST:

1. Be validated against source data
2. Have accompanying documentation
3. Use dated subdirectories for versioning
4. Pass quality checks (completeness, consistency)

## Directory Convention

```
data/processed/
├── manifest/
│   ├── 2024-01-20/
│   │   ├── manifest_final.parquet
│   │   ├── manifest_summary.yaml
│   │   └── VALIDATION.md
│   └── 2024-01-25/
│       └── ...
├── uncertainty/
│   └── 2024-01-22/
│       └── ceo_uncertainty.parquet
└── variables/
    └── 2024-01-24/
        └── financial_variables.parquet
```

## Mutability Rules

| Rule | Description |
|------|-------------|
| DOCUMENT changes | All modifications must be logged |
| VERSION updates | Use dated subdirectories |
| VALIDATE before commit | Run validation checks |
| REVIEW significant changes | Changes affect downstream analysis |

## Subdirectories

| Directory | Description | Primary Consumers |
|-----------|-------------|-------------------|
| `manifest/` | Final analyst-CEO manifest | All stages |
| `uncertainty/` | CEO uncertainty measures | Econometric stage |
| `variables/` | Financial/econometric variables | Econometric stage |

## Validation Requirements

Each processed dataset should include:

1. **Data file:** `.parquet` format (preferred)
2. **Summary statistics:** `.yaml` with row counts, column counts, date ranges
3. **Validation report:** `VALIDATION.md` documenting checks passed

---

**Last Updated:** 2026-02-13
