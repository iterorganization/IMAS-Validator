import pytest
from unittest.mock import Mock

from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.ids_wrapper import IDSWrapper


@pytest.fixture(scope="function")
def res_collector():
    res_col = ResultCollector()
    return res_col


@pytest.fixture()
def rule(res_collector):
    def cool_func_name(ids_name):
        """put docs here"""
        res_collector.assert_(ids_name)

    mock = Mock()
    mock.func = cool_func_name
    return mock


@pytest.fixture()
def rule_error(res_collector):
    def func_error(ids_name):
        """Error docs"""
        a = ids_name / 0
        res_collector.assert_(a)

    mock = Mock()
    mock.func = func_error
    return mock


def check_attrs(val_result, bool_result):
    assert val_result.bool_result == bool_result
    assert val_result.msg == ""
    assert val_result.rule.func.__name__ == "cool_func_name"
    assert val_result.idss == (("core_profiles", 0),)
    assert val_result.tb[val_result.frame_idx].lineno == 18
    assert val_result.exc is None


def check_attrs_error(val_result, bool_result):
    assert val_result.bool_result is False
    assert val_result.msg == ""
    assert val_result.rule.func.__name__ == "func_error"
    assert val_result.idss == (("core_profiles", 0),)
    assert val_result.tb[val_result.frame_idx].lineno == 29
    assert isinstance(val_result.exc, ZeroDivisionError)


def test_all_attrs_filled_on_success(res_collector, rule):
    res_collector.set_context(rule, (("core_profiles", 0),))
    rule.func(IDSWrapper(True))
    check_attrs(res_collector.results[0], True)


def test_all_attrs_filled_on_fail(res_collector, rule):
    res_collector.set_context(rule, (("core_profiles", 0),))
    rule.func(IDSWrapper(False))
    check_attrs(res_collector.results[0], False)


def test_all_attrs_filled_on_non_wrapper_test_arg(res_collector, rule):
    res_collector.set_context(rule, (("core_profiles", 0),))
    rule.func(True)
    check_attrs(res_collector.results[0], True)


def test_appropriate_behavior_on_error(res_collector, rule, rule_error):
    res_collector.set_context(rule, (("core_profiles", 0),))
    rule.func(True)
    check_attrs(res_collector.results[0], True)
    try:
        res_collector.set_context(rule_error, (("core_profiles", 0),))
        rule_error.func(True)
    except Exception as e:
        res_collector.add_error_result(e)
    check_attrs_error(res_collector.results[1], False)
