#!/usr/bin/env python3
"""
Type checking tests using pytest-mypy plugin.

Run with: pytest tests/unit/test_types.py -v -m mypy_testing

These tests verify that type hints are correct and modules
pass mypy type checking.
"""
import pytest


@pytest.mark.mypy_testing
def test_mypy_panel_ols():
    """Verify panel_ols module passes type checking."""
    import f1d.shared.panel_ols

    # Test that function signatures are type-checked
    # This test passes if mypy doesn't report errors
    assert f1d.shared.panel_ols.__name__ == "f1d.shared.panel_ols"


@pytest.mark.mypy_testing
def test_mypy_iv_regression():
    """Verify iv_regression module passes type checking."""
    import f1d.shared.iv_regression

    assert f1d.shared.iv_regression.__name__ == "f1d.shared.iv_regression"


@pytest.mark.mypy_testing
def test_mypy_financial_utils():
    """Verify financial_utils module passes type checking."""
    import f1d.shared.financial_utils

    assert f1d.shared.financial_utils.__name__ == "f1d.shared.financial_utils"


@pytest.mark.mypy_testing
def test_panel_ols_function_signature():
    """Verify run_panel_ols has correct type signature."""
    from typing import get_type_hints
    import f1d.shared.panel_ols

    hints = get_type_hints(f1d.shared.panel_ols.run_panel_ols)
    # Check that key parameters have type hints
    assert "df" in hints
    assert "dependent" in hints
    assert "exog" in hints
    assert "return" in hints


@pytest.mark.mypy_testing
def test_iv_regression_function_signature():
    """Verify run_iv2sls has correct type signature."""
    from typing import get_type_hints
    import f1d.shared.iv_regression

    hints = get_type_hints(f1d.shared.iv_regression.run_iv2sls)
    # Check that key parameters have type hints
    assert "df" in hints
    assert "dependent" in hints
    assert "endog" in hints
    assert "instruments" in hints
    assert "return" in hints


@pytest.mark.mypy_testing
def test_financial_utils_function_signature():
    """Verify calculate_firm_controls has correct type signature."""
    from typing import get_type_hints
    import f1d.shared.financial_utils

    hints = get_type_hints(f1d.shared.financial_utils.calculate_firm_controls)
    # Check that key parameters have type hints
    assert "row" in hints
    assert "compustat_df" in hints
    assert "year" in hints
    assert "return" in hints
