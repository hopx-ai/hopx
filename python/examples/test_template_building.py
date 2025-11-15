#!/usr/bin/env python3
"""
HOPX Python SDK - Template Building Flow Test
Tests the complete template building flow matching test-template-build.sh
"""

import os
import sys
import asyncio
import hashlib
import tarfile
import tempfile
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import hopx_ai
sys.path.insert(0, str(Path(__file__).parent.parent))

from hopx_ai import Template, Sandbox
from hopx_ai.template import BuildOptions, BuildResult

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

# Configuration
API_BASE_URL = os.environ.get("HOPX_BASE_URL", "https://api.hopx.dev")
API_KEY = os.environ.get("HOPX_API_KEY", "")

# Test data
TEST_TEMPLATE_NAME = f"test-python-{int(datetime.now().timestamp())}"
TEST_FILES_HASH = ""

# Test results tracker
test_results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0
}


def print_header(text: str):
    """Print section header"""
    print()
    print(f"{CYAN}{'━' * 60}{NC}")
    print(f"{CYAN}  {text}{NC}")
    print(f"{CYAN}{'━' * 60}{NC}")
    print()


def print_step(text: str):
    """Print test step"""
    print(f"{BLUE}▶ {text}{NC}")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{NC}")
    test_results["passed"] += 1


def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{NC}")
    test_results["failed"] += 1


def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{NC}")
    test_results["warnings"] += 1


def check_api_key():
    """Check if API key is set"""
    print_header("Checking API Key")
    
    if not API_KEY:
        print_error("HOPX_API_KEY environment variable is not set")
        print()
        print("Usage:")
        print("  export HOPX_API_KEY=your_api_key_here")
        print("  python test_template_building.py")
        sys.exit(1)
    
    print_success(f"API Key is set: {API_KEY[:10]}...")


async def test_upload_files():
    """Test Step 1: Create test files, upload to R2"""
    global TEST_FILES_HASH
    
    print_header("Step 1: Get Presigned Upload URL & Upload to R2")
    
    print_step("Creating test tar.gz file")
    
    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "app.py").write_text("print('Hello from HOPX!')")
        (temp_path / "requirements.txt").write_text("flask==3.0.0")
        
        # Create tar.gz
        tar_path = temp_path / "test-files.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(temp_path / "app.py", arcname="app.py")
            tar.add(temp_path / "requirements.txt", arcname="requirements.txt")
        
        # Calculate SHA256 hash
        with open(tar_path, "rb") as f:
            file_content = f.read()
            files_hash = hashlib.sha256(file_content).hexdigest()
        
        TEST_FILES_HASH = files_hash
        file_size = tar_path.stat().st_size
        
        print_success(f"Test file created: {file_size} bytes")
        print_success(f"Files hash: {files_hash}")
        
        print_step("Requesting presigned upload URL")
        
        # Use SDK's internal client to get upload link
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/v1/templates/files/upload-link",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "files_hash": files_hash,
                    "content_length": file_size,
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print_success("Upload link received")
                    
                    if data.get("present"):
                        print_warning("File already exists in R2 (cache hit - skipping upload)")
                    else:
                        upload_url = data.get("upload_url")
                        print_success("Upload URL received")
                        
                        # Upload to R2
                        print_step("Uploading file to R2...")
                        async with session.put(
                            upload_url,
                            headers={
                                "Content-Type": "application/gzip",
                                "Content-Length": str(file_size),
                            },
                            data=file_content
                        ) as upload_response:
                            if upload_response.status in [200, 204]:
                                print_success("File uploaded to R2 successfully!")
                            else:
                                print_error(f"R2 upload failed (HTTP {upload_response.status})")
                else:
                    print_error(f"Failed to get upload link (HTTP {response.status})")


async def test_build_template_minimal():
    """Test Step 2a: Build Template - Minimal (Required Fields Only)"""
    print_header("Step 2a: Build Template - Minimal (Required Fields Only)")
    
    print_step(f"Building template: {TEST_TEMPLATE_NAME}-minimal")
    
    try:
        template = (
            Template()
            .from_python_image("3.11-slim")
            .run_cmd("pip install flask")
        )
        
        result = await Template.build(
            template,
            BuildOptions(
                name=f"{TEST_TEMPLATE_NAME}-minimal",
                api_key=API_KEY,
                base_url=API_BASE_URL,
                cpu=2,
                memory=1024,
                disk_gb=5,
                on_log=lambda log: None,  # Suppress logs for cleaner output
            )
        )
        
        print_success("Template build triggered")
        print_success(f"Template ID: {result.template_id}")
        print_success(f"Build ID: {result.build_id}")
        
        # Save for later tests
        Path("/tmp/hopx_test_template_id_minimal_py.txt").write_text(result.template_id)
        
    except Exception as e:
        print_error(f"Failed to trigger build: {str(e)}")


async def test_build_template_full():
    """Test Step 2b: Build Template - Full Features"""
    print_header("Step 2b: Build Template - Full Features")
    
    print_step(f"Building template with all features: {TEST_TEMPLATE_NAME}-full")
    
    try:
        template = (
            Template()
            .from_python_image("3.11-slim")
            .run_cmd("apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y git curl vim && apt-get clean && rm -rf /var/lib/apt/lists/*")
            .set_env("PYTHON_VERSION", "3.11")
            .set_env("DEBUG", "true")
            .set_env("PORT", "8000")
            .run_cmd("pip install --upgrade pip")
            .run_cmd("pip install flask gunicorn")
            .run_cmd("useradd -m appuser")
            .set_workdir("/app")
            .run_cmd("chown appuser:appuser /app")
            .set_user("appuser")
        )
        
        result = await Template.build(
            template,
            BuildOptions(
                name=f"{TEST_TEMPLATE_NAME}-full",
                api_key=API_KEY,
                base_url=API_BASE_URL,
                cpu=4,
                memory=4096,
                disk_gb=20,
                on_log=lambda log: None,
            )
        )
        
        print_success("Template build triggered (with all features)")
        print_success(f"Template ID: {result.template_id}")
        
        Path("/tmp/hopx_test_template_id_full_py.txt").write_text(result.template_id)
        
    except Exception as e:
        print_error(f"Failed to trigger build: {str(e)}")


async def test_build_template_with_copy():
    """Test Step 2c: Build Template - With COPY Step"""
    print_header("Step 2c: Build Template - With COPY Step")
    
    print_step(f"Building template with COPY step: {TEST_TEMPLATE_NAME}-copy")
    
    try:
        # Create temporary directory with files to copy
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "app.py").write_text("""
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from HOPX!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
""")
            (temp_path / "requirements.txt").write_text("flask==3.0.0")
            
            print_step(f"Created test files in: {temp_dir}")
            
            # Build template using SDK's .copy() method
            template = (
                Template()
                .from_python_image("3.11-slim")
                .set_workdir("/app")
                .copy(str(temp_path), "/app")  # SDK handles upload automatically
                .set_env("FLASK_APP", "app.py")
                .run_cmd("pip install -r requirements.txt")
            )
            
            result = await Template.build(
                template,
                BuildOptions(
                    name=f"{TEST_TEMPLATE_NAME}-copy",
                    api_key=API_KEY,
                    base_url=API_BASE_URL,
                    cpu=2,
                    memory=2048,
                    disk_gb=10,
                    on_log=lambda log: None,
                )
            )
            
            print_success("Template build triggered (with COPY using SDK)")
            print_success(f"Template ID: {result.template_id}")
            
            Path("/tmp/hopx_test_template_id_copy_py.txt").write_text(result.template_id)
        
    except Exception as e:
        print_error(f"Failed to trigger build: {str(e)}")


async def test_build_ubuntu_with_apt():
    """Test Step 2d: Build Template - Ubuntu with apt_install"""
    print_header("Step 2d: Build Template - Ubuntu with apt_install")
    
    print_step(f"Building Ubuntu template with apt_install: {TEST_TEMPLATE_NAME}-ubuntu")
    
    try:
        template = (
            Template()
            .from_ubuntu_image("22.04")
            .apt_install("curl", "git", "vim")
            .run_cmd("curl --version")
            .set_env("MY_VAR", "test")
        )
        
        result = await Template.build(
            template,
            BuildOptions(
                name=f"{TEST_TEMPLATE_NAME}-ubuntu",
                api_key=API_KEY,
                base_url=API_BASE_URL,
                cpu=2,
                memory=1024,
                disk_gb=5,
                on_log=lambda log: None,
            )
        )
        
        print_success("Ubuntu template build triggered (with apt_install)")
        print_success(f"Template ID: {result.template_id}")
        
    except Exception as e:
        print_error(f"Failed to trigger build: {str(e)}")


async def test_build_nodejs_template():
    """Test Step 2e: Build Template - Node.js"""
    print_header("Step 2e: Build Template - Node.js")
    
    print_step(f"Building Node.js template: {TEST_TEMPLATE_NAME}-nodejs")
    
    try:
        template = (
            Template()
            .from_node_image("20")
            .run_cmd("node --version")
            .run_cmd("npm --version")
            .set_workdir("/app")
        )
        
        result = await Template.build(
            template,
            BuildOptions(
                name=f"{TEST_TEMPLATE_NAME}-nodejs",
                api_key=API_KEY,
                base_url=API_BASE_URL,
                cpu=2,
                memory=1024,
                disk_gb=5,
                on_log=lambda log: None,
            )
        )
        
        print_success("Node.js template build triggered")
        print_success(f"Template ID: {result.template_id}")
        
    except Exception as e:
        print_error(f"Failed to trigger build: {str(e)}")


async def test_validation_errors():
    """Test Step 3: Testing Validations (Expected Errors)"""
    print_header("Step 3: Testing Validations (Expected Errors)")
    
    import aiohttp
    
    # Test 3a: Missing CPU
    print_step("Test 3a: Missing CPU (should fail)")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/v1/templates/build",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={
                    "name": "test-invalid",
                    "memory": 1024,
                    "diskGB": 5,
                    "from_image": "ubuntu:22.04",
                    "steps": []
                }
            ) as response:
                if response.status == 400:
                    print_success("Correctly rejected (HTTP 400)")
                else:
                    print_error(f"Should have failed with 400, got {response.status}")
    except Exception as e:
        print_error(f"Test error: {str(e)}")
    
    # Test 3b: CPU too high
    print_step("Test 3b: CPU too high (should fail)")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/v1/templates/build",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={
                    "name": "test-invalid",
                    "cpu": 100,
                    "memory": 1024,
                    "diskGB": 5,
                    "from_image": "ubuntu:22.04",
                    "steps": []
                }
            ) as response:
                if response.status == 400:
                    print_success("Correctly rejected (HTTP 400)")
                else:
                    print_error(f"Should have failed with 400, got {response.status}")
    except Exception as e:
        print_error(f"Test error: {str(e)}")
    
    # Test 3c: Memory too low
    print_step("Test 3c: Memory too low (should fail)")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/v1/templates/build",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={
                    "name": "test-invalid",
                    "cpu": 2,
                    "memory": 256,
                    "diskGB": 5,
                    "from_image": "ubuntu:22.04",
                    "steps": []
                }
            ) as response:
                if response.status == 400:
                    print_success("Correctly rejected (HTTP 400)")
                else:
                    print_error(f"Should have failed with 400, got {response.status}")
    except Exception as e:
        print_error(f"Test error: {str(e)}")
    
    # Test 3d: Alpine (should fail)
    print_step("Test 3d: Alpine image (should fail)")
    try:
        template = Template().from_ubuntu_image("alpine:latest").run_cmd("echo test")
        # This should fail during validation
        result = await Template.build(
            template,
            BuildOptions(
                name="test-invalid-alpine",
                api_key=API_KEY,
                base_url=API_BASE_URL,
                cpu=2,
                memory=1024,
                disk_gb=5,
            )
        )
        print_error("Alpine should have been rejected but wasn't")
    except Exception as e:
        if "alpine" in str(e).lower() or "hopx-agent" in str(e).lower():
            print_success(f"Correctly rejected Alpine: {str(e)[:100]}")
        else:
            print_warning(f"Failed but not with Alpine error: {str(e)[:100]}")
    
    # Test 3e: Duplicate template name (should fail with 409)
    print_step("Test 3e: Duplicate template name without update flag (should fail with 409)")
    try:
        template = Template().from_ubuntu_image("22.04").run_cmd("echo test")
        result = await Template.build(
            template,
            BuildOptions(
                name=f"{TEST_TEMPLATE_NAME}-minimal",
                api_key=API_KEY,
                base_url=API_BASE_URL,
                cpu=2,
                memory=1024,
                disk_gb=5,
            )
        )
        print_error("Duplicate should have been rejected but wasn't")
    except Exception as e:
        if "409" in str(e) or "already exists" in str(e).lower():
            print_success("Correctly rejected duplicate (HTTP 409 Conflict)")
        else:
            print_warning(f"Failed but not with conflict error: {str(e)[:100]}")
    
    # Test 3f: Update non-existent template (should fail with 404)
    print_step("Test 3f: Update non-existent template (should fail with 404)")
    try:
        template = Template().from_ubuntu_image("22.04").run_cmd("echo test")
        result = await Template.build(
            template,
            BuildOptions(
                name=f"non-existent-template-{int(datetime.now().timestamp())}",
                api_key=API_KEY,
                base_url=API_BASE_URL,
                cpu=2,
                memory=1024,
                disk_gb=5,
                update=True,
            )
        )
        print_error("Update of non-existent should have been rejected but wasn't")
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            print_success("Correctly rejected update of non-existent template (HTTP 404 Not Found)")
        else:
            print_warning(f"Failed but not with 404 error: {str(e)[:100]}")


async def test_update_template():
    """Test Step 4: Testing Update Flag (Success Case)"""
    print_header("Step 4: Testing Update Flag (Success Case)")
    
    print_step(f"Updating existing template '{TEST_TEMPLATE_NAME}-minimal' with update=true")
    
    try:
        template = (
            Template()
            .from_python_image("3.11-slim")
            .run_cmd("pip install flask redis")
        )
        
        result = await Template.build(
            template,
            BuildOptions(
                name=f"{TEST_TEMPLATE_NAME}-minimal",
                api_key=API_KEY,
                base_url=API_BASE_URL,
                cpu=2,
                memory=2048,
                disk_gb=10,
                update=True,
                on_log=lambda log: None,
            )
        )
        
        print_success("Template updated successfully (HTTP 202)")
        print_success(f"Template ID: {result.template_id}")
        
    except Exception as e:
        print_error(f"Update failed: {str(e)}")


async def test_get_build_status():
    """Test Step 5: Check Build Status"""
    print_header("Step 5: Check Build Status")
    
    template_id_file = Path("/tmp/hopx_test_template_id_minimal_py.txt")
    if not template_id_file.exists():
        print_warning("No template ID found, skipping status check")
        return
    
    template_id = template_id_file.read_text().strip()
    print_step(f"Checking status for template: {template_id}")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/v1/templates/build/{template_id}/status",
                headers={"Authorization": f"Bearer {API_KEY}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print_success("Build status retrieved")
                    build_status = data.get("status", "unknown")
                    print_success(f"Build status: {build_status}")
                    print(f"  Progress: {data.get('progress', 0)}%")
                else:
                    print_error(f"Failed to get build status (HTTP {response.status})")
    except Exception as e:
        print_error(f"Status check error: {str(e)}")


async def test_get_build_logs():
    """Test Step 6: Get Build Logs (Polling Mode)"""
    print_header("Step 6: Get Build Logs (Polling Mode)")
    
    template_id_file = Path("/tmp/hopx_test_template_id_minimal_py.txt")
    if not template_id_file.exists():
        print_warning("No template ID found, skipping logs check")
        return
    
    template_id = template_id_file.read_text().strip()
    print_step(f"Fetching logs for template: {template_id}")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/v1/templates/build/{template_id}/logs?offset=0",
                headers={"Authorization": f"Bearer {API_KEY}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print_success("Build logs retrieved")
                    logs = data.get("logs", "")
                    print(f"  Log lines: {len(logs.splitlines())}")
                    print(f"  Status: {data.get('status', 'unknown')}")
                    print(f"  Complete: {data.get('complete', False)}")
                else:
                    print_error(f"Failed to get build logs (HTTP {response.status})")
    except Exception as e:
        print_error(f"Logs check error: {str(e)}")


async def test_list_templates():
    """Test Step 7: List Templates"""
    print_header("Step 7: List Templates")
    
    print_step("Listing all templates")
    
    try:
        templates = Sandbox.list_templates(api_key=API_KEY, base_url=API_BASE_URL)
        print_success("Templates listed")
        print_success(f"Found {len(templates)} templates")
        
        # Show our test templates
        for template in templates:
            if TEST_TEMPLATE_NAME in template.name:
                print(f"  - {template.name} (ID: {template.id})")
        
    except Exception as e:
        print_error(f"Failed to list templates: {str(e)}")


def cleanup():
    """Cleanup temporary files"""
    print_header("Cleanup")
    
    print_step("Cleaning up temporary files")
    for file in Path("/tmp").glob("hopx_test_template_id_*_py.txt"):
        file.unlink()
    print_success("Cleanup complete")


async def main():
    """Main test flow"""
    print()
    print(f"{GREEN}╔════════════════════════════════════════════════════════════════╗{NC}")
    print(f"{GREEN}║     HOPX Python SDK - Template Building Flow Test             ║{NC}")
    print(f"{GREEN}╚════════════════════════════════════════════════════════════════╝{NC}")
    print()
    print(f"{CYAN}API Base URL: {NC}{API_BASE_URL}")
    print(f"{CYAN}Test Template: {NC}{TEST_TEMPLATE_NAME}")
    print()
    
    # Run all tests
    check_api_key()
    
    await test_upload_files()
    await test_build_template_minimal()
    await test_build_template_full()
    await test_build_template_with_copy()
    await test_build_ubuntu_with_apt()
    await test_build_nodejs_template()
    
    await test_validation_errors()
    await test_update_template()
    
    await asyncio.sleep(2)  # Give build a moment to start
    
    await test_get_build_status()
    await test_get_build_logs()
    await test_list_templates()
    
    cleanup()
    
    # Summary
    print_header("Test Summary")
    print(f"{GREEN}Passed: {test_results['passed']}{NC}")
    print(f"{RED}Failed: {test_results['failed']}{NC}")
    print(f"{YELLOW}Warnings: {test_results['warnings']}{NC}")
    print()
    
    if test_results['failed'] == 0:
        print_success("All tests completed successfully!")
    else:
        print_error(f"{test_results['failed']} tests failed")
    
    print()
    print("Next steps:")
    print("  1. Check template build status in NodeMgr logs")
    print("  2. Verify templates in database")
    print("  3. Test VM creation with built templates")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Fatal error: {str(e)}{NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

