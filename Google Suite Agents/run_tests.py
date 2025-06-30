#!/usr/bin/env python3
"""
Simple Test Runner
Run tests from the tests folder
"""

import sys
import os

# Add the tests directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "tests"))

if __name__ == "__main__":
    # Import and run the main test runner from tests directory
    # Since we added tests to sys.path, we can import directly
    import run_tests as test_runner
    import asyncio

    try:
        asyncio.run(test_runner.main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
