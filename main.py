from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
from dotenv import load_dotenv
import os
import json
from mcp_client import mcp_client, get_tools_for_agent

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
        "allowed_domains": [],  # No tools needed for user assistant
        "system_message": prompts["UserAssistant"],
    },
    "event_coordinator": {
        "allowed_domains": ["event.*"],  # Only event-related tools
        "system_message": prompts["EventCoordinator"],
    },
    "fundraising_coordinator": {
        "allowed_domains": ["fundraising.*"],  # Only fundraising-related tools
        "system_message": prompts["FundraisingCoordinator"],
    },
    "quality_checker": {
        "allowed_domains": ["quality.*"],  # Only quality-related tools
        "system_message": prompts["QualityChecker"],
    },
}


async def create_agents_with_dynamic_tools():
    """Create agents with dynamically discovered tools based on allowed domains"""
    agents = {}

    for agent_name, config in agent_configs.items():
        # Get tools for this agent based on allowed domains
        if config["allowed_domains"]:
            tools = await get_tools_for_agent(config["allowed_domains"])
        else:
            tools = []

        # Create agent with dynamic tools
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
    # Create agents with dynamic tool discovery
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
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
