import argparse
from abc import abstractmethod
from typing import List

from ids_validator.validate.result import IDSValidationResult

from .command_interface import (
    CommandInterface,
    CommandNotExecutedException,
    RulesetNotImplementedException,
)


class GenericCommand(CommandInterface):

    @property
    def result(self) -> List[IDSValidationResult]:
        if not self._result and self.executed():
            raise RulesetNotImplementedException("All rulesets are not implemented")

        elif not self.executed():
            additional_info = str(self)
            raise CommandNotExecutedException(
                f"Cannot collect result of command that was not executed.\n"
                f"Additional info: {additional_info}"
            )

        return self._result

    def __init__(self, args: argparse.Namespace) -> None:
        self._executed = False
        self._result: List[IDSValidationResult] = []

    @abstractmethod
    def __str__(self) -> str:
        """
        Cast class instance to string.
        :return:
            String in format:
             COMMAND <argument1_name>=<argument1_value> ...
                 ... <argumentN_name>=<argumentN_value>
        """

    def executed(self) -> bool:
        return self._executed

    def execute(self) -> None:
        self._executed = True
