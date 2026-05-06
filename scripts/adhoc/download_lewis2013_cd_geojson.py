"""Download Lewis 2013 Congressional District boundary GeoJSONs.

Source: https://github.com/JeffreyBLewis/congressional-district-boundaries (Lewis et al.)
Data referenced from cdmaps.polisci.ucla.edu — UCLA Political Science.

Filters per-state files to those whose Congress range covers 111th OR 113th.
Mirrors them into:
    inputs/Lewis2013_CD/111/<State>_<a>_to_<b>.geojson  (covers 111th)
    inputs/Lewis2013_CD/113/<State>_<a>_to_<b>.geojson  (covers 113th)

Used by H1.6 redistricting DiD TEST 3 — replaces lossy ZCTA-CD crosswalk
path with geocode + point-in-polygon spatial join (Hasan 2022 verbatim
methodology per Lewis et al. 2013 reference shapefile).

Run once:
    python scripts/adhoc/download_lewis2013_cd_geojson.py
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

REPO = "JeffreyBLewis/congressional-district-boundaries"
API_URL = f"https://api.github.com/repos/{REPO}/contents/GeoJson"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/master/GeoJson"

OUT_DIR = Path("inputs/Lewis2013_CD")
TARGET_CONGRESSES = (111, 113)


def list_repo_geojson() -> list[dict]:
    """Fetch GitHub API listing of GeoJson dir entries."""
    req = urllib.request.Request(
        API_URL, headers={"User-Agent": "F1D-research/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def parse_congress_range(name: str) -> tuple[str, int, int] | None:
    """Parse '<State>_<startCong>_to_<endCong>.geojson' → (state, start, end).

    Returns None if name doesn't match this pattern.
    """
    if not name.endswith(".geojson"):
        return None
    base = name[:-8]
    parts = base.rsplit("_to_", 1)
    if len(parts) != 2:
        return None
    state_a = parts[0].rsplit("_", 1)
    if len(state_a) != 2:
        return None
    state, a_str = state_a
    b_str = parts[1]
    try:
        a = int(a_str)
        b = int(b_str)
    except ValueError:
        return None
    return state, a, b


def download(url: str, out_path: Path) -> int:
    """Stream-download url to out_path. Returns bytes written."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url, headers={"User-Agent": "F1D-research/1.0"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp, open(out_path, "wb") as f:
        data = resp.read()
        f.write(data)
        return len(data)


def main() -> None:
    print(f"[lewis2013] listing {API_URL}")
    entries = list_repo_geojson()
    print(f"[lewis2013] found {len(entries)} entries")

    # Bucket files by which target Congress they cover.
    targets: dict[int, list[tuple[str, str]]] = {c: [] for c in TARGET_CONGRESSES}
    for e in entries:
        name = e.get("name", "")
        if not name.endswith(".geojson"):
            continue
        parsed = parse_congress_range(name)
        if parsed is None:
            continue
        _, a, b = parsed
        for cong in TARGET_CONGRESSES:
            if a <= cong <= b:
                targets[cong].append((name, e.get("download_url", "")))

    for cong, files in targets.items():
        print(f"[lewis2013] Congress {cong}: {len(files)} files to download")

    failed: list[tuple[int, str, str]] = []
    for cong, files in targets.items():
        out_subdir = OUT_DIR / str(cong)
        out_subdir.mkdir(parents=True, exist_ok=True)
        for i, (name, url) in enumerate(sorted(files)):
            target = out_subdir / name
            if target.exists() and target.stat().st_size > 1000:
                print(f"  [{cong}] {i + 1:>2}/{len(files)} skip (exists) {name}")
                continue
            url = url or f"{RAW_BASE}/{name}"
            try:
                size = download(url, target)
                print(
                    f"  [{cong}] {i + 1:>2}/{len(files)} {name}: "
                    f"{size / 1024:.0f} KB"
                )
            except (HTTPError, URLError, TimeoutError) as exc:
                print(f"  [{cong}] {i + 1:>2}/{len(files)} FAIL {name}: {exc}")
                failed.append((cong, name, str(exc)))

    if failed:
        print(f"\n[lewis2013] FAILED: {len(failed)} files")
        for cong, name, err in failed:
            print(f"  {cong} {name}: {err}")
        raise SystemExit(1)

    # Summary
    for cong in TARGET_CONGRESSES:
        sub = OUT_DIR / str(cong)
        files = sorted(sub.glob("*.geojson"))
        total = sum(p.stat().st_size for p in files)
        print(
            f"[lewis2013] {cong}: {len(files)} files, "
            f"{total / (1024 * 1024):.1f} MB → {sub}"
        )


if __name__ == "__main__":
    main()
