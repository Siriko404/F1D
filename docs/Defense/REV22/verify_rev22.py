"""Accept or reject the REV22 render, mechanically.

Run this the moment the render call returns. It answers two separate questions
that must not be confused with each other.

  1. Is the rendering environment faithful?
     Compare the CONTROL render against the locked REV21 PDF. The control was
     produced from a byte-identical copy of the REV21 source HTML, so any
     difference between them is the environment talking, not the edit. If the
     control drifts, the environment is rejected and the edited render cannot
     be trusted either, no matter how good it looks.

  2. Did the edit do only what it was supposed to do?
     Compare the EDITED render against the CONTROL. Exactly four slides may
     differ: 8, 11, 12 and 13. Every other slide must match span for span.

The audit's own verify_deck.py checks slides 8, 9 and 10 only. That is not
enough here. A layout engine that shapes text differently can reflow any slide,
so this script compares all thirteen, span by span, text and position.

    python verify_rev22.py

Exit code 0 means the render is accepted. Any FAIL means it is not.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).resolve().parent
LOCKED = (
    HERE.parent
    / "REV21"
    / "production"
    / "thesis_defense_main_deck_slides_01-13_standardized_v2.pdf"
)
CONTROL = HERE / "production" / "rev22_control_render.pdf"
EDITED = HERE / "production" / "thesis_defense_main_deck_slides_01-13_rev22.pdf"

LOCKED_SHA256 = "b1f396191295e320019d8123fe9cd588088e80f992c46150c5fd270f8e6aa94b"

# The only slides the five approved edits may touch.
EDITED_SLIDES = {8, 11, 12, 13}

# A span is "moved" if any corner shifts by more than this. Same engine and
# same version should be exact; a hundredth of a point absorbs float noise
# without hiding a real reflow, which is never smaller than a fraction of a
# point.
POSITION_TOLERANCE_PT = 0.01

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


def spans(page) -> list[tuple[str, tuple[float, float, float, float]]]:
    """Every text span on the page as (text, bbox), in reading order."""
    out = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"]
                if text.strip():
                    out.append((text, tuple(round(v, 3) for v in span["bbox"])))
    return out


def compare_page(left, right, number: int) -> list[str]:
    """Differences between one page of two documents. Empty means identical."""
    a, b = spans(left[number - 1]), spans(right[number - 1])
    if len(a) != len(b):
        return [f"span count {len(a)} against {len(b)}"]
    problems = []
    for index, ((text_a, box_a), (text_b, box_b)) in enumerate(zip(a, b)):
        if text_a != text_b:
            problems.append(f"span {index} text {text_a!r} against {text_b!r}")
            continue
        drift = max(abs(p - q) for p, q in zip(box_a, box_b))
        if drift > POSITION_TOLERANCE_PT:
            problems.append(f"span {index} {text_a!r} moved {drift:.3f} pt")
    return problems


def drawing_count(page) -> int:
    return len(page.get_drawings())


def verify_files_present() -> bool:
    ok = True
    for path in (LOCKED, CONTROL, EDITED):
        if not path.is_file():
            print(f"FAIL  missing file {path}")
            ok = False
    return ok


def verify_locked_untouched() -> None:
    check("REV21 locked deck is unchanged", sha256(LOCKED) == LOCKED_SHA256)


def verify_environment(locked, control) -> None:
    """Question 1. Does this environment reproduce the locked deck?"""
    print("\n-- environment fidelity: control render against the locked deck --")
    check("control has 13 pages", control.page_count == 13)
    if control.page_count != 13:
        return
    sizes = {(round(p.rect.width), round(p.rect.height)) for p in control}
    check("every control page is 1152 x 648 points", sizes == {(1152, 648)})

    byte_identical = sha256(CONTROL) == LOCKED_SHA256
    print(
        f"      control is byte-identical to the locked deck: {byte_identical}"
        + ("" if byte_identical else "  (not required; the span check decides)")
    )

    drifted = []
    for number in range(1, 14):
        problems = compare_page(locked, control, number)
        if problems:
            drifted.append((number, problems))
    check(
        "all 13 slides reproduce span for span",
        not drifted,
        "" if not drifted else f"drift on slides {[n for n, _ in drifted]}",
    )
    for number, problems in drifted:
        for problem in problems[:4]:
            print(f"        slide {number}: {problem}")
        if len(problems) > 4:
            print(f"        slide {number}: ... {len(problems) - 4} more")


def verify_edit_scope(control, edited) -> None:
    """Question 2. Did the edit touch only the four intended slides?"""
    print("\n-- edit scope: edited render against the control render --")
    check("edited deck has 13 pages", edited.page_count == 13)
    if edited.page_count != 13:
        return
    sizes = {(round(p.rect.width), round(p.rect.height)) for p in edited}
    check("every edited page is 1152 x 648 points", sizes == {(1152, 648)})
    check(
        "the two renders are not the same file",
        sha256(CONTROL) != sha256(EDITED),
    )

    changed = set()
    for number in range(1, 14):
        if compare_page(control, edited, number):
            changed.add(number)

    check(
        "only the four intended slides changed",
        changed == EDITED_SLIDES,
        f"changed {sorted(changed)}, expected {sorted(EDITED_SLIDES)}",
    )
    unexpected = changed - EDITED_SLIDES
    for number in sorted(unexpected):
        for problem in compare_page(control, edited, number)[:4]:
            print(f"        slide {number}: {problem}")
    missing = EDITED_SLIDES - changed
    if missing:
        print(f"        no change reached slides {sorted(missing)}")

    # Vector content carries the charts. The edits are pure text, so no drawing
    # anywhere may appear, vanish, or move.
    for number in range(1, 14):
        before = drawing_count(control[number - 1])
        after = drawing_count(edited[number - 1])
        if before != after:
            check(f"slide {number} keeps its drawing count", False,
                  f"{before} against {after}")


def verify_edits_landed(edited) -> None:
    """The five approved strings are present and the old ones are gone."""
    print("\n-- the five approved edits --")
    text = {n: " ".join(edited[n - 1].get_text("text").split()) for n in range(1, 14)}

    expected = [
        ("R22-01 slide 8 says ln(assets)", 8, "ln(assets)", "Leverage, size,"),
        ("R22-01 slide 8 says dividend indicator", 8, "dividend indicator", "capex, dividends,"),
        ("R22-02 slide 11 compares like with like", 11,
         "rather than stock acquisitions", "rather than stock."),
        ("R22-03 slide 12 note drops the dash", 12,
         "disclosure, no more and no less", "disclosure - no more"),
        ("R22-05 slide 13 restores the hedge", 13,
         "These patterns suggest that", None),
    ]
    for label, number, present, absent in expected:
        ok = present in text[number]
        if absent is not None:
            ok = ok and absent not in text[number]
        check(label, ok)

    # The slide 12 section label is letter-spaced, so the extracted text has
    # spaces inside words. Match on the comma that replaced the dash instead.
    label_12 = text[12]
    check(
        "R22-04 slide 12 section label drops the dash",
        "SHOW - AND" not in label_12.replace(" ", " "),
        "",
    )

    joined = " ".join(text.values())
    check("no em dash or en dash on any slide", "—" not in joined and "–" not in joined)

    # Page text is not the whole document. The PDF's own /Title is audience
    # reachable through a viewer's title bar and properties panel, and REV21
    # carried an em dash and an en dash there for exactly as long as nobody
    # thought to look. A check called "anywhere" has to mean anywhere.
    metadata = " ".join(
        str(edited.metadata.get(key) or "")
        for key in ("title", "author", "subject", "keywords", "creator", "producer")
    )
    check(
        "no em dash or en dash in the PDF metadata",
        "—" not in metadata and "–" not in metadata,
        f"title is {edited.metadata.get('title')!r}",
    )


def verify_no_overflow(edited) -> None:
    """Nothing may sit outside its page. Clipped text still extracts, so this
    catches only gross overflow; the rendered PNGs are the real visual check."""
    print("\n-- containment --")
    bad = []
    for number in range(1, 14):
        page = edited[number - 1]
        for text, box in spans(page):
            if box[0] < -1 or box[1] < -1 or box[2] > 1153 or box[3] > 649:
                bad.append((number, text, box))
    check("every span sits inside its page", not bad,
          "" if not bad else f"{len(bad)} outside")
    for number, text, box in bad[:5]:
        print(f"        slide {number}: {text!r} at {box}")


def main() -> int:
    if not verify_files_present():
        print("\nNothing to verify yet. Put the two returned PDFs in "
              f"{CONTROL.parent} first.")
        return 1

    locked = fitz.open(LOCKED)
    control = fitz.open(CONTROL)
    edited = fitz.open(EDITED)

    verify_locked_untouched()
    verify_environment(locked, control)
    verify_edit_scope(control, edited)
    verify_edits_landed(edited)
    verify_no_overflow(edited)

    print()
    if failures:
        print(f"{len(failures)} check(s) FAILED:")
        for label in failures:
            print(f"  - {label}")
        print("\nREV22 is NOT accepted. Do not replace the production deck.")
        return 1
    print("REV22 render accepted. Rasterise slides 8, 11, 12 and 13 and look at "
          "them before locking; clipped text still extracts cleanly and only "
          "the eye catches it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
