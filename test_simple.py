#!/usr/bin/env python3
"""
Simple test script that doesn't require OAuth authentication
Tests basic MCP client functionality and API key usage
"""

import asyncio
import os
from mcp_client import mcp_client, MCPClient


async def simple_test():
    """Run a simple test without OAuth requirements"""
    print("🧪 Simple MCP Client Test")
    print("=" * 40)

    # Test 1: Check if MCP client works
    print("\n1. Testing MCP Client...")
    try:
        tools = await mcp_client.get_tools(["event.*"])
        print(f"✅ Found {len(tools)} event tools")
        for tool_name in tools.keys():
            print(f"   - {tool_name}")
    except Exception as e:
        print(f"❌ MCP Client error: {e}")
        return False

    # Test 2: Test event tool without sheets
    print("\n2. Testing event tool (basic)...")
    try:
        result = await mcp_client.call_tool(
            "event.plan_event",
            {
                "event_name": "Simple Test Event",
                "theme": "Testing",
                "organization": "Test Org",
            },
        )
        print(f"✅ Basic event tool works: {result[:100]}...")
    except Exception as e:
        print(f"❌ Event tool error: {e}")
        return False

    # Test 3: Test tool function creation
    print("\n3. Testing tool function creation...")
    try:
        event_functions = await mcp_client.create_tool_functions(["event.*"])
        if "event.plan_event" in event_functions:
            print("✅ Event function created successfully")
        else:
            print("❌ Event function not found")
            return False
    except Exception as e:
        print(f"❌ Function creation error: {e}")
        return False

    # Test 4: Test other tools
    print("\n4. Testing other tools...")
    try:
        # Test fundraising tool
        fundraising_result = await mcp_client.call_tool(
            "fundraising.create_plan",
            {"goal": "Test fundraising goal", "event_name": "Test Event"},
        )
        print(f"✅ Fundraising tool works: {fundraising_result[:50]}...")

        # Test quality check tool
        quality_result = await mcp_client.call_tool(
            "quality.check_deliverable",
            {"item": "Test item", "category": "Test category"},
        )
        print(f"✅ Quality tool works: {quality_result[:50]}...")

    except Exception as e:
        print(f"❌ Other tools error: {e}")
        return False

    print("\n🎉 All simple tests passed!")
    print("\nNote: Google Sheets integration requires proper OAuth setup.")
    print("To test with Google Sheets, you need to:")
    print("1. Set up OAuth credentials in Google Cloud Console")
    print("2. Add 'http://localhost:8080' to authorized redirect URIs")
    print("3. Or use a Google Cloud API key for public sheets only")

    return True


if __name__ == "__main__":
    success = asyncio.run(simple_test())
    if not success:
        print("\n❌ Some tests failed.")
        exit(1)
    else:
        print("\n✅ Everything looks good!")
        exit(0)
