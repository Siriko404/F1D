"""
End-to-End integration test for the full pipeline execution.

This test verifies that all 17 pipeline scripts execute successfully in the correct order
from Step 1 (Sample) through Step 4 (Econometric), ensuring data flows correctly between steps.

Purpose: Close the critical testing gap identified in the v1.0.0 milestone audit.
"""

import os
import pytest
import subprocess
import json
from pathlib import Path
import time
import sys

# Add 2_Scripts to path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.path_utils import get_latest_output_dir, OutputResolutionError

pytestmark = pytest.mark.e2e  # Mark all tests in this file as E2E

# Get repository root from test file location
REPO_ROOT = Path(__file__).parent.parent.parent

# Environment for subprocess calls (includes PYTHONPATH for module resolution)
SUBPROCESS_ENV = {
    "PYTHONPATH": str(REPO_ROOT / "2_Scripts"),
    **os.environ,  # Preserve existing environment variables
}

# Define the complete pipeline execution order
PIPELINE_SCRIPTS = [
    # Step 1: Sample Construction (4 scripts)
    "2_Scripts/1_Sample/1.1_CleanMetadata.py",
    "2_Scripts/1_Sample/1.2_LinkEntities.py",
    "2_Scripts/1_Sample/1.3_BuildTenureMap.py",
    "2_Scripts/1_Sample/1.4_AssembleManifest.py",
    # Step 2: Text Processing (3 scripts)
    "2_Scripts/2_Text/2.1_TokenizeAndCount.py",
    "2_Scripts/2_Text/2.2_ConstructVariables.py",
    "2_Scripts/2_Text/2.3_VerifyStep2.py",
    # Step 3: Financial Features (4 scripts)
    "2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py",
    "2_Scripts/3_Financial/3.1_FirmControls.py",
    "2_Scripts/3_Financial/3.2_MarketVariables.py",
    "2_Scripts/3_Financial/3.3_EventFlags.py",
    # Step 4: Econometric Analysis (7 scripts)
    "2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py",
    "2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py",
    "2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py",
    "2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py",
    "2_Scripts/4_Econometric/4.1.4_EstimateCeoTone.py",
    "2_Scripts/4_Econometric/4.2_LiquidityRegressions.py",
    "2_Scripts/4_Econometric/4.3_TakeoverHazards.py",
]

# Expected output files for each script (critical artifacts to verify)
EXPECTED_OUTPUTS = {
    "2_Scripts/1_Sample/1.0_BuildSampleManifest.py": ["stats.json"],
    "2_Scripts/1_Sample/1.1_CleanMetadata.py": [
        "cleaned_metadata.parquet",
        "stats.json",
    ],
    "2_Scripts/1_Sample/1.2_LinkEntities.py": ["linked_entities.parquet", "stats.json"],
    "2_Scripts/1_Sample/1.3_BuildTenureMap.py": ["tenure_map.parquet", "stats.json"],
    "2_Scripts/1_Sample/1.4_AssembleManifest.py": ["manifest.parquet", "stats.json"],
    "2_Scripts/2_Text/2.1_TokenizeAndCount.py": ["token_counts.parquet", "stats.json"],
    "2_Scripts/2_Text/2.2_ConstructVariables.py": [
        "linguistic_variables.parquet",
        "stats.json",
    ],
    "2_Scripts/2_Text/2.3_VerifyStep2.py": ["verification_report.json", "stats.json"],
    "2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py": [
        "financial_features.parquet",
        "stats.json",
    ],
    "2_Scripts/3_Financial/3.1_FirmControls.py": [
        "firm_controls.parquet",
        "stats.json",
    ],
    "2_Scripts/3_Financial/3.2_MarketVariables.py": [
        "market_variables.parquet",
        "stats.json",
    ],
    "2_Scripts/3_Financial/3.3_EventFlags.py": ["event_flags.parquet", "stats.json"],
    "2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py": [
        "regression_results.json",
        "stats.json",
    ],
    "2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py": [
        "ceo_specific_results.json",
        "stats.json",
    ],
    "2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py": [
        "extended_results.json",
        "stats.json",
    ],
    "2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py": [
        "regime_results.json",
        "stats.json",
    ],
    "2_Scripts/4_Econometric/4.1.4_EstimateCeoTone.py": [
        "tone_results.json",
        "stats.json",
    ],
    "2_Scripts/4_Econometric/4.2_LiquidityRegressions.py": [
        "liquidity_results.json",
        "stats.json",
    ],
    "2_Scripts/4_Econometric/4.3_TakeoverHazards.py": [
        "hazard_results.json",
        "stats.json",
    ],
}


def get_output_dir(script_path: str) -> Path:
    """
    Derive output directory path for a given script.

    Scripts output to timestamped directories. Uses get_latest_output_dir()
    to find the most recent output directory by timestamp.

    Mapping:
    - 1_Sample/* → 4_Outputs/1.1_CleanMetadata/ -> TIMESTAMPED
    - 2_Text/* → 4_Outputs/2_Textual_Analysis/2.1_Tokenized/ -> TIMESTAMPED
    - 3_Financial/* → 4_Outputs/3_Financial/3.0_BuildFinancialFeatures/ -> TIMESTAMPED
    - 4_Econometric/* → 4_Outputs/4_Econometric/4.1_EstimateCeoClarity/ -> TIMESTAMPED
    """
    script_name = Path(script_path).stem

    try:
        if "/1_Sample/" in script_path:
            return get_latest_output_dir(REPO_ROOT / "4_Outputs" / script_name)
        elif "/2_Text/" in script_path:
            return get_latest_output_dir(
                REPO_ROOT / "4_Outputs" / "2_Textual_Analysis" / script_name
            )
        elif "/3_Financial/" in script_path:
            return get_latest_output_dir(
                REPO_ROOT / "4_Outputs" / "3_Financial" / script_name
            )
        elif "/4_Econometric/" in script_path:
            return get_latest_output_dir(
                REPO_ROOT / "4_Outputs" / "4_Econometric" / script_name
            )
        else:
            raise ValueError(f"Unknown script path format: {script_path}")
    except OutputResolutionError:
        # Fallback to /latest/ path for tests that run before outputs exist
        if "/1_Sample/" in script_path:
            return REPO_ROOT / "4_Outputs" / script_name / "latest"
        elif "/2_Text/" in script_path:
            return (
                REPO_ROOT / "4_Outputs" / "2_Textual_Analysis" / script_name / "latest"
            )
        elif "/3_Financial/" in script_path:
            return REPO_ROOT / "4_Outputs" / "3_Financial" / script_name / "latest"
        elif "/4_Econometric/" in script_path:
            return REPO_ROOT / "4_Outputs" / "4_Econometric" / script_name / "latest"
        else:
            raise ValueError(f"Unknown script path format: {script_path}")


@pytest.mark.slow
def test_full_pipeline_execution():
    """
    Test end-to-end execution of the full pipeline (all 17 scripts).

    This test:
    1. Runs each script in the defined order
    2. Verifies each script exits with return code 0
    3. Checks that expected output files exist
    4. Fails fast on any error (stops execution on first failure)

    Expected runtime: ~15-20 minutes for full pipeline on production data.
    """
    execution_results = []
    failed_scripts = []

    for i, script_path in enumerate(PIPELINE_SCRIPTS, start=1):
        print(f"\n{'=' * 70}")
        print(f"[{i}/{len(PIPELINE_SCRIPTS)}] Running: {script_path}")
        print(f"{'=' * 70}")

        script_path_obj = Path(script_path)

        # Verify script exists
        if not script_path_obj.exists():
            pytest.fail(f"Script not found: {script_path_obj}")

        # Run script with timeout
        start_time = time.time()
        try:
            result = subprocess.run(
                ["python", str(script_path_obj)],
                env=SUBPROCESS_ENV,
                capture_output=True,
                text=True,
                timeout=600,  # 10-minute timeout per script
            )
        except subprocess.TimeoutExpired as e:
            error_msg = (
                f"Script timed out after 10 minutes: {script_path}\n"
                f"Stdout (last 500 chars): {e.stdout[-500:] if e.stdout else 'N/A'}\n"
                f"Stderr (last 500 chars): {e.stderr[-500:] if e.stderr else 'N/A'}"
            )
            pytest.fail(error_msg)

        duration = time.time() - start_time

        # Record result
        execution_results.append(
            {
                "script": script_path,
                "returncode": result.returncode,
                "duration_seconds": duration,
                "success": result.returncode == 0,
            }
        )

        # Check return code
        if result.returncode != 0:
            error_msg = (
                f"Script failed with exit code {result.returncode}: {script_path}\n"
                f"Duration: {duration:.2f} seconds\n\n"
                f"STDOUT:\n{result.stdout}\n\n"
                f"STDERR:\n{result.stderr}"
            )
            failed_scripts.append(script_path)
            pytest.fail(error_msg)

        # Verify output directory exists
        output_dir = get_output_dir(script_path)
        if not output_dir.exists():
            pytest.fail(
                f"Output directory not created: {output_dir}\n"
                f"Script: {script_path}\n"
                f"STDOUT:\n{result.stdout}"
            )

        # Verify expected output files exist
        expected_files = EXPECTED_OUTPUTS.get(script_path, [])
        missing_files = []

        for filename in expected_files:
            file_path = output_dir / filename
            if not file_path.exists():
                missing_files.append(filename)

        if missing_files:
            pytest.fail(
                f"Missing expected output files for {script_path}:\n"
                f"  - Output dir: {output_dir}\n"
                f"  - Missing files: {missing_files}\n"
                f"  - Files found: {[f.name for f in output_dir.iterdir() if f.is_file()]}"
            )

        print(f"✓ Script completed successfully in {duration:.2f}s")
        print(f"✓ Output directory: {output_dir}")

    # All scripts completed successfully
    print(f"\n{'=' * 70}")
    print(f"✓ All {len(PIPELINE_SCRIPTS)} scripts executed successfully!")
    print(f"{'=' * 70}")

    # Print execution summary
    total_duration = sum(r["duration_seconds"] for r in execution_results)
    print(f"\nExecution Summary:")
    print(f"  Total scripts: {len(PIPELINE_SCRIPTS)}")
    print(
        f"  Total duration: {total_duration:.2f}s ({total_duration / 60:.2f} minutes)"
    )
    print(f"  Average per script: {total_duration / len(PIPELINE_SCRIPTS):.2f}s")

    # Verify final critical outputs exist (Step 4 results)
    try:
        final_outputs_dir = get_latest_output_dir(
            REPO_ROOT / "4_Outputs/4_Econometric/4.3_TakeoverHazards"
        )
    except OutputResolutionError:
        final_outputs_dir = (
            REPO_ROOT / "4_Outputs/4_Econometric/4.3_TakeoverHazards/latest"
        )
    assert final_outputs_dir.exists(), "Final Step 4 output directory not created"

    # Check for at least one output file from the final script
    final_files = list(final_outputs_dir.glob("*.parquet")) + list(
        final_outputs_dir.glob("*.json")
    )
    assert len(final_files) > 0, (
        f"No output files found in final directory: {final_outputs_dir}"
    )


@pytest.mark.slow
def test_pipeline_data_flow():
    """
    Test that data flows correctly between pipeline steps.

    This test verifies:
    1. Step 1 outputs exist and are accessible by Step 2
    2. Step 2 outputs exist and are accessible by Step 3
    3. Step 3 outputs exist and are accessible by Step 4
    4. Step 4 outputs are generated successfully

    This is a lighter-weight test that doesn't run all scripts,
    but verifies the pipeline's data structure is intact.
    """
    # Check Step 1 final output exists
    step1_output = REPO_ROOT / "4_Outputs/1.4_AssembleManifest/latest"
    assert step1_output.exists(), f"Step 1 output directory missing: {step1_output}"

    # Check Step 2 final output exists (critical for Step 4)
    step2_output = (
        REPO_ROOT / "4_Outputs/2_Textual_Analysis/2.2_ConstructVariables/latest"
    )
    assert step2_output.exists(), f"Step 2 output directory missing: {step2_output}"

    # Verify linguistic_variables.parquet exists (Step 4 needs this)
    linguistic_vars = step2_output / "linguistic_variables.parquet"
    assert linguistic_vars.exists(), (
        f"Critical file missing: {linguistic_vars}\n"
        f"This file is required by Step 4 scripts (4.1, 4.1.1, 4.1.3)."
    )

    # Check Step 3 outputs exist
    step3_output = REPO_ROOT / "4_Outputs/3_Financial/3.3_EventFlags/latest"
    assert step3_output.exists(), f"Step 3 output directory missing: {step3_output}"

    # Check Step 4 outputs exist
    step4_output = REPO_ROOT / "4_Outputs/4_Econometric/4.3_TakeoverHazards/latest"
    assert step4_output.exists(), f"Step 4 output directory missing: {step4_output}"

    # Verify at least one output file in Step 4
    step4_files = list(step4_output.glob("*.json")) + list(
        step4_output.glob("*.parquet")
    )
    assert len(step4_files) > 0, (
        f"No output files found in Step 4 directory: {step4_output}"
    )


@pytest.mark.slow
def test_pipeline_stats_json_structure():
    """
    Verify that all scripts generated valid stats.json files with required fields.

    This test ensures the pipeline's observability infrastructure works correctly
    and all scripts produce structured output with proper tracking.
    """
    missing_stats = []
    invalid_stats = []

    for script_path in PIPELINE_SCRIPTS:
        output_dir = get_output_dir(script_path)
        stats_path = output_dir / "stats.json"

        if not stats_path.exists():
            missing_stats.append((script_path, stats_path))
            continue

        try:
            with open(stats_path) as f:
                stats = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            invalid_stats.append((script_path, str(e)))
            continue

        # Verify required fields
        required_fields = ["inputs", "outputs", "processing"]
        for field in required_fields:
            if field not in stats:
                invalid_stats.append((script_path, f"Missing required field: {field}"))

        # Verify processing metadata
        if "processing" in stats:
            required_processing = ["duration_seconds", "start_time", "end_time"]
            for field in required_processing:
                if field not in stats["processing"]:
                    invalid_stats.append((script_path, f"Missing processing.{field}"))

    if missing_stats:
        pytest.fail(
            f"Missing stats.json files:\n"
            + "\n".join(f"  - {s}: {p}" for s, p in missing_stats)
        )

    if invalid_stats:
        pytest.fail(
            f"Invalid stats.json files:\n"
            + "\n".join(f"  - {s}: {e}" for s, e in invalid_stats)
        )
