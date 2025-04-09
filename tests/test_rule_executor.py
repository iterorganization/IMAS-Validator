try:
    import imaspy as imas  # type: ignore
except ImportError:
    import imas  # type: ignore

import logging
from functools import lru_cache, reduce
from pathlib import Path
from unittest.mock import Mock, call

import numpy
import pytest

from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.ids_wrapper import IDSWrapper
from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.rule_executor import RuleExecutor
from ids_validator.validate_options import ValidateOptions

_occurrence_dict = {
    "core_profiles": numpy.array([0, 1, 3, 5]),
    "equilibrium": numpy.array([0, 1]),
    "pf_active": numpy.array([0]),
    "magnetics": numpy.array([1]),
}


def check_expected_calls(func, expected_call_list):
    actual_idss = []
    for args in func.call_args_list:
        assert len(args.args) == 1
        assert not args.kwargs
        assert isinstance(args.args[0], IDSWrapper)
        actual_idss.append(args.args[0]._obj)
    actual_idss.sort(key=id)
    expected_idss = sorted(expected_call_list, key=id)
    assert expected_idss == actual_idss


@lru_cache
def get(ids_name: str, occurrence: int = 0, autoconvert: bool = False):
    # Trying to get an IDS that isn't filled is an error:
    if occurrence not in list_all_occurrences(ids_name):
        raise imas.exception.DataEntryException(f"IDS {ids_name!r}, occurrence {occurrence} is empty.")

    ids = imas.IDSFactory("3.40.1").new(ids_name)
    ids.ids_properties.comment = f"Test IDS: {ids_name}:{occurrence}"
    ids.ids_properties.homogeneous_time = 1
    # TODO: if needed, we can fill IDSs with specific data
    return ids


def list_all_occurrences(ids_name: str):
    return _occurrence_dict.get(ids_name, [])


@pytest.fixture
def dbentry():
    """Get a mocked imas.DBEntry."""
    db = Mock()
    db.list_all_occurrences = Mock(wraps=list_all_occurrences)
    db.get = Mock(wraps=get)
    db.factory = imas.IDSFactory("3.40.1")
    db.dd_version = "3.40.1"
    db.uri = ""
    return db


@pytest.fixture
def rules():
    """get rules"""
    mocks = []
    for i in range(4):
        mock = Mock()
        mock.__name__ = f"Mock func {i}"  # IDSValidationRule requires __name__
        mocks.append(mock)
    rules = [
        IDSValidationRule(Path("t/all.py"), mocks[0], "*", version="==3.40.1"),
        IDSValidationRule(Path("t/core_profiles.py"), mocks[1], "core_profiles"),
        IDSValidationRule(Path("t/summary.py"), mocks[2], "summary:1"),
        IDSValidationRule(Path("t/all.py"), mocks[3], "*", version="==3.40.0"),
        IDSValidationRule(Path("t/summary.py"), mocks[2], "summary:0", "equilibrium:2"),
    ]
    return rules


@pytest.fixture
def rule_executor(dbentry, rules):
    result_collector = ResultCollector(
        validate_options=ValidateOptions(), imas_uri=dbentry.uri
    )
    rule_executor = RuleExecutor(
        dbentry, rules, result_collector, validate_options=ValidateOptions()
    )
    return rule_executor


def test_dbentry_mock(dbentry):
    assert dbentry.list_all_occurrences("summary") == []
    assert numpy.array_equal(dbentry.list_all_occurrences("equilibrium"), [0, 1])

    with pytest.raises(imas.exception.DataEntryException):
        dbentry.get("summary")

    cp = dbentry.get("core_profiles", autoconvert=False)
    assert cp.ids_properties.comment == "Test IDS: core_profiles:0"
    assert cp.metadata.name == "core_profiles"
    cp3 = dbentry.get("core_profiles", 3, autoconvert=False)
    assert cp3.ids_properties.comment == "Test IDS: core_profiles:3"


def test_apply_rules_to_data(rule_executor):
    rules = rule_executor.rules
    dbentry = rule_executor.db_entry
    # Function to test:
    rule_executor.apply_rules_to_data()

    # Check that rule functions were called with expected arguments:
    expected_calls = {
        ids_name: [
            # Note: this works because `get` is cached:
            get(ids_name, occurrence, autoconvert=False)
            for occurrence in _occurrence_dict[ids_name]
        ]
        for ids_name in _occurrence_dict
    }

    # First rule applies to all IDSs
    assert rules[0].func.call_count == 8  # 4x cp, 2x eq, 1x pf_active, 1x magnetics
    # Second rule applies to all occurrences of core_profiles:
    expected_call_list = reduce(lambda a, b: a + b, expected_calls.values())
    check_expected_calls(rules[0].func, expected_call_list)
    assert rules[1].func.call_count == 4
    check_expected_calls(rules[1].func, expected_calls["core_profiles"])
    # Third rule applies to nothing in this DBEntry
    assert rules[2].func.call_count == 0
    assert rules[3].func.call_count == 0

    # Also expect that get() was called exactly once per IDS/occurrence
    get_calls = [
        call(ids_name, occurrence, autoconvert=False)
        for ids_name in _occurrence_dict
        for occurrence in _occurrence_dict[ids_name]
    ]
    assert dbentry.get.call_count == len(get_calls)
    dbentry.get.assert_has_calls(get_calls, any_order=True)


def test_apply_rules_to_data_logging(rule_executor, caplog):
    def list_all_occurrences(ids_name):
        return {"magnetics": numpy.array([1])}.get(ids_name, [])

    rule_executor.db_entry.list_all_occurrences = Mock(wraps=list_all_occurrences)
    rule_executor.rules = rule_executor.rules[:1]
    rule_executor.apply_rules_to_data()
    start_log_calls = [
        "Started executing rules",
        "Running t/all.py:Mock func 0 on magnetics:1",
    ]
    fix_assert_str = (
        "Make sure the validation test is testing something with an assert statement."
    )
    empty_log_calls = [
        f"No assertions in t/all.py:Mock func 0. {fix_assert_str}",
    ]
    module = "ids_validator.validate.rule_executor"
    for val in start_log_calls:
        assert (module, logging.INFO, val) in caplog.record_tuples
    for val in empty_log_calls:
        assert (module, logging.INFO, val) in caplog.record_tuples


def test_find_matching_rules(rule_executor):
    result = list(rule_executor.find_matching_rules())
    rules = rule_executor.rules
    expected_result = []
    for ids_name in _occurrence_dict:
        for occurrence in _occurrence_dict[ids_name]:
            # every occurrence once for '*'
            idss = [
                (get(ids_name, occurrence, autoconvert=False), ids_name, occurrence)
            ]
            expected_result.append((idss, rules[0]))
            # all occurrences for 'core_profiles'
            if ids_name == "core_profiles":
                expected_result.append((idss, rules[1]))
    assert len(result) == len(expected_result) == 12
    # sort results based on id of ids to be able to compare lists
    sorted_result = sorted(result, key=lambda x: id(x[0][0][0]))
    sorted_expected_result = sorted(expected_result, key=lambda x: id(x[0][0][0]))
    assert sorted_result == sorted_expected_result


def test_apply_func(dbentry, rules):
    ids = dbentry.get("core_profiles", 0, autoconvert=False)
    rule = rules[0]
    rule.apply_func([ids])
    rule.func.assert_called_once()
    assert isinstance(rule.func.call_args_list[0][0][0], IDSWrapper)
    assert rule.func.call_args_list[0][0][0]._obj == ids


def test_parse_ids_names(dbentry):
    mock = Mock()
    mock.__name__ = "Mock func"  # IDSValidationRule requires __name__
    # fmt: off
    inputs = [
        (["*"], ("*",), (None,)),
        (["*:2"], ("*",), (2,)),
        (["summary"], ("summary",), (None,)),
        (["summary:0"], ("summary",), (0,)),
        (["summary:0", "core_profiles:0"], ("summary", "core_profiles",), (0, 0,)),
        (
            ["summary:0", "core_profiles:0", "equilibrium:1"],
            ("summary", "core_profiles", "equilibrium",),
            (0, 0, 1,)
        ),
        (["*:0", "core_profiles:0"], ("*", "core_profiles",), (0, 0,)),
    ]
    # fmt: on
    for ids_names, expected_names, expected_occs in inputs:
        rule = IDSValidationRule(Path("t/my_path.py"), mock, *ids_names)
        assert rule.ids_names == expected_names
        assert rule.ids_occs == expected_occs

    inputs = [
        ["summary", "core_profiles"],
        ["summary", "core_profiles:0"],
        ["summary:0", "core_profiles"],
        ["summary", "core_profiles:*"],
        ["summary:*"],
    ]
    for ids_names in inputs:
        with pytest.raises(ValueError):
            rule = IDSValidationRule(Path("/my_path.py"), mock, *ids_names)
