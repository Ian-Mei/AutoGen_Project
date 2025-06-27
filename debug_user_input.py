#!/usr/bin/env python3
"""
Debug User Input - Shows what's keeping the program alive
"""

import asyncio
import sys
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage


def show_running_tasks():
    """Show all currently running tasks"""
    tasks = asyncio.all_tasks()
    print(f"\n📊 Currently running tasks ({len(tasks)}):")
    for i, task in enumerate(tasks):
        print(f"  {i+1}. {task.get_name()} - {task.get_coro()} - Done: {task.done()}")
    return tasks


async def debug_user_input_example():
    """Debug example that shows what's happening"""
    print("🔍 Debug User Input Example")
    print("=" * 50)

    # Show initial tasks
    print("\n🔄 Initial tasks:")
    show_running_tasks()

    async def debug_input(prompt: str, cancellation_token=None) -> str:
        print(f"🔍 Input function called with prompt: {prompt}")
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, prompt),
                timeout=5.0,
            )
            print(f"🔍 Input function returning: {result}")
            return result
        except asyncio.TimeoutError:
            print("🔍 Input function timed out, returning default")
            return "Default User"
        except Exception as e:
            print(f"🔍 Input function error: {e}")
            return "Default User"

    user_proxy = UserProxyAgent(
        name="debug_user", description="Debug user with logging", input_func=debug_input
    )

    token = CancellationToken()

    print("\n🔄 Before creating user proxy:")
    show_running_tasks()

    try:
        print("\n🔄 Before calling on_messages:")
        show_running_tasks()

        response = await user_proxy.on_messages(
            [TextMessage(content="What is your name? (5 seconds): ", source="system")],
            cancellation_token=token,
        )

        print(f"✅ Response: {response.chat_message.content}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("\n🔄 Before reset:")
        show_running_tasks()

        try:
            await user_proxy.on_reset(cancellation_token=token)
            print("✅ User proxy reset successful")
        except Exception as e:
            print(f"⚠️ Reset error: {e}")

        print("\n🔄 After reset:")
        show_running_tasks()


async def main():
    """Main function with extensive debugging"""
    print("🚀 Starting Debug User Input")
    print("=" * 50)

    print("\n🔄 At program start:")
    show_running_tasks()

    try:
        await debug_user_input_example()

    except Exception as e:
        print(f"❌ Error in main: {e}")
    finally:
        print("\n🧹 Final cleanup...")

        # Show all tasks before cleanup
        print("\n🔄 Tasks before cleanup:")
        tasks = show_running_tasks()

        # Cancel all tasks except current
        current_task = asyncio.current_task()
        tasks_to_cancel = []

        for task in tasks:
            if task is not current_task:
                print(f"🔄 Cancelling task: {task.get_name()}")
                task.cancel()
                tasks_to_cancel.append(task)

        if tasks_to_cancel:
            try:
                print("🔄 Waiting for tasks to cancel...")
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")

        # Show tasks after cleanup
        print("\n🔄 Tasks after cleanup:")
        show_running_tasks()

        # Force garbage collection
        import gc

        gc.collect()

        print("✅ Cleanup complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
    finally:
        print("🚪 Exiting program...")
        # Force exit
        sys.exit(0)
