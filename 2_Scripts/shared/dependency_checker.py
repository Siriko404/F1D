#!/usr/bin/env python3
"""
==============================================================================
SHARED MODULE: Dependency Checker
==============================================================================
ID: shared/dependency_checker
Description: Validates prerequisites (input files, previous step outputs)
             for pipeline scripts, providing clear error messages with
             next steps when dependencies are missing.

Inputs:
    - required_files: Dict of {name: Path} for input files to validate
    - required_steps: Dict of {step_name: expected_output_file} for prerequisite steps

Outputs:
    - Validated prerequisites (raises SystemExit if validation fails)
    - Printed error messages with actionable next steps

Deterministic: true
==============================================================================
"""

import sys
from pathlib import Path
from typing import Dict, List


def validate_prerequisites(
    required_files: Dict[str, Path] = None, required_steps: Dict[str, str] = None
) -> None:
    """
    Validates all required inputs and prerequisite step outputs.

    Args:
        required_files: Dict of {name: Path} for input files or directories to check
        required_steps: Dict of {name: expected_output_file} for prerequisite steps

    Raises:
        SystemExit: If validation fails with error code 1
    """
    errors = []

    # Check input files and directories
    if required_files:
        from shared.path_utils import validate_input_file, PathValidationError

        for name, path in required_files.items():
            try:
                # Check if it's a directory (name ends with /) or file
                if name.endswith("/"):
                    # Directory validation
                    if not path.exists():
                        errors.append(f"Missing input directory: {name} ({path})")
                    elif not path.is_dir():
                        errors.append(
                            f"Path exists but is not a directory: {name} ({path})"
                        )
                else:
                    # File validation
                    validate_input_file(path, must_exist=True)
            except PathValidationError as e:
                errors.append(f"Missing input file: {name} ({path})")

    # Check prerequisite steps
    if required_steps:
        root = Path(__file__).parent.parent.parent

        for step_name, expected_output in required_steps.items():
            if not validate_prerequisite_step(step_name, expected_output, root):
                errors.append(
                    f"Missing prerequisite output from {step_name}: {expected_output}"
                )

    # Report results
    if errors:
        print_prerequisite_errors(errors)
        sys.exit(1)
    else:
        print("[OK] All prerequisites validated")


def validate_prerequisite_step(
    step_name: str, expected_output_file: str, root: Path
) -> bool:
    """
    Validates a single prerequisite step has completed.

    Uses timestamp-based resolution instead of symlinks.

    Args:
        step_name: Name of step (e.g., "1.1_CleanMetadata")
        expected_output_file: Expected output filename
        root: Project root path

    Returns:
        True if valid, False otherwise
    """
    from shared.path_utils import get_latest_output_dir, OutputResolutionError

    output_base = root / "4_Outputs" / step_name

    try:
        latest_dir = get_latest_output_dir(
            output_base, required_file=expected_output_file
        )
        return (latest_dir / expected_output_file).exists()
    except OutputResolutionError:
        return False


def print_prerequisite_errors(errors: List[str]) -> None:
    """
    Formats and prints prerequisite error messages.

    Args:
        errors: List of error messages
    """
    print()
    print("=" * 70)
    print("ERROR: Prerequisites not met")
    print("=" * 70)
    print()
    print("The following issues were found:")
    print()

    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

    print()
    print("To fix these issues:")
    print("  1. Ensure all input files are in 1_Inputs/")
    print("  2. Run the pipeline in correct order:")
    print("     Step 1: python 2_Scripts/1_Sample/1.1_CleanMetadata.py")
    print("     Step 2: python 2_Scripts/1_Sample/1.2_LinkEntities.py")
    print("     Step 3: python 2_Scripts/1_Sample/1.3_BuildTenureMap.py")
    print("     Step 4: python 2_Scripts/1_Sample/1.4_AssembleManifest.py")
    print("     Step 2: python 2_Scripts/2_Text/2.1_TokenizeAndCount.py")
    print("     Step 2: python 2_Scripts/2_Text/2.2_ConstructVariables.py")
    print("     Step 3: python 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py")
    print("     Step 4: python 2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py")
    print()
    print("For help, run with --help flag")
    print()


def handle_missing_output(
    step_name: str, output_file: str, calling_script: str
) -> None:
    """
    Print error for missing prerequisite output.

    Args:
        step_name: Name of step that should have been run
        output_file: Expected output file name
        calling_script: Name of current script

    Raises:
        SystemExit: Always exits with error code 1
    """
    print()
    print("=" * 70)
    print("ERROR: Missing prerequisite output")
    print("=" * 70)
    print()
    print(f"Required output from {step_name} not found:")
    print(f"  Expected file: {output_file}")
    print(f"  Location: 4_Outputs/{step_name}/<timestamp>/")
    print()
    print(f"Please run the pipeline in order:")
    print(
        f"  1. {step_name}: python 2_Scripts/{step_name.split('_')[0]}/{step_name}.py"
    )
    print(
        f"  2. {calling_script}: python 2_Scripts/{calling_script.split('_')[0]}/{calling_script}.py"
    )
    print()
    print("For more information, see: README.md")
    sys.exit(1)
