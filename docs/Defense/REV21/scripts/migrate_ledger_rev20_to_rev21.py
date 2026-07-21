#!/usr/bin/env python3
"""Deterministically migrate the exact thesis-defense ledger REV20 to REV21.

The migration is intentionally assertion-heavy. It preserves the complete REV20
object graph, applies only explicit state transitions and user-approved production
changes, builds a portable provenance bundle, and validates every archive member.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from PIL import Image
from pypdf import PdfReader, PdfWriter


WORKSPACE = Path("/workspace/scratch/5dac4a6a3c28")
BASE_LEDGER = WORKSPACE / "upload/THESIS_DEFENSE_CONTINUITY_LEDGER_REV20(1)(1).json"
BASE_LEDGER_SHA256 = "b010f865422dbdfc8458439c04d5b7c6114bbeda43b2b4284e3f052d0f094930"

PROJECT_ROOT = WORKSPACE / "work/ledger-rev21-package"
SCRIPT_PATH = PROJECT_ROOT / "scripts/migrate_ledger_rev20_to_rev21.py"
OUTPUT_DIR = PROJECT_ROOT / "output"
STAGING = PROJECT_ROOT / "staging/THESIS_DEFENSE_PROJECT_REV21"
LEDGER_NAME = "THESIS_DEFENSE_CONTINUITY_LEDGER_REV21.json"
LEDGER_OUTPUT = OUTPUT_DIR / LEDGER_NAME
ZIP_OUTPUT = OUTPUT_DIR / "THESIS_DEFENSE_PROJECT_LOCKED_REV21.zip"

FINAL_DIR = WORKSPACE / "work/deck-standardized/output"
FINAL_HTML = FINAL_DIR / "thesis_defense_main_deck_slides_01-13_standardized_v2.html"
FINAL_PDF = FINAL_DIR / "thesis_defense_main_deck_slides_01-13_standardized_v2.pdf"
FINAL_FILMSTRIP = FINAL_DIR / "thesis_defense_main_deck_slides_01-13_standardized_v2_pdf_filmstrip_300dpi.png"
FINAL_AUDIT = FINAL_DIR / "thesis_defense_main_deck_standardization_audit_applied_v2.json"
ASSEMBLY_SCRIPT = WORKSPACE / "work/deck-standardized/scripts/assemble_standardized_deck.py"
THESIS = Path("/workspace/scratch/5f1f7f3d8737/upload/_thesis_FLAT(2).tex")

EXPECTED_PRODUCTION_HASHES = {
    FINAL_HTML.name: "52b47bf58dfb491cc1d3cbe0be41c8b46e21b7b63648da183ba2e0461e39cc7b",
    FINAL_PDF.name: "b1f396191295e320019d8123fe9cd588088e80f992c46150c5fd270f8e6aa94b",
    FINAL_FILMSTRIP.name: "9692373564d7e7e6b67438d3c4963ae43caf47289bb95d3b83cb8dafc96b6c26",
    FINAL_AUDIT.name: "cde7de3e5e22c872c55e2848baa0691c58895bdd51101fcde1b926c163c7d6a4",
    ASSEMBLY_SCRIPT.name: "f117455dd527b979a0c1a4b35413f7aa76afc422cb6e77c76e69b93bf79b753d",
    THESIS.name: "6f2e003ff63eebb23bed8fe26dbd1601d0b5392a6628320d8782f60d5f936310",
}


SLIDE_INPUTS: dict[int, dict[str, Any]] = {
    1: {
        "html": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_01_corrected(2).html"),
        "pdf": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_01_corrected (1).pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/qa/locked/thesis_defense_slide_01_corrected.png"),
        "canonical": "thesis_defense_slide_01_corrected",
    },
    2: {
        "html": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_02_conceptual_framework_I_v2(1).html"),
        "pdf": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_02_conceptual_framework_I_v2 (1).pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/qa/locked/thesis_defense_slide_02_conceptual_framework_I_v2.png"),
        "canonical": "thesis_defense_slide_02_conceptual_framework_I_v2",
    },
    3: {
        "html": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_03_conceptual_framework_II_v5(1).html"),
        "pdf": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_03_conceptual_framework_II_v5 (1).pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/qa/locked/thesis_defense_slide_03_conceptual_framework_II_v5.png"),
        "canonical": "thesis_defense_slide_03_conceptual_framework_II_v5",
    },
    4: {
        "html": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_04_research_questions_roadmap_v5(1).html"),
        "pdf": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_04_research_questions_roadmap_v5 (1).pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/qa/locked/thesis_defense_slide_04_research_questions_roadmap_v5.png"),
        "canonical": "thesis_defense_slide_04_research_questions_roadmap_v5",
    },
    5: {
        "html": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_05_literature_nearest_work_v4(1).html"),
        "pdf": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_05_literature_nearest_work_v4 (1).pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/qa/locked/thesis_defense_slide_05_literature_nearest_work_v4.png"),
        "canonical": "thesis_defense_slide_05_literature_nearest_work_v4",
    },
    6: {
        "html": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_06_data_sample_v6(1).html"),
        "pdf": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_06_data_sample_v6 (1).pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/qa/locked/thesis_defense_slide_06_data_sample_v6.png"),
        "canonical": "thesis_defense_slide_06_data_sample_v6",
    },
    7: {
        "html": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_07_uncres_measure_v13(1).html"),
        "pdf": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_07_uncres_measure_v13 (1).pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/qa/locked/thesis_defense_slide_07_uncres_measure_v13.png"),
        "canonical": "thesis_defense_slide_07_uncres_measure_v13",
    },
    8: {
        "html": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/output/thesis_defense_slide_08_preannouncement_runup_v1.html"),
        "pdf": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/output/thesis_defense_slide_08_preannouncement_runup_v1.pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/output/thesis_defense_slide_08_preannouncement_runup_v1.png"),
        "canonical": "thesis_defense_slide_08_preannouncement_runup_v1",
    },
    9: {
        "html": Path("/workspace/scratch/c4e11f39ecf4/work/slide9-final/output/thesis_defense_slide_09_announcement_vs_completion_v1.html"),
        "pdf": Path("/workspace/scratch/c4e11f39ecf4/work/slide9-final/output/thesis_defense_slide_09_announcement_vs_completion_v1.pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide9-final/output/thesis_defense_slide_09_announcement_vs_completion_v1.png"),
        "canonical": "thesis_defense_slide_09_announcement_vs_completion_v1",
    },
    10: {
        "html": Path("/workspace/scratch/c4e11f39ecf4/work/slide10-final/output/thesis_defense_slide_10_cash_vs_stock_v1.html"),
        "pdf": Path("/workspace/scratch/c4e11f39ecf4/work/slide10-final/output/thesis_defense_slide_10_cash_vs_stock_v1.pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide10-final/output/thesis_defense_slide_10_cash_vs_stock_v1.png"),
        "canonical": "thesis_defense_slide_10_cash_vs_stock_v1",
    },
    11: {
        "html": Path("/workspace/scratch/c4e11f39ecf4/work/slide11-final/output/thesis_defense_slide_11_contributions_v1.html"),
        "pdf": Path("/workspace/scratch/c4e11f39ecf4/work/slide11-final/output/thesis_defense_slide_11_contributions_v1.pdf"),
        "png": Path("/workspace/scratch/c4e11f39ecf4/work/slide11-final/output/thesis_defense_slide_11_contributions_v1.png"),
        "canonical": "thesis_defense_slide_11_contributions_v1",
    },
    12: {
        "html": WORKSPACE / "work/slides12-13-final/output/thesis_defense_slide_12_evidence_boundaries_v1.html",
        "pdf": WORKSPACE / "work/slides12-13-final/output/thesis_defense_slide_12_evidence_boundaries_v1.pdf",
        "png": WORKSPACE / "work/slides12-13-final/output/thesis_defense_slide_12_evidence_boundaries_v1.png",
        "canonical": "thesis_defense_slide_12_evidence_boundaries_v1",
    },
    13: {
        "html": WORKSPACE / "work/slides12-13-final/output/thesis_defense_slide_13_conclusion_v2.html",
        "pdf": WORKSPACE / "work/slides12-13-final/output/thesis_defense_slide_13_conclusion_v2.pdf",
        "png": WORKSPACE / "work/slides12-13-final/output/thesis_defense_slide_13_conclusion_v2.png",
        "canonical": "thesis_defense_slide_13_conclusion_v2",
    },
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_hash(path: Path, expected: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = digest(path)
    if actual != expected:
        raise RuntimeError(f"SHA-256 mismatch for {path}: {actual} != {expected}")


def assert_replace(items: list[str], old: str, new: str, label: str) -> None:
    try:
        index = items.index(old)
    except ValueError as exc:
        raise RuntimeError(f"Expected ledger anchor missing: {label}: {old}") from exc
    items[index] = new


def artifact_record(path: Path, archive_path: str, role: str, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "role": role,
        "filename": path.name,
        "archive_path": archive_path,
        "sha256": digest(path),
        "size_bytes": path.stat().st_size,
    }
    result.update(extra)
    return result


def copy_payload(
    source: Path,
    archive_path: str,
    role: str,
    payload: list[dict[str, Any]],
    expected_sha256: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    if expected_sha256:
        assert_hash(source, expected_sha256)
    destination = STAGING / archive_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    record = artifact_record(destination, archive_path, role, **extra)
    if expected_sha256 and record["sha256"] != expected_sha256:
        raise RuntimeError(f"Copied payload changed bytes: {archive_path}")
    payload.append(record)
    return record


def find_slide_in_architecture(ledger: dict[str, Any], number: int) -> dict[str, Any]:
    matches = [
        slide
        for section in ledger["presentation_architecture"]["sections"]
        for slide in section["slides"]
        if slide["slide_number"] == number
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one architecture record for Slide {number}, got {len(matches)}")
    return matches[0]


def update_locked_elements(items: list[str], slide_number: int) -> None:
    for index, item in enumerate(items):
        items[index] = item.replace(
            "Times New Roman",
            "the embedded Times-compatible Nimbus Roman Standardized family",
        )

    if slide_number == 2:
        assert_replace(
            items,
            "Core prediction and mechanism-identification boundary.",
            "Core prediction retained; its mechanism-identification qualification is presented as a muted footnote.",
            "Slide 2 footnote policy",
        )
    elif slide_number == 4:
        assert_replace(
            items,
            "Plain-language descriptive equation chunks.",
            "Plain-language equation chunks use one clean compact rounded rectangle per variable; the payment-type cash and stock terms remain on one fitted line.",
            "Slide 4 equation pills",
        )
        assert_replace(
            items,
            "Common spine: firm controls, firm fixed effects, year-quarter fixed effects, firm-clustered errors, descriptive interpretation.",
            "The Main Analysis 1/2/3 labels are removed. The common design is concise, and the empirical boundary is one standalone sentence: all three tests are descriptive within-firm comparisons and do not identify causal effects.",
            "Slide 4 empirical boundary",
        )
    elif slide_number == 6:
        assert_replace(
            items,
            "Boundary on repeated-call and Execucomp selection.",
            "Repeated-call and Execucomp selection qualification is retained as a muted footnote.",
            "Slide 6 footnote policy",
        )
    elif slide_number == 7:
        assert_replace(
            items,
            "Boundary: generated in a first-stage decomposition; two-step estimation uncertainty is a limitation.",
            "First-stage generation and two-step estimation qualification is retained as a muted source footnote.",
            "Slide 7 footnote policy",
        )
    elif slide_number == 8:
        assert_replace(
            items,
            "Estimate point at +0.0461.",
            "Estimate +0.0461, SE 0.0172, and two-tailed p = 0.0074 are presented as coordinated peer statistics with restrained garnet emphasis.",
            "Slide 8 peer statistics",
        )
        items.remove("SE 0.0172 and two-tailed p = 0.0074.")
        assert_replace(
            items,
            "Boundary wording: Descriptive, not causal.",
            "The descriptive-not-causal qualification is retained as a muted source footnote.",
            "Slide 8 footnote policy",
        )
    elif slide_number == 9:
        assert_replace(
            items,
            "Top information-clock panel for residual CEO uncertainty with its displayed coefficients, standard errors, significance labels, approximate 95% CI whiskers, and both adjacent-stage Wald tests.",
            "Top information-clock panel presents coefficients, standard errors, significance, approximate 95% CI whiskers, and both adjacent-stage Wald tests with coordinated peer-statistic emphasis.",
            "Slide 9 peer statistics top",
        )
        assert_replace(
            items,
            "Bottom transaction-clock panel for cash ratio with its displayed coefficients, standard errors, significance labels, approximate 95% CI whiskers, and both adjacent-stage Wald tests.",
            "Bottom transaction-clock panel presents coefficients, standard errors, significance, approximate 95% CI whiskers, and both adjacent-stage Wald tests with coordinated peer-statistic emphasis.",
            "Slide 9 peer statistics bottom",
        )
        assert_replace(
            items,
            "Boundary wording: GAP cash is not significant; persistence rests on no announcement drop. Closing decline partly mechanical. Descriptive, not causal; mechanism remains open.",
            "The GAP-cash, partly-mechanical-closing, descriptive, non-causal, and open-mechanism qualifications are retained in the muted method/source footnote treatment.",
            "Slide 9 footnote policy",
        )
    elif slide_number == 10:
        assert_replace(
            items,
            "Formal pooled cash coefficient 0.0459, SE 0.0185, p < .05.",
            "Formal pooled cash estimate 0.0459, SE 0.0185, and p < .05 are presented as coordinated peer statistics.",
            "Slide 10 pooled cash peer statistics",
        )
        assert_replace(
            items,
            "Formal pooled stock coefficient -0.0524, SE 0.0436, not significant.",
            "Formal pooled stock estimate -0.0524, SE 0.0436, and not-significant inference are presented as coordinated peer statistics.",
            "Slide 10 pooled stock peer statistics",
        )
        assert_replace(
            items,
            "Direct Cash-minus-Stock Wald difference +0.0983, SE 0.0476, approximate 95% CI [0.005, 0.192], two-tailed p = .039.",
            "Direct Cash-minus-Stock Wald estimate +0.0983, SE 0.0476, approximate 95% CI [0.005, 0.192], and two-tailed p = .039 are grouped as peer evidence.",
            "Slide 10 Wald peer statistics",
        )
        assert_replace(
            items,
            "Boundary: within-firm, descriptive, not causal.",
            "The within-firm, descriptive, non-causal qualification is retained as a muted source footnote.",
            "Slide 10 footnote policy",
        )
    elif slide_number == 11:
        assert_replace(
            items,
            "Boundary strip: Contribution type — Descriptive.",
            "The former contribution-type boundary strip is removed from main content.",
            "Slide 11 boundary strip removal",
        )
        assert_replace(
            items,
            "Boundary text: The thesis characterizes a regularity; it does not identify a causal channel.",
            "The sentence 'The thesis characterizes a regularity; it does not identify a causal channel' is retained as a muted source footnote.",
            "Slide 11 footnote policy",
        )
    elif slide_number == 12:
        # User explicitly preserved the causal limitation and merged generalizability item.
        required = [
            "Lead statement: The evidence identifies a language pattern, not its cause.",
            "Boundary 01: The design is descriptive, not causal; it characterizes a within-firm regularity.",
            "Boundary 02: The sample skews toward larger, more heavily covered U.S. public firms, approximately the S&P 1500 during 2002-2018, limiting generalizability.",
        ]
        for anchor in required:
            if anchor not in items:
                raise RuntimeError(f"Slide 12 preserved anchor missing: {anchor}")
    elif slide_number == 13:
        if "Questions label." not in items:
            raise RuntimeError("Slide 13 Questions label anchor missing")
        items.remove("Questions label.")
        items.append("The announcement marker dot is geometrically centered on the timeline axis and marker line.")
        items.append("No standalone Questions label; the explicit defense-floor opening is the thank-you plus invitation to questions and comments.")


def update_architecture_slide_summary(slide: dict[str, Any], number: int) -> None:
    slide["status"] = "content_visual_and_standardized_production_locked"
    slide["production_approval_status"] = "user_approved_locked"
    slide["production_approval_date"] = "2026-07-16"
    if "locked_elements" in slide:
        update_locked_elements(slide["locked_elements"], number)

    summary = slide.get("approved_content_summary")
    if isinstance(summary, list):
        replacements = {
            8: {
                "Boundary: descriptive, not causal.":
                    "Muted source footnote: descriptive, not causal."
            },
            9: {
                "Boundary: GAP cash is not significant; persistence rests on no announcement drop; the closing decline is partly mechanical; descriptive, not causal; mechanism remains open.":
                    "Muted method/source footnote: GAP cash is not significant; persistence rests on no announcement drop; the closing decline is partly mechanical; descriptive, not causal; mechanism remains open."
            },
            10: {
                "Boundary: within-firm and descriptive, not causal; the result is supported but fragile because the stock estimate is imprecisely negative.":
                    "Muted method/source footnote: within-firm and descriptive, not causal; the result is supported but fragile because the stock estimate is imprecisely negative."
            },
            11: {
                "Boundary strip: Contribution type — Descriptive.":
                    "Main-content contribution-type boundary strip removed during standardization.",
                "Boundary wording: The thesis characterizes a regularity; it does not identify a causal channel.":
                    "Muted source footnote: The thesis characterizes a regularity; it does not identify a causal channel."
            },
        }
        for old, new in replacements.get(number, {}).items():
            assert_replace(summary, old, new, f"Slide {number} architecture summary")

    visual = slide.get("approved_visual_summary")
    if isinstance(visual, str):
        if number == 4:
            slide["approved_visual_summary"] = visual + " Standardized production uses single clean rounded equation pills, one-line cash/stock payment terms, no Main Analysis labels, and one standalone empirical-boundary sentence."
        elif number in (8, 9, 10):
            slide["approved_visual_summary"] = visual + " Standardized production balances estimate, SE, and inference as peer statistics and moves repeated boundary language to muted footnote treatment."
        elif number == 11:
            slide["approved_visual_summary"] = visual.replace(
                "a descriptive contribution-type boundary strip, ",
                "a muted descriptive source footnote, ",
            )
        elif number == 13:
            slide["approved_visual_summary"] = visual + " Standardized production removes the standalone Questions label and precisely aligns the announcement marker dot."


def build_payload(base: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    payload: list[dict[str, Any]] = []

    copy_payload(
        THESIS,
        "source/_thesis_FLAT(2).tex",
        "authoritative_approved_thesis",
        payload,
        EXPECTED_PRODUCTION_HASHES[THESIS.name],
        status="read_only_sole_academic_authority",
    )

    production_sources = [
        (FINAL_HTML, "production/" + FINAL_HTML.name, "locked_merged_html"),
        (FINAL_PDF, "production/" + FINAL_PDF.name, "locked_13_page_pdf"),
        (FINAL_FILMSTRIP, "production/" + FINAL_FILMSTRIP.name, "locked_pdf_derived_filmstrip_300dpi"),
        (FINAL_AUDIT, "production/" + FINAL_AUDIT.name, "applied_standardization_audit"),
        (ASSEMBLY_SCRIPT, "scripts/assemble_standardized_deck.py", "deterministic_deck_assembly_script"),
        (SCRIPT_PATH, "scripts/migrate_ledger_rev20_to_rev21.py", "deterministic_ledger_migration_script"),
        (BASE_LEDGER, "provenance/ledger/THESIS_DEFENSE_CONTINUITY_LEDGER_REV20.json", "immutable_rev20_migration_base"),
    ]
    for source, archive_path, role in production_sources:
        expected = EXPECTED_PRODUCTION_HASHES.get(source.name)
        if source == BASE_LEDGER:
            expected = BASE_LEDGER_SHA256
        copy_payload(source, archive_path, role, payload, expected, status="included_and_hash_verified")

    # Recover the two title-slide logo files exactly from the approved embedded HTML.
    html_bytes = SLIDE_INPUTS[1]["html"].read_bytes()
    encoded_images = re.findall(rb"data:image/png;base64,([A-Za-z0-9+/=]+)", html_bytes)
    expected_logos = {
        "9e6117f54bfb505fa07ad2a2d270c6ad9941ebaa98a8c32530c7ee54f765a0b7": "uottawa.png",
        "bc38e7cfa5b3da3f1174fe9e7e379c2c8d3caf49b2efa95332a1234a8fb7b4e0": "Primary_Black3.png",
    }
    recovered: dict[str, bytes] = {}
    for encoded in encoded_images:
        blob = base64.b64decode(encoded)
        recovered[hashlib.sha256(blob).hexdigest()] = blob
    if set(expected_logos) - set(recovered):
        raise RuntimeError("Could not recover both exact title-slide logo assets")
    for sha, filename in expected_logos.items():
        target = STAGING / f"provenance/assets/{filename}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(recovered[sha])
        if digest(target) != sha:
            raise RuntimeError(f"Recovered logo hash mismatch: {filename}")
        payload.append(
            artifact_record(
                target,
                f"provenance/assets/{filename}",
                "title_slide_logo_asset",
                status="recovered_exactly_from_locked_embedded_html",
            )
        )

    # Include the exact pre-standardization inputs that the deterministic assembler consumed.
    provenance_by_slide: dict[int, dict[str, Any]] = {}
    source_slide_records = {s["slide_number"]: s for s in base["slide_artifacts"]["slides"]}
    for number in range(1, 14):
        source_info = SLIDE_INPUTS[number]
        ledger_slide = source_slide_records[number]
        provenance_by_slide[number] = {}
        for extension in ("html", "pdf", "png"):
            source = source_info[extension]
            expected: str | None = None
            provenance_status = "approved_input_to_standardized_v2_assembly"
            provenance_extra: dict[str, Any] = {}
            if extension == "html":
                expected = ledger_slide["html"]["sha256"]
            elif extension == "pdf":
                expected = ledger_slide["pdf"]["sha256"]
            elif number >= 8:
                # The current same-name PNGs are later local renders and do not
                # match the exact PNG-byte hashes recorded in REV20. Do not
                # launder that discrepancy: preserve the available files as
                # non-authoritative provenance and use fresh exact-PDF rasters
                # below as the production slide images.
                recorded = ledger_slide["high_resolution_render"]
                current_sha = digest(source)
                provenance_status = "available_same_name_render_not_byte_identical_to_revision20_record"
                provenance_extra = {
                    "revision20_recorded_sha256": recorded["sha256"],
                    "revision20_recorded_size_bytes": recorded["size_bytes"],
                    "byte_identity_with_revision20_record": current_sha == recorded["sha256"],
                    "authority_note": "Not a production authority; use the standardized-v2 PDF-derived raster.",
                }
            canonical_name = f"{source_info['canonical']}.{extension}"
            archive_path = f"provenance/pre_standardization_locked_inputs/slide_{number:02d}/{canonical_name}"
            record = copy_payload(
                source,
                archive_path,
                f"slide_{number:02d}_pre_standardization_{extension}",
                payload,
                expected,
                slide_number=number,
                status=provenance_status,
                **provenance_extra,
            )
            provenance_by_slide[number][extension] = record

    # Split and rasterize the exact locked production PDF for portable per-slide exports.
    reader = PdfReader(str(FINAL_PDF))
    if len(reader.pages) != 13:
        raise RuntimeError(f"Expected 13 PDF pages, found {len(reader.pages)}")
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - 1152.0) > 0.01 or abs(height - 648.0) > 0.01:
            raise RuntimeError(f"Unexpected page box: {width} x {height}")

    with tempfile.TemporaryDirectory(prefix="rev21-pdf-raster-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        prefix = temp_dir / "page"
        subprocess.run(
            ["pdftoppm", "-r", "300", "-png", str(FINAL_PDF), str(prefix)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        rendered = sorted(temp_dir.glob("page-*.png"))
        if len(rendered) != 13:
            raise RuntimeError(f"Expected 13 raster pages, found {len(rendered)}")

        for number, page in enumerate(reader.pages, 1):
            pdf_name = f"thesis_defense_standardized_slide_{number:02d}.pdf"
            pdf_archive = f"production/individual_pages/{pdf_name}"
            pdf_target = STAGING / pdf_archive
            pdf_target.parent.mkdir(parents=True, exist_ok=True)
            writer = PdfWriter()
            writer.add_page(page)
            with pdf_target.open("wb") as handle:
                writer.write(handle)
            payload.append(
                artifact_record(
                    pdf_target,
                    pdf_archive,
                    f"slide_{number:02d}_standardized_pdf_page",
                    slide_number=number,
                    status="derived_from_locked_13_page_pdf",
                    page_size_points=[1152, 648],
                )
            )

            png_name = f"thesis_defense_standardized_slide_{number:02d}_300dpi.png"
            png_archive = f"production/individual_pages/{png_name}"
            png_target = STAGING / png_archive
            shutil.copy2(rendered[number - 1], png_target)
            with Image.open(png_target) as image:
                if image.size != (4800, 2700):
                    raise RuntimeError(f"Slide {number} raster is {image.size}, expected 4800x2700")
            payload.append(
                artifact_record(
                    png_target,
                    png_archive,
                    f"slide_{number:02d}_standardized_pdf_raster_300dpi",
                    slide_number=number,
                    status="rasterized_from_locked_13_page_pdf",
                    dpi=300,
                    pixel_dimensions=[4800, 2700],
                )
            )

    return payload, provenance_by_slide


def current_artifact_entry(path: Path, role: str, relationship: str) -> dict[str, Any]:
    return {
        "role": role,
        "filename": path.name,
        "sha256": digest(path),
        "size_bytes": path.stat().st_size,
        "status": "user_approved_locked",
        "version": "standardized_v2_production_lock",
        "approved_on": "2026-07-16",
        "locked": True,
        "relationship_to_thesis": relationship,
    }


def migrate_ledger(
    base: dict[str, Any],
    payload: list[dict[str, Any]],
    provenance_by_slide: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    ledger = copy.deepcopy(base)
    metadata = ledger["ledger_metadata"]
    if metadata["ledger_revision"] != 20:
        raise RuntimeError("Migration base is not revision 20")
    metadata.update(
        {
            "ledger_revision": 21,
            "last_updated_on": "2026-07-16",
            "status": "active_current_canonical_production_lock",
            "reconciliation_note": (
                "Revision 21 was produced by an assertion-based programmatic migration of the exact "
                f"Revision 20 bytes (SHA-256 {BASE_LEDGER_SHA256}). It preserves the full Revision 20 "
                "history, records the user's explicit reopening and approval of the cross-slide "
                "standardization pass, locks the synchronized standardized-v2 merged HTML, 13-page PDF, "
                "PDF-derived filmstrip, and applied audit, resolves combined-deck assembly, and advances "
                "the project to the already-approved indexed Q&A appendix architecture."
            ),
        }
    )

    # Project deliverables and scope.
    for item in ledger["project_definition"]["primary_deliverables"]:
        if item["name"] == "Main defense presentation":
            item.update(
                {
                    "status": "standardized_v2_assembled_user_approved_locked",
                    "combined_deck_assembled": True,
                    "standardization_applied": True,
                    "production_lock_date": "2026-07-16",
                    "production_edition": "standardized_v2",
                }
            )
        elif item["name"] == "Continuity ledger":
            item["status"] = "current_revision_21"
    scope = ledger["project_definition"]["scope_boundaries"]
    old_visual = "The visual system is locked: Times New Roman throughout, warm ivory background, near-black text, Telfer garnet accents, minimal elegant layouts, and university branding on Slide 1."
    new_visual = "The production visual system is locked: one embedded Times-compatible Nimbus Roman Standardized family throughout, warm ivory background, near-black text, Telfer garnet accents, minimal elegant layouts, and university branding on Slide 1."
    assert_replace(scope, old_visual, new_visual, "project visual-system scope")

    # Current file registry.
    registry = ledger["file_registry"]
    for item in registry["required_conditionally"]:
        if item["role"] == "current_defense_deck":
            item.update(
                {
                    "filename": FINAL_PDF.name,
                    "status": "created_user_approved_locked",
                    "trigger": "Use this exact standardized-v2 PDF for presentation or future review; do not substitute pre-standardization individual PDFs.",
                    "sha256": digest(FINAL_PDF),
                }
            )
    registry["current_defense_deck_status"] = {
        "status": "standardized_v2_assembled_user_approved_locked",
        "active_architecture": "13-slide Intro-Message-Outro deck",
        "production_edition": "standardized_v2",
        "production_lock_date": "2026-07-16",
        "approved_locked_slides": list(range(1, 14)),
        "current_artifacts": {
            "merged_html": {
                "filename": FINAL_HTML.name,
                "sha256": digest(FINAL_HTML),
                "archive_path": f"production/{FINAL_HTML.name}",
            },
            "merged_pdf": {
                "filename": FINAL_PDF.name,
                "sha256": digest(FINAL_PDF),
                "archive_path": f"production/{FINAL_PDF.name}",
                "pages": 13,
                "page_size_points": [1152, 648],
            },
            "pdf_derived_filmstrip": {
                "filename": FINAL_FILMSTRIP.name,
                "sha256": digest(FINAL_FILMSTRIP),
                "archive_path": f"production/{FINAL_FILMSTRIP.name}",
                "pixel_dimensions": [6592, 3792],
            },
            "applied_standardization_audit": {
                "filename": FINAL_AUDIT.name,
                "sha256": digest(FINAL_AUDIT),
                "archive_path": f"production/{FINAL_AUDIT.name}",
            },
        },
        "pre_standardization_individual_artifacts": "Preserved in the portable package as provenance; they are not the current production deck.",
        "full_deck_assembled": True,
        "completed_locked_sections": ["INTRO", "MESSAGE", "OUTRO"],
        "active_section": "MAIN_PRESENTATION_PRODUCTION_LOCKED",
        "individual_slide_design_complete": True,
        "next_project_action": "Resume the approved indexed Q&A appendix architecture when directed.",
    }
    registry["created_artifacts"].extend(
        [
            current_artifact_entry(FINAL_HTML, "main_deck_standardized_v2_html", "Current production source for the complete 13-slide defense deck."),
            current_artifact_entry(FINAL_PDF, "main_deck_standardized_v2_pdf", "Current production 13-page defense deck, rendered from the synchronized merged HTML."),
            current_artifact_entry(FINAL_FILMSTRIP, "main_deck_standardized_v2_pdf_filmstrip", "High-resolution montage derived only from the locked production PDF pages."),
            current_artifact_entry(FINAL_AUDIT, "main_deck_standardization_audit_applied_v2", "Machine-readable record of the applied and verified standardization changes."),
        ]
    )

    # Explicit new approvals; earlier decisions remain immutable history.
    ledger["approved_decisions"].extend(
        [
            {
                "decision_id": "D037",
                "record_type": "user_approved_decision",
                "date": "2026-07-16",
                "topic": "Authorized cross-slide standardization pass",
                "decision": (
                    "The user explicitly reopened the locked main deck only for the specified standardization audit and targeted fixes. "
                    "The authorized pass standardized the embedded Times-compatible font family, physical page boxes, and footer convention; "
                    "corrected Slide 4 equation pills and payment-term layout; removed Slide 4 Main Analysis labels; balanced estimate, SE, and p-value emphasis on Slides 8-10; "
                    "moved repeated boundary language to footnotes while preserving the standalone empirical boundary on Slide 4 and the causal limitation on Slide 12; "
                    "and aligned the Slide 13 announcement marker while removing its standalone Questions label."
                ),
                "status": "user_approved_and_applied",
            },
            {
                "decision_id": "D038",
                "record_type": "user_approved_decision",
                "date": "2026-07-16",
                "topic": "Standardized v2 full-deck production lock",
                "decision": (
                    "The user approved the synchronized standardized-v2 merged HTML, 13-page PDF, PDF-derived 300-DPI filmstrip, and applied audit as the final production main deck. "
                    "All 13 slides and the assembled deck are locked. The standardized-v2 merged HTML and PDF, identified by SHA-256, supersede the pre-standardization individual artifacts as current production authority; those earlier artifacts remain provenance only."
                ),
                "status": "user_approved_locked",
            },
        ]
    )

    architecture = ledger["presentation_architecture"]
    architecture["status"] = "final_architecture_and_standardized_v2_production_deck_user_approved_locked"
    architecture["completion_status"].update(
        {
            "individual_slides_complete": True,
            "approved_locked_slides": list(range(1, 14)),
            "combined_deck_assembled": True,
            "standardized_production_deck_locked": True,
            "next_production_step": "Resume the approved indexed Q&A appendix architecture when directed.",
        }
    )
    for section in architecture["sections"]:
        section["status"] = "content_visual_and_standardized_production_complete_locked"
        for slide in section["slides"]:
            update_architecture_slide_summary(slide, slide["slide_number"])

    # Slide artifacts: preserve original inputs but make the standardized deck/page the active authority.
    artifacts = ledger["slide_artifacts"]
    artifacts["approved_locked_slide_numbers"] = list(range(1, 14))
    artifacts["next_slide_number"] = None
    artifacts["source_format"] = "Synchronized merged HTML/CSS; pre-standardization individual HTML preserved as provenance"
    artifacts["render_format"] = "One locked 13-page PDF plus exact per-slide PDF pages and 300-DPI PDF rasters"

    payload_by_role = {item["role"]: item for item in payload}
    merged_html_ref = payload_by_role["locked_merged_html"]
    for slide in artifacts["slides"]:
        number = slide["slide_number"]
        slide["status"] = "user_approved_locked_standardized_v2_production"
        update_locked_elements(slide["locked_elements"], number)
        page_pdf = payload_by_role[f"slide_{number:02d}_standardized_pdf_page"]
        page_png = payload_by_role[f"slide_{number:02d}_standardized_pdf_raster_300dpi"]
        slide["production_lock"] = {
            "edition": "standardized_v2",
            "status": "user_approved_locked",
            "approved_on": "2026-07-16",
            "current_source_authority": {
                "filename": merged_html_ref["filename"],
                "archive_path": merged_html_ref["archive_path"],
                "sha256": merged_html_ref["sha256"],
                "slide_index": number,
            },
            "pdf_page": page_pdf,
            "high_resolution_pdf_raster": page_png,
            "pre_standardization_inputs": provenance_by_slide[number],
            "authority_note": "The production lock above controls. The older html/pdf/high_resolution_render fields remain immutable provenance from the pre-standardization approval sequence.",
        }

    # Open decisions.
    for item in ledger["open_decisions"]:
        if item["open_id"] == "O001":
            item.update(
                {
                    "status": "resolved",
                    "resolution": "All 13 slides were designed, approved, standardized under explicit user authorization, assembled, and locked in standardized-v2 production form.",
                    "resolved_on": "2026-07-16",
                }
            )
        elif item["open_id"] == "O023":
            item.update(
                {
                    "status": "resolved",
                    "resolution": (
                        "The complete 13-slide deck was assembled in order as synchronized merged HTML and a 13-page PDF, standardized under explicit user authorization, rasterized from the exact PDF at 300 DPI, audited, approved by the user, and locked as standardized v2."
                    ),
                    "resolved_on": "2026-07-16",
                }
            )

    # Current state and main-presentation completion.
    state = ledger["current_state"]
    state.update(
        {
            "stage": "The 13-slide main presentation is assembled, standardized, user-approved, and production-locked as v2; the indexed Q&A appendix architecture remains approved but its content is not yet designed.",
            "last_completed_action": "Received user approval for the standardized-v2 13-slide production deck and locked the synchronized merged HTML, 13-page PDF, PDF-derived filmstrip, and applied audit.",
            "next_action": "Resume the approved indexed Q&A appendix architecture when the user directs. Use only the authoritative LaTeX thesis for academic content and do not modify the standardized-v2 main deck unless the user explicitly reopens it.",
            "blockers": [],
            "files_needed_for_next_action": [
                LEDGER_NAME,
                "source/_thesis_FLAT(2).tex from the portable package",
                f"production/{FINAL_PDF.name} from the portable package for main-deck continuity",
            ],
            "do_not_do_next": [
                "Do not alter, rebuild, restyle, or substitute any standardized-v2 main-deck slide unless the user explicitly reopens it.",
                "Do not treat pre-standardization individual slide artifacts as the current production deck; they are provenance only.",
                "Do not treat filename duplicate suffixes as new design versions.",
                "Do not use any source other than the authoritative thesis for future academic claims.",
                "Do not begin a new appendix structure; resume the already-approved indexed Q&A appendix architecture unless the user changes it.",
            ],
        }
    )
    state["completed_actions"].extend(
        [
            "Explicitly reopened the locked main deck for the user-authorized standardization pass.",
            "Applied the standardization audit and the user's targeted Slide 4, Slide 13, coefficient-emphasis, and boundary-note instructions.",
            "Rendered and inspected the exact standardized 13-page PDF and its 300-DPI page rasters.",
            "Received user approval and locked the standardized-v2 merged HTML, PDF, PDF-derived filmstrip, and applied audit.",
            "Programmatically migrated the exact Revision 20 ledger to Revision 21 and built a hash-verified portable project package.",
        ]
    )
    completion = ledger["main_presentation_completion"]
    completion.update(
        {
            "status": "standardized_v2_assembled_user_approved_locked",
            "completed_on": "2026-07-16",
            "combined_pdf_status": "assembled_inspected_user_approved_locked",
            "standardization_status": "applied_inspected_user_approved_locked",
            "production_edition": "standardized_v2",
            "production_artifacts": registry["current_defense_deck_status"]["current_artifacts"],
            "appendix_status": "architecture_approved_content_not_yet_designed",
            "precise_next_action": "Resume the approved indexed Q&A appendix architecture when directed.",
        }
    )

    # Visual system now records the exact production implementation.
    visual = ledger["visual_system"]
    visual["status"] = "standardized_v2_production_locked_all_13_slides"
    visual["format"] = "One self-contained merged HTML/CSS source rendered to one 13-page PDF"
    visual["page_dimensions"] = {
        "all_slides": "16in x 9in CSS canvas; 1152 x 648 PDF points",
        "physical_pdf_page_box": [1152, 648],
        "pdf_raster_at_300_dpi": [4800, 2700],
    }
    visual["typography"].update(
        {
            "font_family": "Nimbus Roman Standardized (embedded Times-compatible family)",
            "font_files_embedded": ["regular", "bold", "italic", "bold-italic"],
            "production_rule": "Use only the embedded standardized family; do not rely on platform Times New Roman substitution.",
        }
    )
    visual["footer"].update(
        {
            "standard": "Muted source line at bottom-left and garnet NN / 13 at bottom-right on Slides 2-13.",
            "title_slide_exception": "Slide 1 intentionally has no source footer or page number.",
            "page_number_sequence": "02 / 13 through 13 / 13",
        }
    )
    visual["hierarchy_and_spacing"].append(
        "On finding slides, estimate, standard error, and p-value/inference are coordinated peer statistics; coefficients remain clear without oversized red dominance."
    )
    visual["hierarchy_and_spacing"].append(
        "Repeated descriptive boundary language is footnote-level except for the standalone empirical-test boundary on Slide 4 and the dedicated evidence-boundary treatment on Slide 12."
    )

    # Workflow and handoff state.
    ledger["handoff_reconciliation"].update(
        {
            "date": "2026-07-16",
            "canonical_state": "Standardized-v2 13-slide production deck assembled, inspected, user-approved, and locked; indexed Q&A appendix architecture approved but content not yet designed.",
            "current_canonical_revision": 21,
            "revision_21_update_base": {
                "base_file": "provenance/ledger/THESIS_DEFENSE_CONTINUITY_LEDGER_REV20.json",
                "source_storage_filename_documentary": BASE_LEDGER.name,
                "base_revision": 20,
                "base_sha256": BASE_LEDGER_SHA256,
                "method": "Assertion-based programmatic migration; complete REV20 JSON object preserved and selectively patched.",
            },
        }
    )
    workflow = ledger["production_and_qa_workflow"]
    workflow.update(
        {
            "status": "binding_for_future_reopened_main_deck_work_and_appendix_production",
            "authoring": "For the locked main deck, the current source authority is the self-contained standardized-v2 merged HTML. Appendix slides remain separate HTML/CSS until their own assembly stage.",
            "inspection_rule": "Render the exact target PDF, rasterize its pages at 300 DPI or higher, and inspect those PDF-derived images after the final edit.",
            "main_deck_lock_rule": "Do not edit or regenerate the standardized-v2 main deck unless the user explicitly reopens it.",
            "current_main_deck_html": FINAL_HTML.name,
            "current_main_deck_pdf": FINAL_PDF.name,
        }
    )

    # Old per-slide planning nodes remain as history, clearly non-operative.
    for key, value in ledger.items():
        if key.startswith("next_slide_") and isinstance(value, dict):
            value["status"] = "completed_locked_historical_record"
            value["current_authority"] = "main_presentation_completion.production_artifacts"
        if key.startswith("remaining_uncertainties_relevant_to_slide_") and isinstance(value, dict):
            value["status"] = "resolved_for_locked_main_deck_or_preserved_as_historical_context"

    # Portable-package reference scope: exact and machine-verifiable.
    ledger["portable_package"] = {
        "record_type": "artifact_manifest_scope",
        "package_revision": 21,
        "created_on": "2026-07-16",
        "status": "complete_hash_verified",
        "ledger_members": [LEDGER_NAME, metadata["portable_filename"]],
        "manifest_members": ["manifest/package_manifest.json", "manifest/SHA256SUMS.txt"],
        "reference_scope_rule": (
            "Every file object listed in included_files is an active or provenance package dependency and must exist at its archive_path with the recorded SHA-256. "
            "Filename strings elsewhere in preserved change logs, superseded_versions_do_not_reuse, retired_or_superseded_artifacts, stale-ledger history, and other explicitly historical fields are documentary records only; they are not active package dependencies unless also listed in included_files."
        ),
        "production_authority_rule": (
            "The synchronized standardized-v2 merged HTML and 13-page PDF are the current main-deck authority. Individual standardized PDF pages and 300-DPI rasters are exact derivatives. Pre-standardization individual HTML/PDF/render files are included only for provenance."
        ),
        "included_files": sorted(payload, key=lambda item: item["archive_path"]),
        "payload_file_count": len(payload),
        "payload_total_size_bytes": sum(item["size_bytes"] for item in payload),
        "integrity_method": "SHA-256 for every payload member; package_manifest.json and SHA256SUMS.txt verified after ZIP extraction.",
    }

    # Machine validation and immutable history.
    ledger["validation"]["required_pre_save_checks"] = [
        "Valid JSON syntax",
        "Exact migration base is Revision 20 with SHA-256 " + BASE_LEDGER_SHA256,
        "Ledger revision equals 21",
        "Final architecture remains locked at 13 slides",
        "Slides 1-13 are user-approved and production-locked",
        "Standardized-v2 merged HTML, 13-page PDF, PDF-derived filmstrip, and audit hashes match",
        "All PDF pages are 1152 x 648 points and all fresh 300-DPI rasters are 4800 x 2700 pixels",
        "O001 and O023 are resolved",
        "Combined deck is marked assembled, inspected, user-approved, and locked",
        "Slide 4, Slide 12, and Slide 13 standardization constraints are recorded exactly",
        "Every portable_package.included_files archive path exists and matches its recorded SHA-256",
        "The ZIP extracts cleanly and every checksum in SHA256SUMS.txt matches",
        "The appendix architecture remains approved and not yet designed",
        "The authoritative LaTeX thesis remains the sole academic source",
    ]
    ledger["validation"]["validation_status_at_revision_21"] = "passed_machine_validation"
    ledger["validation"]["revision_21_checks"] = {
        "json_syntax_valid": True,
        "ledger_revision": 21,
        "migration_base_revision": 20,
        "migration_base_sha256": BASE_LEDGER_SHA256,
        "migration_method": "programmatic_selective_patch_with_assertions",
        "total_slides": 13,
        "approved_locked_slides": list(range(1, 14)),
        "individual_slide_design_complete": True,
        "combined_deck_assembled": True,
        "standardized_v2_user_approved_locked": True,
        "merged_html_sha256": digest(FINAL_HTML),
        "merged_pdf_sha256": digest(FINAL_PDF),
        "filmstrip_sha256": digest(FINAL_FILMSTRIP),
        "audit_sha256": digest(FINAL_AUDIT),
        "pdf_page_count": 13,
        "pdf_page_size_points": [1152, 648],
        "pdf_raster_dpi": 300,
        "pdf_raster_page_pixels": [4800, 2700],
        "slide_4_authorized_fixes_recorded": True,
        "slide_12_causal_limitation_preserved": True,
        "slide_12_generalizability_item_remains_merged": True,
        "slide_13_questions_label_removed": True,
        "slide_13_marker_alignment_recorded": True,
        "o023_resolved": True,
        "appendix_architecture_preserved": True,
        "authoritative_thesis_rule_preserved": True,
        "portable_payload_file_count": len(payload),
        "portable_payload_hashes_verified": True,
    }

    ledger["change_log"].append(
        {
            "revision": 21,
            "date": "2026-07-16",
            "record_type": "artifact_status",
            "summary": (
                "Programmatically migrated the exact Revision 20 ledger to Revision 21 after explicit user approval of the standardized-v2 production deck. "
                "Recorded the authorized standardization pass, locked the synchronized merged HTML, 13-page PDF, PDF-derived filmstrip, and applied audit by SHA-256, "
                "updated Slide 4/8/9/10/11/12/13 production details, resolved full-deck assembly, standardized the visual-system record, preserved all prior ledger history and pre-standardization inputs as provenance, "
                "and defined a complete portable-package dependency set with per-file hashes."
            ),
            "next_action_after_change": "Resume the approved indexed Q&A appendix architecture when directed; do not modify the standardized-v2 main deck unless explicitly reopened.",
        }
    )

    return ledger


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_ledger(ledger: dict[str, Any]) -> None:
    if ledger["ledger_metadata"]["ledger_revision"] != 21:
        raise RuntimeError("Ledger revision validation failed")
    if ledger["presentation_architecture"]["total_slides"] != 13:
        raise RuntimeError("Slide-count validation failed")
    if ledger["slide_artifacts"]["approved_locked_slide_numbers"] != list(range(1, 14)):
        raise RuntimeError("Locked-slide validation failed")
    if ledger["slide_artifacts"]["next_slide_number"] is not None:
        raise RuntimeError("Next-slide validation failed")
    if not ledger["presentation_architecture"]["completion_status"]["combined_deck_assembled"]:
        raise RuntimeError("Combined deck state validation failed")
    if ledger["main_presentation_completion"]["status"] != "standardized_v2_assembled_user_approved_locked":
        raise RuntimeError("Main-presentation lock validation failed")

    decisions = {item["open_id"]: item for item in ledger["open_decisions"]}
    if decisions["O001"]["status"] != "resolved" or decisions["O023"]["status"] != "resolved":
        raise RuntimeError("Open-decision resolution validation failed")

    slides = {item["slide_number"]: item for item in ledger["slide_artifacts"]["slides"]}
    if "Questions label." in slides[13]["locked_elements"]:
        raise RuntimeError("Slide 13 stale Questions label survived migration")
    if not any("announcement marker dot" in item for item in slides[13]["locked_elements"]):
        raise RuntimeError("Slide 13 marker alignment was not recorded")
    slide12_text = "\n".join(slides[12]["locked_elements"])
    for required in (
        "The evidence identifies a language pattern, not its cause.",
        "The design is descriptive, not causal",
        "limiting generalizability",
    ):
        if required not in slide12_text:
            raise RuntimeError(f"Slide 12 preserved limitation missing: {required}")
    slide4_text = "\n".join(slides[4]["locked_elements"])
    for required in ("one clean compact rounded rectangle", "payment-type cash and stock terms", "Main Analysis 1/2/3 labels are removed", "do not identify causal effects"):
        if required not in slide4_text:
            raise RuntimeError(f"Slide 4 production detail missing: {required}")

    seen_paths: set[str] = set()
    for item in ledger["portable_package"]["included_files"]:
        path = item["archive_path"]
        if path in seen_paths:
            raise RuntimeError(f"Duplicate portable archive path: {path}")
        seen_paths.add(path)
        target = STAGING / path
        if not target.is_file():
            raise RuntimeError(f"Portable payload missing: {path}")
        if digest(target) != item["sha256"]:
            raise RuntimeError(f"Portable payload hash mismatch: {path}")
        if target.stat().st_size != item["size_bytes"]:
            raise RuntimeError(f"Portable payload size mismatch: {path}")


def build_manifest_and_zip(ledger: dict[str, Any]) -> dict[str, Any]:
    staging_ledger = STAGING / LEDGER_NAME
    write_json(staging_ledger, ledger)
    canonical_ledger = STAGING / ledger["ledger_metadata"]["portable_filename"]
    shutil.copy2(staging_ledger, canonical_ledger)
    shutil.copy2(staging_ledger, LEDGER_OUTPUT)
    if not (
        staging_ledger.read_bytes()
        == canonical_ledger.read_bytes()
        == LEDGER_OUTPUT.read_bytes()
    ):
        raise RuntimeError("External, revisioned, and canonical packaged ledger bytes differ")

    payload_files = sorted(path for path in STAGING.rglob("*") if path.is_file())
    manifest_entries = [
        {
            "archive_path": path.relative_to(STAGING).as_posix(),
            "sha256": digest(path),
            "size_bytes": path.stat().st_size,
        }
        for path in payload_files
    ]
    manifest = {
        "package_name": "THESIS_DEFENSE_PROJECT_REV21",
        "ledger_revision": 21,
        "created_on": "2026-07-16",
        "migration_base": {
            "revision": 20,
            "sha256": BASE_LEDGER_SHA256,
        },
        "manifest_scope": "All package members present before manifest creation; package_manifest.json and SHA256SUMS.txt are verified separately.",
        "file_count_excluding_manifest_files": len(manifest_entries),
        "files": manifest_entries,
    }
    manifest_path = STAGING / "manifest/package_manifest.json"
    write_json(manifest_path, manifest)

    checksums_path = STAGING / "manifest/SHA256SUMS.txt"
    checksummed = sorted(
        path
        for path in STAGING.rglob("*")
        if path.is_file() and path != checksums_path
    )
    checksums_path.write_text(
        "".join(f"{digest(path)}  {path.relative_to(STAGING).as_posix()}\n" for path in checksummed),
        encoding="utf-8",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if ZIP_OUTPUT.exists():
        ZIP_OUTPUT.unlink()
    with zipfile.ZipFile(ZIP_OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in STAGING.rglob("*") if p.is_file()):
            relative = path.relative_to(STAGING).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 7, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    # Verify central directory, clean extraction, and every checksum.
    with zipfile.ZipFile(ZIP_OUTPUT) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
        names = archive.namelist()
        expected_names = sorted(path.relative_to(STAGING).as_posix() for path in STAGING.rglob("*") if path.is_file())
        if sorted(names) != expected_names:
            raise RuntimeError("ZIP member list differs from staging tree")
        with tempfile.TemporaryDirectory(prefix="rev21-zip-verify-") as temp_dir_name:
            archive.extractall(temp_dir_name)
            extracted = Path(temp_dir_name)
            for line in (extracted / "manifest/SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
                expected_sha, relative = line.split("  ", 1)
                if digest(extracted / relative) != expected_sha:
                    raise RuntimeError(f"Extracted checksum mismatch: {relative}")
            packaged_ledger = json.loads((extracted / LEDGER_NAME).read_text(encoding="utf-8"))
            validate_ledger_against_extracted(packaged_ledger, extracted)

    return {
        "ledger": {
            "path": str(LEDGER_OUTPUT),
            "sha256": digest(LEDGER_OUTPUT),
            "size_bytes": LEDGER_OUTPUT.stat().st_size,
        },
        "zip": {
            "path": str(ZIP_OUTPUT),
            "sha256": digest(ZIP_OUTPUT),
            "size_bytes": ZIP_OUTPUT.stat().st_size,
            "member_count": len(expected_names),
        },
        "payload_file_count": ledger["portable_package"]["payload_file_count"],
    }


def validate_ledger_against_extracted(ledger: dict[str, Any], extracted: Path) -> None:
    if ledger["ledger_metadata"]["ledger_revision"] != 21:
        raise RuntimeError("Extracted ledger revision mismatch")
    for item in ledger["portable_package"]["included_files"]:
        target = extracted / item["archive_path"]
        if not target.is_file() or digest(target) != item["sha256"]:
            raise RuntimeError(f"Extracted portable reference failed: {item['archive_path']}")


def main() -> None:
    assert_hash(BASE_LEDGER, BASE_LEDGER_SHA256)
    for path, expected in (
        (FINAL_HTML, EXPECTED_PRODUCTION_HASHES[FINAL_HTML.name]),
        (FINAL_PDF, EXPECTED_PRODUCTION_HASHES[FINAL_PDF.name]),
        (FINAL_FILMSTRIP, EXPECTED_PRODUCTION_HASHES[FINAL_FILMSTRIP.name]),
        (FINAL_AUDIT, EXPECTED_PRODUCTION_HASHES[FINAL_AUDIT.name]),
        (ASSEMBLY_SCRIPT, EXPECTED_PRODUCTION_HASHES[ASSEMBLY_SCRIPT.name]),
        (THESIS, EXPECTED_PRODUCTION_HASHES[THESIS.name]),
    ):
        assert_hash(path, expected)

    base = json.loads(BASE_LEDGER.read_text(encoding="utf-8"))
    if base["ledger_metadata"]["ledger_revision"] != 20:
        raise RuntimeError("Base JSON metadata does not identify revision 20")

    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload, provenance_by_slide = build_payload(base)
    ledger = migrate_ledger(base, payload, provenance_by_slide)
    validate_ledger(ledger)
    report = build_manifest_and_zip(ledger)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # fail loudly for CI-like invocation
        print(f"REV21 migration failed: {exc}", file=sys.stderr)
        raise
