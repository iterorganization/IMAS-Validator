"""
This file describes the validation loop in which the rules are applied to the
IDS data
"""
from typing import List

from imaspy import DBEntry, IDSToplevel

from .result import IDSValidationResult
from .overload_class import OverloadClass
from ..rules.data import IDSValidationRule


def apply_rules_to_data(
    db_entry: DBEntry, rules: List[IDSValidationRule]
) -> List[IDSValidationResult]:
    """"""
    # loop over ids_names
    # load necessary ids's into memory
    # find matching rules for given ids_names
    # loop over rules
    # apply rules
    pass


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
    # rule.apply(*map(lambda x: OverloadClass(x, val_result), ids_instances), **kwargs)
    # make overload for operators and checks to log successful and failed assertions
    # generate IDSValidationResult based assertions
    # return val_result
    pass
