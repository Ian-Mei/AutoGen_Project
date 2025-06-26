#!/usr/bin/env python3
"""
Simple AutoGen User Input Example
Basic demonstration of how agents can get user input
"""

import asyncio
from typing import Any
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from dotenv import load_dotenv

load_dotenv()


async def simple_user_input_example():
    """Simple example of AutoGen user input"""
    print("🤖 Simple AutoGen User Input Example")
    print("=" * 50)

    # Create model client
    model_client = OpenAIChatCompletionClient(
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Create a simple assistant agent
    assistant = AssistantAgent(
        name="assistant",
        system_message="I'm a helpful assistant. I can ask you questions when I need more information.",
        model_client=model_client,
    )

    # Create a user proxy agent with default input function
    user_proxy = UserProxyAgent(
        name="user_proxy", description="A human user who can provide input"
    )

    # Create cancellation token
    token = CancellationToken()

    try:
        # Start a conversation by sending a message to the assistant
        assistant_response = await assistant.on_messages(
            [
                TextMessage(
                    content="I need help planning a birthday party. Can you help me?",
                    source="user",
                )
            ],
            cancellation_token=token,
        )

        print(f"Assistant: {assistant_response.chat_message.content}")

        # Now get user input through the user proxy
        user_response = await user_proxy.on_messages(
            [
                TextMessage(
                    content="Please provide your preferences for the birthday party:",
                    source="assistant",
                )
            ],
            cancellation_token=token,
        )

        print(f"User: {user_response.chat_message.content}")

    except asyncio.CancelledError:
        print("⏰ Task was cancelled.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
    finally:
        await model_client.close()


async def conditional_user_input_example():
    """Example where the agent decides when to ask for input"""
    print("\n🎯 Conditional User Input Example")
    print("=" * 50)

    # Create model client
    model_client = OpenAIChatCompletionClient(
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Create an assistant that can decide when to ask for input
    assistant = AssistantAgent(
        name="smart_assistant",
        system_message="""You are a smart assistant. You can:
        1. Answer simple questions directly
        2. Ask for more information when needed
        3. Provide suggestions and ask for preferences
        
        When you need specific information, ask clearly for it.""",
        model_client=model_client,
    )

    user_proxy = UserProxyAgent(
        name="user_proxy", description="A human user who can provide input"
    )

    token = CancellationToken()

    try:
        # Start conversation about website creation
        assistant_response = await assistant.on_messages(
            [
                TextMessage(
                    content="I want to create a website for my business.", source="user"
                )
            ],
            cancellation_token=token,
        )

        print(f"Assistant: {assistant_response.chat_message.content}")

        # Get user input for website details
        user_response = await user_proxy.on_messages(
            [
                TextMessage(
                    content="What type of business do you have and what features do you need?",
                    source="assistant",
                )
            ],
            cancellation_token=token,
        )

        print(f"User: {user_response.chat_message.content}")

    except asyncio.CancelledError:
        print("⏰ Task was cancelled.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
    finally:
        await model_client.close()


async def cancellable_user_input_example():
    """Example with timeout and default response"""
    print("\n⏰ Cancellable User Input Example")
    print("=" * 50)

    # Custom input function that returns default response after timeout
    async def input_with_default(prompt: str, cancellation_token=None) -> str:
        try:
            # Use asyncio.wait_for to timeout the input
            return await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, prompt),
                timeout=10.0,  # 10 second timeout
            )
        except asyncio.TimeoutError:
            print("⏰ Timeout reached! Using default response.")
            return "Default User"  # Default response
        except Exception as e:
            print(f"⚠️ Input error: {e}. Using default response.")
            return "Default User"  # Default response on any error

    user_proxy = UserProxyAgent(
        name="user_proxy",
        description="A human user with timeout and default response",
        input_func=input_with_default,
    )

    token = CancellationToken()

    try:
        response = await user_proxy.on_messages(
            [
                TextMessage(
                    content="What is your name? (You have 10 seconds to respond): ",
                    source="system",
                )
            ],
            cancellation_token=token,
        )

        assert isinstance(response.chat_message, TextMessage)
        print(f"Response received: {response.chat_message.content}")

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
    except BaseException as e:
        print(f"💥 Unexpected error: {e}")
    finally:
        # Reset the user proxy agent to clear any internal state
        try:
            await user_proxy.on_reset(cancellation_token=token)
        except Exception as e:
            print(f"⚠️ Warning: Could not reset user proxy: {e}")

        # Force garbage collection to clean up any remaining references
        import gc

        gc.collect()


def show_user_input_modes():
    """Show different user input modes"""
    print("\n📋 AutoGen User Input Modes")
    print("=" * 40)

    modes = {
        "Default input_func": "Uses built-in input() function",
        "Custom input_func": "Provide your own input function",
        "Async input_func": "Provide async input function for web/UI integration",
        "Cancellable": "Use CancellationToken for timeout handling",
    }

    for mode, description in modes.items():
        print(f"• {mode}: {description}")

    print("\n💡 Key Features:")
    print("• UserProxyAgent represents human users")
    print("• Use CancellationToken for timeout and cancellation")
    print("• Can integrate with web frameworks (FastAPI, ChainLit)")
    print("• Supports both sync and async input functions")


async def main():
    """Main function"""
    print("Choose an example:")
    print("1. Simple user input")
    print("2. Conditional user input")
    print("3. Cancellable user input (with timeout)")
    print("4. Show user input modes")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        await simple_user_input_example()
    elif choice == "2":
        await conditional_user_input_example()
    elif choice == "3":
        await cancellable_user_input_example()
    elif choice == "4":
        show_user_input_modes()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
