"""Command-line interface for oppwatch."""

import argparse
import logging
import os
import sys

from oppwatch.config import get_env, load_sources
from oppwatch.pipeline import run


def _cmd_run(args: argparse.Namespace) -> None:
    """Execute the pipeline run command."""
    stats = run(dry_run=args.dry_run, only=args.only)
    logging.info("Run completed: %s", stats)


def _cmd_list_sources(_args: argparse.Namespace) -> None:
    """Print each enabled source's name and type."""
    sources = load_sources()
    for src in sources:
        print(f"{src['name']} ({src['type']})")


def _cmd_reset_db(_args: argparse.Namespace) -> None:
    """Prompt user and remove the SQLite database if confirmed."""
    db_path = get_env("DB_PATH", "data/seen.db")
    answer = input("Type YES to delete the database: ")
    if answer == "YES":
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Database deleted.")
        else:
            print("Database file does not exist.")
    else:
        print("Aborted.")


def main() -> None:
    """Parse CLI arguments and route to appropriate command handler."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="oppwatch", description="Weekly Opportunity Watcher")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the watcher pipeline")
    run_parser.add_argument("--dry-run", action="store_true", help="Print digest without marking notified")
    run_parser.add_argument("--only", type=str, default=None, help="Run only the specified source")
    run_parser.set_defaults(func=_cmd_run)

    list_parser = subparsers.add_parser("list-sources", help="List enabled sources")
    list_parser.set_defaults(func=_cmd_list_sources)

    reset_parser = subparsers.add_parser("reset-db", help="Reset the seen opportunities database")
    reset_parser.set_defaults(func=_cmd_reset_db)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
