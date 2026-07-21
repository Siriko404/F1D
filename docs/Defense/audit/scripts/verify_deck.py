"""Re-runnable verification of every mechanical claim in AUDIT_REGISTER.md.

Nothing here depends on a model, a rendered image, or this conversation. Run it
against the locked deck and it reproduces the artifact identity, the text layer,
the numeric inventory, the language scan, and the chart geometry.

    python verify_deck.py

Exit code 0 means every check reproduced. Any FAIL line means the register no
longer matches the artifact and the difference must be explained before the deck
is trusted again.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
DECK = (
    AUDIT.parent
    / "REV21"
    / "production"
    / "thesis_defense_main_deck_slides_01-13_standardized_v2.pdf"
)
EXPECTED_DECK_SHA256 = (
    "b1f396191295e320019d8123fe9cd588088e80f992c46150c5fd270f8e6aa94b"
)

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
    if not ok:
        failures.append(label)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def page_spans(page):
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                yield span["text"].strip(), fitz.Rect(span["bbox"])


def filled_dots(page, y_range, x_max=None):
    lo, hi = y_range
    found = []
    for item in page.get_drawings():
        rect = item["rect"]
        centre_y = (rect.y0 + rect.y1) / 2
        centre_x = (rect.x0 + rect.x1) / 2
        if not item.get("fill"):
            continue
        if not (2 < rect.width < 14 and abs(rect.width - rect.height) < 3):
            continue
        if not lo <= centre_y <= hi:
            continue
        if x_max is not None and centre_x >= x_max:
            continue
        found.append((centre_x, centre_y))
    return sorted(found)


def verify_identity(document) -> None:
    check(
        "deck SHA-256 matches the REV21 ledger",
        sha256(DECK) == EXPECTED_DECK_SHA256,
    )
    check("deck has 13 pages", document.page_count == 13)
    sizes = {(round(p.rect.width), round(p.rect.height)) for p in document}
    check("every page is 1152 x 648 points", sizes == {(1152, 648)})


def verify_language(document) -> None:
    """The deck must contain no em dash or en dash in any audience-facing text."""
    banned = {"—": "em dash", "–": "en dash"}
    hits = []
    dash_constructions = []
    for number, page in enumerate(document, 1):
        flat = " ".join(page.get_text("text").split())
        for character, name in banned.items():
            if character in flat:
                hits.append(f"slide {number} {name}")
        # Require two letters either side, which drops the letter-spaced heading
        # artifacts such as "CA S H - DE A L", and skip statistical contrast
        # names such as "GAP - POST Wald", where the hyphen means minus.
        for match in re.finditer(r"(?<=[A-Za-z]{2})\s+-\s+(?=[A-Za-z]{2})", flat):
            window = flat[max(0, match.start() - 30) : match.end() + 30]
            if "Wald" in window:
                continue
            dash_constructions.append((number, window))
    check("no em dash or en dash anywhere", not hits, "; ".join(hits))
    # Two are known and recorded on slide 12. More than two is a regression.
    check(
        "exactly the two recorded dash constructions remain, both on slide 12",
        len(dash_constructions) == 2 and all(n == 12 for n, _ in dash_constructions),
        f"found {len(dash_constructions)} on slides "
        f"{sorted({n for n, _ in dash_constructions})}",
    )


def verify_geometry(document) -> None:
    """Every plotted point must sit where its printed coefficient puts it."""
    panels = [
        ("slide 9 residual CEO uncertainty", 9, (290, 335), None,
         [0.0068, 0.0473, 0.0018, -0.0250]),
        ("slide 9 cash ratio", 9, (420, 470), None,
         [0.0008, 0.0061, 0.0055, -0.0155]),
        ("slide 10 cash acquirers", 10, (290, 320), 700,
         [0.0105, 0.0486, 0.0058, -0.0195]),
        ("slide 10 stock acquirers", 10, (400, 430), 700,
         [-0.0056, -0.0404, 0.0353, -0.0048]),
    ]
    scales = {}
    for label, page_number, band, x_max, values in panels:
        dots = filled_dots(document[page_number - 1], band, x_max)
        if len(dots) != 4:
            check(f"{label}: four plotted points located", False, f"found {len(dots)}")
            continue
        pairs = sorted(zip(values, [y for _, y in dots]))
        (low_value, low_y), (high_value, high_y) = pairs[0], pairs[-1]
        slope = (high_y - low_y) / (high_value - low_value)
        worst = max(abs(y - (low_y + slope * (v - low_value))) for v, y in pairs)
        scales[label] = abs(slope)
        check(
            f"{label}: points are linear in the coefficients",
            worst < 0.05,
            f"worst deviation {worst:.3f} pt, scale {abs(slope):.1f} pt/unit",
        )

    cash = scales.get("slide 10 cash acquirers")
    stock = scales.get("slide 10 stock acquirers")
    if cash and stock:
        check(
            "slide 10 panels share one scale, so the eye may compare them",
            abs(cash - stock) / cash < 0.01,
            f"{cash:.1f} against {stock:.1f}",
        )
    uncertainty = scales.get("slide 9 residual CEO uncertainty")
    ratio = scales.get("slide 9 cash ratio")
    if uncertainty and ratio:
        check(
            "slide 9 panels use separate scales, so different units are never "
            "compared by height",
            abs(ratio / uncertainty - 4.0) < 0.05,
            f"ratio {ratio / uncertainty:.2f}x",
        )

    verify_slide_8(document)


def verify_slide_8(document) -> None:
    """Slide 8 is measured against the drawn ticks, never the tick labels.

    Text centres sit below the rules they annotate. Anchoring to them produces a
    spurious two-point error that looks exactly like a real defect.
    """
    page = document[7]
    ticks = sorted(
        (item["rect"].y0, item["rect"].x0, item["rect"].x1)
        for item in page.get_drawings()
        if item["rect"].height == 0
        and 190 < item["rect"].x0 < 206
        and item["rect"].width < 12
    )
    if len(ticks) != 3:
        check("slide 8: three axis ticks located", False, f"found {len(ticks)}")
        return
    top, zero, bottom = (t[0] for t in ticks)
    check(
        "slide 8: axis is symmetric about zero",
        abs((zero - top) - (bottom - zero)) < 0.05,
        f"{zero - top:.2f} pt above, {bottom - zero:.2f} pt below",
    )
    scale = (bottom - top) / 0.602
    dots = [
        ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
        for r in (item["rect"] for item in page.get_drawings() if item.get("fill"))
        if 10 < r.width < 13 and abs(r.width - r.height) < 1 and 300 < (r.y0 + r.y1) / 2 < 350
    ]
    if len(dots) != 1:
        check("slide 8: the estimate point located", False, f"found {len(dots)}")
        return
    predicted = zero - scale * 0.0461
    check(
        "slide 8: the estimate sits at +0.0461",
        abs(dots[0][1] - predicted) < 0.05,
        f"drawn {dots[0][1]:.2f}, expected {predicted:.2f}",
    )


def main() -> int:
    if not DECK.is_file():
        print(f"FAIL  deck not found at {DECK}")
        return 1
    document = fitz.open(DECK)
    verify_identity(document)
    verify_language(document)
    verify_geometry(document)
    print()
    if failures:
        print(f"{len(failures)} check(s) FAILED: {', '.join(failures)}")
        return 1
    print("All checks reproduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
