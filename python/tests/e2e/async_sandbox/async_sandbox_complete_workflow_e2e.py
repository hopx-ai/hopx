"""
End-to-end test for complete AsyncSandbox workflow.

Tests cover:
- Creating sandbox with async context manager
- File operations
- Code execution
- Environment variables
- Cleanup
"""

import os
import pytest
import asyncio
from hopx_ai import AsyncSandbox, ExecutionResult

# Import cleanup registration functions
from tests.conftest import _register_async_sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


@pytest.mark.asyncio
async def test_complete_async_sandbox_workflow(api_key):
    """Test complete async sandbox workflow."""
    sandbox_id = None
    try:
        # 1. Create sandbox using async context manager
        async with AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
            timeout_seconds=600,
        ) as sandbox:
            # Register sandbox for automatic cleanup (safety net)
            _register_async_sandbox(sandbox)
            sandbox_id = sandbox.sandbox_id
            print(f"\nE2E: Created async sandbox {sandbox_id}")

            # Verify initial info
            info = await sandbox.get_info()
            assert info.status == "running"
            assert info.public_host is not None

            # 2. Perform file operations
            test_file_path = "/workspace/e2e_async_test_file.txt"
            test_content = "E2E async test content for file operations."
            await sandbox.files.write(test_file_path, test_content)
            print(f"E2E: Wrote to {test_file_path}")

            read_content = await sandbox.files.read(test_file_path)
            assert read_content == test_content
            print(f"E2E: Read from {test_file_path}")

            # 3. Run code
            code_to_run = """
import os
print(os.getenv('E2E_VAR', 'default'))
print('Async code execution successful')
"""
            result = await sandbox.run_code(code_to_run, language="python")
            assert isinstance(result, ExecutionResult)
            assert result.success is True
            assert "Async code execution successful" in result.stdout
            print("E2E: Executed code")

            # 4. Set and get environment variables
            env_key = "E2E_VAR"
            env_value = "e2e_async_value_set"
            await sandbox.env.set(env_key, env_value)
            print(f"E2E: Set environment variable {env_key}={env_value}")

            retrieved_env_value = await sandbox.env.get(env_key)
            assert retrieved_env_value == env_value
            print(f"E2E: Retrieved environment variable {env_key}={retrieved_env_value}")

            # Run code again to verify env var is picked up
            code_to_run_env = "import os; print(os.getenv('E2E_VAR'))"
            result_env = await sandbox.run_code(code_to_run_env, language="python")
            assert result_env.success is True
            assert env_value in result_env.stdout
            print("E2E: Verified environment variable in code execution")

            # 5. Pause and resume
            await sandbox.pause()
            info_paused = await sandbox.get_info()
            assert info_paused.status == "paused"
            print("E2E: Paused sandbox")

            await sandbox.resume()
            await asyncio.sleep(2)  # Wait for state change
            info_resumed = await sandbox.get_info()
            assert info_resumed.status == "running"
            print("E2E: Resumed sandbox")

        print(f"E2E: Async sandbox {sandbox_id} automatically killed by context manager.")

        # Verify sandbox is indeed killed
        from hopx_ai.errors import NotFoundError, HopxError
        await asyncio.sleep(2)
        with pytest.raises((NotFoundError, HopxError)):
            await AsyncSandbox.connect(
                sandbox_id=sandbox_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        print(f"E2E: Verified async sandbox {sandbox_id} is stopped.")

    except Exception as e:
        if sandbox_id:
            try:
                # Attempt to kill sandbox even if test failed
                temp_sandbox = AsyncSandbox(
                    sandbox_id=sandbox_id,
                    api_key=api_key,
                    base_url=BASE_URL,
                )
                await temp_sandbox.kill()
                print(f"E2E: Cleaned up async sandbox {sandbox_id} after error.")
            except Exception as cleanup_e:
                print(f"E2E: Failed to clean up async sandbox {sandbox_id}: {cleanup_e}")
        raise e

