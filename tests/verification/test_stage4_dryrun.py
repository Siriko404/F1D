"""
Stage 4 (Econometric) dry-run verification tests.

Tests that all Stage 4 econometric analysis scripts:
1. Can be imported without errors
2. Have proper --dry-run flag support
3. Execute dry-run validation without exceptions
4. Follow the expected module structure (f1d.shared.* imports)

Stage 4 Scripts (econometric/):
    - run_h0_3_ceo_clarity_extended.py
    - run_h1_cash_holdings.py
    - run_h1_1_cash_tsimm.py
    - run_h1_1b_cash_tsimm_binary.py
    - run_h1_2_cash_constraint.py
    - run_h4_leverage.py
    - run_h5b_wang_disp.py
    - run_h7_illiquidity.py
    - run_h9_takeover_hazards.py (survival analysis)
    - run_h11_prisk_uncertainty.py
    - run_h11_prisk_uncertainty_lag.py
    - run_h11_prisk_uncertainty_lead.py
    - run_h12_payout.py
    - run_h13_1_competition.py
    - run_h13_capex.py
    - run_h14_bidask_spread.py
    - run_h16_rd_sales.py
    - run_h17_repurchase_intensity.py
    - run_h18_cccl_received.py

Dependencies:
    - Scripts depend on Stage 3 and Stage 2 outputs
    - run_h9_takeover_hazards.py uses lifelines for survival analysis
"""

import os
import subprocess
from pathlib import Path

import pytest

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent.parent

# All Stage 4 econometric scripts to test (excluding __init__.py)
STAGE4_ALL_SCRIPTS = [
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
]


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


class TestStage4ScriptImports:
    """Test that Stage 4 scripts can be imported."""

    @pytest.mark.parametrize("script", STAGE4_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_exists(self, script: str):
        """Verify each script file exists."""
        script_path = REPO_ROOT / script
        assert script_path.exists(), f"Script not found: {script_path}"

    @pytest.mark.parametrize("script", STAGE4_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
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


class TestStage4DryRunFlags:
    """Test that Stage 4 scripts support --dry-run flag."""

    @pytest.mark.parametrize("script", STAGE4_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_dryrun_flag_accepted(self, script: str, subprocess_env: dict):
        """Test that --dry-run flag is accepted by each script."""
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


class TestStage4ModuleStructure:
    """Test that Stage 4 scripts use correct module structure."""

    @pytest.mark.parametrize("script", STAGE4_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_uses_f1d_shared_imports(self, script: str):
        """Verify scripts use f1d.shared.* namespace imports."""
        script_path = REPO_ROOT / script
        content = script_path.read_text(encoding="utf-8")

        # Check for correct import pattern
        assert "from f1d.shared" in content or "import f1d.shared" in content, (
            f"Script {script} should use f1d.shared.* imports"
        )

    @pytest.mark.parametrize("script", STAGE4_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
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


class TestStage4ArgumentParsing:
    """Test that Stage 4 scripts have proper CLI argument parsing."""

    @pytest.mark.parametrize("script", STAGE4_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_help_flag_works(self, script: str, subprocess_env: dict):
        """Test that --help flag works for each script."""
        import sys

        script_path = REPO_ROOT / script
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            env=subprocess_env,
            timeout=30,
            cwd=str(REPO_ROOT),
        )

        # --help should exit with 0 and show usage
        if result.returncode != 0:
            # Check if it's a Unicode encoding error (Windows console limitation)
            if "UnicodeEncodeError" in result.stderr:
                pytest.skip(
                    f"Unicode encoding error in {script} help text (Windows console limitation)"
                )
            assert result.returncode == 0, (
                f"--help failed for {script}: {result.stderr}"
            )

        assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower(), (
            f"--help should show usage for {script}"
        )


class TestStage4HypothesisMapping:
    """Test that hypothesis regression scripts are correctly mapped."""

    def test_h1_regression_exists(self):
        """Verify H1 (Cash Holdings) regression script exists."""
        h1_path = REPO_ROOT / "src/f1d/econometric/run_h1_cash_holdings.py"
        assert h1_path.exists(), "H1 Cash Holdings regression script should exist"

    def test_h4_regression_exists(self):
        """Verify H4 (Leverage Discipline) regression script exists."""
        h4_path = REPO_ROOT / "src/f1d/econometric/run_h4_leverage.py"
        assert h4_path.exists(), "H4 Leverage Discipline regression script should exist"

    def test_h7_regression_exists(self):
        """Verify H7 (Illiquidity) regression script exists."""
        h7_path = REPO_ROOT / "src/f1d/econometric/run_h7_illiquidity.py"
        assert h7_path.exists(), "H7 Illiquidity regression script should exist"


class TestStage4SurvivalAnalysis:
    """Test survival analysis specific scripts (H9 Takeover Hazards)."""

    def test_takeover_hazards_script_exists(self):
        """Verify run_h9_takeover_hazards.py script exists."""
        haz_path = REPO_ROOT / "src/f1d/econometric/run_h9_takeover_hazards.py"
        assert haz_path.exists(), "Takeover Hazards script should exist"

    def test_takeover_hazards_uses_lifelines(self):
        """Verify run_h9_takeover_hazards.py uses lifelines for Cox PH."""
        haz_path = REPO_ROOT / "src/f1d/econometric/run_h9_takeover_hazards.py"
        content = haz_path.read_text(encoding="utf-8")

        # Check for lifelines import
        assert "lifelines" in content, "TakeoverHazards should import lifelines"
        assert "CoxPHFitter" in content, "TakeoverHazards should use CoxPHFitter"

    def test_takeover_hazards_has_cause_specific_hazards(self):
        """Verify run_h9_takeover_hazards.py uses cause-specific Cox hazards.

        As per 77-03 decision: Using cause-specific Cox hazards instead of
        FineGrayAFTFitter (not available in lifelines 0.30.0).
        """
        haz_path = REPO_ROOT / "src/f1d/econometric/run_h9_takeover_hazards.py"
        content = haz_path.read_text(encoding="utf-8")

        # Verify it uses CoxPHFitter
        assert "CoxPHFitter" in content, "Should use CoxPHFitter for survival analysis"

        # Verify it mentions cause-specific hazards approach
        assert (
            "cause-specific" in content.lower() or "cause_specific" in content.lower()
        ), "Should mention cause-specific hazards approach"
