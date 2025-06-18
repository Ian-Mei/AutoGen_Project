from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
from dotenv import load_dotenv
import os
import json

load_dotenv()
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)

with open("prompts.json", "r", encoding="utf-8") as pf:
    prompts = json.load(pf)


# Specialized agents
async def event_task(event: str) -> str:
    return f"Event Coordinator: Planning event '{event}'."


async def fundraising_task(goal: str) -> str:
    return f"Fundraising Coordinator: Organizing fundraising for '{goal}'."


async def quality_check_task(item: str) -> str:
    return f"Quality Checker: Reviewing '{item}' for quality assurance."


# Define agents
user_assistant = AssistantAgent(
    name="user_assistant",
    model_client=model_client,
    system_message=prompts["UserAssistant"],
    reflect_on_tool_use=True,
    model_client_stream=True,
)
event_coordinator = AssistantAgent(
    name="event_coordinator",
    model_client=model_client,
    tools=[event_task],
    system_message=prompts["EventCoordinator"],
    reflect_on_tool_use=True,
    model_client_stream=True,
)
fundraising_coordinator = AssistantAgent(
    name="fundraising_coordinator",
    model_client=model_client,
    tools=[fundraising_task],
    system_message=prompts["FundraisingCoordinator"],
    reflect_on_tool_use=True,
    model_client_stream=True,
)
quality_checker = AssistantAgent(
    name="quality_checker",
    model_client=model_client,
    tools=[quality_check_task],
    system_message=prompts["QualityChecker"],
    reflect_on_tool_use=True,
    model_client_stream=True,
)

# Group chat functionality is commented out due to missing GroupChat class in your environment.
# If you update your AutoGen package and GroupChat becomes available, uncomment and use the following:
termination = TextMentionTermination("TERMINATE")
team = RoundRobinGroupChat(
    [user_assistant, event_coordinator, fundraising_coordinator, quality_checker],
    termination_condition=termination,
    max_turns=25,
)


async def main() -> None:
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
