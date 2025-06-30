#!/usr/bin/env python3
"""
Authentication Test Suite
Comprehensive testing of Google Sheets authentication and setup
"""

import asyncio
import os
import sys

# Add parent directory to path to import mcp_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from mcp_client import mcp_client

# Google Sheets API configuration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


class AuthTestSuite:
    """Authentication test suite"""

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

    def test_credentials_file(self):
        """Test if credentials file exists and is valid"""
        print("\n🔑 Testing Credentials File...")

        if not os.path.exists(CREDENTIALS_FILE):
            self.log_test(
                "Credentials File Exists", False, f"{CREDENTIALS_FILE} not found"
            )
            return False

        try:
            # Try to load the credentials file
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            self.log_test(
                "Credentials File Valid", True, "Successfully loaded credentials file"
            )
            return True
        except Exception as e:
            self.log_test("Credentials File Valid", False, f"Error loading: {e}")
            return False

    def test_token_file(self):
        """Test if token file exists and is valid"""
        print("\n🎫 Testing Token File...")

        if not os.path.exists(TOKEN_FILE):
            self.log_test("Token File Exists", False, f"{TOKEN_FILE} not found")
            return False

        try:
            # Try to load the token file
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

            if creds.valid:
                self.log_test("Token Valid", True, "Token is valid and not expired")
                return True
            elif creds.expired and creds.refresh_token:
                self.log_test(
                    "Token Expired", True, "Token expired but can be refreshed"
                )
                return True
            else:
                self.log_test(
                    "Token Valid", False, "Token is invalid and cannot be refreshed"
                )
                return False

        except Exception as e:
            self.log_test("Token File Valid", False, f"Error loading: {e}")
            return False

    async def test_oauth_flow(self):
        """Test OAuth flow"""
        print("\n🔐 Testing OAuth Flow...")

        try:
            # Remove existing token to force OAuth flow
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
                print("🗑️  Removed existing token to test OAuth flow")

            # Test OAuth flow
            service, creds = mcp_client._get_google_sheets_service_with_creds()

            if service and creds:
                self.log_test("OAuth Flow", True, "Successfully completed OAuth flow")
                return True
            else:
                self.log_test("OAuth Flow", False, "Failed to complete OAuth flow")
                return False

        except Exception as e:
            self.log_test("OAuth Flow", False, f"Error: {e}")
            return False

    async def test_service_creation(self):
        """Test Google Sheets service creation"""
        print("\n🔧 Testing Service Creation...")

        try:
            service, creds = mcp_client._get_google_sheets_service_with_creds()

            if service and creds:
                self.log_test(
                    "Service Creation",
                    True,
                    "Successfully created Google Sheets service",
                )

                # Test if service can make basic API calls
                try:
                    # Try to get user info (this should work with valid credentials)
                    from googleapiclient.discovery import build as build_drive

                    drive_service = build_drive("drive", "v3", credentials=creds)

                    # Make a simple API call
                    about = drive_service.about().get(fields="user").execute()
                    user_info = about.get("user", {})

                    if user_info:
                        self.log_test(
                            "API Access",
                            True,
                            f"Successfully accessed API as {user_info.get('emailAddress', 'Unknown')}",
                        )
                    else:
                        self.log_test("API Access", False, "No user info returned")

                except Exception as e:
                    self.log_test("API Access", False, f"Error accessing API: {e}")

                return True
            else:
                self.log_test("Service Creation", False, "Failed to create service")
                return False

        except Exception as e:
            self.log_test("Service Creation", False, f"Error: {e}")
            return False

    async def test_sheet_access(self):
        """Test access to Google Sheets"""
        print("\n📊 Testing Sheet Access...")

        try:
            # Test with a known public sheet
            sample_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            sample_range = "Class Data!A1:E5"

            result = mcp_client._read_google_sheet(sample_sheet_id, sample_range)

            if result:
                self.log_test(
                    "Public Sheet Access",
                    True,
                    f"Successfully read {len(result)} rows from public sheet",
                )
            else:
                self.log_test(
                    "Public Sheet Access", False, "Failed to read public sheet"
                )

            # Test listing user's sheets
            try:
                sheet_list_result = await mcp_client.sheets_select_sheet("", "")
                if (
                    "📋 Found" in sheet_list_result
                    or "❌ No Google Sheets found" in sheet_list_result
                ):
                    self.log_test(
                        "User Sheets Access",
                        True,
                        "Successfully accessed user's sheets",
                    )
                else:
                    self.log_test(
                        "User Sheets Access", False, "Failed to access user's sheets"
                    )
            except Exception as e:
                self.log_test("User Sheets Access", False, f"Error: {e}")

            return True

        except Exception as e:
            self.log_test("Sheet Access", False, f"Error: {e}")
            return False

    async def test_mcp_integration(self):
        """Test MCP client authentication integration"""
        print("\n🔗 Testing MCP Integration...")

        try:
            # Test if MCP client can access Google Sheets
            result = await mcp_client.call_tool(
                "event.plan_event",
                {
                    "event_name": "Auth Test Event",
                    "theme": "Testing",
                    "organization": "Test Org",
                },
            )

            if result and "Event Coordinator" in result:
                self.log_test(
                    "MCP Tool Execution", True, "Successfully executed MCP tool"
                )
            else:
                self.log_test("MCP Tool Execution", False, "Failed to execute MCP tool")

            return True

        except Exception as e:
            self.log_test("MCP Integration", False, f"Error: {e}")
            return False

    async def run_all_tests(self):
        """Run all authentication tests"""
        print("🔐 Authentication Test Suite")
        print("=" * 50)

        # Run tests in order
        self.test_credentials_file()
        self.test_token_file()
        await self.test_oauth_flow()
        await self.test_service_creation()
        await self.test_sheet_access()
        await self.test_mcp_integration()

        # Print summary
        print("\n" + "=" * 50)
        print("📊 Authentication Test Summary")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(
            f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%"
        )

        if self.failed == 0:
            print("\n🎉 All authentication tests passed!")
        else:
            print(f"\n⚠️  {self.failed} authentication test(s) failed.")
            print("💡 Check the setup instructions in setup_google_sheets.py")


def setup_instructions():
    """Display setup instructions"""
    print("🔧 Google Sheets Setup Instructions")
    print("=" * 40)
    print("\n1. Go to Google Cloud Console:")
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
    print("\n5. Save the downloaded JSON file as 'credentials.json' in this directory")
    print(f"   Current directory: {os.getcwd()}")


async def main():
    """Main authentication test runner"""
    print("Choose option:")
    print("1. Run authentication tests")
    print("2. Show setup instructions")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        test_suite = AuthTestSuite()
        await test_suite.run_all_tests()
    elif choice == "2":
        setup_instructions()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
