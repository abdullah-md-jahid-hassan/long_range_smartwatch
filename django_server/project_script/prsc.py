#!/usr/bin/env python3
"""
Entry point for the Project Prompts CLI application (prsc).
Usage: python prsc.py <command> [args]
"""
import sys
import os

# Ensure the package can be imported from root regardless of sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from cli.main import main

if __name__ == "__main__":
    main()
