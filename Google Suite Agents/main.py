#!/usr/bin/env python3
"""
AutoGen Multi-Agent Event Planning System

This system creates specialized agents for different aspects of event planning:
- User Assistant: Manages user interactions and coordination
- Sheets Explorer: Handles Google Sheets data retrieval
- Event Coordinator: Plans events and manages logistics
- Fundraising Coordinator: Handles fundraising and budgeting
- Quality Checker: Ensures quality assurance across deliverables

The agents work together using a SelectorGroupChat to coordinate tasks
and share information through FastMCP tools integration.
"""

import asyncio
import json
import os
from typing import List, Dict, Any

# Third-party imports
from dotenv import load_dotenv

# AutoGen imports
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Local imports
from fastmcp import FastMCP

# Load environment variables from current directory or parent directory
if os.path.exists(".env"):
    load_dotenv(".env")
elif os.path.exists("../.env"):
    load_dotenv("../.env")
else:
    # No .env file found, rely on system environment variables
    pass

# Initialize OpenAI client
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Load agent prompts
with open("prompts.json", "r", encoding="utf-8") as pf:
    prompts = json.load(pf)


# Agent definitions with allowed tool domains
agent_configs = {
    "user_assistant": {
        "allowed_domains": ["ask_user_input"],  # Only user input tool
        "system_message": prompts["user_assistant"],
    },
    "sheets_explorer": {
        "allowed_domains": ["sheets_"],  # Only sheets-related tools
        "system_message": prompts["sheets_explorer"],
    },
    "event_coordinator": {
        "allowed_domains": ["event_"],  # Only event-related tools
        "system_message": prompts["event_coordinator"],
    },
    "fundraising_coordinator": {
        "allowed_domains": ["fundraising_"],  # Only fundraising-related tools
        "system_message": prompts["fundraising_coordinator"],
    },
    "quality_checker": {
        "allowed_domains": ["quality_"],  # Only quality-related tools
        "system_message": prompts["quality_checker"],
    },
}


async def get_tools_from_fastmcp_server() -> List[Any]:
    """Import tools directly from FastMCP server module"""
    try:
        # Import the FastMCP server instance from fastmcp_server.py
        import fastmcp_server

        mcp_instance = fastmcp_server.mcp

        # Get tools from the FastMCP instance (returns a dict)
        tools_dict = await mcp_instance.get_tools()

        # Convert to list of callable functions for AutoGen
        tools_list = []
        for tool_name, tool_obj in tools_dict.items():
            # Get the actual function from the FastMCP FunctionTool
            try:
                # Access the actual function via the 'fn' attribute
                actual_func = tool_obj.fn
                tools_list.append(actual_func)
            except Exception as e:
                print(f"⚠️  Could not get function for {tool_name}: {e}")
                continue

        print(f"📋 Retrieved {len(tools_list)} callable tools from FastMCP server")
        for tool in tools_list[:5]:
            print(f"  - {tool.__name__}")
        if len(tools_list) > 5:
            print(f"  ... and {len(tools_list) - 5} more tools")

        return tools_list
    except Exception as e:
        print(f"❌ Error importing FastMCP tools: {e}")
        import traceback

        traceback.print_exc()
        return []


def filter_tools_by_domain(tools: List[Any], allowed_domains: List[str]) -> List[Any]:
    """Filter tools based on allowed domains"""
    if not allowed_domains:
        return []

    filtered_tools = []
    for tool in tools:
        tool_name = getattr(tool, "__name__", "")
        for domain in allowed_domains:
            if domain.endswith("_"):
                # Underscore pattern matching (e.g., "event_")
                if tool_name.startswith(domain):
                    filtered_tools.append(tool)
                    break
            elif domain == tool_name:
                # Exact match
                filtered_tools.append(tool)
                break

    return filtered_tools


async def create_agents_with_dynamic_tools():
    """Create agents with dynamically discovered tools from FastMCP server"""
    agents = {}

    # Get all available tools from the FastMCP server
    all_tools = await get_tools_from_fastmcp_server()

    for agent_name, config in agent_configs.items():
        # Filter tools for this agent based on allowed domains
        if config["allowed_domains"]:
            tools = filter_tools_by_domain(all_tools, config["allowed_domains"])
            print(f"🔧 Agent '{agent_name}' assigned {len(tools)} tools")
        else:
            tools = []

        # Create AssistantAgent for all agents
        agent = AssistantAgent(
            name=agent_name,
            model_client=model_client,
            tools=tools,
            system_message=config["system_message"],
            reflect_on_tool_use=True,
            model_client_stream=True,
        )
        agents[agent_name] = agent

    return agents


async def main() -> None:
    try:
        # Create agents with dynamic tool discovery from FastMCP server
        agents = await create_agents_with_dynamic_tools()

        # Create team with dynamically created agents
        text_mention_termination = TextMentionTermination("TERMINATE")
        max_messages_termination = MaxMessageTermination(max_messages=25)
        termination = text_mention_termination | max_messages_termination

        participants = [agent.name for agent in agents.values()]

        selector_prompt = """
            
            {roles}

            Current conversation context:
            {history}

            Read the above conversation, then select an agent from {participants} to perform the next task.
            Make sure the planner agent has assigned tasks before other agents start working. If the task has been fufilled, tell the next agent to say 'TERMINATE' to end the conversation.
            Only select one agent.
        """
        # Create roles dictionary without MainTask
        roles = {k: v for k, v in prompts.items() if k != "MainTask"}

        team = SelectorGroupChat(
            [
                agents["user_assistant"],
                agents["sheets_explorer"],
                agents["event_coordinator"],
                agents["fundraising_coordinator"],
                agents["quality_checker"],
            ],
            model_client=model_client,
            termination_condition=termination,
            selector_prompt=selector_prompt,
            allow_repeated_speaker=True,
        )

        # Show streaming output in the console
        response = await Console(
            team.run_stream(
                task=prompts["MainTask"],
            )
        )

        # Prepare formatted output
        lines = []
        # If response has a 'messages' attribute, use it; otherwise, treat as a single message
        messages = getattr(response, "messages", [response])
        for msg in messages:
            msg_type = getattr(msg, "type", type(msg).__name__)
            source = getattr(msg, "source", "unknown")
            content = getattr(msg, "content", str(msg))
            lines.append(f"---------- {msg_type} ({source}) ----------\n{content}\n\n")

        with open("output.txt", "w", encoding="utf-8") as f:
            f.writelines(lines)

    finally:
        # Cleanup resources
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
