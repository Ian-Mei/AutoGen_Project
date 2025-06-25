#!/usr/bin/env python3
"""
Script to create a test Google Sheet for testing the AutoGen integration
"""

import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def create_test_sheet():
    """Create a test Google Sheet with sample data"""

    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                print(
                    "❌ credentials.json not found. Please run setup_google_sheets.py first."
                )
                return None
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)

    # Create a new spreadsheet
    spreadsheet = {
        "properties": {"title": "AutoGen Test Sheet"},
        "sheets": [{"properties": {"title": "Event Data"}}],
    }

    try:
        spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet["spreadsheetId"]

        print(f"✅ Created new Google Sheet: {spreadsheet_id}")
        print(f"📊 Sheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

        # Add sample data
        sample_data = [
            ["Event Name", "Date", "Location", "Budget", "Attendees"],
            ["Mid Autumn Festival", "2024-09-15", "Campus Center", 5000, 200],
            ["Spring Festival", "2024-02-10", "Student Union", 3000, 150],
            ["Cultural Night", "2024-11-20", "Auditorium", 4000, 180],
            ["Study Group", "2024-10-05", "Library", 500, 30],
            ["Workshop", "2024-12-01", "Classroom 101", 1000, 50],
        ]

        body = {"values": sample_data}

        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range="Event Data!A1:E6",
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

        print(f"✅ Added sample data: {result.get('updatedCells')} cells updated")
        print(f"📋 Range: Event Data!A1:E6")

        return spreadsheet_id

    except Exception as e:
        print(f"❌ Error creating sheet: {str(e)}")
        return None


if __name__ == "__main__":
    print("🚀 Creating Test Google Sheet for AutoGen Integration")
    print("=" * 60)

    sheet_id = create_test_sheet()

    if sheet_id:
        print("\n🎉 Success! Your test sheet is ready.")
        print(
            f"\n📝 To use this sheet in your tests, update the sheet ID to: {sheet_id}"
        )
        print("📋 Range: Event Data!A1:E6")
        print("\n🔗 Sheet URL: https://docs.google.com/spreadsheets/d/" + sheet_id)
        print("\n💡 You can now test with:")
        print(f"   Sheet ID: {sheet_id}")
        print("   Range: Event Data!A1:E6")
    else:
        print("\n❌ Failed to create test sheet. Check your credentials.")
