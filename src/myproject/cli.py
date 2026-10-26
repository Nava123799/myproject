"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from myproject import __version__
from myproject.core import slugify


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the ``myproject`` command."""
    parser = argparse.ArgumentParser(
        prog="myproject",
        description="Convert text into URL-friendly slugs.",
    )
    parser.add_argument("text", nargs="*", help="Text to slugify. Reads stdin when omitted.")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the command-line interface.

    Args:
        argv: Argument list, defaulting to ``sys.argv[1:]``.

    Returns:
        Process exit code.
    """
    args = build_parser().parse_args(argv)

    if args.text:
        print(slugify(" ".join(args.text)))
        return 0

    if sys.stdin is None or sys.stdin.isatty():
        build_parser().print_help(sys.stderr)
        return 2

    for line in sys.stdin:
        stripped = line.strip()
        if stripped:
            print(slugify(stripped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
