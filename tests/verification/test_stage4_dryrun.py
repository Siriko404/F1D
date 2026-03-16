"""
Stage 4 (Econometric) dry-run verification tests.

Tests that all Stage 4 econometric analysis scripts:
1. Can be imported without errors
2. Have proper --dry-run flag support
3. Execute dry-run validation without exceptions
4. Follow the expected module structure (f1d.shared.* imports)

Stage 4 Scripts (econometric/):
    - run_h0_1_manager_clarity.py
    - run_h0_3_ceo_clarity_extended.py
    - run_h0_4_ceo_clarity_regime.py
    - run_h0_5_ceo_tone.py
    - run_h1_cash_holdings.py
    - run_h2_investment.py
    - run_h3_payout_policy.py
    - run_h4_leverage.py
    - run_h5_dispersion.py
    - run_h6_cccl.py
    - run_h7_illiquidity.py
    - run_h9_takeover_hazards.py (survival analysis)

Dependencies:
    - Scripts depend on Step 3.x and Step 2.2 outputs
    - run_h9_takeover_hazards.py uses lifelines for survival analysis
"""

import os
import subprocess
from pathlib import Path

import pytest

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent.parent

# Stage 4 V1 econometric scripts to test (excluding __init__.py)

# Stage 4 V2 econometric scripts to test (excluding __init__.py)

# All Stage 4 scripts combined
STAGE4_ALL_SCRIPTS = [
    "src/f1d/econometric/run_h0_1_manager_clarity.py",
    "src/f1d/econometric/run_h0_3_ceo_clarity_extended.py",
    "src/f1d/econometric/run_h0_4_ceo_clarity_regime.py",
    "src/f1d/econometric/run_h0_5_ceo_tone.py",
    "src/f1d/econometric/run_h1_cash_holdings.py",
    "src/f1d/econometric/run_h2_investment.py",
    "src/f1d/econometric/run_h3_payout_policy.py",
    "src/f1d/econometric/run_h4_leverage.py",
    "src/f1d/econometric/run_h5_dispersion.py",
    "src/f1d/econometric/run_h6_cccl.py",
    "src/f1d/econometric/run_h7_illiquidity.py",
    "src/f1d/econometric/run_h9_takeover_hazards.py",
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
    """Test that Stage 4 V1 scripts can be imported."""

    @pytest.mark.parametrize("script", STAGE4_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_exists(self, script: str):
        """Verify each V1 script file exists."""
        script_path = REPO_ROOT / script
        assert script_path.exists(), f"Script not found: {script_path}"

    @pytest.mark.parametrize("script", STAGE4_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_importable(self, script: str, subprocess_env: dict):
        """Test that V1 script can be imported without errors."""
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
        # Note: Some scripts may have Unicode in help text that fails on Windows
        # This is a known issue with 4.9_CEOFixedEffects.py (Dzieliński)
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

    def test_h2_regression_exists(self):
        """Verify H2 (Investment Efficiency) regression script exists."""
        h2_path = REPO_ROOT / "src/f1d/econometric/run_h2_investment.py"
        assert h2_path.exists(), (
            "H2 Investment Efficiency regression script should exist"
        )

    def test_h3_regression_exists(self):
        """Verify H3 (Payout Policy) regression script exists."""
        h3_path = REPO_ROOT / "src/f1d/econometric/run_h3_payout_policy.py"
        assert h3_path.exists(), "H3 Payout Policy regression script should exist"

    def test_h4_regression_exists(self):
        """Verify H4 (Leverage Discipline) regression script exists."""
        h4_path = REPO_ROOT / "src/f1d/econometric/run_h4_leverage.py"
        assert h4_path.exists(), "H4 Leverage Discipline regression script should exist"

    def test_h5_regression_exists(self):
        """Verify H5 (Dispersion) regression script exists."""
        h5_path = REPO_ROOT / "src/f1d/econometric/run_h5_dispersion.py"
        assert h5_path.exists(), "H5 Dispersion regression script should exist"

    def test_h6_regression_exists(self):
        """Verify H6 (CCC&L) regression script exists."""
        h6_path = REPO_ROOT / "src/f1d/econometric/run_h6_cccl.py"
        assert h6_path.exists(), "H6 CCC&L regression script should exist"

    def test_h7_regression_exists(self):
        """Verify H7 (Illiquidity) regression script exists."""
        h7_path = REPO_ROOT / "src/f1d/econometric/run_h7_illiquidity.py"
        assert h7_path.exists(), "H7 Illiquidity regression script should exist"


class TestStage4SurvivalAnalysis:
    """Test survival analysis specific scripts (4.3_TakeoverHazards)."""

    def test_takeover_hazards_script_exists(self):
        """Verify 4.3_TakeoverHazards.py script exists."""
        haz_path = REPO_ROOT / "src/f1d/econometric/run_h9_takeover_hazards.py"
        assert haz_path.exists(), "Takeover Hazards script should exist"

    def test_takeover_hazards_uses_lifelines(self):
        """Verify 4.3_TakeoverHazards.py uses lifelines for Cox PH."""
        haz_path = REPO_ROOT / "src/f1d/econometric/run_h9_takeover_hazards.py"
        content = haz_path.read_text(encoding="utf-8")

        # Check for lifelines import
        assert "lifelines" in content, "TakeoverHazards should import lifelines"
        assert "CoxPHFitter" in content, "TakeoverHazards should use CoxPHFitter"

    def test_takeover_hazards_has_cause_specific_hazards(self):
        """Verify 4.3_TakeoverHazards.py uses cause-specific Cox hazards.

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


class TestStage4CeoFixedEffects:
    """Test CEO Fixed Effects script (H0.4 CEO Clarity Regime)."""

    def test_ceo_fixed_effects_script_exists(self):
        """Verify H0.4 CEO Clarity Regime script exists."""
        cfe_path = REPO_ROOT / "src/f1d/econometric/run_h0_4_ceo_clarity_regime.py"
        assert cfe_path.exists(), "CEO Fixed Effects script should exist"

    def test_ceo_fixed_effects_uses_statsmodels(self):
        """Verify H0.4 CEO Clarity Regime uses statsmodels for regression."""
        cfe_path = REPO_ROOT / "src/f1d/econometric/run_h0_4_ceo_clarity_regime.py"
        content = cfe_path.read_text(encoding="utf-8")

        # Check for statsmodels import
        assert "statsmodels" in content, "CEO Fixed Effects should import statsmodels"
