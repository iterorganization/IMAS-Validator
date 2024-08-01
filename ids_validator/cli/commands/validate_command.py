import argparse
import logging
from pathlib import Path

from ids_validator.common.utils import (
    flatten_2d_list_or_return_empty,
    get_all_ids_names,
)
from ids_validator.validate.validate import validate
from ids_validator.validate_options import ValidateOptions

from .command_generic import GenericCommand


class ValidateCommand(GenericCommand):
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self, args: argparse.Namespace) -> None:
        super(ValidateCommand, self).__init__(args)
        self.uri = args.uri[0]
        self.validate_options = ValidateOptions(
            rulesets=flatten_2d_list_or_return_empty(args.ruleset),
            extra_rule_dirs=[
                Path(element)
                for element in flatten_2d_list_or_return_empty(args.extra_rule_dirs)
            ],
            apply_generic=args.no_generic,
            use_pdb=args.debug,
            use_bundled_rulesets=not args.no_bundled,  # invert logic
        )

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

    def execute(self) -> None:
        super().execute()
        self._result = validate(
            imas_uri=self.uri, validate_options=self.validate_options
        )

    def __str__(self) -> str:
        return f"VALIDATE URI={self.uri} VALIDATE_OPTIONS={self.validate_options}"
