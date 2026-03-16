"""
Balance Management System - Main Entry Point

A system for managing third-party service balances and usage.
"""

__version__ = "1.0.0"
__author__ = "Balance Manager Team"


def main():
    """Main entry point."""
    from src.cli.main import cli
    cli()


if __name__ == "__main__":
    main()
