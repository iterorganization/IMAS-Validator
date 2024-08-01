"""
This file describes the data class for successes and failures of the
validation tool
"""

import logging
import traceback
from typing import Any, Dict, List, Set, Tuple

import imaspy.util
from imaspy import DBEntry
from imaspy.ids_primitive import IDSPrimitive

from ids_validator.exceptions import InternalValidateDebugException
from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.ids_wrapper import IDSWrapper
from ids_validator.validate.result import IDSValidationResult
from ids_validator.validate_options import ValidateOptions

logger = logging.getLogger(__name__)
NODES_DICT = Dict[Tuple[str, int], Set[str]]


class ResultCollector:
    """Class for storing IDSValidationResult objects"""

    def __init__(
        self,
        validate_options: ValidateOptions,
        db_entry: DBEntry,
    ) -> None:
        """
        Initialize ResultCollector

        Args:
            validate_options: Dataclass for validate options
        """
        self.results: List[IDSValidationResult] = []
        self.validate_options = validate_options
        self.db_entry = db_entry

    def set_context(self, rule: IDSValidationRule, idss: List[Tuple[str, int]]) -> None:
        """Set which rule and IDSs should be stored in results

        Args:
            rule: Rule to apply to IDS data
            idss: Tuple of ids_names and occurrences
        """
        unique_ids_names = set(ids[0] for ids in idss)
        if len(unique_ids_names) != len(idss):
            raise NotImplementedError(
                "Two occurrence of one IDS in a single validation rule is not supported"
            )
        self._current_rule = rule
        self._current_idss = idss

    def add_error_result(self, exc: Exception) -> None:
        """Add result after an exception was encountered in the rule

        Args:
            exc: Exception that was encountered while running validation test
        """
        tb = traceback.extract_tb(exc.__traceback__)
        logger.error(
            f"Exception while executing rule {self._current_rule.name}: '{str(exc)}' "
            f"in {tb[-1].name}:{tb[-1].lineno}. This could be a bug in the rule. See "
            "detailed report for further information."
        )
        result = IDSValidationResult(
            False,
            "",
            self._current_rule,
            self._current_idss,
            tb,
            {},
            exc=exc,
            imas_uri=self.db_entry.uri,
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
        # pop last stack frame so that new last frame is inside validation test
        tb.pop()
        if isinstance(test, IDSWrapper):
            nodes_dict = self.create_nodes_dict(test._ids_nodes)
        else:
            nodes_dict = {}
        res_bool = bool(test)
        result = IDSValidationResult(
            res_bool,
            msg,
            self._current_rule,
            self._current_idss,
            tb,
            nodes_dict,
            exc=None,
            imas_uri=self.db_entry.uri,
        )
        self.results.append(result)
        # raise exception for debugging traceback
        if self.validate_options.use_pdb and not res_bool:
            raise InternalValidateDebugException()

    def create_nodes_dict(self, ids_nodes: List[IDSPrimitive]) -> NODES_DICT:
        """
        Create dict with list of touched nodes for the IDSValidationResult object

        Args:
            ids_nodes: List of IDSPrimitive nodes that have been touched in this test
        """
        nodes_dict: NODES_DICT = {key: set() for key in self._current_idss}
        occ_dict = {key[0]: key for key in self._current_idss}
        for node in ids_nodes:
            ids_name = node._toplevel.metadata.name
            ids_result = nodes_dict[occ_dict[ids_name]]
            ids_result.add(node._path)
        return nodes_dict

    def visited_nodes_dict(self) -> NODES_DICT:
        nodes_dict: NODES_DICT = {}
        for result in self.results:
            for key, value in result.nodes_dict.items():
                if key not in nodes_dict.keys():
                    nodes_dict[key] = set()
                nodes_dict[key] |= value
        return nodes_dict

    def db_entry_nodes_dict(self) -> Tuple[NODES_DICT, NODES_DICT]:
        filled_nodes_dict: NODES_DICT = {}
        total_nodes_dict: NODES_DICT = {}
        for ids_name in self.db_entry.factory.ids_names():
            occurrence_list = self.db_entry.list_all_occurrences(ids_name)
            for occurrence in occurrence_list:
                ids = self.db_entry.get(ids_name, occurrence, autoconvert=False)
                filled_set = set()
                total_set = set()
                imaspy.util.visit_children(
                    lambda x: filled_set.add(x._toplevel.metadata.name),
                    ids,
                    leaf_only=True,
                    visit_empty=False,
                )
                imaspy.util.visit_children(
                    lambda x: total_set.add(x._toplevel.metadata.name),
                    ids,
                    leaf_only=True,
                    visit_empty=True,
                )
                filled_nodes_dict[(ids_name, occurrence)] = filled_set
                total_nodes_dict[(ids_name, occurrence)] = total_set
        return filled_nodes_dict, total_nodes_dict

    def coverage_dict(self) -> Dict[Tuple[str, int], Dict[str, float]]:
        coverage_dict: Dict[Tuple[str, int], Dict[str, float]] = {}
        visited_nodes_dict = self.visited_nodes_dict()
        filled_nodes_dict, total_nodes_dict = self.db_entry_nodes_dict()
        for key in total_nodes_dict.keys():
            filled = filled_nodes_dict[key]
            total = total_nodes_dict[key]
            visited = visited_nodes_dict[key]
            unfilled = total - filled
            coverage_dict[key] = {
                "filled": len(filled & visited) / len(filled),
                "unfilled": len(unfilled & visited) / len(unfilled),
                "total": len(total & visited) / len(total),
            }
        return coverage_dict
