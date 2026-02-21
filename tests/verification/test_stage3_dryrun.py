"""
Stage 3 (Financial) dry-run verification tests.

Tests that all Stage 3 financial feature scripts:
1. Can be imported without errors
2. Have proper --dry-run flag support
3. Execute dry-run validation without exceptions
4. Follow the expected module structure (f1d.shared.* imports)

Stage 3 V1 Scripts (financial/v1/):
    - 3.0_BuildFinancialFeatures.py (orchestrator)
    - 3.1_FirmControls.py
    - 3.2_MarketVariables.py
    - 3.3_EventFlags.py
    - 3.4_Utils.py (utility module)

Stage 3 V2 Scripts (financial/v2/ - Hypothesis H1-H9):
    - 3.1_H1Variables.py (Cash Holdings)
    - 3.2_H2Variables.py (Investment Efficiency)
    - 3.2a_AnalystDispersionPatch.py
    - 3.3_H3Variables.py (Payout Policy)
    - 3.5_H5Variables.py (Dispersion)
    - 3.6_H6Variables.py (CCC&L)
    - 3.7_H7IlliquidityVariables.py
    - 3.8_H8TakeoverVariables.py
    - 3.9_H2_BiddleInvestmentResidual.py
    - 3.10_H2_PRiskUncertaintyMerge.py
    - 3.11_H9_StyleFrozen.py
    - 3.12_H9_PRiskFY.py
    - 3.13_H9_AbnormalInvestment.py

Dependencies:
    - V1 scripts depend on Step 2.2 outputs
    - V2 scripts depend on Step 1.4 and Step 2.2 outputs
"""

import os
import subprocess
from pathlib import Path

import pytest

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent.parent

# Stage 3 V1 financial scripts to test (excluding __init__.py)

# Stage 3 V2 financial scripts to test (excluding __init__.py)

# All Stage 3 scripts combined
STAGE3_ALL_SCRIPTS = [
    "src/f1d/variables/build_ceo_clarity_extended_panel.py",
    "src/f1d/variables/build_ceo_clarity_panel.py",
    "src/f1d/variables/build_ceo_tone_panel.py",
    "src/f1d/variables/build_h1_cash_holdings_panel.py",
    "src/f1d/variables/build_h2_investment_panel.py",
    "src/f1d/variables/build_h3_payout_policy_panel.py",
    "src/f1d/variables/build_h4_leverage_panel.py",
    "src/f1d/variables/build_h5_dispersion_panel.py",
    "src/f1d/variables/build_h6_cccl_panel.py",
    "src/f1d/variables/build_h7_illiquidity_panel.py",
    "src/f1d/variables/build_h8_policy_risk_panel.py",
    "src/f1d/variables/build_manager_clarity_panel.py",
    "src/f1d/variables/build_takeover_panel.py",
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


class TestStage3ScriptImports:
    """Test that Stage 3 V1 scripts can be imported."""

    @pytest.mark.parametrize("script", STAGE3_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_exists(self, script: str):
        """Verify each V1 script file exists."""
        script_path = REPO_ROOT / script
        assert script_path.exists(), f"Script not found: {script_path}"

    @pytest.mark.parametrize("script", STAGE3_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
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
        assert "ImportError" not in result.stderr, f"Import error in {script}: {result.stderr}"
        assert "ModuleNotFoundError" not in result.stderr, f"Module not found in {script}: {result.stderr}"




class TestStage3DryRunFlags:
    """Test that Stage 3 scripts support --dry-run flag."""

    @pytest.mark.parametrize("script", STAGE3_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
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
            assert error not in stderr_lower, f"Unexpected {error} in {script}: {result.stderr}"
            assert error not in stdout_lower, f"Unexpected {error} in {script}: {result.stdout}"


class TestStage3ModuleStructure:
    """Test that Stage 3 scripts use correct module structure."""

    @pytest.mark.parametrize("script", STAGE3_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_uses_f1d_shared_imports(self, script: str):
        """Verify scripts use f1d.shared.* namespace imports."""
        script_path = REPO_ROOT / script
        content = script_path.read_text(encoding="utf-8")

        # Check for correct import pattern
        assert "from f1d.shared" in content or "import f1d.shared" in content, \
            f"Script {script} should use f1d.shared.* imports"

    @pytest.mark.parametrize("script", STAGE3_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
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


class TestStage3ArgumentParsing:
    """Test that Stage 3 scripts have proper CLI argument parsing."""

    @pytest.mark.parametrize("script", STAGE3_ALL_SCRIPTS, ids=lambda s: Path(s).stem)
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
        assert result.returncode == 0, f"--help failed for {script}: {result.stderr}"
        assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower(), \
            f"--help should show usage for {script}"


class TestStage3HypothesisMapping:
    """Test that hypothesis scripts are correctly mapped."""

    def test_h1_script_exists(self):
        """Verify H1 (Cash Holdings) script exists."""
        h1_path = REPO_ROOT / "src/f1d/financial/build_h1_cash_holdings_panel.py"
        assert h1_path.exists(), "H1 Cash Holdings script should exist"

    def test_h2_script_exists(self):
        """Verify H2 (Investment Efficiency) scripts exist."""
        h2_path = REPO_ROOT / "src/f1d/financial/build_h2_investment_panel.py"
        assert h2_path.exists(), "H2 Investment Efficiency script should exist"

    def test_h3_script_exists(self):
        """Verify H3 (Payout Policy) script exists."""
        h3_path = REPO_ROOT / "src/f1d/financial/build_h3_payout_policy_panel.py"
        assert h3_path.exists(), "H3 Payout Policy script should exist"

    def test_h5_script_exists(self):
        """Verify H5 (Dispersion) script exists."""
        h5_path = REPO_ROOT / "src/f1d/financial/build_h5_dispersion_panel.py"
        assert h5_path.exists(), "H5 Dispersion script should exist"

    def test_h6_script_exists(self):
        """Verify H6 (CCC&L) script exists."""
        h6_path = REPO_ROOT / "src/f1d/financial/build_h6_cccl_panel.py"
        assert h6_path.exists(), "H6 CCC&L script should exist"

    def test_h7_script_exists(self):
        """Verify H7 (Illiquidity) script exists."""
        h7_path = REPO_ROOT / "src/f1d/financial/build_h7_illiquidity_panel.py"
        assert h7_path.exists(), "H7 Illiquidity script should exist"

    def test_h8_script_exists(self):
        """Verify H8 (Takeover) script exists."""
        h8_path = REPO_ROOT / "src/f1d/financial/build_h8_policy_risk_panel.py"
        assert h8_path.exists(), "H8 Takeover script should exist"

    def test_h9_scripts_exist(self):
        """Verify H9-related scripts exist."""
        h9_style_path = REPO_ROOT / "src/f1d/variables/3.11_H9_StyleFrozen.py"
        h9_prisk_path = REPO_ROOT / "src/f1d/variables/3.12_H9_PRiskFY.py"
        h9_invest_path = REPO_ROOT / "src/f1d/variables/3.13_H9_AbnormalInvestment.py"

        assert h9_style_path.exists(), "H9 StyleFrozen script should exist"
        assert h9_prisk_path.exists(), "H9 PRiskFY script should exist"
        assert h9_invest_path.exists(), "H9 AbnormalInvestment script should exist"

    def test_v1_orchestrator_exists(self):
        """Verify V1 orchestrator script exists."""
        orchestrator_path = REPO_ROOT / "src/f1d/variables/3.0_BuildFinancialFeatures.py"
        assert orchestrator_path.exists(), "V1 Financial orchestrator script should exist"
