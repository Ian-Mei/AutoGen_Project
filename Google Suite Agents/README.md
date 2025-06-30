# Google Suite Agents

An intelligent multi-agent system built with AutoGen that specializes in Google Sheets integration and event planning coordination.

## Overview

This project implements a collaborative AI system using specialized agents that work together to handle various aspects of event planning and data management through Google Sheets integration.

## Agents

- **User Assistant**: Manages user interactions and coordinates between agents
- **Sheets Explorer**: Handles Google Sheets data retrieval and analysis
- **Event Coordinator**: Plans events and manages logistics
- **Fundraising Coordinator**: Handles fundraising activities and budget calculations
- **Quality Checker**: Ensures quality assurance across all deliverables

## Key Features

- **Google Sheets Integration**: Seamless reading and analysis of Google Sheets data
- **FastMCP Framework**: Uses FastMCP for tool discovery and integration
- **Timeout-Safe User Input**: Robust user interaction with timeout handling
- **Multi-Agent Coordination**: Agents collaborate using SelectorGroupChat
- **Event Planning Tools**: Comprehensive event planning and management capabilities

## Files

- `main.py` - Main AutoGen application with multi-agent coordination
- `fastmcp_server.py` - FastMCP server with specialized tools
- `simple_user_input.py` - User input utilities with timeout handling
- `prompts.json` - Agent system messages and prompts
- `setup_google_sheets.py` - Google Sheets API setup and configuration
- `google_sheets_examples.md` - Documentation and examples
- `token.json` - Google Sheets authentication token (auto-generated)
- `tests/` - Test suite for the application
- `run_tests.py` & `test_runner.py` - Test execution scripts

## Setup

1. **Install dependencies**: `pip install -r ../requirements.txt`
2. **Set up Google Sheets API credentials** (follow `setup_google_sheets.py`)
3. **Configure your `.env` file** with OpenAI API key in the parent directory
4. **Run the application**: `python main.py`

## Usage

The system automatically coordinates between agents based on the task at hand. Simply run the main application and describe what you need - the agents will collaborate to fulfill your request using Google Sheets data when necessary. 