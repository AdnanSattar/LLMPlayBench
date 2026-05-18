#!/usr/bin/env python
"""
Database management utility script.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_command(command):
    """Run a shell command and log the output."""
    logger.info(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"Command output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return False


def create_migration(message):
    """Create a new migration with the given message."""
    return run_command(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message]
    )


def upgrade_db(revision="head"):
    """Upgrade database to the specified revision (default: head)."""
    return run_command([sys.executable, "-m", "alembic", "upgrade", revision])


def downgrade_db(revision="-1"):
    """Downgrade database by the specified number of revisions (default: -1)."""
    return run_command([sys.executable, "-m", "alembic", "downgrade", revision])


def show_history():
    """Show migration history."""
    return run_command([sys.executable, "-m", "alembic", "history"])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Database management utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create migration
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")

    # Upgrade
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument(
        "--revision", default="head", help="Revision to upgrade to (default: head)"
    )

    # Downgrade
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument(
        "--revision", default="-1", help="Revision to downgrade to (default: -1)"
    )

    # History
    subparsers.add_parser("history", help="Show migration history")

    args = parser.parse_args()

    # Change to the backend directory
    backend_dir = Path(__file__).parent.absolute()

    if args.command == "create":
        create_migration(args.message)
    elif args.command == "upgrade":
        upgrade_db(args.revision)
    elif args.command == "downgrade":
        downgrade_db(args.revision)
    elif args.command == "history":
        show_history()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
