#!/usr/bin/env python3
"""
Master Test Runner
Run all consolidated test suites
"""

import asyncio
import sys
import os

# Add parent directories to path to import modules
# Current structure: AutoGen_Project/Google Suite Agents/tests/run_tests.py
# Need to go up two levels to get to AutoGen_Project, then into Google Suite Agents
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Google Suite Agents directory
sys.path.append(parent_dir)


async def run_test_suite(test_file: str, test_name: str):
    """Run a specific test suite"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_name}")
    print(f"{'='*60}")

    try:
        # Import and run the test suite
        if test_file == "test_core.py":
            from test_core import main as test_main
        elif test_file == "test_auth.py":
            from test_auth import main as test_main
        elif test_file == "test_sheets.py":
            from test_sheets import main as test_main
        elif test_file == "test_mcp.py":
            from test_mcp import main as test_main
        else:
            print(f"❌ Unknown test file: {test_file}")
            return False

        await test_main()
        return True

    except Exception as e:
        print(f"❌ Error running {test_name}: {e}")
        return False


async def run_all_tests():
    """Run all test suites"""
    print("🚀 Master Test Runner")
    print("=" * 60)

    test_suites = [
        ("test_core.py", "Core Test Suite"),
        ("test_auth.py", "Authentication Test Suite"),
        ("test_sheets.py", "Google Sheets Test Suite"),
        ("test_mcp.py", "MCP Client Test Suite"),
    ]

    results = []

    for test_file, test_name in test_suites:
        test_path = os.path.join("tests", test_file)
        if os.path.exists(test_path):
            success = await run_test_suite(test_file, test_name)
            results.append((test_name, success))
        else:
            print(f"❌ Test file not found: {test_path}")
            results.append((test_name, False))

    # Print overall summary
    print(f"\n{'='*60}")
    print("📊 Overall Test Summary")
    print(f"{'='*60}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")

    print(
        f"\n📈 Overall Success Rate: {(passed / total * 100):.1f}% ({passed}/{total})"
    )

    if passed == total:
        print("\n🎉 All test suites passed!")
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed.")


def show_test_menu():
    """Show interactive test menu"""
    print("🧪 Test Suite Menu")
    print("=" * 40)
    print("1. Run all test suites")
    print("2. Core functionality tests")
    print("3. Authentication tests")
    print("4. Google Sheets tests")
    print("5. MCP client tests")
    print("6. Exit")

    choice = input("\nEnter your choice (1-6): ").strip()

    if choice == "1":
        return "all"
    elif choice == "2":
        return "core"
    elif choice == "3":
        return "auth"
    elif choice == "4":
        return "sheets"
    elif choice == "5":
        return "mcp"
    elif choice == "6":
        return "exit"
    else:
        print("❌ Invalid choice")
        return None


async def main():
    """Main test runner"""
    print("Choose test mode:")
    print("1. Automated (run all tests)")
    print("2. Interactive (choose specific tests)")

    mode = input("\nEnter mode (1-2): ").strip()

    if mode == "1":
        await run_all_tests()
    elif mode == "2":
        while True:
            choice = show_test_menu()

            if choice == "all":
                await run_all_tests()
            elif choice == "core":
                await run_test_suite("test_core.py", "Core Test Suite")
            elif choice == "auth":
                await run_test_suite("test_auth.py", "Authentication Test Suite")
            elif choice == "sheets":
                await run_test_suite("test_sheets.py", "Google Sheets Test Suite")
            elif choice == "mcp":
                await run_test_suite("test_mcp.py", "MCP Client Test Suite")
            elif choice == "exit":
                print("👋 Goodbye!")
                break
            else:
                continue

            # Ask if user wants to continue
            if choice != "exit":
                continue_test = input("\nContinue testing? (y/n): ").strip().lower()
                if continue_test != "y":
                    print("👋 Goodbye!")
                    break
    else:
        print("❌ Invalid mode")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
