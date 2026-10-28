"""Command line interface for the prompt privacy scrubber."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .polish import DEFAULT_ENDPOINT, DEFAULT_MODEL, polish
from .scrub import scrub


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scrubber",
        description=(
            "Scrub names, phones, emails, and addresses from text before "
            "sending it to an LLM. Optional polishing through a local-first "
            "OpenAI-compatible endpoint (default Ollama)."
        ),
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Input file (default: stdin)",
    )
    parser.add_argument(
        "-i", "--input",
        dest="input_file",
        help="Input file (default: stdin)",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--polish",
        action="store_true",
        help="Polish the scrubbed text through the configured endpoint",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help=f"OpenAI-compatible endpoint URL (default: {DEFAULT_ENDPOINT})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for the endpoint (not stored; Ollama needs none)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress warnings to stderr",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    source = args.input_file or args.file
    if source:
        try:
            with open(source, "r", encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"scrubber: cannot read {source}: {exc}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read()

    result = scrub(text)

    if args.polish:
        result = polish(
            result,
            endpoint=args.endpoint,
            model=args.model,
            api_key=args.api_key,
            quiet=args.quiet,
        )

    if args.output_file:
        try:
            with open(args.output_file, "w", encoding="utf-8") as fh:
                fh.write(result)
        except OSError as exc:
            print(f"scrubber: cannot write {args.output_file}: {exc}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(result)

    return 0
