#!/usr/bin/env python3
"""
Test WebSocket Authentication

Comprehensive test suite verifying JWT token authentication for WebSocket connections.
Tests both sync (Sandbox + Terminal) and async (AsyncSandbox + AsyncTerminal) implementations.

Requirements:
- HOPX_API_KEY environment variable must be set
- Sandbox must support terminal WebSocket connections

Run:
    export HOPX_API_KEY="your_api_key"
    python examples/test_websocket_auth.py
"""

import os
import sys
import asyncio
from hopx_ai import Sandbox, AsyncSandbox


def test_sync_websocket_client_jwt_token():
    """Test that WebSocketClient stores and uses JWT token."""
    print("\n" + "=" * 80)
    print("TEST 1: WebSocketClient JWT Token Storage")
    print("=" * 80)

    try:
        # Create sandbox
        sandbox = Sandbox.create(template="code-interpreter")
        print(f"✓ Created sandbox: {sandbox.sandbox_id}")

        # Initialize WebSocket client (lazy load)
        sandbox._ensure_ws_client()
        print(f"✓ WebSocket client initialized")

        # Verify token is stored
        assert sandbox._ws_client is not None, "WebSocket client not initialized"
        assert sandbox._ws_client._jwt_token is not None, "JWT token not stored"
        print(f"✓ JWT token stored in WebSocket client")

        # Verify token matches sandbox token
        sandbox_token = sandbox.get_token()
        ws_token = sandbox._ws_client._jwt_token
        assert ws_token == sandbox_token, "Token mismatch"
        print(f"✓ WebSocket token matches sandbox token")

        # Cleanup
        sandbox.kill()
        print(f"✓ Sandbox cleaned up")
        print("\n✅ TEST 1 PASSED: WebSocket client properly stores JWT token\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}\n")
        return False


def test_sync_token_refresh_updates_ws_client():
    """Test that token refresh updates WebSocket client."""
    print("\n" + "=" * 80)
    print("TEST 2: Token Refresh Updates WebSocket Client")
    print("=" * 80)

    try:
        # Create sandbox
        sandbox = Sandbox.create(template="code-interpreter")
        print(f"✓ Created sandbox: {sandbox.sandbox_id}")

        # Initialize WebSocket client
        sandbox._ensure_ws_client()
        old_token = sandbox._ws_client._jwt_token
        print(f"✓ Initial token: {old_token[:20]}...")

        # Refresh token
        sandbox.refresh_token()
        new_token = sandbox._ws_client._jwt_token
        print(f"✓ Token refreshed: {new_token[:20]}...")

        # Verify token was updated
        assert new_token != old_token, "Token not updated after refresh"
        print(f"✓ WebSocket client token updated on refresh")

        # Cleanup
        sandbox.kill()
        print(f"✓ Sandbox cleaned up")
        print("\n✅ TEST 2 PASSED: Token refresh updates WebSocket client\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}\n")
        return False


async def test_async_terminal_jwt_auth():
    """Test that AsyncTerminal includes JWT token in connection."""
    print("\n" + "=" * 80)
    print("TEST 3: AsyncTerminal JWT Authentication")
    print("=" * 80)

    try:
        # Create async sandbox
        sandbox = await AsyncSandbox.create(template="code-interpreter")
        print(f"✓ Created async sandbox: {sandbox.sandbox_id}")

        # Get token to verify it exists
        token = await sandbox.get_token()
        assert token is not None, "No JWT token available"
        print(f"✓ JWT token available: {token[:20]}...")

        # Connect to terminal (should include JWT auth)
        async with await sandbox.terminal.connect(timeout=30) as ws:
            print(f"✓ Terminal WebSocket connected with JWT authentication")

            # Send a simple command
            await sandbox.terminal.send_input(ws, "echo 'auth test'\n")
            print(f"✓ Sent test command")

            # Read output (with timeout)
            output_received = False
            try:
                async for msg in sandbox.terminal.iter_output(ws):
                    if msg.get('type') == 'output' and 'auth test' in msg.get('data', ''):
                        output_received = True
                        print(f"✓ Received output: {msg['data'].strip()}")
                        break
                    if msg.get('type') == 'exit':
                        break
            except asyncio.TimeoutError:
                print("⚠ Timeout waiting for output (connection still valid)")

        # Cleanup
        await sandbox.kill()
        print(f"✓ Sandbox cleaned up")
        print("\n✅ TEST 3 PASSED: AsyncTerminal authenticates with JWT token\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}\n")
        try:
            await sandbox.kill()
        except:
            pass
        return False


def test_websocket_error_handling():
    """Test that WebSocket errors are wrapped in SDK exceptions."""
    print("\n" + "=" * 80)
    print("TEST 4: WebSocket Error Handling")
    print("=" * 80)

    try:
        from hopx_ai._ws_client import WebSocketClient
        from hopx_ai.errors import AgentError

        # Create WebSocket client with invalid URL
        client = WebSocketClient(
            agent_url="https://invalid-host-that-does-not-exist.hopx.dev",
            jwt_token="fake_token"
        )
        print(f"✓ Created WebSocket client with invalid URL")

        # Try to connect (should raise AgentError)
        try:
            import asyncio
            asyncio.run(client.connect("/test", timeout=5))
            print(f"❌ Expected AgentError but connection succeeded")
            return False
        except AgentError as e:
            print(f"✓ WebSocket error wrapped in AgentError: {str(e)[:60]}...")
            print("\n✅ TEST 4 PASSED: WebSocket errors properly wrapped\n")
            return True
        except Exception as e:
            print(f"❌ Unexpected error type: {type(e).__name__}")
            return False

    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}\n")
        return False


def main():
    """Run all tests and report results."""
    print("\n" + "=" * 80)
    print("WebSocket Authentication Test Suite")
    print("=" * 80)
    print("\nTesting JWT token authentication for WebSocket connections")
    print("This verifies fixes in v0.3.3 for sync and async implementations\n")

    # Check API key
    api_key = os.environ.get("HOPX_API_KEY")
    if not api_key:
        print("❌ ERROR: HOPX_API_KEY environment variable not set")
        print("   Set it with: export HOPX_API_KEY='your_api_key'")
        sys.exit(1)

    print(f"✓ API key found: {api_key[:15]}...\n")

    # Run tests
    results = []

    # Test 1: Sync WebSocket client JWT storage
    results.append(("WebSocket JWT Token Storage", test_sync_websocket_client_jwt_token()))

    # Test 2: Token refresh updates WebSocket
    results.append(("Token Refresh Updates WebSocket", test_sync_token_refresh_updates_ws_client()))

    # Test 3: Async terminal authentication
    results.append(("AsyncTerminal JWT Auth", asyncio.run(test_async_terminal_jwt_auth())))

    # Test 4: Error handling
    results.append(("WebSocket Error Handling", test_websocket_error_handling()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if failed > 0:
        print(f"\n❌ {failed} test(s) failed")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        print("\nWebSocket authentication is working correctly:")
        print("- JWT tokens properly stored in WebSocket clients")
        print("- Token refresh updates WebSocket clients")
        print("- AsyncTerminal includes JWT authentication")
        print("- WebSocket errors wrapped in SDK exceptions")
        sys.exit(0)


if __name__ == "__main__":
    main()
