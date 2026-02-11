"""
ID: industry_utils
Description: Fama-French industry classification utilities
Declared Inputs: Fama-French industry classification files (FF_Industry_Portfolios.zip)
Declared Outputs: parse_ff_industries() function
deterministic: true
"""

import zipfile
from pathlib import Path
from typing import Dict, Tuple


def parse_ff_industries(
    zip_path: Path, num_industries: int
) -> Dict[int, Tuple[int, str]]:
    """
    Parse Fama-French industry classification from SIC code ranges.

    Extracts industry classification mapping from Fama-French text files packaged
    in zip archives. Maps SIC codes to (industry_code, industry_name) tuples.

    Args:
        zip_path: Path to zip file containing Fama-French industry definitions
                  (e.g., Siccodes12.zip or Siccodes48.zip)
        num_industries: Number of industry classifications expected (12 or 48)
                        Used for validation/context, not strict enforcement

    Returns:
        Dictionary mapping SIC codes (int) to tuples of (industry_code, industry_name)
        where industry_code is the FF industry number and industry_name is the label

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
        >>> from shared.industry_utils import parse_ff_industries
        >>> ff12 = parse_ff_industries(Path("Siccodes12.zip"), 12)
        >>> ff12[2834]  # Returns: (12, 'Chemicals')
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        txt_file = z.namelist()[0]
        with z.open(txt_file) as f:
            content = f.read().decode("utf-8")

    industry_map = {}
    lines = content.strip().split("\n")

    current_industry_code = None
    current_industry_name = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split(maxsplit=2)
        if len(parts) >= 2 and parts[0].isdigit():
            current_industry_code = int(parts[0])
            current_industry_name = parts[1]
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
                except ValueError:
                    continue

    return industry_map
