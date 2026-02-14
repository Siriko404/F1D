
import pytest
import pandas as pd


class TestPermnoMatching:
    """Tests for PERMNO-based matching."""

    def test_match_exact_permno(self):
        """Test exact PERMNO match works."""
        test_df = pd.DataFrame({
            "PERMNO": ["12345", "67890", "54321"],
            "company_name": ["Company A", "Company B", "Company C"]
        })

        lookup_df = pd.DataFrame({
            "PERMNO": ["12345", "67890", "99999"],
            "gvkey": ["001234", "005678", "009999"],
            "company_name": ["Company A", "Company B", "Unknown Co"]
        })

        result = test_df.merge(
            lookup_df,
            left_on="PERMNO",
            right_on="PERMNO",
            how="left"
        )

        assert len(result[result["gvkey"].notna()]) == 2
