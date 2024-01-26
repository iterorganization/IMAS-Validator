from functools import lru_cache
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
    apply_rules,
    find_matching_rules,
    apply_rule,
    get_ids_instance_args,
)


_occurrence_dict = {
    "core_profiles": numpy.array([0, 1, 3, 5]),
    "equilibrium": numpy.array([0, 1]),
    "pf_active": numpy.array([0]),
    "magnetics": numpy.array([1]),
}


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


@pytest.mark.xfail(reason="Not implemented yet", strict=True)
def test_apply_rules_to_data(dbentry, rules):
    # TODO, but something like the following
    # Function to test:
    apply_rules_to_data(dbentry, rules)

    # Check that rule functions were called with expected arguments:
    expected_calls = {
        ids_name: [
            # Note: this works because `get` is cached:
            call(get(ids_name, occurrence))
            for occurrence in _occurrence_dict[ids_name]
        ]
        for ids_name in _occurrence_dict
    }
    # First rule applies to all IDSs
    assert rules[0].func.call_count == 8  # 4x cp, 2x eq, 1x pf_active, 1x magnetics
    assert rules[0].func.assert_has_calls(sum(expected_calls.values()), any_order=True)
    # Second rule applies to all occurrences of core_profiles:
    assert rules[1].func.call_count == 4
    assert rules[1].func.assert_has_calls(
        expected_calls["core_profiles"], any_order=True
    )
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


@pytest.mark.xfail(reason="Not implemented yet", strict=True)
def test_apply_rules(dbentry, rules):
    ids = dbentry.get("core_profiles", 0)

    apply_rules(ids, rules)

    # Check that rule functions were called with expected arguments:
    expected_calls = {
        "core_profiles": [
            # Note: this works because `get` is cached:
            call(get("core_profiles", 0))
        ]
    }
    # First rule applies to all IDSs
    assert rules[0].func.called_once()
    assert rules[0].func.assert_has_calls(
        expected_calls["core_profiles"], any_order=True
    )
    # Second rule applies to all occurrences of core_profiles:
    assert rules[1].func.called_once()
    assert rules[1].func.assert_has_calls(
        expected_calls["core_profiles"], any_order=True
    )
    # Third rule applies to nothing in this DBEntry
    assert rules[2].func.call_count == 0


@pytest.mark.xfail(reason="Not implemented yet", strict=True)
def test_find_matching_rules(dbentry, rules):
    ids = dbentry.get("core_profiles", 0)
    assert find_matching_rules(ids, rules) == rules[:1]


@pytest.mark.xfail(reason="Not implemented yet", strict=True)
def test_apply_rule(dbentry, rules):
    ids = dbentry.get("core_profiles", 0)
    rule = rules[0]
    apply_rule(ids, rule)
    rule.func.assert_called_once()
    assert isinstance(rule.func.call_arg_list[0], IDSWrapper)
    assert rule.func.call_arg_list[0].obj == ids


@pytest.mark.xfail(reason="Not implemented yet", strict=True)
def test_apply_rule_arg_error(dbentry, rules):
    with pytest.raises(ValueError):
        apply_rule([], rules[0])


# implement for multi-IDS apply
@pytest.mark.skip(reason="Not implemented yet")
def test_get_ids_instance_args(dbentry, rules):
    rule = rules[4]
    ids1 = dbentry.get("core_profiles", 0)
    ids2 = dbentry.get("equilibrium", 0)
    idss = [ids1, ids2]
    ids_args = get_ids_instance_args(idss, rule)
    assert [arg.name for arg in ids_args] == rule.ids_names
    ids_args = get_ids_instance_args(reversed(idss), rule)
    assert [arg.name for arg in ids_args] == rule.ids_names

    rule.ids_names = reversed(rule.ids_names)
    ids_args = get_ids_instance_args(idss, rule)
    assert [arg.name for arg in ids_args] == rule.ids_names
    ids_args = get_ids_instance_args(reversed(idss), rule)
    assert [arg.name for arg in ids_args] == rule.ids_names
