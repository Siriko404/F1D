#!/usr/bin/env python3
"""
==============================================================================
STEP 2: Linguistic Analysis (Orchestrator)
==============================================================================
ID: 2.0_LinguisticAnalysis
Description: Orchestrates the 2-substep process to extract linguistic features
             from earnings call transcripts.
             
Substeps:
    2.1 - Process Text Features (Token extraction by LM category)
    2.3 - Linguistic Measures (pct, unique_pct, entropy, interaction)
    
Inputs:
    - 4_Outputs/1_Sample/latest/master_sample_manifest.parquet
    - 0_Unified-data-info/speakers/*.parquet
    - 1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv
    
Outputs:
    - 4_Outputs/2_Linguistic_Analysis/{timestamp}/linguistic_features_*.parquet
    - 4_Outputs/2_Linguistic_Analysis/{timestamp}/linguistic_measures_*.parquet
    - 4_Outputs/2_Linguistic_Analysis/{timestamp}/variable_reference.csv
    - 4_Outputs/2_Linguistic_Analysis/{timestamp}/report_step_2.md
    - 3_Logs/2_Text/{timestamp}.log
    
Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import yaml
import shutil
import subprocess

# ==============================================================================
# Dual-write logging utility
# ==============================================================================

class DualWriter:
    """Writes to both stdout and log file verbatim"""
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def print_dual(msg):
    """Print to both terminal and log"""
    print(msg, flush=True)

# ==============================================================================
# Configuration and setup
# ==============================================================================

def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Fallback defaults
        return {
            'paths': {
                'outputs': '4_Outputs',
                'logs': '3_Logs'
            }
        }

def setup_paths(config):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        'root': root,
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "2_Linguistic_Analysis"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "2_Text"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# ==============================================================================
# Report generation
# ==============================================================================

def generate_report(output_dir, timestamp, substep_results, total_time):
    """Generate comprehensive markdown report"""
    
    report_lines = [
        "# Step 2: Linguistic Analysis Report",
        "",
        f"**Timestamp:** {timestamp}",
        f"**Total Runtime:** {total_time:.1f} seconds",
        f"**Output Directory:** `{output_dir}`",
        "",
        "---",
        "",
        "## Substep Summary",
        "",
    ]
    
    for result in substep_results:
        status = "[PASS]" if result['success'] else "[FAIL]"
        report_lines.append(f"### {result['id']}: {result['name']} {status}")
        report_lines.append(f"- **Description:** {result['description']}")
        report_lines.append(f"- **Runtime:** {result.get('runtime', 'N/A')}")
        report_lines.append("")
    
    report_lines.extend([
        "---",
        "",
        "## Output Files",
        "",
    ])
    
    # List output files
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            size_mb = f.stat().st_size / (1024 * 1024)
            report_lines.append(f"- `{f.name}` ({size_mb:.2f} MB)")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## Variable Reference",
        "",
        "See `variable_reference.csv` for complete column definitions.",
        "",
    ])
    
    report_path = output_dir / "report_step_2.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return report_path

def generate_combined_variable_reference(output_dir):
    """Generate combined variable reference CSV"""
    import pandas as pd
    
    categories = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 
                  'Strong_Modal', 'Weak_Modal', 'Constraining']
    
    rows = [
        # Step 2.1 Output (linguistic_features)
        ('file_name', 'Input (Unified-info)', 'Unique identifier for the earnings call'),
        ('last_update', 'Input (Unified-info)', 'Last update timestamp of the call data'),
        ('speaker_name', 'Input (Speaker Data)', 'Name of the speaker'),
        ('employer', 'Input (Speaker Data)', 'Employer of the speaker'),
        ('role', 'Input (Speaker Data)', 'Role/title of the speaker'),
        ('speaker_number', 'Input (Speaker Data)', 'Speaker sequence number in the call'),
        ('speaker_text', 'Input (Speaker Data)', 'Full text of the speaking turn'),
        ('context', 'Input (Speaker Data)', 'Section of the call (pres/qa)'),
        ('section', 'Input (Speaker Data)', 'Detailed section identifier'),
        ('total_tokens', 'Calculated (Step 2.1)', 'Total alpha-only tokens in speaking turn'),
        ('gvkey', 'Merged (Manifest)', 'Global Company Key'),
        ('conm', 'Merged (Manifest)', 'Company Name'),
        ('sic', 'Merged (Manifest)', 'Standard Industrial Classification'),
        ('call_desc', 'Merged (Manifest)', 'Call description'),
        ('start_date', 'Merged (Manifest)', 'Call date'),
        ('year', 'Calculated (Step 2.1)', 'Year of the call'),
    ]
    
    # Step 2.1 token columns
    for cat in categories:
        rows.extend([
            (f'{cat}_tokens', 'Calculated (Step 2.1)', f'List of exact {cat} tokens found'),
            (f'{cat}_unique_tokens', 'Calculated (Step 2.1)', f'List of unique {cat} tokens found'),
            (f'{cat}_count', 'Calculated (Step 2.1)', f'Total count of {cat} words'),
            (f'{cat}_unique_count', 'Calculated (Step 2.1)', f'Count of unique {cat} words'),
        ])
    
    # Step 2.3 extended measures
    for cat in categories:
        rows.extend([
            (f'{cat}_pct', 'Calculated (Step 2.3)', f'Proportion of {cat} tokens to total tokens'),
            (f'{cat}_unique_pct', 'Calculated (Step 2.3)', f'Proportion of unique {cat} tokens to total tokens'),
            (f'{cat}_entropy', 'Calculated (Step 2.3)', f'Normalized Shannon Entropy of {cat} tokens (0=focused, 1=diffuse)'),
            (f'{cat}_interaction', 'Calculated (Step 2.3)', f'{cat}_pct * {cat}_entropy'),
        ])
    
    df = pd.DataFrame(rows, columns=['Variable', 'Source', 'Description'])
    out_path = output_dir / 'variable_reference.csv'
    df.to_csv(out_path, index=False)
    return out_path

# ==============================================================================
# Orchestration
# ==============================================================================

def main():
    """Main orchestration function"""
    
    # Load config
    config = load_config()
    paths, timestamp = setup_paths(config)
    
    # Setup dual logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print_dual("="*80)
    print_dual("STEP 2.0: Linguistic Analysis - Orchestrator")
    print_dual("="*80)
    print_dual(f"Timestamp: {timestamp}")
    print_dual(f"Output Directory: {paths['output_dir']}")
    print_dual(f"Log File: {paths['log_file']}")
    print_dual("")
    
    start_time = datetime.now()
    
    # Define substeps
    substeps = [
        {
            'id': '2.1',
            'name': 'Process Text Features',
            'script': '2.1_ProcessTextFeatures.py',
            'description': 'Extracts LM dictionary tokens from speaker turns'
        },
        {
            'id': '2.3',
            'name': 'Linguistic Measures',
            'script': '2.3_Linguistic_Measures.py',
            'description': 'Calculates pct, unique_pct, entropy, and interaction'
        }
    ]
    
    # Execute substeps sequentially
    success = True
    substep_results = []
    
    for step in substeps:
        print_dual(f"\n{'='*80}")
        print_dual(f"Substep {step['id']}: {step['name']}")
        print_dual(f"{'='*80}")
        print_dual(f"Description: {step['description']}")
        print_dual(f"Script: {step['script']}\n")
        
        step_start = datetime.now()
        
        # Construct path to subscript
        script_path = Path(__file__).parent / step['script']
        
        if not script_path.exists():
            print_dual(f"ERROR: Script not found: {script_path}")
            substep_results.append({**step, 'success': False, 'runtime': 'N/A'})
            success = False
            break
        
        # Execute subscript with real-time output streaming
        process = subprocess.Popen(
            [sys.executable, '-u', str(script_path)],  # -u for unbuffered output
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Stream stdout in real-time
        while True:
            line = process.stdout.readline()
            if line:
                print_dual(line.rstrip())
            elif process.poll() is not None:
                break
        
        # Capture any remaining stderr
        stderr = process.stderr.read()
        
        step_runtime = (datetime.now() - step_start).total_seconds()
        
        if process.returncode != 0:
            print_dual(f"\nERROR: Substep {step['id']} failed with exit code {process.returncode}")
            if stderr:
                print_dual(f"STDERR:\n{stderr}")
            substep_results.append({**step, 'success': False, 'runtime': f'{step_runtime:.1f}s'})
            success = False
            break
        
        print_dual(f"\nSubstep {step['id']} completed successfully in {step_runtime:.1f}s.")
        substep_results.append({**step, 'success': True, 'runtime': f'{step_runtime:.1f}s'})
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    # Final summary
    print_dual(f"\n{'='*80}")
    print_dual("EXECUTION SUMMARY")
    print_dual(f"{'='*80}")
    
    if success:
        print_dual("Status: SUCCESS")
        print_dual("All substeps completed successfully.")
        print_dual(f"Total runtime: {total_time:.1f}s")
        
        # Copy outputs from substeps to orchestrator output directory
        print_dual("\nConsolidating outputs...")
        
        # Copy Step 2.1 outputs (linguistic_features)
        step21_latest = paths['root'] / '4_Outputs' / '2_Linguistic_Analysis' / 'latest'
        if step21_latest.exists():
            for f in step21_latest.glob("linguistic_features_*.parquet"):
                shutil.copy2(f, paths['output_dir'])
                print_dual(f"  Copied: {f.name}")
        
        # Copy Step 2.3 outputs (linguistic_measures)
        step23_latest = paths['root'] / '4_Outputs' / '2_Linguistic_Analysis' / 'extended_latest'
        if step23_latest.exists():
            for f in step23_latest.glob("linguistic_measures_*.parquet"):
                shutil.copy2(f, paths['output_dir'])
                print_dual(f"  Copied: {f.name}")
        
        # Generate combined variable reference
        varref_path = generate_combined_variable_reference(paths['output_dir'])
        print_dual(f"  Generated: {varref_path.name}")
        
        # Generate report
        report_path = generate_report(paths['output_dir'], timestamp, substep_results, total_time)
        print_dual(f"  Generated: {report_path.name}")
        
        # Update latest symlink
        if paths['latest_dir'].exists():
            if paths['latest_dir'].is_symlink():
                paths['latest_dir'].unlink()
            else:
                shutil.rmtree(paths['latest_dir'])
        
        try:
            paths['latest_dir'].symlink_to(paths['output_dir'], target_is_directory=True)
            print_dual(f"\nUpdated 'latest' -> {paths['output_dir'].name}")
        except OSError:
            shutil.copytree(paths['output_dir'], paths['latest_dir'])
            print_dual(f"\nCopied outputs to 'latest' (symlink not available)")
        
    else:
        print_dual("Status: FAILED")
        print_dual("One or more substeps failed. Please check the logs above.")
    
    print_dual(f"\nLog file: {paths['log_file']}")
    print_dual("="*80)
    
    # Restore stdout and close log
    sys.stdout = dual_writer.terminal
    dual_writer.close()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
