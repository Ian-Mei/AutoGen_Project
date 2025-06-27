#!/usr/bin/env python3
"""
Direct FastMCP Tools Integration for AutoGen
Provides tools directly from FastMCP server without unnecessary client wrapper
"""

import asyncio
import os
from typing import Any, Dict, List, Callable
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Sheets API configuration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


class GoogleSheetsService:
    """Google Sheets service for tools"""
    
    def __init__(self):
        self._service = None
        self._credentials = None
    
    def _get_service(self):
        """Initialize Google Sheets API service"""
        if self._service:
            return self._service, self._credentials
            
        creds = None
        
        if os.path.exists(TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            except Exception as e:
                print(f"⚠️  Error loading credentials: {e}")
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(f"Google Sheets credentials file '{CREDENTIALS_FILE}' not found.")
                
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=8080, open_browser=True)
                
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
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            return result.get("values", [])
        except Exception as e:
            print(f"Error reading Google Sheet: {str(e)}")
            return []


# Initialize shared Google Sheets service
sheets_service = GoogleSheetsService()


# Direct Tool Functions (No MCP wrapper needed!)
async def event_plan_event(
    event_name: str,
    theme: str = "",
    organization: str = "",
    requirements: str = "",
    google_sheet_id: str = "",
    sheet_range: str = ""
) -> str:
    """
    Plan an event with specified details, optionally reading from Google Sheets
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


async def event_get_venue_suggestions(
    event_type: str,
    capacity: int = 50,
    location: str = "",
    budget_range: str = "medium"
) -> str:
    """Get venue suggestions for an event"""
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


async def fundraising_create_plan(
    goal: str,
    event_name: str = "",
    budget_target: float = 0
) -> str:
    """Create a comprehensive fundraising plan"""
    response = f"Fundraising Coordinator: Creating plan for '{goal}'"
    
    if event_name:
        response += f" related to {event_name}"
    
    if budget_target > 0:
        response += f"\n\n💰 Budget Target: ${budget_target:,.2f}"
        
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


async def fundraising_calculate_budget(
    venue_cost: float,
    catering_cost: float,
    materials_cost: float = 0,
    marketing_cost: float = 0,
    contingency_percent: float = 10
) -> str:
    """Calculate total event budget with breakdown"""
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


async def quality_check_deliverable(
    item: str,
    category: str = "",
    criteria: str = ""
) -> str:
    """Perform quality assurance checks on deliverables"""
    response = f"Quality Checker: Reviewing '{item}'"
    
    if category:
        response += f" in category '{category}'"
    
    response += " for quality assurance.\n\n"
    
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


async def quality_create_checklist(
    project_type: str,
    specific_requirements: str = ""
) -> str:
    """Create a quality assurance checklist for a project type"""
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


async def sheets_read_data(
    spreadsheet_id: str,
    range_name: str
) -> str:
    """Read data from a Google Sheets spreadsheet"""
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
            
            if i >= 15:
                remaining = len(values) - 16
                if remaining > 0:
                    response += f"  ... and {remaining} more rows\n"
                break
        
        return response
        
    except Exception as e:
        return f"❌ Error reading spreadsheet: {str(e)}"


async def ask_user_input(question: str) -> str:
    """Ask the user for input when needed"""
    print(f"\n🤖 UserAssistant: {question}")
    try:
        response = input("👤 Your response: ").strip()
        if response.lower() in ['exit', 'quit', 'terminate']:
            return "TERMINATE"
        return response
    except (EOFError, KeyboardInterrupt):
        return "TERMINATE"


# Tool Registry for Domain-Based Access
TOOL_REGISTRY = {
    "event_plan_event": event_plan_event,
    "event_get_venue_suggestions": event_get_venue_suggestions,
    "fundraising_create_plan": fundraising_create_plan,
    "fundraising_calculate_budget": fundraising_calculate_budget,
    "quality_check_deliverable": quality_check_deliverable,
    "quality_create_checklist": quality_create_checklist,
    "sheets_read_data": sheets_read_data,
    "ask_user_input": ask_user_input,
}


async def get_tools_for_agent(allowed_domains: List[str]) -> List[Callable]:
    """Get tools for an agent based on allowed domains - DIRECT ACCESS"""
    tools = []
    
    for tool_name, tool_func in TOOL_REGISTRY.items():
        for domain in allowed_domains:
            if domain.endswith("*"):
                # Pattern matching (e.g., "event.*")
                domain_prefix = domain[:-1]
                if tool_name.startswith(domain_prefix):
                    tools.append(tool_func)
                    break
            elif domain.endswith("_"):
                # Underscore pattern matching (e.g., "event_")
                if tool_name.startswith(domain):
                    tools.append(tool_func)
                    break
            elif tool_name == domain:
                # Exact match
                tools.append(tool_func)
                break
    
    return tools


# Convenience functions for specific agent types
async def get_event_tools() -> List[Callable]:
    """Get event-related tools"""
    return await get_tools_for_agent(["event_"])


async def get_fundraising_tools() -> List[Callable]:
    """Get fundraising-related tools"""
    return await get_tools_for_agent(["fundraising_"])


async def get_quality_tools() -> List[Callable]:
    """Get quality-related tools"""
    return await get_tools_for_agent(["quality_"])


async def get_sheets_tools() -> List[Callable]:
    """Get Google Sheets-related tools"""
    return await get_tools_for_agent(["sheets_"])


async def get_all_tools() -> List[Callable]:
    """Get all available tools"""
    return list(TOOL_REGISTRY.values())