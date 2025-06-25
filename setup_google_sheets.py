#!/usr/bin/env python3
"""
Setup script for Google Sheets API integration
This script helps you set up the Google Sheets API credentials
"""

import os


def setup_google_sheets():
    """Guide user through Google Sheets API setup"""
    print("🔧 Google Sheets API Setup Guide")
    print("=" * 40)

    print("\n🚨 SECURITY WARNING:")
    print("   The credentials.json file contains sensitive data!")
    print("   - NEVER commit it to version control")
    print("   - NEVER share it publicly")
    print("   - Store it securely on your local machine only")
    print("   - See SECURITY.md for full security guidelines")

    print("\n1. Go to the Google Cloud Console:")
    print("   https://console.cloud.google.com/")

    print("\n2. Create a new project or select an existing one")

    print("\n3. Enable the Google Sheets API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Sheets API'")
    print("   - Click 'Enable'")

    print("\n4. Create credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - Choose 'Desktop application'")
    print("   - Download the JSON file")

    print("\n5. Save the downloaded JSON file as 'credentials.json' in this directory:")
    print(f"   {os.getcwd()}")

    print("\n6. Create a test Google Sheet and note down:")
    print("   - The Sheet ID (from the URL)")
    print("   - The range you want to read (e.g., 'Sheet1!A1:D10')")

    print(
        "\n7. Run your main.py script - it will prompt for authorization on first run"
    )

    print("\n📝 Example Google Sheet structure for event planning:")
    print("   A1: Event Name    | B1: Theme         | C1: Date      | D1: Budget")
    print("   A2: Mid Autumn    | B2: Festival      | C2: 2024-09-15| D2: 5000")
    print("   A3: Spring Mixer  | B3: Social        | C3: 2024-03-20| D3: 3000")

    # Check if credentials file exists
    if os.path.exists("credentials.json"):
        print("\n✅ credentials.json found!")
    else:
        print("\n❌ credentials.json not found - please download and save it here")

    print(
        "\n🚀 Once setup is complete, you can use the event planning tool with Google Sheets!"
    )


if __name__ == "__main__":
    setup_google_sheets()
