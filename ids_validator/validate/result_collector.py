"""
This file describes the data class for successes and failures of the
validation tool
"""

import traceback
from typing import Any, List, Tuple

from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.result import IDSValidationResult


class ResultCollector:
    """Class for storing IDSValidationResult objects"""

    def __init__(self) -> None:
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

    def add_error_result(self, exc: Exception) -> None:
        """Add result after an exception was encountered in the rule

        Args:
            exc: Exception that was encountered while running validation test
        """
        tb = traceback.extract_tb(exc.__traceback__)
        frame_idx = -1
        assert tb[frame_idx].name == self._current_rule.func.__name__
        result = IDSValidationResult(
            False,
            "",
            self._current_rule,
            self._current_idss,
            tb,
            frame_idx,
            exc=exc,
        )
        self.results.append(result)

    def assert_(self, test: Any, msg: str = "") -> None:
        """
        Custom assert function with which to overwrite assert statements in IDS
        validation tests

        Args:
            test: Expression to evaluate in test
            msg: Given message for failed assertion
        """
        tb = traceback.extract_stack()
        frame_idx = -2
        assert tb[frame_idx + 1].name == "assert_"
        assert tb[frame_idx].name == self._current_rule.func.__name__
        result = IDSValidationResult(
            bool(test),
            msg,
            self._current_rule,
            self._current_idss,
            tb,
            frame_idx,
            exc=None,
        )
        self.results.append(result)
