#!/usr/bin/env python3
"""
Individual Test Runner
Run specific test files from the tests folder
"""

import sys
import os
import asyncio

# Add the tests directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "tests"))


def run_test(test_name):
    """Run a specific test file"""
    try:
        if test_name == "core":
            from test_core import main
        elif test_name == "auth":
            from test_auth import main
        elif test_name == "sheets":
            from test_sheets import main
        elif test_name == "mcp":
            from test_mcp import main
        else:
            print(f"❌ Unknown test: {test_name}")
            print("Available tests: core, auth, sheets, mcp")
            return False

        asyncio.run(main())
        return True

    except Exception as e:
        print(f"❌ Error running {test_name} test: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_runner.py <test_name>")
        print("Available tests: core, auth, sheets, mcp")
        print("Example: python test_runner.py core")
        sys.exit(1)

    test_name = sys.argv[1].lower()
    run_test(test_name)
