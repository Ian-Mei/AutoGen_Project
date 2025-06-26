#!/usr/bin/env python3
"""
Task Utilities - Helper functions for proper async task management
"""

import asyncio
from typing import Optional, List


async def cleanup_task(task: Optional[asyncio.Task], task_name: str = "task"):
    """Safely cancel and cleanup a single task"""
    if task and not task.done():
        print(f"🧹 Cleaning up {task_name}...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print(f"✅ {task_name} cleaned up successfully")
        except Exception as e:
            print(f"⚠️ Error cleaning up {task_name}: {e}")


async def cleanup_tasks(
    tasks: List[Optional[asyncio.Task]], task_names: List[str] = None
):
    """Safely cancel and cleanup multiple tasks"""
    if task_names is None:
        task_names = [f"task_{i}" for i in range(len(tasks))]

    cleanup_coroutines = []
    for task, name in zip(tasks, task_names):
        if task and not task.done():
            cleanup_coroutines.append(cleanup_task(task, name))

    if cleanup_coroutines:
        await asyncio.gather(*cleanup_coroutines, return_exceptions=True)


async def run_with_timeout(
    coro, timeout_seconds: float, timeout_message: str = "Operation timed out"
):
    """Run a coroutine with a timeout and proper cleanup"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        print(f"⏰ {timeout_message}")
        return None


async def run_with_cancellation(
    coro, cancellation_token, timeout_seconds: float = None
):
    """Run a coroutine with cancellation token and optional timeout"""
    if timeout_seconds:
        # Create a timeout task that cancels the token
        async def timeout_task():
            await asyncio.sleep(timeout_seconds)
            cancellation_token.cancel()

        timeout_coro = asyncio.create_task(timeout_task())
        main_coro = asyncio.create_task(coro)

        try:
            # Wait for either the main task to complete or timeout
            done, pending = await asyncio.wait(
                [main_coro, timeout_coro], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel any pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Return the result if main task completed
            if main_coro in done:
                return await main_coro
            else:
                raise asyncio.CancelledError()

        except asyncio.CancelledError:
            print("⏰ Operation was cancelled")
            raise

    else:
        # Just run with cancellation token
        return await coro


class TaskManager:
    """Context manager for managing multiple tasks with automatic cleanup"""

    def __init__(self):
        self.tasks = []
        self.task_names = []

    def add_task(self, task: asyncio.Task, name: str = None):
        """Add a task to be managed"""
        if name is None:
            name = f"task_{len(self.tasks)}"
        self.tasks.append(task)
        self.task_names.append(name)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await cleanup_tasks(self.tasks, self.task_names)

    def get_task(self, name: str) -> Optional[asyncio.Task]:
        """Get a task by name"""
        try:
            index = self.task_names.index(name)
            return self.tasks[index]
        except ValueError:
            return None

    async def wait_for_task(self, name: str):
        """Wait for a specific task to complete"""
        task = self.get_task(name)
        if task:
            return await task
        return None
