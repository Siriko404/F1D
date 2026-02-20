"""
Stage 1 (Sample) dry-run verification tests.

Tests that all Stage 1 sample scripts:
1. Can be imported without errors
2. Have proper --dry-run flag support
3. Execute dry-run validation without exceptions
4. Follow the expected module structure (f1d.shared.* imports)

Stage 1 Scripts:
    - 1.0_BuildSampleManifest.py (orchestrator)
    - 1.1_CleanMetadata.py
    - 1.2_LinkEntities.py
    - 1.3_BuildTenureMap.py
    - 1.4_AssembleManifest.py

Dependencies:
    - Scripts depend on config/project.yaml
    - Scripts depend on inputs/Earnings_Calls_Transcripts/Unified-info.parquet
"""

import os
import subprocess
from pathlib import Path

import pytest

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent.parent

# Stage 1 sample scripts to test (excluding utility modules)
STAGE1_SCRIPTS = [
    "src/f1d/sample/1.0_BuildSampleManifest.py",
    "src/f1d/sample/1.1_CleanMetadata.py",
    "src/f1d/sample/1.2_LinkEntities.py",
    "src/f1d/sample/1.3_BuildTenureMap.py",
    "src/f1d/sample/1.4_AssembleManifest.py",
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


class TestStage1ScriptImports:
    """Test that Stage 1 scripts can be imported."""

    @pytest.mark.parametrize("script", STAGE1_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_script_exists(self, script: str):
        """Verify each script file exists."""
        script_path = REPO_ROOT / script
        assert script_path.exists(), f"Script not found: {script_path}"

    @pytest.mark.parametrize("script", STAGE1_SCRIPTS, ids=lambda s: Path(s).stem)
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
        assert "ImportError" not in result.stderr, (
            f"Import error in {script}: {result.stderr}"
        )
        assert "ModuleNotFoundError" not in result.stderr, (
            f"Module not found in {script}: {result.stderr}"
        )


class TestStage1DryRunFlags:
    """Test that Stage 1 scripts support --dry-run flag."""

    @pytest.mark.parametrize("script", STAGE1_SCRIPTS, ids=lambda s: Path(s).stem)
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
            assert error not in stderr_lower, (
                f"Unexpected {error} in {script}: {result.stderr}"
            )
            assert error not in stdout_lower, (
                f"Unexpected {error} in {script}: {result.stdout}"
            )


class TestStage1ModuleStructure:
    """Test that Stage 1 scripts use correct module structure."""

    @pytest.mark.parametrize("script", STAGE1_SCRIPTS, ids=lambda s: Path(s).stem)
    def test_uses_f1d_shared_imports(self, script: str):
        """Verify scripts use f1d.shared.* namespace imports."""
        script_path = REPO_ROOT / script
        content = script_path.read_text(encoding="utf-8")

        # Check for correct import pattern
        assert "from f1d.shared" in content or "import f1d.shared" in content, (
            f"Script {script} should use f1d.shared.* imports"
        )

    @pytest.mark.parametrize("script", STAGE1_SCRIPTS, ids=lambda s: Path(s).stem)
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


class TestStage1ArgumentParsing:
    """Test that Stage 1 scripts have proper CLI argument parsing."""

    @pytest.mark.parametrize("script", STAGE1_SCRIPTS, ids=lambda s: Path(s).stem)
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
        assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower(), (
            f"--help should show usage for {script}"
        )


class TestStage1SequentialDependencies:
    """Test Stage 1 script execution order and dependencies."""

    def test_script_order(self):
        """Verify scripts are in correct dependency order."""
        # The order in STAGE1_SCRIPTS should match execution order
        expected_order = [
            "1.0_BuildSampleManifest",  # Orchestrator
            "1.1_CleanMetadata",
            "1.2_LinkEntities",
            "1.3_BuildTenureMap",
            "1.4_AssembleManifest",
        ]

        actual_order = [Path(s).stem for s in STAGE1_SCRIPTS]
        assert actual_order == expected_order, (
            f"Scripts should be in dependency order: expected {expected_order}, got {actual_order}"
        )

    def test_orchestrator_references_substeps(self):
        """Verify 1.0 orchestrator references all substeps."""
        orchestrator_path = REPO_ROOT / "src/f1d/sample/1.0_BuildSampleManifest.py"
        content = orchestrator_path.read_text(encoding="utf-8")

        substeps = [
            "1.1_CleanMetadata",
            "1.2_LinkEntities",
            "1.3_BuildTenureMap",
            "1.4_AssembleManifest",
        ]

        for substep in substeps:
            assert substep in content, f"Orchestrator should reference {substep}"
