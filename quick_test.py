#!/usr/bin/env python3
"""
Quick test runner for Google Sheets API integration
Run this to quickly check if everything is working
"""

import asyncio
import os
from mcp_client import mcp_client


async def quick_test():
    """Run a quick test of the Google Sheets integration"""
    print("🚀 Quick Google Sheets API Test")
    print("=" * 40)

    # Test 1: Check if MCP client works
    print("\n1. Testing MCP Client...")
    try:
        tools = await mcp_client.get_tools(["event.*"])
        print(f"✅ Found {len(tools)} event tools")
    except Exception as e:
        print(f"❌ MCP Client error: {e}")
        return False

    # Test 2: Check credentials
    print("\n2. Checking credentials...")
    if os.path.exists("credentials.json"):
        print("✅ credentials.json found")
    else:
        print("❌ credentials.json not found")
        print("   Run: python setup_google_sheets.py")
        return False

    # Test 3: Test event tool without sheets
    print("\n3. Testing event tool (basic)...")
    try:
        result = await mcp_client.call_tool(
            "event.plan_event",
            {
                "event_name": "Quick Test Event",
                "theme": "Testing",
                "organization": "Test Org",
            },
        )
        print(f"✅ Basic event tool works: {result}...")
    except Exception as e:
        print(f"❌ Event tool error: {e}")
        return False

    # Test 4: Test with Google Sheets (using public example)
    print("\n4. Testing with Google Sheets...")
    try:
        result = await mcp_client.call_tool(
            "event.plan_event",
            {
                "event_name": "Sheets Test Event",
                "theme": "Data Integration",
                "organization": "Test Org",
                "google_sheet_id": "1bWMM3u-Y2b_5zfIetLLvkreZ6iOVvvaX",
                "sheet_range": "Sheet1!A1:E19",
            },
        )
        print("✅ Google Sheets integration works!")
        print(f"   Response: {result}...")  # Print first 100 chars
        print(f"   Response length: {len(result)} characters")
        if "📊 Google Sheets Data Retrieved" in result:
            print("   ✅ Sheet data was successfully retrieved")
        else:
            print("   ⚠️ Sheet data may not have been retrieved")
    except Exception as e:
        print(f"❌ Google Sheets error: {e}")
        return False

    print("\n🎉 All quick tests passed!")
    print("\nTo run full tests: python test_google_sheets.py")
    return True


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    if not success:
        print("\n❌ Some tests failed. Check the setup guide.")
        exit(1)
    else:
        print("\n✅ Everything looks good!")
        exit(0)
