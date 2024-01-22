"""
This file describes the main function for the IMAS IDS validation tool
"""
from typing import List
from pathlib import Path

from imaspy import DBEntry

from .result import IDSValidationResult
from .result_collector import ResultCollector
from .apply_loop import apply_rules_to_data
from ..rules.loading import load_rules


def validate(
    ids_url: str, extra_rule_dirs: List[Path] = [], apply_generic: bool = True
) -> List[IDSValidationResult]:
    """
    Main function
    Args:
        ids_url: url for DBEntry object
        extra_rule_dirs: List of names for ruleset groups that should be applied
        apply_generic: Whether or not to apply the generic ruleset

    Returns:
        List of IDSValidationResult objects
    """
    dbentry = DBEntry(ids_url, "r")
    result_collector = ResultCollector()
    rules = load_rules(
        extra_rule_dirs, apply_generic=apply_generic, result_collector=result_collector
    )
    results = apply_rules_to_data(dbentry, rules)
    return results
