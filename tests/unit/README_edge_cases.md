# Edge Case Testing Patterns

## Purpose

Edge case testing ensures pipeline handles unusual data scenarios gracefully.

## Common Edge Cases

1. Empty Datasets: DataFrame with no rows
2. Single Row DataFrames: DataFrame with one row
3. All-Null Columns: All values are null
4. Boundary Values: Min/max values for types
5. Type Extremes: Maximum values for types
6. Missing Files: File not found errors

## Parametrization

Use `@pytest.mark.parametrize` for multiple edge cases:
```python
@pytest.mark.parametrize("edge_case,expected", [
    ("empty", "handle gracefully"),
    ("single", "process correctly"),
])
def test_edge_cases(edge_case, expected):
    # Implementation
```

## Checklist

- Empty DataFrame
- Single row DataFrame
- Boundary values (min/max)
- Type extremes
- Missing/null values
- Use @pytest.mark.parametrize
