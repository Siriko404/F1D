#!/usr/bin/env python3
"""
==============================================================================
STEP 1: Build Sample Manifest (Orchestrator)
==============================================================================
ID: 1.0_BuildSampleManifest
Description: Orchestrates the 4-substep process to build the master sample
             manifest that defines the universe of analysis before any text
             processing occurs.
             
Substeps:
    1.1 - Clean Metadata & Filter Events
    1.2 - Entity Resolution (CCM Linking)
    1.3 - CEO Tenure Map Construction
    1.4 - Manifest Assembly & CEO Filtering
    
Inputs:
    - config/project.yaml
    
Outputs:
    - 4_Outputs/1.0_BuildSampleManifest/{timestamp}/master_sample_manifest.parquet
    - 4_Outputs/1.0_BuildSampleManifest/{timestamp}/report_step_1_0.md
    - 3_Logs/1.0_BuildSampleManifest/{timestamp}.log
    
Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import yaml
import shutil

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
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        'root': root,
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "1.0_BuildSampleManifest"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "1.0_BuildSampleManifest"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

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
    print_dual("STEP 1.0: Build Sample Manifest - Orchestrator")
    print_dual("="*80)
    print_dual(f"Timestamp: {timestamp}")
    print_dual(f"Output Directory: {paths['output_dir']}")
    print_dual(f"Log File: {paths['log_file']}")
    print_dual("")
    
    # Define substeps
    substeps = [
        {
            'id': '1.1',
            'name': 'Clean Metadata & Filter Events',
            'script': '1.1_CleanMetadata.py',
            'description': 'Deduplicates Unified-info and filters for earnings calls'
        },
        {
            'id': '1.2',
            'name': 'Entity Resolution (CCM Linking)',
            'script': '1.2_LinkEntities.py',
            'description': '4-tier linking to assign GVKEY and industry codes'
        },
        {
            'id': '1.3',
            'name': 'CEO Tenure Map Construction',
            'script': '1.3_BuildTenureMap.py',
            'description': 'Builds monthly CEO tenure panel from Execucomp'
        },
        {
            'id': '1.4',
            'name': 'Manifest Assembly & CEO Filtering',
            'script': '1.4_AssembleManifest.py',
            'description': 'Joins metadata with CEO panel and applies minimum call threshold'
        }
    ]
    
    # Execute substeps sequentially
    success = True
    for step in substeps:
        print_dual(f"\n{'='*80}")
        print_dual(f"Substep {step['id']}: {step['name']}")
        print_dual(f"{'='*80}")
        print_dual(f"Description: {step['description']}")
        print_dual(f"Script: {step['script']}\n")
        
        # Construct path to subscript
        script_path = Path(__file__).parent / step['script']
        
        if not script_path.exists():
            print_dual(f"ERROR: Script not found: {script_path}")
            success = False
            break
        
        # Execute subscript
        import subprocess
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print_dual(result.stdout)
        
        if result.returncode != 0:
            print_dual(f"\nERROR: Substep {step['id']} failed with exit code {result.returncode}")
            if result.stderr:
                print_dual(f"STDERR:\n{result.stderr}")
            success = False
            break
        
        print_dual(f"Substep {step['id']} completed successfully.")
    
    # Final summary
    print_dual(f"\n{'='*80}")
    print_dual("EXECUTION SUMMARY")
    print_dual(f"{'='*80}")
    
    if success:
        print_dual("Status: SUCCESS")
        print_dual("All substeps completed successfully.")
        
        # Copy final manifest to orchestrator output
        manifest_source = paths['root'] / '4_Outputs' / '1.4_AssembleManifest' / 'latest' / 'master_sample_manifest.parquet'
        if manifest_source.exists():
            manifest_dest = paths['output_dir'] / 'master_sample_manifest.parquet'
            shutil.copy2(manifest_source, manifest_dest)
            print_dual(f"Final manifest copied to: {manifest_dest}")
        
        # Update latest symlink (directory junction on Windows)
        if paths['latest_dir'].exists():
            if paths['latest_dir'].is_symlink() or paths['latest_dir'].is_junction():
                paths['latest_dir'].unlink()
            else:
                shutil.rmtree(paths['latest_dir'])
        
        try:
            paths['latest_dir'].symlink_to(paths['output_dir'], target_is_directory=True)
            print_dual(f"Updated 'latest' -> {paths['output_dir'].name}")
        except OSError:
            shutil.copytree(paths['output_dir'], paths['latest_dir'])
            print_dual(f"Copied outputs to 'latest' (symlink not available)")
        
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
