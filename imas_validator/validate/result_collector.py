"""
This file describes the data class for successes and failures of the
validation tool
"""

import logging
import sys
import traceback
from types import FrameType
from typing import Any, Dict, Iterator, List, Optional, Tuple

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


def _iter_filled_paths(
    node: imas.ids_structure.IDSStructure, prefix: str = ""
) -> Iterator[str]:
    """Yield filled leaf paths relative to the IDS root.

    Carry the path down the tree so AoS indices are obtained once by enumeration,
    rather than repeatedly searching parent arrays through ``node._path``.
    ``iter_nonempty_`` retains the rejection of lazy-loaded IDSs: their unloaded
    nodes must not be silently omitted from coverage.
    """
    for child in node.iter_nonempty_():
        path = prefix + child.metadata.name
        if isinstance(child, imas.ids_primitive.IDSPrimitive):
            yield path
        elif isinstance(child, imas.ids_struct_array.IDSStructArray):
            for index, item in enumerate(child):
                yield from _iter_filled_paths(item, f"{path}[{index}]/")
        else:
            yield from _iter_filled_paths(child, path + "/")


def _extract_stack(frame: Optional[FrameType]) -> traceback.StackSummary:
    """Cheap equivalent of ``traceback.extract_stack(frame)``.

    ``traceback.extract_stack`` calls ``linecache.checkcache`` (an ``os.stat``) for
    every file in the stack and reads the source line of every frame. That work is
    wasted for the vast majority of asserts, whose traceback is never displayed.
    The frame summaries created here look up their source line lazily, on first
    access of ``FrameSummary.line``.
    """
    frames = []
    while frame is not None:
        code = frame.f_code
        frames.append(
            traceback.FrameSummary(
                code.co_filename, frame.f_lineno, code.co_name, lookup_line=False
            )
        )
        frame = frame.f_back
    frames.reverse()
    return traceback.StackSummary.from_list(frames)


class _NodePathCache:
    """Memoized equivalent of ``IDSBase._path``.

    ``IDSBase._path`` recomputes the path from the root for every call, and finds
    the index of each AoS element with a linear search through its parent array.
    For large AoS (e.g. GGD objects) this makes path computation quadratic. This
    cache memoizes the path of every node it has seen and builds an index map once
    per AoS, so that computing the paths of all nodes of an IDS is linear.

    Entries are keyed by ``id()`` and keep a reference to the node, so that ids
    cannot be recycled while the cache is alive. The IDS data must not be modified
    while the cache is in use: call :meth:`clear` when switching IDSs.
    """

    def __init__(self) -> None:
        self._paths: Dict[int, Tuple[Any, str]] = {}
        self._aos_indices: Dict[int, Tuple[Any, Dict[int, int]]] = {}

    def clear(self) -> None:
        self._paths.clear()
        self._aos_indices.clear()

    def path(self, node: Any) -> str:
        entry = self._paths.get(id(node))
        if entry is not None:
            return entry[1]
        if isinstance(node, imas.ids_toplevel.IDSToplevel):
            path = ""
        else:
            parent = node._parent
            parent_path = self.path(parent)
            if isinstance(parent, imas.ids_struct_array.IDSStructArray):
                index = self._aos_index(parent).get(id(node))
                if index is None:
                    # Broken link to parent: let imas handle (and log) this case
                    path = node._path
                else:
                    path = f"{parent_path}[{index}]"
            elif parent_path:
                path = f"{parent_path}/{node.metadata.name}"
            else:
                path = node.metadata.name
        self._paths[id(node)] = (node, path)
        return path

    def _aos_index(self, aos: Any) -> Dict[int, int]:
        entry = self._aos_indices.get(id(aos))
        if entry is None:
            entry = (aos, {id(item): index for index, item in enumerate(aos)})
            self._aos_indices[id(aos)] = entry
        return entry[1]


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
        self._path_cache = _NodePathCache()
        self._current_idss: List[Tuple[imas.ids_toplevel.IDSToplevel, str, int]] = []

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
        # Paths remain valid as long as the same IDS instances are validated
        if [id(ids[0]) for ids in idss] != [id(ids[0]) for ids in self._current_idss]:
            self._path_cache.clear()
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
        # start at the caller, so that the last frame is inside the validation test
        tb = _extract_stack(sys._getframe(1))
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
            ids_result.add(self._path_cache.path(node))
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
                # Only cache a complete traversal, so a failure cannot leave partial
                # coverage that would prevent a later attempt from collecting it.
                self.filled_nodes_dict[key] = set(_iter_filled_paths(ids_instance))

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
