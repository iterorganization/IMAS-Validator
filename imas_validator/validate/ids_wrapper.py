"""
This file describes the overload class for the operators
"""

import operator
from typing import Any, Callable, Collection, Iterator, List, Optional, Tuple

import imas  # type: ignore
import numpy as np


def _binary_wrapper(op: Callable, name: str) -> Callable:
    def func(self: "IDSWrapper", other: Any) -> "IDSWrapper":
        if isinstance(other, IDSWrapper):
            new_nodes = other._ids_nodes
            other = other._obj
        else:
            new_nodes = []
        return IDSWrapper(op(self._obj, other), ids_nodes=self._ids_nodes + new_nodes)

    func.__name__ = f"__{name}__"
    return func


def _reflected_binary_wrapper(op: Callable, name: str) -> Callable:
    def func(self: "IDSWrapper", other: Any) -> "IDSWrapper":
        if isinstance(other, IDSWrapper):
            new_nodes = other._ids_nodes
            other = other._obj
        else:
            new_nodes = []
        return IDSWrapper(op(other, self._obj), ids_nodes=self._ids_nodes + new_nodes)

    func.__name__ = f"__r{name}__"
    return func


def _numeric_wrapper(op: Callable, name: str) -> Tuple[Callable, Callable]:
    return (_binary_wrapper(op, name), _reflected_binary_wrapper(op, name))


def _unary_wrapper(op: Callable, name: str) -> Callable:
    def func(self: "IDSWrapper") -> "IDSWrapper":
        return IDSWrapper(op(self._obj), ids_nodes=self._ids_nodes)

    func.__name__ = f"__{name}__"
    return func


class IDSWrapper:
    """
    Wrapper objects with operator overloads for reporting validation test results
    """

    def __init__(
        self,
        obj: Any,
        *,
        ids_nodes: Optional[List[imas.ids_primitive.IDSPrimitive]] = None,
    ) -> None:
        """Initialize IDSWrapper

        Args:
            obj: Object to be wrapped

        Keyword Args:
            ids_nodes: List of ids nodes the IDSWrapper has touched
        """
        if isinstance(obj, IDSWrapper):
            raise ValueError("Cannot wrap already wrapped object")
        self._obj = obj
        self._ids_nodes = ids_nodes or []
        if isinstance(obj, imas.ids_primitive.IDSPrimitive):
            self._ids_nodes = self._ids_nodes + [obj]

    def __array_ufunc__(
        self, ufunc: Any, method: Any, *args: Any, **kwargs: Any
    ) -> Optional["IDSWrapper"]:
        """Implement numpy protocol for universal functions."""
        # types argument is currently ignored, so pass empty list
        return self.__array_function__(getattr(ufunc, method), [], args, kwargs)

    def __array_function__(
        self, func: Any, types: Collection, args: Any, kwargs: Any
    ) -> Optional["IDSWrapper"]:
        """Implement numpy protocol for public API functions.

        See numpy docs:
        https://numpy.org/doc/stable/user/basics.interoperability.html#operating-on-foreign-objects-without-converting
        https://numpy.org/doc/stable/user/basics.dispatch.html and
        https://numpy.org/doc/stable/reference/arrays.classes.html#special-attributes-and-methods
        """
        # Unpack args:
        unpacked_args = []
        ids_nodes = []
        for value in args:
            if isinstance(value, IDSWrapper):
                ids_nodes.extend(value._ids_nodes)
                value = value._obj
                if isinstance(value, imas.ids_primitive.IDSPrimitive):
                    value = value.value
            unpacked_args.append(value)
        # Pass unpacked inputs to the function:
        result = func(*unpacked_args, **kwargs)
        return None if result is None else IDSWrapper(result, ids_nodes=ids_nodes)

    def __getattr__(self, attr: str) -> "IDSWrapper":
        if not attr.startswith("_"):
            return IDSWrapper(getattr(self._obj, attr), ids_nodes=self._ids_nodes)
        raise AttributeError(f"{self.__class__} object has no attribute {attr}")

    def __call__(self, *args: Any, **kwargs: Any) -> "IDSWrapper":
        return IDSWrapper(self._obj(*args, **kwargs), ids_nodes=self._ids_nodes)

    def __getitem__(self, item: Any) -> "IDSWrapper":
        if isinstance(item, IDSWrapper):
            self._ids_nodes.extend(item._ids_nodes)
        return IDSWrapper(self._obj[item], ids_nodes=self._ids_nodes)

    def __index__(self) -> int:
        return int(self._obj)

    def __repr__(self) -> str:
        return f"IDSWrapper({self._obj!r})"

    def __iter__(self) -> Iterator["IDSWrapper"]:
        for item in self._obj:
            yield IDSWrapper(item, ids_nodes=self._ids_nodes)

    def __str__(self) -> str:
        return str(self._obj)

    def __int__(self) -> int:
        return int(self._obj)

    # comparison operators
    __eq__ = _binary_wrapper(operator.eq, "eq")
    __ne__ = _binary_wrapper(operator.ne, "ne")
    __lt__ = _binary_wrapper(operator.lt, "lt")
    __le__ = _binary_wrapper(operator.le, "le")
    __gt__ = _binary_wrapper(operator.gt, "gt")
    __ge__ = _binary_wrapper(operator.ge, "ge")
    __contains__ = _binary_wrapper(operator.contains, "contains")

    # numeric operators
    __add__, __radd__ = _numeric_wrapper(operator.add, "add")
    __sub__, __rsub__ = _numeric_wrapper(operator.sub, "sub")
    __mul__, __rmul__ = _numeric_wrapper(operator.mul, "mul")
    __matmul__, __rmatmul__ = _numeric_wrapper(operator.matmul, "matmul")
    __truediv__, __rtruediv__ = _numeric_wrapper(operator.truediv, "truediv")
    __floordiv__, __rfloordiv__ = _numeric_wrapper(operator.floordiv, "floordiv")
    __mod__, __rmod__ = _numeric_wrapper(operator.mod, "mod")
    __divmod__, __rdivmod__ = _numeric_wrapper(divmod, "divmod")

    # unary operators
    __neg__ = _unary_wrapper(operator.neg, "neg")
    __pos__ = _unary_wrapper(operator.pos, "pos")
    __abs__ = _unary_wrapper(operator.abs, "abs")
    __invert__ = _unary_wrapper(operator.invert, "invert")

    # len must always return int
    def __len__(self) -> int:
        return len(self._obj)

    # __bool__ must always return bool
    def __bool__(self) -> bool:
        # evaluate bool of np arrays as 'all'
        if isinstance(self._obj, np.ndarray):
            return bool(self._obj.all())
        return bool(self._obj)
