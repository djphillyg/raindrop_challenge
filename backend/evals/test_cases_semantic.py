"""
Semantic Correctness Evaluation Test Cases
Tests that generated SQL matches the intent of the natural language query.
"""

SEMANTIC_CORRECTNESS_TESTS = [
    {
        "description": "Total should use SUM not COUNT",
        "natural_language_query": "What's the total calories burned?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "correct_aggregation", "expected": "SUM"},
            {"type": "correct_columns", "columns": ["active_calories"]},
        ]
    },
    {
        "description": "Average should use AVG aggregation",
        "natural_language_query": "What's the average distance of my activities?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "correct_aggregation", "expected": "AVG"},
            {"type": "correct_columns", "columns": ["distance"]},
        ]
    },
    {
        "description": "Count should use COUNT aggregation",
        "natural_language_query": "How many activities do I have?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "correct_aggregation", "expected": "COUNT"},
        ]
    },
    {
        "description": "Highest should use ORDER BY DESC",
        "natural_language_query": "What's my highest calorie activity?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "correct_sort", "expected_direction": "DESC"},
            {"type": "correct_columns", "columns": ["active_calories"]},
        ]
    },
    {
        "description": "Lowest should use ORDER BY ASC",
        "natural_language_query": "What's my lowest step count activity?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "correct_sort", "expected_direction": "ASC"},
            {"type": "correct_columns", "columns": ["steps"]},
        ]
    },
    {
        "description": "Greater than filter semantic match",
        "natural_language_query": "Show activities with more than 1000 calories",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "correct_where_clause", "expected_conditions": [">", "1000"]},
            {"type": "correct_columns", "columns": ["active_calories"]},
        ]
    },
    {
        "description": "Distance column for distance queries",
        "natural_language_query": "What's my total distance?",
        "assertions": [
            {"type": "sql_executes"},
            {"type": "correct_aggregation", "expected": "SUM"},
            {"type": "correct_columns", "columns": ["distance"]},
        ]
    },
]