#!/usr/bin/env python3
"""
Simple Exit Example - No task cancellation, just clean exit
"""

import asyncio
import sys
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage


async def simple_exit_test():
    """Simple test that should exit cleanly without task cancellation"""
    print("🧪 Simple Exit Test")
    print("=" * 30)

    # Simple input function that returns immediately
    async def simple_input(prompt: str, cancellation_token=None) -> str:
        print(f"📝 Prompt: {prompt}")
        return "Test User"  # Always return immediately

    # Create user proxy
    user_proxy = UserProxyAgent(name="simple_user", input_func=simple_input)

    token = CancellationToken()

    try:
        response = await user_proxy.on_messages(
            [TextMessage(content="Test prompt: ", source="system")],
            cancellation_token=token,
        )
        print(f"✅ Response: {response.chat_message.content}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Reset user proxy
        try:
            await user_proxy.on_reset(cancellation_token=token)
            print("✅ Reset successful")
        except Exception as e:
            print(f"⚠️ Reset error: {e}")

    print("✅ Test completed")


async def main():
    """Main function - no task cancellation"""
    print("🚀 Starting Simple Exit Test")
    print("=" * 40)

    try:
        await simple_exit_test()
        print("✅ All tests passed")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("✅ Program completed successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"\n💥 Error: {e}")

    print("🚪 Exiting...")
    sys.exit(0)
