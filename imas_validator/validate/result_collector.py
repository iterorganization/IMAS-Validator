"""
This file describes the data class for successes and failures of the
validation tool
"""

import logging
import traceback
from typing import Any, List, Tuple

try:
    import imaspy as imas  # type: ignore
except ImportError:
    import imas  # type: ignore

from imas_validator.exceptions import InternalValidateDebugException
from imas_validator.rules.data import IDSValidationRule
from imas_validator.validate.ids_wrapper import IDSWrapper
from imas_validator.validate.result import (
    CoverageDict,
    CoverageMap,
    IDSValidationResult,
    IDSValidationResultCollection,
    NodesDict,
)
from imas_validator.validate_options import ValidateOptions

logger = logging.getLogger(__name__)


class ResultCollector:
    """Class for storing IDSValidationResult objects"""

    def __init__(
        self,
        validate_options: ValidateOptions,
        imas_uri: str,
    ) -> None:
        """
        Initialize ResultCollector

        Args:
            validate_options: Dataclass for validate options
        """
        self.results: List[IDSValidationResult] = []
        self.validate_options = validate_options
        self.imas_uri = imas_uri
        self.visited_nodes_dict: NodesDict = {}
        self.filled_nodes_dict: NodesDict = {}

    def set_context(
        self,
        rule: IDSValidationRule,
        idss: List[Tuple[imas.ids_toplevel.IDSToplevel, str, int]],
    ) -> None:
        """Set which rule and IDSs should be stored in results

        Args:
            rule: Rule to apply to IDS data
            idss: Tuple of ids_instances, ids_names and occurrences
        """
        unique_ids_names = set(ids[1] for ids in idss)
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
            [(x[1], x[2]) for x in self._current_idss],
            tb,
            {},
            exc=exc,
        )
        self.results.append(result)
        self.append_nodes_dict({}, self._current_idss)

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
            [(x[1], x[2]) for x in self._current_idss],
            tb,
            nodes_dict,
            exc=None,
        )
        self.results.append(result)
        if self.validate_options.track_node_dict:
            self.append_nodes_dict(nodes_dict, self._current_idss)
        # raise exception for debugging traceback
        if self.validate_options.use_pdb and not res_bool:
            raise InternalValidateDebugException()

    def create_nodes_dict(
        self, ids_nodes: List[imas.ids_primitive.IDSPrimitive]
    ) -> NodesDict:
        """
        Create dict with list of touched nodes for the IDSValidationResult object

        Args:
            ids_nodes: List of IDSPrimitive nodes that have been touched in this test
        """
        nodes_dict: NodesDict = {
            (name, occ): set() for _, name, occ in self._current_idss
        }
        occ_dict = {name: (name, occ) for _, name, occ in self._current_idss}
        for node in ids_nodes:
            ids_name = node._toplevel.metadata.name
            ids_result = nodes_dict[occ_dict[ids_name]]
            ids_result.add(node._path)
        return nodes_dict

    def append_nodes_dict(
        self,
        nodes_dict: NodesDict,
        idss: List[Tuple[imas.ids_toplevel.IDSToplevel, str, int]],
    ) -> None:
        """
        Add touched nodes and filled nodes to nodes_dicts during assert

        Args:
            nodes_dict: dict of touched nodes during validation process
            idss: Tuple of ids_instances, ids_names and occurrences
        """
        for key, value in nodes_dict.items():
            if key not in self.visited_nodes_dict.keys():
                self.visited_nodes_dict[key] = set()
            self.visited_nodes_dict[key] |= value
        for ids_instance, name, occ in idss:
            key = (name, occ)
            if key not in self.filled_nodes_dict.keys():
                self.filled_nodes_dict[key] = set()
                imas.util.visit_children(
                    lambda node: self.filled_nodes_dict[key].add(node._path),
                    ids_instance,
                    leaf_only=True,
                    visit_empty=False,
                )

    def coverage_dict(self) -> CoverageDict:
        """
        Return a dictionary of IDSs showing how many nodes per IDS are covered in
        different categories
        """
        coverage_dict: CoverageDict = {}
        visited_nodes_dict = self.visited_nodes_dict
        filled_nodes_dict = self.filled_nodes_dict
        for key in filled_nodes_dict.keys():
            if key not in self.visited_nodes_dict.keys():
                self.visited_nodes_dict[key] = set()
            filled = filled_nodes_dict[key]
            visited = visited_nodes_dict[key]
            coverage_dict[key] = CoverageMap(
                filled=len(filled),
                visited=len(visited),
                overlap=len(visited & filled),
            )
        return coverage_dict

    def result_collection(self) -> IDSValidationResultCollection:
        """
        Return object detailing the final results of validation process
        """
        return IDSValidationResultCollection(
            results=self.results,
            coverage_dict=self.coverage_dict(),
            validate_options=self.validate_options,
            imas_uri=self.imas_uri,
        )
