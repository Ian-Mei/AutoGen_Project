#!/usr/bin/env python3
"""
Default Response Example - Different strategies for handling timeouts
"""

import asyncio
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage


class SmartInputHandler:
    """Smart input handler with different default response strategies"""

    def __init__(self, timeout_seconds: float = 10.0):
        self.timeout_seconds = timeout_seconds
        self.default_responses = {
            "name": "Anonymous User",
            "color": "Blue",
            "age": "25",
            "preference": "No preference",
            "general": "Default response",
        }

    async def get_input_with_default(self, prompt: str, cancellation_token=None) -> str:
        """Get input with default response on timeout"""
        try:
            return await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, prompt),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError:
            print(
                f"⏰ Timeout after {self.timeout_seconds} seconds! Using default response."
            )
            return self._get_smart_default(prompt)
        except Exception as e:
            print(f"⚠️ Input error: {e}. Using default response.")
            return self._get_smart_default(prompt)

    def _get_smart_default(self, prompt: str) -> str:
        """Get a smart default response based on the prompt"""
        prompt_lower = prompt.lower()

        if "name" in prompt_lower:
            return self.default_responses["name"]
        elif "color" in prompt_lower:
            return self.default_responses["color"]
        elif "age" in prompt_lower:
            return self.default_responses["age"]
        elif "preference" in prompt_lower or "like" in prompt_lower:
            return self.default_responses["preference"]
        else:
            return self.default_responses["general"]


async def basic_default_example():
    """Basic example with simple default response"""
    print("🔄 Basic Default Response Example")
    print("=" * 50)

    async def simple_input(prompt: str, cancellation_token=None) -> str:
        try:
            return await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, prompt),
                timeout=5.0,
            )
        except asyncio.TimeoutError:
            print("⏰ Timeout! Using default response.")
            return "Default User"

    user_proxy = UserProxyAgent(
        name="basic_user",
        description="User with basic default response",
        input_func=simple_input,
    )

    token = CancellationToken()

    try:
        response = await user_proxy.on_messages(
            [TextMessage(content="What is your name? (5 seconds): ", source="system")],
            cancellation_token=token,
        )
        print(f"✅ Response: {response.chat_message.content}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await user_proxy.on_reset(cancellation_token=token)


async def smart_default_example():
    """Example with smart default responses"""
    print("\n🧠 Smart Default Response Example")
    print("=" * 50)

    input_handler = SmartInputHandler(timeout_seconds=3.0)

    user_proxy = UserProxyAgent(
        name="smart_user",
        description="User with smart default responses",
        input_func=input_handler.get_input_with_default,
    )

    token = CancellationToken()

    # Test different types of prompts
    prompts = [
        "What is your name? (3 seconds): ",
        "What's your favorite color? (3 seconds): ",
        "How old are you? (3 seconds): ",
        "Do you prefer cats or dogs? (3 seconds): ",
        "Tell me something random: (3 seconds): ",
    ]

    try:
        for i, prompt in enumerate(prompts, 1):
            print(f"\n{i}. Testing prompt: {prompt.strip()}")

            response = await user_proxy.on_messages(
                [TextMessage(content=prompt, source="system")], cancellation_token=token
            )
            print(f"   Response: {response.chat_message.content}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await user_proxy.on_reset(cancellation_token=token)


async def configurable_default_example():
    """Example with configurable default responses"""
    print("\n⚙️ Configurable Default Response Example")
    print("=" * 50)

    # Define custom default responses
    custom_defaults = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "555-1234",
        "address": "123 Main St",
        "general": "No response provided",
    }

    async def configurable_input(prompt: str, cancellation_token=None) -> str:
        try:
            return await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, prompt),
                timeout=4.0,
            )
        except asyncio.TimeoutError:
            print("⏰ Timeout! Using configured default.")
            # Determine which default to use based on prompt
            prompt_lower = prompt.lower()
            if "name" in prompt_lower:
                return custom_defaults["name"]
            elif "email" in prompt_lower:
                return custom_defaults["email"]
            elif "phone" in prompt_lower:
                return custom_defaults["phone"]
            elif "address" in prompt_lower:
                return custom_defaults["address"]
            else:
                return custom_defaults["general"]

    user_proxy = UserProxyAgent(
        name="config_user",
        description="User with configurable defaults",
        input_func=configurable_input,
    )

    token = CancellationToken()

    try:
        response = await user_proxy.on_messages(
            [TextMessage(content="What is your name? (4 seconds): ", source="system")],
            cancellation_token=token,
        )
        print(f"✅ Response: {response.chat_message.content}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await user_proxy.on_reset(cancellation_token=token)


async def main():
    """Main function"""
    print("🚀 Starting Default Response Examples")
    print("=" * 50)

    try:
        await basic_default_example()
        await smart_default_example()
        await configurable_default_example()

    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        print("\n✅ Program completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
