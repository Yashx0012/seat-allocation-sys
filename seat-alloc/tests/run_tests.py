"""
Test Runner Script for Seat Allocation System
===============================================
Run this script to execute the full test suite with a summary report.

Usage:
    python tests/run_tests.py              # Run all tests
    python tests/run_tests.py --suite algo  # Run only algorithm tests
    python tests/run_tests.py --suite iso   # Run only isolation tests
    python tests/run_tests.py --suite db    # Run only DB centralization tests
    python tests/run_tests.py --suite auth  # Run only auth tests
    python tests/run_tests.py --suite api   # Run only API endpoint tests
    python tests/run_tests.py --suite red   # Run only redundancy/service tests
"""
import sys
import os
import argparse
import subprocess
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

SUITE_MAP = {
    "iso":  "tests/test_session_isolation.py",
    "db":   "tests/test_db_centralization.py",
    "auth": "tests/test_auth_service.py",
    "algo": "tests/test_core_algorithm.py",
    "api":  "tests/test_api_endpoints.py",
    "red":  "tests/test_redundancy_and_services.py",
}

SUITE_LABELS = {
    "iso":  "Session Isolation & Data Ownership",
    "db":   "Database Centralization",
    "auth": "Authentication Service",
    "algo": "Core Seating Algorithm",
    "api":  "API Endpoints",
    "red":  "Redundancy Fixes & Service Layer",
}


def run_suite(suite_key=None, extra_args=None):
    """Run a specific suite or all suites."""
    python = sys.executable
    cmd = [python, "-m", "pytest"]

    if suite_key and suite_key in SUITE_MAP:
        cmd.append(SUITE_MAP[suite_key])
        print(f"\n{'='*60}")
        print(f"  Running: {SUITE_LABELS[suite_key]}")
        print(f"  File:    {SUITE_MAP[suite_key]}")
        print(f"{'='*60}\n")
    else:
        # Run all test files in order
        for key in SUITE_MAP:
            cmd.append(SUITE_MAP[key])
        print(f"\n{'='*60}")
        print(f"  Running: ALL TEST SUITES ({len(SUITE_MAP)} suites)")
        print(f"{'='*60}\n")

    cmd.extend(["-v", "--tb=short"])
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


def run_all_suites_individually():
    """Run each suite individually and collect results."""
    results = {}
    total_pass = 0
    total_fail = 0

    print("\n" + "=" * 70)
    print("  SEAT ALLOCATION SYSTEM — FULL TEST SUITE")
    print("=" * 70)

    for key in SUITE_MAP:
        python = sys.executable
        cmd = [python, "-m", "pytest", SUITE_MAP[key], "-v", "--tb=short", "-q"]

        print(f"\n{'─'*60}")
        print(f"  [{key.upper()}] {SUITE_LABELS[key]}")
        print(f"{'─'*60}")

        proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        
        # Print test output
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            # Filter out warnings for cleaner output
            for line in proc.stderr.split("\n"):
                if "WARNING" not in line and "DeprecationWarning" not in line:
                    if line.strip():
                        print(line)

        passed = proc.stdout.count(" PASSED")
        failed = proc.stdout.count(" FAILED")
        errors = proc.stdout.count(" ERROR")

        results[key] = {
            "label": SUITE_LABELS[key],
            "passed": passed,
            "failed": failed + errors,
            "returncode": proc.returncode,
        }
        total_pass += passed
        total_fail += failed + errors

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"{'Suite':<45} {'Pass':>6} {'Fail':>6} {'Status':>8}")
    print("─" * 70)

    for key, info in results.items():
        status = "✅ PASS" if info["returncode"] == 0 else "❌ FAIL"
        print(f"  {info['label']:<43} {info['passed']:>6} {info['failed']:>6} {status:>8}")

    print("─" * 70)
    overall = "✅ ALL PASSED" if total_fail == 0 else f"❌ {total_fail} FAILURES"
    print(f"  {'TOTAL':<43} {total_pass:>6} {total_fail:>6} {overall:>8}")
    print("=" * 70 + "\n")

    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run test suites")
    parser.add_argument(
        "--suite", "-s",
        choices=list(SUITE_MAP.keys()) + ["all"],
        default="all",
        help="Which test suite to run (default: all)",
    )
    parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="Run all suites individually with summary report",
    )
    args, extra = parser.parse_known_args()

    if args.detailed or args.suite == "all":
        exit_code = run_all_suites_individually()
    else:
        exit_code = run_suite(args.suite, extra)

    sys.exit(exit_code)
