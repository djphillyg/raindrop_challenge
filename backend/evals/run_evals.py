#!/usr/bin/env python3
"""
CFG Evaluation Runner
Executes all eval test cases and generates reports.

Usage:
    python run_evals.py
    python run_evals.py --api-url http://localhost:8000
"""

import argparse
import json
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Import test cases
from test_cases_grammar import GRAMMAR_SYNTAX_TESTS
from test_cases_semantic import SEMANTIC_CORRECTNESS_TESTS
from test_cases_results import RESULT_ACCURACY_TESTS

# Import assertions
from assertions import (
    assert_sql_executes,
    assert_sql_parseable,
    assert_valid_table_name,
    assert_valid_columns,
    assert_correct_aggregation,
    assert_correct_columns,
    assert_correct_where_clause,
    assert_correct_sort,
    assert_non_empty_results,
    assert_empty_results,
    assert_result_count,
    assert_result_shape,
    assert_value_ranges,
)


# Map assertion type names to functions
ASSERTION_MAP = {
    "sql_executes": assert_sql_executes,
    "sql_parseable": assert_sql_parseable,
    "valid_table_name": assert_valid_table_name,
    "valid_columns": assert_valid_columns,
    "correct_aggregation": assert_correct_aggregation,
    "correct_columns": assert_correct_columns,
    "correct_where_clause": assert_correct_where_clause,
    "correct_sort": assert_correct_sort,
    "non_empty_results": assert_non_empty_results,
    "empty_results": assert_empty_results,
    "result_count": assert_result_count,
    "result_shape": assert_result_shape,
    "value_ranges": assert_value_ranges,
}


def call_query_api(query: str, api_url: str) -> Dict[str, Any]:
    """Call the /query API endpoint with natural language query"""
    try:
        response = requests.post(
            f"{api_url}/query",
            json={"query": query},
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "natural_query": query,
                "generated_sql": "",
                "results": None,
                "error": f"API returned status {response.status_code}: {response.text}"
            }

    except requests.exceptions.RequestException as e:
        return {
            "natural_query": query,
            "generated_sql": "",
            "results": None,
            "error": f"API request failed: {str(e)}"
        }


def run_assertion(assertion_spec: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, str]:
    """Execute a single assertion"""
    assertion_type = assertion_spec["type"]
    assertion_func = ASSERTION_MAP.get(assertion_type)

    if not assertion_func:
        return False, f"Unknown assertion type: {assertion_type}"

    # Extract parameters (everything except 'type')
    params = {k: v for k, v in assertion_spec.items() if k != "type"}

    try:
        return assertion_func(response, **params)
    except Exception as e:
        return False, f"Assertion {assertion_type} raised error: {str(e)}"


def run_test_case(test_case: Dict[str, Any], api_url: str) -> Dict[str, Any]:
    """Run a single test case and return results"""
    description = test_case["description"]
    query = test_case["natural_language_query"]
    assertions = test_case["assertions"]

    # Call API
    response = call_query_api(query, api_url)

    # Run assertions
    assertion_results = []
    passed_count = 0

    for assertion_spec in assertions:
        passed, message = run_assertion(assertion_spec, response)

        assertion_results.append({
            "type": assertion_spec["type"],
            "passed": passed,
            "message": message
        })

        if passed:
            passed_count += 1

    all_passed = passed_count == len(assertions)

    return {
        "description": description,
        "query": query,
        "generated_sql": response.get("generated_sql", ""),
        "passed": all_passed,
        "assertions": assertion_results,
        "passed_assertions": passed_count,
        "total_assertions": len(assertions)
    }


def run_eval_suite(
    suite_name: str,
    test_cases: List[Dict[str, Any]],
    api_url: str
) -> Dict[str, Any]:
    """Run a suite of test cases"""
    print(f"\nRunning {suite_name}...")
    print("=" * 60)

    results = []
    passed_tests = 0

    for i, test_case in enumerate(test_cases, 1):
        result = run_test_case(test_case, api_url)
        results.append(result)

        # Print result
        status = "✓" if result["passed"] else "✗"
        print(f"{status} Test {i}: {result['description']}")

        if result["passed"]:
            passed_tests += 1
        else:
            # Print failure details
            for assertion in result["assertions"]:
                if not assertion["passed"]:
                    print(f"  - {assertion['type']}: {assertion['message']}")

        print()

    pass_rate = passed_tests / len(test_cases) if test_cases else 0

    print(f"{suite_name} Summary: {passed_tests}/{len(test_cases)} ({pass_rate*100:.1f}%)")

    return {
        "suite_name": suite_name,
        "passed": passed_tests,
        "total": len(test_cases),
        "pass_rate": pass_rate,
        "results": results
    }


def generate_json_report(all_results: List[Dict[str, Any]], output_path: str):
    """Generate JSON report file"""
    total_passed = sum(r["passed"] for r in all_results)
    total_tests = sum(r["total"] for r in all_results)

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total_tests,
            "passed": total_passed,
            "failed": total_tests - total_passed,
            "pass_rate": total_passed / total_tests if total_tests else 0
        },
        "by_type": {
            r["suite_name"]: {
                "passed": r["passed"],
                "failed": r["total"] - r["passed"],
                "pass_rate": r["pass_rate"]
            }
            for r in all_results
        },
        "details": all_results
    }

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nJSON report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Run CFG SQL evaluation tests")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL for the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--output",
        default="eval_results.json",
        help="Output file for JSON results (default: eval_results.json)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("CFG SQL Evaluation Runner")
    print("=" * 60)
    print(f"API URL: {args.api_url}")
    print(f"Output: {args.output}")

    # Check API is reachable
    try:
        response = requests.get(f"{args.api_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"\n⚠️  Warning: API health check failed (status {response.status_code})")
            print("Make sure the backend is running!")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error: Cannot reach API at {args.api_url}")
        print(f"   {str(e)}")
        print("\nMake sure the backend is running:")
        print("   cd backend && python run.py")
        sys.exit(1)

    print("✓ API is reachable\n")

    # Run all eval suites
    all_results = []

    all_results.append(run_eval_suite(
        "Grammar Syntax",
        GRAMMAR_SYNTAX_TESTS,
        args.api_url
    ))

    all_results.append(run_eval_suite(
        "Semantic Correctness",
        SEMANTIC_CORRECTNESS_TESTS,
        args.api_url
    ))

    all_results.append(run_eval_suite(
        "Result Accuracy",
        RESULT_ACCURACY_TESTS,
        args.api_url
    ))

    # Print overall summary
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)

    for result in all_results:
        print(f"{result['suite_name']}: {result['passed']}/{result['total']} ({result['pass_rate']*100:.1f}%)")

    total_passed = sum(r["passed"] for r in all_results)
    total_tests = sum(r["total"] for r in all_results)
    overall_pass_rate = total_passed / total_tests if total_tests else 0

    print(f"\nOverall: {total_passed}/{total_tests} ({overall_pass_rate*100:.1f}%)")
    print("=" * 60)

    # Generate JSON report
    generate_json_report(all_results, args.output)

    # Exit with error code if not all tests passed
    if total_passed < total_tests:
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()