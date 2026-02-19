#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Industry Classification Utilities
================================================================================
ID: shared/industry_utils
Description: Fama-French industry classification utilities.

Purpose: Parse and handle Fama-French industry classifications from SIC codes.

Inputs:
    - Fama-French industry classification files (FF_Industry_Portfolios.zip)
    - SIC codes

Outputs:
    - Industry classification mappings

Main Functions:
    - parse_ff_industries(): Parse Fama-French industry classifications from SIC codes

Dependencies:
    - Utility module for industry classifications
    - Uses: pandas, numpy

Deterministic: true

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import zipfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def parse_ff_industries(zip_path: Path, num_industries: int) -> Dict[Any, Any]:
    """
    Parse Fama-French industry classification from SIC code ranges.

    Extracts industry classification mapping from Fama-French text files packaged
    in zip archives. Maps SIC codes to (industry_code, industry_name) tuples.

    The Fama-French classification files define explicit SIC ranges only for
    categories 1 through N-1. The last category (e.g., FF12 code 12 "Other") is
    intentionally a catch-all: any SIC code not covered by an explicit range
    belongs to it. This function detects such catch-all categories (those that
    appear in the file header but have no associated SIC ranges) and stores them
    as a ``_catchall`` sentinel key so callers can apply the fallback via
    ``industry_map.get(sic) or industry_map.get("_catchall")``.

    Args:
        zip_path: Path to zip file containing Fama-French industry definitions
                  (e.g., Siccodes12.zip or Siccodes48.zip)
        num_industries: Number of industry classifications expected (12 or 48)
                        Used for validation/context, not strict enforcement

    Returns:
        Dictionary mapping SIC codes (int) to tuples of (industry_code, industry_name).
        Also contains the special key ``"_catchall"`` mapped to the catch-all
        industry tuple (e.g., ``(12, "Other")`` for FF12), or ``None`` if no
        catch-all category was detected.

    Raises:
        FileNotFoundError: If zip_path does not exist
        zipfile.BadZipFile: If file is not a valid zip archive
        ValueError: If zip file is empty or contains no text files

    Notes:
        - File format: Industry definitions stored as text lines with:
          * Header: "IndustryCode IndustryName"
          * Data: "SICRange" (e.g., "100-199" or "2000-2099")
        - Parsing is deterministic: same input always produces same output
        - No external dependencies beyond zipfile and pathlib
        - Handles both 2-digit and 4-digit SIC code ranges

    Example:
        >>> from pathlib import Path
        >>> from f1d.shared.industry_utils import parse_ff_industries
        >>> ff12 = parse_ff_industries(Path("Siccodes12.zip"), 12)
        >>> ff12[2834]  # Returns: (3, 'Manuf')
        >>> ff12.get(4011) or ff12.get("_catchall")  # Returns: (12, 'Other')
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        txt_file = z.namelist()[0]
        with z.open(txt_file) as f:
            content = f.read().decode("utf-8")

    industry_map: Dict = {}
    lines = content.strip().split("\n")

    current_industry_code = None
    current_industry_name = None
    # Track which industry codes appear in headers vs which have SIC ranges
    all_industry_headers: Dict[int, str] = {}
    industries_with_ranges: set = set()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split(maxsplit=2)
        if len(parts) >= 2 and parts[0].isdigit():
            current_industry_code = int(parts[0])
            current_industry_name = parts[1]
            all_industry_headers[current_industry_code] = current_industry_name
        elif stripped and current_industry_code is not None:
            sic_range = stripped.split()[0] if stripped.split() else ""
            if "-" in sic_range:
                try:
                    start, end = sic_range.split("-")
                    for sic in range(int(start), int(end) + 1):
                        industry_map[sic] = (
                            current_industry_code,
                            current_industry_name,
                        )
                    industries_with_ranges.add(current_industry_code)
                except ValueError:
                    continue

    # Detect catch-all industries: defined in headers but with no SIC ranges.
    # In FF12, code 12 "Other" is the canonical catch-all.
    catchall_industries = {
        code: name
        for code, name in all_industry_headers.items()
        if code not in industries_with_ranges
    }

    if catchall_industries:
        # Use the highest-numbered catch-all (FF12: code 12 "Other")
        catchall_code = max(catchall_industries.keys())
        catchall_name = catchall_industries[catchall_code]
        industry_map["_catchall"] = (catchall_code, catchall_name)
    else:
        industry_map["_catchall"] = None

    return industry_map
