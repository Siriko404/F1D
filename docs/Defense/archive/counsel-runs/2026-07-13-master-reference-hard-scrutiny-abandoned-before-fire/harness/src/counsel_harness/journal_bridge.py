from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .policy import ExpertPolicy


class JournalError(RuntimeError):
    pass


@dataclass(frozen=True)
class AppendResult:
    output: str
    stderr: str = ""


def _sanitized_subprocess_env() -> dict[str, str]:
    allowed = ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "COMSPEC", "PATHEXT")
    return {name: os.environ[name] for name in allowed if name in os.environ}


class JournalBridge:
    def __init__(
        self,
        policy: ExpertPolicy,
        *,
        journal_path: Path | None = None,
        node_executable: str | None = None,
    ):
        self.policy = policy
        self.journal_path = policy.validate_journal(journal_path or policy.expert.journal)
        self.enforcer = policy.validate_enforcer(policy.run_dir / "tools" / "journal.js")
        self.node_executable = node_executable or shutil.which("node")
        if not self.node_executable:
            raise JournalError("Node.js executable not found")

    def append(self, entry: dict) -> AppendResult:
        if not isinstance(entry, dict):
            raise JournalError("journal entry must be an object")
        payload = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
        completed = subprocess.run(
            [
                self.node_executable,
                str(self.enforcer),
                "append",
                str(self.journal_path),
            ],
            input=payload,
            text=True,
            capture_output=True,
            shell=False,
            cwd=self.policy.run_dir,
            env=_sanitized_subprocess_env(),
            timeout=30,
            check=False,
        )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        if completed.returncode != 0:
            message = stdout or stderr or f"journal enforcer exited {completed.returncode}"
            raise JournalError(message)
        return AppendResult(output=stdout, stderr=stderr)

