from functools import lru_cache, reduce
from pathlib import Path
from unittest.mock import Mock, call

from imaspy import IDSFactory

from imaspy.exception import DataEntryException
import numpy
import pytest

from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.ids_wrapper import IDSWrapper
from ids_validator.validate.apply_loop import (
    apply_rules_to_data,
    find_matching_rules,
)


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
def get(ids_name: str, occurrence: int = 0):
    # Trying to get an IDS that isn't filled is an error:
    if occurrence not in list_all_occurrences(ids_name):
        raise DataEntryException(f"IDS {ids_name!r}, occurrence {occurrence} is empty.")

    ids = IDSFactory("3.40.1").new(ids_name)
    ids.ids_properties.comment = f"Test IDS: {ids_name}/{occurrence}"
    ids.ids_properties.homogeneous_time = 1
    # TODO: if needed, we can fill IDSs with specific data
    return ids


def list_all_occurrences(ids_name: str):
    return _occurrence_dict.get(ids_name, [])


@pytest.fixture
def dbentry():
    """Get a mocked imaspy.DBEntry."""
    db = Mock()
    db.list_all_occurrences = Mock(wraps=list_all_occurrences)
    db.get = Mock(wraps=get)
    db.factory = IDSFactory("3.40.1")
    return db


@pytest.fixture
def rules():
    """get rules"""
    mocks = []
    for i in range(3):
        mock = Mock()
        mock.__name__ = f"Mock func {i}"  # IDSValidationRule requires __name__
        mocks.append(mock)
    rules = [
        IDSValidationRule(Path("t/all.py"), mocks[0], "*"),
        IDSValidationRule(Path("t/core_profiles.py"), mocks[1], "core_profiles"),
        IDSValidationRule(Path("t/summary.py"), mocks[2], "summary"),
    ]
    return rules


def test_dbentry_mock(dbentry):
    assert dbentry.list_all_occurrences("summary") == []
    assert numpy.array_equal(dbentry.list_all_occurrences("equilibrium"), [0, 1])

    with pytest.raises(DataEntryException):
        dbentry.get("summary")

    cp = dbentry.get("core_profiles")
    assert cp.ids_properties.comment == "Test IDS: core_profiles/0"
    assert cp.metadata.name == "core_profiles"
    cp3 = dbentry.get("core_profiles", 3)
    assert cp3.ids_properties.comment == "Test IDS: core_profiles/3"


def test_apply_rules_to_data(dbentry, rules):
    # Function to test:
    apply_rules_to_data(dbentry, rules)

    # Check that rule functions were called with expected arguments:
    expected_calls = {
        ids_name: [
            # Note: this works because `get` is cached:
            get(ids_name, occurrence)
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

    # Also expect that get() was called exactly once per IDS/occurrence
    get_calls = [
        call(ids_name, occurrence)
        for ids_name in _occurrence_dict
        for occurrence in _occurrence_dict[ids_name]
    ]
    assert dbentry.get.call_count == len(get_calls)
    dbentry.get.assert_has_calls(get_calls, any_order=True)


def test_find_matching_rules(dbentry, rules):
    expected_result = []
    for ids_name in _occurrence_dict:
        for occurence in _occurrence_dict[ids_name]:
            # every occurrence once for '*'
            ids = (get(ids_name, occurence),)
            expected_result.append((ids, rules[0]))
            # all occurrences for 'core_profiles'
            if ids_name == "core_profiles":
                expected_result.append((ids, rules[1]))
    result = [(ids, rule) for ids, rule in find_matching_rules(dbentry, rules)]
    assert len(result) == len(expected_result) == 12
    diff = set(result) - set(expected_result)
    assert len(diff) == 0


def test_apply_func(dbentry, rules):
    ids = dbentry.get("core_profiles", 0)
    rule = rules[0]
    rule.apply_func([ids])
    rule.func.assert_called_once()
    assert isinstance(rule.func.call_args_list[0][0][0], IDSWrapper)
    assert rule.func.call_args_list[0][0][0]._obj == ids
