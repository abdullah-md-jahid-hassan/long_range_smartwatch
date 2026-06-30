"""
Dynamic command loader for the CLI system.
Scans the `commands` directory and registers available commands.
"""
import os
import importlib
import argparse
import pkgutil
from typing import Any

from . import commands

def load_commands(subparsers: argparse._SubParsersAction) -> None:
    """
    Dynamically load all command modules from the `commands` package.
    
    Args:
        subparsers: The argparse subparsers action to which commands are registered.
    """
    # Get the directory where the commands package is located
    package_path = os.path.dirname(commands.__file__)
    
    # Iterate through all modules in the commands directory
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        # Import the module dynamically
        full_module_name = f"{commands.__name__}.{module_name}"
        try:
            module = importlib.import_module(full_module_name)
            
            # Look for the register_command function in the module
            if hasattr(module, "register_command"):
                register_func = getattr(module, "register_command")
                if callable(register_func):
                    register_func(subparsers)
        except Exception as e:
            # In a production system, this could log the error instead of printing
            print(f"Warning: Failed to load command module '{module_name}': {e}")
