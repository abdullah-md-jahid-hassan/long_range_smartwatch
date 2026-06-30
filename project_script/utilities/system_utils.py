"""
Utilities for operating system detection.
"""
import platform

def detect_os() -> str:
    """
    Detect the current operating system.
    
    Returns:
        str: "windows" if running on Windows, "linux" if running on Linux.
        
    Raises:
        RuntimeError: If the operating system is not supported.
    """
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

def is_windows() -> bool:
    """
    Check if the current operating system is Windows.
    
    Returns:
        bool: True if OS is Windows, False otherwise.
    """
    try:
        return detect_os() == "windows"
    except RuntimeError:
        return False

def is_linux() -> bool:
    """
    Check if the current operating system is Linux.
    
    Returns:
        bool: True if OS is Linux, False otherwise.
    """
    try:
        return detect_os() == "linux"
    except RuntimeError:
        return False
