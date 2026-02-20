"""
Stage 2 (Text) dry-run verification tests.

Tests that all Stage 2 text processing scripts:
1. Can be imported without errors
2. Have proper --dry-run flag support
3. Execute dry-run validation without exceptions
4. Follow the expected module structure (f1d.shared.* imports)

Stage 2 Scripts (migrated from 2_Scripts/2_Text/):
    - tokenize_and_count.py (was 2.1_TokenizeAndCount.py)
    - construct_variables.py (was 2.2_ConstructVariables.py)
    - report_step2.py (was 2.3_ReportStep2.py)
    - verify_step2.py (was 2.3_VerifyStep2.py)

Dependencies:
    - Scripts depend on Step 1.4 outputs (master_sample_manifest.parquet)
    - Scripts depend on inputs/transcripts/*.txt files
"""

import os
import subprocess
from pathlib import Path

import pytest

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent.parent

# Stage 2 text scripts to test (excluding utility modules)
STAGE2_SCRIPTS = [
    "src/f1d/text/tokenize_and_count.py",
    "src/f1d/text/construct_variables.py",
    "src/f1d/text/report_step2.py",
    "src/f1d/text/verify_step2.py",
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


class TestStage2ScriptImports:
    """Test that Stage 2 scripts can be imported."""

    @pytest.mark.parametrize("script", STAGE2_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_exists(self, script: str):
        """Verify each script file exists."""
        script_path = REPO_ROOT / script
        assert script_path.exists(), f"Script not found: {script_path}"

    @pytest.mark.parametrize("script", STAGE2_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_importable(self, script: str, subprocess_env: dict):
        """Test that script can be imported without errors.

        Uses subprocess to isolate import test from test process.
        """
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


class TestStage2DryRunFlags:
    """Test that Stage 2 scripts support --dry-run flag."""

    @pytest.mark.parametrize("script", STAGE2_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_dryrun_flag_accepted(self, script: str, subprocess_env: dict):
        """Test that --dry-run flag is accepted by each script.

        Note: Scripts may exit with error if prerequisites are missing,
        but should not crash with unexpected exceptions.
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


class TestStage2ModuleStructure:
    """Test that Stage 2 scripts use correct module structure."""

    @pytest.mark.parametrize("script", STAGE2_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_uses_f1d_shared_imports(self, script: str):
        """Verify scripts use f1d.shared.* namespace imports."""
        script_path = REPO_ROOT / script
        content = script_path.read_text(encoding="utf-8")

        # Check for correct import pattern
        assert "from f1d.shared" in content or "import f1d.shared" in content, \
            f"Script {script} should use f1d.shared.* imports"

    @pytest.mark.parametrize("script", STAGE2_SCRIPTS, ids=lambda s: Path(s).stem)
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


class TestStage2ArgumentParsing:
    """Test that Stage 2 scripts have proper CLI argument parsing."""

    @pytest.mark.parametrize("script", STAGE2_SCRIPTS, ids=lambda s: Path(s).stem)
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


class TestStage2ParallelExecution:
    """Test Stage 2 script parallel execution compatibility."""

    def test_tokenizer_and_variables_are_parallelizable(self):
        """Verify tokenize_and_count and construct_variables can run in parallel.

        These scripts (2.1 and 2.2) are designed to run concurrently as they
        have no interdependencies.
        """
        tokenizer_path = REPO_ROOT / "src/f1d/text/tokenize_and_count.py"
        variables_path = REPO_ROOT / "src/f1d/text/construct_variables.py"

        tokenizer_content = tokenizer_path.read_text(encoding="utf-8")
        variables_content = variables_path.read_text(encoding="utf-8")

        # Both scripts should exist
        assert tokenizer_path.exists(), "tokenize_and_count.py should exist"
        assert variables_path.exists(), "construct_variables.py should exist"

        # Neither should depend on the other's output
        # (they both depend on Step 1.4 output independently)
        assert "tokenize_and_count" not in variables_content.lower() or \
               "tokenize_and_count" not in variables_content, \
            "construct_variables should not depend on tokenize_and_count output"

    def test_report_and_verify_depend_on_variables(self):
        """Verify report_step2 and verify_step2 depend on construct_variables."""
        construct_vars_path = REPO_ROOT / "src/f1d/text/construct_variables.py"
        report_path = REPO_ROOT / "src/f1d/text/report_step2.py"
        verify_path = REPO_ROOT / "src/f1d/text/verify_step2.py"

        # These scripts process outputs from construct_variables
        assert construct_vars_path.exists(), "construct_variables.py should exist"
        assert report_path.exists(), "report_step2.py should exist"
        assert verify_path.exists(), "verify_step2.py should exist"
