"""
Grammar Syntax Evaluation Test Cases
Tests that CFG produces valid, parseable SQL that executes.
"""

GRAMMAR_SYNTAX_TESTS = [
    {
        "description": "Basic SELECT all columns",
        "natural_language_query": "Show me all my activities",
        "assertions": [
            {"type": "sql_parseable"},
            {"type": "sql_executes"},
            {"type": "valid_table_name"},
            {"type": "valid_columns"},
        ]
    },
    {
        "description": "SELECT with specific columns",
        "natural_language_query": "Show me timestamps and calories",
        "assertions": [
            {"type": "sql_parseable"},
            {"type": "sql_executes"},
            {"type": "valid_table_name"},
            {"type": "correct_columns", "columns": ["timestamp_day", "active_calories"]},
        ]
    },
    {
        "description": "SUM aggregation",
        "natural_language_query": "What's the total of all my active calories?",
        "assertions": [
            {"type": "sql_parseable"},
            {"type": "sql_executes"},
            {"type": "valid_table_name"},
            {"type": "correct_aggregation", "expected": "SUM"},
        ]
    },
    {
        "description": "AVG aggregation",
        "natural_language_query": "What's my average distance?",
        "assertions": [
            {"type": "sql_parseable"},
            {"type": "sql_executes"},
            {"type": "correct_aggregation", "expected": "AVG"},
        ]
    },
    {
        "description": "WHERE clause with single condition",
        "natural_language_query": "Show activities where calories are greater than 500",
        "assertions": [
            {"type": "sql_parseable"},
            {"type": "sql_executes"},
            {"type": "valid_table_name"},
        ]
    },
    {
        "description": "WHERE clause with multiple AND conditions",
        "natural_language_query": "Show activities where calories > 500 AND steps > 10000",
        "assertions": [
            {"type": "sql_parseable"},
            {"type": "sql_executes"},
            {"type": "valid_table_name"},
        ]
    },
    {
        "description": "ORDER BY with DESC",
        "natural_language_query": "Show my activities ordered by highest calories",
        "assertions": [
            {"type": "sql_parseable"},
            {"type": "sql_executes"},
            {"type": "correct_sort", "expected_direction": "DESC"},
        ]
    },
]