"""
Example: Automatic API Key Rotation
When one organization hits its limit, automatically switch to the next.
"""

from hopx_ai import Sandbox
from hopx_ai.errors import ResourceLimitExceededError

# All available API keys organized by tier
API_KEYS = {
    "tier1": [  # 10 VMs each = 40 total
        "hopx_test_org_010_api_key_abc123def456",
        "hopx_test_org_011_api_key_ghi789jkl012",
        "hopx_test_org_012_api_key_mno345pqr678",
        "hopx_test_org_013_api_key_stu901vwx234",
    ],
    "tier2": [  # 100 VMs each = 300 total
        "hopx_test_org_014_api_key_yza567bcd890",
        "hopx_test_org_015_api_key_efg123hij456",
        "hopx_test_org_016_api_key_klm789nop012",
    ],
    "tier3": [  # 500 VMs each = 1,500 total
        "hopx_test_org_017_api_key_qrs345tuv678",
        "hopx_test_org_018_api_key_wxy901zab234",
        "hopx_test_org_019_api_key_cde567fgh890",
    ],
}


def create_with_rotation(template="code-interpreter", vcpu=2, memory_mb=2048, tier="tier1"):
    """
    Create a sandbox, automatically rotating through API keys if limits are hit.
    
    Args:
        template: Template name
        vcpu: Number of vCPUs
        memory_mb: Memory in MB
        tier: Which tier to use ("tier1", "tier2", or "tier3")
    
    Returns:
        Sandbox instance or None if all keys exhausted
    """
    keys = API_KEYS[tier]
    
    for i, api_key in enumerate(keys):
        try:
            print(f"🔄 Trying key {i+1}/{len(keys)} ({tier})...")
            sandbox = Sandbox.create(
                template=template,
                vcpu=vcpu,
                memory_mb=memory_mb,
                api_key=api_key
            )
            print(f"✅ Success! Created: {sandbox.sandbox_id}")
            return sandbox
            
        except ResourceLimitExceededError:
            print(f"⚠️  Limit hit on key {i+1}, rotating to next...")
            if i == len(keys) - 1:
                print(f"❌ All {tier} keys exhausted!")
                
                # Try next tier
                if tier == "tier1":
                    print("🔄 Switching to Tier 2 (100 VMs/org)...")
                    return create_with_rotation(template, vcpu, memory_mb, "tier2")
                elif tier == "tier2":
                    print("🔄 Switching to Tier 3 (500 VMs/org)...")
                    return create_with_rotation(template, vcpu, memory_mb, "tier3")
                else:
                    print("❌ ALL TIERS EXHAUSTED!")
                    return None
            continue
    
    return None


def main():
    """Example usage"""
    print("╔══════════════════════════════════════════════════╗")
    print("║   🔄 AUTOMATIC API KEY ROTATION DEMO 🔄        ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # Create 5 sandboxes with automatic rotation
    sandboxes = []
    for i in range(5):
        print(f"\n{i+1}. Creating sandbox...")
        sandbox = create_with_rotation()
        if sandbox:
            sandboxes.append(sandbox)
        else:
            print("Failed to create sandbox!")
            break
    
    print(f"\n✅ Successfully created {len(sandboxes)} sandboxes!")
    
    # Clean up
    print("\n🧹 Cleaning up...")
    for sandbox in sandboxes:
        try:
            sandbox.kill()
            print(f"   ✅ Deleted: {sandbox.sandbox_id}")
        except Exception as e:
            print(f"   ❌ Failed to delete: {e}")


if __name__ == "__main__":
    main()
