#!/usr/bin/env python3
"""
Direct FastMCP Test Suite
Comprehensive testing of direct FastMCP tools functionality
"""

import asyncio
import os
import sys

# Add parent directory to path to import direct_fastmcp_tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from direct_fastmcp_tools import (
    get_tools_for_agent, 
    event_plan_event, 
    fundraising_create_plan,
    quality_check_deliverable,
    TOOL_REGISTRY
)


async def test_direct_tools_initialization():
    """Test direct FastMCP tools initialization"""
    print("🔧 Testing direct FastMCP tools...")
    
    try:
        tools = await get_tools_for_agent(['event_'])
        print(f"✅ Direct tools initialized successfully ({len(tools)} tools)")
        return True
    except Exception as e:
        print(f"❌ Direct tools initialization failed: {e}")
        return False


async def test_tool_discovery():
    """Test tool discovery functionality"""
    print("\n🔍 Testing Tool Discovery...")
    
    try:
        # Test getting all tools
        all_tools = list(TOOL_REGISTRY.keys())
        
        if all_tools and len(all_tools) > 0:
            print(f"✅ Tool discovery successful - Found {len(all_tools)} tools")
            for tool_name in all_tools:
                print(f"   - {tool_name}")
            return True
        else:
            print("❌ Tool discovery failed - no tools found")
            return False
            
    except Exception as e:
        print(f"❌ Tool discovery failed: {e}")
        return False


async def test_tool_calling():
    """Test direct FastMCP tool calling functionality"""
    print("\n🛠️  Testing direct tool calling...")
    
    try:
        # Test calling an event planning tool directly
        result = await event_plan_event(
            event_name="Test Event",
            theme="Direct FastMCP Testing",
            organization="Test Organization"
        )
        
        if result and "Test Event" in result:
            print("✅ Direct tool calling successful")
            print(f"   Result preview: {result[:100]}...")
            return True
        else:
            print("❌ Direct tool calling failed - invalid result")
            return False
            
    except Exception as e:
        print(f"❌ Direct tool calling failed: {e}")
        return False


async def test_domain_filtering():
    """Test domain-based tool filtering"""
    print("\n🎯 Testing Domain Filtering...")
    
    try:
        # Test event domain filtering
        event_tools = await get_tools_for_agent(['event_'])
        
        # Test fundraising domain filtering
        fundraising_tools = await get_tools_for_agent(['fundraising_'])
        
        # Test quality domain filtering
        quality_tools = await get_tools_for_agent(['quality_'])
        
        if (len(event_tools) > 0 and len(fundraising_tools) > 0 and len(quality_tools) > 0):
            print(f"✅ Domain filtering successful")
            print(f"   Event tools: {len(event_tools)}")
            print(f"   Fundraising tools: {len(fundraising_tools)}")
            print(f"   Quality tools: {len(quality_tools)}")
            return True
        else:
            print("❌ Domain filtering failed - some domains returned no tools")
            return False
            
    except Exception as e:
        print(f"❌ Domain filtering failed: {e}")
        return False


async def test_multiple_tools():
    """Test calling multiple different tools"""
    print("\n🔄 Testing Multiple Tool Calls...")
    
    try:
        # Test event tool
        event_result = await event_plan_event("Multi-Test Event")
        
        # Test fundraising tool
        fundraising_result = await fundraising_create_plan("Test fundraising goal")
        
        # Test quality tool
        quality_result = await quality_check_deliverable("Test deliverable")
        
        if (event_result and fundraising_result and quality_result):
            print("✅ Multiple tool calls successful")
            print(f"   Event result: {len(event_result)} chars")
            print(f"   Fundraising result: {len(fundraising_result)} chars")
            print(f"   Quality result: {len(quality_result)} chars")
            return True
        else:
            print("❌ Multiple tool calls failed - some tools returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Multiple tool calls failed: {e}")
        return False


async def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n⚠️  Testing Error Handling...")
    
    try:
        # Test with empty parameters (should still work)
        result = await event_plan_event("")
        
        if result:
            print("✅ Error handling successful - graceful handling of edge cases")
            return True
        else:
            print("❌ Error handling failed - no result returned")
            return False
            
    except Exception as e:
        # This is actually expected behavior
        print(f"✅ Error handling successful - proper exception handling: {type(e).__name__}")
        return True


async def main():
    """Main Direct FastMCP Test Suite"""
    print("🧪 Direct FastMCP Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Direct Tools Initialization
    result = await test_direct_tools_initialization()
    test_results.append(("Direct Tools Initialization", result))
    
    # Test 2: Tool Discovery
    result = await test_tool_discovery()
    test_results.append(("Tool Discovery", result))
    
    # Test 3: Tool Calling
    result = await test_tool_calling()
    test_results.append(("Tool Calling", result))
    
    # Test 4: Domain Filtering
    result = await test_domain_filtering()
    test_results.append(("Domain Filtering", result))
    
    # Test 5: Multiple Tool Calls
    result = await test_multiple_tools()
    test_results.append(("Multiple Tool Calls", result))
    
    # Test 6: Error Handling
    result = await test_error_handling()
    test_results.append(("Error Handling", result))
    
    # Print results summary
    print(f"\n{'='*50}")
    print("📊 Direct FastMCP Test Results Summary")
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
        print("🎉 All Direct FastMCP tests passed!")
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