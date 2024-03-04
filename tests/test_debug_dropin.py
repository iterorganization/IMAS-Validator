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
    mock.func = cool_func_name
    mock.apply_func = lambda x: cool_func_name(*x)
    return mock


@pytest.fixture
def rule_error(res_collector):
    def func_error(ids_name):
        """Error docs"""
        a = ids_name / 0
        res_collector.assert_(a)

    mock = Mock()
    mock.func = func_error
    mock.apply_func = lambda x: func_error(*x)
    return mock


@pytest.fixture
def rule_executor(rule, rule_error, res_collector):
    dbentry = Mock()
    rules = [rule, rule_error]
    rule_executor = RuleExecutor(dbentry, rules, res_collector, debug=True)
    return rule_executor


def test_debug(rule_executor, res_collector):
    rules = rule_executor.rules
    my_pdb = Mock()
    my_pdb.__name__ = "post_mortem"

    with patch(
        "ids_validator.validate.rule_executor.pdb",
        post_mortem=my_pdb,
    ):
        res_collector.set_context(rules[0], [("core_profiles", 0)])
        rule_executor.run(rules[0], [True])
        assert len(res_collector.results) == 1
        assert my_pdb.call_count == 0

        res_collector.set_context(rules[0], [("core_profiles", 1)])
        rule_executor.run(rules[0], [False])
        assert len(res_collector.results) == 2
        assert my_pdb.call_count == 1
        tbi = my_pdb.call_args_list[0][0][0]
        while tbi.tb_next:
            tbi = tbi.tb_next
        assert tbi.tb_frame.f_code.co_name == "cool_func_name"

        res_collector.set_context(rules[1], [("core_profiles", 2)])
        rule_executor.run(rules[1], [1])
        assert len(res_collector.results) == 3
        assert my_pdb.call_count == 2
        tbi = my_pdb.call_args_list[1][0][0]
        while tbi.tb_next:
            tbi = tbi.tb_next
        assert tbi.tb_frame.f_code.co_name == "func_error"
