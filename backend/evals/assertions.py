"""
Assertion functions for CFG SQL evaluation.
Each function returns (passed: bool, message: str)
"""
from typing import Tuple, Dict, Any, List, Optional


# ============================================
# Grammar Syntax Assertions
# ============================================

def assert_sql_executes(response: Dict[str, Any]) -> Tuple[bool, str]:
    """Assert that SQL executed without errors"""
    if response.get("error"):
        return False, f"SQL execution error: {response['error']}"

    if response.get("results") is None:
        return False, "SQL did not return results"

    return True, "SQL executed successfully"


def assert_sql_parseable(response: Dict[str, Any]) -> Tuple[bool, str]:
    """Assert that SQL was generated (CFG parsing succeeded)"""
    sql = response.get("generated_sql", "")

    if not sql or not isinstance(sql, str):
        return False, "No SQL generated - CFG may have failed to parse"

    if len(sql.strip()) == 0:
        return False, "Generated SQL is empty"

    # Check it looks like SQL
    if not sql.strip().upper().startswith("SELECT"):
        return False, f"Generated text doesn't look like SQL: {sql[:50]}"

    return True, f"SQL parseable: {sql[:80]}..."


def assert_valid_table_name(response: Dict[str, Any]) -> Tuple[bool, str]:
    """Assert SQL references the correct table"""
    sql = response.get("generated_sql", "").upper()

    if "GARMIN_ACTIVE_CAL_DATA" not in sql:
        return False, f"SQL doesn't reference garmin_active_cal_data table"

    return True, "SQL references correct table"


def assert_valid_columns(response: Dict[str, Any]) -> Tuple[bool, str]:
    """Assert SQL only uses valid columns from grammar"""
    valid_columns = {
        "TIMESTAMP_DAY", "ACTIVE_CALORIES", "ACTIVE_TIME",
        "DISTANCE", "ACTIVITY_TYPE", "DURATION_MIN", "STEPS"
    }

    sql = response.get("generated_sql", "").upper()

    # Simple check - look for invalid column patterns
    # This is a heuristic, not perfect
    for word in sql.split():
        # Clean up punctuation
        word = word.strip("(),")
        # If it looks like a column (not a keyword) and not valid
        if (word.isalnum() and
            word not in {"SELECT", "FROM", "WHERE", "ORDER", "BY", "LIMIT", "AND", "ASC", "DESC"} and
            word not in valid_columns and
            not word.isdigit()):
            # Could be a function like SUM, COUNT, etc - allow those
            if word not in {"SUM", "AVG", "COUNT", "MAX", "MIN", "TODAY", "TOINTERVALDAY"}:
                return False, f"SQL may contain invalid column: {word}"

    return True, "SQL uses valid columns"


# ============================================
# Semantic Correctness Assertions
# ============================================

def assert_correct_aggregation(
    response: Dict[str, Any],
    expected: str
) -> Tuple[bool, str]:
    """Assert SQL uses the expected aggregation function"""
    sql = response.get("generated_sql", "").upper()
    expected_upper = expected.upper()

    if expected_upper not in sql:
        return False, f"Expected {expected} aggregation not found in SQL"

    return True, f"SQL correctly uses {expected} aggregation"


def assert_correct_columns(
    response: Dict[str, Any],
    columns: List[str]
) -> Tuple[bool, str]:
    """Assert SQL selects the expected columns"""
    sql = response.get("generated_sql", "").upper()

    for col in columns:
        col_upper = col.upper()
        if col_upper not in sql:
            return False, f"Expected column '{col}' not found in SQL"

    return True, f"SQL contains expected columns: {', '.join(columns)}"


def assert_correct_where_clause(
    response: Dict[str, Any],
    expected_conditions: List[str]
) -> Tuple[bool, str]:
    """Assert WHERE clause contains expected conditions"""
    sql = response.get("generated_sql", "").upper()

    if not expected_conditions:
        return True, "No WHERE conditions to check"

    if "WHERE" not in sql:
        return False, "Expected WHERE clause not found in SQL"

    for condition in expected_conditions:
        condition_upper = condition.upper()
        if condition_upper not in sql:
            return False, f"Expected condition '{condition}' not found in WHERE clause"

    return True, f"WHERE clause contains expected conditions"


def assert_correct_sort(
    response: Dict[str, Any],
    expected_direction: str
) -> Tuple[bool, str]:
    """Assert ORDER BY uses correct direction (ASC/DESC)"""
    sql = response.get("generated_sql", "").upper()
    expected_upper = expected_direction.upper()

    if "ORDER BY" not in sql:
        return False, "No ORDER BY clause found"

    if expected_upper not in sql:
        return False, f"Expected sort direction '{expected_direction}' not found"

    return True, f"SQL sorts with {expected_direction}"


# ============================================
# Result Accuracy Assertions
# ============================================

def assert_non_empty_results(response: Dict[str, Any]) -> Tuple[bool, str]:
    """Assert query returned at least one result"""
    results = response.get("results", {})
    rows = results.get("rows", [])

    if not rows or len(rows) == 0:
        return False, "Expected non-empty results but got no rows"

    return True, f"Results contain {len(rows)} row(s)"


def assert_empty_results(response: Dict[str, Any]) -> Tuple[bool, str]:
    """Assert query returned no results (for impossible conditions)"""
    results = response.get("results", {})
    rows = results.get("rows", [])

    if rows and len(rows) > 0:
        return False, f"Expected empty results but got {len(rows)} rows"

    return True, "Results correctly empty"


def assert_result_count(
    response: Dict[str, Any],
    expected: int
) -> Tuple[bool, str]:
    """Assert exact number of results returned"""
    results = response.get("results", {})
    row_count = results.get("row_count", 0)

    if row_count != expected:
        return False, f"Expected {expected} rows but got {row_count}"

    return True, f"Correct row count: {expected}"


def assert_result_shape(
    response: Dict[str, Any],
    expected_columns: int
) -> Tuple[bool, str]:
    """Assert result has expected number of columns"""
    results = response.get("results", {})
    rows = results.get("rows", [])

    if not rows:
        return False, "No rows to check column count"

    first_row = rows[0]
    actual_columns = len(first_row)

    if actual_columns != expected_columns:
        return False, f"Expected {expected_columns} columns but got {actual_columns}"

    return True, f"Correct column count: {expected_columns}"


def assert_value_ranges(
    response: Dict[str, Any],
    column: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> Tuple[bool, str]:
    """Assert values in column are within expected range"""
    results = response.get("results", {})
    rows = results.get("rows", [])

    if not rows:
        return False, "No rows to check values"

    # Get column index (handle different result formats)
    first_row = rows[0]

    # Try to find the value
    value = None
    if isinstance(first_row, dict):
        # Row is a dictionary
        value = first_row.get(column)
    elif isinstance(first_row, (list, tuple)):
        # Row is a list/tuple - value is first element for aggregations
        if len(first_row) > 0:
            value = first_row[0]

    if value is None:
        return False, f"Column '{column}' not found in results"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return False, f"Value '{value}' is not numeric"

    if min_val is not None and value < min_val:
        return False, f"Value {value} is below minimum {min_val}"

    if max_val is not None and value > max_val:
        return False, f"Value {value} is above maximum {max_val}"

    return True, f"Value {value} is within range"