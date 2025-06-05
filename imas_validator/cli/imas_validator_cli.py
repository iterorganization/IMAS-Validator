#!/usr/bin/env python
import argparse
import logging
import os
import sys
from datetime import datetime
from typing import List

from junit2htmlreport.parser import Junit  # type: ignore

from imas_validator.cli.command_parser import CommandParser
from imas_validator.cli.commands.command_interface import CommandNotRecognisedException
from imas_validator.cli.commands.validate_command import ValidateCommand
from imas_validator.report.summaryReportGenerator import SummaryReportGenerator
from imas_validator.report.validationReportGenerator import ValidationReportGenerator
from imas_validator.validate.result import IDSValidationResultCollection

cli_logger = logging.getLogger(__name__)
cli_logger.setLevel(logging.INFO)


def configure_argument_parser() -> argparse.ArgumentParser:
    # Management of input arguments
    parser = argparse.ArgumentParser(
        description="IMAS-Validator",
        epilog="Validate command prints URIs that failed validation on stdout."
        "One can take advantage of this behaviour and pipe validator"
        " calls using xargs command eg.:"
        "imas_validator validate <uri1> <uri2> <uriX> | xargs imas_validator validate",
    )
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
        "-nc",
        "--node-coverage",
        action="store_true",
        default=False,
        help="Track the node coverage for a test",
    )

    validate_group.add_argument(
        "-o", "--output", help="""Specify report directory path"""
    )

    explore_parser = subparsers.add_parser("explore", help="explore existing rulesets")

    explore_group = explore_parser.add_argument_group("Explore arguments")

    """ Add to existing CLI new group for exclusive arguments """
    explore_group_exclusive = explore_group.add_mutually_exclusive_group()

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
            help="Disable rulesets bundled with imas_validator.",
        )
        group.add_argument(
            "--verbose",
            action="store_true",
            default=False,
            help="Display detailed output",
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

    try:
        command_parser = CommandParser()
        command_objects = command_parser.parse(args)

        # command specific actions
        if isinstance(command_objects[0], ValidateCommand):
            reports_path = args.output or "./validate_reports"

        for command in command_objects:
            command.execute()

        # 'common' means it contains results for all executed commands
        common_result_list: List[IDSValidationResultCollection] = []

        for command in command_objects:
            if isinstance(command, ValidateCommand) and command.result is not None:

                common_result_list.append(command.result)

                # save result for this URI
                report_generator = ValidationReportGenerator(command.result)
                report_filename = (
                    f"{reports_path}/{today}/"
                    f"{command.result.imas_uri.replace('/', '|')}"
                )

                os.makedirs(os.path.dirname(report_filename), exist_ok=True)
                report_generator.save_xml(f"{report_filename}.xml")
                report_generator.save_txt(f"{report_filename}.txt")

                # generate detailed html report
                junit_report_parser = Junit(f"{report_filename}.xml")
                html = junit_report_parser.html(show_toc=True)
                with open(f"{report_filename}.html", "wb") as outfile:
                    outfile.write(html.encode("utf-8"))

                # print output
                validation_passed = all(
                    [result.success for result in command.result.results]
                )
                color_red = "[red]"
                color_green = "[green]"
                color_end = "[/]"
                PASSED_FAILED_KEYWORD: str = (
                    f"{color_green}PASSED{color_end}"
                    if validation_passed
                    else f"{color_red}FAILED{color_end}"
                )

                cli_logger.info(
                    f"URI {command.result.imas_uri} has"
                    f" {PASSED_FAILED_KEYWORD} validation."
                )

                # display txt report if set to verbose output
                if args.verbose:
                    cli_logger.info("See detailed report below:")
                    cli_logger.info(
                        f"{color_red}{'-'*50}\n{report_generator.txt}"  # noqa: E226
                    )
                    cli_logger.info(f"{color_red}{'-'*50}")  # noqa: E226

        if not common_result_list:
            return

        if isinstance(command_objects[0], ValidateCommand):
            # generate summary report
            summary_filename = f"{reports_path}/{today}/report.html"
            summary_generator = SummaryReportGenerator(common_result_list, today)
            summary_generator.save_html(summary_filename)
            cli_logger.info(f"Report summary saved as: {summary_filename}")

            # print URIs of failed tests
            failed_test_uris = [
                result_collection.imas_uri
                for result_collection in common_result_list
                if not all([result.success for result in result_collection.results])
            ]
            if failed_test_uris:
                sys.stdout.write(" ".join(failed_test_uris) + "\n")

    except CommandNotRecognisedException:
        parser.print_help()


def execute_cli() -> None:
    argv: List = sys.argv[1:]
    main(argv)


if __name__ == "__main__":
    argv: List = sys.argv[1:]
    main(argv)
