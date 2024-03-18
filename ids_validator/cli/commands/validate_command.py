from ids_validator.validate.validate import validate
from ids_validator.validate_options import ValidateOptions
from .command_generic import GenericCommand
from pathlib import Path
import logging

class ValidateCommand(GenericCommand):
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self, args):
        super(ValidateCommand, self).__init__(args)
        self.uri = args.uri[0]
        self.validate_options = ValidateOptions(
            rulesets = args.ruleset,
            extra_rule_dirs = [Path(args.extra_rule_dirs)] if args.extra_rule_dirs else [],
            apply_generic = args.generic,
            use_pdb = args.debug,
        )

    def execute(self):
        super().execute()
        self._result = validate(imas_uri=self.uri, validate_options=self.validate_options)
        return self._result

    def __str__(self):
        return f'VALIDATE URI={self.uri} VALIDATE_OPTIONS={self.validate_options}'