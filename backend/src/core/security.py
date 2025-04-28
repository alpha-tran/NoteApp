import subprocess
import shlex
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)

def secure_subprocess_run(
    command: Union[str, List[str]],
    *,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    timeout: Optional[int] = 60,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """
    Securely execute a subprocess command.
    
    Args:
        command: Command to execute (string or list of arguments)
        cwd: Working directory for the command
        env: Environment variables for the command
        timeout: Timeout in seconds (default: 60)
        check: Whether to raise an exception on non-zero exit code
    
    Returns:
        CompletedProcess instance with command output
    
    Raises:
        subprocess.SubprocessError: If command fails and check=True
        subprocess.TimeoutExpired: If command times out
        ValueError: If command is empty or invalid
    """
    if not command:
        raise ValueError("Command cannot be empty")
    
    # Convert string command to list of arguments
    if isinstance(command, str):
        command = shlex.split(command)
    
    # Validate all arguments are strings
    if not all(isinstance(arg, str) for arg in command):
        raise ValueError("All command arguments must be strings")
    
    try:
        # Run command with security best practices:
        # - shell=False to prevent shell injection
        # - timeout to prevent hanging
        # - check=True to raise on error
        result = subprocess.run(
            command,
            shell=False,  # Prevent shell injection
            cwd=cwd,
            env=env,
            timeout=timeout,
            check=check,
            text=True,
            capture_output=True,
        )
        return result
        
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
        raise
        
    except subprocess.SubprocessError as e:
        logger.error(f"Command failed: {' '.join(command)}")
        logger.error(f"Error: {str(e)}")
        raise 