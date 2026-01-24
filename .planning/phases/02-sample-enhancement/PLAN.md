---
phase: 02-sample-enhancement
plan: 01
type: execute
wave: 1
depends_on: ["01-template-pilot"]
files_modified: ["2_Scripts/1.4_AssembleManifest.py"]
autonomous: true

must_haves:
  truths:
    - "stats.json contains industry_distribution section with ff12_code counts"
    - "stats.json contains time_distribution section with yearly counts"
    - "stats.json contains unique_firm_count field with integer value"
    - "All new stats validate successfully"
    - "Console output displays new statistics"
    - "Enhancements maintain existing functionality"
  artifacts:
    - path: "4_Outputs/1.4_AssembleManifest/latest/stats.json"
      provides: "Enhanced manifest with industry, time, and firm stats"
  key_links:
    - from: "stats.json"
      to: "SAMP-04, SAMP-05, SAMP-06"
      via: "new stats sections"
      pattern: "industry_distribution|time_distribution|unique_firm_count"
---

<objective>
Add SAMP-04, SAMP-05, SAMP-06 requirements to Step 1.4 manifest assembly script.

Purpose: Enhance the final manifest script to provide sample construction analytics including industry breakdown (Fama-French 12 sectors), temporal distribution, and unique firm count.

Output: Enhanced 1.4_AssembleManifest.py with new statistics in stats.json and console display.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-template-pilot/01-03-SUMMARY.md
@.planning/requirements/SAMPLE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add industry distribution statistics (SAMP-04)</name>
  <files>2_Scripts/1.4_AssembleManifest.py</files>
  <action>
Enhance the stats calculation section to include industry distribution:

1. **Add industry distribution calculation:**
```python
# After existing stats calculations
industry_dist = df['ff12_code'].value_counts().sort_index().to_dict()
stats['sample']['industry_distribution'] = {
    'ff12_code': industry_dist,
    'total_sectors': len(industry_dist)
}
```

2. **Add to console display:**
```python
# In the summary table section, add:
print(f"Industry Sectors: {len(industry_dist)}")
print(f"\nIndustry Distribution:")
for code, count in sorted(industry_dist.items()):
    pct = (count / len(df)) * 100
    print(f"  {code}: {count:,} ({pct:.1f}%)")
```

3. **Validate ff12_code column exists:**
```python
assert 'ff12_code' in df.columns, "ff12_code column required for SAMP-04"
```
  </action>
  <verify>
industry_distribution section exists in stats.json with ff12_code counts and total_sectors field.
  </verify>
  <done>
Industry distribution by Fama-French 12 sectors calculated and stored.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add time distribution statistics (SAMP-05)</name>
  <files>2_Scripts/1.4_AssembleManifest.py</files>
  <action>
Enhance the stats calculation section to include temporal distribution:

1. **Extract year and calculate distribution:**
```python
# Identify date column (could be call_date, date, etc.)
date_col = None
for col in ['call_date', 'date', 'call_date_dt']:
    if col in df.columns:
        date_col = col
        break

if date_col and pd.api.types.is_datetime64_any_dtype(df[date_col]):
    df['year'] = df[date_col].dt.year
    time_dist = df['year'].value_counts().sort_index().to_dict()
    stats['sample']['time_distribution'] = {
        'year': time_dist,
        'min_year': int(df['year'].min()),
        'max_year': int(df['year'].max()),
        'total_years': len(time_dist)
    }
```

2. **Add to console display:**
```python
print(f"\nTime Distribution:")
print(f"  Year Range: {df['year'].min()} - {df['year'].max()} ({len(time_dist)} years)")
for year, count in sorted(time_dist.items()):
    print(f"  {year}: {count:,}")
```

3. **Handle missing date column:**
```python
if date_col is None:
    stats['sample']['time_distribution'] = {
        'error': 'No date column found for time distribution'
    }
```
  </action>
  <verify>
time_distribution section exists in stats.json with yearly counts, min_year, max_year, total_years.
  </verify>
  <done>
Time distribution by year calculated and stored.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add unique firm count statistics (SAMP-06)</name>
  <files>2_Scripts/1.4_AssembleManifest.py</files>
  <action>
Enhance the stats calculation section to include unique firm count:

1. **Calculate unique firms:**
```python
# Identify GVKEY or equivalent firm identifier
firm_col = None
for col in ['gvkey', 'GVKEY', 'firm_id', 'company_id']:
    if col in df.columns:
        firm_col = col
        break

if firm_col:
    unique_firms = df[firm_col].nunique()
    stats['sample']['unique_firm_count'] = {
        'count': int(unique_firms),
        'column_used': firm_col
    }
else:
    stats['sample']['unique_firm_count'] = {
        'error': 'No firm identifier column found'
    }
```

2. **Add to console display:**
```python
if 'unique_firm_count' in stats['sample'] and 'count' in stats['sample']['unique_firm_count']:
    print(f"Unique Firms: {stats['sample']['unique_firm_count']['count']:,}")
else:
    print("Unique Firms: Unable to calculate (no GVKEY column)")
```
  </action>
  <verify>
unique_firm_count section exists in stats.json with count and column_used fields.
  </verify>
  <done>
Unique firm count calculated and stored.
  </done>
</task>

<task type="auto">
  <name>Task 4: Validate new statistics in stats.json</name>
  <files></files>
  <action>
Run validation checks on the enhanced stats.json:

1. **Run the enhanced script:**
```bash
python 2_Scripts/1.4_AssembleManifest.py
```

2. **Validate new sections exist (Python script):**
```python
import json

with open('4_Outputs/1.4_AssembleManifest/latest/stats.json') as f:
    stats = json.load(f)

# Check sample section exists
assert 'sample' in stats, "Missing 'sample' section"
print("[PASS] sample section present")

# Check SAMP-04: Industry distribution
assert 'industry_distribution' in stats['sample'], "Missing SAMP-04: industry_distribution"
assert 'ff12_code' in stats['sample']['industry_distribution'], "Missing ff12_code counts"
assert 'total_sectors' in stats['sample']['industry_distribution'], "Missing total_sectors"
assert stats['sample']['industry_distribution']['total_sectors'] > 0, "total_sectors must be > 0"
print("[PASS] SAMP-04: Industry distribution present")

# Check SAMP-05: Time distribution
assert 'time_distribution' in stats['sample'], "Missing SAMP-05: time_distribution"
assert 'year' in stats['sample']['time_distribution'], "Missing yearly counts"
assert 'min_year' in stats['sample']['time_distribution'], "Missing min_year"
assert 'max_year' in stats['sample']['time_distribution'], "Missing max_year"
print("[PASS] SAMP-05: Time distribution present")

# Check SAMP-06: Unique firm count
assert 'unique_firm_count' in stats['sample'], "Missing SAMP-06: unique_firm_count"
assert 'count' in stats['sample']['unique_firm_count'], "Missing count field"
print("[PASS] SAMP-06: Unique firm count present")

print("\n=== ALL NEW STATISTICS VALIDATED ===")
```

3. **Map to requirements:**

| Requirement | stats.json Field | Validation |
|-------------|------------------|------------|
| SAMP-04 (industry dist) | sample.industry_distribution.ff12_code | Dict with code:count pairs |
| SAMP-04 (sector count) | sample.industry_distribution.total_sectors | Integer > 0 |
| SAMP-05 (yearly counts) | sample.time_distribution.year | Dict with year:count pairs |
| SAMP-05 (year range) | sample.time_distribution.min_year, max_year | Integers |
| SAMP-06 (firm count) | sample.unique_firm_count.count | Integer > 0 |
  </action>
  <verify>
All three new sections (industry_distribution, time_distribution, unique_firm_count) exist and contain valid data.
  </verify>
  <done>
New statistics validated in stats.json.
  </done>
</task>

<task type="auto">
  <name>Task 5: Verify console output displays new statistics</name>
  <files></files>
  <action>
Check that the enhanced console output includes the new statistics:

1. **Check log file for new sections:**
```bash
grep "Industry Distribution:" 3_Logs/1.4_AssembleManifest/*.log | tail -1
grep "Time Distribution:" 3_Logs/1.4_AssembleManifest/*.log | tail -1
grep "Unique Firms:" 3_Logs/1.4_AssembleManifest/*.log | tail -1
```

2. **Verify formatting:**
- Industry sectors should show counts and percentages
- Time distribution should show year range and per-year counts
- Unique firms should show comma-formatted count

3. **Sample expected output:**
```
Industry Sectors: 12

Industry Distribution:
  1: 5,234 (15.2%)
  2: 3,456 (10.1%)
  ...

Time Distribution:
  Year Range: 2010 - 2020 (11 years)
  2010: 1,234
  2011: 1,456
  ...

Unique Firms: 2,345
```
  </action>
  <verify>
Log file contains all three new sections with properly formatted data.
  </verify>
  <done>
Console output displays all new statistics correctly.
  </done>
</task>

<task type="auto">
  <name>Task 6: Verify existing functionality is preserved</name>
  <files></files>
  <action>
Ensure enhancements didn't break existing stats:

1. **Validate core stats still work:**
```python
import json

with open('4_Outputs/1.4_AssembleManifest/latest/stats.json') as f:
    stats = json.load(f)

# Verify original stats still present
assert 'input' in stats, "Missing input section"
assert 'output' in stats, "Missing output section"
assert 'timing' in stats, "Missing timing section"
print("[PASS] Core stats sections preserved")

assert 'total_rows' in stats['input'], "Missing input.total_rows"
assert 'final_rows' in stats['output'], "Missing output.final_rows"
print("[PASS] Core row counts present")
```

2. **Run script on test data:**
```bash
python 2_Scripts/1.4_AssembleManifest.py
```

3. **Check for errors:**
No assertion errors or exceptions should occur.
  </action>
  <verify>
Original statistics (input, output, timing) remain intact and valid.
  </verify>
  <done>
Existing functionality preserved; no regressions.
  </done>
</task>

</tasks>

<verification>
- [ ] Industry distribution (SAMP-04) calculated and stored in stats.json
- [ ] Time distribution (SAMP-05) calculated and stored in stats.json
- [ ] Unique firm count (SAMP-06) calculated and stored in stats.json
- [ ] All three new sections contain valid, non-empty data
- [ ] Console output displays all new statistics with proper formatting
- [ ] Existing statistics sections remain intact
- [ ] No errors or exceptions during script execution
- [ ] Log file matches console output for new statistics
</verification>

<success_criteria>
Enhancement complete when:
1. SAMP-04, SAMP-05, SAMP-06 are fully implemented in 1.4_AssembleManifest.py
2. All three new statistics appear correctly in stats.json
3. Console/log output displays all new statistics
4. Existing functionality remains intact (no regressions)
5. All validation checks pass without errors
</success_criteria>

<output>
After completion, create `.planning/phases/02-sample-enhancement/01-SUMMARY.md`
</output>
