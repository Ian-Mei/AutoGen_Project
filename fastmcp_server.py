#!/usr/bin/env python3
"""
FastMCP Server for AutoGen Integration
Implements MCP server using FastMCP framework with dynamic tool discovery
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Union
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Import FastMCP
from fastmcp import FastMCP

# Google Sheets API configuration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# Initialize FastMCP server
mcp = FastMCP("AutoGen Event Planning Server")


class GoogleSheetsService:
    """Google Sheets service for MCP tools"""
    
    def __init__(self):
        self._service = None
        self._credentials = None
    
    def _get_service(self):
        """Initialize Google Sheets API service"""
        if self._service:
            return self._service, self._credentials
            
        creds = None
        
        # Load existing credentials
        if os.path.exists(TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            except Exception as e:
                print(f"⚠️  Error loading credentials: {e}")
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Google Sheets credentials file '{CREDENTIALS_FILE}' not found."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=8080, open_browser=True)
                
                # Save credentials
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
        
        self._service = build("sheets", "v4", credentials=creds)
        self._credentials = creds
        return self._service, self._credentials
    
    def read_sheet(self, spreadsheet_id: str, range_name: str) -> List[List[str]]:
        """Read data from Google Sheets"""
        try:
            service, _ = self._get_service()
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            return result.get("values", [])
        except Exception as e:
            print(f"Error reading Google Sheet: {str(e)}")
            return []
    
    def list_sheets(self) -> List[Dict[str, Any]]:
        """List all available Google Sheets"""
        try:
            _, creds = self._get_service()
            if not creds:
                return []
            
            # Use Drive API to list spreadsheets
            from googleapiclient.discovery import build as build_drive
            drive_service = build_drive("drive", "v3", credentials=creds)
            
            results = (
                drive_service.files()
                .list(
                    q="mimeType='application/vnd.google-apps.spreadsheet'",
                    pageSize=20,
                    fields="files(id, name, createdTime, modifiedTime, owners)",
                )
                .execute()
            )
            
            return results.get("files", [])
        except Exception as e:
            print(f"Error listing sheets: {str(e)}")
            return []
    
    def get_sheet_metadata(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Get metadata for a specific sheet"""
        try:
            service, _ = self._get_service()
            return service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        except Exception as e:
            print(f"Error getting sheet metadata: {str(e)}")
            return {}


# Initialize Google Sheets service
sheets_service = GoogleSheetsService()


# Event Planning Tools
@mcp.tool()
def event_plan_event(
    event_name: str,
    theme: str = "",
    organization: str = "",
    requirements: str = "",
    google_sheet_id: str = "",
    sheet_range: str = ""
) -> str:
    """
    Plan an event with specified details, optionally reading from Google Sheets
    
    Args:
        event_name: Name of the event to plan
        theme: Theme for the event
        organization: Organization hosting the event
        requirements: Special requirements or considerations
        google_sheet_id: Google Sheets ID to read event data from
        sheet_range: Range in the sheet to read (e.g., 'Sheet1!A1:D10')
    
    Returns:
        Event planning details with optional Google Sheets data
    """
    response = f"Event Coordinator: Planning event '{event_name}'"
    
    if theme:
        response += f" with theme '{theme}'"
    if organization:
        response += f" for {organization}"
    
    response += "."
    
    if requirements:
        response += f" Requirements: {requirements}"
    
    # Read from Google Sheets if provided
    if google_sheet_id and sheet_range:
        try:
            sheet_data = sheets_service.read_sheet(google_sheet_id, sheet_range)
            if sheet_data:
                response += f"\n\n📊 Google Sheets Data Retrieved ({len(sheet_data)} rows):\n"
                for i, row in enumerate(sheet_data):
                    if i == 0:  # Header row
                        response += f"Headers: {' | '.join(row)}\n"
                    else:
                        response += f"Row {i}: {' | '.join(row)}\n"
                    if i >= 10:  # Limit to first 10 rows
                        response += f"... and {len(sheet_data) - 10} more rows\n"
                        break
            else:
                response += f"\n⚠️ No data found in Google Sheet range '{sheet_range}'"
        except Exception as e:
            response += f"\n❌ Error reading Google Sheet: {str(e)}"
    
    return response


@mcp.tool()
def event_get_venue_suggestions(
    event_type: str,
    capacity: int = 50,
    location: str = "",
    budget_range: str = "medium"
) -> str:
    """
    Get venue suggestions for an event
    
    Args:
        event_type: Type of event (conference, party, meeting, etc.)
        capacity: Expected number of attendees
        location: Preferred location or area
        budget_range: Budget range (low, medium, high)
    
    Returns:
        List of venue suggestions
    """
    venues = {
        "conference": ["Convention Center", "Hotel Conference Room", "University Auditorium"],
        "party": ["Community Center", "Restaurant Private Room", "Outdoor Pavilion"],
        "meeting": ["Office Conference Room", "Library Meeting Room", "Coworking Space"],
        "cultural": ["Cultural Center", "Museum Event Space", "Art Gallery"]
    }
    
    suggestions = venues.get(event_type.lower(), ["Community Center", "Hotel Meeting Room"])
    
    response = f"Event Venue Suggestions for {event_type} ({capacity} people):\n\n"
    for i, venue in enumerate(suggestions, 1):
        response += f"{i}. {venue}\n"
        response += f"   Capacity: Suitable for {capacity} attendees\n"
        response += f"   Budget: {budget_range.title()} range\n"
        if location:
            response += f"   Location: Near {location}\n"
        response += "\n"
    
    return response


# Fundraising Tools
@mcp.tool()
def fundraising_create_plan(
    goal: str,
    event_name: str = "",
    budget_target: float = 0
) -> str:
    """
    Create a comprehensive fundraising plan
    
    Args:
        goal: Primary fundraising goal or purpose
        event_name: Associated event name
        budget_target: Target budget amount
    
    Returns:
        Detailed fundraising plan
    """
    response = f"Fundraising Coordinator: Creating plan for '{goal}'"
    
    if event_name:
        response += f" related to {event_name}"
    
    if budget_target > 0:
        response += f"\n\n💰 Budget Target: ${budget_target:,.2f}"
        
        # Suggest fundraising strategies based on budget
        if budget_target < 1000:
            strategies = ["Bake sale", "Small donations", "Ticket sales"]
        elif budget_target < 5000:
            strategies = ["Silent auction", "Corporate sponsorships", "Crowdfunding"]
        else:
            strategies = ["Major donor outreach", "Grant applications", "Premium sponsorships"]
        
        response += "\n\n📋 Recommended Strategies:\n"
        for i, strategy in enumerate(strategies, 1):
            response += f"{i}. {strategy}\n"
    
    response += "\n\n📈 Next Steps:\n"
    response += "1. Identify potential donors and sponsors\n"
    response += "2. Create compelling fundraising materials\n"
    response += "3. Set up donation tracking system\n"
    response += "4. Launch fundraising campaign\n"
    
    return response


@mcp.tool()
def fundraising_calculate_budget(
    venue_cost: float,
    catering_cost: float,
    materials_cost: float = 0,
    marketing_cost: float = 0,
    contingency_percent: float = 10
) -> str:
    """
    Calculate total event budget with breakdown
    
    Args:
        venue_cost: Cost of venue rental
        catering_cost: Cost of food and beverages
        materials_cost: Cost of materials and supplies
        marketing_cost: Cost of marketing and promotion
        contingency_percent: Contingency percentage (default 10%)
    
    Returns:
        Detailed budget breakdown
    """
    subtotal = venue_cost + catering_cost + materials_cost + marketing_cost
    contingency = subtotal * (contingency_percent / 100)
    total = subtotal + contingency
    
    response = "💰 Event Budget Calculation:\n\n"
    response += "📊 Cost Breakdown:\n"
    response += f"  Venue:          ${venue_cost:8,.2f}\n"
    response += f"  Catering:       ${catering_cost:8,.2f}\n"
    response += f"  Materials:      ${materials_cost:8,.2f}\n"
    response += f"  Marketing:      ${marketing_cost:8,.2f}\n"
    response += f"  Subtotal:       ${subtotal:8,.2f}\n"
    response += f"  Contingency:    ${contingency:8,.2f} ({contingency_percent}%)\n"
    response += f"  TOTAL:          ${total:8,.2f}\n\n"
    
    # Fundraising recommendations
    response += "💡 Fundraising Recommendations:\n"
    if total < 1000:
        response += "- Focus on small-scale fundraising activities\n"
        response += "- Seek local business sponsorships\n"
    elif total < 5000:
        response += "- Organize multiple fundraising events\n"
        response += "- Apply for community grants\n"
    else:
        response += "- Seek major corporate sponsorships\n"
        response += "- Apply for large grants\n"
        response += "- Consider premium ticket pricing\n"
    
    return response


# Quality Assurance Tools
@mcp.tool()
def quality_check_deliverable(
    item: str,
    category: str = "",
    criteria: str = ""
) -> str:
    """
    Perform quality assurance checks on deliverables
    
    Args:
        item: Item or deliverable to check
        category: Category of the item (document, event, material, etc.)
        criteria: Specific criteria to check against
    
    Returns:
        Quality assessment report
    """
    response = f"Quality Checker: Reviewing '{item}'"
    
    if category:
        response += f" in category '{category}'"
    
    response += " for quality assurance.\n\n"
    
    # Standard quality checks based on category
    if category.lower() in ["document", "plan", "proposal"]:
        checks = [
            "Content accuracy and completeness",
            "Grammar and spelling",
            "Formatting and presentation",
            "Adherence to guidelines",
            "Clarity and readability"
        ]
    elif category.lower() in ["event", "activity"]:
        checks = [
            "Schedule feasibility",
            "Resource availability",
            "Safety considerations",
            "Accessibility compliance",
            "Backup plans"
        ]
    else:
        checks = [
            "Meets requirements",
            "Quality standards",
            "Functionality",
            "User experience",
            "Risk assessment"
        ]
    
    response += "✅ Quality Checklist:\n"
    for i, check in enumerate(checks, 1):
        response += f"{i}. {check}\n"
    
    if criteria:
        response += f"\n🎯 Specific Criteria: {criteria}\n"
    
    response += "\n📋 Status: Under Review\n"
    response += "⏱️  Estimated completion: Pending detailed review\n"
    
    return response


@mcp.tool()
def quality_create_checklist(
    project_type: str,
    specific_requirements: str = ""
) -> str:
    """
    Create a quality assurance checklist for a project type
    
    Args:
        project_type: Type of project (event, document, software, etc.)
        specific_requirements: Additional specific requirements
    
    Returns:
        Customized quality checklist
    """
    checklists = {
        "event": [
            "Venue confirmed and accessible",
            "Catering arranged with dietary options",
            "Audio/visual equipment tested",
            "Registration system working",
            "Emergency procedures in place",
            "Staff briefed on responsibilities",
            "Backup plans documented"
        ],
        "document": [
            "Content reviewed for accuracy",
            "Grammar and spelling checked",
            "Formatting consistent",
            "All references verified",
            "Version control maintained",
            "Approval signatures obtained",
            "Distribution list confirmed"
        ],
        "marketing": [
            "Target audience defined",
            "Messaging consistent across channels",
            "Visual design approved",
            "Contact information verified",
            "Legal compliance checked",
            "Performance metrics defined",
            "Launch timeline confirmed"
        ]
    }
    
    checklist = checklists.get(project_type.lower(), [
        "Requirements clearly defined",
        "Quality standards established",
        "Testing procedures completed",
        "Stakeholder approval obtained",
        "Documentation updated",
        "Risk assessment completed"
    ])
    
    response = f"📋 Quality Checklist for {project_type.title()} Project:\n\n"
    
    for i, item in enumerate(checklist, 1):
        response += f"☐ {i}. {item}\n"
    
    if specific_requirements:
        response += f"\n🎯 Additional Requirements:\n"
        response += f"☐ {specific_requirements}\n"
    
    response += "\n💡 Instructions:\n"
    response += "- Check off each item as completed\n"
    response += "- Document any issues or exceptions\n"
    response += "- Obtain stakeholder sign-off before proceeding\n"
    
    return response


# Google Sheets Integration Tools
@mcp.tool()
def sheets_read_data(
    spreadsheet_id: str,
    range_name: str
) -> str:
    """
    Read data from a Google Sheets spreadsheet
    
    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        range_name: Range to read (e.g., 'Sheet1!A1:D10')
    
    Returns:
        Formatted data from the spreadsheet
    """
    try:
        values = sheets_service.read_sheet(spreadsheet_id, range_name)
        
        if not values:
            return "❌ No data found in the specified range"
        
        response = f"📊 Retrieved {len(values)} rows from {range_name}\n\n"
        
        for i, row in enumerate(values):
            if i == 0:
                response += "📋 Headers:\n"
                response += "  " + " | ".join(f"{j+1:2d}. {cell}" for j, cell in enumerate(row)) + "\n\n"
                response += "📄 Data:\n"
            else:
                response += f"  Row {i:2d}: " + " | ".join(str(cell) for cell in row) + "\n"
            
            if i >= 15:  # Limit display
                remaining = len(values) - 16
                if remaining > 0:
                    response += f"  ... and {remaining} more rows\n"
                break
        
        return response
        
    except Exception as e:
        return f"❌ Error reading spreadsheet: {str(e)}"


@mcp.tool()
def sheets_list_available() -> str:
    """
    List all available Google Sheets in the user's account
    
    Returns:
        List of available spreadsheets with metadata
    """
    try:
        files = sheets_service.list_sheets()
        
        if not files:
            return "❌ No Google Sheets found in your account"
        
        response = f"📋 Found {len(files)} Google Sheets:\n\n"
        
        for i, file in enumerate(files, 1):
            response += f"{i:2d}. {file['name']}\n"
            response += f"    ID: {file['id']}\n"
            response += f"    URL: https://docs.google.com/spreadsheets/d/{file['id']}\n"
            response += f"    Modified: {file.get('modifiedTime', 'Unknown')}\n"
            
            owners = file.get("owners", [])
            if owners:
                owner_email = owners[0].get("emailAddress", "Unknown")
                response += f"    Owner: {owner_email}\n"
            
            response += "\n"
        
        return response
        
    except Exception as e:
        return f"❌ Error listing sheets: {str(e)}"


@mcp.tool()
def sheets_explore_structure(
    spreadsheet_id: str
) -> str:
    """
    Explore the structure of a Google Sheets spreadsheet
    
    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
    
    Returns:
        Information about worksheets and their structure
    """
    try:
        metadata = sheets_service.get_sheet_metadata(spreadsheet_id)
        
        if not metadata:
            return "❌ Could not retrieve spreadsheet metadata"
        
        sheet_title = metadata.get("properties", {}).get("title", "Unknown")
        response = f"🔍 Exploring: {sheet_title}\n"
        response += f"🌐 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}\n\n"
        
        worksheets = metadata.get("sheets", [])
        response += f"📋 Worksheets ({len(worksheets)}):\n\n"
        
        for i, worksheet in enumerate(worksheets, 1):
            props = worksheet["properties"]
            title = props["title"]
            grid_props = props.get("gridProperties", {})
            rows = grid_props.get("rowCount", "Unknown")
            cols = grid_props.get("columnCount", "Unknown")
            
            response += f"  {i}. {title}\n"
            response += f"     Size: {rows} rows × {cols} columns\n"
            
            # Try to read sample data
            try:
                sample_range = f"{title}!A1:Z5"
                sample_data = sheets_service.read_sheet(spreadsheet_id, sample_range)
                if sample_data:
                    response += f"     Sample data: {len(sample_data)} rows found\n"
                    if len(sample_data) > 0:
                        response += f"     Headers: {sample_data[0]}\n"
                        if len(sample_data) > 1:
                            response += f"     First row: {sample_data[1]}\n"
                else:
                    response += "     No data found\n"
            except Exception:
                response += "     Could not read sample data\n"
            
            response += "\n"
        
        response += "💡 To read data, use sheets_read_data with specific range.\n"
        response += "💡 Example ranges: 'Sheet1!A1:D10', 'Data!A:A', 'Sheet1' (entire sheet)"
        
        return response
        
    except Exception as e:
        return f"❌ Error exploring spreadsheet: {str(e)}"


# Database Tools (Simulated)
@mcp.tool()
def db_query(query: str) -> str:
    """
    Execute a database query (simulated)
    
    Args:
        query: SQL query to execute
    
    Returns:
        Simulated query results
    """
    return f"Database: Executed query '{query}' - Results would appear here in a real implementation."


# File System Tools (Simulated)
@mcp.tool()
def file_read(path: str) -> str:
    """
    Read file contents (simulated)
    
    Args:
        path: File path to read
    
    Returns:
        File contents or error message
    """
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File System: Read file '{path}':\n\n{content}"
        else:
            return f"File System: File '{path}' not found."
    except Exception as e:
        return f"File System: Error reading file '{path}': {str(e)}"


@mcp.tool()
def ask_user_input(question: str) -> str:
    """
    Ask the user for input when needed
    
    Args:
        question: The question to ask the user
    
    Returns:
        User's response or TERMINATE
    """
    print(f"\n🤖 UserAssistant: {question}")
    try:
        response = input("👤 Your response: ").strip()
        if response.lower() in ['exit', 'quit', 'terminate']:
            return "TERMINATE"
        return response
    except (EOFError, KeyboardInterrupt):
        return "TERMINATE"


if __name__ == "__main__":
    # Run the FastMCP server
    import argparse
    import asyncio
    
    # Parse command line arguments to support different transport methods
    parser = argparse.ArgumentParser(description="AutoGen FastMCP Server")
    parser.add_argument("--transport", choices=["stdio", "http", "sse"], default="http", 
                       help="Transport method (default: http for modern API access)")
    parser.add_argument("--port", type=int, default=8000, 
                       help="Port for HTTP/SSE transport")
    parser.add_argument("--host", default="localhost", 
                       help="Host for HTTP/SSE transport")
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        # Run with stdio transport for direct MCP client compatibility
        mcp.run()
    elif args.transport == "sse":
        # Run with SSE transport for streaming capabilities
        print(f"🚀 Starting FastMCP server with SSE on {args.host}:{args.port}")
        asyncio.run(mcp.run_sse_async(host=args.host, port=args.port))
    else:
        # Run with HTTP transport
        print(f"🚀 Starting FastMCP server with HTTP on {args.host}:{args.port}")
        asyncio.run(mcp.run_http_async(host=args.host, port=args.port))