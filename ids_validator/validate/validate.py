"""
This file describes the main function for the IMAS IDS validation tool
"""

from typing import List
from pathlib import Path

from imaspy import DBEntry
from imaspy.imas_interface import has_imas, ll_interface
from packaging.version import Version

from ids_validator.exceptions import IMASVersionError
from .result import IDSValidationResult
from .result_collector import ResultCollector
from .apply_loop import apply_rules_to_data
from ..rules.loading import load_rules


def validate(
    rulesets: List[str],
    ids_url: str,
    extra_rule_dirs: List[Path] = [],
    apply_generic: bool = True,
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

    _check_imas_version()
    dbentry = DBEntry(ids_url, "r")
    result_collector = ResultCollector()
    rules = load_rules(
        rulesets=rulesets,
        extra_rule_dirs=extra_rule_dirs,
        apply_generic=apply_generic,
        result_collector=result_collector,
    )
    apply_rules_to_data(dbentry, rules)
    results = result_collector.results
    return results


def _check_imas_version() -> None:
    """Check if the installed IMAS version is sufficient."""
    # TODO: check if this is the best level to test for the IMAS version
    if not has_imas:
        raise IMASVersionError()
    if ll_interface._al_version < Version("5.1"):
        raise IMASVersionError(ll_interface._al_version)
