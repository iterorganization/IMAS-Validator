import pytest
import unittest.mock

from ids_validator.rules.ast_rewrite import rewrite_assert


class wrapperClass:
    def __init__(self, val):
        self.val = val


@pytest.fixture()
def mock():
    return unittest.mock.Mock()


def test_fix_func():
    code = "x = 2"
    new_code = rewrite_assert(code)
    glob = {}
    exec(new_code, glob)
    assert glob["x"] == 2


def test_wrapperClass_in_target():
    code = "x = wrapperClass(2)"
    new_code = rewrite_assert(code)
    glob = {"wrapperClass": wrapperClass}
    exec(new_code, glob)
    assert glob["x"].val == 2
    assert isinstance(glob["x"], wrapperClass)


def test_rewrite_assert(mock):
    code = """
x = 2
assert x == 2
    """
    new_code = rewrite_assert(code)
    glob = {"assert_": mock}
    exec(new_code, glob)
    mock.assert_called_with(True)


def test_rewrite_assert_with_msg(mock):
    code = """
x = 2
assert x == 3, 'test_string'
    """
    new_code = rewrite_assert(code)
    glob = {"assert_": mock}
    exec(new_code, glob)
    mock.assert_called_with(False, "test_string")
