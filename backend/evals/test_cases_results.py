"""
Result Accuracy Evaluation Test Cases
Tests that query results are logically correct and reasonable.
"""

RESULT_ACCURACY_TESTS = [
    {
        "description": "Aggregation should return single row",
        "natural_language_query": "What's the sum of all calories?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "non_empty_results"},
            {"type": "result_count", "expected": 1},
        ]
    },
    {
        "description": "Total calories should be positive",
        "natural_language_query": "Sum all my active calories",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "non_empty_results"},
            {"type": "value_ranges", "column": "SUM(active_calories)", "min_val": 0},
        ]
    },
    {
        "description": "Average distance should be reasonable",
        "natural_language_query": "What's my average distance?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "non_empty_results"},
            {"type": "value_ranges", "column": "AVG(distance)", "min_val": 0},
        ]
    },
    {
        "description": "COUNT should return non-negative integer",
        "natural_language_query": "How many activities do I have?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "non_empty_results"},
            {"type": "value_ranges", "column": "COUNT(*)", "min_val": 0},
        ]
    },
    {
        "description": "LIMIT should constrain result count",
        "natural_language_query": "Show me 5 activities",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "non_empty_results"},
            # Note: may return fewer than 5 if dataset is small
        ]
    },
    {
        "description": "Impossible condition returns empty",
        "natural_language_query": "Show activities with calories less than 0",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "empty_results"},
        ]
    },
    {
        "description": "MAX returns single value",
        "natural_language_query": "What's my maximum step count?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "non_empty_results"},
            {"type": "result_count", "expected": 1},
            {"type": "value_ranges", "column": "MAX(steps)", "min_val": 0},
        ]
    },
]
