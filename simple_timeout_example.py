#!/usr/bin/env python3
"""
Simple Timeout Example - Using asyncio.wait_for for reliable timeout handling
"""

import asyncio
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage


async def simple_timeout_example():
    """Simple example using asyncio.wait_for for timeout"""
    print("⏰ Simple Timeout Example")
    print("=" * 50)

    user_proxy = UserProxyAgent(
        name="simple_user", description="Simple user with timeout"
    )

    token = CancellationToken()

    try:
        # Use asyncio.wait_for for automatic timeout handling
        response = await asyncio.wait_for(
            user_proxy.on_messages(
                [
                    TextMessage(
                        content="What is your name? (You have 5 seconds): ",
                        source="system",
                    )
                ],
                cancellation_token=token,
            ),
            timeout=5.0,  # 5 second timeout
        )

        print(f"✅ Success! Your name is: {response.chat_message.content}")

    except asyncio.TimeoutError:
        print("⏰ Timeout reached! The operation took too long.")
    except asyncio.CancelledError:
        print("⏰ Operation was cancelled.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
    finally:
        # Reset the user proxy
        try:
            await user_proxy.on_reset(cancellation_token=token)
        except Exception as e:
            print(f"⚠️ Warning: Could not reset user proxy: {e}")


async def multiple_timeout_example():
    """Example with multiple timeout scenarios"""
    print("\n🔄 Multiple Timeout Scenarios")
    print("=" * 50)

    user_proxy = UserProxyAgent(
        name="multi_user", description="User for multiple timeout tests"
    )

    token = CancellationToken()

    # Test 1: Quick timeout (should timeout)
    print("\n1️⃣ Quick timeout test (2 seconds)")
    try:
        response = await asyncio.wait_for(
            user_proxy.on_messages(
                [
                    TextMessage(
                        content="Quick! Enter your name (2 seconds): ", source="system"
                    )
                ],
                cancellation_token=token,
            ),
            timeout=2.0,
        )
        print(f"✅ Success: {response.chat_message.content}")
    except asyncio.TimeoutError:
        print("⏰ Quick timeout test timed out (expected)")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Longer timeout (might succeed if user responds quickly)
    print("\n2️⃣ Longer timeout test (8 seconds)")
    try:
        response = await asyncio.wait_for(
            user_proxy.on_messages(
                [
                    TextMessage(
                        content="You have 8 seconds to enter your favorite color: ",
                        source="system",
                    )
                ],
                cancellation_token=token,
            ),
            timeout=8.0,
        )
        print(f"✅ Success: {response.chat_message.content}")
    except asyncio.TimeoutError:
        print("⏰ Longer timeout test timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Reset the user proxy
    try:
        await user_proxy.on_reset(cancellation_token=token)
    except Exception as e:
        print(f"⚠️ Warning: Could not reset user proxy: {e}")


async def main():
    """Main function"""
    print("🚀 Starting Simple Timeout Examples")
    print("=" * 50)

    try:
        await simple_timeout_example()
        await multiple_timeout_example()

    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        print("\n✅ Program completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
