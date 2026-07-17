"""
Utilities for terminal command execution.
"""
import subprocess
from .system_utils import detect_os

def run_command(command_linux: str, command_windows: str) -> str:
    """
    Run a terminal command depending on the detected OS.
    
    Args:
        command_linux (str): Command to run if OS is Linux.
        command_windows (str): Command to run if OS is Windows.
        
    Returns:
        str: Standard output from the executed command.
        
    Raises:
        RuntimeError: If the operating system is unsupported.
        subprocess.CalledProcessError: If the command fails execution.
    """
    # Detect OS using system_utils
    os_type = detect_os()
    
    # Select command based on OS Type
    if os_type == "windows":
        cmd_to_run = command_windows
    else:
        cmd_to_run = command_linux
        
    # Use subprocess module safely
    # check=True raises CalledProcessError if the command fails
    result = subprocess.run(
        cmd_to_run,
        shell=True,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    
    return result.stdout
