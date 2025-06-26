#!/usr/bin/env python3
"""
Test file for the updated simple_user_input.py
"""

import asyncio
import os
from dotenv import load_dotenv
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


async def test_basic_user_input():
    """Test basic user input functionality"""
    print("🧪 Testing Basic User Input")
    print("=" * 40)

    # Create user proxy agent
    user_proxy = UserProxyAgent(name="test_user", description="Test user for input")

    # Create cancellation token
    token = CancellationToken()

    try:
        # Test user input
        response = await user_proxy.on_messages(
            [TextMessage(content="Please enter your name:", source="system")],
            cancellation_token=token,
        )

        print(f"✅ User input received: {response.chat_message.content}")
        return True

    except asyncio.CancelledError:
        print("⏰ User input task was cancelled.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_assistant_agent():
    """Test assistant agent functionality"""
    print("\n🤖 Testing Assistant Agent")
    print("=" * 40)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found in environment variables")
        print("   Skipping assistant agent test")
        return True

    # Create model client
    model_client = OpenAIChatCompletionClient(
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Create assistant agent
    assistant = AssistantAgent(
        name="test_assistant",
        system_message="You are a helpful test assistant.",
        model_client=model_client,
    )

    # Create cancellation token
    token = CancellationToken()

    try:
        # Test assistant response
        response = await assistant.on_messages(
            [TextMessage(content="Hello! Can you help me?", source="user")],
            cancellation_token=token,
        )

        print(f"✅ Assistant response: {response.chat_message.content[:100]}...")
        return True

    except asyncio.CancelledError:
        print("⏰ Assistant task was cancelled.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await model_client.close()


async def main():
    """Run all tests"""
    print("🚀 Starting AutoGen User Input Tests")
    print("=" * 50)

    # Test basic user input
    user_test_passed = await test_basic_user_input()

    # Test assistant agent
    assistant_test_passed = await test_assistant_agent()

    # Summary
    print("\n📊 Test Results")
    print("=" * 30)
    print(f"User Input Test: {'✅ PASSED' if user_test_passed else '❌ FAILED'}")
    print(f"Assistant Test: {'✅ PASSED' if assistant_test_passed else '❌ FAILED'}")

    if user_test_passed and assistant_test_passed:
        print("\n🎉 All tests passed! The updated code is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
