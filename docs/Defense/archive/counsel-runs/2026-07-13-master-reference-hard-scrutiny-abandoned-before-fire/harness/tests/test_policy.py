from pathlib import Path

import pytest

from counsel_harness.policy import ExpertPolicy, PolicyViolation


def test_only_c1_c2_and_private_snapshots_are_readable(run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)
    isolated_expert.download_dir.mkdir(parents=True)
    snapshot = isolated_expert.download_dir / "source.html"
    snapshot.write_text("raw source", encoding="utf-8")

    assert policy.resolve_read("C1") == isolated_expert.sources[0].path
    assert policy.resolve_read("C2") == isolated_expert.sources[1].path
    assert policy.resolve_read(str(snapshot)) == snapshot.resolve()

    with pytest.raises(PolicyViolation, match="not readable"):
        policy.resolve_read(str(run_config.run_dir / "subject-brief.md"))
    with pytest.raises(PolicyViolation, match="not readable"):
        policy.resolve_read(str(run_config.run_dir / "archive" / "anything.txt"))
    with pytest.raises(PolicyViolation, match="not readable"):
        policy.resolve_read(str(isolated_expert.download_dir.parent / "another-expert" / "x"))


def test_path_traversal_and_symlink_escape_are_rejected(run_config, isolated_expert, tmp_path: Path):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)
    isolated_expert.download_dir.mkdir(parents=True)
    outside = tmp_path / "sealed.txt"
    outside.write_text("sealed", encoding="utf-8")

    with pytest.raises(PolicyViolation):
        policy.resolve_download("../sealed.txt")
    with pytest.raises(PolicyViolation):
        policy.resolve_download("downloads/quantitative-results/../../sealed.txt")

    link = isolated_expert.download_dir / "escape.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(PolicyViolation, match="not readable"):
        policy.resolve_read(str(link))


def test_download_destination_is_private_and_exclusive(run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)
    destination = policy.resolve_download("downloads/quantitative-results/page.html")

    assert destination == isolated_expert.download_dir / "page.html"
    destination.parent.mkdir(parents=True)
    destination.write_text("existing", encoding="utf-8")
    with pytest.raises(PolicyViolation, match="already exists"):
        policy.resolve_download("page.html", require_new=True)


def test_only_assigned_journal_and_enforcer_are_accepted(run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)

    assert policy.validate_journal(isolated_expert.journal) == isolated_expert.journal
    assert policy.validate_enforcer(run_config.run_dir / "tools" / "journal.js").name == "journal.js"
    with pytest.raises(PolicyViolation):
        policy.validate_journal(run_config.run_dir / "journal" / "other.jsonl")
    with pytest.raises(PolicyViolation):
        policy.validate_enforcer(run_config.run_dir / "tools" / "verify-readback.js")

