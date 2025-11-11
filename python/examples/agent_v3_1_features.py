#!/usr/bin/env python3
"""
Agent v3.1.0 Features Example.

Demonstrates new features in Agent v3.1.0:
- Request ID tracking (automatic in errors)
- Agent metrics monitoring
"""

from hopx_ai import Sandbox, FileNotFoundError

def main():
    print("=" * 60)
    print("Agent v3.1.0 Features Demo")
    print("=" * 60)
    print()
    
    # Create sandbox
    print("Creating sandbox...")
    sandbox = Sandbox.create(template="code-interpreter")
    print(f"✅ Sandbox: {sandbox.sandbox_id}\n")
    
    try:
        # Feature 1: Request ID tracking (automatic)
        print("1️⃣  Request ID Tracking")
        print("=" * 60)
        try:
            # This will fail and include request ID in error
            sandbox.files.read('/nonexistent_file.txt')
        except FileNotFoundError as e:
            print(f"✅ Error caught with Request ID!")
            print(f"   Message: {e.message[:50]}...")
            print(f"   Request ID: {e.request_id}")
            print(f"   (Use this ID for debugging in logs)")
        print()
        
        # Feature 2: Agent Metrics
        print("2️⃣  Agent Metrics Monitoring")
        print("=" * 60)
        metrics = sandbox.get_agent_metrics()
        
        print(f"✅ Agent Metrics:")
        print(f"   Uptime: {metrics.get('uptime_seconds', 0):.0f}s")
        print(f"   Total Requests: {metrics.get('total_requests', 0)}")
        print(f"   Total Errors: {metrics.get('total_errors', 0)}")
        
        # Per-endpoint metrics (if available)
        requests_total = metrics.get('requests_total', {})
        if requests_total:
            print(f"\n   Requests by endpoint:")
            for endpoint, counts in list(requests_total.items())[:5]:
                success = counts.get('success', 0)
                error = counts.get('error', 0)
                print(f"   - {endpoint}: {success} success, {error} errors")
        
        # Performance metrics (if available)
        avg_duration = metrics.get('avg_duration_ms', {})
        if avg_duration:
            print(f"\n   Average duration by endpoint:")
            for endpoint, duration in list(avg_duration.items())[:5]:
                print(f"   - {endpoint}: {duration:.2f}ms")
        
        print()
        
        # Feature 3: Version Tracking
        print("3️⃣  Agent Version")
        print("=" * 60)
        info = sandbox.get_info()
        print(f"✅ Agent Version: {getattr(info, 'agent_version', 'N/A')}")
        print()
        
        # Example: Health monitoring
        print("4️⃣  Health Monitoring Example")
        print("=" * 60)
        
        def is_agent_healthy(sandbox):
            """Check if agent is healthy based on metrics."""
            try:
                metrics = sandbox.get_agent_metrics()
                uptime = metrics.get('uptime_seconds', 0)
                total_errors = metrics.get('total_errors', 0)
                total_requests = metrics.get('total_requests', 0)
                
                # Agent is healthy if:
                # 1. It's running (uptime > 0)
                # 2. Error rate < 10%
                error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
                
                return uptime > 0 and error_rate < 10
            except Exception:
                return False
        
        if is_agent_healthy(sandbox):
            print("✅ Agent is HEALTHY")
            print("   - Uptime > 0")
            print("   - Error rate < 10%")
        else:
            print("⚠️  Agent health check failed")
        
        print()
        
        print("=" * 60)
        print("✅ All Agent v3.1.0 features demonstrated!")
        print("=" * 60)
        print()
        print("New in v3.1.0:")
        print("  ✅ Request ID tracking (automatic)")
        print("  ✅ Agent metrics endpoint")
        print("  ✅ Version tracking (fixed)")
        print("  ✅ Prometheus metrics support")
        print()
        
    finally:
        # Cleanup
        print("Cleaning up...")
        sandbox.kill()
        print("✅ Done!\n")


if __name__ == "__main__":
    main()

