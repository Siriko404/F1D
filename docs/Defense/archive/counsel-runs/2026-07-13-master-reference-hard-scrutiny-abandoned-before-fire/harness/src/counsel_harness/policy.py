from __future__ import annotations

from pathlib import Path, PurePosixPath

from .config import ExpertConfig


class PolicyViolation(ValueError):
    """Raised when an expert attempts an operation outside its ratified boundary."""


class ExpertPolicy:
    def __init__(self, run_dir: Path, expert: ExpertConfig):
        self.run_dir = run_dir.resolve(strict=True)
        self.expert = expert
        self._source_by_cid = {source.cid: source.path for source in expert.sources}

    def resolve_read(self, ref_or_path: str) -> Path:
        if ref_or_path in self._source_by_cid:
            return self._source_by_cid[ref_or_path]

        candidate = Path(ref_or_path)
        if not candidate.is_absolute():
            posix = PurePosixPath(ref_or_path.replace("\\", "/"))
            prefix = ("downloads", self.expert.slug)
            if posix.parts[:2] == prefix:
                candidate = self.expert.download_dir.joinpath(*posix.parts[2:])
            else:
                candidate = self.expert.download_dir / candidate
        try:
            resolved = candidate.resolve(strict=True)
        except (FileNotFoundError, OSError) as exc:
            raise PolicyViolation(f"path is not readable: {ref_or_path}") from exc

        allowed_sources = set(self._source_by_cid.values())
        download_root = self.expert.download_dir.resolve(strict=False)
        if resolved in allowed_sources:
            return resolved
        if resolved.is_file() and resolved.is_relative_to(download_root):
            return resolved
        raise PolicyViolation(f"path is not readable: {ref_or_path}")

    def resolve_download(self, relative_name: str, *, require_new: bool = False) -> Path:
        normalized = relative_name.replace("\\", "/")
        pure = PurePosixPath(normalized)
        if pure.is_absolute() or not pure.parts or ".." in pure.parts:
            raise PolicyViolation(f"download path escapes private directory: {relative_name}")
        if pure.parts[0] == "downloads":
            if len(pure.parts) < 3 or pure.parts[1] != self.expert.slug:
                raise PolicyViolation(f"download path belongs to another expert: {relative_name}")
            pure = PurePosixPath(*pure.parts[2:])
        if not pure.parts or any(part in {"", "."} for part in pure.parts):
            raise PolicyViolation(f"invalid download path: {relative_name}")

        root = self.expert.download_dir.resolve(strict=False)
        destination = root.joinpath(*pure.parts).resolve(strict=False)
        if not destination.is_relative_to(root):
            raise PolicyViolation(f"download path escapes private directory: {relative_name}")
        if require_new and destination.exists():
            raise PolicyViolation(f"download destination already exists: {relative_name}")
        return destination

    def validate_journal(self, path: Path) -> Path:
        candidate = path.resolve(strict=False)
        expected = self.expert.journal.resolve(strict=False)
        if candidate != expected:
            raise PolicyViolation(f"journal does not belong to {self.expert.slug}: {path}")
        return candidate

    def validate_enforcer(self, path: Path) -> Path:
        candidate = path.resolve(strict=True)
        expected = (self.run_dir / "tools" / "journal.js").resolve(strict=True)
        if candidate != expected:
            raise PolicyViolation(f"unapproved executable: {path}")
        return candidate

