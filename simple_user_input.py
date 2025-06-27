#!/usr/bin/env python3
"""
AutoGen User Input with Timeout - Complete Example
Handles user input, timeouts, and AutoGen integration cleanly
"""

import asyncio
import sys
import os
from typing import Optional
from dotenv import load_dotenv

from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


async def safe_input_with_timeout(prompt: str, timeout: float = 10.0, default: str = "No response") -> str:
    """
    Safe input function that handles EOF and timeout gracefully
    
    Args:
        prompt: The prompt to show the user
        timeout: Timeout in seconds (default: 10.0)
        default: Default response if timeout/error occurs
    
    Returns:
        User input or default response
    """
    
    print(f"\n{prompt}")
    
    # Check if we're in an interactive environment
    if not sys.stdin.isatty():
        print(f"⚠️  Non-interactive environment - using default: '{default}'")
        return default
    
    print(f"⏰ You have {timeout} seconds to respond...")
    
    # Create a task for input
    input_task = None
    
    try:
        def get_input():
            try:
                return input("👤 Your response: ")
            except EOFError:
                raise EOFError("No input stream available")
        
        # Create the input task
        input_task = asyncio.get_event_loop().run_in_executor(None, get_input)
        
        result = await asyncio.wait_for(input_task, timeout=timeout)
        
        if result.strip():
            print(f"✅ Input received: '{result.strip()}'")
            return result.strip()
        else:
            print(f"⚠️  Empty input - using default: '{default}'")
            return default
            
    except asyncio.TimeoutError:
        print(f"⏰ Timeout ({timeout}s) - using default: '{default}'")
        # Cancel the input task to prevent hanging
        if input_task and not input_task.done():
            input_task.cancel()
        return default
    except EOFError:
        print(f"⚠️  EOF error - using default: '{default}'")
        return default
    except KeyboardInterrupt:
        print(f"⚠️  Interrupted - using default: '{default}'")
        # Cancel the input task
        if input_task and not input_task.done():
            input_task.cancel()
        return default
    except Exception as e:
        print(f"⚠️  Error ({type(e).__name__}): {e} - using default: '{default}'")
        # Cancel the input task
        if input_task and not input_task.done():
            input_task.cancel()
        return default


async def basic_timeout_test():
    """Basic timeout functionality test"""
    print("🧪 Basic Timeout Test")
    print("=" * 40)
    
    response = await safe_input_with_timeout(
        "What is your name?",
        timeout=5.0,
        default="Anonymous User"
    )
    
    print(f"🎯 Result: '{response}'")
    return response


async def user_proxy_test():
    """Test UserProxyAgent with timeout handling"""
    print("\n🧪 UserProxy with Timeout")
    print("=" * 40)
    
    # Create timeout input function for UserProxy
    async def timeout_input_func(prompt: str, cancellation_token=None) -> str:
        return await safe_input_with_timeout(prompt, timeout=8.0, default="Default User")
    
    user_proxy = UserProxyAgent(
        name="timeout_user",
        description="User with timeout handling",
        input_func=timeout_input_func
    )
    
    token = CancellationToken()
    
    try:
        response = await user_proxy.on_messages(
            [TextMessage(
                content="What's your favorite programming language?",
                source="assistant"
            )],
            cancellation_token=token
        )
        
        print(f"🎯 UserProxy result: '{response.chat_message.content}'")
        return response.chat_message.content
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Error: {e}"
    finally:
        try:
            await user_proxy.on_reset(cancellation_token=token)
        except Exception as e:
            print(f"⚠️  Reset warning: {e}")


async def interactive_chat_example():
    """Interactive chat with AutoGen agents"""
    print("\n🧪 Interactive AutoGen Chat")
    print("=" * 40)
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found - running simulation")
        await chat_simulation()
        return
    
    # Create model client
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    # Create user input function with timeout
    async def robust_user_input(prompt: str, cancellation_token=None) -> str:
        return await safe_input_with_timeout(
            prompt, 
            timeout=15.0, 
            default="I need help with a general question"
        )
    
    # Create agents
    assistant = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message="You are a helpful assistant. Provide concise, useful responses.",
    )
    
    user_proxy = UserProxyAgent(
        name="user",
        description="Human user",
        input_func=robust_user_input
    )
    
    # Create team
    termination = TextMentionTermination("GOODBYE")
    team = SelectorGroupChat(
        [user_proxy, assistant],
        termination_condition=termination,
        max_turns=6,
    )
    
    try:
        print("\n🚀 Starting chat (type 'GOODBYE' to end)...")
        
        response = await Console(
            team.run_stream(
                task="Hello! How can I help you today? Feel free to ask me anything."
            )
        )
        
        print("\n✅ Chat completed!")
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
    finally:
        await model_client.close()


async def chat_simulation():
    """Simulate chat without API calls"""
    print("🎭 Chat Simulation")
    
    user_input = await safe_input_with_timeout(
        "What would you like to ask the assistant?",
        timeout=10.0,
        default="Tell me a joke"
    )
    
    # Simulate assistant response
    responses = {
        "tell me a joke": "Why don't scientists trust atoms? Because they make up everything! 😄",
        "what is python": "Python is a high-level programming language known for its simplicity and readability.",
        "help": "I'm here to help! You can ask me about programming, general knowledge, or anything else.",
    }
    
    # Find best match
    user_lower = user_input.lower()
    response = "That's an interesting question! I'd be happy to help you explore that topic."
    
    for key, value in responses.items():
        if key in user_lower:
            response = value
            break
    
    print(f"\n🤖 Assistant: {response}")
    print("✅ Simulation completed!")


def show_environment_info():
    """Show current environment information"""
    print("🔍 Environment Information")
    print("=" * 40)
    
    checks = [
        ("Interactive stdin", sys.stdin.isatty()),
        ("Interactive stdout", sys.stdout.isatty()),
        ("TTY available", os.isatty(0)),
        ("TERM set", bool(os.environ.get('TERM'))),
        ("OpenAI API key", bool(os.getenv("OPENAI_API_KEY"))),
    ]
    
    for name, check in checks:
        status = "✅" if check else "❌"
        print(f"{status} {name}")
    
    if not sys.stdin.isatty():
        print("\n⚠️  Non-interactive environment detected")
        print("   Input functions will use default values automatically")


def show_usage_examples():
    """Show usage examples"""
    print("\n📖 Usage Examples")
    print("=" * 40)
    
    examples = [
        "# Basic timeout input",
        'response = await safe_input_with_timeout("Question?", timeout=5.0)',
        "",
        "# UserProxy with timeout",
        "async def my_input(prompt, token=None):",
        "    return await safe_input_with_timeout(prompt, timeout=10.0)",
        "",
        "user_proxy = UserProxyAgent(",
        '    name="user",',
        "    input_func=my_input",
        ")",
        "",
        "# Multiple scenarios",
        "await safe_input_with_timeout('Quick?', timeout=3.0, default='Fast')",
        "await safe_input_with_timeout('Normal?', timeout=10.0, default='Medium')",
        "await safe_input_with_timeout('Slow?', timeout=30.0, default='Patient')",
    ]
    
    for example in examples:
        print(f"  {example}")


async def main():
    """Main function with interactive menu"""
    print("🎯 AutoGen User Input with Timeout")
    print("=" * 50)
    
    # Show environment info
    show_environment_info()
    
    # Interactive menu
    choice = await safe_input_with_timeout(
        """
Choose an example:
1. Basic timeout test
2. UserProxy with timeout
3. Interactive AutoGen chat
4. Show usage examples
5. Exit

Enter choice (1-5):""",
        timeout=10.0,
        default="1"
    )
    
    try:
        if choice == "1":
            await basic_timeout_test()
        elif choice == "2":
            await user_proxy_test()
        elif choice == "3":
            await interactive_chat_example()
        elif choice == "4":
            show_usage_examples()
        elif choice == "5":
            print("👋 Goodbye!")
        else:
            print(f"❌ Invalid choice: '{choice}' - running basic test")
            await basic_timeout_test()
            
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted")
    except Exception as e:
        print(f"\n💥 Error: {type(e).__name__}: {e}")
    finally:
        print("\n✅ Program completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 Fatal error: {e}")
    finally:
        print("🚪 Exiting...")
        sys.exit(0)