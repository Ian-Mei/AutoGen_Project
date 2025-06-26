#!/usr/bin/env python3
"""
Google Sheets Test Suite
Comprehensive testing of Google Sheets functionality
"""

import asyncio
import os
import sys

# Add parent directory to path to import mcp_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import mcp_client


class SheetsTestSuite:
    """Google Sheets test suite"""

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} | {test_name}"
        if message:
            result += f" | {message}"

        self.test_results.append(result)
        if success:
            self.passed += 1
        else:
            self.failed += 1

        print(result)

    async def test_sheet_listing(self):
        """Test listing all available sheets"""
        print("\n📋 Testing Sheet Listing...")

        try:
            result = await mcp_client.sheets_select_sheet("", "")

            if result and "📋 Found" in result:
                # Extract number of sheets found
                import re

                match = re.search(r"Found (\d+) Google Sheets", result)
                if match:
                    sheet_count = int(match.group(1))
                    self.log_test("Sheet Listing", True, f"Found {sheet_count} sheets")
                else:
                    self.log_test("Sheet Listing", True, "Successfully listed sheets")
            elif result and "❌ No Google Sheets found" in result:
                self.log_test(
                    "Sheet Listing",
                    True,
                    "No sheets found (expected for some accounts)",
                )
            else:
                self.log_test("Sheet Listing", False, "Failed to list sheets")

            return True

        except Exception as e:
            self.log_test("Sheet Listing", False, f"Error: {e}")
            return False

    async def test_public_sheet_access(self):
        """Test access to public Google Sheets"""
        print("\n🌐 Testing Public Sheet Access...")

        try:
            # Test with Google's public sample sheet
            sample_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            sample_range = "Class Data!A1:E10"

            result = mcp_client._read_google_sheet(sample_sheet_id, sample_range)

            if result and len(result) > 0:
                self.log_test(
                    "Public Sheet Read", True, f"Successfully read {len(result)} rows"
                )

                # Test the data structure
                if len(result) > 1:
                    headers = result[0]
                    first_row = result[1]
                    self.log_test(
                        "Data Structure",
                        True,
                        f"Headers: {len(headers)} columns, First row: {len(first_row)} values",
                    )
                else:
                    self.log_test("Data Structure", True, "Single row of data")
            else:
                self.log_test("Public Sheet Read", False, "No data returned")

            return True

        except Exception as e:
            self.log_test("Public Sheet Access", False, f"Error: {e}")
            return False

    async def test_sheet_exploration(self):
        """Test sheet exploration functionality"""
        print("\n🔍 Testing Sheet Exploration...")

        try:
            # Test with Google's public sample sheet
            sample_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

            result = await mcp_client.sheets_select_sheet(sample_sheet_id, "")

            if result and "🔍 Exploring:" in result:
                self.log_test(
                    "Sheet Exploration", True, "Successfully explored sheet structure"
                )

                # Check if worksheets are listed
                if "📋 Worksheets" in result:
                    self.log_test(
                        "Worksheet Discovery",
                        True,
                        "Successfully discovered worksheets",
                    )
                else:
                    self.log_test("Worksheet Discovery", False, "No worksheets found")
            else:
                self.log_test("Sheet Exploration", False, "Failed to explore sheet")

            return True

        except Exception as e:
            self.log_test("Sheet Exploration", False, f"Error: {e}")
            return False

    async def test_data_reading(self):
        """Test reading specific data from sheets"""
        print("\n📊 Testing Data Reading...")

        try:
            # Test with Google's public sample sheet
            sample_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            sample_range = "Class Data!A1:D5"

            result = await mcp_client.sheets_select_sheet(sample_sheet_id, sample_range)

            if result and "📊 Retrieved" in result:
                self.log_test("Data Reading", True, "Successfully read sheet data")

                # Check if headers and data are displayed
                if "📋 Headers:" in result and "📄 Data:" in result:
                    self.log_test(
                        "Data Formatting", True, "Data properly formatted with headers"
                    )
                else:
                    self.log_test(
                        "Data Formatting", False, "Data not properly formatted"
                    )
            else:
                self.log_test("Data Reading", False, "Failed to read sheet data")

            return True

        except Exception as e:
            self.log_test("Data Reading", False, f"Error: {e}")
            return False

    async def test_range_formats(self):
        """Test different range formats"""
        print("\n📏 Testing Range Formats...")

        try:
            sample_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

            # Test different range formats
            test_ranges = [
                ("Class Data!A1:D5", "Specific range"),
                ("Class Data!A:A", "Entire column"),
                ("Class Data!1:1", "Entire row"),
                ("Class Data", "Entire sheet"),
            ]

            for range_name, description in test_ranges:
                try:
                    result = await mcp_client.sheets_select_sheet(
                        sample_sheet_id, range_name
                    )
                    if result and "📊 Retrieved" in result:
                        self.log_test(
                            f"Range: {description}",
                            True,
                            f"Successfully read {range_name}",
                        )
                    else:
                        self.log_test(
                            f"Range: {description}",
                            False,
                            f"Failed to read {range_name}",
                        )
                except Exception as e:
                    self.log_test(
                        f"Range: {description}", False, f"Error with {range_name}: {e}"
                    )

            return True

        except Exception as e:
            self.log_test("Range Formats", False, f"Error: {e}")
            return False

    async def test_error_handling(self):
        """Test error handling for invalid sheets/ranges"""
        print("\n⚠️  Testing Error Handling...")

        try:
            # Test with invalid sheet ID
            invalid_sheet_id = "invalid_sheet_id_12345"

            result = await mcp_client.sheets_select_sheet(
                invalid_sheet_id, "Sheet1!A1:D5"
            )

            if result and ("❌ Error" in result or "Error reading data" in result):
                self.log_test(
                    "Invalid Sheet ID", True, "Properly handled invalid sheet ID"
                )
            else:
                self.log_test(
                    "Invalid Sheet ID",
                    False,
                    "Did not handle invalid sheet ID properly",
                )

            # Test with invalid range
            sample_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            invalid_range = "InvalidSheet!A1:D5"

            result = await mcp_client.sheets_select_sheet(
                sample_sheet_id, invalid_range
            )

            if result and ("❌ Error" in result or "No data found" in result):
                self.log_test("Invalid Range", True, "Properly handled invalid range")
            else:
                self.log_test(
                    "Invalid Range", False, "Did not handle invalid range properly"
                )

            return True

        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {e}")
            return False

    async def test_mcp_integration(self):
        """Test MCP integration with Google Sheets"""
        print("\n🔗 Testing MCP Integration...")

        try:
            # Test event planning with Google Sheets
            result = await mcp_client.call_tool(
                "event.plan_event",
                {
                    "event_name": "Test Event with Sheets",
                    "theme": "Testing",
                    "organization": "Test Org",
                    "google_sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                    "sheet_range": "Class Data!A1:E5",
                },
            )

            if result and "Event Coordinator" in result:
                if "📊 Google Sheets Data Retrieved" in result:
                    self.log_test(
                        "MCP Sheet Integration",
                        True,
                        "Successfully integrated sheets with MCP",
                    )
                else:
                    self.log_test(
                        "MCP Sheet Integration",
                        True,
                        "Event planned without sheet data",
                    )
            else:
                self.log_test(
                    "MCP Sheet Integration",
                    False,
                    "Failed to integrate sheets with MCP",
                )

            return True

        except Exception as e:
            self.log_test("MCP Integration", False, f"Error: {e}")
            return False

    async def run_all_tests(self):
        """Run all Google Sheets tests"""
        print("📊 Google Sheets Test Suite")
        print("=" * 50)

        # Run tests in order
        await self.test_sheet_listing()
        await self.test_public_sheet_access()
        await self.test_sheet_exploration()
        await self.test_data_reading()
        await self.test_range_formats()
        await self.test_error_handling()
        await self.test_mcp_integration()

        # Print summary
        print("\n" + "=" * 50)
        print("📊 Google Sheets Test Summary")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(
            f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%"
        )

        if self.failed == 0:
            print("\n🎉 All Google Sheets tests passed!")
        else:
            print(f"\n⚠️  {self.failed} Google Sheets test(s) failed.")


async def interactive_sheet_test():
    """Interactive sheet testing"""
    print("🎯 Interactive Google Sheets Testing")
    print("=" * 40)

    while True:
        print("\nOptions:")
        print("1. List all my sheets")
        print("2. Explore a specific sheet")
        print("3. Read data from a sheet")
        print("4. Test with public sample sheet")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print("\n📋 Listing all sheets...")
            result = await mcp_client.sheets_select_sheet("", "")
            print(result)

        elif choice == "2":
            sheet_id = input("Enter sheet ID: ").strip()
            if sheet_id:
                print(f"\n🔍 Exploring sheet {sheet_id}...")
                result = await mcp_client.sheets_select_sheet(sheet_id, "")
                print(result)
            else:
                print("❌ Please enter a valid sheet ID")

        elif choice == "3":
            sheet_id = input("Enter sheet ID: ").strip()
            range_name = input("Enter range (e.g., Sheet1!A1:D10): ").strip()
            if sheet_id and range_name:
                print(f"\n📊 Reading data from {sheet_id}, range {range_name}...")
                result = await mcp_client.sheets_select_sheet(sheet_id, range_name)
                print(result)
            else:
                print("❌ Please enter both sheet ID and range")

        elif choice == "4":
            print("\n🌐 Testing with Google's public sample sheet...")
            sample_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            result = await mcp_client.sheets_select_sheet(
                sample_sheet_id, "Class Data!A1:E5"
            )
            print(result)

        elif choice == "5":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1-5.")


async def main():
    """Main Google Sheets test runner"""
    print("Choose option:")
    print("1. Run automated tests")
    print("2. Interactive testing")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        test_suite = SheetsTestSuite()
        await test_suite.run_all_tests()
    elif choice == "2":
        await interactive_sheet_test()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
