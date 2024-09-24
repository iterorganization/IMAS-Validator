#!/usr/bin/env python
import argparse
import os
import sys
from datetime import datetime
from typing import List

from ids_validator.cli.command_parser import CommandParser
from ids_validator.cli.commands.command_interface import CommandNotRecognisedException
from ids_validator.report.validationResultGenerator import (
    SummaryReportGenerator,
    ValidationResultGenerator,
)
from ids_validator.validate.result import IDSValidationResult


def configure_argument_parser() -> argparse.ArgumentParser:
    # Management of input arguments
    parser = argparse.ArgumentParser(description="IDS validator")
    subparsers = parser.add_subparsers(
        dest="command", description="subparsers for command"
    )
    validate_parser = subparsers.add_parser("validate", help="validate IDS")

    validate_group = validate_parser.add_argument_group("Validator arguments")

    validate_group.add_argument(
        "URI",
        type=str,
        nargs="+",
        action="append",
        help="URI for database entry",
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
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="Drop into debugger if tests fails",
    )

    validate_group.add_argument(
        "-o", "--output", help="""Specify report directory path"""
    )

    explore_parser = subparsers.add_parser("explore", help="explore existing rulesets")

    explore_group = explore_parser.add_argument_group("Explore arguments")

    """ Add to existing CLI new group for exclusive arguments """
    explore_group_exclusive = explore_group.add_mutually_exclusive_group()

    explore_group_exclusive.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Display detailed ruleset description",
    )
    explore_group_exclusive.add_argument(
        "--no-docstring",
        action="store_true",
        default=False,
        help="Display limited ruleset description",
    )

    explore_group.add_argument(
        "--show-empty",
        action="store_true",
        default=False,
        help="Whether or not to show empty directories and files",
    )

    explore_group.add_argument(
        "-e",
        "--extra-rule-dirs",
        type=str,
        action="append",
        nargs="+",
        default=[],
        help="""Specify path to your custom ruleset. Subsequent usage of following
                argument will overwrite previous occurrences of the argument""",
    )

    explore_group.add_argument(
        "-r",
        "--ruleset",
        type=str,
        action="append",
        nargs="+",
        default=[],
        help="""Specify with following argument one or more rulesets
                available under RULESET_PATH variable.""",
    )

    # Options common for validate and explore commands
    for group in [validate_group, explore_group]:
        group.add_argument(
            "-b",
            "--no-bundled",
            action="store_true",
            default=False,
            help="Disable rulesets bundled with ids_validator.",
        )

        group.add_argument(
            "-f",
            "--filter",
            type=str,
            action="append",
            nargs="+",
            default=[],
            help="Specify combined list of rule names and ids names"
            " that should be present in rule",
        )

        group.add_argument(
            "--filter_name",
            type=str,
            action="append",
            nargs="+",
            default=[],
            help="Specify list of strings that should be present in rule name",
        )

        group.add_argument(
            "--filter_ids",
            type=str,
            action="append",
            nargs="+",
            default=[],
            help="Specify list of strings that should be present in rule ids names",
        )

    return parser


def main(argv: List) -> None:

    parser = configure_argument_parser()
    args = parser.parse_args(args=argv if argv else ["--help"])

    today = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    reports_path = args.output or "./validate_reports"

    try:
        command_parser = CommandParser()
        command_objects = command_parser.parse(args)
        for command in command_objects:
            command.execute()

        # 'common' means it contains results for all executed commands
        common_result_dict: dict[str, List[IDSValidationResult]] = {}

        for command in command_objects:
            if command.result is not None:
                if command.uri:
                    # save result for summary.html generation
                    common_result_dict[command.uri] = command.result

                    # save result for this URI
                    report_generator = ValidationResultGenerator(
                        command.uri, command.result
                    )
                    report_filename = (
                        f"{reports_path}/{today}/{command.uri.replace('/','|')}"
                    )

                    os.makedirs(os.path.dirname(report_filename), exist_ok=True)
                    report_generator.save_xml(f"{report_filename}.xml")
                    report_generator.save_txt(f"{report_filename}.txt")

        if not common_result_dict:
            return

        summary_filename = f"{reports_path}/{today}/summary.html"
        summary_generator = SummaryReportGenerator(common_result_dict, today)
        summary_generator.save_html(summary_filename, verbose=True)

    except CommandNotRecognisedException:
        parser.print_help()


def execute_cli() -> None:
    argv: List = sys.argv[1:]
    main(argv)


if __name__ == "__main__":
    argv: List = sys.argv[1:]
    main(argv)
