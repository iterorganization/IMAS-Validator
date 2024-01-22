"""
This file describes the overload class for the operators
"""
from typing import Any
import operator


def _binary_wrapper(op, name):
    def func(self, other):
        if isinstance(other, IDSWrapper):
            other = other.value
        return op(self.value, other)

    func.__name__ = f"__{name}__"
    return func


def _reflected_binary_wrapper(op, name):
    def func(self, other):
        if isinstance(other, IDSWrapper):
            other = other.value
        return op(other, self.value)

    func.__name__ = f"__r{name}__"
    return func


def _numeric_wrapper(op, name):
    return (_binary_wrapper(op, name), _reflected_binary_wrapper(op, name))


def _unary_wrapper(op, name):
    def func(self):
        return op(self.value)

    func.__name__ = f"__{name}__"
    return func


class IDSWrapper:
    # how to handle if statements? (asserts?)
    # error on assignment operators
    # ids_primitive for operator list

    def __init__(self, obj: Any):
        # check if value/array/whatever
        self.obj = obj

    def __getattr__(self, attr: Any):
        return IDSWrapper(self.__getattr__(attr))

    def __getitem__(self, item: str):
        return IDSWrapper(self.__getitem__(item))

    __eq__ = _binary_wrapper(operator.eq, "eq")
    __ne__ = _binary_wrapper(operator.ne, "ne")
    __lt__ = _binary_wrapper(operator.lt, "lt")
    __le__ = _binary_wrapper(operator.le, "le")
    __gt__ = _binary_wrapper(operator.gt, "gt")
    __ge__ = _binary_wrapper(operator.ge, "ge")

    __add__, __radd__ = _numeric_wrapper(operator.add, "add")

    __neg__ = _unary_wrapper(operator.neg, "neg")
