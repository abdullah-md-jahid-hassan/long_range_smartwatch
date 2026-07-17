# Project Prompts Automation Toolkit

This foundational toolkit provides a cross-platform, modular CLI automation system (`prsc`) designed to run securely across Linux and Windows systems. It operates as the core execution layer for orchestrating dynamic tasks within your project.

## Project Structure

```text
project_prompts/
│
├── cli/
│   ├── __init__.py          # Initializes the CLI module
│   ├── main.py              # Core CLI execution engine utilizing argparse
│   ├── command_loader.py    # Dynamic command auto-discovery and loading interface
│   │
│   └── commands/            # Directory containing all modular CLI commands
│       ├── __init__.py
│       └── copy_env.py      # Implementation for the `copy_env` command handler
│
├── utilities/
│   ├── __init__.py          # Exposes the core utility functions globally
│   ├── system_utils.py      # Functions to detect OS specifics (`detect_os`, `is_windows`, `is_linux`)
│   ├── file_utils.py        # Utilities for safe file manipulation (`copy_env_keys_only`)
│   └── command_utils.py     # Secure logic for OS-dependent terminal command execution (`run_command`)
│
├── prsc.py                  # The primary CLI entry point script
└── README.md                # Project documentation
```

## CLI Architecture & How It Works

The CLI is designed for **extreme modularity and extensibility**. It uses a plugin-styled architecture:

1. **The Entry Point**: When you run `python prsc.py <command>`, the script imports and executes the core CLI engine inside `cli/main.py`.
2. **Dynamic Discovery**: The engine leverages `cli/command_loader.py` to recursively scan the `cli/commands/` directory.
3. **Execution Routing**: For every module it discovers, it dynamically executes the `register_command(subparsers)` function inside that module to attach it to the main `argparse` configuration. This is what makes the CLI dynamic.

### Adding New Commands

**You do not need to modify the core CLI engine when adding new commands.**

To add a new automation task locally:
1. Create a new python file in `cli/commands/`, e.g., `my_script.py`.
2. Inside it, define your core logic and expose the required `register_command` function:

```python
import argparse

def handle_my_command(args: argparse.Namespace) -> None:
    print(f"Running custom command for: {args.target}")

def register_command(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("my_command", help="Description of your task here.")
    parser.add_argument("target", type=str)
    # Map the handler to the parser execution hook
    parser.set_defaults(func=handle_my_command)
```

The CLI engine will automatically pick it up the next time you run `python prsc.py --help`.

---

## Core Utilities Overview

Under the hood, automation commands should rely on isolated, modular, and robust utilities stored in `utilities/`:
1. **System Utilities**: Detects the underlying system environment dynamically (e.g. `detect_os()`).
2. **File Utilities**: Implements clean operations like scrubbing `.env` file credentials dynamically to prevent unsafe leakages (`copy_env_keys_only`). It handles encoding, sanitization, and variable extraction logic safely.
3. **Command Utilities**: Provides a safe wrapper to execute environment-dependent shell commands predictably with full `subprocess` execution checks and stack tracing (`run_command`).

---

## Usage Example

You can run the CLI using the entry script `prsc.py`:

```bash
# Provide a list of all dynamically registered commands
python prsc.py --help

# Example: Copy ONLY the keys from an environment file up to the '=' character
python prsc.py copy_env ./.env.example ./.env

# Example: Copy keys AND exact values (preserving formatting and comments)
python prsc.py copy_env ./.env.example ./.env --with-values
```
