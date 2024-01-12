import unittest.mock
from textwrap import dedent

from ids_validator.rules.ast_rewrite import rewrite_assert


class WrapperClass:
    def __init__(self, val):
        self.val = val


def test_rewrite_assert():
    code = "x = 2"
    new_code = rewrite_assert(code, "<string>")
    glob = {}
    exec(new_code, glob)
    assert glob["x"] == 2


def test_wrapperClass_in_target():
    code = "x = wrapperClass(2)"
    new_code = rewrite_assert(code, "<string>")
    glob = {"wrapperClass": WrapperClass}
    exec(new_code, glob)
    assert glob["x"].val == 2
    assert isinstance(glob["x"], WrapperClass)


def test_overwritten_assert():
    code = dedent(
        """\
        x = 2
        assert x == 2
        """
    )
    new_code = rewrite_assert(code, "<string>")
    mock = unittest.mock.Mock()
    glob = {"assert": mock}
    exec(new_code, glob)
    mock.assert_called_with(True)


def test_overwritten_assert_with_msg():
    code = dedent(
        """\
        x = 2
        assert x == 3, 'test_string'
        """
    )
    new_code = rewrite_assert(code, "<string>")
    mock = unittest.mock.Mock()
    glob = {"assert": mock}
    exec(new_code, glob)
    mock.assert_called_with(False, "test_string")
