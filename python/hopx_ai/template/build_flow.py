"""
Build Flow - Orchestrates the complete build process
"""

import os
import time
import asyncio
import aiohttp
from typing import List, Optional, Set
from dataclasses import dataclass, asdict

from .types import (
    Step,
    StepType,
    BuildOptions,
    BuildResult,
    CreateVMOptions,
    VM,
    UploadLinkResponse,
    BuildResponse,
    BuildStatusResponse,
)
from .file_hasher import FileHasher
from .tar_creator import TarCreator


DEFAULT_BASE_URL = "https://api.hopx.dev"


def _validate_template(template) -> None:
    """Validate template before building"""
    steps = template.get_steps()
    
    if not steps:
        raise ValueError("Template must have at least one step")
    
    # Check for FROM step
    has_from = any(step.type == StepType.FROM for step in steps)
    if not has_from:
        raise ValueError(
            "Template must start with a FROM step.\n"
            "Examples:\n"
            "  .from_ubuntu_image('22.04')\n"
            "  .from_python_image('3.12')\n"
            "  .from_node_image('20')"
        )
    
    # Check for meaningful steps (not just FROM + ENV)
    meaningful_steps = [
        step for step in steps
        if step.type not in [StepType.FROM, StepType.ENV, StepType.WORKDIR, StepType.USER]
    ]
    
    if not meaningful_steps:
        raise ValueError(
            "Template must have at least one build step besides FROM/ENV/WORKDIR/USER.\n"
            "Environment variables can be set when creating a sandbox.\n"
            "Add at least one of:\n"
            "  .run_cmd('...')     - Execute shell command\n"
            "  .apt_install(...)   - Install system packages\n"
            "  .pip_install(...)   - Install Python packages\n"
            "  .npm_install(...)   - Install Node packages\n"
            "  .copy('src', 'dst') - Copy files"
        )


async def build_template(template, options: BuildOptions) -> BuildResult:
    """
    Build a template
    
    Args:
        template: Template instance
        options: Build options
        
    Returns:
        BuildResult with template ID and helpers
    """
    base_url = options.base_url or DEFAULT_BASE_URL
    context_path = options.context_path or os.getcwd()
    
    # Validate template
    _validate_template(template)
    
    # Step 1: Calculate file hashes for COPY steps
    steps_with_hashes = await calculate_step_hashes(
        template.get_steps(), 
        context_path, 
        options
    )
    
    # Step 2: Upload files for COPY steps
    await upload_files(steps_with_hashes, context_path, base_url, options)
    
    # Step 3: Trigger build
    build_response = await trigger_build(
        steps_with_hashes,
        template.get_start_cmd(),
        template.get_ready_check(),
        base_url,
        options,
    )
    
    # Step 4: Stream logs (if callback provided)
    if options.on_log or options.on_progress:
        await stream_logs(build_response.build_id, base_url, options)
    
    # Step 5: Poll status until complete
    final_status = await poll_status(build_response.build_id, base_url, options)
    
    # Status "active" means template is ready
    if final_status.status not in ["active", "success"]:
        raise Exception(f"Build failed: {final_status.error or 'Unknown error'}")
    
    # Step 6: Wait for template to be published (background job: publishing → active)
    # Build is done, but template needs to be published to public API
    template_id = final_status.template_id
    await wait_for_template_active(template_id, base_url, options)
    
    # Calculate duration
    try:
        # Try parsing with timezone first
        from datetime import datetime
        started = datetime.fromisoformat(final_status.started_at.replace('Z', '+00:00'))
        duration = int(time.time() * 1000) - int(started.timestamp() * 1000)
    except Exception:
        # Fallback: use current time
        duration = 0
    
    # Create VM helper function
    async def create_vm_helper(vm_options: CreateVMOptions = None) -> VM:
        return await create_vm_from_template(
            final_status.template_id, 
            base_url, 
            options, 
            vm_options or CreateVMOptions()
        )
    
    # Return result
    return BuildResult(
        build_id=build_response.build_id,
        template_id=final_status.template_id,
        duration=duration,
        _create_vm_func=create_vm_helper,
    )


async def calculate_step_hashes(
    steps: List[Step], 
    context_path: str, 
    options: BuildOptions
) -> List[Step]:
    """Calculate file hashes for COPY steps"""
    hasher = FileHasher()
    result = []
    
    for step in steps:
        if step.type == StepType.COPY:
            src, dest = step.args[0], step.args[1]
            sources = src.split(',')
            
            # Calculate hash for all sources
            hash_value = await hasher.calculate_multi_hash(
                [(s, dest) for s in sources],
                context_path
            )
            
            # Create new step with hash
            new_step = Step(
                type=step.type,
                args=step.args,
                files_hash=hash_value,
                skip_cache=step.skip_cache,
            )
            result.append(new_step)
        else:
            result.append(step)
    
    return result


async def upload_files(
    steps: List[Step],
    context_path: str,
    base_url: str,
    options: BuildOptions,
) -> None:
    """Upload files for COPY steps"""
    tar_creator = TarCreator()
    uploaded_hashes: Set[str] = set()
    
    async with aiohttp.ClientSession() as session:
        for step in steps:
            if step.type == StepType.COPY and step.files_hash:
                # Skip if already uploaded
                if step.files_hash in uploaded_hashes:
                    continue
                
                # Get sources
                src = step.args[0]
                sources = src.split(',')
                
                # Create tar.gz
                tar_result = await tar_creator.create_multi_tar_gz(sources, context_path)
                
                try:
                    # Request upload link
                    upload_link = await get_upload_link(
                        step.files_hash,
                        tar_result.size,
                        base_url,
                        options.api_key,
                        session,
                    )
                    
                    # Upload if not already present
                    if not upload_link.present and upload_link.upload_url:
                        await upload_file(upload_link.upload_url, tar_result, session)
                    
                    uploaded_hashes.add(step.files_hash)
                finally:
                    # Cleanup temporary file
                    tar_result.cleanup()


async def get_upload_link(
    files_hash: str,
    content_length: int,
    base_url: str,
    api_key: str,
    session: aiohttp.ClientSession,
) -> UploadLinkResponse:
    """Get presigned upload URL"""
    async with session.post(
        f"{base_url}/v1/templates/files/upload-link",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "files_hash": files_hash,
            "content_length": content_length,
        },
    ) as response:
        if not response.ok:
            raise Exception(f"Failed to get upload link: {response.status}")
        
        data = await response.json()
        return UploadLinkResponse(**data)


async def upload_file(
    upload_url: str,
    tar_result,
    session: aiohttp.ClientSession,
) -> None:
    """Upload file to R2"""
    with tar_result.open('rb') as f:
        file_content = f.read()
    
    async with session.put(
        upload_url,
        headers={
            "Content-Type": "application/gzip",
            "Content-Length": str(tar_result.size),
        },
        data=file_content,
    ) as response:
        if not response.ok:
            raise Exception(f"Upload failed: {response.status}")


async def trigger_build(
    steps: List[Step],
    start_cmd: Optional[str],
    ready_cmd: Optional[dict],
    base_url: str,
    options: BuildOptions,
) -> BuildResponse:
    """Trigger build"""
    # Convert steps to dict
    steps_dict = []
    for step in steps:
        step_dict = {
            "type": step.type.value,
            "args": step.args,
        }
        if step.files_hash:
            step_dict["filesHash"] = step.files_hash
        if step.skip_cache:
            step_dict["skipCache"] = True
        steps_dict.append(step_dict)
    
    # Convert ready check to dict
    ready_cmd_dict = None
    if ready_cmd:
        ready_cmd_dict = {
            "type": ready_cmd.type.value,
            "timeout": ready_cmd.timeout,
            "interval": ready_cmd.interval,
        }
        if ready_cmd.port:
            ready_cmd_dict["port"] = ready_cmd.port
        if ready_cmd.url:
            ready_cmd_dict["url"] = ready_cmd.url
        if ready_cmd.path:
            ready_cmd_dict["path"] = ready_cmd.path
        if ready_cmd.process_name:
            ready_cmd_dict["processName"] = ready_cmd.process_name
        if ready_cmd.command:
            ready_cmd_dict["command"] = ready_cmd.command
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{base_url}/v1/templates/build",
            headers={
                "Authorization": f"Bearer {options.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "alias": options.alias,
                "steps": steps_dict,
                "startCmd": start_cmd,
                "readyCmd": ready_cmd_dict,
                "cpu": options.cpu,
                "memory": options.memory,
                "diskGB": options.disk_gb,
                "skipCache": options.skip_cache,
            },
        ) as response:
            if not response.ok:
                raise Exception(f"Build trigger failed: {response.status}")
            
            data = await response.json()
            return BuildResponse(**data)


async def stream_logs(
    build_id: str,
    base_url: str,
    options: BuildOptions,
) -> None:
    """Stream logs via polling (offset-based)"""
    offset = 0
    last_progress = -1
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(
                    f"{base_url}/v1/templates/build/{build_id}/logs",
                    params={"offset": offset},
                    headers={
                        "Authorization": f"Bearer {options.api_key}",
                    },
                ) as response:
                    if not response.ok:
                        return  # Stop streaming on error
                    
                    data = await response.json()
                    logs = data.get("logs", "")
                    offset = data.get("offset", offset)
                    status = data.get("status", "unknown")
                    complete = data.get("complete", False)
                    
                    # Output logs line by line
                    if logs and options.on_log:
                        for line in logs.split('\n'):
                            if line.strip():
                                # Extract log level if present
                                level = "INFO"
                                if "❌" in line or "ERROR" in line:
                                    level = "ERROR"
                                elif "✅" in line:
                                    level = "INFO"
                                elif "⚠" in line or "WARN" in line:
                                    level = "WARN"
                                
                                options.on_log({
                                    "level": level,
                                    "message": line,
                                    "timestamp": ""
                                })
                    
                    # Update progress (estimate based on status)
                    if options.on_progress and status == "building":
                        # Simple progress estimation
                        progress = 50  # Building phase
                        if progress != last_progress:
                            options.on_progress(progress)
                            last_progress = progress
                    
                    # Check if complete
                    if complete or status in ["active", "success", "failed"]:
                        if options.on_progress and status in ["active", "success"]:
                            options.on_progress(100)
                        return
                    
                    # Wait before next poll
                    await asyncio.sleep(2)
                    
            except Exception as e:
                # Stop streaming on error
                return


async def poll_status(
    build_id: str,
    base_url: str,
    options: BuildOptions,
    interval_ms: int = 2000,
) -> BuildStatusResponse:
    """Poll build status (building → success/failed)"""
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(
                f"{base_url}/v1/templates/build/{build_id}/status",
                headers={
                    "Authorization": f"Bearer {options.api_key}",
                },
            ) as response:
                if not response.ok:
                    raise Exception(f"Status check failed: {response.status}")
                
                data = await response.json()
                status = BuildStatusResponse(**data)
                
                # Status can be: building, active (success), failed
                if status.status in ["active", "success", "failed"]:
                    return status
                
                # Wait before next poll
                await asyncio.sleep(interval_ms / 1000)


async def wait_for_template_active(
    template_id: str,
    base_url: str,
    options: BuildOptions,
    max_wait_seconds: int = 60,
) -> None:
    """
    Wait for template to be published and active in public API.
    
    After build completes, a background job publishes the template:
    - Build done (success) → publishing → active
    
    This ensures the template is immediately usable after Template.build() returns.
    """
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            try:
                async with session.get(
                    f"{base_url}/v1/templates/{template_id}",
                    headers={
                        "Authorization": f"Bearer {options.api_key}",
                    },
                ) as response:
                    if response.ok:
                        data = await response.json()
                        status = data.get('status', '')
                        
                        if status == 'active':
                            # Template is published and ready!
                            if options.on_log:
                                options.on_log({'message': f'✅ Template published and active (ID: {template_id})'})
                            return
                        elif status == 'failed':
                            raise Exception(f"Template publishing failed")
                        elif status in ['building', 'publishing']:
                            # Still processing, wait more
                            if options.on_log:
                                options.on_log({'message': f'⏳ Template status: {status}, waiting for active...'})
                    
            except Exception as e:
                # Template might not be visible yet, continue waiting
                pass
            
            await asyncio.sleep(2)  # Check every 2 seconds
        
        # Timeout - but don't fail, template might still become active later
        if options.on_log:
            options.on_log({'message': f'⚠️  Template not yet active after {max_wait_seconds}s, but build succeeded'})


async def get_logs(
    build_id: str,
    api_key: str,
    offset: int = 0,
    base_url: str = None,
) -> "LogsResponse":
    """
    Get build logs with offset-based polling
    
    Args:
        build_id: Build ID
        api_key: API key
        offset: Starting offset (default: 0)
        base_url: Base URL (default: https://api.hopx.dev)
        
    Returns:
        LogsResponse with logs, offset, status, complete
        
    Example:
        ```python
        from hopx_ai.template import get_logs
        
        # Get logs from beginning
        response = await get_logs("123", "api_key")
        print(response.logs)
        
        # Get new logs from last offset
        response = await get_logs("123", "api_key", offset=response.offset)
        ```
    """
    from .types import LogsResponse
    
    if base_url is None:
        base_url = DEFAULT_BASE_URL
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{base_url}/v1/templates/build/{build_id}/logs",
            params={"offset": offset},
            headers={
                "Authorization": f"Bearer {api_key}",
            },
        ) as response:
            if not response.ok:
                raise Exception(f"Get logs failed: {response.status}")
            
            data = await response.json()
            return LogsResponse(
                logs=data.get("logs", ""),
                offset=data.get("offset", 0),
                status=data.get("status", "unknown"),
                complete=data.get("complete", False),
                request_id=data.get("request_id"),
            )


async def create_vm_from_template(
    template_id: str,
    base_url: str,
    build_options: BuildOptions,
    vm_options: CreateVMOptions,
) -> VM:
    """Create sandbox from template using Sandbox.create() API"""
    from ..async_sandbox import AsyncSandbox
    
    # Create sandbox with template ID
    sandbox = await AsyncSandbox.create(
        template_id=template_id,
        api_key=build_options.api_key,
        base_url=base_url,
        env_vars=vm_options.env_vars,
        timeout_seconds=None,  # No timeout by default
    )
    
    # Get sandbox info for VM-like interface
    info = await sandbox.get_info()
    
    # Create delete function
    async def delete_func():
        await sandbox.kill()
    
    # Return VM-like interface for backward compatibility
    return VM(
        vm_id=sandbox.sandbox_id,
        template_id=info.template_id or template_id,
        status=info.status,
        ip=info.public_host.split("://")[1] if "://" in info.public_host else info.public_host,
        agent_url=info.public_host,
        started_at=info.created_at,
        _delete_func=delete_func,
    )

