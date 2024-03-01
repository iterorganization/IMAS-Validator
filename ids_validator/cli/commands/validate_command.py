from ids_validator.validate.validate import validate
from .command_generic import GenericCommand
from pathlib import Path
import logging

class ValidateCommand(GenericCommand):
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self, args):

        self.ruleset = [args.ruleset]
        self.uri = args.uri
        self.extra_rule_dirs = [Path(args.extra_rule_dirs)] if args.extra_rule_dirs else []
        self.apply_generic = args.generic

    def execute(self):
        self._result = validate(self.ruleset, self.uri, self.extra_rule_dirs, self.apply_generic)
        return self._result

    def __str__(self):
        return f'VALIDATE URI={self.uri} RULESET={self.ruleset} EXTRA_RULE_DIRS={self.extra_rule_dirs} APPLY_GENERIC={self.apply_generic}'