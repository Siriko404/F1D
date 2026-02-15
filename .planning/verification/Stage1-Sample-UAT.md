---
status: testing
phase: Stage1-Sample
source: 2_Scripts/1_Sample/*.py
started: 2026-02-15T00:00:00Z
updated: 2026-02-15T00:00:00Z
---

## Current Test

number: 2
name: Run 1.1_CleanMetadata.py
expected: |
  Script executes successfully and creates:
  - 4_Outputs/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet
  - 4_Outputs/1.1_CleanMetadata/{timestamp}/variable_reference.csv
  - 4_Outputs/1.1_CleanMetadata/{timestamp}/report_step_1_1.md
  - 3_Logs/1.1_CleanMetadata/{timestamp}.log
awaiting: user response

## Tests

### 1. Verify Input Data Availability
expected: |
  Required input files exist and are accessible:
  - 1_Inputs/Earnings_Calls_Transcripts/Unified-info.parquet (main metadata source)
  - 1_Inputs/Execucomp/comp_execucomp.parquet (CEO data)
  - 1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet (firm linking)
  - 1_Inputs/FF1248/Siccodes12.zip, Siccodes48.zip (industry codes)
result: pass

### 2. Run 1.1_CleanMetadata.py
expected: |
  Script executes successfully and creates:
  - 4_Outputs/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet
  - 4_Outputs/1.1_CleanMetadata/{timestamp}/variable_reference.csv
  - 4_Outputs/1.1_CleanMetadata/{timestamp}/report_step_1_1.md
  - 3_Logs/1.1_CleanMetadata/{timestamp}.log

  Output parquet contains cleaned earnings call metadata (event_type='1') from 2002-2018.
result: [pending]

### 3. Verify 1.1_CleanMetadata Output Structure
expected: |
  metadata_cleaned.parquet has required columns:
  - file_name: Unique identifier for each transcript
  - event_type: Should all be '1' (earnings calls only)
  - call_date: Date of earnings call
  - company_name: Company name from transcript

  Data quality checks:
  - No duplicate file_name values
  - call_date range: 2002-01-01 to 2018-12-31
  - No null values in file_name, event_type, call_date
result: [pending]

### 4. Run 1.2_LinkEntities.py
expected: |
  Script executes successfully and creates:
  - 4_Outputs/1.2_LinkEntities/{timestamp}/metadata_linked.parquet
  - 4_Outputs/1.2_LinkEntities/{timestamp}/variable_reference.csv
  - 4_Outputs/1.2_LinkEntities/{timestamp}/report_step_1_2.md
  - 3_Logs/1.2_LinkEntities/{timestamp}.log

  Output contains linked firm identifiers (gvkey, cusip, permno).
result: [pending]

### 5. Verify 1.2_LinkEntities Output Structure
expected: |
  metadata_linked.parquet has additional columns from CCM linking:
  - gvkey: Compustat firm identifier
  - cusip: CUSIP identifier
  - permno: CRSP permno
  - sic: SIC industry code
  - ff12/ff48: Fama-French industry codes

  Data quality checks:
  - Link rate (gvkey not null): > 80% of records
  - No duplicate (gvkey, call_date) pairs for same CEO
  - All gvkey values are valid Compustat identifiers
result: [pending]

### 6. Run 1.3_BuildTenureMap.py
expected: |
  Script executes successfully and creates:
  - 4_Outputs/1.3_BuildTenureMap/{timestamp}/tenure_map.parquet
  - 4_Outputs/1.3_BuildTenureMap/{timestamp}/variable_reference.csv
  - 4_Outputs/1.3_BuildTenureMap/{timestamp}/report_step_1_3.md
  - 3_Logs/1.3_BuildTenureMap/{timestamp}.log

  Output contains CEO tenure information.
result: [pending]

### 7. Verify 1.3_BuildTenureMap Output Structure
expected: |
  tenure_map.parquet has CEO tenure columns:
  - ceo_id: Unique CEO identifier
  - ceo_name: CEO name
  - gvkey: Firm identifier
  - start_date: CEO tenure start date
  - end_date: CEO tenure end date (or NaT if current)
  - tenure_years: Calculated tenure in years

  Data quality checks:
  - start_date <= end_date for all non-null end_dates
  - tenure_years = (end_date - start_date) / 365.25
  - No duplicate (ceo_id, gvkey) pairs
result: [pending]

### 8. Run 1.4_AssembleManifest.py
expected: |
  Script executes successfully and creates:
  - 4_Outputs/1.4_AssembleManifest/{timestamp}/sample_manifest.parquet
  - 4_Outputs/1.4_AssembleManifest/{timestamp}/variable_reference.csv
  - 4_Outputs/1.4_AssembleManifest/{timestamp}/report_step_1_4.md
  - 3_Logs/1.4_AssembleManifest/{timestamp}.log

  Output is the final sample manifest merging all previous outputs.
result: [pending]

### 9. Verify 1.4_AssembleManifest Output Structure
expected: |
  sample_manifest.parquet is the final master sample with columns:
  - gvkey, cusip, permno: Firm identifiers
  - ceo_id, ceo_name: CEO identifiers
  - fyear, fyrq, datadate: Fiscal year info
  - n_calls: Number of earnings calls
  - start_date, end_date, tenure_years: CEO tenure

  Data quality checks:
  - No null values in gvkey, ceo_id, fyear
  - No duplicate (gvkey, fyear, ceo_id) triples
  - Total rows ~100,000+ (based on ~112,000 calls described in README)
result: [pending]

### 10. Verify Sample Manifest Statistics
expected: |
  Sample manifest statistics match README expectations:
  - Total unique firms: ~1,500
  - Total unique CEOs: ~500
  - Year range: 2002-2018 (17 years)
  - Total observations: ~100,000+

  Distribution checks:
  - No SIC codes in 6000-6999 (financial sector excluded)
  - No SIC codes in 4900-4999 (utilities excluded)
result: [pending]

## Summary

total: 10
passed: 1
issues: 0
pending: 9
skipped: 0

## Gaps

[none yet]
