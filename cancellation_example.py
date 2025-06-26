#!/usr/bin/env python3
"""
Cancellation Example - Demonstrating proper error handling
"""

import asyncio
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage


async def demonstrate_cancellation():
    """Demonstrate different cancellation scenarios"""
    print("🔄 Cancellation Demonstration")
    print("=" * 50)

    user_proxy = UserProxyAgent(
        name="demo_user", description="Demo user for cancellation testing"
    )

    # Scenario 1: Quick response (should succeed)
    print("\n1️⃣ Quick Response Test (2 seconds)")
    print("-" * 30)

    token1 = CancellationToken()
    timeout_task1 = None
    user_task1 = None

    async def quick_timeout():
        await asyncio.sleep(2)
        token1.cancel()

    try:
        # Start timeout task
        timeout_task1 = asyncio.create_task(quick_timeout())

        # Start user input task
        user_task1 = asyncio.create_task(
            user_proxy.on_messages(
                [
                    TextMessage(
                        content="Quick! Enter your name (you have 2 seconds):",
                        source="system",
                    )
                ],
                cancellation_token=token1,
            )
        )

        response = await user_task1
        print(f"✅ Success: {response.chat_message.content}")

    except asyncio.CancelledError:
        print("⏰ Quick response test timed out (expected)")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Clean up tasks
        if timeout_task1 and not timeout_task1.done():
            timeout_task1.cancel()
            try:
                await timeout_task1
            except asyncio.CancelledError:
                pass

        if user_task1 and not user_task1.done():
            user_task1.cancel()
            try:
                await user_task1
            except asyncio.CancelledError:
                pass

    # Scenario 2: Longer timeout (should succeed if user responds quickly)
    print("\n2️⃣ Normal Response Test (10 seconds)")
    print("-" * 30)

    token2 = CancellationToken()
    timeout_task2 = None
    user_task2 = None

    async def normal_timeout():
        await asyncio.sleep(10)
        token2.cancel()

    try:
        # Start timeout task
        timeout_task2 = asyncio.create_task(normal_timeout())

        # Start user input task
        user_task2 = asyncio.create_task(
            user_proxy.on_messages(
                [
                    TextMessage(
                        content="You have 10 seconds to enter your favorite color:",
                        source="system",
                    )
                ],
                cancellation_token=token2,
            )
        )

        response = await user_task2
        print(f"✅ Success: {response.chat_message.content}")

    except asyncio.CancelledError:
        print("⏰ Normal response test timed out")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Clean up tasks
        if timeout_task2 and not timeout_task2.done():
            timeout_task2.cancel()
            try:
                await timeout_task2
            except asyncio.CancelledError:
                pass

        if user_task2 and not user_task2.done():
            user_task2.cancel()
            try:
                await user_task2
            except asyncio.CancelledError:
                pass

    # Scenario 3: Immediate cancellation
    print("\n3️⃣ Immediate Cancellation Test")
    print("-" * 30)

    token3 = CancellationToken()

    try:
        # Cancel immediately
        token3.cancel()

        response = await user_proxy.on_messages(
            [
                TextMessage(
                    content="This should be cancelled immediately:", source="system"
                )
            ],
            cancellation_token=token3,
        )

        print(f"❌ This should not print: {response.chat_message.content}")

    except asyncio.CancelledError:
        print("✅ Immediate cancellation worked correctly")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def main():
    """Main function"""
    print("🚀 Starting Cancellation Examples")
    print("=" * 50)

    await demonstrate_cancellation()

    print("\n📋 Summary")
    print("=" * 20)
    print("• asyncio.CancelledError is thrown when tasks are cancelled")
    print("• Always catch CancelledError specifically for timeout handling")
    print("• Use CancellationToken.cancel() to trigger cancellation")
    print("• Proper error handling prevents unexpected crashes")


if __name__ == "__main__":
    asyncio.run(main())
