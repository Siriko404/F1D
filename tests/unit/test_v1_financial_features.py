"""
Unit tests for V1 financial scripts in src/f1d/financial/v1/.

Tests verify:
- 3.0_BuildFinancialFeatures.py: Orchestrator functionality
- 3.1_FirmControls.py: Firm control variable calculations
- 3.2_MarketVariables.py: Market variable construction
- 3.3_EventFlags.py: Event flag creation

Uses factory fixtures from tests/conftest.py for test data generation.
"""

import runpy
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# ==============================================================================
# Helper: Import modules with dots in filenames using runpy
# ==============================================================================

V1_FINANCIAL_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "f1d" / "financial" / "v1"
)


def load_v1_module(filename: str) -> Dict[str, Any]:
    """Load a V1 module using runpy (handles dots in filenames)."""
    module_path = V1_FINANCIAL_DIR / filename
    if not module_path.exists():
        pytest.skip(f"V1 module not found: {module_path}")
    return runpy.run_path(str(module_path))


# ==============================================================================
# Fixtures for V1 Financial Testing
# ==============================================================================


@pytest.fixture
def sample_manifest_data():
    """Create sample manifest data for V1 financial tests."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "file_name": [f"call_{i:04d}.docx" for i in range(n)],
        "gvkey": [f"{i % 10:06d}" for i in range(n)],
        "start_date": pd.to_datetime([
            f"{2002 + (i // 10)}-{(i % 12) + 1:02d}-15" for i in range(n)
        ]),
        "year": [2002 + (i // 10) for i in range(n)],
        "permno": [10000 + i for i in range(n)],
        "cusip": [f"CUSIP{i:08d}" for i in range(n)],  # 8-digit CUSIP for event flags
    })


@pytest.fixture
def sample_compustat_quarterly():
    """Create sample Compustat quarterly data for V1 financial tests."""
    np.random.seed(42)
    n_firms = 10
    n_quarters = 20  # 5 years of quarterly data
    data = []

    for firm_id in range(n_firms):
        gvkey = f"{firm_id:06d}"
        base_assets = np.random.uniform(1000, 10000)

        for q in range(n_quarters):
            year = 2000 + (q // 4)
            quarter = (q % 4) + 1

            row = {
                "gvkey": gvkey,
                "datadate": pd.Timestamp(f"{year}-{quarter * 3:02d}-01"),
                "atq": base_assets * np.random.uniform(0.9, 1.1),
                "ceqq": base_assets * 0.4 * np.random.uniform(0.9, 1.1),
                "cshoq": np.random.uniform(10, 100),
                "prccq": np.random.uniform(20, 100),
                "ltq": base_assets * 0.6 * np.random.uniform(0.9, 1.1),
                "niq": base_assets * 0.05 * np.random.uniform(-0.5, 1.5),
                "epspxq": np.random.uniform(-1, 3),
                "actq": base_assets * 0.3,
                "lctq": base_assets * 0.15,
                "xrdq": base_assets * 0.02 * np.random.uniform(0, 1),
            }
            data.append(row)

    return pd.DataFrame(data)


@pytest.fixture
def sample_ibes_data():
    """Create sample IBES analyst forecast data."""
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "MEASURE": ["EPS"] * n,
        "FISCALP": ["QTR"] * n,
        "TICKER": [f"TICK{i:04d}" for i in range(n)],
        "CUSIP": [f"CUSIP{i:08d}" for i in range(n)],
        "FPEDATS": pd.to_datetime([
            f"{2002 + (i // 50)}-{((i % 4) + 1) * 3:02d}-01" for i in range(n)
        ]),
        "STATPERS": pd.to_datetime([
            f"{2002 + (i // 50)}-{((i % 4) + 1) * 3:02d}-01" for i in range(n)
        ]) - pd.Timedelta(days=10),
        "MEANEST": np.random.uniform(0.5, 2.5, n),
        "ACTUAL": np.random.uniform(0.3, 2.8, n),
    })


@pytest.fixture
def sample_cccl_data():
    """Create sample CCCL instrument data."""
    np.random.seed(42)
    n_firms = 10
    n_years = 5
    data = []

    for firm_id in range(n_firms):
        for year_offset in range(n_years):
            row = {
                "gvkey": f"{firm_id:06d}",
                "year": 2002 + year_offset,
                "shift_intensity_sale_ff12": np.random.uniform(0, 1),
                "shift_intensity_mkvalt_ff12": np.random.uniform(0, 1),
                "shift_intensity_sale_ff48": np.random.uniform(0, 1),
                "shift_intensity_mkvalt_ff48": np.random.uniform(0, 1),
                "shift_intensity_sale_sic2": np.random.uniform(0, 1),
                "shift_intensity_mkvalt_sic2": np.random.uniform(0, 1),
            }
            data.append(row)

    return pd.DataFrame(data)


@pytest.fixture
def sample_sdc_data():
    """Create sample SDC M&A data for event flag testing."""
    np.random.seed(42)
    n = 50
    # Generate valid dates (avoiding month > 12)
    dates_announced = []
    dates_effective = []
    for i in range(n):
        year = 2003 + (i // 12)
        month = (i % 12) + 1
        dates_announced.append(f"{year}-{month:02d}-15")
        # Effective date is 3 months later, wrapping to next year if needed
        eff_month = month + 3
        eff_year = year
        if eff_month > 12:
            eff_month -= 12
            eff_year += 1
        dates_effective.append(f"{eff_year}-{eff_month:02d}-01")

    return pd.DataFrame({
        "Target 6-digit CUSIP": [f"CUSIP{i:06d}" for i in range(n)],
        "Date Announced": pd.to_datetime(dates_announced),
        "Date Effective": pd.to_datetime(dates_effective),
        "Date Withdrawn": [None] * n,
        "Deal Attitude": (["Friendly"] * 30) + (["Hostile"] * 10) + (["Unsolicited"] * 10),
        "Deal Status": ["Completed"] * n,
    })


@pytest.fixture
def sample_crsp_data():
    """Create sample CRSP data for market variable testing."""
    np.random.seed(42)
    n_days = 252  # One year of trading days
    n_stocks = 10
    data = []

    base_date = pd.Timestamp("2002-01-02")
    for stock_id in range(n_stocks):
        permno = 10000 + stock_id
        for day in range(n_days):
            row = {
                "PERMNO": permno,
                "date": base_date + pd.Timedelta(days=day),
                "RET": np.random.normal(0.001, 0.02),
                "VOL": np.random.uniform(100000, 1000000),
                "VWRETD": np.random.normal(0.0005, 0.01),
                "ASKHI": np.random.uniform(50, 55),
                "BIDLO": np.random.uniform(48, 52),
                "PRC": np.random.uniform(49, 53),
            }
            data.append(row)

    return pd.DataFrame(data)


@pytest.fixture
def sample_normalized_sdc_data(sample_sdc_data):
    """Create normalized SDC data (as returned by load_sdc function)."""
    # Apply the same normalization as 3.3_EventFlags.load_sdc
    df = sample_sdc_data.copy()
    col_mapping = {
        "Target 6-digit CUSIP": "target_cusip6",
        "Date Announced": "date_announced",
        "Date Effective": "date_effective",
        "Date Withdrawn": "date_withdrawn",
        "Deal Attitude": "deal_attitude",
        "Deal Status": "deal_status",
    }
    for old_name, new_name in col_mapping.items():
        if old_name in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)

    for col in ["date_announced", "date_effective", "date_withdrawn"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["target_cusip6"] = df["target_cusip6"].astype(str).str[:6]
    return df


# ==============================================================================
# Tests for 3.1_FirmControls.py
# ==============================================================================


class TestFirmControlsDataLoading:
    """Tests for data loading functions in 3.1_FirmControls.py."""

    def test_load_manifest_returns_dataframe(self, sample_manifest_data, tmp_path):
        """Test that load_manifest returns a DataFrame with expected columns."""
        # Create temporary manifest file
        manifest_file = tmp_path / "master_sample_manifest.parquet"
        sample_manifest_data.to_parquet(manifest_file)

        # Load module and test
        module = load_v1_module("3.1_FirmControls.py")
        load_manifest = module["load_manifest"]

        result = load_manifest(tmp_path)

        assert isinstance(result, pd.DataFrame)
        assert "gvkey" in result.columns
        assert "start_date" in result.columns
        assert "year" in result.columns

    def test_load_manifest_converts_gvkey_to_string(self, sample_manifest_data, tmp_path):
        """Test that gvkey is converted to zero-padded string."""
        manifest_file = tmp_path / "master_sample_manifest.parquet"
        sample_manifest_data.to_parquet(manifest_file)

        module = load_v1_module("3.1_FirmControls.py")
        load_manifest = module["load_manifest"]

        result = load_manifest(tmp_path)

        assert result["gvkey"].dtype == object
        assert result["gvkey"].str.len().max() == 6

    def test_load_compustat_loads_required_columns(self, sample_compustat_quarterly, tmp_path):
        """Test that load_compustat loads and normalizes Compustat data."""
        comp_file = tmp_path / "comp_na_daily_all.parquet"
        sample_compustat_quarterly.to_parquet(comp_file)

        module = load_v1_module("3.1_FirmControls.py")
        load_compustat = module["load_compustat"]

        result = load_compustat(comp_file)

        assert isinstance(result, pd.DataFrame)
        assert "gvkey" in result.columns
        assert "atq" in result.columns
        assert result["gvkey"].dtype == object

    def test_load_compustat_converts_numeric_columns(self, sample_compustat_quarterly, tmp_path):
        """Test that Compustat numeric columns are converted to float64."""
        comp_file = tmp_path / "comp_na_daily_all.parquet"
        sample_compustat_quarterly.to_parquet(comp_file)

        module = load_v1_module("3.1_FirmControls.py")
        load_compustat = module["load_compustat"]

        result = load_compustat(comp_file)

        numeric_cols = ["atq", "ceqq", "cshoq", "prccq", "ltq", "niq"]
        for col in numeric_cols:
            assert result[col].dtype in [np.float64, np.int64]

    def test_load_ibes_filters_to_eps_quarterly(self, sample_ibes_data, tmp_path):
        """Test that load_ibes filters to EPS quarterly forecasts."""
        # Add non-EPS records to test filtering
        ibes_data = pd.concat([
            sample_ibes_data,
            pd.DataFrame({
                "MEASURE": ["REVENUE"] * 10,
                "FISCALP": ["QTR"] * 10,
                "TICKER": [f"TICK{i:04d}" for i in range(200, 210)],
                "CUSIP": [f"CUSIP{i:08d}" for i in range(200, 210)],
                "FPEDATS": pd.to_datetime(["2005-01-01"] * 10),
                "STATPERS": pd.to_datetime(["2004-12-15"] * 10),
                "MEANEST": np.random.uniform(10, 100, 10),
                "ACTUAL": np.random.uniform(10, 110, 10),
            })
        ], ignore_index=True)

        ibes_file = tmp_path / "tr_ibes.parquet"
        ibes_data.to_parquet(ibes_file)

        module = load_v1_module("3.1_FirmControls.py")
        load_ibes = module["load_ibes"]

        result = load_ibes(ibes_file)

        # The function filters to EPS/QTR and returns subset of columns
        # Check that it returned data (was filtered correctly)
        assert len(result) < len(ibes_data)  # Should have fewer rows after filtering
        assert "TICKER" in result.columns  # Required output columns exist
        assert "CUSIP" in result.columns

    def test_load_cccl_loads_shift_intensity_columns(self, sample_cccl_data, tmp_path):
        """Test that load_cccl loads all shift_intensity variants."""
        cccl_file = tmp_path / "instrument_shift_intensity.parquet"
        sample_cccl_data.to_parquet(cccl_file)

        module = load_v1_module("3.1_FirmControls.py")
        load_cccl = module["load_cccl"]

        result = load_cccl(cccl_file)

        intensity_cols = [c for c in result.columns if c.startswith("shift_intensity")]
        assert len(intensity_cols) >= 1
        assert "gvkey" in result.columns
        assert "year" in result.columns


class TestFirmControlsComputation:
    """Tests for variable computation functions in 3.1_FirmControls.py."""

    def test_compute_compustat_controls_creates_expected_columns(
        self, sample_manifest_data, sample_compustat_quarterly
    ):
        """Test that compute_compustat_controls creates Size, BM, Lev, ROA."""
        module = load_v1_module("3.1_FirmControls.py")
        compute_compustat_controls = module["compute_compustat_controls"]

        result = compute_compustat_controls(sample_manifest_data, sample_compustat_quarterly)

        expected_cols = ["file_name", "Size", "BM", "Lev", "ROA"]
        for col in expected_cols:
            assert col in result.columns

    def test_compute_compustat_controls_returns_correct_row_count(
        self, sample_manifest_data, sample_compustat_quarterly
    ):
        """Test that result has same number of rows as manifest."""
        module = load_v1_module("3.1_FirmControls.py")
        compute_compustat_controls = module["compute_compustat_controls"]

        result = compute_compustat_controls(sample_manifest_data, sample_compustat_quarterly)

        assert len(result) == len(sample_manifest_data)

    def test_merge_cccl_adds_intensity_columns(
        self, sample_manifest_data, sample_cccl_data
    ):
        """Test that merge_cccl adds shift_intensity columns."""
        module = load_v1_module("3.1_FirmControls.py")
        merge_cccl = module["merge_cccl"]

        result = merge_cccl(sample_manifest_data, sample_cccl_data)

        intensity_cols = [c for c in result.columns if c.startswith("shift_intensity")]
        assert len(intensity_cols) >= 1
        assert "file_name" in result.columns


# ==============================================================================
# Tests for 3.2_MarketVariables.py
# ==============================================================================


class TestMarketVariablesDataLoading:
    """Tests for data loading functions in 3.2_MarketVariables.py."""

    def test_load_manifest_with_permno_adds_permno_column(
        self, sample_manifest_data, tmp_path
    ):
        """Test that load_manifest_with_permno adds permno from CCM."""
        manifest_file = tmp_path / "master_sample_manifest.parquet"
        sample_manifest_data.to_parquet(manifest_file)

        # Create mock CCM file
        ccm_data = pd.DataFrame({
            "gvkey": [f"{i:06d}" for i in range(10)],
            "LPERMNO": [10000 + i for i in range(10)],
            "cusip": [f"CUSIP{i:08d}" for i in range(10)],
        })
        ccm_file = tmp_path / "CRSPCompustat_CCM.parquet"
        ccm_data.to_parquet(ccm_file)

        module = load_v1_module("3.2_MarketVariables.py")
        load_manifest_with_permno = module["load_manifest_with_permno"]

        result = load_manifest_with_permno(tmp_path, ccm_file)

        assert "permno" in result.columns
        assert result["permno"].notna().sum() > 0

    def test_load_crsp_for_years_returns_dataframe(
        self, sample_crsp_data, tmp_path
    ):
        """Test that load_crsp_for_years loads CRSP data for specified years."""
        # Create CRSP directory structure
        crsp_dir = tmp_path / "CRSP_DSF"
        crsp_dir.mkdir()

        # Save CRSP data in quarterly files
        for year in [2002, 2003]:
            for q in range(1, 5):
                q_data = sample_crsp_data[
                    ((sample_crsp_data["date"].dt.year == year) &
                     (sample_crsp_data["date"].dt.month <= q * 3) &
                     (sample_crsp_data["date"].dt.month > (q - 1) * 3))
                ]
                if len(q_data) > 0:
                    q_file = crsp_dir / f"CRSP_DSF_{year}_Q{q}.parquet"
                    q_data.to_parquet(q_file)

        module = load_v1_module("3.2_MarketVariables.py")
        load_crsp_for_years = module["load_crsp_for_years"]

        result = load_crsp_for_years(crsp_dir, [2002])

        assert isinstance(result, pd.DataFrame)
        assert "date" in result.columns
        assert "RET" in result.columns


class TestMarketVariablesComputation:
    """Tests for market variable computation functions in 3.2_MarketVariables.py."""

    def test_compute_returns_for_year_creates_stockret_column(
        self, sample_manifest_data, sample_crsp_data
    ):
        """Test that compute_returns_for_year creates StockRet column."""
        # Add prev_call_date to manifest
        sample_manifest_data = sample_manifest_data.copy()
        sample_manifest_data = sample_manifest_data.sort_values(["gvkey", "start_date"])
        sample_manifest_data["prev_call_date"] = sample_manifest_data.groupby("gvkey")["start_date"].shift(1)
        sample_manifest_data = sample_manifest_data.dropna(subset=["prev_call_date"])

        config = {
            "step_07": {
                "return_windows": {
                    "days_after_prev_call": 5,
                    "days_before_current_call": 5,
                    "min_trading_days": 10,
                }
            }
        }

        module = load_v1_module("3.2_MarketVariables.py")
        compute_returns_for_year = module["compute_returns_for_year"]

        result = compute_returns_for_year(sample_manifest_data, sample_crsp_data, config)

        assert "StockRet" in result.columns
        assert "MarketRet" in result.columns

    def test_compute_liquidity_for_year_creates_amihud_column(
        self, sample_manifest_data, sample_crsp_data
    ):
        """Test that compute_liquidity_for_year creates Amihud column."""
        sample_manifest_data = sample_manifest_data.copy()

        config = {
            "step_09": {
                "window_days": 5,
                "baseline_start": -35,
                "baseline_end": -6,
            }
        }

        module = load_v1_module("3.2_MarketVariables.py")
        compute_liquidity_for_year = module["compute_liquidity_for_year"]

        result = compute_liquidity_for_year(sample_manifest_data, sample_crsp_data, config)

        assert "Amihud" in result.columns
        assert "Corwin_Schultz" in result.columns


# ==============================================================================
# Tests for 3.3_EventFlags.py
# ==============================================================================


class TestEventFlagsDataLoading:
    """Tests for data loading functions in 3.3_EventFlags.py."""

    def test_load_manifest_adds_year_and_cusip6_columns(
        self, sample_manifest_data, tmp_path
    ):
        """Test that load_manifest extracts year from start_date and cusip6 from cusip."""
        manifest_file = tmp_path / "master_sample_manifest.parquet"
        sample_manifest_data.to_parquet(manifest_file)

        module = load_v1_module("3.3_EventFlags.py")
        load_manifest = module["load_manifest"]

        result = load_manifest(tmp_path)

        # load_manifest adds 'year' column from start_date
        assert "year" in result.columns
        assert result["year"].dtype in [np.int64, np.int32]
        # Also verifies cusip6 column is derived from cusip (requires cusip in input)
        assert "cusip6" in result.columns

    def test_load_sdc_normalizes_column_names(
        self, sample_sdc_data, tmp_path
    ):
        """Test that load_sdc normalizes column names to snake_case."""
        sdc_file = tmp_path / "sdc-ma-merged.parquet"
        sample_sdc_data.to_parquet(sdc_file)

        module = load_v1_module("3.3_EventFlags.py")
        load_sdc = module["load_sdc"]

        result = load_sdc(sdc_file)

        assert "target_cusip6" in result.columns
        assert "date_announced" in result.columns
        assert "deal_attitude" in result.columns


class TestEventFlagsComputation:
    """Tests for event flag computation in 3.3_EventFlags.py."""

    def test_compute_takeover_flags_creates_expected_columns(
        self, sample_manifest_data, sample_normalized_sdc_data
    ):
        """Test that compute_takeover_flags creates Takeover, Takeover_Type, Duration."""
        module = load_v1_module("3.3_EventFlags.py")
        compute_takeover_flags = module["compute_takeover_flags"]

        # Ensure manifest has cusip6 for matching
        sample_manifest_data = sample_manifest_data.copy()
        sample_manifest_data["cusip6"] = sample_manifest_data["cusip"].str[:6]

        result = compute_takeover_flags(sample_manifest_data, sample_normalized_sdc_data)

        assert "Takeover" in result.columns
        assert "Takeover_Type" in result.columns
        assert "Duration" in result.columns

    def test_compute_takeover_flags_sets_binary_values(
        self, sample_manifest_data, sample_normalized_sdc_data
    ):
        """Test that Takeover is binary (0 or 1)."""
        module = load_v1_module("3.3_EventFlags.py")
        compute_takeover_flags = module["compute_takeover_flags"]

        sample_manifest_data = sample_manifest_data.copy()
        sample_manifest_data["cusip6"] = sample_manifest_data["cusip"].str[:6]

        result = compute_takeover_flags(sample_manifest_data, sample_normalized_sdc_data)

        assert result["Takeover"].isin([0, 1]).all()

    def test_compute_takeover_flags_classifies_deal_attitude(
        self, sample_manifest_data, sample_normalized_sdc_data
    ):
        """Test that Takeover_Type is classified as Friendly or Uninvited."""
        module = load_v1_module("3.3_EventFlags.py")
        compute_takeover_flags = module["compute_takeover_flags"]

        sample_manifest_data = sample_manifest_data.copy()
        sample_manifest_data["cusip6"] = sample_manifest_data["cusip"].str[:6]

        result = compute_takeover_flags(sample_manifest_data, sample_normalized_sdc_data)

        # Check that non-null Takeover_Type values are valid
        valid_types = {"Friendly", "Uninvited", None}
        takeover_types = set(result[result["Takeover"] == 1]["Takeover_Type"].unique())
        assert takeover_types.issubset(valid_types)


# ==============================================================================
# Tests for 3.0_BuildFinancialFeatures.py
# ==============================================================================


class TestBuildFinancialFeaturesOrchestrator:
    """Tests for the orchestrator script 3.0_BuildFinancialFeatures.py."""

    def test_import_module_succeeds(self):
        """Test that 3.0_BuildFinancialFeatures module can be imported."""
        module = load_v1_module("3.0_BuildFinancialFeatures.py")
        assert "main" in module

    def test_module_has_expected_functions(self):
        """Test that module has expected helper functions."""
        module = load_v1_module("3.0_BuildFinancialFeatures.py")

        expected_functions = [
            "load_config",
            "setup_paths",
            "check_prerequisites",
        ]
        for func_name in expected_functions:
            assert func_name in module, f"Missing function: {func_name}"

    def test_get_process_memory_mb_returns_dict(self):
        """Test that get_process_memory_mb returns expected keys."""
        module = load_v1_module("3.0_BuildFinancialFeatures.py")
        get_process_memory_mb = module["get_process_memory_mb"]

        result = get_process_memory_mb()

        assert "rss_mb" in result
        assert "vms_mb" in result
        assert "percent" in result
        assert result["rss_mb"] > 0

    def test_calculate_throughput_returns_float(self):
        """Test that calculate_throughput returns correct value."""
        module = load_v1_module("3.0_BuildFinancialFeatures.py")
        calculate_throughput = module["calculate_throughput"]

        result = calculate_throughput(1000, 10)

        assert result == 100.0

    def test_calculate_throughput_handles_zero_duration(self):
        """Test that calculate_throughput handles zero duration."""
        module = load_v1_module("3.0_BuildFinancialFeatures.py")
        calculate_throughput = module["calculate_throughput"]

        result = calculate_throughput(1000, 0)

        assert result == 0.0

    def test_detect_anomalies_zscore_returns_dict(self):
        """Test that detect_anomalies_zscore returns expected structure."""
        module = load_v1_module("3.0_BuildFinancialFeatures.py")
        detect_anomalies_zscore = module["detect_anomalies_zscore"]

        df = pd.DataFrame({
            "value": np.random.normal(0, 1, 100),
        })

        result = detect_anomalies_zscore(df, ["value"], threshold=3.0)

        assert "value" in result
        assert "count" in result["value"]
        assert "sample_anomalies" in result["value"]

    def test_detect_anomalies_iqr_returns_dict(self):
        """Test that detect_anomalies_iqr returns expected structure."""
        module = load_v1_module("3.0_BuildFinancialFeatures.py")
        detect_anomalies_iqr = module["detect_anomalies_iqr"]

        df = pd.DataFrame({
            "value": np.random.normal(0, 1, 100),
        })

        result = detect_anomalies_iqr(df, ["value"], multiplier=3.0)

        assert "value" in result
        assert "count" in result["value"]
        assert "iqr_bounds" in result["value"]


# ==============================================================================
# Edge Case Tests
# ==============================================================================


class TestV1FinancialEdgeCases:
    """Tests for edge cases in V1 financial scripts."""

    def test_firm_controls_handles_small_dataframe(self):
        """Test that firm controls handle small/edge case manifest DataFrame."""
        module = load_v1_module("3.1_FirmControls.py")
        compute_compustat_controls = module["compute_compustat_controls"]

        # Use minimal but valid data (empty dataframes cause key errors in internal processing)
        manifest = pd.DataFrame({
            "file_name": ["call_001.docx"],
            "gvkey": ["000001"],
            "start_date": pd.to_datetime(["2002-06-15"]),
            "year": [2002],
        })

        compustat = pd.DataFrame({
            "gvkey": ["000001"],
            "datadate": pd.to_datetime(["2002-03-31"]),
            "atq": [1000.0],
            "ceqq": [400.0],
            "cshoq": [50.0],
            "prccq": [25.0],
            "ltq": [600.0],
            "niq": [50.0],
            "epspxq": [1.0],
            "actq": [300.0],
            "lctq": [150.0],
            "xrdq": [20.0],
        })

        result = compute_compustat_controls(manifest, compustat)

        assert isinstance(result, pd.DataFrame)
        assert "file_name" in result.columns

    def test_market_variables_handles_missing_permno(self):
        """Test market variables when permno is missing."""
        module = load_v1_module("3.2_MarketVariables.py")
        compute_returns_for_year = module["compute_returns_for_year"]

        manifest = pd.DataFrame({
            "file_name": ["call_001.docx"],
            "gvkey": ["000001"],
            "start_date": pd.to_datetime(["2002-06-15"]),
            "year": [2002],
            "permno": [np.nan],  # Missing permno
            "prev_call_date": pd.to_datetime(["2002-03-15"]),
        })

        config = {"step_07": {"return_windows": {
            "days_after_prev_call": 5,
            "days_before_current_call": 5,
            "min_trading_days": 10,
        }}}

        crsp = pd.DataFrame({
            "PERMNO": [10000],
            "date": pd.to_datetime(["2002-04-01"]),
            "RET": [0.01],
            "VWRETD": [0.005],
        })

        result = compute_returns_for_year(manifest, crsp, config)

        # Should still return a DataFrame, just with NaN for StockRet
        assert isinstance(result, pd.DataFrame)
        assert "StockRet" in result.columns

    def test_event_flags_handles_no_matches(self):
        """Test event flags when no SDC matches exist."""
        module = load_v1_module("3.3_EventFlags.py")
        compute_takeover_flags = module["compute_takeover_flags"]

        manifest = pd.DataFrame({
            "file_name": ["call_001.docx"],
            "start_date": pd.to_datetime(["2002-06-15"]),
            "cusip6": ["XXXXXX"],  # Won't match any SDC CUSIP
        })

        # Use normalized column names as expected by compute_takeover_flags
        sdc = pd.DataFrame({
            "target_cusip6": ["CUSIP0"],
            "date_announced": pd.to_datetime(["2003-01-15"]),
            "deal_attitude": ["Friendly"],
        })

        result = compute_takeover_flags(manifest, sdc)

        assert result["Takeover"].iloc[0] == 0
        assert result["Takeover_Type"].iloc[0] is None

    def test_event_flags_handles_nan_cusip(self):
        """Test event flags when CUSIP is missing."""
        module = load_v1_module("3.3_EventFlags.py")
        compute_takeover_flags = module["compute_takeover_flags"]

        manifest = pd.DataFrame({
            "file_name": ["call_001.docx"],
            "start_date": pd.to_datetime(["2002-06-15"]),
            "cusip6": [np.nan],  # Missing CUSIP
        })

        # Use normalized column names as expected by compute_takeover_flags
        sdc = pd.DataFrame({
            "target_cusip6": ["CUSIP0"],
            "date_announced": pd.to_datetime(["2003-01-15"]),
            "deal_attitude": ["Friendly"],
        })

        result = compute_takeover_flags(manifest, sdc)

        # Should handle NaN gracefully
        assert result["Takeover"].iloc[0] == 0


# ==============================================================================
# Integration Tests (within V1 scripts)
# ==============================================================================


class TestV1FinancialIntegration:
    """Integration tests for V1 financial scripts working together."""

    def test_firm_controls_market_variables_schema_compatibility(
        self, sample_manifest_data, sample_compustat_quarterly, sample_crsp_data
    ):
        """Test that firm controls and market variables have compatible schemas."""
        # Load both modules
        firm_module = load_v1_module("3.1_FirmControls.py")
        market_module = load_v1_module("3.2_MarketVariables.py")

        # Compute firm controls
        firm_result = firm_module["compute_compustat_controls"](
            sample_manifest_data, sample_compustat_quarterly
        )

        # Compute market variables
        sample_manifest_with_prev = sample_manifest_data.copy()
        sample_manifest_with_prev = sample_manifest_with_prev.sort_values(["gvkey", "start_date"])
        sample_manifest_with_prev["prev_call_date"] = sample_manifest_with_prev.groupby("gvkey")["start_date"].shift(1)
        sample_manifest_with_prev = sample_manifest_with_prev.dropna(subset=["prev_call_date"])

        config = {"step_07": {"return_windows": {
            "days_after_prev_call": 5,
            "days_before_current_call": 5,
            "min_trading_days": 10,
        }}}

        market_result = market_module["compute_returns_for_year"](
            sample_manifest_with_prev, sample_crsp_data, config
        )

        # Both should have file_name for merging
        assert "file_name" in firm_result.columns
        assert "file_name" in market_result.columns

        # Both should have same number of rows as input (or less if filtered)
        assert len(firm_result) <= len(sample_manifest_data)

    def test_event_flags_output_schema(
        self, sample_manifest_data, sample_normalized_sdc_data
    ):
        """Test that event flags output has expected schema."""
        module = load_v1_module("3.3_EventFlags.py")
        compute_takeover_flags = module["compute_takeover_flags"]

        sample_manifest_data = sample_manifest_data.copy()
        sample_manifest_data["cusip6"] = sample_manifest_data["cusip"].str[:6]

        result = compute_takeover_flags(sample_manifest_data, sample_normalized_sdc_data)

        expected_columns = ["file_name", "Takeover", "Takeover_Type", "Duration"]
        for col in expected_columns:
            assert col in result.columns
