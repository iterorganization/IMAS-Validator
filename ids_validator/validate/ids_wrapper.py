"""
This file describes the overload class for the operators
"""

from typing import Any
import operator

import numpy as np


def _binary_wrapper(op, name):
    def func(self, other):
        if isinstance(other, IDSWrapper):
            other = other._obj
        return IDSWrapper(op(self._obj, other))

    func.__name__ = f"__{name}__"
    return func


def _reflected_binary_wrapper(op, name):
    def func(self, other):
        if isinstance(other, IDSWrapper):
            other = other._obj
        return IDSWrapper(op(other, self._obj))

    func.__name__ = f"__r{name}__"
    return func


def _numeric_wrapper(op, name):
    return (_binary_wrapper(op, name), _reflected_binary_wrapper(op, name))


def _unary_wrapper(op, name):
    def func(self):
        return IDSWrapper(op(self._obj))

    func.__name__ = f"__{name}__"
    return func


class IDSWrapper:
    """
    Wrapper objects with operator overloads for reporting validation test results
    """

    def __init__(self, obj: Any):
        """Initialize IDSWrapper

        Args:
            obj: Object to be wrapped
        """
        if isinstance(obj, IDSWrapper):
            raise ValueError("Cannot wrap already wrapped object")
        self._obj = obj

    def __getattr__(self, attr: str):
        if not attr.startswith("_"):
            return IDSWrapper(getattr(self._obj, attr))
        raise AttributeError(f"{self.__class__} object has no attribute {attr}")

    def __call__(self, *args, **kwargs):
        return IDSWrapper(self._obj(*args, **kwargs))

    def __getitem__(self, item: Any):
        return IDSWrapper(self._obj[item])

    # comparison operators
    __eq__ = _binary_wrapper(operator.eq, "eq")
    __ne__ = _binary_wrapper(operator.ne, "ne")
    __lt__ = _binary_wrapper(operator.lt, "lt")
    __le__ = _binary_wrapper(operator.le, "le")
    __gt__ = _binary_wrapper(operator.gt, "gt")
    __ge__ = _binary_wrapper(operator.ge, "ge")
    __contains__ = _binary_wrapper(operator.contains, "contains")

    # numeric operators (others follow in different PR)
    __add__, __radd__ = _numeric_wrapper(operator.add, "add")

    # unary operators (others follow in different PR)
    __neg__ = _unary_wrapper(operator.neg, "neg")

    # len must always return int
    def __len__(self) -> int:
        return len(self._obj)

    # __bool__ must always return bool
    def __bool__(self) -> bool:
        # evaluate bool of np arrays as 'all'
        if isinstance(self._obj, np.ndarray):
            return bool(self._obj.all())
        return bool(self._obj)
