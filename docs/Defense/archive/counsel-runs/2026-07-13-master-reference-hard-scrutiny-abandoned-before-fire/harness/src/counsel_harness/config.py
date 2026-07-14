from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


EXPECTED_SLUGS = (
    "quantitative-results",
    "empirical-interpretation",
    "narrative-timing",
    "slide-consistency",
    "visualization-standards",
)


def validate_source_path(path: Path, context_root: Path) -> Path:
    resolved_root = context_root.resolve(strict=True)
    resolved_path = path.resolve(strict=True)
    if not resolved_path.is_file():
        raise ValueError(f"manifest source is not a file: {path}")
    if not resolved_path.is_relative_to(resolved_root):
        raise ValueError(f"manifest source is outside context-sources: {path}")
    return resolved_path


@dataclass(frozen=True)
class SourceConfig:
    cid: str
    source: str
    path: Path
    what: str
    must_read: bool


@dataclass(frozen=True)
class ExpertConfig:
    slug: str
    aspect: str
    prompt: Path
    manifest_path: Path
    journal: Path
    download_dir: Path
    sources: tuple[SourceConfig, ...]


@dataclass(frozen=True)
class RunConfig:
    run_dir: Path
    experts: dict[str, ExpertConfig]
    s2_ratification: Path
    s3_ratification: Path

    @classmethod
    def load(cls, run_dir: Path) -> "RunConfig":
        run_dir = run_dir.resolve(strict=True)
        context_root = run_dir / "context-sources"
        s2_ratification = run_dir / "s2-ratification.md"
        s3_ratification = run_dir / "s3-ratification.md"
        for gate in (s2_ratification, s3_ratification):
            if not gate.is_file() or "Ratified by Sina" not in gate.read_text(encoding="utf-8"):
                raise ValueError(f"missing ratification gate: {gate}")

        manifest_dir = run_dir / "context"
        actual_slugs = {
            path.name.removesuffix("-manifest.json")
            for path in manifest_dir.glob("*-manifest.json")
        }
        if actual_slugs != set(EXPECTED_SLUGS):
            raise ValueError(
                f"expected manifests {sorted(EXPECTED_SLUGS)}, found {sorted(actual_slugs)}"
            )

        experts: dict[str, ExpertConfig] = {}
        for slug in EXPECTED_SLUGS:
            manifest_path = manifest_dir / f"{slug}-manifest.json"
            raw = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            prompt = run_dir / "prompts" / f"{slug}.md"
            if not prompt.is_file():
                raise ValueError(f"missing generated prompt: {prompt}")

            expected_journal = (run_dir / "journal" / f"{slug}.jsonl").resolve()
            declared_journal = Path(raw["journal"]).resolve()
            if declared_journal != expected_journal:
                raise ValueError(f"journal path mismatch for {slug}")

            manifest = raw.get("manifest")
            if not isinstance(manifest, list) or len(manifest) != 2:
                raise ValueError(f"{slug} must have exactly two manifest sources")

            sources = tuple(
                SourceConfig(
                    cid=item["id"],
                    source=item["source"],
                    path=validate_source_path(Path(item["path"]), context_root),
                    what=item["what"],
                    must_read=item["must_read"] is True,
                )
                for item in manifest
            )
            if [source.cid for source in sources] != ["C1", "C2"]:
                raise ValueError(f"{slug} must expose only C1 and C2")
            if [source.source for source in sources] != [
                "master_reference",
                "flattened_thesis",
            ]:
                raise ValueError(f"{slug} source identity mismatch")
            if not all(source.must_read for source in sources):
                raise ValueError(f"{slug} must read both assigned sources")

            experts[slug] = ExpertConfig(
                slug=slug,
                aspect=raw["aspect"],
                prompt=prompt.resolve(strict=True),
                manifest_path=manifest_path.resolve(strict=True),
                journal=expected_journal,
                download_dir=(run_dir / "downloads" / slug).resolve(),
                sources=sources,
            )

        return cls(
            run_dir=run_dir,
            experts=experts,
            s2_ratification=s2_ratification.resolve(strict=True),
            s3_ratification=s3_ratification.resolve(strict=True),
        )
