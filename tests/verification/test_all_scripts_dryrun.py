"""
Full pipeline dry-run verification tests.

Tests that ALL scripts in the F1D pipeline:
1. Can be imported without ImportError
2. Follow the expected module structure (f1d.shared.* imports)
3. Don't manipulate sys.path (ROADMAP compliance)
4. Support --dry-run or --help flags without unexpected errors

This is an aggregate test that covers all 41+ scripts across all 4 stages.

Pipeline Structure:
    Stage 1 (Sample): 5 scripts - Build sample manifest
    Stage 2 (Text): 4 scripts - Process transcripts
    Stage 3 (Financial): 17 scripts - Build financial features
    Stage 4 (Econometric): 19 scripts - Run regressions

Total: 45+ scripts

Usage:
    pytest tests/verification/test_all_scripts_dryrun.py -v
    pytest tests/verification/test_all_scripts_dryrun.py -m slow -v
"""

import os
import subprocess
from pathlib import Path
from typing import List

import pytest

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent.parent

# All scripts organized by stage
ALL_SCRIPTS: List[str] = [
    # Stage 1: Sample Construction (5 scripts)
    "src/f1d/sample/1.0_BuildSampleManifest.py",
    "src/f1d/sample/1.1_CleanMetadata.py",
    "src/f1d/sample/1.2_LinkEntities.py",
    "src/f1d/sample/1.3_BuildTenureMap.py",
    "src/f1d/sample/1.4_AssembleManifest.py",

    # Stage 2: Text Processing (4 scripts)
    "src/f1d/text/tokenize_and_count.py",
    "src/f1d/text/construct_variables.py",
    "src/f1d/text/report_step2.py",
    "src/f1d/text/verify_step2.py",

    # Stage 3 V1: Financial Features (4 scripts)
    "src/f1d/financial/v1/3.0_BuildFinancialFeatures.py",
    "src/f1d/financial/v1/3.1_FirmControls.py",
    "src/f1d/financial/v1/3.2_MarketVariables.py",
    "src/f1d/financial/v1/3.3_EventFlags.py",

    # Stage 3 V2: Hypothesis Variables (13 scripts)
    "src/f1d/financial/v2/3.1_H1Variables.py",
    "src/f1d/financial/v2/3.2_H2Variables.py",
    "src/f1d/financial/v2/3.2a_AnalystDispersionPatch.py",
    "src/f1d/financial/v2/3.3_H3Variables.py",
    "src/f1d/financial/v2/3.5_H5Variables.py",
    "src/f1d/financial/v2/3.6_H6Variables.py",
    "src/f1d/financial/v2/3.7_H7IlliquidityVariables.py",
    "src/f1d/financial/v2/3.8_H8TakeoverVariables.py",
    "src/f1d/financial/v2/3.9_H2_BiddleInvestmentResidual.py",
    "src/f1d/financial/v2/3.10_H2_PRiskUncertaintyMerge.py",
    "src/f1d/financial/v2/3.11_H9_StyleFrozen.py",
    "src/f1d/financial/v2/3.12_H9_PRiskFY.py",
    "src/f1d/financial/v2/3.13_H9_AbnormalInvestment.py",

    # Stage 4 V1: Econometric Analysis (8 scripts)
    "src/f1d/econometric/v1/4.1_EstimateCeoClarity.py",
    "src/f1d/econometric/v1/4.1.1_EstimateCeoClarity_CeoSpecific.py",
    "src/f1d/econometric/v1/4.1.2_EstimateCeoClarity_Extended.py",
    "src/f1d/econometric/v1/4.1.3_EstimateCeoClarity_Regime.py",
    "src/f1d/econometric/v1/4.1.4_EstimateCeoTone.py",
    "src/f1d/econometric/v1/4.2_LiquidityRegressions.py",
    "src/f1d/econometric/v1/4.3_TakeoverHazards.py",
    "src/f1d/econometric/v1/4.4_GenerateSummaryStats.py",

    # Stage 4 V2: Hypothesis Regressions (11 scripts)
    "src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py",
    "src/f1d/econometric/v2/4.2_H2InvestmentEfficiencyRegression.py",
    "src/f1d/econometric/v2/4.3_H3PayoutPolicyRegression.py",
    "src/f1d/econometric/v2/4.4_H4_LeverageDiscipline.py",
    "src/f1d/econometric/v2/4.5_H5DispersionRegression.py",
    "src/f1d/econometric/v2/4.6_H6CCCLRegression.py",
    "src/f1d/econometric/v2/4.7_H7IlliquidityRegression.py",
    "src/f1d/econometric/v2/4.8_H8TakeoverRegression.py",
    "src/f1d/econometric/v2/4.9_CEOFixedEffects.py",
    "src/f1d/econometric/v2/4.10_H2_PRiskUncertainty_Investment.py",
    "src/f1d/econometric/v2/4.11_H9_Regression.py",
]

# Count by stage
SCRIPT_COUNTS = {
    "Stage 1": 5,
    "Stage 2": 4,
    "Stage 3 V1": 4,
    "Stage 3 V2": 13,
    "Stage 4 V1": 8,
    "Stage 4 V2": 11,
    "Total": 45,
}


@pytest.fixture(scope="module")
def subprocess_env():
    """
    Environment for subprocess calls with PYTHONPATH set.

    Required for scripts to import f1d.shared.* modules.
    """
    return {
        "PYTHONPATH": str(REPO_ROOT / "src" / "f1d"),
        **dict(os.environ),  # Preserve existing environment
    }


class TestAllScriptsExist:
    """Verify all expected scripts exist."""

    def test_script_count(self):
        """Verify we have the expected number of scripts."""
        actual_count = len(ALL_SCRIPTS)
        expected_count = SCRIPT_COUNTS["Total"]
        assert actual_count == expected_count, \
            f"Expected {expected_count} scripts, found {actual_count}"

    @pytest.mark.parametrize("script", ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_exists(self, script: str):
        """Verify each script file exists."""
        script_path = REPO_ROOT / script
        assert script_path.exists(), f"Script not found: {script_path}"


class TestAllScriptsImport:
    """Test that all scripts can be imported."""

    @pytest.mark.parametrize("script", ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_importable(self, script: str, subprocess_env: dict):
        """Test that script can be imported without errors."""
        import sys

        script_path = REPO_ROOT / script
        result = subprocess.run(
            [sys.executable, "-c", f"import runpy; runpy.run_path('{script_path}')"],
            capture_output=True,
            text=True,
            env=subprocess_env,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        # Script may fail on missing inputs, but should not have import errors
        assert "ImportError" not in result.stderr, f"Import error in {script}: {result.stderr}"
        assert "ModuleNotFoundError" not in result.stderr, f"Module not found in {script}: {result.stderr}"


class TestAllScriptsRoadmapCompliance:
    """Test ROADMAP compliance for all scripts."""

    @pytest.mark.parametrize("script", ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_uses_f1d_shared_imports(self, script: str):
        """Verify scripts use f1d.shared.* namespace imports."""
        script_path = REPO_ROOT / script
        content = script_path.read_text(encoding="utf-8")

        # Check for correct import pattern
        assert "from f1d.shared" in content or "import f1d.shared" in content, \
            f"Script {script} should use f1d.shared.* imports"

    @pytest.mark.parametrize("script", ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_no_sys_path_manipulation(self, script: str):
        """Verify scripts don't manipulate sys.path (ROADMAP compliance)."""
        script_path = REPO_ROOT / script
        content = script_path.read_text(encoding="utf-8")

        # Check for forbidden sys.path manipulation
        forbidden_patterns = [
            "sys.path.insert",
            "sys.path.append",
        ]

        for pattern in forbidden_patterns:
            assert pattern not in content, \
                f"Script {script} should not use {pattern} (use f1d.shared.* imports)"


class TestAllScriptsDryRun:
    """Test that all scripts support dry-run validation."""

    @pytest.mark.slow
    @pytest.mark.parametrize("script", ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_dryrun_no_unexpected_errors(self, script: str, subprocess_env: dict):
        """Test that --dry-run flag doesn't cause unexpected errors.

        Scripts may exit with error if prerequisites are missing,
        but should not crash with code errors.
        """
        import sys

        script_path = REPO_ROOT / script
        result = subprocess.run(
            [sys.executable, str(script_path), "--dry-run"],
            capture_output=True,
            text=True,
            env=subprocess_env,
            timeout=60,
            cwd=str(REPO_ROOT),
        )

        # Check for unexpected errors (not prerequisite failures)
        stderr_lower = result.stderr.lower()
        stdout_lower = result.stdout.lower()

        # These errors indicate code problems, not missing inputs
        unexpected_errors = [
            "syntaxerror",
            "nameerror",
            "typeerror",
            "attributeerror",
            "indexerror",
            "keyerror",
            "zerodivisionerror",
        ]

        for error in unexpected_errors:
            assert error not in stderr_lower, f"Unexpected {error} in {script}: {result.stderr}"
            assert error not in stdout_lower, f"Unexpected {error} in {script}: {result.stdout}"


class TestPipelineSummary:
    """Summary tests for the full pipeline."""

    def test_pipeline_script_counts(self):
        """Verify pipeline structure matches expectations."""
        # Verify stage counts
        stage1_count = len([s for s in ALL_SCRIPTS if "/sample/" in s])
        stage2_count = len([s for s in ALL_SCRIPTS if "/text/" in s])
        stage3_count = len([s for s in ALL_SCRIPTS if "/financial/" in s])
        stage4_count = len([s for s in ALL_SCRIPTS if "/econometric/" in s])

        assert stage1_count == SCRIPT_COUNTS["Stage 1"], \
            f"Expected {SCRIPT_COUNTS['Stage 1']} Stage 1 scripts, found {stage1_count}"
        assert stage2_count == SCRIPT_COUNTS["Stage 2"], \
            f"Expected {SCRIPT_COUNTS['Stage 2']} Stage 2 scripts, found {stage2_count}"
        assert stage3_count == SCRIPT_COUNTS["Stage 3 V1"] + SCRIPT_COUNTS["Stage 3 V2"], \
            f"Expected {SCRIPT_COUNTS['Stage 3 V1'] + SCRIPT_COUNTS['Stage 3 V2']} Stage 3 scripts, found {stage3_count}"
        assert stage4_count == SCRIPT_COUNTS["Stage 4 V1"] + SCRIPT_COUNTS["Stage 4 V2"], \
            f"Expected {SCRIPT_COUNTS['Stage 4 V1'] + SCRIPT_COUNTS['Stage 4 V2']} Stage 4 scripts, found {stage4_count}"

    def test_all_scripts_use_subprocess_pattern(self):
        """Verify scripts can be run via subprocess for integration tests."""
        # This is a design verification test
        for script in ALL_SCRIPTS:
            script_path = REPO_ROOT / script
            assert script_path.suffix == ".py", f"Script {script} should be a Python file"
            content = script_path.read_text(encoding="utf-8")
            assert "if __name__" in content, f"Script {script} should have if __name__ guard"

    def test_zero_import_errors_summary(self, subprocess_env: dict):
        """Summary test: verify zero import errors across all scripts."""
        import sys

        failed_scripts = []

        for script in ALL_SCRIPTS:
            script_path = REPO_ROOT / script
            result = subprocess.run(
                [sys.executable, "-c", f"import runpy; runpy.run_path('{script_path}')"],
                capture_output=True,
                text=True,
                env=subprocess_env,
                timeout=30,
                cwd=str(REPO_ROOT),
            )

            if "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr:
                failed_scripts.append(script)

        assert len(failed_scripts) == 0, \
            f"Scripts with import errors: {failed_scripts}"
