import argparse
import logging
from pathlib import Path

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
            rulesets=args.ruleset,
            extra_rule_dirs=(
                [Path(args.extra_rule_dirs)] if args.extra_rule_dirs else []
            ),
            apply_generic=args.generic,
            use_pdb=args.debug,
        )

    def execute(self) -> None:
        super().execute()
        self._result = validate(
            imas_uri=self.uri, validate_options=self.validate_options
        )

    def __str__(self) -> str:
        return f"VALIDATE URI={self.uri} VALIDATE_OPTIONS={self.validate_options}"
