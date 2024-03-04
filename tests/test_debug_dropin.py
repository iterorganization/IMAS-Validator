from unittest.mock import Mock, patch

import pytest

from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.rule_executor import RuleExecutor


@pytest.fixture
def res_collector():
    res_col = ResultCollector(debug=True)
    return res_col


@pytest.fixture
def rule(res_collector):
    def cool_func_name(ids_name):
        """put docs here"""
        res_collector.assert_(ids_name)

    mock = Mock()
    mock.apply_func = lambda x: cool_func_name(*x)
    return mock


@pytest.fixture
def rule_error(res_collector):
    def func_error(ids_name):
        """Error docs"""
        a = ids_name / 0
        res_collector.assert_(a)

    mock = Mock()
    mock.apply_func = lambda x: func_error(*x)
    return mock


@pytest.fixture
def rule_executor(rule, rule_error, res_collector):
    dbentry = Mock()
    rules = [rule, rule_error]
    rule_executor = RuleExecutor(dbentry, rules, res_collector, debug=True)
    return rule_executor


def assert_last_tb(tbi, res):
    while tbi.tb_next:
        tbi = tbi.tb_next
    assert tbi.tb_frame.f_code.co_name == res


def test_debug_true(rule, rule_executor, res_collector):
    my_pdb = Mock()

    with patch(
        "ids_validator.validate.rule_executor.pdb",
        post_mortem=my_pdb,
    ):
        res_collector.set_context(rule, [("core_profiles", 0)])
        rule_executor.run(rule, [True])
        assert len(res_collector.results) == 1
        assert my_pdb.call_count == 0


def test_debug_false(rule, rule_executor, res_collector):
    my_pdb = Mock()

    with patch(
        "ids_validator.validate.rule_executor.pdb",
        post_mortem=my_pdb,
    ):
        res_collector.set_context(rule, [("core_profiles", 0)])
        rule_executor.run(rule, [False])
        assert len(res_collector.results) == 1
        assert my_pdb.call_count == 1
        assert_last_tb(my_pdb.call_args_list[0][0][0], "cool_func_name")


def test_debug_error(rule_error, rule_executor, res_collector):
    my_pdb = Mock()

    with patch(
        "ids_validator.validate.rule_executor.pdb",
        post_mortem=my_pdb,
    ):
        res_collector.set_context(rule_error, [("core_profiles", 0)])
        rule_executor.run(rule_error, [1])
        assert len(res_collector.results) == 1
        assert my_pdb.call_count == 1
        assert_last_tb(my_pdb.call_args_list[0][0][0], "func_error")
