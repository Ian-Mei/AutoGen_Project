#!/usr/bin/env python3
"""
Improved Cancellation Example - Using task utilities for proper cleanup
"""

import asyncio
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage
from task_utils import TaskManager, cleanup_task, run_with_cancellation


async def improved_cancellation_demo():
    """Demonstrate improved cancellation with proper task cleanup"""
    print("🔄 Improved Cancellation Demo")
    print("=" * 50)

    user_proxy = UserProxyAgent(
        name="demo_user", description="Demo user for improved cancellation testing"
    )

    # Using TaskManager context manager for automatic cleanup
    async with TaskManager() as task_mgr:
        print("\n1️⃣ TaskManager Demo (5 seconds)")
        print("-" * 30)

        token = CancellationToken()

        # Create timeout task
        async def timeout_task():
            await asyncio.sleep(5)
            token.cancel()

        timeout_coro = asyncio.create_task(timeout_task())
        task_mgr.add_task(timeout_coro, "timeout")

        # Create user input task
        user_coro = asyncio.create_task(
            user_proxy.on_messages(
                [
                    TextMessage(
                        content="You have 5 seconds to enter your name:",
                        source="system",
                    )
                ],
                cancellation_token=token,
            )
        )
        task_mgr.add_task(user_coro, "user_input")

        try:
            response = await user_coro
            print(f"✅ Success: {response.chat_message.content}")
        except asyncio.CancelledError:
            print("⏰ Task was cancelled (expected)")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        # TaskManager automatically cleans up all tasks when exiting context

    # Manual cleanup example
    print("\n2️⃣ Manual Cleanup Demo (3 seconds)")
    print("-" * 30)

    token2 = CancellationToken()
    timeout_task2 = None
    user_task2 = None

    async def quick_timeout():
        await asyncio.sleep(3)
        token2.cancel()

    try:
        timeout_task2 = asyncio.create_task(quick_timeout())
        user_task2 = asyncio.create_task(
            user_proxy.on_messages(
                [
                    TextMessage(
                        content="Quick! Enter your favorite color (3 seconds):",
                        source="system",
                    )
                ],
                cancellation_token=token2,
            )
        )

        response = await user_task2
        print(f"✅ Success: {response.chat_message.content}")

    except asyncio.CancelledError:
        print("⏰ Task was cancelled (expected)")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Manual cleanup
        await cleanup_task(timeout_task2, "timeout_task")
        await cleanup_task(user_task2, "user_task")

    # Using run_with_cancellation utility
    print("\n3️⃣ Utility Function Demo (4 seconds)")
    print("-" * 30)

    token3 = CancellationToken()

    try:
        response = await run_with_cancellation(
            user_proxy.on_messages(
                [TextMessage(content="Enter your age (4 seconds):", source="system")],
                cancellation_token=token3,
            ),
            token3,
            timeout_seconds=4,
        )

        if response:
            print(f"✅ Success: {response.chat_message.content}")
        else:
            print("⏰ Operation timed out")

    except asyncio.CancelledError:
        print("⏰ Operation was cancelled")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def main():
    """Main function"""
    print("🚀 Starting Improved Cancellation Examples")
    print("=" * 50)

    await improved_cancellation_demo()

    print("\n📋 Summary")
    print("=" * 20)
    print("• TaskManager provides automatic cleanup")
    print("• cleanup_task() for manual task cleanup")
    print("• run_with_cancellation() for simplified timeout handling")
    print("• All tasks are properly cancelled and cleaned up")
    print("• Program exits cleanly after timeouts")


if __name__ == "__main__":
    asyncio.run(main())
