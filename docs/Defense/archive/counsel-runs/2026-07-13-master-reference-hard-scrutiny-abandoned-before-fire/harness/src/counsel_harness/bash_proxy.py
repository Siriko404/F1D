from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path

from .policy import ExpertPolicy, PolicyViolation


class BashProxy:
    MAX_READ_LINES = 400
    MAX_MATCHES = 200

    def __init__(self, policy: ExpertPolicy, *, downloader, append_entry: Callable[[dict], str]):
        self.policy = policy
        self.downloader = downloader
        self.append_entry = append_entry

    def run(self, command: str) -> str:
        handlers = (
            self._journal,
            self._curl,
            self._wget,
            self._sed,
            self._head,
            self._tail,
            self._wc,
            self._rg,
        )
        for handler in handlers:
            result = handler(command)
            if result is not None:
                return result
        raise PolicyViolation("unsupported command")

    def _read_lines(self, path_text: str) -> tuple[Path, list[str]]:
        path = self.policy.resolve_read(path_text)
        return path, path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

    def _journal(self, command: str) -> str | None:
        match = re.fullmatch(
            r'node\s+"([^"]+)"\s+append\s+"([^"]+)"\s+<<\'EOF\'\r?\n(.+?)\r?\nEOF\s*',
            command,
            flags=re.DOTALL,
        )
        if not match:
            return None
        self.policy.validate_enforcer(Path(match.group(1)))
        self.policy.validate_journal(Path(match.group(2)))
        try:
            entry = json.loads(match.group(3))
        except json.JSONDecodeError as exc:
            raise PolicyViolation(f"invalid journal JSON: {exc.msg}") from exc
        if not isinstance(entry, dict):
            raise PolicyViolation("journal entry must be a JSON object")
        return self.append_entry(entry)

    def _curl(self, command: str) -> str | None:
        match = re.fullmatch(
            r'curl\s+-L\s+--fail\s+--silent\s+--show-error\s+-o\s+"([^"]+)"\s+"(https?://[^"]+)"\s*',
            command,
        )
        if not match:
            return None
        return str(self.downloader.download(match.group(2), match.group(1)))

    def _wget(self, command: str) -> str | None:
        match = re.fullmatch(r'wget\s+-q\s+-O\s+"([^"]+)"\s+"(https?://[^"]+)"\s*', command)
        if not match:
            return None
        return str(self.downloader.download(match.group(2), match.group(1)))

    def _sed(self, command: str) -> str | None:
        match = re.fullmatch(r'sed\s+-n\s+\'(\d+),(\d+)p\'\s+"([^"]+)"\s*', command)
        if not match:
            return None
        start, end = int(match.group(1)), int(match.group(2))
        if start < 1 or end < start or end - start + 1 > self.MAX_READ_LINES:
            raise PolicyViolation("sed request exceeds bounded read limit")
        _, lines = self._read_lines(match.group(3))
        return "".join(lines[start - 1 : end])

    def _head(self, command: str) -> str | None:
        match = re.fullmatch(r'head\s+-n\s+(\d+)\s+"([^"]+)"\s*', command)
        if not match:
            return None
        count = int(match.group(1))
        if not 1 <= count <= self.MAX_READ_LINES:
            raise PolicyViolation("head request exceeds bounded read limit")
        _, lines = self._read_lines(match.group(2))
        return "".join(lines[:count])

    def _tail(self, command: str) -> str | None:
        match = re.fullmatch(r'tail\s+-n\s+(\d+)\s+"([^"]+)"\s*', command)
        if not match:
            return None
        count = int(match.group(1))
        if not 1 <= count <= self.MAX_READ_LINES:
            raise PolicyViolation("tail request exceeds bounded read limit")
        _, lines = self._read_lines(match.group(2))
        return "".join(lines[-count:])

    def _wc(self, command: str) -> str | None:
        match = re.fullmatch(r'wc\s+-l\s+"([^"]+)"\s*', command)
        if not match:
            return None
        _, lines = self._read_lines(match.group(1))
        return str(len(lines))

    def _rg(self, command: str) -> str | None:
        match = re.fullmatch(
            r'rg\s+-n\s+(?:(--fixed-strings)\s+)?--\s+"([^"]*)"\s+"([^"]+)"\s*',
            command,
        )
        if not match:
            return None
        fixed, pattern, path_text = match.groups()
        if not pattern:
            raise PolicyViolation("search pattern cannot be empty")
        _, lines = self._read_lines(path_text)
        try:
            regex = None if fixed else re.compile(pattern)
        except re.error as exc:
            raise PolicyViolation(f"invalid search regex: {exc}") from exc
        matches = []
        for number, line in enumerate(lines, start=1):
            text = line.rstrip("\r\n")
            if (pattern in text) if fixed else bool(regex.search(text)):
                matches.append(f"{number}:{text}")
                if len(matches) >= self.MAX_MATCHES:
                    break
        return "\n".join(matches)
