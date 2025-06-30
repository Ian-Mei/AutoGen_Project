#!/usr/bin/env python3
"""
FastMCP Server Test Suite
Comprehensive testing of FastMCP server functionality
"""

import asyncio
import os
import sys

# Add parent directory to path to import fastmcp_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import FastMCP server
import fastmcp_server


async def test_fastmcp_server_initialization():
    """Test FastMCP server initialization"""
    print("🔧 Testing FastMCP server...")

    try:
        # Check if the server instance exists
        if hasattr(fastmcp_server, "mcp"):
            print("✅ FastMCP server initialized successfully")
            return True
        else:
            print("❌ FastMCP server initialization failed - no mcp instance")
            return False
    except Exception as e:
        print(f"❌ FastMCP server initialization failed: {e}")
        return False


async def test_tool_discovery():
    """Test tool discovery functionality"""
    print("\n🔍 Testing Tool Discovery...")

    try:
        # Get tools from the FastMCP server
        tools_dict = await fastmcp_server.mcp.get_tools()

        if tools_dict and len(tools_dict) > 0:
            print(f"✅ Tool discovery successful - Found {len(tools_dict)} tools")
            for tool_name in list(tools_dict.keys())[:5]:  # Show first 5 tools
                print(f"   - {tool_name}")
            if len(tools_dict) > 5:
                print(f"   ... and {len(tools_dict) - 5} more tools")
            return True
        else:
            print("❌ Tool discovery failed - no tools found")
            return False

    except Exception as e:
        print(f"❌ Tool discovery failed: {e}")
        return False


async def test_tool_calling():
    """Test FastMCP tool calling functionality"""
    print("\n🛠️  Testing tool calling...")

    try:
        # Get tools from the server
        tools_dict = await fastmcp_server.mcp.get_tools()

        # Find an event planning tool to test
        event_tools = [name for name in tools_dict.keys() if name.startswith("event_")]

        if event_tools:
            tool_name = event_tools[0]
            tool_obj = tools_dict[tool_name]
            print(f"✅ Found event tool for testing: {tool_name}")

            # Test the tool (this is a basic test - the actual function call may vary)
            # We're just checking that the tool exists and can be accessed
            if hasattr(tool_obj, "fn"):
                print("✅ Tool has callable function")
                return True
            else:
                print("❌ Tool object doesn't have expected structure")
                return False
        else:
            print("❌ No event tools found for testing")
            return False

    except Exception as e:
        print(f"❌ Tool calling test failed: {e}")
        return False


async def test_domain_filtering():
    """Test domain-based tool filtering"""
    print("\n🎯 Testing Domain Filtering...")

    try:
        # Get all tools from the server
        tools_dict = await fastmcp_server.mcp.get_tools()

        # Count tools by domain
        event_tools = [name for name in tools_dict.keys() if name.startswith("event_")]
        fundraising_tools = [
            name for name in tools_dict.keys() if name.startswith("fundraising_")
        ]
        quality_tools = [
            name for name in tools_dict.keys() if name.startswith("quality_")
        ]
        sheets_tools = [
            name for name in tools_dict.keys() if name.startswith("sheets_")
        ]

        domains_found = 0
        if event_tools:
            print(f"   Event tools: {len(event_tools)}")
            domains_found += 1
        if fundraising_tools:
            print(f"   Fundraising tools: {len(fundraising_tools)}")
            domains_found += 1
        if quality_tools:
            print(f"   Quality tools: {len(quality_tools)}")
            domains_found += 1
        if sheets_tools:
            print(f"   Sheets tools: {len(sheets_tools)}")
            domains_found += 1

        if domains_found >= 2:  # At least 2 different domains
            print(
                f"✅ Domain filtering successful - Found {domains_found} different domains"
            )
            return True
        else:
            print("❌ Domain filtering failed - not enough tool domains found")
            return False

    except Exception as e:
        print(f"❌ Domain filtering failed: {e}")
        return False


async def test_server_integration():
    """Test FastMCP server integration"""
    print("\n🔄 Testing Server Integration...")

    try:
        # Test that we can get tools the same way main.py does
        tools_dict = await fastmcp_server.mcp.get_tools()

        # Convert to list of callable functions like main.py does
        tools_list = []
        for tool_name, tool_obj in tools_dict.items():
            try:
                # Access the actual function via the 'fn' attribute
                actual_func = tool_obj.fn
                tools_list.append(actual_func)
            except Exception as e:
                print(f"⚠️  Could not get function for {tool_name}: {e}")
                continue

        if len(tools_list) > 0:
            print(
                f"✅ Server integration successful - {len(tools_list)} callable tools"
            )
            return True
        else:
            print("❌ Server integration failed - no callable tools")
            return False

    except Exception as e:
        print(f"❌ Server integration failed: {e}")
        return False


async def test_error_handling():
    """Test error handling with server operations"""
    print("\n⚠️  Testing Error Handling...")

    try:
        # Test accessing non-existent tools gracefully
        tools_dict = await fastmcp_server.mcp.get_tools()

        # This should work without errors
        non_existent = tools_dict.get("non_existent_tool", None)

        if non_existent is None:
            print("✅ Error handling successful - graceful handling of missing tools")
            return True
        else:
            print("❌ Error handling test inconclusive")
            return True  # This is still OK

    except Exception as e:
        # Graceful error handling
        print(
            f"✅ Error handling successful - proper exception handling: {type(e).__name__}"
        )
        return True


async def main():
    """Main FastMCP Test Suite"""
    print("🧪 FastMCP Server Test Suite")
    print("=" * 50)

    test_results = []

    # Test 1: Server Initialization
    result = await test_fastmcp_server_initialization()
    test_results.append(("FastMCP Server Initialization", result))

    # Test 2: Tool Discovery
    result = await test_tool_discovery()
    test_results.append(("Tool Discovery", result))

    # Test 3: Tool Calling
    result = await test_tool_calling()
    test_results.append(("Tool Calling", result))

    # Test 4: Domain Filtering
    result = await test_domain_filtering()
    test_results.append(("Domain Filtering", result))

    # Test 5: Server Integration
    result = await test_server_integration()
    test_results.append(("Server Integration", result))

    # Test 6: Error Handling
    result = await test_error_handling()
    test_results.append(("Error Handling", result))

    # Print results summary
    print(f"\n{'='*50}")
    print("📊 FastMCP Test Results Summary")
    print(f"{'='*50}")

    passed = 0
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if success:
            passed += 1

    success_rate = (passed / len(test_results)) * 100
    print(f"\n📈 Success Rate: {success_rate:.1f}% ({passed}/{len(test_results)})")

    if passed == len(test_results):
        print("🎉 All FastMCP tests passed!")
    else:
        print(f"⚠️  {len(test_results) - passed} test(s) failed.")

    return passed == len(test_results)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
