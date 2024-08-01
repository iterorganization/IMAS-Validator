import argparse
from abc import abstractmethod

from ids_validator.validate.result import IDSValidationResultCollection

from .command_interface import CommandInterface, CommandNotExecutedException


class GenericCommand(CommandInterface):

    _result: IDSValidationResultCollection

    @property
    def result(self) -> IDSValidationResultCollection:
        if not self.executed():
            additional_info = str(self)
            raise CommandNotExecutedException(
                f"Cannot collect result of command that was not executed.\n"
                f"Additional info: {additional_info}"
            )

        return self._result

    def __init__(self, args: argparse.Namespace) -> None:
        self._executed = False

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
