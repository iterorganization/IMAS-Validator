import pytest
from unittest.mock import Mock

from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.ids_wrapper import IDSWrapper


@pytest.fixture(scope="function")
def res_collector():
    res_col = ResultCollector()
    return res_col


@pytest.fixture()
def call_func(res_collector):
    def cool_func_name(ids_name):
        "put docs here"
        res_collector.assert_(ids_name)

    return cool_func_name


@pytest.fixture()
def rule(call_func):
    mock = Mock()
    mock.func = call_func
    return mock


@pytest.fixture()
def call_func_error(res_collector):
    def func_error(ids_name):
        a = ids_name / 0
        res_collector.assert_(a)

    return func_error


def check_attrs(val_result, bool_result):
    assert val_result.func_name == "cool_func_name"
    assert val_result.func_docs == "put docs here"
    assert val_result.ids_names == ("core_profiles",)
    assert val_result.ids_occurences == (0,)
    assert "/".join(val_result.file_name.parts[-2:]) == "tests/test_assert.py"
    assert val_result.lineno == 18
    assert val_result.code_context == "res_collector.assert_(ids_name)"
    assert val_result.bool_result == bool_result


def test_all_attrs_filled_on_success(res_collector, rule):
    res_collector.set_context(rule, ("core_profiles",), (0,))
    rule.func(IDSWrapper(True))
    check_attrs(res_collector.results[0], True)


def test_all_attrs_filled_on_fail(res_collector, rule):
    res_collector.set_context(rule, ("core_profiles",), (0,))
    rule.func(IDSWrapper(False))
    check_attrs(res_collector.results[0], False)


def test_all_attrs_filled_on_non_wrapper_test_arg(res_collector, rule):
    res_collector.set_context(rule, ("core_profiles",), (0,))
    rule.func(True)
    check_attrs(res_collector.results[0], True)


def test_appropriate_behavior_on_error(res_collector, call_func_error):
    # TODO: decide whether to raise error immediately or continue and log error in
    # results
    pass
