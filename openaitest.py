import asyncio
from autogen_core.models import UserMessage


async def main():
    result = await openai_model_client.create(
        [UserMessage(content="What is the capital of France?", source="user")]
    )
    print(result)
    await openai_model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
