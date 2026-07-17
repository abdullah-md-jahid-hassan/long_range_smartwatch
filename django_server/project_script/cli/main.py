"""
Main CLI execution engine.
Sets up the argument parser and triggers command execution.
"""
import argparse
import sys
from .command_loader import load_commands

def main() -> None:
    """
    Entry point for the CLI. Sets up arg parsing and executes commands.
    """
    parser = argparse.ArgumentParser(
        prog="prsc",
        description="Production-grade cross-platform CLI automation toolkit."
    )
    
    # Create subparsers for dynamically loaded commands
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Available commands"
    )
    
    # Dynamically load all available commands
    load_commands(subparsers)
    
    # Parse the arguments provided by the user
    args = parser.parse_args()
    
    # Route to the appropriate command handler based on user input
    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:
            print(f"Error executing command: {e}")
            sys.exit(1)
    else:
        # If no command or an invalid command was passed, show help
        parser.print_help()
        sys.exit(1)
        
if __name__ == "__main__":
    main()
