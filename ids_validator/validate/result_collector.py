"""
This file describes the data class for successes and failures of the
validation tool
"""

from typing import List, Tuple, Union

from ids_validator.validate.result import IDSValidationResult
from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.ids_wrapper import IDSWrapper


class ResultCollector:
    """Class for storing IDSValidationResult objects"""

    def __init__(self):
        """Initialize ResultCollector"""
        self.results: List[IDSValidationResult] = []

    def set_context(self, rule: IDSValidationRule, idss: Tuple[Tuple[str, int]]):
        """Set which rule and IDSs should be stored in results

        Args:
            rule: Rule to apply to IDS data
            idss: Tuple of ids_names and occurrences
        """
        self._current_rule = rule
        self._current_idss = idss

    def add_error_result(self, exc: Exception):
        """Add result after an exception was encountered in the rule

        Args:
            exc: Exception that was encountered while running validation test
        """
        result = IDSValidationResult(
            False,
            "",
            self._current_rule,
            self._current_idss,
            exc=exc,
        )
        self.results.append(result)

    def assert_(self, test: Union[IDSWrapper, bool], msg: str = ""):
        """
        Custom assert function with which to overwrite assert statetements in IDS
        validation tests

        Args:
            test: Expression to evaluate in test
            msg: Given message for failed assertion
        """
        result = IDSValidationResult(
            test,
            msg,
            self._current_rule,
            self._current_idss,
        )
        self.results.append(result)
