"""Render the deck locally with WeasyPrint.

WeasyPrint needs Pango, GLib, GObject, HarfBuzz, FreeType and Fontconfig. None
of them ship with Python and this machine has no GTK runtime installed, but
Tesseract-OCR bundles the complete set, so we borrow its DLL directory.

The subtlety that cost an hour: since Python 3.8, Windows DLL resolution for
ctypes and cffi ignores PATH. Putting the Tesseract directory on PATH looks
right and does nothing. os.add_dll_directory is the only thing that works, and
it must run before weasyprint is imported.

    python render.py control     # the untouched REV21 source
    python render.py edited      # the REV22 source with the five fixes
    python render.py both
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Any directory holding the full GLib/Pango stack works. Tesseract is simply
# the one already on this machine.
DLL_DIRECTORIES = [
    Path(r"C:\Program Files\Tesseract-OCR"),
    Path(r"C:\Program Files\GTK3-Runtime Win64\bin"),
]

for directory in DLL_DIRECTORIES:
    if directory.is_dir():
        os.add_dll_directory(str(directory))

import weasyprint  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
PRODUCTION = HERE / "production"

TARGETS = {
    # The control is not a deliverable. It is the evidence that this machine
    # renders exactly like the machine that produced the locked REV21 deck.
    "control": (SOURCE / "rev22_control.html", PRODUCTION / "rev22_control_render.pdf"),
    "edited": (
        SOURCE / "rev22_edited.html",
        PRODUCTION / "thesis_defense_main_deck_slides_01-13_rev22.pdf",
    ),
}


def render(name: str) -> None:
    html, pdf = TARGETS[name]
    PRODUCTION.mkdir(parents=True, exist_ok=True)
    weasyprint.HTML(filename=str(html)).write_pdf(str(pdf))
    print(f"{name}: {html.name} -> {pdf.name}  {pdf.stat().st_size} bytes")


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    print(f"WeasyPrint {weasyprint.__version__}")
    for name in TARGETS if which == "both" else [which]:
        render(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
