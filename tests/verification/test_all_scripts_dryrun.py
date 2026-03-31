"""
Full pipeline dry-run verification tests.

Tests that ALL scripts in the F1D pipeline:
1. Can be imported without ImportError
2. Follow the expected module structure (f1d.shared.* imports)
3. Don't manipulate sys.path (ROADMAP compliance)
4. Support --dry-run or --help flags without unexpected errors

Pipeline Structure:
    Stage 1 (Sample): 5 scripts - Build sample manifest
    Stage 2 (Text): 2 scripts - Process transcripts
    Stage 3 (Variables): 17 scripts - Build panel variables
    Stage 4 (Econometric): 21 scripts - Run regressions
    Reporting: 1 script - Generate summary stats

Total: 46 scripts

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
    # Stage 1 (Sample)
    "src/f1d/sample/build_sample_manifest.py",
    "src/f1d/sample/clean_metadata.py",
    "src/f1d/sample/link_entities.py",
    "src/f1d/sample/build_tenure_map.py",
    "src/f1d/sample/assemble_manifest.py",
    # Stage 2 (Text)
    "src/f1d/text/tokenize_transcripts.py",
    "src/f1d/text/build_linguistic_variables.py",
    # Stage 3 (Variables)
    "src/f1d/variables/build_h0_3_ceo_clarity_extended_panel.py",
    "src/f1d/variables/build_h1_cash_holdings_panel.py",
    "src/f1d/variables/build_h4_leverage_panel.py",
    "src/f1d/variables/build_h5b_wang_disp_panel.py",
    "src/f1d/variables/build_h7_illiquidity_panel.py",
    "src/f1d/variables/build_h9_takeover_panel.py",
    "src/f1d/variables/build_h11_prisk_uncertainty_panel.py",
    "src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py",
    "src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py",
    "src/f1d/variables/build_h12_payout_panel.py",
    "src/f1d/variables/build_h13_capex_panel.py",
    "src/f1d/variables/build_h14_bidask_spread_panel.py",
    "src/f1d/variables/build_h16_rd_sales_panel.py",
    "src/f1d/variables/build_h17_repurchase_intensity_panel.py",
    "src/f1d/variables/build_h18_cccl_received_panel.py",
    # Stage 4 (Econometric)
    "src/f1d/econometric/run_h0_3_ceo_clarity_extended.py",
    "src/f1d/econometric/run_h1_cash_holdings.py",
    "src/f1d/econometric/run_h1_1_cash_tsimm.py",
    "src/f1d/econometric/run_h1_1b_cash_tsimm_binary.py",
    "src/f1d/econometric/run_h1_2_cash_constraint.py",
    "src/f1d/econometric/run_h4_leverage.py",
    "src/f1d/econometric/run_h5b_wang_disp.py",
    "src/f1d/econometric/run_h7_illiquidity.py",
    "src/f1d/econometric/run_h9_takeover_hazards.py",
    "src/f1d/econometric/run_h11_prisk_uncertainty.py",
    "src/f1d/econometric/run_h11_prisk_uncertainty_lag.py",
    "src/f1d/econometric/run_h11_prisk_uncertainty_lead.py",
    "src/f1d/econometric/run_h12_payout.py",
    "src/f1d/econometric/run_h13_1_competition.py",
    "src/f1d/econometric/run_h13_capex.py",
    "src/f1d/econometric/run_h14_bidask_spread.py",
    "src/f1d/econometric/run_h16_rd_sales.py",
    "src/f1d/econometric/run_h17_repurchase_intensity.py",
    "src/f1d/econometric/run_h18_cccl_received.py",
    # Reporting
    "src/f1d/reporting/generate_summary_stats.py",
]

# Count by stage
SCRIPT_COUNTS = {
    "Stage 1": 5,
    "Stage 2": 2,
    "Stage 3": 17,
    "Stage 4": 21,
    "Reporting": 1,
    "Total": 46,
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
        assert actual_count == expected_count, (
            f"Expected {expected_count} scripts, found {actual_count}"
        )

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
        assert "ImportError" not in result.stderr, (
            f"Import error in {script}: {result.stderr}"
        )
        assert "ModuleNotFoundError" not in result.stderr, (
            f"Module not found in {script}: {result.stderr}"
        )


class TestAllScriptsRoadmapCompliance:
    """Test ROADMAP compliance for all scripts."""

    @pytest.mark.parametrize("script", ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_uses_f1d_shared_imports(self, script: str):
        """Verify scripts use f1d.shared.* namespace imports."""
        script_path = REPO_ROOT / script
        content = script_path.read_text(encoding="utf-8")

        # Check for correct import pattern
        assert "from f1d.shared" in content or "import f1d.shared" in content, (
            f"Script {script} should use f1d.shared.* imports"
        )

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
            assert pattern not in content, (
                f"Script {script} should not use {pattern} (use f1d.shared.* imports)"
            )


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
            assert error not in stderr_lower, (
                f"Unexpected {error} in {script}: {result.stderr}"
            )
            assert error not in stdout_lower, (
                f"Unexpected {error} in {script}: {result.stdout}"
            )


class TestPipelineSummary:
    """Summary tests for the full pipeline."""

    def test_pipeline_script_counts(self):
        """Verify pipeline structure matches expectations."""
        stage1_count = len([s for s in ALL_SCRIPTS if "/sample/" in s])
        stage2_count = len([s for s in ALL_SCRIPTS if "/text/" in s])
        stage3_count = len([s for s in ALL_SCRIPTS if "/variables/" in s])
        stage4_count = len([s for s in ALL_SCRIPTS if "/econometric/" in s])
        reporting_count = len([s for s in ALL_SCRIPTS if "/reporting/" in s])

        assert stage1_count == SCRIPT_COUNTS["Stage 1"], (
            f"Expected {SCRIPT_COUNTS['Stage 1']} Stage 1 scripts, found {stage1_count}"
        )
        assert stage2_count == SCRIPT_COUNTS["Stage 2"], (
            f"Expected {SCRIPT_COUNTS['Stage 2']} Stage 2 scripts, found {stage2_count}"
        )
        assert stage3_count == SCRIPT_COUNTS["Stage 3"], (
            f"Expected {SCRIPT_COUNTS['Stage 3']} Stage 3 scripts, found {stage3_count}"
        )
        assert stage4_count == SCRIPT_COUNTS["Stage 4"], (
            f"Expected {SCRIPT_COUNTS['Stage 4']} Stage 4 scripts, found {stage4_count}"
        )
        assert reporting_count == SCRIPT_COUNTS["Reporting"], (
            f"Expected {SCRIPT_COUNTS['Reporting']} Reporting scripts, found {reporting_count}"
        )

    def test_all_scripts_use_subprocess_pattern(self):
        """Verify scripts can be run via subprocess for integration tests."""
        # This is a design verification test
        for script in ALL_SCRIPTS:
            script_path = REPO_ROOT / script
            assert script_path.suffix == ".py", (
                f"Script {script} should be a Python file"
            )
            content = script_path.read_text(encoding="utf-8")
            assert "if __name__" in content, (
                f"Script {script} should have if __name__ guard"
            )

    def test_zero_import_errors_summary(self, subprocess_env: dict):
        """Summary test: verify zero import errors across all scripts."""
        import sys

        failed_scripts = []

        for script in ALL_SCRIPTS:
            script_path = REPO_ROOT / script
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    f"import runpy; runpy.run_path('{script_path}')",
                ],
                capture_output=True,
                text=True,
                env=subprocess_env,
                timeout=30,
                cwd=str(REPO_ROOT),
            )

            if "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr:
                failed_scripts.append(script)

        assert len(failed_scripts) == 0, f"Scripts with import errors: {failed_scripts}"
