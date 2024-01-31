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

    def assert_(self, test, msg=""):
        self.results.append(IDSValidationResult(test, msg))
