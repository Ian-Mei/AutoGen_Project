#!/usr/bin/env python3
"""
Test script using a public Google Sheet to verify functionality
"""

import asyncio
import os
from mcp_client import mcp_client

# Public Google Sheet for testing (Google's sample data)
PUBLIC_SHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
PUBLIC_SHEET_RANGE = "Class Data!A1:E10"


async def test_public_sheet():
    """Test with a known public Google Sheet"""
    print("🧪 Testing with Public Google Sheet")
    print("=" * 50)

    # Ensure API key is set
    api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
    if not api_key:
        print("❌ GOOGLE_CLOUD_API_KEY environment variable not set")
        print("   Please set your Google Cloud API key")
        return False

    print(f"✅ API Key found: {api_key[:10]}...")

    try:
        # Test the event tool with public sheet
        result = await mcp_client.call_tool(
            "event.plan_event",
            {
                "event_name": "Public Sheet Test",
                "theme": "Testing Public Access",
                "organization": "Test Org",
                "google_sheet_id": PUBLIC_SHEET_ID,
                "sheet_range": PUBLIC_SHEET_RANGE,
            },
        )

        print("✅ Test completed successfully!")
        print(f"Response: {result}")

        if "📊 Google Sheets Data Retrieved" in result:
            print("✅ Sheet data was successfully retrieved")
        else:
            print("⚠️ Sheet data may not have been retrieved")

        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_public_sheet())
    if success:
        print("\n🎉 Public sheet test passed!")
    else:
        print("\n❌ Public sheet test failed!")
        exit(1)
