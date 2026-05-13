# Variables YAML repair scout report

**Generated:** scout_variables_yaml.py | specs=37 modules=84 yaml_cols=96 extra_vars=1

## Top-line gap
- **Canonical var set:** 88 (specs+extra_vars)
- **In current YAML (by column):** 96
- **MISSING (in spec/extra, not in YAML):** 0
- **DEAD (in YAML, not in any spec/extra):** 8
- **In both (need metadata fill check):** 88

## Missing — by category

## DEAD entries (in YAML, no spec/extra reference)
Manual review needed — may be archived suites or planned future work.
- `EquityDelayCon` (entry_name=`equity_delay_con`, ref=`hm2015`)
- `ceo_id` (entry_name=`manifest`, ref=`?`)
- `ceo_name` (entry_name=`manifest`, ref=`?`)
- `ff12_code` (entry_name=`manifest`, ref=`?`)
- `ff12_name` (entry_name=`manifest`, ref=`?`)
- `file_name` (entry_name=`manifest`, ref=`?`)
- `gvkey` (entry_name=`manifest`, ref=`?`)
- `start_date` (entry_name=`manifest`, ref=`?`)

## Incomplete metadata (in YAML, fields missing)

### Missing `suites` (1)
- `TotalSimilarity` (entry: `total_similarity`)

## Module docstring quality (78 modules)
- **with line-1 docstring:** 84 (100%)
- no docstring: 0
- parse fail: 0

### Sample line-1 docstrings (first 10)
- `_clarity_residual_engine.py`: Private engine to load clarity residuals from CEO Clarity Extended Stage 4 output.
- `_compustat_engine.py`: Private Compustat compute engine.
- `_crsp_engine.py`: Private CRSP compute engine.
- `_hassan_engine.py`: Private Hassan Political Risk (PRisk) compute engine.
- `_ibes_detail_engine.py`: Singleton engine for loading and caching IBES Detail data (individual analyst estimates).
- `_ibes_engine.py`: Singleton engine for loading and caching IBES Analyst Forecast data.
- `_linguistic_engine.py`: Private Linguistic compute engine.
- `amihud_change.py`: Builder for Amihud illiquidity change around earnings calls (H7).
- `amihud_illiq.py`: Builder for Amihud Illiquidity (amihud_illiq) variable.
- `analyst_qa_negative.py`: Builder for Analyst Q&A Negative Sentiment variable.

## Metadata dict extraction coverage
- modules with `source` in VariableResult metadata: 74
- modules with `column` in metadata: 43
- modules with `reference` in metadata: 4

→ If `with_column` close to 78, the metadata walker is reliable for var↔module
  mapping. If sparse, need fallback (e.g., engine COLS scan).

## Decision points (post-scout)
1. AST metadata walker needed? → check `with_source` / `with_column` above.
2. Splice strategy → depends on diff size (missing+dead+incomplete).
3. Speech IV count → confirms hand-stub list size.
4. Lead/lag derivative count → confirms naming-rule scope.