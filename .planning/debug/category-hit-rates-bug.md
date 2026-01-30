---
status: investigating
trigger: "Script 2.1_TokenizeAndCount must produce correct output without manual intervention"
created: 2025-01-30T00:00:00Z
updated: 2025-01-30T00:00:00Z
---

## Current Focus

hypothesis: ROOT CAUSE - compute_tokenize_process_stats initializes category_hit_rates with zeros. The post-load workaround (lines 1093-1104) DOES calculate correctly BUT loads output files AFTER compute_tokenize_process_stats has already been called. The fix needs to move the workaround BEFORE calling compute_tokenize_process_stats, OR modify the function to accept output_dfs parameter.
test: Check the execution order - when is compute_tokenize_process_stats called vs when output files are loaded?
expecting: compute_tokenize_process_stats called at line 1073, outputs loaded at line 1083, workaround at line 1093 (too late!)
next_action: Fix by moving workaround before line 1073, OR by modifying compute_tokenize_process_stats to calculate from output_dfs

## Symptoms

expected: category_hit_rates in stats.json should show correct percentage values (e.g., 95.00%, 87.50%)
actual: category_hit_rates shows 0.00% for all categories
errors: ProcessPool crash on re-run: "A process in the process pool was terminated abruptly while the future was running or pending."
reproduction: Run 2_Scripts/2_Text/2.1_TokenizeAndCount.py
started: After quick task 023 added descriptive statistics; bug fix applied in commit ad3f486 but ProcessPool crashes on re-run

## Eliminated

## Evidence

- timestamp: 2025-01-30T00:00:00Z
  checked: compute_tokenize_process_stats function in observability_utils.py (lines 2275-2380)
  found: Lines 2337-2342 initialize category_hit_rates with zeros and comment "To be filled during script execution"
  implication: This function creates the structure but doesn't calculate actual values - it's a placeholder

- timestamp: 2025-01-30T00:00:00Z
  checked: Main script 2.1_TokenizeAndCount.py lines 1093-1104
  found: Post-load workaround that calculates category_hit_rates AFTER loading output files back
  implication: This works but requires loading all output files again - inefficient and was the source of the bug

- timestamp: 2025-01-30T00:00:00Z
  checked: Lines 1070-1075 in main script
  found: compute_tokenize_process_stats called at line 1073-1075, returns zeros, then saved to stats
  implication: The zero values get written to stats.json and report before the post-load calculation happens

- timestamp: 2025-01-30T00:00:00Z
  checked: Execution flow in main() function (lines 1069-1105)
  found: Line 1073 calls compute_tokenize_process_stats (returns zeros), line 1083 loads output files, line 1093 fills in category_hit_rates, line 1143 saves stats
  implication: When stats are saved at line 1181 (save_stats call), category_hit_rates has been filled, so stats.json should be correct. But need to verify the report generation happens at the right time.

- timestamp: 2025-01-30T00:00:00Z
  checked: Line 1185 - generate_tokenization_report called AFTER save_stats
  found: Report generation uses stats["tokenize_process"]["category_hit_rates"] which should be filled by line 1104
  implication: Both stats.json and report should have correct values if the workaround at 1093-1104 executes. But user reports 0.00% values, suggesting workaround might not be executing.

