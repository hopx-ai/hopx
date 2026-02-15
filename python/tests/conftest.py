"""
Shared pytest configuration and fixtures for Hopx SDK tests.

This module provides common fixtures and configuration used across
integration and E2E tests.
"""

import os
import pytest
import pytest_asyncio
import time
import atexit
import weakref
from pathlib import Path
from typing import Set, Union
from hopx_ai import Sandbox, AsyncSandbox
from hopx_ai.errors import NotFoundError

# Load .env file if it exists (for test environment variables)
try:
    from dotenv import load_dotenv
    
    # Try to load .env file from tests/integration/.env (same location as bash script)
    env_file = Path(__file__).parent / "integration" / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=False)  # Don't override existing env vars
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Test configuration
BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")

# Global sandbox registry for cleanup
# Use weak references to avoid keeping sandboxes alive, but track them for cleanup
_sandbox_registry: Set[weakref.ref] = set()
_async_sandbox_registry: Set[weakref.ref] = set()

# Track sandbox IDs separately for cleanup when objects are lost
# Format: (sandbox_id, api_key, base_url, is_async)
_sandbox_id_registry: Set[tuple] = set()

# Global template registry for cleanup
# Store template_id, api_key, and base_url for cleanup
_template_registry: Set[tuple] = set()  # (template_id, api_key, base_url)


def _register_sandbox(sandbox: Sandbox):
    """Register a sandbox for automatic cleanup."""
    def cleanup_ref(ref):
        """Remove dead references."""
        _sandbox_registry.discard(ref)
    
    ref = weakref.ref(sandbox, cleanup_ref)
    _sandbox_registry.add(ref)
    
    # Also track sandbox_id separately for cleanup when object is lost
    try:
        sandbox_id = getattr(sandbox, 'sandbox_id', None)
        # Get api_key and base_url from the client
        client = getattr(sandbox, '_client', None)
        api_key = None
        base_url = BASE_URL
        if client:
            api_key = getattr(client, 'api_key', None)
            base_url = getattr(client, 'base_url', BASE_URL)
        if sandbox_id and api_key:
            _sandbox_id_registry.add((sandbox_id, api_key, base_url, False))
    except Exception:
        pass  # If we can't get the ID, weak ref is still there
    
    return sandbox


def _register_async_sandbox(sandbox: AsyncSandbox):
    """Register an async sandbox for automatic cleanup."""
    def cleanup_ref(ref):
        """Remove dead references."""
        _async_sandbox_registry.discard(ref)
    
    ref = weakref.ref(sandbox, cleanup_ref)
    _async_sandbox_registry.add(ref)
    
    # Also track sandbox_id separately for cleanup when object is lost
    try:
        sandbox_id = getattr(sandbox, 'sandbox_id', None)
        # Get api_key and base_url from the client
        client = getattr(sandbox, '_client', None)
        api_key = None
        base_url = BASE_URL
        if client:
            api_key = getattr(client, 'api_key', None)
            base_url = getattr(client, 'base_url', BASE_URL)
        if sandbox_id and api_key:
            _sandbox_id_registry.add((sandbox_id, api_key, base_url, True))
    except Exception:
        pass  # If we can't get the ID, weak ref is still there
    
    return sandbox


def _register_template(template_id: str, api_key: str, base_url: str = None):
    """
    Register a template for automatic cleanup.
    
    Args:
        template_id: The template ID to clean up
        api_key: API key for authentication
        base_url: Base URL for the API (defaults to BASE_URL from env)
    """
    if base_url is None:
        base_url = BASE_URL
    _template_registry.add((template_id, api_key, base_url))
    return template_id


def _cleanup_sandbox_by_id(sandbox_id: str, api_key: str, base_url: str, is_async: bool = False):
    """
    Helper function to clean up a sandbox by ID when the object is lost.
    
    This is useful when sandbox creation fails but a sandbox was created on the server,
    or when the sandbox object is garbage collected but we still have the ID.
    """
    if not sandbox_id or not api_key:
        return False
    
    try:
        if is_async:
            import asyncio
            from hopx_ai import AsyncSandbox
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            temp_sandbox = AsyncSandbox(
                sandbox_id=sandbox_id,
                api_key=api_key,
                base_url=base_url,
            )
            loop.run_until_complete(temp_sandbox.kill())
        else:
            from hopx_ai import Sandbox
            temp_sandbox = Sandbox(
                sandbox_id=sandbox_id,
                api_key=api_key,
                base_url=base_url,
            )
            temp_sandbox.kill()
        return True
    except NotFoundError:
        # Sandbox already deleted - that's fine, cleanup successful
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger("hopx.test.cleanup")
        logger.warning(f"Failed to cleanup sandbox {sandbox_id} by ID: {e}")
        return False


def _cleanup_all_sandboxes():
    """Clean up all registered sandboxes."""
    cleaned = 0
    errors = []
    
    # Clean up sync sandboxes via weak references
    for ref in list(_sandbox_registry):
        sandbox = ref()
        if sandbox is not None:
            try:
                sandbox.kill()
                cleaned += 1
            except NotFoundError:
                # Already deleted - that's fine
                cleaned += 1
            except Exception as e:
                sandbox_id = getattr(sandbox, 'sandbox_id', 'unknown')
                errors.append(f"Failed to cleanup sync sandbox {sandbox_id}: {e}")
    
    # Clean up async sandboxes via weak references
    import asyncio
    for ref in list(_async_sandbox_registry):
        sandbox = ref()
        if sandbox is not None:
            try:
                # Try to get existing event loop, create one if needed
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                loop.run_until_complete(sandbox.kill())
                cleaned += 1
            except NotFoundError:
                # Already deleted - that's fine
                cleaned += 1
            except Exception as e:
                sandbox_id = getattr(sandbox, 'sandbox_id', 'unknown')
                errors.append(f"Failed to cleanup async sandbox {sandbox_id}: {e}")
    
    # Clean up sandboxes by ID (handles lost objects and failed creations)
    for sandbox_id, api_key, base_url, is_async in list(_sandbox_id_registry):
        if _cleanup_sandbox_by_id(sandbox_id, api_key, base_url, is_async):
            cleaned += 1
    
    # Clear ID registry after cleanup
    _sandbox_id_registry.clear()
    
    if cleaned > 0 or errors:
        import logging
        logger = logging.getLogger("hopx.test.cleanup")
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} sandbox(es) during session teardown")
        if errors:
            for error in errors:
                logger.warning(error)


def _cleanup_all_templates():
    """Clean up all registered templates."""
    cleaned = 0
    errors = []
    
    import asyncio
    # Try to get existing event loop, create one if needed
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Clean up templates
    for template_id, api_key, base_url in list(_template_registry):
        try:
            loop.run_until_complete(
                AsyncSandbox.delete_template(
                    template_id=template_id,
                    api_key=api_key,
                    base_url=base_url,
                )
            )
            cleaned += 1
        except Exception as e:
            errors.append(f"Failed to cleanup template {template_id}: {e}")
    
    if cleaned > 0 or errors:
        import logging
        logger = logging.getLogger("hopx.test.cleanup")
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} template(s) during session teardown")
        if errors:
            for error in errors:
                logger.warning(error)


# Register cleanup on exit
atexit.register(_cleanup_all_sandboxes)
atexit.register(_cleanup_all_templates)

# Import debug utilities if available
try:
    from tests.integration.debug_utils import (
        timed_operation,
        ProgressIndicator,
        log_test_start,
        log_test_complete,
        DEBUG_ENABLED,
    )
    DEBUG_AVAILABLE = True
except ImportError:
    DEBUG_AVAILABLE = False
    DEBUG_ENABLED = False


@pytest.fixture(scope="session")
def api_key():
    """
    Get API key from environment variable.
    
    Skips tests if HOPX_API_KEY is not set.
    """
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


@pytest.fixture
def test_base_url():
    """Get test base URL from environment or use default."""
    return BASE_URL


@pytest.fixture
def test_template():
    """Get test template name from environment or use default."""
    return TEST_TEMPLATE


@pytest.fixture
def cleanup_template():
    """
    Fixture to ensure template cleanup after test for manually created templates.
    
    Use this fixture when you create templates in your test. Call the returned
    function with template_id, api_key, and optionally base_url to register
    the template for automatic cleanup.
    
    Templates are automatically cleaned up even if the test fails.
    
    Example:
        async def test_create_template(api_key, cleanup_template):
            result = await Template.build(...)
            cleanup_template(result.template_id, api_key)
            # ... test code ...
    """
    registered_templates = []
    
    def register(template_id: str, api_key: str, base_url: str = None):
        """Register a template for cleanup."""
        _register_template(template_id, api_key, base_url)
        registered_templates.append((template_id, api_key, base_url or BASE_URL))
    
    try:
        yield register
    finally:
        # Cleanup registered templates, even if test fails
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        for template_id, api_key, base_url in registered_templates:
            try:
                loop.run_until_complete(
                    AsyncSandbox.delete_template(
                        template_id=template_id,
                        api_key=api_key,
                        base_url=base_url,
                    )
                )
            except Exception as e:
                import logging
                logger = logging.getLogger("hopx.test.cleanup")
                logger.warning(f"Failed to cleanup template {template_id}: {e}")


@pytest.fixture
def sandbox_factory(api_key, test_base_url, test_template):
    """
    Factory fixture for creating sandboxes.
    
    Returns a function that creates a sandbox with default settings.
    Sandboxes created through this factory are automatically registered for cleanup.
    """
    def _create_sandbox(**kwargs):
        """Create a sandbox with optional overrides."""
        defaults = {
            "template": test_template,
            "api_key": api_key,
            "base_url": test_base_url,
            "timeout_seconds": 600,  # 10 minutes
        }
        defaults.update(kwargs)
        sandbox = Sandbox.create(**defaults)
        _register_sandbox(sandbox)
        return sandbox
    
    return _create_sandbox


@pytest.fixture
def sandbox(api_key, test_base_url, test_template):
    """
    Create a standard sandbox for testing and clean up after.
    
    This fixture creates a sandbox with default settings and automatically
    cleans it up after the test completes, even if the test fails.
    """
    sandbox = None
    sandbox_id = None
    try:
        sandbox = Sandbox.create(
            template=test_template,
            api_key=api_key,
            base_url=test_base_url,
            timeout_seconds=600,  # 10 minutes
        )
        sandbox_id = getattr(sandbox, 'sandbox_id', None)
        _register_sandbox(sandbox)
        yield sandbox
    except Exception as e:
        # If creation fails but we got a sandbox_id, try to clean up
        if sandbox_id:
            _cleanup_sandbox_by_id(sandbox_id, api_key, test_base_url, is_async=False)
        raise e
    finally:
        # Always cleanup, even if test fails
        if sandbox is not None:
            try:
                sandbox.kill()
            except NotFoundError:
                # Already deleted - that's fine
                pass
            except Exception as e:
                import logging
                logger = logging.getLogger("hopx.test.cleanup")
                logger.warning(f"Failed to cleanup sandbox {getattr(sandbox, 'sandbox_id', 'unknown')}: {e}")
        elif sandbox_id:
            # Sandbox object lost but we have the ID - try cleanup by ID
            _cleanup_sandbox_by_id(sandbox_id, api_key, test_base_url, is_async=False)


@pytest_asyncio.fixture
async def async_sandbox(api_key, test_base_url, test_template):
    """
    Create a standard async sandbox for testing and clean up after.
    
    This fixture creates an async sandbox with default settings and automatically
    cleans it up after the test completes, even if the test fails.
    """
    sandbox = None
    sandbox_id = None
    try:
        sandbox = await AsyncSandbox.create(
            template=test_template,
            api_key=api_key,
            base_url=test_base_url,
            timeout_seconds=600,  # 10 minutes
        )
        sandbox_id = getattr(sandbox, 'sandbox_id', None)
        _register_async_sandbox(sandbox)
        yield sandbox
    except Exception as e:
        # If creation fails but we got a sandbox_id, try to clean up
        if sandbox_id:
            _cleanup_sandbox_by_id(sandbox_id, api_key, test_base_url, is_async=True)
        raise e
    finally:
        # Always cleanup, even if test fails
        if sandbox is not None:
            try:
                await sandbox.kill()
            except NotFoundError:
                # Already deleted - that's fine
                pass
            except Exception as e:
                import logging
                logger = logging.getLogger("hopx.test.cleanup")
                logger.warning(f"Failed to cleanup async sandbox {getattr(sandbox, 'sandbox_id', 'unknown')}: {e}")
        elif sandbox_id:
            # Sandbox object lost but we have the ID - try cleanup by ID
            _cleanup_sandbox_by_id(sandbox_id, api_key, test_base_url, is_async=True)


@pytest.fixture
def desktop_sandbox(api_key, test_base_url):
    """
    Create a sandbox with desktop-enabled template for desktop tests.
    
    This fixture creates a sandbox using the desktop template (ID: 399 by default,
    configurable via HOPX_DESKTOP_TEMPLATE env var) and automatically cleans it up
    after the test completes, even if the test fails.
    
    Desktop tests require a template with desktop/VNC capabilities. This fixture
    ensures the correct template is used.
    """
    desktop_template = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")
    sandbox = None
    sandbox_id = None
    try:
        sandbox = Sandbox.create(
            template_id=desktop_template,  # Use template_id for desktop template
            api_key=api_key,
            base_url=test_base_url,
            timeout_seconds=600,  # 10 minutes
        )
        sandbox_id = getattr(sandbox, 'sandbox_id', None)
        _register_sandbox(sandbox)
        yield sandbox
    except Exception as e:
        # If creation fails but we got a sandbox_id, try to clean up
        if sandbox_id:
            _cleanup_sandbox_by_id(sandbox_id, api_key, test_base_url, is_async=False)
        raise e
    finally:
        # Always cleanup, even if test fails
        if sandbox is not None:
            try:
                sandbox.kill()
            except NotFoundError:
                # Already deleted - that's fine
                pass
            except Exception as e:
                import logging
                logger = logging.getLogger("hopx.test.cleanup")
                logger.warning(f"Failed to cleanup desktop sandbox {getattr(sandbox, 'sandbox_id', 'unknown')}: {e}")
        elif sandbox_id:
            # Sandbox object lost but we have the ID - try cleanup by ID
            _cleanup_sandbox_by_id(sandbox_id, api_key, test_base_url, is_async=False)


@pytest.fixture
def cleanup_sandbox():
    """
    Fixture to ensure sandbox cleanup after test for manually created sandboxes.
    
    Use this fixture when you need to create sandboxes with custom parameters
    in your test. Append any sandbox you create to the returned list, and
    they will be automatically cleaned up after the test, even if the test fails.
    
    Sandboxes are automatically registered in the global registry for
    session-level cleanup as a safety net when appended to the list.
    
    Example:
        def test_custom_sandbox(api_key, cleanup_sandbox):
            sandbox = Sandbox.create(template="custom", api_key=api_key)
            cleanup_sandbox.append(sandbox)  # Automatically registered for cleanup
            # ... test code ...
    """
    sandboxes_to_cleanup = []
    
    # Custom list class that auto-registers sandboxes when appended
    class AutoRegisterList(list):
        def append(self, sandbox):
            super().append(sandbox)
            if sandbox is not None:
                _register_sandbox(sandbox)
    
    cleanup_list = AutoRegisterList()
    try:
        yield cleanup_list
    finally:
        # Always cleanup, even if test fails
        for sandbox in cleanup_list:
            if sandbox is not None:
                try:
                    sandbox.kill()
                except NotFoundError:
                    # Already deleted - that's fine
                    pass
                except Exception as e:
                    import logging
                    logger = logging.getLogger("hopx.test.cleanup")
                    logger.warning(f"Failed to cleanup sandbox {getattr(sandbox, 'sandbox_id', 'unknown')}: {e}")


@pytest_asyncio.fixture
async def cleanup_async_sandbox():
    """
    Fixture to ensure async sandbox cleanup after test for manually created sandboxes.
    
    Use this fixture when you need to create async sandboxes with custom parameters
    in your test. Append any sandbox you create to the returned list, and
    they will be automatically cleaned up after the test, even if the test fails.
    
    Sandboxes are automatically registered in the global registry for
    session-level cleanup as a safety net when appended to the list.
    
    Example:
        async def test_custom_sandbox(api_key, cleanup_async_sandbox):
            sandbox = await AsyncSandbox.create(template="custom", api_key=api_key)
            cleanup_async_sandbox.append(sandbox)  # Automatically registered for cleanup
            # ... test code ...
    """
    # Custom list class that auto-registers sandboxes when appended
    class AutoRegisterList(list):
        def append(self, sandbox):
            super().append(sandbox)
            if sandbox is not None:
                _register_async_sandbox(sandbox)
    
    cleanup_list = AutoRegisterList()
    try:
        yield cleanup_list
    finally:
        # Always cleanup, even if test fails
        for sandbox in cleanup_list:
            if sandbox is not None:
                try:
                    await sandbox.kill()
                except NotFoundError:
                    # Already deleted - that's fine
                    pass
                except Exception as e:
                    import logging
                    logger = logging.getLogger("hopx.test.cleanup")
                    logger.warning(f"Failed to cleanup async sandbox {getattr(sandbox, 'sandbox_id', 'unknown')}: {e}")


@pytest.fixture(autouse=True)
def test_timer(request):
    """
    Automatic fixture that times each test and logs debug information.
    
    This fixture runs automatically for every test and provides timing
    information when HOPX_TEST_DEBUG environment variable is set.
    """
    if not DEBUG_AVAILABLE:
        yield
        return
    
    test_name = f"{request.node.parent.name}::{request.node.name}"
    start_time = time.time()
    
    log_test_start(test_name)
    
    yield
    
    duration = time.time() - start_time
    log_test_complete(test_name, duration)
    
    # Warn if test takes longer than 2 minutes
    if duration > 120:
        import logging
        logger = logging.getLogger("hopx.test.debug")
        logger.warning(
            f"⚠️  Test {test_name} took {duration:.2f}s (>2 minutes)"
        )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    
    # Enable verbose output if debug mode is enabled
    if DEBUG_AVAILABLE and DEBUG_ENABLED:
        # Set pytest to show more verbose output
        if hasattr(config.option, 'verbose'):
            config.option.verbose = max(config.option.verbose or 0, 1)


def pytest_runtest_teardown(item, nextitem):
    """
    Hook called after each test teardown.
    
    This ensures cleanup happens even if test fixtures fail.
    """
    # Cleanup is handled by fixtures with finally blocks
    # This hook is here as a safety net for any edge cases
    pass


def pytest_sessionfinish(session, exitstatus):
    """
    Hook called after entire test session finishes.
    
    This is a final safety net to cleanup any remaining sandboxes and templates
    that weren't cleaned up by fixtures (e.g., due to crashes, interrupts).
    """
    _cleanup_all_sandboxes()
    _cleanup_all_templates()

