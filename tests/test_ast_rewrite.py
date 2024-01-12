import pytest
import unittest.mock

from ids_validator.rules.ast_rewrite import (
    fix_func,
    AssertTransformer,
    FunctionDefTransformer,
)


class wrapperClass:
    def __init__(self, val):
        self.val = val


@pytest.fixture()
def transformer_list():
    return [AssertTransformer(), FunctionDefTransformer()]


@pytest.fixture()
def mock():
    return unittest.mock.Mock()


def func_fix_func():
    x = 2


def test_fix_func(transformer_list):
    code = fix_func(func_fix_func, transformer_list)
    glob = {}
    exec(code, glob)
    assert glob["x"] == 2


def func_wrapperClass_in_target():
    x = wrapperClass(2)


def test_wrapperClass_in_target(transformer_list):
    code = fix_func(func_wrapperClass_in_target, transformer_list)
    glob = {"wrapperClass": wrapperClass}
    exec(code, glob)
    assert glob["x"].val == 2
    assert isinstance(glob["x"], wrapperClass)


def func_rewrite_assert():
    x = 2
    assert x == 2


def test_rewrite_assert(transformer_list, mock):
    code = fix_func(func_rewrite_assert, transformer_list)
    glob = {"assert_": mock}
    exec(code, glob)
    mock.assert_called_with(True)


def func_rewrite_assert_with_msg():
    x = 2
    assert x == 3, "test_string"


def test_rewrite_assert_with_msg(transformer_list, mock):
    code = fix_func(func_rewrite_assert_with_msg, transformer_list)
    glob = {"assert_": mock}
    exec(code, glob)
    mock.assert_called_with(False, "test_string")
