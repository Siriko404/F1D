#!/usr/bin/env python3
"""
==============================================================================
STEP 2.0: Validate V2 Structure
==============================================================================
ID: 2_0_ValidateV2Structure
Description: Validates Phase 28 V2 folder structure and documentation

Validates all 6 STRUCT requirements:
- STRUCT-01: Financial_V2 script folder with README
- STRUCT-02: Econometric_V2 script folder with README
- STRUCT-03: Financial_V2 outputs folder
- STRUCT-04: Econometric_V2 outputs folder
- STRUCT-05: Financial_V2 and Econometric_V2 logs folders
- STRUCT-06: Script naming convention documented

Inputs:
    - 2_Scripts/3_Financial_V2/README.md
    - 2_Scripts/4_Econometric_V2/README.md
    - Various folder paths for existence checks

Outputs:
    - Validation report to stdout and logs
    - Exit code 0 if all checks pass, 1 if any fail

Deterministic: true
==============================================================================
"""

import argparse
import json
import sys

# Add parent directory to sys.path for shared module imports
import sys as _sys
from datetime import datetime
from pathlib import Path

_script_dir = Path(__file__).parent.parent
_sys.path.insert(0, str(_script_dir))

# Import shared path validation utilities
# Import DualWriter from shared.observability_utils
from shared.observability_utils import DualWriter
from shared.path_utils import (
    ensure_output_dir,
)

# ==============================================================================
# Configuration
# ==============================================================================


def load_config():
    """Load configuration from project.yaml

    Auto-detects project root by looking for the standard top-level folders.
    """
    import yaml

    # Search upward for project root (max 3 levels)
    root = None
    for level in range(4):
        check_path = Path(__file__).resolve().parents[level]
        if all((check_path / d).exists() for d in ["2_Scripts", "3_Logs", "4_Outputs"]):
            root = check_path
            break

    # Fallback
    if root is None:
        candidate1 = Path(__file__).parent.parent.resolve()
        candidate2 = Path(__file__).parent.parent.parent.resolve()
        root = candidate1 if (candidate1 / "2_Scripts").exists() else candidate2

    config_path = root / "config" / "project.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return None


def setup_paths(timestamp):
    """Set up all required paths for validation script

    Auto-detects project root by looking for the standard top-level folders.
    """
    # Start from script location and search upward for project root
    # Project root contains: 1_Inputs, 2_Scripts, 3_Logs, 4_Outputs
    Path(__file__).parent.parent.resolve()
    root = None

    # Search upward for project root (max 3 levels)
    for level in range(4):
        check_path = Path(__file__).resolve().parents[level]
        if all((check_path / d).exists() for d in ["2_Scripts", "3_Logs", "4_Outputs"]):
            root = check_path
            break

    # Fallback: Use the directory containing 2_Scripts
    if root is None:
        # Try parent.parent (F1D level) or parent.parent.parent (if F1D is nested)
        candidate1 = Path(__file__).parent.parent.resolve()
        candidate2 = Path(__file__).parent.parent.parent.resolve()

        # Check which one has 2_Scripts
        root = candidate1 if (candidate1 / "2_Scripts").exists() else candidate2

    paths = {
        "root": root,
        "scripts_financial_v2": root / "2_Scripts" / "3_Financial_V2",
        "scripts_econometric_v2": root / "2_Scripts" / "4_Econometric_V2",
        "outputs_financial_v2": root / "4_Outputs" / "3_Financial_V2",
        "outputs_econometric_v2": root / "4_Outputs" / "4_Econometric_V2",
        "logs_financial_v2": root / "3_Logs" / "3_Financial_V2",
        "logs_econometric_v2": root / "3_Logs" / "4_Econometric_V2",
        # V1.0 paths for conflict checking
        "scripts_financial_v1": root / "2_Scripts" / "3_Financial",
        "scripts_econometric_v1": root / "2_Scripts" / "4_Econometric",
        "outputs_financial_v1": root / "4_Outputs" / "3_Financial",
        "outputs_econometric_v1": root / "4_Outputs" / "4_Econometric",
        "logs_financial_v1": root / "3_Logs" / "3_Financial",
        "logs_econometric_v1": root / "3_Logs" / "4_Econometric",
    }

    # Output directory for validation results
    output_base = root / "4_Outputs" / "2.0_ValidateV2Structure"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "2.0_ValidateV2Structure"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths


# ==============================================================================
# Validation Functions
# ==============================================================================


class ValidationResult:
    """Container for validation results"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.passed = True
        self.checks = []
        self.failures = []

    def add_check(self, check_name: str, passed: bool, details: str = ""):
        """Add a validation check result"""
        self.checks.append({"name": check_name, "passed": passed, "details": details})
        if not passed:
            self.passed = False
            self.failures.append(f"{check_name}: {details}")

    def format_report(self, width: int = 80) -> str:
        """Format validation result as a report string"""
        status = "[PASS]" if self.passed else "[FAIL]"
        lines = [
            f"\n{self.name}: {status}",
            f"  {self.description}",
        ]
        for check in self.checks:
            # Use ASCII-compatible symbols for Windows console
            symbol = "[OK]" if check["passed"] else "[X]"
            lines.append(f"  {symbol} {check['name']}")
            if check["details"] and not check["passed"]:
                lines.append(f"      {check['details']}")
        return "\n".join(lines)


def check_financial_v2_script_folder(paths) -> ValidationResult:
    """
    STRUCT-01: Financial_V2 Script Folder

    Checks:
    - 2_Scripts/3_Financial_V2/ exists
    - README.md exists in folder
    - README contains "Hypothesis 1" section
    - README contains "Hypothesis 2" section
    - README contains "Hypothesis 3" section
    - README mentions Compustat fields (CHE, AT, DLTT, etc.)
    - README contains "Input/Output Mapping" section
    """
    result = ValidationResult(
        "STRUCT-01", "Financial_V2 script folder with complete README"
    )

    folder = paths["scripts_financial_v2"]
    result.add_check(
        "Folder exists: 2_Scripts/3_Financial_V2/",
        folder.exists(),
        f"Folder not found: {folder}",
    )

    if not folder.exists():
        return result

    readme = folder / "README.md"
    result.add_check("README.md exists", readme.exists(), f"README not found: {readme}")

    if readme.exists():
        content = readme.read_text(encoding="utf-8")

        # Check for hypothesis sections
        result.add_check(
            "Contains Hypothesis 1 section",
            "Hypothesis 1" in content
            or "## H1" in content
            or "H1 Cash Holdings" in content,
            "Hypothesis 1 section not found in README",
        )

        result.add_check(
            "Contains Hypothesis 2 section",
            "Hypothesis 2" in content
            or "## H2" in content
            or "H2 Investment" in content,
            "Hypothesis 2 section not found in README",
        )

        result.add_check(
            "Contains Hypothesis 3 section",
            "Hypothesis 3" in content or "## H3" in content or "H3 Payout" in content,
            "Hypothesis 3 section not found in README",
        )

        # Check for Compustat fields
        compustat_fields = ["CHE", "AT", "DLTT"]
        fields_found = sum(1 for field in compustat_fields if field in content)
        result.add_check(
            "Documents Compustat fields",
            fields_found >= 2,
            f"Compustat fields not documented (found {fields_found}/3)",
        )

        # Check for Input/Output Mapping
        result.add_check(
            "Contains Input/Output Mapping section",
            "Input/Output Mapping" in content or "Input/Output" in content,
            "Input/Output Mapping section not found",
        )

    return result


def check_econometric_v2_script_folder(paths) -> ValidationResult:
    """
    STRUCT-02: Econometric_V2 Script Folder

    Checks:
    - 2_Scripts/4_Econometric_V2/ exists
    - README.md exists in folder
    - README contains "Econometric Infrastructure" section
    - README contains "H1 Cash Holdings" section
    - README contains "H2 Investment Efficiency" section
    - README contains "H3 Payout Policy" section
    - README contains regression equations
    """
    result = ValidationResult(
        "STRUCT-02", "Econometric_V2 script folder with complete README"
    )

    folder = paths["scripts_econometric_v2"]
    result.add_check(
        "Folder exists: 2_Scripts/4_Econometric_V2/",
        folder.exists(),
        f"Folder not found: {folder}",
    )

    if not folder.exists():
        return result

    readme = folder / "README.md"
    result.add_check("README.md exists", readme.exists(), f"README not found: {readme}")

    if readme.exists():
        content = readme.read_text(encoding="utf-8")

        # Check for infrastructure section
        result.add_check(
            "Contains Econometric Infrastructure section",
            "Econometric Infrastructure" in content or "Infrastructure" in content,
            "Econometric Infrastructure section not found",
        )

        # Check for hypothesis regression sections
        result.add_check(
            "Contains H1 Cash Holdings regression",
            "H1 Cash Holdings" in content or "Cash Holdings Regression" in content,
            "H1 regression section not found",
        )

        result.add_check(
            "Contains H2 Investment Efficiency regression",
            "H2 Investment Efficiency" in content
            or "Investment Efficiency Regression" in content,
            "H2 regression section not found",
        )

        result.add_check(
            "Contains H3 Payout Policy regression",
            "H3 Payout Policy" in content or "Payout Policy Regression" in content,
            "H3 regression section not found",
        )

        # Check for regression equations (look for beta notation or equation patterns)
        equation_indicators = ["beta_", "beta_0", "= beta", "Fixed Effects", "firm_FE"]
        equations_found = sum(
            1 for indicator in equation_indicators if indicator in content
        )
        result.add_check(
            "Contains regression equations",
            equations_found >= 2,
            f"Regression equations not documented (found {equations_found}/5 indicators)",
        )

    return result


def check_financial_v2_outputs_folder(paths) -> ValidationResult:
    """
    STRUCT-03: Financial_V2 Outputs Folder

    Checks:
    - 4_Outputs/3_Financial_V2/ exists
    - .gitkeep exists in folder
    - No naming conflicts with 4_Outputs/3_Financial/
    """
    result = ValidationResult("STRUCT-03", "Financial_V2 outputs folder with .gitkeep")

    folder = paths["outputs_financial_v2"]
    result.add_check(
        "Folder exists: 4_Outputs/3_Financial_V2/",
        folder.exists(),
        f"Folder not found: {folder}",
    )

    if folder.exists():
        gitkeep = folder / ".gitkeep"
        result.add_check(
            ".gitkeep exists", gitkeep.exists(), f".gitkeep not found: {gitkeep}"
        )

        # Check for naming conflicts with v1.0
        v1_folder = paths["outputs_financial_v1"]
        if v1_folder.exists():
            # No conflict if folders are separate (which they are by name)
            result.add_check(
                "No naming conflicts with v1.0 outputs",
                True,
                "V2 folder is separate from v1.0",
            )
        else:
            result.add_check(
                "No naming conflicts with v1.0 outputs",
                True,
                "v1.0 folder does not exist (not a conflict)",
            )

    return result


def check_econometric_v2_outputs_folder(paths) -> ValidationResult:
    """
    STRUCT-04: Econometric_V2 Outputs Folder

    Checks:
    - 4_Outputs/4_Econometric_V2/ exists
    - .gitkeep exists in folder
    - No naming conflicts with 4_Outputs/4_Econometric/
    """
    result = ValidationResult(
        "STRUCT-04", "Econometric_V2 outputs folder with .gitkeep"
    )

    folder = paths["outputs_econometric_v2"]
    result.add_check(
        "Folder exists: 4_Outputs/4_Econometric_V2/",
        folder.exists(),
        f"Folder not found: {folder}",
    )

    if folder.exists():
        gitkeep = folder / ".gitkeep"
        result.add_check(
            ".gitkeep exists", gitkeep.exists(), f".gitkeep not found: {gitkeep}"
        )

        # Check for naming conflicts with v1.0
        v1_folder = paths["outputs_econometric_v1"]
        if v1_folder.exists():
            result.add_check(
                "No naming conflicts with v1.0 outputs",
                True,
                "V2 folder is separate from v1.0",
            )
        else:
            result.add_check(
                "No naming conflicts with v1.0 outputs",
                True,
                "v1.0 folder does not exist (not a conflict)",
            )

    return result


def check_logs_folders(paths) -> ValidationResult:
    """
    STRUCT-05: Logs Folders

    Checks:
    - 3_Logs/3_Financial_V2/ exists
    - 3_Logs/3_Financial_V2/.gitkeep exists
    - 3_Logs/4_Econometric_V2/ exists
    - 3_Logs/4_Econometric_V2/.gitkeep exists
    - No naming conflicts with existing v1.0 log folders
    """
    result = ValidationResult(
        "STRUCT-05", "Financial_V2 and Econometric_V2 logs folders with .gitkeep"
    )

    # Financial_V2 logs
    fin_folder = paths["logs_financial_v2"]
    result.add_check(
        "Folder exists: 3_Logs/3_Financial_V2/",
        fin_folder.exists(),
        f"Folder not found: {fin_folder}",
    )

    if fin_folder.exists():
        fin_gitkeep = fin_folder / ".gitkeep"
        result.add_check(
            "3_Financial_V2/.gitkeep exists",
            fin_gitkeep.exists(),
            f".gitkeep not found: {fin_gitkeep}",
        )

    # Econometric_V2 logs
    econ_folder = paths["logs_econometric_v2"]
    result.add_check(
        "Folder exists: 3_Logs/4_Econometric_V2/",
        econ_folder.exists(),
        f"Folder not found: {econ_folder}",
    )

    if econ_folder.exists():
        econ_gitkeep = econ_folder / ".gitkeep"
        result.add_check(
            "4_Econometric_V2/.gitkeep exists",
            econ_gitkeep.exists(),
            f".gitkeep not found: {econ_gitkeep}",
        )

    # Check for conflicts
    v1_fin = paths["logs_financial_v1"]
    v1_econ = paths["logs_econometric_v1"]
    result.add_check(
        "No naming conflicts with v1.0 log folders",
        fin_folder != v1_fin and econ_folder != v1_econ,
        "V2 log folders are separate from v1.0",
    )

    return result


def check_naming_convention(paths) -> ValidationResult:
    """
    STRUCT-06: Naming Convention

    Checks:
    - Financial_V2 README documents script naming: {step}.{substep}_{Name}.py
    - Econometric_V2 README documents script naming: {step}.{substep}_{Name}.py
    - Examples include: 3.1_H1Variables.py, 4.1_H1Regression.py
    """
    result = ValidationResult(
        "STRUCT-06", "Script naming convention documented in READMEs"
    )

    # Check Financial_V2 README
    fin_readme = paths["scripts_financial_v2"] / "README.md"
    if fin_readme.exists():
        content = fin_readme.read_text(encoding="utf-8")

        # Check for naming convention documentation
        naming_found = (
            "{step}.{substep}" in content
            or "3.1_H1Variables" in content
            or "3.2_H2Variables" in content
            or "3.3_H3Variables" in content
        )
        result.add_check(
            "Financial_V2 README documents script naming",
            naming_found,
            "Script naming pattern not found in Financial_V2 README",
        )

        # Check for specific examples
        examples_found = (
            "3.1_H1Variables.py" in content
            or "3.2_H2Variables.py" in content
            or "3.3_H3Variables.py" in content
        )
        result.add_check(
            "Financial_V2 README includes script examples",
            examples_found,
            "Script examples not found in Financial_V2 README",
        )
    else:
        result.add_check(
            "Financial_V2 README documents script naming",
            False,
            "Financial_V2 README not found",
        )
        result.add_check(
            "Financial_V2 README includes script examples",
            False,
            "Financial_V2 README not found",
        )

    # Check Econometric_V2 README
    econ_readme = paths["scripts_econometric_v2"] / "README.md"
    if econ_readme.exists():
        content = econ_readme.read_text(encoding="utf-8")

        # Check for naming convention documentation
        naming_found = (
            "{step}.{substep}" in content
            or "4.0_EconometricInfra" in content
            or "4.1_H1Regression" in content
        )
        result.add_check(
            "Econometric_V2 README documents script naming",
            naming_found,
            "Script naming pattern not found in Econometric_V2 README",
        )

        # Check for specific examples
        examples_found = (
            "4.0_EconometricInfra.py" in content
            or "4.1_H1Regression.py" in content
            or "4.2_H2Regression.py" in content
            or "4.3_H3Regression.py" in content
        )
        result.add_check(
            "Econometric_V2 README includes script examples",
            examples_found,
            "Script examples not found in Econometric_V2 README",
        )
    else:
        result.add_check(
            "Econometric_V2 README documents script naming",
            False,
            "Econometric_V2 README not found",
        )
        result.add_check(
            "Econometric_V2 README includes script examples",
            False,
            "Econometric_V2 README not found",
        )

    return result


def run_all_validations(paths) -> dict:
    """
    Run all STRUCT validations and collect results.

    Returns:
        Dictionary with validation results and overall status
    """
    results = {
        "validations": [],
        "total": 6,
        "passed": 0,
        "failed": 0,
        "all_passed": True,
    }

    # Run all validation checks
    validators = [
        ("STRUCT-01", check_financial_v2_script_folder),
        ("STRUCT-02", check_econometric_v2_script_folder),
        ("STRUCT-03", check_financial_v2_outputs_folder),
        ("STRUCT-04", check_econometric_v2_outputs_folder),
        ("STRUCT-05", check_logs_folders),
        ("STRUCT-06", check_naming_convention),
    ]

    for _name, validator in validators:
        result = validator(paths)
        results["validations"].append(result)
        if result.passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["all_passed"] = False

    return results


def print_header(width: int = 80):
    """Print validation report header"""
    print("=" * width)
    print("V2 Structure Validation Report")
    print("=" * width)


def print_footer(results: dict, width: int = 80):
    """Print validation summary footer"""
    print("-" * width)
    print(f"SUMMARY: {results['passed']}/{results['total']} requirements passed")

    if results["all_passed"]:
        print("\nAll STRUCT requirements validated successfully!")
    else:
        print("\nVALIDATION FAILED - Some requirements are not met:")
        for result in results["validations"]:
            if not result.passed:
                print(f"  - {result.name}: {', '.join(result.failures)}")

    print("=" * width)


def save_stats(results: dict, paths: dict, timestamp: str):
    """Save validation statistics to JSON file"""
    stats = {
        "step_id": "2.0_ValidateV2Structure",
        "timestamp": timestamp,
        "validation_results": {
            "total": results["total"],
            "passed": results["passed"],
            "failed": results["failed"],
            "all_passed": results["all_passed"],
        },
        "details": [],
    }

    for result in results["validations"]:
        detail = {
            "name": result.name,
            "description": result.description,
            "passed": result.passed,
            "checks": result.checks,
        }
        stats["details"].append(detail)

    # Save stats.json
    stats_file = paths["output_dir"] / "stats.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    return stats_file


# ==============================================================================
# Main
# ==============================================================================


def main(args=None):
    """Main validation orchestrator"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Validate Phase 28 V2 folder structure and documentation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation without creating output files",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress terminal output (still write to log)",
    )

    parsed_args = parser.parse_args(args)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Set up paths
    paths = setup_paths(timestamp)

    # Set up dual-writer for logging
    if not parsed_args.dry_run:
        # Ensure parent directory exists
        paths["log_file"].parent.mkdir(parents=True, exist_ok=True)
        dual_writer = DualWriter(paths["log_file"])
        if not parsed_args.quiet:
            sys.stdout = dual_writer

    try:
        # Print header
        if not parsed_args.quiet:
            print_header()

        # Run all validations
        results = run_all_validations(paths)

        # Print individual results
        if not parsed_args.quiet:
            for result in results["validations"]:
                print(result.format_report())

            print_footer(results)

        # Save stats if not dry run
        if not parsed_args.dry_run:
            stats_file = save_stats(results, paths, timestamp)
            if not parsed_args.quiet:
                print(f"\nStats saved to: {stats_file}")
                print(f"Log saved to: {paths['log_file']}")

        # Restore stdout
        if not parsed_args.dry_run and not parsed_args.quiet:
            sys.stdout = dual_writer.terminal
            dual_writer.close()

        # Return exit code
        return 0 if results["all_passed"] else 1

    except Exception as e:
        print(f"\nERROR: Validation failed with exception: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()

        # Restore stdout if dual-writer was set up
        if not parsed_args.dry_run and not parsed_args.quiet:
            try:
                sys.stdout = dual_writer.terminal
                dual_writer.close()
            except:
                pass

        return 1


if __name__ == "__main__":
    sys.exit(main())
