#!/usr/bin/env python3
"""
Template Building Cookbook - Python

Examples of building custom templates with the Hopx SDK
"""

import os
import asyncio
from hopx_ai import Template, wait_for_port, wait_for_url, wait_for_process
from hopx_ai.template import BuildOptions, CreateVMOptions


# =============================================================================
# Example 1: Simple Python Web App
# =============================================================================

async def example1_python_web_app():
    """Build a Flask web application template"""
    print("Example 1: Python Flask Web App\n")
    
    template = (
        Template()
        .from_python_image("3.11")
        .copy("app/", "/app/")
        .pip_install()  # Installs from requirements.txt
        .set_env("FLASK_APP", "app.py")
        .set_env("FLASK_ENV", "production")
        .set_start_cmd("python /app/app.py", wait_for_port(5000))
    )
    
    result = await Template.build(
        template,
        BuildOptions(
            alias="my-flask-app",
            api_key=os.environ["HOPX_API_KEY"],
            cpu=2,
            memory=2048,
            disk_gb=10,
            on_log=lambda log: print(f"[{log['level']}] {log['message']}"),
            on_progress=lambda p: print(f"Progress: {p}%")
        )
    )
    
    print(f"✅ Template built: {result.template_id}")
    
    # Create VM from template
    vm = await result.create_vm(CreateVMOptions(alias="flask-instance-1"))
    print(f"✅ VM created: {vm.ip}")
    
    # Cleanup
    await vm.delete()


# =============================================================================
# Example 2: Data Science Environment
# =============================================================================

async def example2_data_science():
    """Build a Jupyter notebook environment"""
    print("Example 2: Data Science with Jupyter\n")
    
    template = (
        Template()
        .from_python_image("3.11")
        .pip_install([
            "jupyter",
            "numpy",
            "pandas",
            "matplotlib",
            "scikit-learn",
            "tensorflow"
        ])
        .copy("notebooks/", "/notebooks/")
        .set_env("JUPYTER_TOKEN", "mysecret")
        .set_workdir("/notebooks")
        .set_start_cmd(
            "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root",
            wait_for_port(8888)
        )
    )
    
    result = await Template.build(
        template,
        BuildOptions(
            alias="jupyter-datascience",
            api_key=os.environ["HOPX_API_KEY"],
            cpu=8,
            memory=16384,
            disk_gb=100
        )
    )
    
    print(f"✅ Data science environment: {result.template_id}")


# =============================================================================
# Example 3: Microservices Stack
# =============================================================================

async def example3_microservices():
    """Build a microservices environment"""
    print("Example 3: Microservices Stack\n")
    
    template = (
        Template()
        .from_ubuntu_image("22.04")
        .apt_install(["python3-pip", "redis-server", "nginx"])
        .copy("services/", "/services/")
        .pip_install(["flask", "fastapi", "uvicorn", "redis"])
        .set_env("SERVICE_PORT", "8000")
        .set_env("REDIS_PORT", "6379")
        .set_workdir("/services")
        .set_start_cmd(
            "redis-server --daemonize yes && uvicorn main:app --host 0.0.0.0",
            wait_for_port(8000)
        )
    )
    
    result = await Template.build(
        template,
        BuildOptions(
            alias="microservices-stack",
            api_key=os.environ["HOPX_API_KEY"],
            cpu=4,
            memory=4096,
            disk_gb=30
        )
    )
    
    print(f"✅ Microservices template: {result.template_id}")


# =============================================================================
# Example 4: Development Environment
# =============================================================================

async def example4_dev_environment():
    """Build a complete development environment"""
    print("Example 4: Development Environment\n")
    
    template = (
        Template()
        .from_ubuntu_image("22.04")
        .apt_install([
            "git", "curl", "wget", "vim", "build-essential",
            "python3-pip", "python3-dev"
        ])
        .run_cmd("curl -fsSL https://deb.nodesource.com/setup_18.x | bash -")
        .apt_install(["nodejs"])
        .pip_install(["ipython", "pytest", "black", "mypy"])
        .npm_install(["typescript", "eslint", "prettier"])
        .set_env("EDITOR", "vim")
        .set_workdir("/workspace")
    )
    
    result = await Template.build(
        template,
        BuildOptions(
            alias="dev-environment",
            api_key=os.environ["HOPX_API_KEY"],
            cpu=4,
            memory=8192,
            disk_gb=50
        )
    )
    
    print(f"✅ Dev environment: {result.template_id}")


# =============================================================================
# Example 5: Clone & Build from GitHub
# =============================================================================

async def example5_github_clone():
    """Clone a GitHub repo and build it"""
    print("Example 5: Clone from GitHub\n")
    
    template = (
        Template()
        .from_node_image("18")
        .apt_install(["git"])
        .git_clone("https://github.com/example/repo.git", "/app")
        .set_workdir("/app")
        .npm_install()
        .run_cmd("npm run build")
        .set_env("NODE_ENV", "production")
        .set_start_cmd("npm start", wait_for_port(3000))
    )
    
    result = await Template.build(
        template,
        BuildOptions(
            alias="github-app",
            api_key=os.environ["HOPX_API_KEY"]
        )
    )
    
    print(f"✅ GitHub app template: {result.template_id}")


# =============================================================================
# Example 6: Different Ready Checks
# =============================================================================

async def example6_ready_checks():
    """Demonstrate all ready check types"""
    print("Example 6: Different Ready Check Types\n")
    
    # Port check
    template_port = (
        Template()
        .from_python_image("3.11")
        .pip_install(["flask"])
        .set_start_cmd("flask run", wait_for_port(5000, timeout_seconds=60000))
    )
    
    # URL check
    template_url = (
        Template()
        .from_node_image("18")
        .npm_install(["express"])
        .set_start_cmd(
            "node server.js",
            wait_for_url("http://localhost:3000/health", timeout_seconds=60000)
        )
    )
    
    # Process check
    template_process = (
        Template()
        .from_ubuntu_image("22.04")
        .apt_install(["nginx"])
        .set_start_cmd(
            "nginx -g 'daemon off;'",
            wait_for_process("nginx", timeout_seconds=30000)
        )
    )
    
    print("✅ Defined 3 templates with different ready checks")


# =============================================================================
# Example 7: Resource Optimization
# =============================================================================

async def example7_resource_optimization():
    """Build templates with different resource profiles"""
    print("Example 7: Resource Optimization\n")
    
    # Light template (minimal resources)
    template_light = (
        Template()
        .from_python_image("3.11-slim")
        .pip_install(["flask"])
        .copy("app/", "/app/")
        .set_start_cmd("python /app/app.py", wait_for_port(5000))
    )
    
    result_light = await Template.build(
        template_light,
        BuildOptions(
            alias="light-app",
            api_key=os.environ["HOPX_API_KEY"],
            cpu=1,
            memory=512,
            disk_gb=5
        )
    )
    
    # Heavy template (ML workload)
    template_heavy = (
        Template()
        .from_python_image("3.11")
        .pip_install(["tensorflow", "torch", "transformers"])
        .copy("models/", "/models/")
        .set_start_cmd("python train.py", wait_for_port(8000))
    )
    
    result_heavy = await Template.build(
        template_heavy,
        BuildOptions(
            alias="ml-training",
            api_key=os.environ["HOPX_API_KEY"],
            cpu=16,
            memory=32768,
            disk_gb=200
        )
    )
    
    print(f"✅ Light template: {result_light.template_id}")
    print(f"✅ Heavy template: {result_heavy.template_id}")


# =============================================================================
# Run All Examples
# =============================================================================

async def run_all_examples():
    """Run all cookbook examples"""
    try:
        await example1_python_web_app()
        await example2_data_science()
        await example3_microservices()
        await example4_dev_environment()
        await example5_github_clone()
        await example6_ready_checks()
        await example7_resource_optimization()
        
        print("\n✨ All examples completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_examples())

