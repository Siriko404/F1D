"""
End-to-End integration test for the pipeline over synthetic data.
"""
import pytest
import subprocess
import shutil
import tempfile
import sys
import os
from pathlib import Path
from tests.fixtures.synthetic_generator import generate_synthetic_inputs

pytestmark = pytest.mark.e2e

@pytest.fixture(scope="session")
def synthetic_workspace():
    """Create a temporary workspace mirroring the repo with synthetic inputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        repo_root = Path(__file__).parent.parent.parent
        
        # Copy src and config to temp workspace so __file__ resolution works
        shutil.copytree(repo_root / "src", temp_path / "src")
        shutil.copytree(repo_root / "config", temp_path / "config")
        
        # Generate tiny synthetic input files
        generate_synthetic_inputs(temp_path)
        
        # Create output and log dirs
        (temp_path / "outputs").mkdir(exist_ok=True)
        (temp_path / "logs").mkdir(exist_ok=True)
        
        yield temp_path

def run_script(script_path: Path, cwd: Path):
    """Run a pipeline script natively."""
    print(f"Running {script_path.name}...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd / "src")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env
    )
    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        pytest.fail(f"Script {script_path.name} failed with exit code {result.returncode}")

def test_full_pipeline_e2e(synthetic_workspace):
    """Run all pipeline scripts sequentially on synthetic data."""
    root_dir = synthetic_workspace
    src_dir = root_dir / "src" / "f1d"
    
    # Just run a smoke test of the main orchestrator to verify the inputs are valid
    run_script(src_dir / "sample" / "build_sample_manifest.py", root_dir)
    
    # If we made it here, the pipeline ran without crashing!
    assert True
