"""
This file describes the data class for successes and failures of the
validation tool
"""

from typing import List
from ids_validator.validate.result import IDSValidationResult


class ResultCollector:
    """"""

    def __init__(self):
        self.results: List[IDSValidationResult] = []

    def set_context(self, rule, idss):
        self._current_rule = rule
        self._current_idss = idss

    def add_error_result(self, error):
        result = IDSValidationResult(
            False,
            "",
            self._current_rule,
            self._current_idss,
            error=error,
        )
        self.results.append(result)

    def assert_(self, test, msg=""):
        result = IDSValidationResult(
            test,
            msg,
            self._current_rule,
            self._current_idss,
        )
        self.results.append(result)
