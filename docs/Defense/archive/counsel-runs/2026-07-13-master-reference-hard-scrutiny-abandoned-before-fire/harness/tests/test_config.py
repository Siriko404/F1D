import json
from pathlib import Path

import pytest

from counsel_harness.config import RunConfig, validate_source_path


RUN_DIR = Path(__file__).resolve().parents[2]
EXPECTED_SLUGS = {
    "quantitative-results",
    "empirical-interpretation",
    "narrative-timing",
    "slide-consistency",
    "visualization-standards",
}


def test_loads_exactly_the_ratified_five_experts_and_two_sources_each():
    config = RunConfig.load(RUN_DIR)

    assert set(config.experts) == EXPECTED_SLUGS
    assert config.s2_ratification.is_file()
    assert config.s3_ratification.is_file()

    for slug, expert in config.experts.items():
        assert expert.prompt.is_file()
        assert expert.journal == RUN_DIR / "journal" / f"{slug}.jsonl"
        assert expert.download_dir == RUN_DIR / "downloads" / slug
        assert [source.cid for source in expert.sources] == ["C1", "C2"]
        assert [source.source for source in expert.sources] == [
            "master_reference",
            "flattened_thesis",
        ]
        assert all(source.must_read for source in expert.sources)
        assert all(source.path.parent == RUN_DIR / "context-sources" for source in expert.sources)


def test_manifest_source_paths_outside_context_sources_are_rejected(tmp_path: Path):
    allowed = tmp_path / "context-sources"
    allowed.mkdir()
    inside = allowed / "C1.txt"
    inside.write_text("allowed", encoding="utf-8")
    outside = tmp_path / "subject-brief.md"
    outside.write_text("sealed", encoding="utf-8")

    assert validate_source_path(inside, allowed) == inside.resolve()
    with pytest.raises(ValueError, match="outside context-sources"):
        validate_source_path(outside, allowed)


def test_generated_manifests_have_no_unratified_source_ids():
    config = RunConfig.load(RUN_DIR)
    spec = json.loads((RUN_DIR / "context" / "panel-spec.json").read_text(encoding="utf-8"))

    assert set(spec["sources"]) == {"master_reference", "flattened_thesis"}
    assert all(
        [source.source for source in expert.sources]
        == ["master_reference", "flattened_thesis"]
        for expert in config.experts.values()
    )
