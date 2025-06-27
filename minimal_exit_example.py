#!/usr/bin/env python3
"""
Minimal Exit Example - Tests if the issue is with AutoGen or our code
"""

import asyncio
import sys
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage


async def minimal_test():
    """Minimal test that should exit cleanly"""
    print("🧪 Minimal Exit Test")
    print("=" * 30)

    # Simple input function
    async def simple_input(prompt: str, cancellation_token=None) -> str:
        return "Test User"  # Always return immediately

    # Create user proxy
    user_proxy = UserProxyAgent(name="minimal_user", input_func=simple_input)

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
        except Exception as e:
            print(f"⚠️ Reset error: {e}")

    print("✅ Test completed")


async def main():
    """Main function"""
    print("🚀 Starting Minimal Exit Test")
    print("=" * 40)

    try:
        await minimal_test()
        print("✅ All tests passed")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🧹 Cleanup...")

        # Cancel all remaining tasks
        tasks = [
            task for task in asyncio.all_tasks() if task is not asyncio.current_task()
        ]
        for task in tasks:
            task.cancel()

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        print("✅ Cleanup complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"\n💥 Error: {e}")
    finally:
        print("🚪 Exiting...")
        sys.exit(0)
