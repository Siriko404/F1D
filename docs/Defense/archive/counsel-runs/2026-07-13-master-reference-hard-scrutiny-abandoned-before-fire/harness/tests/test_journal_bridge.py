import json
import subprocess

import pytest

from counsel_harness.journal_bridge import JournalBridge, JournalError
from counsel_harness.policy import ExpertPolicy


def test_append_invokes_node_with_json_on_stdin_and_sanitized_environment(
    monkeypatch, run_config, isolated_expert
):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured.update(kwargs)
        return subprocess.CompletedProcess(args, 0, stdout="OK counts findings=1\n", stderr="")

    monkeypatch.setenv("DEEPSEEK_API_KEY", "must-not-leak")
    monkeypatch.setenv("OPENAI_API_KEY", "also-secret")
    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = JournalBridge(policy, node_executable="C:/Program Files/nodejs/node.exe")
    entry = {"t": "gap", "what": "not established"}

    result = bridge.append(entry)

    assert captured["args"] == [
        "C:/Program Files/nodejs/node.exe",
        str(run_config.run_dir / "tools" / "journal.js"),
        "append",
        str(isolated_expert.journal),
    ]
    assert json.loads(captured["input"]) == entry
    assert captured["shell"] is False
    assert captured["text"] is True
    assert "DEEPSEEK_API_KEY" not in captured["env"]
    assert "OPENAI_API_KEY" not in captured["env"]
    assert result.output == "OK counts findings=1"


def test_node_rejection_propagates_without_modifying_the_message(monkeypatch, run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args, 1, stdout="ERROR: quote not literally present\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    bridge = JournalBridge(policy, node_executable="node")

    with pytest.raises(JournalError, match="quote not literally present"):
        bridge.append({"t": "record"})


def test_bridge_cannot_be_constructed_for_another_journal(run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)

    with pytest.raises(Exception):
        JournalBridge(
            policy,
            journal_path=run_config.run_dir / "journal" / "other.jsonl",
            node_executable="node",
        )
