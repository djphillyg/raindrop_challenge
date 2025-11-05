"""Tests for eval assertions"""
from assertions import (
    assert_sql_executes,
    assert_sql_parseable,
    assert_valid_table_name,
    assert_valid_columns,
    assert_correct_aggregation,
    assert_correct_columns,
    assert_non_empty_results,
    assert_result_count,
    assert_value_ranges,
)


def test_sql_executes_with_valid_sql():
    """Test that valid SQL passes execution check"""
    response = {
        "generated_sql": "SELECT * FROM garmin_active_cal_data LIMIT 1",
        "error": None,
        "results": {"rows": [{"col": "val"}], "row_count": 1}
    }
    passed, message = assert_sql_executes(response)
    assert passed == True
    assert "executed successfully" in message.lower()


def test_sql_executes_with_error():
    """Test that SQL with error fails execution check"""
    response = {
        "generated_sql": "SELECT * FROM invalid_table",
        "error": "Table does not exist",
        "results": None
    }
    passed, message = assert_sql_executes(response)
    assert passed == False
    assert "error" in message.lower()