"""
Debugging utilities for integration tests.

This module provides utilities to help identify where tests get stuck,
including timing information, progress indicators, and verbose logging.
"""

import os
import time
import logging
import functools
from contextlib import contextmanager
from typing import Optional, Callable, Any

# Configure debug logging
DEBUG_ENABLED = os.getenv("HOPX_TEST_DEBUG", "false").lower() in ("true", "1", "yes")
LOG_LEVEL = logging.DEBUG if DEBUG_ENABLED else logging.INFO

# Set up logger
logger = logging.getLogger("hopx.test.debug")
logger.setLevel(LOG_LEVEL)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_operation(operation_name: str, **kwargs):
    """
    Log the start of an operation with context.
    
    Args:
        operation_name: Name of the operation being performed
        **kwargs: Additional context to log
    """
    if DEBUG_ENABLED:
        context = ", ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
        logger.debug(f"Starting: {operation_name}" + (f" ({context})" if context else ""))


def log_operation_complete(operation_name: str, duration: float, **kwargs):
    """
    Log the completion of an operation with timing information.
    
    Args:
        operation_name: Name of the operation that completed
        duration: Time taken in seconds
        **kwargs: Additional context to log
    """
    if DEBUG_ENABLED:
        context = ", ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
        logger.debug(
            f"Completed: {operation_name} in {duration:.2f}s" + 
            (f" ({context})" if context else "")
        )


@contextmanager
def timed_operation(operation_name: str, warn_threshold: float = 60.0, **context):
    """
    Context manager to time an operation and log warnings if it takes too long.
    
    Args:
        operation_name: Name of the operation being timed
        warn_threshold: Time in seconds after which to log a warning (default: 60s)
        **context: Additional context to include in logs
        
    Example:
        with timed_operation("Template.build", template_name="my-template"):
            result = await Template.build(...)
    """
    start_time = time.time()
    log_operation(operation_name, **context)
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        log_operation_complete(operation_name, duration, **context)
        
        if duration > warn_threshold:
            logger.warning(
                f"⚠️  {operation_name} took {duration:.2f}s (>{warn_threshold}s threshold)"
            )


def timed_function(operation_name: Optional[str] = None, warn_threshold: float = 60.0):
    """
    Decorator to time a function execution and log warnings if it takes too long.
    
    Args:
        operation_name: Name of the operation (defaults to function name)
        warn_threshold: Time in seconds after which to log a warning (default: 60s)
        
    Example:
        @timed_function("create_sandbox", warn_threshold=30.0)
        def create_sandbox(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with timed_operation(op_name, warn_threshold=warn_threshold):
                return func(*args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with timed_operation(op_name, warn_threshold=warn_threshold):
                return await func(*args, **kwargs)
        
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        return sync_wrapper
    
    return decorator


class ProgressIndicator:
    """
    Progress indicator for long-running operations.
    
    Prints periodic updates to show that an operation is still running.
    """
    
    def __init__(self, operation_name: str, interval: float = 30.0):
        """
        Initialize progress indicator.
        
        Args:
            operation_name: Name of the operation being monitored
            interval: Time in seconds between progress updates (default: 30s)
        """
        self.operation_name = operation_name
        self.interval = interval
        self.start_time = time.time()
        self.last_update = self.start_time
        
    def check(self, force: bool = False):
        """
        Check if it's time to print a progress update.
        
        Args:
            force: If True, print update regardless of interval
        """
        now = time.time()
        elapsed = now - self.start_time
        
        if force or (now - self.last_update) >= self.interval:
            logger.info(
                f"⏳ {self.operation_name} still running... "
                f"(elapsed: {elapsed:.1f}s)"
            )
            self.last_update = now
    
    def complete(self):
        """Mark the operation as complete and print final timing."""
        duration = time.time() - self.start_time
        logger.info(f"✅ {self.operation_name} completed in {duration:.2f}s")


def log_test_start(test_name: str):
    """Log the start of a test."""
    if DEBUG_ENABLED:
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"{'='*60}")


def log_test_complete(test_name: str, duration: float):
    """Log the completion of a test."""
    if DEBUG_ENABLED:
        logger.info(f"TEST COMPLETE: {test_name} (duration: {duration:.2f}s)")
        logger.info(f"{'='*60}\n")

