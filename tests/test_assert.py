import pytest
import unittest.mock

from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.ids_wrapper import IDSWrapper


@pytest.fixture(scope="function")
def res_collector():
    return ResultCollector()


@pytest.fixture()
def call_func(res_collector):
    def func_fine(ids_name):
        res_collector.assert_(ids_name)

    mock = unittest.mock.Mock(side_effect=func_fine)
    mock.__doc__ = "put docs here"
    mock.__name__ = "cool_func_name"
    return mock


@pytest.fixture()
def call_func_error(res_collector):
    def func_error(ids_name):
        a = ids_name / 0
        res_collector.assert_(a)

    mock = unittest.mock.Mock(side_effect=func_error)
    mock.__doc__ = "put docs here"
    mock.__name__ = "cool_func_name"
    return mock


def test_attrs(val_result, bool_result, wrapped):
    assert val_result.file_name.parts[-2:] == "tests/test_assert.py"
    assert val_result.func_name == "cool_func_name"
    assert val_result.wrapped == wrapped
    if val_result.wrapped:
        assert val_result.ids_names == ["core_profiles"]
        assert val_result.ids_occurences == [0]
        assert val_result.func_docs == "put docs here"
    else:
        assert val_result.ids_names == []
        assert val_result.ids_occurences == []
        assert val_result.func_docs == ""
    assert val_result.lineno == 16
    assert val_result.bool_result == bool_result


def test_all_attrs_filled_on_success(res_collector, call_func):
    call_func(IDSWrapper(True))
    test_attrs(res_collector.results[0], True, True)


def test_all_attrs_filled_on_fail(res_collector, call_func):
    call_func(IDSWrapper(False))
    test_attrs(res_collector.results[0], False, True)


def test_all_attrs_filled_on_non_wrapper_test_arg(res_collector, call_func):
    call_func(True)
    test_attrs(res_collector.results[0], True, False)


def test_appropriate_behavior_on_error(res_collector, call_func_error):
    # TODO: decide whether to raise error immediately or continue and log error in
    # results
    pass
