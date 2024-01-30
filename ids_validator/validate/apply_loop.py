"""
This file describes the validation loop in which the rules are applied to the
IDS data
"""

from typing import List, Tuple

from imaspy import DBEntry
from imaspy.ids_toplevel import IDSToplevel

# from ids_validator.validate.ids_wrapper import IDSWrapper
from .result import IDSValidationResult
from ..rules.data import IDSValidationRule


def apply_rules_to_data(
    db_entry: DBEntry, rules: List[IDSValidationRule]
) -> List[IDSValidationResult]:
    """Apply set of rules to the Data Entry.

    Args:
        db_entry: An opened DBEntry.
        rules: List of rules to apply to the data.
    """
    # loop over ids_names
    idss: List[Tuple[str, int]] = []  # (ids_name, occurrence)
    for ids_name in db_entry.factory.ids_names():
        occurrence_list = db_entry.list_all_occurrences(ids_name)
        for occurrence in occurrence_list:
            idss.append((ids_name, occurrence))

    # load necessary ids's into memory
    # Note: need to rethink this when doing multi-IDS validation
    for ids_name, occurrence in idss:
        ids = db_entry.get(ids_name, occurrence)
        # TODO: handle results
        apply_rules(ids, rules)


def apply_rules(ids: IDSToplevel, rules: List[IDSValidationRule]):
    """"""
    pass
    # find matching rules for given ids_names
    # loop over rules
    # apply rules


def find_matching_rules(ids_names: List[str], rules: List[IDSValidationRule]):
    """"""
    # find all rules that match the given ids names
    # how to optimize ids combinations in memory?
    pass


def apply_rule(
    ids_instances: List[IDSToplevel], rule: IDSValidationRule
) -> IDSValidationResult:
    """"""
    # val_result = IDSValidationResult(rule_name)
    # rule.apply(*map(lambda x: IDSWrapper(x, val_result), ids_instances), **kwargs)
    # make overload for operators and checks to log successful and failed assertions
    # generate IDSValidationResult based assertions
    # return val_result
    pass


def get_ids_instance_args(ids_instances: List[IDSToplevel], rule: IDSValidationRule):
    # return list of args in proper order (implementation for later PR)
    pass
