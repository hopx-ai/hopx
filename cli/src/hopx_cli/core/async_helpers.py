"""Async operation helpers for CLI commands.

Provides utilities for running async functions in CLI commands and handling
event loop lifecycle.
"""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

# Type variable for decorated function return type
F = TypeVar("F", bound=Callable[..., Any])


def run_async(func: F) -> F:
    """Decorator to run async functions in sync CLI commands.

    Wraps an async function to be callable from synchronous code by
    running it with asyncio.run(). Handles edge cases like nested
    event loops and keyboard interrupts.

    Args:
        func: Async function to wrap

    Returns:
        Synchronous wrapper function

    Example:
        @run_async
        async def my_command():
            sandbox = await AsyncSandbox.create(template="python")
            result = await sandbox.run_code("print('Hello')")
            print(result.stdout)

        # Can be called synchronously
        my_command()

    Note:
        This decorator automatically handles:
        - Event loop creation and cleanup
        - Keyboard interrupt (Ctrl+C) propagation
        - Nested event loop detection
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # Try to get current event loop
            try:
                loop = asyncio.get_running_loop()
                # Event loop is already running (nested call)
                # Run in the existing loop using create_task
                task = loop.create_task(func(*args, **kwargs))
                return loop.run_until_complete(task)
            except RuntimeError:
                # No event loop running, create new one
                return asyncio.run(func(*args, **kwargs))
        except KeyboardInterrupt:
            # Propagate keyboard interrupt to caller
            raise

    return cast(F, wrapper)


async def run_with_timeout(coro: Any, timeout: float) -> Any:
    """Run coroutine with timeout.

    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds

    Returns:
        Coroutine result

    Raises:
        asyncio.TimeoutError: If operation times out

    Example:
        result = await run_with_timeout(
            sandbox.run_code("import time; time.sleep(10)"),
            timeout=5.0
        )
    """
    return await asyncio.wait_for(coro, timeout=timeout)


async def gather_with_concurrency(n: int, *tasks: Any) -> list[Any]:
    """Run multiple tasks with limited concurrency.

    Args:
        n: Maximum number of concurrent tasks
        *tasks: Coroutines to run

    Returns:
        List of results in same order as tasks

    Example:
        # Run 10 operations with max 3 concurrent
        results = await gather_with_concurrency(
            3,
            sandbox1.run_code("print(1)"),
            sandbox2.run_code("print(2)"),
            # ... 8 more tasks
        )
    """
    semaphore = asyncio.Semaphore(n)

    async def run_with_semaphore(task: Any) -> Any:
        async with semaphore:
            return await task

    return await asyncio.gather(*[run_with_semaphore(task) for task in tasks])
