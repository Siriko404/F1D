from dataclasses import replace
from pathlib import Path

import pytest

from counsel_harness.config import RunConfig


RUN_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture
def run_config() -> RunConfig:
    return RunConfig.load(RUN_DIR)


@pytest.fixture
def isolated_expert(run_config: RunConfig, tmp_path: Path):
    expert = run_config.experts["quantitative-results"]
    return replace(
        expert,
        journal=(tmp_path / "journal" / "quantitative-results.jsonl").resolve(),
        download_dir=(tmp_path / "downloads" / "quantitative-results").resolve(),
    )

