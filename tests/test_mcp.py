#!/usr/bin/env python3
"""
MCP Client Test Suite
Comprehensive testing of MCP client and tool functionality
"""

import asyncio
import os
import sys

# Add parent directory to path to import mcp_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import mcp_client


class MCPTestSuite:
    """MCP client test suite"""

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

    async def test_tool_discovery(self):
        """Test MCP tool discovery"""
        print("\n🔍 Testing Tool Discovery...")

        try:
            # Test getting all tools
            tools = await mcp_client.get_tools()

            if tools and len(tools) > 0:
                self.log_test("Tool Discovery", True, f"Found {len(tools)} tools")

                # List all available tools
                print("   Available tools:")
                for tool_name in tools.keys():
                    print(f"   - {tool_name}")
            else:
                self.log_test("Tool Discovery", False, "No tools found")
                return False

            return True

        except Exception as e:
            self.log_test("Tool Discovery", False, f"Error: {e}")
            return False

    async def test_tool_filtering(self):
        """Test tool filtering by domain"""
        print("\n🎯 Testing Tool Filtering...")

        try:
            # Test filtering by domain
            event_tools = await mcp_client.get_tools(["event.*"])
            fundraising_tools = await mcp_client.get_tools(["fundraising.*"])
            quality_tools = await mcp_client.get_tools(["quality.*"])
            sheet_tools = await mcp_client.get_tools(["sheets.*"])

            if event_tools:
                self.log_test(
                    "Event Tools Filter", True, f"Found {len(event_tools)} event tools"
                )
            else:
                self.log_test("Event Tools Filter", False, "No event tools found")

            if fundraising_tools:
                self.log_test(
                    "Fundraising Tools Filter",
                    True,
                    f"Found {len(fundraising_tools)} fundraising tools",
                )
            else:
                self.log_test(
                    "Fundraising Tools Filter", False, "No fundraising tools found"
                )

            if quality_tools:
                self.log_test(
                    "Quality Tools Filter",
                    True,
                    f"Found {len(quality_tools)} quality tools",
                )
            else:
                self.log_test("Quality Tools Filter", False, "No quality tools found")

            if sheet_tools:
                self.log_test(
                    "Sheet Tools Filter", True, f"Found {len(sheet_tools)} sheet tools"
                )
            else:
                self.log_test("Sheet Tools Filter", False, "No sheet tools found")

            return True

        except Exception as e:
            self.log_test("Tool Filtering", False, f"Error: {e}")
            return False

    async def test_tool_function_creation(self):
        """Test creating callable tool functions"""
        print("\n⚙️  Testing Tool Function Creation...")

        try:
            # Test creating functions for all tools
            tool_functions = await mcp_client.create_tool_functions(["*"])

            if tool_functions and len(tool_functions) > 0:
                self.log_test(
                    "Tool Function Creation",
                    True,
                    f"Created {len(tool_functions)} functions",
                )

                # Test that functions are callable
                for tool_name, func in tool_functions.items():
                    if callable(func):
                        self.log_test(
                            f"Function: {tool_name}", True, "Function is callable"
                        )
                    else:
                        self.log_test(
                            f"Function: {tool_name}", False, "Function is not callable"
                        )
            else:
                self.log_test("Tool Function Creation", False, "No functions created")
                return False

            return True

        except Exception as e:
            self.log_test("Tool Function Creation", False, f"Error: {e}")
            return False

    async def test_event_tool(self):
        """Test event planning tool"""
        print("\n📅 Testing Event Tool...")

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
                self.log_test("Event Tool Basic", True, "Event planning successful")
            else:
                self.log_test("Event Tool Basic", False, "Event planning failed")

            # Test event planning with optional parameters
            result = await mcp_client.call_tool(
                "event.plan_event", {"event_name": "Minimal Event"}
            )

            if result and "Event Coordinator" in result:
                self.log_test(
                    "Event Tool Minimal", True, "Minimal event planning successful"
                )
            else:
                self.log_test(
                    "Event Tool Minimal", False, "Minimal event planning failed"
                )

            return True

        except Exception as e:
            self.log_test("Event Tool", False, f"Error: {e}")
            return False

    async def test_fundraising_tool(self):
        """Test fundraising tool"""
        print("\n💰 Testing Fundraising Tool...")

        try:
            # Test fundraising planning
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
                    "Fundraising Tool", True, "Fundraising planning successful"
                )
            else:
                self.log_test("Fundraising Tool", False, "Fundraising planning failed")

            return True

        except Exception as e:
            self.log_test("Fundraising Tool", False, f"Error: {e}")
            return False

    async def test_quality_tool(self):
        """Test quality check tool"""
        print("\n✅ Testing Quality Tool...")

        try:
            # Test quality checking
            result = await mcp_client.call_tool(
                "quality.check_deliverable",
                {
                    "item": "Test Item",
                    "category": "Testing",
                    "criteria": "Basic quality criteria",
                },
            )

            if result and "Quality Checker" in result:
                self.log_test("Quality Tool", True, "Quality check successful")
            else:
                self.log_test("Quality Tool", False, "Quality check failed")

            return True

        except Exception as e:
            self.log_test("Quality Tool", False, f"Error: {e}")
            return False

    async def test_db_tool(self):
        """Test database query tool"""
        print("\n🗄️  Testing Database Tool...")

        try:
            # Test database query
            result = await mcp_client.call_tool(
                "db.query", {"query": "SELECT * FROM test_table"}
            )

            if result and "Database" in result:
                self.log_test("Database Tool", True, "Database query successful")
            else:
                self.log_test("Database Tool", False, "Database query failed")

            return True

        except Exception as e:
            self.log_test("Database Tool", False, f"Error: {e}")
            return False

    async def test_file_tool(self):
        """Test file read tool"""
        print("\n📁 Testing File Tool...")

        try:
            # Test file reading
            result = await mcp_client.call_tool(
                "file.read", {"path": "requirements.txt"}
            )

            if result and "File System" in result:
                self.log_test("File Tool", True, "File read successful")
            else:
                self.log_test("File Tool", False, "File read failed")

            return True

        except Exception as e:
            self.log_test("File Tool", False, f"Error: {e}")
            return False

    async def test_sheet_selector_tool(self):
        """Test sheet selector tool"""
        print("\n📊 Testing Sheet Selector Tool...")

        try:
            # Test sheet listing
            result = await mcp_client.call_tool(
                "sheets.select_sheet", {"spreadsheet_id": "", "range_name": ""}
            )

            if result and (
                "📋 Found" in result or "❌ No Google Sheets found" in result
            ):
                self.log_test("Sheet Selector Tool", True, "Sheet selector working")
            else:
                self.log_test("Sheet Selector Tool", False, "Sheet selector failed")

            return True

        except Exception as e:
            self.log_test("Sheet Selector Tool", False, f"Error: {e}")
            return False

    async def test_legacy_functions(self):
        """Test legacy compatibility functions"""
        print("\n🔄 Testing Legacy Functions...")

        try:
            # Import the legacy functions from the module
            from mcp_client import (
                get_mcp_event_task,
                get_mcp_fundraising_task,
                get_mcp_quality_check_task,
            )

            # Test legacy event task
            event_task = await get_mcp_event_task()
            if callable(event_task):
                result = await event_task("Test Legacy Event")
                if result and "Event Coordinator" in result:
                    self.log_test(
                        "Legacy Event Task", True, "Legacy event task working"
                    )
                else:
                    self.log_test(
                        "Legacy Event Task", False, "Legacy event task failed"
                    )
            else:
                self.log_test(
                    "Legacy Event Task", False, "Legacy event task not callable"
                )

            # Test legacy fundraising task
            fundraising_task = await get_mcp_fundraising_task()
            if callable(fundraising_task):
                result = await fundraising_task("Test Legacy Fundraising")
                if result and "Fundraising Coordinator" in result:
                    self.log_test(
                        "Legacy Fundraising Task",
                        True,
                        "Legacy fundraising task working",
                    )
                else:
                    self.log_test(
                        "Legacy Fundraising Task",
                        False,
                        "Legacy fundraising task failed",
                    )
            else:
                self.log_test(
                    "Legacy Fundraising Task",
                    False,
                    "Legacy fundraising task not callable",
                )

            # Test legacy quality check task
            quality_task = await get_mcp_quality_check_task()
            if callable(quality_task):
                result = await quality_task("Test Legacy Quality")
                if result and "Quality Checker" in result:
                    self.log_test(
                        "Legacy Quality Task", True, "Legacy quality task working"
                    )
                else:
                    self.log_test(
                        "Legacy Quality Task", False, "Legacy quality task failed"
                    )
            else:
                self.log_test(
                    "Legacy Quality Task", False, "Legacy quality task not callable"
                )

            return True

        except Exception as e:
            self.log_test("Legacy Functions", False, f"Error: {e}")
            return False

    async def test_error_handling(self):
        """Test error handling for invalid tools"""
        print("\n⚠️  Testing Error Handling...")

        try:
            # Test calling non-existent tool
            result = await mcp_client.call_tool("non.existent.tool", {})

            if result and "Unknown tool" in result:
                self.log_test(
                    "Invalid Tool Handling", True, "Properly handled invalid tool"
                )
            else:
                self.log_test(
                    "Invalid Tool Handling",
                    False,
                    "Did not handle invalid tool properly",
                )

            # Test calling tool with invalid parameters
            result = await mcp_client.call_tool(
                "event.plan_event", {"invalid_param": "value"}
            )

            if result and "Event Coordinator" in result:
                self.log_test(
                    "Invalid Parameters Handling",
                    True,
                    "Properly handled invalid parameters",
                )
            else:
                self.log_test(
                    "Invalid Parameters Handling",
                    False,
                    "Did not handle invalid parameters properly",
                )

            return True

        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {e}")
            return False

    async def run_all_tests(self):
        """Run all MCP tests"""
        print("🔧 MCP Client Test Suite")
        print("=" * 50)

        # Run tests in order
        await self.test_tool_discovery()
        await self.test_tool_filtering()
        await self.test_tool_function_creation()
        await self.test_event_tool()
        await self.test_fundraising_tool()
        await self.test_quality_tool()
        await self.test_db_tool()
        await self.test_file_tool()
        await self.test_sheet_selector_tool()
        await self.test_legacy_functions()
        await self.test_error_handling()

        # Print summary
        print("\n" + "=" * 50)
        print("📊 MCP Test Summary")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(
            f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%"
        )

        if self.failed == 0:
            print("\n🎉 All MCP tests passed!")
        else:
            print(f"\n⚠️  {self.failed} MCP test(s) failed.")


async def interactive_mcp_test():
    """Interactive MCP testing"""
    print("🎯 Interactive MCP Testing")
    print("=" * 40)

    while True:
        print("\nOptions:")
        print("1. List all available tools")
        print("2. Test event planning")
        print("3. Test fundraising")
        print("4. Test quality check")
        print("5. Test sheet selector")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            print("\n🔍 Listing all tools...")
            tools = await mcp_client.get_tools()
            if tools:
                print(f"Found {len(tools)} tools:")
                for tool_name, tool_info in tools.items():
                    print(
                        f"  - {tool_name}: {tool_info.get('description', 'No description')}"
                    )
            else:
                print("No tools found")

        elif choice == "2":
            print("\n📅 Testing event planning...")
            result = await mcp_client.call_tool(
                "event.plan_event",
                {
                    "event_name": "Interactive Test Event",
                    "theme": "Interactive Testing",
                    "organization": "Test Org",
                },
            )
            print(result)

        elif choice == "3":
            print("\n💰 Testing fundraising...")
            result = await mcp_client.call_tool(
                "fundraising.create_plan",
                {
                    "goal": "Interactive Test Goal",
                    "event_name": "Test Event",
                    "budget_target": 10000,
                },
            )
            print(result)

        elif choice == "4":
            print("\n✅ Testing quality check...")
            result = await mcp_client.call_tool(
                "quality.check_deliverable",
                {
                    "item": "Interactive Test Item",
                    "category": "Interactive Testing",
                    "criteria": "Interactive test criteria",
                },
            )
            print(result)

        elif choice == "5":
            print("\n📊 Testing sheet selector...")
            result = await mcp_client.sheets_select_sheet("", "")
            print(result)

        elif choice == "6":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1-6.")


async def main():
    """Main MCP test runner"""
    print("Choose option:")
    print("1. Run automated tests")
    print("2. Interactive testing")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        test_suite = MCPTestSuite()
        await test_suite.run_all_tests()
    elif choice == "2":
        await interactive_mcp_test()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
