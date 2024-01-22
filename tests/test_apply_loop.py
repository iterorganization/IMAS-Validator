import unittest.mock
import pytest
from ids_validator.validate.apply_loop import (
    apply_rule,
    apply_rules_to_data,
    find_matching_rules,
    get_ids_instance_args,
)


@pytest.fixture()
def db_entry():
    pass


@pytest.fixture()
def ids_instances():
    pass


@pytest.fixture()
def val_rules():
    rule_list = []
    ids_names_list = [[""], [""], [""], [""]]
    for i in range(4):
        mock = unittest.mock.MagicMock()
        mock.name = str(i)
        mock.ids_names = ids_names_list[i]
        rule_list.append(mock)
    return rule_list


@pytest.fixture()
def val_rule(val_rules):
    return val_rules[0]


def test_apply_rule(ids_instances, val_rule):
    apply_rule(ids_instances, val_rule)
    val_rule.func.assert_called_once()


def test_apply_rule_arg_error(val_rule):
    with pytest.raises(ValueError):
        apply_rule([], val_rule)


def test_get_ids_instance_args(ids_instances, val_rule):
    ids_args = get_ids_instance_args(ids_instances, val_rule.ids_names)
    assert [arg.name for arg in ids_args] == val_rule.ids_names
    ids_args = get_ids_instance_args(ids_instances, reversed(val_rule.ids_names))
    assert [arg.name for arg in ids_args] == reversed(val_rule.ids_names)
    ids_args = get_ids_instance_args(reversed(ids_instances), val_rule.ids_names)
    assert [arg.name for arg in ids_args] == val_rule.ids_names
    ids_args = get_ids_instance_args(
        reversed(ids_instances), reversed(val_rule.ids_names)
    )
    assert [arg.name for arg in ids_args] == reversed(val_rule.ids_names)


def test_find_matching_rules(ids_instances, val_rules):
    ids_names = [ids.name for ids in ids_instances]
    assert find_matching_rules(ids_names, val_rules) == ["1", "2", "4"]
    assert find_matching_rules(ids_names[:2], val_rules) == ["1", "4"]


def test_apply_rules_to_data(db_entry, val_rules):
    apply_rules_to_data(db_entry, val_rules)
    for rule in val_rules:
        assert rule.func.assert_called_once()
