import json

import pytest

from counsel_harness.coordinator import Coordinator, DuplicateLaunchError


class FakeAgentOSClient:
    def __init__(self):
        self.started = []
        self.cancelled = []
        self.continued = []

    async def start(self, agent_id, prompt, session_id):
        self.started.append((agent_id, prompt, session_id))
        return {"run_id": f"run-{agent_id}", "session_id": session_id, "status": "RUNNING"}

    async def cancel(self, agent_id, run_id, session_id):
        self.cancelled.append((agent_id, run_id, session_id))
        return True

    async def continue_run(self, agent_id, run_id, session_id, message):
        self.continued.append((agent_id, run_id, session_id, message))
        return {"run_id": run_id, "session_id": session_id, "status": "RUNNING"}


@pytest.mark.asyncio
async def test_start_once_launches_all_five_and_atomically_persists_returned_ids(run_config, tmp_path):
    client = FakeAgentOSClient()
    coordinator = Coordinator(
        run_config,
        client,
        status_path=tmp_path / "status.json",
        marker_path=tmp_path / "start-marker.json",
    )

    status = await coordinator.start_once()

    assert len(client.started) == 5
    assert set(status["experts"]) == set(run_config.experts)
    persisted = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
    assert all(item["run_id"].startswith("run-defense-counsel-") for item in persisted["experts"].values())
    assert (tmp_path / "start-marker.json").is_file()

    with pytest.raises(DuplicateLaunchError):
        await coordinator.start_once()


@pytest.mark.asyncio
async def test_cancel_and_continue_use_the_same_native_run_and_session(run_config, tmp_path):
    client = FakeAgentOSClient()
    coordinator = Coordinator(
        run_config,
        client,
        status_path=tmp_path / "status.json",
        marker_path=tmp_path / "start-marker.json",
    )
    await coordinator.start_once()

    assert await coordinator.cancel("narrative-timing") is True
    await coordinator.continue_run("narrative-timing", "Record the remaining duty as a gap and seal.")

    item = coordinator.status()["experts"]["narrative-timing"]
    expected = (
        "defense-counsel-narrative-timing",
        item["run_id"],
        item["session_id"],
    )
    assert client.cancelled == [expected]
    assert client.continued == [expected + ("Record the remaining duty as a gap and seal.",)]


def test_status_file_never_contains_provider_secrets(run_config, tmp_path):
    status_path = tmp_path / "status.json"
    status_path.write_text('{"experts": {}, "note": "safe"}', encoding="utf-8")
    coordinator = Coordinator(
        run_config,
        FakeAgentOSClient(),
        status_path=status_path,
        marker_path=tmp_path / "start-marker.json",
    )

    serialized = json.dumps(coordinator.status())
    assert "sk-" not in serialized
    assert "API_KEY" not in serialized
