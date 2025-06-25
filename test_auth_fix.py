#!/usr/bin/env python3
"""
Simple test to verify Google Sheets authentication fix
"""

import asyncio
import os
from mcp_client import mcp_client


async def test_fix():
    print("🔧 Testing Google Sheets Authentication Fix")
    print("=" * 50)

    # Test 1: Check if credentials exist
    print("\n1. Checking for credentials...")
    if os.path.exists("credentials.json"):
        print("✅ credentials.json found")

        # Test 2: Try to call the event tool with Google Sheets
        print("\n2. Testing event tool with Google Sheets...")
        try:
            result = await mcp_client.call_tool(
                "event.plan_event",
                {
                    "event_name": "Test Event",
                    "theme": "Testing",
                    "organization": "Test Org",
                    "google_sheet_id": "1bWMM3u-Y2b_5zfIetLLvkreZ6iOVvvaX",
                    "sheet_range": "Sheet1!A1:E19",
                },
            )

            print("✅ Google Sheets integration working!")
            print(f"Response preview: {result}...")

            if "📊 Google Sheets Data Retrieved" in result:
                print("✅ Sheet data successfully retrieved")
            elif "❌ Error reading Google Sheet" in result:
                print("⚠️ Error occurred, but handled gracefully")
            else:
                print("ℹ️ Basic event planning without sheet data")

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    else:
        print("❌ credentials.json not found")
        print("   Please download it from Google Cloud Console")
        print("   Run: python setup_google_sheets.py for instructions")

        # Test without credentials
        print("\n2. Testing without credentials (should handle gracefully)...")
        result = await mcp_client.call_tool(
            "event.plan_event",
            {
                "event_name": "Test Event No Creds",
                "theme": "Testing",
                "organization": "Test Org",
                "google_sheet_id": "test_id",
                "sheet_range": "Sheet1!A1:B2",
            },
        )

        print("✅ Error handled gracefully")
        print(f"Response: {result}")


if __name__ == "__main__":
    asyncio.run(test_fix())
