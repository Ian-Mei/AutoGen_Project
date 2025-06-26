#!/usr/bin/env python3
"""
Robust User Input Example - Properly handles cancellation and cleanup
"""

import asyncio
import signal
import sys
from typing import Optional
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage


class CancellableInput:
    """A cancellable input function that can be interrupted"""

    def __init__(self):
        self._input_future: Optional[asyncio.Future] = None
        self._loop = asyncio.get_event_loop()

    async def get_input(
        self, prompt: str, cancellation_token: CancellationToken
    ) -> str:
        """Get user input with cancellation support"""
        if cancellation_token.is_cancelled():
            raise asyncio.CancelledError()

        # Create a future for the input
        self._input_future = self._loop.create_future()

        try:
            # Run input in a thread to avoid blocking
            def input_thread():
                try:
                    user_input = input(prompt)
                    if not self._input_future.done():
                        self._input_future.set_result(user_input)
                except (EOFError, KeyboardInterrupt):
                    if not self._input_future.done():
                        self._input_future.set_exception(asyncio.CancelledError())

            # Start input thread
            await self._loop.run_in_executor(None, input_thread)

            # Wait for input or cancellation
            return await asyncio.wait_for(self._input_future, timeout=None)

        except asyncio.CancelledError:
            # Cancel the input future if it's still pending
            if self._input_future and not self._input_future.done():
                self._input_future.cancel()
            raise
        finally:
            self._input_future = None

    def cancel_input(self):
        """Cancel the current input operation"""
        if self._input_future and not self._input_future.done():
            self._input_future.cancel()


async def robust_user_input_example():
    """Robust example with proper cancellation and cleanup"""
    print("🛡️ Robust User Input Example")
    print("=" * 50)

    # Create cancellable input handler
    input_handler = CancellableInput()

    # Create user proxy with custom input function
    user_proxy = UserProxyAgent(
        name="robust_user",
        description="A robust user with cancellable input",
        input_func=input_handler.get_input,
    )

    token = CancellationToken()
    timeout_task = None
    agent_task = None

    async def timeout(delay: float):
        await asyncio.sleep(delay)
        print(f"\n⏰ Timeout after {delay} seconds!")
        token.cancel()
        input_handler.cancel_input()

    try:
        # Set up timeout task
        timeout_task = asyncio.create_task(timeout(10))

        # Request user input
        agent_task = asyncio.create_task(
            user_proxy.on_messages(
                [
                    TextMessage(
                        content="What is your name? (You have 10 seconds to respond): ",
                        source="system",
                    )
                ],
                cancellation_token=token,
            )
        )

        response = await agent_task
        print(f"\n✅ Success! Your name is: {response.chat_message.content}")

    except asyncio.CancelledError:
        print("\n⏰ Operation was cancelled due to timeout")
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
    finally:
        # Clean up tasks
        if timeout_task and not timeout_task.done():
            timeout_task.cancel()
            try:
                await timeout_task
            except asyncio.CancelledError:
                pass

        if agent_task and not agent_task.done():
            agent_task.cancel()
            try:
                await agent_task
            except asyncio.CancelledError:
                pass

        # Reset the user proxy
        try:
            await user_proxy.on_reset(cancellation_token=token)
        except Exception as e:
            print(f"⚠️ Warning: Could not reset user proxy: {e}")

        # Force cleanup
        import gc

        gc.collect()


async def signal_handler_example():
    """Example with signal handling for graceful shutdown"""
    print("\n🔄 Signal Handler Example")
    print("=" * 50)

    input_handler = CancellableInput()

    user_proxy = UserProxyAgent(
        name="signal_user",
        description="User with signal handling",
        input_func=input_handler.get_input,
    )

    token = CancellationToken()

    # Set up signal handlers
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, cancelling operation...")
        token.cancel()
        input_handler.cancel_input()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        response = await user_proxy.on_messages(
            [
                TextMessage(
                    content="Enter something (press Ctrl+C to cancel): ",
                    source="system",
                )
            ],
            cancellation_token=token,
        )
        print(f"\n✅ Success! You entered: {response.chat_message.content}")

    except asyncio.CancelledError:
        print("\n⏰ Operation was cancelled by signal")
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
    finally:
        # Reset the user proxy
        try:
            await user_proxy.on_reset(cancellation_token=token)
        except Exception as e:
            print(f"⚠️ Warning: Could not reset user proxy: {e}")


async def main():
    """Main function with proper cleanup"""
    print("🚀 Starting Robust User Input Examples")
    print("=" * 50)

    try:
        await robust_user_input_example()
        await signal_handler_example()

    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        print("\n🧹 Cleaning up and exiting...")
        # Ensure all pending tasks are cancelled
        tasks = [
            task for task in asyncio.all_tasks() if task is not asyncio.current_task()
        ]
        for task in tasks:
            task.cancel()

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        print("✅ Cleanup complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Program terminated by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
