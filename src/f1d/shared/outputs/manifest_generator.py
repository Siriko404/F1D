"""Centralized manifest generation for all pipeline stages.

Generates run_manifest.json with full reproducibility information:
- Git commit SHA (with container/Docker fallback via F1D_GIT_COMMIT env var)
- SHA256 hashes of input files
- Command line invocation
- Timestamp and stage identifier

Usage:
    from f1d.shared.outputs import generate_manifest

    generate_manifest(
        output_dir=out_dir,
        stage="stage3",
        timestamp=timestamp,
        input_paths={"manifest": manifest_path},
        output_files={"panel": panel_file, "report": report_file},
    )
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def generate_manifest(
    output_dir: Path,
    stage: str,
    timestamp: str,
    input_paths: Dict[str, Optional[Path]],
    output_files: Dict[str, Path],
    config: Optional[Dict[str, Any]] = None,
    panel_path: Optional[Path] = None,
) -> Path:
    """Generate run_manifest.json with full reproducibility info.

    Args:
        output_dir: Directory to write run_manifest.json
        stage: Pipeline stage identifier ("stage3" or "stage4")
        timestamp: Run timestamp string
        input_paths: Dict mapping input names to their paths (values can be None)
        output_files: Dict mapping output names to their paths
        config: Optional configuration dict to include
        panel_path: Optional path to panel file (Stage 4 only, for hash verification)

    Returns:
        Path to the generated manifest file
    """
    manifest = {
        "manifest_version": "1.0",
        "stage": stage,
        "timestamp": timestamp,
        "generated_at": datetime.now().isoformat(),
        "git_commit": _get_git_commit(output_dir),
        "command": " ".join(sys.argv),
        "input_hashes": _compute_input_hashes(input_paths),
        "output_files": {k: str(v) for k, v in output_files.items()},
        "config": config or {},
    }

    if panel_path:
        manifest["panel_path"] = str(panel_path)
        if panel_path.exists():
            manifest["panel_hash"] = _sha256_file(panel_path)

    manifest_path = output_dir / "run_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, default=str)

    return manifest_path


def _get_git_commit(work_dir: Path) -> str:
    """Get git commit SHA with fallback for containerized environments.

    Tries in order:
    1. git rev-parse HEAD (if in git repo)
    2. F1D_GIT_COMMIT environment variable (for Docker/CI)
    3. "unknown" fallback
    """
    # Try environment variable first (for containers)
    env_commit = os.environ.get("F1D_GIT_COMMIT")
    if env_commit:
        return env_commit

    # Try git command
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return "unknown"


def _compute_input_hashes(input_paths: Dict[str, Optional[Path]]) -> Dict[str, Optional[str]]:
    """Compute SHA256 hashes for input files.

    Args:
        input_paths: Dict mapping names to paths (paths can be None)

    Returns:
        Dict mapping names to hex digest strings (or None if path is None/missing)
    """
    hashes: Dict[str, Optional[str]] = {}
    for name, path in input_paths.items():
        if path is None:
            hashes[name] = None
        elif path.exists():
            hashes[name] = _sha256_file(path)
        else:
            hashes[name] = None
    return hashes


def _sha256_file(path: Path) -> str:
    """Compute SHA256 hash of file contents.

    Uses chunked reading to handle large files efficiently.

    Args:
        path: Path to file

    Returns:
        Hex digest string
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


__all__ = ["generate_manifest"]
