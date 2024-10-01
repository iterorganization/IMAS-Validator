import argparse
from abc import ABC, abstractmethod

from ids_validator.validate.result import IDSValidationResultCollection


class CommandNotExecutedException(Exception):
    """
    Exception to be raised when one tries to get not-executed command result
    """

    ...


class CommandNotRecognisedException(Exception):
    """
    Exception to be raised when incorrect command is provided
    """

    ...


class CommandInterface(ABC):

    @property
    @abstractmethod
    def result(self) -> IDSValidationResultCollection: ...

    @property
    def uri(self) -> str:
        """
        ValidateCommand specific property to get validated URI
        """
        return ""

    @uri.setter
    def uri(self, value: str) -> None:
        # URI should be not settable from outside
        ...

    @abstractmethod
    def __init__(self, args: argparse.Namespace) -> None: ...

    @abstractmethod
    def __str__(self) -> str:
        """
        Cast class instance to string.
        :return:
            String in format: COMMAND <argument1_name>=<argument1_value>
                                  ... <argumentN_name>=<argumentN_value>
        """
        ...

    @abstractmethod
    def execute(self) -> None:
        """
        Executes command with stored arguments and fills self._result variable
        """
        ...

    @abstractmethod
    def executed(self) -> bool:
        """
        Returns True if command was executed, False otherwise
        """
        ...
