"""
Command module for copy_env operations.
Integrates heavily with utilities.file_utils.copy_env_keys_only
"""
import argparse
from utilities.file_utils import copy_env_keys_only

def handle_copy_env(args: argparse.Namespace) -> None:
    """
    Handler function for the `copy_env` command.
    
    Args:
        args: Parsed command-line arguments.
    """
    try:
        copy_env_keys_only(args.source, args.destination, with_values=args.with_values)
        print(f"Successfully copied environment keys from '{args.source}' to '{args.destination}'.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def register_command(subparsers: argparse._SubParsersAction) -> None:
    """
    Register the `copy_env` command with the CLI parser.
    
    Args:
        subparsers: The argparse subparsers action provided by the loader.
    """
    # Create the parser for the "copy_env" command
    parser = subparsers.add_parser(
        "copy_env",
        help="Copy only the variable keys from a .env file to a new destination file."
    )
    
    # Define arguments for this command
    parser.add_argument(
        "source",
        type=str,
        help="The path to the source .env file."
    )
    
    parser.add_argument(
        "destination",
        type=str,
        help="The path to the destination file."
    )
    
    parser.add_argument(
        "--with-values",
        action="store_true",
        help="Copy both the keys and their values."
    )
    
    # Attach the handler function to execute when this command is called
    parser.set_defaults(func=handle_copy_env)

