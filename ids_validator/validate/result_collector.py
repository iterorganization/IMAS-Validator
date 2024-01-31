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

    def set_context(self, rule, ids_names, ids_occurrences):
        self._current_rule = rule
        self._current_ids_names = ids_names
        self._current_ids_occurrences = ids_occurrences

    def assert_(self, test, msg=""):
        result = IDSValidationResult(
            test,
            msg,
            self._current_rule,
            self._current_ids_names,
            self._current_ids_occurrences,
        )
        self.results.append(result)
