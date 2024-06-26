import argparse
import logging
from pathlib import Path

from ids_validator.validate.explore import explore
from ids_validator.validate_options import ValidateOptions

from .command_generic import GenericCommand


class ExploreCommand(GenericCommand):
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self, args: argparse.Namespace) -> None:
        super(ExploreCommand, self).__init__(args)
        self.validate_options = ValidateOptions(
            # List comprehension for flattening 2D list into 1D.
            # CLI After providing -r option passes this argument as [['ruleset' ...]]
            rulesets=[
                ruleset for given_rulesets in args.ruleset for ruleset in given_rulesets
            ],
            # List comprehension for flattening 2D list into 1D.
            # CLI After providing -r option passes this argument as [['ruleset' ...]]
            # If empty return empty list
            extra_rule_dirs=(
                [
                    Path(extra_ruleset)
                    for given_extra_rulesets in args.extra_rule_dirs
                    for extra_ruleset in given_extra_rulesets
                ]
                if args.extra_rule_dirs
                else []
            ),
        )
        self.show_empty = args.empty
        self.docstring_level = args.verbose

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
