import argparse
from abc import ABC, abstractmethod
from typing import List

from ids_validator.validate.result import IDSValidationResult


class CommandNotExecutedException(Exception): ...


class RulesetNotImplementedException(Exception): ...


class CommandInterface(ABC):

    @property
    @abstractmethod
    def result(self) -> List[IDSValidationResult]: ...

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
    def executed(self) -> bool:
        """
        Returns True if command was executed, False otherwise
        """
        ...
