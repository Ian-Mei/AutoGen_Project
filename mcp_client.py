#!/usr/bin/env python3
"""
MCP Client for AutoGen Integration with Dynamic Tool Discovery
Connects to the unified MCP server and provides tool functions for AutoGen agents
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Callable
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Tool name constants
EVENT_PLAN_TOOL = "event.plan_event"
FUNDRAISING_PLAN_TOOL = "fundraising.create_plan"
QUALITY_CHECK_TOOL = "quality.check_deliverable"
DB_QUERY_TOOL = "db.query"
FILE_READ_TOOL = "file.read"

# Google Sheets API configuration
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


class MCPClient:
    def __init__(self):
        self.server_process = None
        self.available_tools = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize available tools registry"""
        self.available_tools = {
            EVENT_PLAN_TOOL: {
                "description": "Plan an event with specified details, optionally reading from Google Sheets",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_name": {"type": "string"},
                        "theme": {"type": "string"},
                        "organization": {"type": "string"},
                        "requirements": {"type": "string"},
                        "google_sheet_id": {
                            "type": "string",
                            "description": "Google Sheets ID to read event data from",
                        },
                        "sheet_range": {
                            "type": "string",
                            "description": "Range in the sheet to read (e.g., 'Sheet1!A1:D10')",
                        },
                    },
                    "required": ["event_name"],
                },
            },
            FUNDRAISING_PLAN_TOOL: {
                "description": "Create a fundraising plan",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {"type": "string"},
                        "event_name": {"type": "string"},
                        "budget_target": {"type": "number"},
                    },
                    "required": ["goal"],
                },
            },
            QUALITY_CHECK_TOOL: {
                "description": "Perform quality assurance checks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item": {"type": "string"},
                        "category": {"type": "string"},
                        "criteria": {"type": "string"},
                    },
                    "required": ["item"],
                },
            },
            DB_QUERY_TOOL: {
                "description": "Execute database queries",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
            FILE_READ_TOOL: {
                "description": "Read file contents",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
        }

    def _get_google_sheets_service(self):
        """Initialize Google Sheets API service"""
        # Try API key first (for public sheets only)
        api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        if api_key:
            print("🔑 Using Google Cloud API key for public sheets access")
            service = build("sheets", "v4", developerKey=api_key)
            return service

        # Fallback to OAuth for private sheets
        print("🔐 Using OAuth credentials for private sheets access")
        print(
            "⚠️  Note: If you get 'access_denied' error, add your email as a test user in Google Cloud Console"
        )
        creds = None

        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Google Sheets credentials file '{CREDENTIALS_FILE}' not found. "
                        "Please download your credentials from Google Cloud Console or use API key for public sheets only."
                    )
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES
                    )
                    creds = flow.run_local_server(port=8080)
                except Exception as e:
                    if "access_denied" in str(e) or "403" in str(e):
                        print(
                            "❌ OAuth access denied. Please add your email as a test user in Google Cloud Console:"
                        )
                        print(
                            "   1. Go to Google Cloud Console → APIs & Services → OAuth consent screen"
                        )
                        print("   2. Scroll to 'Test users' section")
                        print("   3. Add your email address")
                        print("   4. Try again")
                        raise Exception(
                            "OAuth access denied. Add your email as a test user in Google Cloud Console."
                        )
                    else:
                        raise e

            # Save the credentials for the next run
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

        service = build("sheets", "v4", credentials=creds)
        return service

    def _read_google_sheet(
        self, spreadsheet_id: str, range_name: str
    ) -> List[List[str]]:
        """Read data from Google Sheets"""
        try:
            service = self._get_google_sheets_service()
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            values = result.get("values", [])
            return values
        except FileNotFoundError as e:
            print(f"Google Sheets credentials not found: {str(e)}")
            print("Please run: python setup_google_sheets.py")
            return []
        except Exception as e:
            print(f"Error reading Google Sheet: {str(e)}")
            print(
                "Note: API key only works for public sheets. Private sheets require OAuth credentials."
            )
            return []

    async def get_tools(self, allowed_domains: List[str] = None) -> Dict[str, Any]:
        """Get available tools, optionally filtered by domain patterns"""
        if not allowed_domains:
            return self.available_tools

        filtered_tools = {}
        for tool_name, tool_info in self.available_tools.items():
            for domain in allowed_domains:
                if domain.endswith("*"):
                    # Pattern matching (e.g., "event.*")
                    domain_prefix = domain[:-1]
                    if tool_name.startswith(domain_prefix):
                        filtered_tools[tool_name] = tool_info
                        break
                elif tool_name == domain:
                    # Exact match
                    filtered_tools[tool_name] = tool_info
                    break
        return filtered_tools

    async def create_tool_functions(
        self, allowed_domains: List[str]
    ) -> Dict[str, Callable]:
        """Create callable functions for allowed tools"""
        available_tools = await self.get_tools(allowed_domains)
        tool_functions = {}

        for tool_name, tool_info in available_tools.items():
            # Create a closure that captures the tool_name and create specific functions
            if tool_name == EVENT_PLAN_TOOL:

                async def event_plan_event(
                    event_name: str,
                    theme: str = "",
                    organization: str = "",
                    requirements: str = "",
                    google_sheet_id: str = "",
                    sheet_range: str = "",
                ) -> str:
                    """Plan an event with specified details, optionally reading from Google Sheets"""
                    return await self.call_tool(
                        EVENT_PLAN_TOOL,
                        {
                            "event_name": event_name,
                            "theme": theme,
                            "organization": organization,
                            "requirements": requirements,
                            "google_sheet_id": google_sheet_id,
                            "sheet_range": sheet_range,
                        },
                    )

                tool_functions[tool_name] = event_plan_event

            elif tool_name == FUNDRAISING_PLAN_TOOL:

                async def fundraising_create_plan(
                    goal: str, event_name: str = "", budget_target: float = 0
                ) -> str:
                    """Create a fundraising plan"""
                    return await self.call_tool(
                        FUNDRAISING_PLAN_TOOL,
                        {
                            "goal": goal,
                            "event_name": event_name,
                            "budget_target": budget_target,
                        },
                    )

                tool_functions[tool_name] = fundraising_create_plan

            elif tool_name == QUALITY_CHECK_TOOL:

                async def quality_check_deliverable(
                    item: str, category: str = "", criteria: str = ""
                ) -> str:
                    """Perform quality assurance checks"""
                    return await self.call_tool(
                        QUALITY_CHECK_TOOL,
                        {"item": item, "category": category, "criteria": criteria},
                    )

                tool_functions[tool_name] = quality_check_deliverable

            elif tool_name == DB_QUERY_TOOL:

                async def db_query(query: str) -> str:
                    """Execute database queries"""
                    return await self.call_tool(DB_QUERY_TOOL, {"query": query})

                tool_functions[tool_name] = db_query

            elif tool_name == FILE_READ_TOOL:

                async def file_read(path: str) -> str:
                    """Read file contents"""
                    return await self.call_tool(FILE_READ_TOOL, {"path": path})

                tool_functions[tool_name] = file_read

        return tool_functions

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the MCP server via subprocess"""
        try:
            # For now, simulate the MCP call with direct function calls
            # This avoids the complexity of setting up MCP client/server communication
            if name == EVENT_PLAN_TOOL:
                event_name = arguments.get("event_name", "")
                theme = arguments.get("theme", "")
                organization = arguments.get("organization", "")
                requirements = arguments.get("requirements", "")
                google_sheet_id = arguments.get("google_sheet_id", "")
                sheet_range = arguments.get("sheet_range", "")

                # Base event planning response
                response = f"Event Coordinator: Planning event '{event_name}' with theme '{theme}' for {organization}."

                if requirements:
                    response += f" Requirements: {requirements}"

                # If Google Sheets parameters are provided, read from the sheet
                if google_sheet_id and sheet_range:
                    try:
                        sheet_data = self._read_google_sheet(
                            google_sheet_id, sheet_range
                        )
                        if sheet_data:
                            response += f"\n\n📊 Google Sheets Data Retrieved ({len(sheet_data)} rows):\n"
                            # Format the sheet data nicely
                            for i, row in enumerate(sheet_data):
                                if i == 0:  # Header row
                                    response += f"Headers: {' | '.join(row)}\n"
                                else:
                                    response += f"Row {i}: {' | '.join(row)}\n"
                                if i >= 10:  # Limit to first 10 rows for readability
                                    response += (
                                        f"... and {len(sheet_data) - 10} more rows\n"
                                    )
                                    break
                        else:
                            response += f"\n⚠️ No data found in Google Sheet range '{sheet_range}'"
                    except Exception as e:
                        response += f"\n❌ Error reading Google Sheet: {str(e)}"

                return response

            elif name == FUNDRAISING_PLAN_TOOL:
                goal = arguments.get("goal", "")
                event_name = arguments.get("event_name", "")

                return f"Fundraising Coordinator: Organizing fundraising for '{goal}' related to {event_name}."

            elif name == QUALITY_CHECK_TOOL:
                item = arguments.get("item", "")
                category = arguments.get("category", "")

                return f"Quality Checker: Reviewing '{item}' for quality assurance in category '{category}'."

            elif name == DB_QUERY_TOOL:
                query = arguments.get("query", "")
                return (
                    f"Database: Executed query '{query}' - Results would appear here."
                )

            elif name == FILE_READ_TOOL:
                path = arguments.get("path", "")
                return f"File System: Read file '{path}' - Content would appear here."

            else:
                return f"Unknown tool: {name}"

        except Exception as e:
            return f"Error calling MCP tool {name}: {str(e)}"  # Legacy methods for backward compatibility

    async def event_task(self, event: str) -> str:
        """Event coordinator task using MCP"""
        return await self.call_tool(
            EVENT_PLAN_TOOL,
            {
                "event_name": event,
                "theme": "General planning",
                "organization": "AutoGen Team",
            },
        )

    async def fundraising_task(self, goal: str) -> str:
        """Fundraising coordinator task using MCP"""
        return await self.call_tool(
            FUNDRAISING_PLAN_TOOL, {"goal": goal, "event_name": "Current Event"}
        )

    async def quality_check_task(self, item: str) -> str:
        """Quality checker task using MCP"""
        return await self.call_tool(
            QUALITY_CHECK_TOOL, {"item": item, "category": "general"}
        )


# Global MCP client instance
mcp_client = MCPClient()


# Tool discovery helper functions
async def get_tools_for_agent(allowed_domains: List[str]) -> List[Callable]:
    """Get tools for an agent based on allowed domains"""
    tool_functions = await mcp_client.create_tool_functions(allowed_domains)
    return list(tool_functions.values())


async def get_event_tools() -> List[Callable]:
    """Get event-related tools"""
    return await get_tools_for_agent(["event.*"])


async def get_fundraising_tools() -> List[Callable]:
    """Get fundraising-related tools"""
    return await get_tools_for_agent(["fundraising.*"])


async def get_quality_tools() -> List[Callable]:
    """Get quality-related tools"""
    return await get_tools_for_agent(["quality.*"])


async def get_all_tools() -> List[Callable]:
    """Get all available tools"""
    return await get_tools_for_agent(["*"])


# Legacy compatibility functions
async def get_mcp_event_task():
    """Get event task function that uses MCP"""

    async def event_task(event: str) -> str:
        return await mcp_client.event_task(event)

    return event_task


async def get_mcp_fundraising_task():
    """Get fundraising task function that uses MCP"""

    async def fundraising_task(goal: str) -> str:
        return await mcp_client.fundraising_task(goal)

    return fundraising_task


async def get_mcp_quality_check_task():
    """Get quality check task function that uses MCP"""

    async def quality_check_task(item: str) -> str:
        return await mcp_client.quality_check_task(item)

    return quality_check_task
