"""
This file describes the helper functions for the validation rules
"""

import imas  # type: ignore

import operator
from typing import Any, Callable, Iterator, List

import numpy as np

from imas_validator.validate.ids_wrapper import IDSWrapper

# Make the following helpers available for rule developers:
__all__ = ["Select", "Increasing", "Decreasing", "Approx", "Parent"]


class Select:
    """Select children of an IDS toplevel or structure, based on the given criteria.

    Example:
        .. code-block:: python

            @validator("*")
            def validate_time(ids):
                '''Validate that all non-empty time nodes are strictly increasing'''
                for time_node in Select(ids, '(/|^)time$'):
                    assert Increasing(time_node)
    """

    def __init__(
        self,
        wrapped: IDSWrapper,
        query: str,
        *,
        has_value: bool = True,
        leaf_only: bool = True,
    ) -> None:
        """Construct a Select object.

        Args:
            wrapped: IDS toplevel or structure element
            query: Regular expression to match the paths of child elements to. See also
                :py:func:`imas.util.find_paths`.

        Keyword Args:
            has_value: When True, children without value are not included. Set to False
                to include all child items (including those without a set value).
            leaf_only: When True, only leaf data nodes are included in the selection.
                Set to False to also iterate over Structures and Arrays of Structures.
        """
        self._query = query
        self._has_value = has_value
        self._leaf_only = leaf_only

        if not isinstance(wrapped, IDSWrapper):
            raise TypeError("First argument of Select must be an IDS node")
        self._node: imas.ids_base.IDSBase = wrapped._obj
        if not isinstance(self._node, imas.ids_base.IDSBase):
            raise TypeError("First argument of Select must be an IDS node")

        self._matches: List[IDSWrapper] = []
        self._matching_paths = set(imas.util.find_paths(self._node, self._query))

        # Loop over all elements in self._node, and append matches to self._matches.
        # Note: this is not very efficient when a lot of nodes are filled and only a
        # small number match the query. We can improve performance later if it is a
        # bottleneck.
        imas.util.visit_children(
            self._visitor, self._node, leaf_only=leaf_only, visit_empty=not has_value
        )

    def _visitor(self, node: imas.ids_base.IDSBase) -> None:
        """Visitor function used in imas.util.visit_children."""
        if node.metadata.path_string in self._matching_paths:
            self._matches.append(IDSWrapper(node))

    def __iter__(self) -> Iterator[IDSWrapper]:
        """Iterate over all children matching the criteria of this Select class."""
        return iter(self._matches)


def Increasing(wrapped: IDSWrapper) -> IDSWrapper:
    """Return whether a given array is strictly increasing

    Args:
        wrapped: 1D IDSPrimitive or numpy array
    """
    return _check_order(wrapped, operator.gt)


def Decreasing(wrapped: IDSWrapper) -> IDSWrapper:
    """Return whether a given array is strictly decreasing

    Args:
        wrapped: 1D IDSPrimitive or numpy array
    """
    return _check_order(wrapped, operator.lt)


def _check_order(wrapped: IDSWrapper, op: Callable) -> IDSWrapper:
    if not isinstance(wrapped, IDSWrapper):
        raise TypeError("First argument must be an IDS node")
    node_arr = np.asarray(wrapped._obj)
    if node_arr.ndim != 1:
        raise ValueError(
            f"Expected a 1D array, but {wrapped._obj!r} has {node_arr.ndim} dimensions"
        )

    diff = np.diff(node_arr)
    res = bool(np.all(op(diff, 0)))
    return IDSWrapper(res, ids_nodes=wrapped._ids_nodes.copy())


def Approx(a: Any, b: Any, rtol: float = 1e-5, atol: float = 1e-8) -> IDSWrapper:
    """Return whether a and b are equal within a tolerance

    This method uses :external:py:func:`numpy.allclose` internally. Please check the
    numpy documentation for a detailed explanation of the arguments.

    Args:
        a, b: Inputs to compare
        rtol: Relative tolerance parameter
        atol: Absolute tolerance parameter
    """
    ids_nodes = []
    if isinstance(a, IDSWrapper):
        a_val = a._obj
        ids_nodes += a._ids_nodes
    else:
        a_val = a
    if isinstance(b, IDSWrapper):
        b_val = b._obj
        ids_nodes += b._ids_nodes
    else:
        b_val = b
    res = np.allclose(a_val, b_val, rtol=rtol, atol=atol)
    return IDSWrapper(res, ids_nodes=ids_nodes)


def Parent(wrapped: IDSWrapper, level: int = 1) -> IDSWrapper:
    """Get the parent of an IDS node.

    Will raise an exception when attempting to get the parent of an IDS toplevel node.

    Example:
        .. code-block:: python

            >>> node = core_profiles.profiles_1d[0].ion[1].label
            >>> Parent(node)
            IDSWrapper(<IDSStructure (IDS:core_profiles, profiles_1d[0]/ion[1])>)
            >>> Parent(node, 2)
            IDSWrapper(<IDSStructArray (IDS:core_profiles, profiles_1d[0]/ion with 2 items)>)
            >>> Parent(node, 3)
            IDSWrapper(<IDSStructure (IDS:core_profiles, profiles_1d[0])>)
            >>> Parent(node, 4)
            IDSWrapper(<IDSStructArray (IDS:core_profiles, profiles_1d with 1 items)>)
            >>> Parent(node, 5)
            IDSWrapper(<IDSToplevel (IDS:core_profiles)>)
            >>> Parent(node, 6)
            [...]
            ValueError: Cannot get the parent of <IDSToplevel (IDS:core_profiles)>

    Args:
        wrapped: IDS node
        level: Specify which "level" parent you want. For example, ``level=2`` returns
            the grandparent of the given IDS node.
    """  # noqa: 501
    if not isinstance(wrapped, IDSWrapper):
        raise TypeError("First argument must be an IDS node")
    node = wrapped._obj
    if not isinstance(node, imas.ids_base.IDSBase):
        raise TypeError("First argument must be an IDS node")
    for _ in range(level):
        if isinstance(node, imas.ids_toplevel.IDSToplevel):
            raise ValueError(f"Cannot get the parent of {node!r}")
        node = node._parent
    return IDSWrapper(node)


HELPER_DICT = {helper_name: globals()[helper_name] for helper_name in __all__}
