#!/usr/bin/env python3
"""
Core Test Suite for AutoGen Google Sheets Integration
Comprehensive testing of all major functionality
"""

import asyncio
import os
import sys

# Add parent directory to path to import mcp_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import mcp_client


class CoreTestSuite:
    """Main test suite for all functionality"""

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

    async def test_authentication(self):
        """Test Google Sheets authentication"""
        print("\n🔐 Testing Authentication...")

        try:
            # Test if credentials file exists
            if os.path.exists("credentials.json"):
                self.log_test("Credentials File", True, "credentials.json found")
            else:
                self.log_test("Credentials File", False, "credentials.json not found")
                return False

            # Test if token file exists
            if os.path.exists("token.json"):
                self.log_test("Token File", True, "token.json found")
            else:
                self.log_test("Token File", False, "token.json not found")

            # Test service initialization
            try:
                service, creds = mcp_client._get_google_sheets_service_with_creds()
                if service and creds:
                    self.log_test(
                        "Service Initialization", True, "Google Sheets service created"
                    )
                else:
                    self.log_test(
                        "Service Initialization", False, "Failed to create service"
                    )
                    return False
            except Exception as e:
                self.log_test("Service Initialization", False, f"Error: {e}")
                return False

            return True

        except Exception as e:
            self.log_test("Authentication", False, f"Unexpected error: {e}")
            return False

    async def test_mcp_tools(self):
        """Test MCP tool functionality"""
        print("\n🛠️  Testing MCP Tools...")

        try:
            # Test tool discovery
            tools = await mcp_client.get_tools()
            if tools:
                self.log_test("Tool Discovery", True, f"Found {len(tools)} tools")
            else:
                self.log_test("Tool Discovery", False, "No tools found")
                return False

            # Test specific tools
            expected_tools = [
                "event.plan_event",
                "fundraising.create_plan",
                "quality.check_deliverable",
                "db.query",
                "file.read",
                "sheets.select_sheet",
            ]

            for tool_name in expected_tools:
                if tool_name in tools:
                    self.log_test(f"Tool: {tool_name}", True)
                else:
                    self.log_test(f"Tool: {tool_name}", False, "Tool not found")

            # Test tool function creation
            tool_functions = await mcp_client.create_tool_functions(["*"])
            if tool_functions:
                self.log_test(
                    "Tool Function Creation",
                    True,
                    f"Created {len(tool_functions)} functions",
                )
            else:
                self.log_test("Tool Function Creation", False, "No functions created")

            return True

        except Exception as e:
            self.log_test("MCP Tools", False, f"Error: {e}")
            return False

    async def test_event_planning(self):
        """Test event planning functionality"""
        print("\n📅 Testing Event Planning...")

        try:
            # Test basic event planning
            result = await mcp_client.call_tool(
                "event.plan_event",
                {
                    "event_name": "Test Event",
                    "theme": "Testing",
                    "organization": "Test Org",
                    "requirements": "Basic testing requirements",
                },
            )

            if result and "Event Coordinator" in result:
                self.log_test("Basic Event Planning", True, "Event planning successful")
            else:
                self.log_test("Basic Event Planning", False, "Event planning failed")

            # Test event planning with Google Sheets (if available)
            try:
                result = await mcp_client.call_tool(
                    "event.plan_event",
                    {
                        "event_name": "Test Event with Sheets",
                        "theme": "Testing",
                        "organization": "Test Org",
                        "google_sheet_id": "1bWMM3u-Y2b_5zfIetLLvkreZ6iOVvvaX",
                        "sheet_range": "Sheet1!A1:E19",
                    },
                )

                if result:
                    if "📊 Google Sheets Data Retrieved" in result:
                        self.log_test(
                            "Event Planning with Sheets",
                            True,
                            "Successfully read sheet data",
                        )
                    elif "❌ Error reading Google Sheet" in result:
                        self.log_test(
                            "Event Planning with Sheets", False, "Sheet access error"
                        )
                    else:
                        self.log_test(
                            "Event Planning with Sheets",
                            True,
                            "Event planned without sheet data",
                        )
                else:
                    self.log_test(
                        "Event Planning with Sheets", False, "No result returned"
                    )

            except Exception as e:
                self.log_test("Event Planning with Sheets", False, f"Error: {e}")

            return True

        except Exception as e:
            self.log_test("Event Planning", False, f"Error: {e}")
            return False

    async def test_fundraising(self):
        """Test fundraising functionality"""
        print("\n💰 Testing Fundraising...")

        try:
            result = await mcp_client.call_tool(
                "fundraising.create_plan",
                {
                    "goal": "Test Fundraising Goal",
                    "event_name": "Test Event",
                    "budget_target": 5000,
                },
            )

            if result and "Fundraising Coordinator" in result:
                self.log_test(
                    "Fundraising Planning", True, "Fundraising planning successful"
                )
            else:
                self.log_test(
                    "Fundraising Planning", False, "Fundraising planning failed"
                )

            return True

        except Exception as e:
            self.log_test("Fundraising", False, f"Error: {e}")
            return False

    async def test_quality_check(self):
        """Test quality check functionality"""
        print("\n✅ Testing Quality Checks...")

        try:
            result = await mcp_client.call_tool(
                "quality.check_deliverable",
                {
                    "item": "Test Item",
                    "category": "Testing",
                    "criteria": "Basic quality criteria",
                },
            )

            if result and "Quality Checker" in result:
                self.log_test("Quality Check", True, "Quality check successful")
            else:
                self.log_test("Quality Check", False, "Quality check failed")

            return True

        except Exception as e:
            self.log_test("Quality Check", False, f"Error: {e}")
            return False

    async def test_sheet_selector(self):
        """Test sheet selector functionality"""
        print("\n📊 Testing Sheet Selector...")

        try:
            # Test listing sheets
            result = await mcp_client.sheets_select_sheet("", "")

            if result and "📋 Found" in result:
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
            self.log_test("Sheet Selector", False, f"Error: {e}")
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Core Test Suite")
        print("=" * 50)

        # Run tests in order
        await self.test_authentication()
        await self.test_mcp_tools()
        await self.test_event_planning()
        await self.test_fundraising()
        await self.test_quality_check()
        await self.test_sheet_selector()

        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(
            f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%"
        )

        if self.failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Check the results above.")


async def main():
    """Main test runner"""
    test_suite = CoreTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
