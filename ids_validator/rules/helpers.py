"""
This file describes the helper functions for the validation rules
"""

import operator
from typing import Callable, Iterator, List

from imaspy.ids_base import IDSBase
from imaspy.ids_primitive import IDSPrimitive
from imaspy.util import find_paths, visit_children

from ids_validator.validate.ids_wrapper import IDSWrapper


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
                :py:func:`imaspy.util.find_paths`.

        Kwargs:
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
        self._node: IDSBase = wrapped._obj
        if not isinstance(self._node, IDSBase):
            raise TypeError("First argument of Select must be an IDS node")

        self._matches: List[IDSWrapper] = []
        self._matching_paths = set(find_paths(self._node, self._query))

        # Loop over all elements in self._node, and append matches to self._matches.
        # Note: this is not very efficient when a lot of nodes are filled and only a
        # small number match the query. We can improve performance later if it is a
        # bottleneck.
        visit_children(
            self._visitor, self._node, leaf_only=leaf_only, visit_empty=not has_value
        )

    def _visitor(self, node: IDSBase) -> None:
        """Visitor function used in imaspy.util.visit_children."""
        if node.metadata.path_string in self._matching_paths:
            self._matches.append(IDSWrapper(node))

    def __iter__(self) -> Iterator[IDSWrapper]:
        """Iterate over all children matching the criteria of this Select class."""
        return iter(self._matches)


def Increasing(wrapped: IDSWrapper) -> IDSWrapper:
    """Return whether a given array is increasing

    Args:
        wrapped: IDS toplevel or structure element

    Returns:
        boolean describing whether the array is increasing
    """
    return IDSWrapper(_check_order(wrapped, operator.gt))


def Decreasing(wrapped: IDSWrapper) -> IDSWrapper:
    """Return whether a given array is decreasing

    Args:
        wrapped: IDS toplevel or structure element

    Returns:
        boolean describing whether the array is decreasing
    """
    return IDSWrapper(_check_order(wrapped, operator.lt))


def _check_order(wrapped: IDSWrapper, op: Callable) -> bool:
    if not isinstance(wrapped, IDSWrapper):
        raise TypeError("First argument must be an IDS node")
    node = wrapped._obj
    if not (isinstance(node, IDSPrimitive)):
        raise TypeError("Object must be IDS node")
    if not (node.metadata.ndim == 1 and len(node) > 1):
        raise ValueError("Object must be 1d with len > 1")

    for i in range(len(node) - 1):
        if not op(node[i + 1], node[i]):
            return False
    return True


def Exists() -> None:
    """"""
    pass
