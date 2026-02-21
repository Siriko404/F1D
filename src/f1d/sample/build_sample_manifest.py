#!/usr/bin/env python3
"""
==============================================================================
STEP 1: Build Sample Manifest (Orchestrator)
==============================================================================
Tier 2: Stage 1 - Sample construction module.

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
    - outputs/1.0_BuildSampleManifest/{timestamp}/master_sample_manifest.parquet
    - outputs/1.0_BuildSampleManifest/{timestamp}/report_step_1_0.md
    - logs/1.0_BuildSampleManifest/{timestamp}.log

Deterministic: true
Dependencies:
    - Requires: inputs/Earnings_Calls_Transcripts/Unified-info.parquet
    - Uses: pandas, yaml

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from f1d.shared.observability import DualWriter
from f1d.shared.path_utils import (
    OutputResolutionError,
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
    validate_output_path,
)
from f1d.shared.subprocess_validation import validate_script_path


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for 1.0_BuildSampleManifest.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 1.0: Build Sample Manifest (Orchestrator)

Orchestrates 4-substep process to build the master sample
manifest that defines the universe of analysis before any text
processing occurs.

Substeps:
    1.1 - Clean Metadata & Filter Events
    1.2 - Entity Resolution (CCM Linking)
    1.3 - CEO Tenure Map Construction
    1.4 - Manifest Assembly & CEO Filtering
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    parser.add_argument(
        "--skip",
        type=str,
        nargs="+",
        help="Skip specific substeps (e.g., --skip 1.1 1.2)",
    )

    return parser.parse_args()


def check_prerequisites(root: Path) -> None:
    """Validate all required inputs exist."""
    from f1d.shared.dependency_checker import validate_prerequisites

    required_files = {
        "config/project.yaml": root / "config/project.yaml",
        "inputs/Earnings_Calls_Transcripts/Unified-info.parquet": root
        / "inputs"
        / "Earnings_Calls_Transcripts"
        / "Unified-info.parquet",
    }

    required_steps: Dict[str, str] = {}

    validate_prerequisites(required_files, required_steps)


def print_dual(msg: str) -> None:
    """Print to both terminal and log"""
    print(msg, flush=True)


# ==============================================================================
# Configuration and setup
# ==============================================================================

# Allowed script directory for subprocess validation (prevents path traversal)
ALLOWED_SCRIPT_DIR = Path(__file__).parent  # src/f1d/sample/


def load_config() -> Dict[str, Any]:
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config: Dict[str, Any]) -> tuple[Dict[str, Path], str]:
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent.parent

    paths = {
        "root": root,
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config["paths"]["outputs"] / "1.0_BuildSampleManifest"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Create log directory
    log_base = root / config["paths"]["logs"] / "1.0_BuildSampleManifest"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths, timestamp


# ==============================================================================
# Orchestration
# ==============================================================================


def main() -> int:
    """Main orchestration function"""

    # Load config
    config = load_config()
    paths, timestamp = setup_paths(config)

    # Setup dual logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print_dual("=" * 80)
    print_dual("STEP 1.0: Build Sample Manifest - Orchestrator")
    print_dual("=" * 80)
    print_dual(f"Timestamp: {timestamp}")
    print_dual(f"Output Directory: {paths['output_dir']}")
    print_dual(f"Log File: {paths['log_file']}")
    print_dual("")

    # Define substeps
    substeps = [
        {
            "id": "1.1",
            "name": "Clean Metadata & Filter Events",
            "script": "1.1_CleanMetadata.py",
            "description": "Deduplicates Unified-info and filters for earnings calls",
        },
        {
            "id": "1.2",
            "name": "Entity Resolution (CCM Linking)",
            "script": "1.2_LinkEntities.py",
            "description": "4-tier linking to assign GVKEY and industry codes",
        },
        {
            "id": "1.3",
            "name": "CEO Tenure Map Construction",
            "script": "1.3_BuildTenureMap.py",
            "description": "Builds monthly CEO tenure panel from Execucomp",
        },
        {
            "id": "1.4",
            "name": "Manifest Assembly & CEO Filtering",
            "script": "1.4_AssembleManifest.py",
            "description": "Joins metadata with CEO panel and applies minimum call threshold",
        },
    ]

    # Execute substeps sequentially
    success = True
    for step in substeps:
        print_dual(f"\n{'=' * 80}")
        print_dual(f"Substep {step['id']}: {step['name']}")
        print_dual(f"{'=' * 80}")
        print_dual(f"Description: {step['description']}")
        print_dual(f"Script: {step['script']}\n")

        # Construct path to subscript
        script_path = Path(__file__).parent / step["script"]

        # Validate script path before execution (security: prevents path traversal)
        try:
            validated_path = validate_script_path(script_path, ALLOWED_SCRIPT_DIR)
        except (ValueError, FileNotFoundError) as e:
            print_dual(f"ERROR: Script validation failed: {e}")
            success = False
            break

        # Execute subscript with validated absolute path
        # Set PYTHONPATH to include project root for f1d.shared.* imports
        env = os.environ.copy()
        scripts_root = str(Path(__file__).parent.parent.parent.parent)
        # Use os.pathsep for cross-platform compatibility (':' on Unix, ';' on Windows)
        existing_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{existing_path}{os.pathsep}{scripts_root}"
            if existing_path
            else scripts_root
        )

        result = subprocess.run(
            [sys.executable, str(validated_path)],
            capture_output=True,
            text=True,
            env=env,
        )

        # Print output
        if result.stdout:
            print_dual(result.stdout)

        if result.returncode != 0:
            print_dual(
                f"\nERROR: Substep {step['id']} failed with exit code {result.returncode}"
            )
            if result.stderr:
                print_dual(f"STDERR:\n{result.stderr}")
            success = False
            break

        print_dual(f"Substep {step['id']} completed successfully.")

    # Final summary
    print_dual(f"\n{'=' * 80}")
    print_dual("EXECUTION SUMMARY")
    print_dual(f"{'=' * 80}")

    if success:
        print_dual("Status: SUCCESS")
        print_dual("All substeps completed successfully.")

        # Copy final manifest to orchestrator output
        manifest_dir = get_latest_output_dir(
            paths["root"] / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_source = manifest_dir / "master_sample_manifest.parquet"
        manifest_dest = paths["output_dir"] / "master_sample_manifest.parquet"
        shutil.copy2(manifest_source, manifest_dest)
        print_dual(f"Final manifest copied to: {manifest_dest}")

    else:
        print_dual("Status: FAILED")
        print_dual("One or more substeps failed. Please check the logs above.")

    print_dual(f"\nLog file: {paths['log_file']}")
    print_dual("=" * 80)

    # Restore stdout and close log
    sys.stdout = dual_writer.terminal
    dual_writer.close()

    return 0 if success else 1


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        print("[OK] All prerequisites validated")
        print("[OK] Ready to execute: python -m f1d.sample.1_0_BuildSampleManifest")
        sys.exit(0)

    check_prerequisites(root)
    main()
