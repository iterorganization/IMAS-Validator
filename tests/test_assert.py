import pytest
import unittest.mock

from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.ids_wrapper import IDSWrapper


@pytest.fixture(scope="function")
def res_collector():
    return ResultCollector()


@pytest.fixture()
def call_func(res_collector):
    def func(ids_name):
        res_collector.assert_(ids_name)

    mock = unittest.mock.Mock(side_effect=func)
    mock.filename = "myfilename"
    mock.doc = "put docs here"
    mock.name = "cool_func_name"
    return mock


@pytest.fixture()
def call_func_error(res_collector):
    def func(ids_name):
        a = ids_name / 0
        res_collector.assert_(a)

    mock = unittest.mock.Mock(side_effect=func)
    mock.filename = "myfilename"
    mock.doc = "put docs here"
    mock.name = "cool_func_name"
    return mock


def test_attrs(val_result, bool_result):
    assert val_result.file_name == "myfilename"
    assert val_result.func_name == "cool_func_name"
    assert val_result.func_docs == "put docs here"
    assert val_result.ids_names == ["ids_name"]
    assert val_result.ids_occurences == ...
    assert val_result.lineno == ...
    assert val_result.bool_result == bool_result


def test_all_attrs_filled_on_success(res_collector, call_func):
    call_func(IDSWrapper(True))
    test_attrs(res_collector.results[0], True)


def test_all_attrs_filled_on_fail(res_collector, call_func):
    call_func(IDSWrapper(False))
    test_attrs(res_collector.results[0], False)


def test_all_attrs_filled_on_non_wrapper_test_arg(res_collector, call_func):
    call_func(True)
    test_attrs(res_collector.results[0], True)


def test_appropriate_behavior_on_error(res_collector, call_func_error):
    # TODO: decide whether to raise error immediately or continue and log error in
    # results
    pass
