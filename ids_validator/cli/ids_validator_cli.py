#!/usr/bin/env python
import argparse
import sys
from typing import List

from ids_validator.cli.command_parser import CommandParser
from ids_validator.cli.commands.command_interface import CommandNotRecognisedException
from ids_validator.rapport.junit_xml_format import create_JUnit_xml


def configure_argument_parser() -> argparse.ArgumentParser:
    # Management of input arguments
    parser = argparse.ArgumentParser(description="IDS validator")
    subparsers = parser.add_subparsers(
        dest="command", description="subparsers for command"
    )
    validate_parser = subparsers.add_parser("validate", help="validate command")

    validate_group = validate_parser.add_argument_group("Validator arguments")

    validate_group.add_argument(
        "URI",
        type=str,
        nargs="+",
        action="append",
        help="uri for database entree",
    )

    validate_group.add_argument(
        "-r",
        "--ruleset",
        type=str,
        action="append",
        nargs="+",
        default=[],
        help="""Specify with following argument one or more rulesets
                available under RULESET_PATH variable.""",
    )

    validate_group.add_argument(
        "-e",
        "--extra-rule-dirs",
        type=str,
        action="append",
        nargs="+",
        default=[],
        help="""Specify path to your custom ruleset. Subsequent usage of following
                argument will overwrite previous occurrences of the argument""",
    )

    validate_group.add_argument(
        "-g",
        "--no-generic",
        action="store_false",
        help="Disable usage of generic ruleset",
    )

    validate_group.add_argument(
        "-d", "--debug", action="store_true", help="drop into debugger if tests fails"
    )

    validate_group.add_argument(
        "--output",
        help="""Specify name of file result"""
    )
    
    return parser


def main(argv: List) -> None:

    parser = configure_argument_parser()
    args = parser.parse_args(args=argv if argv else ["--help"])

    if args.debug:
        print("debug option enabled")
    try:
        command_parser = CommandParser()
        command_objects = command_parser.parse(args)
        for command in command_objects:
            command.execute()

        # temporary, print command results:
        for command in command_objects:
            print("===========================")
            print(command.result)
            print("===========================\n")

        # Create output file
        create_JUnit_xml(command.result, args.output)
    except CommandNotRecognisedException:
        parser.print_help()


def execute_cli() -> None:
    argv: List = sys.argv[1:]
    main(argv)


if __name__ == "__main__":
    argv: List = sys.argv[1:]
    main(argv)
