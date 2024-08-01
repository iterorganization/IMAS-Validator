import argparse
import logging
from pathlib import Path

from ids_validator.common.utils import (
    flatten_2d_list_or_return_empty,
    get_all_ids_names,
)
from ids_validator.validate.explore import explore
from ids_validator.validate_options import ValidateOptions

from .command_generic import GenericCommand


class ExploreCommand(GenericCommand):
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self, args: argparse.Namespace) -> None:
        super(ExploreCommand, self).__init__(args)
        self.validate_options = ValidateOptions(
            rulesets=flatten_2d_list_or_return_empty(args.ruleset),
            extra_rule_dirs=[
                Path(element)
                for element in flatten_2d_list_or_return_empty(args.extra_rule_dirs)
            ],
        )

        # prepare --filer, --filter_name and --filter_ids options to be passed
        self.validate_options.rule_filter.name.extend(
            flatten_2d_list_or_return_empty(args.filter_name)
        )
        self.validate_options.rule_filter.ids.extend(
            flatten_2d_list_or_return_empty(args.filter_ids)
        )

        # Filter ids names and ruleset names from combined args.filter parameter:
        filter_ids_names = list(
            set(flatten_2d_list_or_return_empty(args.filter)).intersection(
                get_all_ids_names()
            )
        )
        filter_rule_names = list(
            set(flatten_2d_list_or_return_empty(args.filter)) - set(filter_ids_names)
        )

        self.validate_options.rule_filter.name.extend(filter_rule_names)
        self.validate_options.rule_filter.ids.extend(filter_ids_names)

        self.show_empty = args.show_empty
        self.docstring_level = 1

        if args.no_docstring:
            self.docstring_level = 0

        if args.verbose:
            self.docstring_level = 2

    def execute(self) -> None:
        super().execute()
        explore(
            validate_options=self.validate_options,
            show_empty=self.show_empty,
            docstring_level=self.docstring_level,
        )

    def __str__(self) -> str:
        return f"""Explore rulesets VALIDATE_OPTIONS={self.validate_options}
                    SHOW_EMPTY={self.show_empty}
                    DOCSTRING_LEVEL={self.docstring_level}"""
