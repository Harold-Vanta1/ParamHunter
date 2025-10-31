#!/usr/bin/env python3
"""
Compatibility wrapper for running ParamHunter as a script.
Preferred usage: install and run `paramhunter` CLI (via pyproject entry point).
"""

from paramhunter.cli import main

if __name__ == "__main__":
    main()
