#!/usr/bin/env python
import argparse
import sys

from ids_validator.cli.command_parser import CommandParser


def configure_argument_parser() -> argparse.ArgumentParser:
    # Management of input arguments
    parser = argparse.ArgumentParser(description="IDS validator")
    parser.add_argument("-d", "--debug", action="store_true")

    subparsers = parser.add_subparsers(
        dest="command", description="subparsers for command"
    )

    validate_parser = subparsers.add_parser("validate", help="validate command")

    validate_group = validate_parser.add_argument_group("Validator arguments")

    validate_group.add_argument(
        "-u",
        "--uri",
        type=str,
        required=True,
        action="append",
        help="uri for database entree",
    )

    validate_group.add_argument(
        "-r",
        "--ruleset",
        type=str,
        action="append",
        nargs="*",
        default=[],
        help="""Specify with following argument one or more rulesets
                available under RULESET_PATH variable.""",
    )

    validate_group.add_argument(
        "-e",
        "--extra-rule-dirs",
        type=str,
        action="append",
        nargs="*",
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
    return parser


def main() -> None:
    parser = configure_argument_parser()
    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])

    if args.debug:
        print("enable debug option")
    try:
        if args.command.lower() == "validate":
            command_parser = CommandParser()
            print(f"=== TYPE = {type(args)}")
            command_objects = command_parser.parse(args)

            for command in command_objects:
                command.execute()

            # temporary, print command results:
            for command in command_objects:
                print("===========================")
                print(command.result)
                print("===========================\n")
    except AttributeError:
        parser.print_help()


if __name__ == "__main__":
    main()
