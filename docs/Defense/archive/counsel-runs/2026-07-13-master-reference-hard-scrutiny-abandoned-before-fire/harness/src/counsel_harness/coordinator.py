from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .config import RunConfig


class DuplicateLaunchError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_json_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


class Coordinator:
    def __init__(
        self,
        config: RunConfig,
        client,
        *,
        status_path: Path | None = None,
        marker_path: Path | None = None,
    ):
        self.config = config
        self.client = client
        self.status_path = status_path or config.run_dir / "harness" / "status.json"
        self.marker_path = marker_path or config.run_dir / "harness" / "start-marker.json"

    async def start_once(self) -> dict:
        self.marker_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.marker_path.open("x", encoding="utf-8") as handle:
                json.dump({"started_at": _now(), "panel_size": len(self.config.experts)}, handle)
        except FileExistsError as exc:
            raise DuplicateLaunchError(f"panel already launched: {self.marker_path}") from exc

        status = {
            "started_at": _now(),
            "updated_at": _now(),
            "experts": {
                slug: {
                    "agent_id": f"defense-counsel-{slug}",
                    "session_id": f"defense-counsel-{slug}-2026-07-13",
                    "run_id": None,
                    "status": "STARTING",
                }
                for slug in self.config.experts
            },
        }
        _atomic_json_write(self.status_path, status)

        async def start_expert(slug: str):
            expert = self.config.experts[slug]
            return await self.client.start(
                f"defense-counsel-{slug}",
                expert.prompt.read_text(encoding="utf-8"),
                f"defense-counsel-{slug}-2026-07-13",
            )

        slugs = list(self.config.experts)
        results = await asyncio.gather(*(start_expert(slug) for slug in slugs), return_exceptions=True)
        for slug, result in zip(slugs, results, strict=True):
            item = status["experts"][slug]
            if isinstance(result, Exception):
                item["status"] = "FAILED_TO_START"
                item["error_type"] = type(result).__name__
            else:
                item["run_id"] = result["run_id"]
                item["session_id"] = result.get("session_id", item["session_id"])
                item["status"] = result.get("status", "RUNNING")
        status["updated_at"] = _now()
        _atomic_json_write(self.status_path, status)
        return status

    def status(self) -> dict:
        if not self.status_path.is_file():
            return {"experts": {}, "status": "NOT_STARTED"}
        return json.loads(self.status_path.read_text(encoding="utf-8"))

    def _expert_state(self, slug: str) -> dict:
        status = self.status()
        try:
            return status["experts"][slug]
        except KeyError as exc:
            raise ValueError(f"unknown or unstarted expert: {slug}") from exc

    async def cancel(self, slug: str) -> bool:
        item = self._expert_state(slug)
        result = await self.client.cancel(item["agent_id"], item["run_id"], item["session_id"])
        if result:
            status = self.status()
            status["experts"][slug]["status"] = "CANCEL_REQUESTED"
            status["updated_at"] = _now()
            _atomic_json_write(self.status_path, status)
        return bool(result)

    async def continue_run(self, slug: str, message: str) -> dict:
        item = self._expert_state(slug)
        result = await self.client.continue_run(
            item["agent_id"],
            item["run_id"],
            item["session_id"],
            message,
        )
        status = self.status()
        status["experts"][slug]["status"] = result.get("status", "RUNNING")
        status["updated_at"] = _now()
        _atomic_json_write(self.status_path, status)
        return result
