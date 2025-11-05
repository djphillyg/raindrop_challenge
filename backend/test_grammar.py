#!/usr/bin/env python3
"""
Test script to validate the Lark grammar produces correct SQL
Run: python backend/test_grammar.py
"""

from lark import Lark
from services.openai_service import FITNESS_SQL_GRAMMAR

# Test SQL queries that should be valid according to your grammar
test_cases = [
    # Basic aggregations
    {
        "name": "Query 1: Average distance with date range",
        "sql": "SELECT AVG(distance) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 30 DAY",
        "should_parse": True
    },
    {
        "name": "Query 2: Sum calories with date range",
        "sql": "SELECT SUM(active_calories) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 7 DAY",
        "should_parse": True
    },
    {
        "name": "Query 3: Sum active time",
        "sql": "SELECT SUM(active_time) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 90 DAY",
        "should_parse": True
    },

    # Filtering + Aggregation
    {
        "name": "Query 4: Count with AND condition",
        "sql": "SELECT COUNT(*) FROM garmin_active_cal_data WHERE active_calories > 500 AND timestamp_day >= CURRENT_DATE - INTERVAL 30 DAY",
        "should_parse": True
    },
    {
        "name": "Query 5: Multi-column select with multiple conditions",
        "sql": "SELECT timestamp_day, distance, active_calories FROM garmin_active_cal_data WHERE distance > 5000 AND active_calories > 400",
        "should_parse": True
    },
    {
        "name": "Query 6: AVG with simple WHERE",
        "sql": "SELECT AVG(distance) FROM garmin_active_cal_data WHERE active_time > 1800",
        "should_parse": True
    },

    # Edge cases
    {
        "name": "Query 7: Zero value with date range",
        "sql": "SELECT timestamp_day FROM garmin_active_cal_data WHERE active_time = 0 AND timestamp_day >= CURRENT_DATE - INTERVAL 7 DAY",
        "should_parse": True
    },
    {
        "name": "Query 8: MAX with date range",
        "sql": "SELECT MAX(distance) FROM garmin_active_cal_data WHERE timestamp_day >= CURRENT_DATE - INTERVAL 180 DAY",
        "should_parse": True
    },

    # Additional edge cases
    {
        "name": "Simple SELECT *",
        "sql": "SELECT * FROM garmin_active_cal_data",
        "should_parse": True
    },
    {
        "name": "SELECT with LIMIT",
        "sql": "SELECT * FROM garmin_active_cal_data LIMIT 5",
        "should_parse": True
    },
    {
        "name": "SELECT with ORDER BY",
        "sql": "SELECT timestamp_day, distance FROM garmin_active_cal_data ORDER BY distance DESC",
        "should_parse": True
    },

    # Invalid queries (should NOT parse)
    {
        "name": "Invalid: Wrong table name",
        "sql": "SELECT * FROM wrong_table",
        "should_parse": False
    },
    {
        "name": "Invalid: Invalid column name",
        "sql": "SELECT invalid_column FROM garmin_active_cal_data",
        "should_parse": False
    },
    {
        "name": "Invalid: Missing SELECT",
        "sql": "FROM garmin_active_cal_data WHERE distance > 100",
        "should_parse": False
    }
]

def test_grammar():
    """Test the grammar against various SQL queries"""
    print("=" * 80)
    print("Testing Lark Grammar for Fitness SQL")
    print("=" * 80)
    print()

    # Initialize Lark parser
    try:
        parser = Lark(FITNESS_SQL_GRAMMAR, start='query')
        print("✓ Grammar is syntactically valid!")
        print()
    except Exception as e:
        print(f"✗ Grammar has syntax errors:")
        print(f"  {e}")
        return

    # Test each case
    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  SQL: {test['sql'][:80]}{'...' if len(test['sql']) > 80 else ''}")

        try:
            tree = parser.parse(test['sql'])

            if test['should_parse']:
                print(f"  ✓ PASS - Parsed successfully")
                passed += 1

                # Optionally show parse tree for first few
                if i <= 3:
                    print(f"  Parse tree preview:")
                    print(f"    {tree.pretty()[:200]}...")
            else:
                print(f"  ✗ FAIL - Should NOT have parsed (but did)")
                failed += 1

        except Exception as e:
            if not test['should_parse']:
                print(f"  ✓ PASS - Correctly rejected (expected to fail)")
                passed += 1
            else:
                print(f"  ✗ FAIL - Parse error: {e}")
                failed += 1

        print()

    # Summary
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)

    if failed == 0:
        print("🎉 All tests passed! Grammar is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Review grammar definition.")

    return failed == 0

if __name__ == "__main__":
    success = test_grammar()
    exit(0 if success else 1)