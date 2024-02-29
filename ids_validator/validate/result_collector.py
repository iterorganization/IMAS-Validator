"""
This file describes the data class for successes and failures of the
validation tool
"""

import traceback
from typing import Any, Dict, List, Tuple

from imaspy.ids_primitive import IDSPrimitive

from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.ids_wrapper import IDSWrapper
from ids_validator.validate.result import IDSValidationResult


class ResultCollector:
    """Class for storing IDSValidationResult objects"""

    def __init__(self) -> None:
        """Initialize ResultCollector"""
        self.results: List[IDSValidationResult] = []

    def set_context(self, rule: IDSValidationRule, idss: List[Tuple[str, int]]) -> None:
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
        nodes_dict: Dict = {}
        result = IDSValidationResult(
            False,
            "",
            self._current_rule,
            self._current_idss,
            tb,
            nodes_dict,
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
        if isinstance(test, IDSWrapper):
            nodes_dict = self.create_nodes_dict(test._nodes_list)
        else:
            nodes_dict = {}
        # pop last stack frame so that new last frame is inside validation test
        tb.pop()
        result = IDSValidationResult(
            bool(test),
            msg,
            self._current_rule,
            self._current_idss,
            tb,
            nodes_dict,
            exc=None,
        )
        self.results.append(result)

    def create_nodes_dict(
        self, nodes_list: List[IDSPrimitive]
    ) -> Dict[Tuple[str, int], List[str]]:
        result: Dict[Tuple[str, int], List[str]] = {
            key: [] for key in self._current_idss
        }
        occ_dict = {key[0]: key for key in self._current_idss}
        print(occ_dict)
        print(nodes_list)
        for node in nodes_list:
            ids_name = node._toplevel.metadata.name
            if node._path not in result[occ_dict[ids_name]]:
                result[occ_dict[ids_name]].append(node._path)
        return result
