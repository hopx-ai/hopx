"""
Ready Check Helpers
"""

from .types import ReadyCheck, ReadyCheckType


def wait_for_port(port: int, timeout: int = 30000, interval: int = 2000) -> ReadyCheck:
    """
    Wait for TCP port to be open
    
    Args:
        port: Port number to check
        timeout: Timeout in milliseconds (default: 30000)
        interval: Check interval in milliseconds (default: 2000)
        
    Returns:
        ReadyCheck configuration
    """
    return ReadyCheck(
        type=ReadyCheckType.PORT,
        port=port,
        timeout=timeout,
        interval=interval,
    )


def wait_for_url(url: str, timeout: int = 30000, interval: int = 2000) -> ReadyCheck:
    """
    Wait for HTTP URL to return 200
    
    Args:
        url: URL to check
        timeout: Timeout in milliseconds (default: 30000)
        interval: Check interval in milliseconds (default: 2000)
        
    Returns:
        ReadyCheck configuration
    """
    return ReadyCheck(
        type=ReadyCheckType.URL,
        url=url,
        timeout=timeout,
        interval=interval,
    )


def wait_for_file(path: str, timeout: int = 30000, interval: int = 2000) -> ReadyCheck:
    """
    Wait for file to exist
    
    Args:
        path: File path to check
        timeout: Timeout in milliseconds (default: 30000)
        interval: Check interval in milliseconds (default: 2000)
        
    Returns:
        ReadyCheck configuration
    """
    return ReadyCheck(
        type=ReadyCheckType.FILE,
        path=path,
        timeout=timeout,
        interval=interval,
    )


def wait_for_process(process_name: str, timeout: int = 30000, interval: int = 2000) -> ReadyCheck:
    """
    Wait for process to be running
    
    Args:
        process_name: Process name to check
        timeout: Timeout in milliseconds (default: 30000)
        interval: Check interval in milliseconds (default: 2000)
        
    Returns:
        ReadyCheck configuration
    """
    return ReadyCheck(
        type=ReadyCheckType.PROCESS,
        process_name=process_name,
        timeout=timeout,
        interval=interval,
    )


def wait_for_command(command: str, timeout: int = 30000, interval: int = 2000) -> ReadyCheck:
    """
    Wait for command to exit with code 0
    
    Args:
        command: Command to execute
        timeout: Timeout in milliseconds (default: 30000)
        interval: Check interval in milliseconds (default: 2000)
        
    Returns:
        ReadyCheck configuration
    """
    return ReadyCheck(
        type=ReadyCheckType.COMMAND,
        command=command,
        timeout=timeout,
        interval=interval,
    )

