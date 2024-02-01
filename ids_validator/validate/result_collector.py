"""
This file describes the data class for successes and failures of the
validation tool
"""

from typing import List, Any
from ids_validator.validate.result import IDSValidationResult
from ids_validator.validate.ids_wrapper import IDSWrapper


class ResultCollector:
    """"""

    def __init__(self) -> None:
        self.results: List[IDSValidationResult] = []

    def assert_(self, test: Any, msg: str = "") -> None:
        self.results.append(IDSValidationResult())
