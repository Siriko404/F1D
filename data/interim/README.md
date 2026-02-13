# Intermediate Processing Data

**This directory contains regenerable intermediate files. Files here CAN be deleted and regenerated.**

This directory follows the Cookiecutter Data Science convention for interim data storage.
Files here are intermediate products of the data processing pipeline.

---

## Purpose

- Store intermediate processing outputs between pipeline stages
- Enable restart from any stage without re-running from beginning
- Provide debugging visibility into transformation steps

## Directory Convention

Use dated subdirectories to version intermediate outputs:

```
data/interim/
├── sample/
│   ├── 2024-01-15/
│   │   ├── step1_initial_filter.parquet
│   │   └── step2_ceo_match.parquet
│   └── 2024-01-20/
│       └── ...
├── text/
│   └── 2024-01-16/
│       └── tokenized_transcripts.parquet
└── financial/
    └── 2024-01-17/
        └── merged_financial.parquet
```

## Mutability Rules

| Rule | Description |
|------|-------------|
| CAN delete | Files here are regenerable from `data/raw/` |
| CAN overwrite | New runs replace old outputs |
| Version by date | Use YYYY-MM-DD subdirectories |
| Not source of truth | Final data goes to `data/processed/` |

## Storage Management

Since interim files can be regenerated:

- Periodically clean up old dated directories
- Keep only recent versions (last 2-3 runs)
- Do NOT track interim files in git (gitignored)

## Subdirectories

| Directory | Stage | Description |
|-----------|-------|-------------|
| `sample/` | Stage 1 | Sample construction intermediates |
| `text/` | Stage 2 | Text processing intermediates |
| `financial/` | Stage 3 | Financial variable intermediates |
| `econometric/` | Stage 4 | Analysis intermediates |

---

**Last Updated:** 2026-02-13
