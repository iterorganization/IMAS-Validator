from pathlib import Path
from unittest.mock import Mock

import pytest

from ids_validator.rules.ast_rewrite import rewrite_assert
from ids_validator.rules.data import ValidatorRegistry
from ids_validator.validate.ids_wrapper import IDSWrapper
from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate_options import ValidateOptions


@pytest.fixture
def res_collector():
    res_col = ResultCollector(validate_options=ValidateOptions(), db_entry=Mock)
    return res_col


@pytest.fixture
def rule(res_collector):
    def cool_func_name(ids_name):
        """put docs here"""
        res_collector.assert_(ids_name)

    mock = Mock()
    mock.func = cool_func_name
    return mock


@pytest.fixture
def rule_error(res_collector):
    def func_error(ids_name):
        """Error docs"""
        a = ids_name / 0
        res_collector.assert_(a)

    mock = Mock()
    mock.func = func_error
    return mock


@pytest.fixture
def rewritten_rule(res_collector):
    val_registry = ValidatorRegistry(Path("a/b/c.py"))
    code = rewrite_assert(
        """
@validator("*")
def rewritten_rule(ids):
    '''Put docs here'''
    assert ids is not None
""",
        "a/b/c.py",
    )
    exec(code, {"validator": val_registry.validator, "assert": res_collector.assert_})
    return val_registry.validators[0]


def check_attrs(val_result, success):
    assert val_result.success == success
    assert val_result.msg == ""
    assert val_result.rule.func.__name__ == "cool_func_name"
    assert val_result.idss == [("core_profiles", 0)]
    assert val_result.tb[-1].lineno == 23
    assert val_result.exc is None


def check_attrs_error(val_result):
    assert val_result.success is False
    assert val_result.msg == ""
    assert val_result.rule.func.__name__ == val_result.tb[-1].name == "func_error"
    assert val_result.idss == [("core_profiles", 0)]
    assert val_result.tb[-1].lineno == 34
    assert isinstance(val_result.exc, ZeroDivisionError)


def test_all_attrs_filled_on_success(res_collector, rule):
    res_collector.set_context(rule, [("core_profiles", 0)])
    a = IDSWrapper(True)
    rule.func(a)
    check_attrs(res_collector.results[0], True)


def test_all_attrs_filled_on_fail(res_collector, rule):
    res_collector.set_context(rule, [("core_profiles", 0)])
    rule.func(IDSWrapper(False))
    check_attrs(res_collector.results[0], False)


def test_list_nodes(res_collector, rule, test_data_core_profiles, test_data_waves):
    res_collector.set_context(rule, [("core_profiles", 0), ("waves", 1)])
    cp_time = test_data_core_profiles.ids_properties.homogeneous_time
    waves_time = test_data_waves.ids_properties.homogeneous_time
    rule.func(cp_time == waves_time)
    assert res_collector.results[0].nodes_dict == {
        ("core_profiles", 0): ["ids_properties/homogeneous_time"],
        ("waves", 1): ["ids_properties/homogeneous_time"],
    }


def test_all_attrs_filled_on_non_wrapper_test_arg(res_collector, rule):
    res_collector.set_context(rule, [("core_profiles", 0)])
    rule.func(True)
    check_attrs(res_collector.results[0], True)


def test_appropriate_behavior_on_error(res_collector, rule, rule_error):
    res_collector.set_context(rule, [("core_profiles", 0)])
    rule.func(True)
    check_attrs(res_collector.results[0], True)
    try:
        res_collector.set_context(rule_error, [("core_profiles", 0)])
        rule_error.func(True)
    except Exception as e:
        res_collector.add_error_result(e)
    check_attrs_error(res_collector.results[1])


def test_double_occurrence_not_implemented(res_collector, rule):
    with pytest.raises(NotImplementedError):
        res_collector.set_context(rule, [("core_profiles", 0), ("core_profiles", 1)])


def test_rewritten_rule(res_collector, rewritten_rule):
    res_collector.set_context(rewritten_rule, [("core_profiles", 0)])
    rewritten_rule.func(True)
    val_result = res_collector.results[0]
    assert val_result.success is True
    assert val_result.msg == ""
    assert val_result.rule.func.__name__ == "rewritten_rule"
    assert val_result.idss == [("core_profiles", 0)]
    assert val_result.tb[-1].lineno == 5
    assert val_result.exc is None
