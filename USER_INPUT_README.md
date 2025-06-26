# AutoGen User Input Examples - Updated

This directory contains updated examples of how to use AutoGen's UserProxyAgent for handling user input, based on the latest AutoGen documentation.

## Key Changes Made

### 1. Updated Imports
```python
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
```

### 2. Updated AssistantAgent Constructor
**Old way:**
```python
assistant = AssistantAgent(
    name="assistant",
    system_message="You are helpful",
    llm_config={
        "config_list": [{"model": "gpt-4", "api_key": "your-key"}]
    },
)
```

**New way:**
```python
model_client = OpenAIChatCompletionClient(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
)

assistant = AssistantAgent(
    name="assistant",
    system_message="You are helpful",
    model_client=model_client,
)
```

### 3. Updated UserProxyAgent Constructor
**Old way:**
```python
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=0,
    llm_config=False,
)
```

**New way:**
```python
user_proxy = UserProxyAgent(
    name="user_proxy",
    description="A human user who can provide input"
)
```

### 4. Updated Conversation Handling
**Old way:**
```python
response = await user_proxy.a_initiate_chat(
    assistant, message="Hello!"
)
```

**New way:**
```python
token = CancellationToken()
response = await user_proxy.on_messages(
    [TextMessage(content="Hello!", source="user")],
    cancellation_token=token
)
```

## Files

### `simple_user_input.py`
Updated main example file with three different user input scenarios:
1. **Simple user input** - Basic interaction between assistant and user
2. **Conditional user input** - Assistant asks for specific information
3. **Cancellable user input** - Example with timeout and cancellation

### `test_simple_user_input.py`
Test file to verify the updated functionality works correctly.

## How to Run

### Prerequisites
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
# or create a .env file with: OPENAI_API_KEY=your-api-key-here
```

### Running the Examples
```bash
python simple_user_input.py
```

### Running Tests
```bash
python test_simple_user_input.py
```

## Key Features

### 1. Model Client
The new API uses `OpenAIChatCompletionClient` for model configuration:
```python
model_client = OpenAIChatCompletionClient(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
)
# Don't forget to close: await model_client.close()
```

### 2. CancellationToken
The new API uses `CancellationToken` for timeout and cancellation handling:
```python
token = CancellationToken()
# Use token in on_messages calls
```

### 3. TextMessage
Messages are now wrapped in `TextMessage` objects:
```python
TextMessage(content="Your message here", source="user")
```

### 4. Async/Await Pattern
All interactions are now properly async:
```python
response = await agent.on_messages(messages, cancellation_token=token)
```

### 5. Error Handling
Proper exception handling for timeouts and cancellations:
```python
try:
    response = await user_proxy.on_messages(messages, token)
except asyncio.CancelledError:
    print("⏰ Task was cancelled.")
except Exception as e:
    print(f"❌ Exception occurred: {e}")
finally:
    await model_client.close()  # Important!
```

**Exception Types:**
- `asyncio.CancelledError`: Thrown when the task is cancelled via CancellationToken
- `Exception`: General exceptions that might occur during execution
- `BaseException`: Unexpected errors (rare, but good to catch)

### 6. Task Cleanup
Proper task cleanup to ensure clean program exit:
```python
# Manual cleanup
timeout_task = asyncio.create_task(timeout_function())
user_task = asyncio.create_task(user_input_function())

try:
    response = await user_task
except asyncio.CancelledError:
    print("Task cancelled")
finally:
    # Clean up all tasks
    if timeout_task and not timeout_task.done():
        timeout_task.cancel()
        try:
            await timeout_task
        except asyncio.CancelledError:
            pass
    
    if user_task and not user_task.done():
        user_task.cancel()
        try:
            await user_task
        except asyncio.CancelledError:
            pass
```

**Or use the TaskManager utility:**
```python
from task_utils import TaskManager

async with TaskManager() as task_mgr:
    timeout_task = asyncio.create_task(timeout_function())
    user_task = asyncio.create_task(user_input_function())
    
    task_mgr.add_task(timeout_task, "timeout")
    task_mgr.add_task(user_task, "user_input")
    
    try:
        response = await user_task
    except asyncio.CancelledError:
        print("Task cancelled")
    # Tasks are automatically cleaned up when exiting context
```

### 7. Default Response Strategy
Instead of cancelling operations, return default responses on timeout:
```python
async def input_with_default(prompt: str, cancellation_token=None) -> str:
    try:
        return await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, input, prompt),
            timeout=10.0
        )
    except asyncio.TimeoutError:
        print("⏰ Timeout! Using default response.")
        return "Default User"  # Return default instead of cancelling
    except Exception as e:
        print(f"⚠️ Input error: {e}. Using default response.")
        return "Default User"

user_proxy = UserProxyAgent(
    name="user_proxy",
    input_func=input_with_default
)
```

**Smart Default Responses:**
```python
class SmartInputHandler:
    def __init__(self):
        self.default_responses = {
            "name": "Anonymous User",
            "color": "Blue",
            "age": "25",
            "preference": "No preference"
        }
    
    async def get_input_with_default(self, prompt: str, cancellation_token=None) -> str:
        try:
            return await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, prompt),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            return self._get_smart_default(prompt)
    
    def _get_smart_default(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "name" in prompt_lower:
            return self.default_responses["name"]
        elif "color" in prompt_lower:
            return self.default_responses["color"]
        # ... more logic
        return "Default response"
```

## Integration Examples

### Web Framework Integration (FastAPI)
```python
from fastapi import FastAPI
from autogen_agentchat.agents import UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

app = FastAPI()

async def custom_input_func(prompt: str, cancellation_token=None):
    # Custom input function for web interface
    return await get_user_input_from_web(prompt)

model_client = OpenAIChatCompletionClient(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
)

user_proxy = UserProxyAgent(
    name="web_user",
    input_func=custom_input_func
)
```

### ChainLit Integration
```python
import chainlit as cl
from autogen_agentchat.agents import UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def chainlit_input_func(prompt: str, cancellation_token=None):
    response = await cl.AskUserMessage(content=prompt).send()
    return response.content

model_client = OpenAIChatCompletionClient(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
)

user_proxy = UserProxyAgent(
    name="chainlit_user",
    input_func=chainlit_input_func
)
```

## Important Notes

1. **Model Client Management**: Always close the model client with `await model_client.close()`
2. **Timeout Handling**: Always use `CancellationToken` for user input to prevent hanging
3. **State Management**: Agents are stateful - maintain conversation context between calls
4. **Error Recovery**: Handle exceptions gracefully, especially for user input timeouts
5. **Web Integration**: Use custom `input_func` for web/UI frameworks

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you have the latest AutoGen packages installed
2. **API Key Issues**: Verify your OpenAI API key is set correctly
3. **Timeout Issues**: Use `CancellationToken` with appropriate timeout values
4. **Async Issues**: Ensure all code is properly async/await
5. **Model Client**: Remember to close the model client in finally blocks

### Getting Help

- Check the [AutoGen documentation](https://microsoft.github.io/autogen/)
- Review the [Human-in-the-loop guide](https://microsoft.github.io/autogen/docs/use-cases/human-in-the-loop)
- Test with the provided test file first 