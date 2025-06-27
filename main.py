from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
from dotenv import load_dotenv
import os
import json
import subprocess
import time
from typing import List, Dict, Any
from fastmcp import FastMCP

load_dotenv()
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)

with open("prompts.json", "r", encoding="utf-8") as pf:
    prompts = json.load(pf)


# Agent definitions with allowed tool domains
agent_configs = {
    "user_assistant": {
        "allowed_domains": ["ask_user_input"],  # Only user input tool
        "system_message": prompts["UserAssistant"],
    },
    "event_coordinator": {
        "allowed_domains": ["event_"],  # Only event-related tools
        "system_message": prompts["EventCoordinator"],
    },
    "fundraising_coordinator": {
        "allowed_domains": ["fundraising_"],  # Only fundraising-related tools
        "system_message": prompts["FundraisingCoordinator"],
    },
    "quality_checker": {
        "allowed_domains": ["quality_"],  # Only quality-related tools
        "system_message": prompts["QualityChecker"],
    },
}


async def get_tools_from_fastmcp_server() -> List[Dict[str, Any]]:
    """Import tools directly from FastMCP server module"""
    try:
        # Import the FastMCP server instance from fastmcp_server.py
        import fastmcp_server
        mcp_instance = fastmcp_server.mcp
        
        # Get tools from the FastMCP instance
        tools = mcp_instance.get_tools()
        print(f"📋 Retrieved {len(tools)} tools from FastMCP server")
        return tools
    except Exception as e:
        print(f"❌ Error importing FastMCP tools: {e}")
        return []


def filter_tools_by_domain(tools: List[Dict], allowed_domains: List[str]) -> List[Dict]:
    """Filter tools based on allowed domains"""
    if not allowed_domains:
        return []
    
    filtered_tools = []
    for tool in tools:
        tool_name = tool.get("function", {}).get("name", "")
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


async def simple_user_input(prompt: str, cancellation_token=None) -> str:
    """Simple input without timeout - cleaner for main system"""
    print(f"\n{prompt}")
    try:
        return input("👤 Your response: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "TERMINATE"


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
        termination = TextMentionTermination("TERMINATE")
        team = SelectorGroupChat(
            [
                agents["user_assistant"],
                agents["event_coordinator"],
                agents["fundraising_coordinator"],
                agents["quality_checker"],
            ],
            termination_condition=termination,
            max_turns=25,
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
