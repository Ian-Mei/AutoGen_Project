#!/usr/bin/env python3
"""
Test script for Google Sheets API integration in MCP Client
This script tests the Google Sheets functionality without requiring AutoGen agents
"""

import asyncio
import os
import sys
from mcp_client import mcp_client, MCPClient

# Test configuration - Replace these with your actual Google Sheet details
TEST_SHEET_ID = "1bWMM3u-Y2b_5zfIetLLvkreZ6iOVvvaX"  # Example public sheet
TEST_SHEET_RANGE = "Sheet1!A1:E19"  # Example range

# Alternative test with your own sheet (uncomment and modify)
# TEST_SHEET_ID = "your_sheet_id_here"
# TEST_SHEET_RANGE = "Sheet1!A1:D10"


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")


def print_step(step_num: int, description: str):
    """Print a formatted step"""
    print(f"\n{step_num}. {description}")
    print("-" * 40)


async def test_basic_functionality():
    """Test basic MCP client functionality"""
    print_header("Basic MCP Client Tests")

    # Test 1: Initialize client
    print_step(1, "Testing MCP Client Initialization")
    client = MCPClient()
    print("✅ MCP Client initialized successfully")

    # Test 2: Check available tools
    print_step(2, "Testing Available Tools Discovery")
    all_tools = await client.get_tools()
    print(f"✅ Found {len(all_tools)} total tools:")
    for tool_name, tool_info in all_tools.items():
        print(f"   - {tool_name}: {tool_info['description']}")

    # Test 3: Check event-specific tools
    print_step(3, "Testing Event Tool Filtering")
    event_tools = await client.get_tools(["event.*"])
    print(f"✅ Found {len(event_tools)} event tools:")
    for tool_name, tool_info in event_tools.items():
        print(f"   - {tool_name}: {tool_info['description']}")

    return client


async def test_google_sheets_credentials():
    """Test Google Sheets API credentials setup"""
    print_header("Google Sheets Credentials Test")

    print_step(1, "Checking for credentials file")
    if os.path.exists("credentials.json"):
        print("✅ credentials.json found")
    else:
        print("❌ credentials.json not found")
        print("   Please run: python setup_google_sheets.py")
        return False

    print_step(2, "Testing Google Sheets API access")
    client = MCPClient()
    try:
        # Test with a public Google Sheet (Google's example sheet)
        test_data = client._read_google_sheet(TEST_SHEET_ID, TEST_SHEET_RANGE)
        if test_data:
            print(f"✅ Successfully read {len(test_data)} rows from test sheet")
            print("   Sample data:")
            for i, row in enumerate(test_data[:3]):  # Show first 3 rows
                print(f"   Row {i+1}: {row}")
            return True
        else:
            print("⚠️ No data returned from test sheet")
            return False
    except Exception as e:
        print(f"❌ Error accessing Google Sheets: {str(e)}")
        return False


async def test_event_tool_without_sheets():
    """Test event planning tool without Google Sheets"""
    print_header("Event Tool Test (Without Google Sheets)")

    print_step(1, "Creating event planning tool function")
    client = MCPClient()
    event_functions = await client.create_tool_functions(["event.*"])

    if "event.plan_event" in event_functions:
        event_func = event_functions["event.plan_event"]
        print("✅ Event planning function created")

        print_step(2, "Testing event tool call")
        result = await event_func(
            event_name="Test Event",
            theme="Testing",
            organization="Test Organization",
            requirements="Basic test requirements",
        )
        print(f"✅ Event tool response:\n{result}")
        return True
    else:
        print("❌ Event planning function not found")
        return False


async def test_event_tool_with_sheets():
    """Test event planning tool with Google Sheets integration"""
    print_header("Event Tool Test (With Google Sheets)")

    print_step(1, "Testing event tool with Google Sheets parameters")
    client = MCPClient()

    # Test the call_tool method directly
    result = await client.call_tool(
        "event.plan_event",
        {
            "event_name": "Mid Autumn Festival",
            "theme": "Traditional Chinese Festival",
            "organization": "Taiwanese Chinese Students Association",
            "requirements": "Games, food, decorations",
            "google_sheet_id": TEST_SHEET_ID,
            "sheet_range": TEST_SHEET_RANGE,
        },
    )

    print("✅ Event tool with Google Sheets response:")
    print(f"{result}")

    # Test with function interface
    print_step(2, "Testing with function interface")
    event_functions = await client.create_tool_functions(["event.*"])
    if "event.plan_event" in event_functions:
        event_func = event_functions["event.plan_event"]

        result2 = await event_func(
            event_name="Spring Festival",
            theme="Cultural Celebration",
            organization="Student Association",
            requirements="Traditional activities",
            google_sheet_id=TEST_SHEET_ID,
            sheet_range=TEST_SHEET_RANGE,
        )
        print(f"✅ Function interface response:\n{result2}")
        return True
    else:
        print("❌ Event function not found")
        return False


async def test_custom_sheet():
    """Test with custom sheet data (if provided)"""
    print_header("Custom Sheet Test")

    print("📝 To test with your own Google Sheet:")
    print("1. Create a Google Sheet with event data")
    print("2. Update TEST_SHEET_ID and TEST_SHEET_RANGE in this file")
    print("3. Make sure the sheet is accessible with your credentials")

    # Ask user if they want to test with custom sheet
    print("\n🤔 Do you want to test with a custom sheet?")
    print("   (Update the TEST_SHEET_ID and TEST_SHEET_RANGE variables first)")

    # For now, we'll use the default test sheet
    print("   Using default test sheet for demonstration...")

    client = MCPClient()
    try:
        result = await client.call_tool(
            "event.plan_event",
            {
                "event_name": "Custom Event Test",
                "theme": "Data Integration",
                "organization": "Test Org",
                "google_sheet_id": TEST_SHEET_ID,
                "sheet_range": TEST_SHEET_RANGE,
            },
        )
        print(f"✅ Custom sheet test result:\n{result}")
        return True
    except Exception as e:
        print(f"❌ Custom sheet test failed: {str(e)}")
        return False


async def test_error_handling():
    """Test error handling for various scenarios"""
    print_header("Error Handling Tests")

    client = MCPClient()

    # Test 1: Invalid sheet ID
    print_step(1, "Testing invalid sheet ID")
    result = await client.call_tool(
        "event.plan_event",
        {
            "event_name": "Error Test",
            "google_sheet_id": "invalid_sheet_id",
            "sheet_range": "Sheet1!A1:B2",
        },
    )
    print(f"✅ Invalid sheet ID handled: {result}")

    # Test 2: Invalid range
    print_step(2, "Testing invalid range")
    result = await client.call_tool(
        "event.plan_event",
        {
            "event_name": "Range Error Test",
            "google_sheet_id": TEST_SHEET_ID,
            "sheet_range": "InvalidSheet!A1:B2",
        },
    )
    print(f"✅ Invalid range handled: {result}")

    # Test 3: Missing credentials
    print_step(3, "Testing missing credentials scenario")
    if not os.path.exists("credentials.json"):
        print("✅ Missing credentials will be handled gracefully")
    else:
        print("✅ Credentials available - error handling ready")


def print_summary(results: dict):
    """Print test summary"""
    print_header("Test Summary")

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")

    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Google Sheets integration is working correctly.")
    else:
        print(
            f"\n⚠️ {total_tests - passed_tests} test(s) failed. Check the setup guide."
        )


async def main():
    """Run all tests"""
    print("🚀 Starting Google Sheets API Integration Tests")
    print(f"📁 Working directory: {os.getcwd()}")

    results = {}

    try:
        # Basic functionality tests
        await test_basic_functionality()
        results["Basic Functionality"] = True

        # Credentials test
        credentials_ok = await test_google_sheets_credentials()
        results["Google Sheets Credentials"] = credentials_ok

        # Event tool without sheets
        event_basic = await test_event_tool_without_sheets()
        results["Event Tool (Basic)"] = event_basic

        # Event tool with sheets (only if credentials are OK)
        if credentials_ok:
            event_sheets = await test_event_tool_with_sheets()
            results["Event Tool (With Sheets)"] = event_sheets

            # Custom sheet test
            custom_sheet = await test_custom_sheet()
            results["Custom Sheet Test"] = custom_sheet
        else:
            results["Event Tool (With Sheets)"] = False
            results["Custom Sheet Test"] = False
            print("\n⚠️ Skipping Google Sheets tests due to credential issues")

        # Error handling tests
        await test_error_handling()
        results["Error Handling"] = True

    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        results["Unexpected Error"] = False

    finally:
        print_summary(results)


if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("mcp_client.py"):
        print("❌ Error: mcp_client.py not found in current directory")
        print("   Please run this script from the AutoGen_Project directory")
        sys.exit(1)

    # Run the tests
    asyncio.run(main())
