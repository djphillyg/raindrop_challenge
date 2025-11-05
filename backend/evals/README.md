# CFG SQL Evaluation Framework

Standalone evaluation framework for testing GPT-5's Context Free Grammar (CFG) SQL generation.

## Overview

This framework tests the end-to-end pipeline of natural language → CFG-constrained SQL → ClickHouse execution across 3 evaluation types:

1. **Grammar Syntax** (7 tests) - CFG produces valid, parseable SQL
2. **Semantic Correctness** (7 tests) - Generated SQL matches query intent
3. **Result Accuracy** (7 tests) - Query results are logically correct

**Total: 21 test cases**

## Structure

```
evals/
├── assertions.py              # Reusable assertion functions
├── test_assertions.py         # Unit tests for assertions
├── test_cases_grammar.py      # Grammar syntax test cases
├── test_cases_semantic.py     # Semantic correctness test cases
├── test_cases_results.py      # Result accuracy test cases
├── run_evals.py               # Main eval runner script
└── README.md                  # This file
```

## Running Evals

### Prerequisites

1. Start the backend API:
```bash
docker-compose up backend
```

2. Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Run All Evals

```bash
cd backend/evals
python run_evals.py
```

### Custom API URL

```bash
python run_evals.py --api-url http://localhost:5000
```

### Custom Output File

```bash
python run_evals.py --output my_results.json
```

## Output

### Console Output

```
Running Grammar Syntax...
✓ Test 1: Basic SELECT all columns
✓ Test 2: SELECT with specific columns
✗ Test 3: SUM aggregation
  - correct_aggregation: Expected SUM aggregation not found in SQL

...

Grammar Syntax Summary: 6/7 (85.7%)
```

### JSON Report

Results are saved to `eval_results.json`:

```json
{
  "timestamp": "2025-11-05T10:30:00Z",
  "summary": {
    "total": 21,
    "passed": 18,
    "failed": 3,
    "pass_rate": 0.857
  },
  "by_type": {
    "Grammar Syntax": {"passed": 6, "failed": 1},
    ...
  }
}
```

## Adding New Test Cases

1. Choose the appropriate test case file based on eval type
2. Add a new test case dictionary:

```python
{
    "description": "Test description",
    "natural_language_query": "User's natural language query",
    "assertions": [
        {"type": "assertion_name"},
        {"type": "assertion_with_param", "param": "value"}
    ]
}
```

3. Re-run evals to validate

## Available Assertions

See `assertions.py` for full list. Common assertions:

- `sql_parseable` - SQL was generated
- `sql_executes` - SQL runs without errors
- `correct_aggregation` - Uses expected function (SUM, AVG, etc.)
- `correct_columns` - Selects expected columns
- `non_empty_results` - Returns data
- `result_count` - Exact number of rows
- `value_ranges` - Values within expected range

## Testing Assertions

```bash
pytest test_assertions.py -v
```

## Success Criteria

- **>70% overall pass rate** is acceptable for MVP
- Individual test failures indicate specific areas for improvement
- Track results over time to measure progress
