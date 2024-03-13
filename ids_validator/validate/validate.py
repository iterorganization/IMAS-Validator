"""
This file describes the main function for the IMAS IDS validation tool
"""

from typing import List

from imaspy import DBEntry
from imaspy.imas_interface import has_imas, ll_interface
from packaging.version import Version

from ids_validator.exceptions import IMASVersionError
from ids_validator.rules.loading import load_rules
from ids_validator.validate.result import IDSValidationResult
from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.rule_executor import RuleExecutor
from ids_validator.validate_options import ValidateOptions


def validate(
    rulesets: List[str],
    ids_url: str,
    validate_options: ValidateOptions,
) -> List[IDSValidationResult]:
    """
    Main function
    Args:
        rulesets: names of rulesets to be applied
        ids_url: url for DBEntry object
        validate_options: dataclass with options for validate function

    Returns:
        List of IDSValidationResult objects
    """

    _check_imas_version()
    dbentry = DBEntry(ids_url, "r")
    result_collector = ResultCollector(validate_options=validate_options)
    rules = load_rules(
        rulesets=rulesets,
        result_collector=result_collector,
        validate_options=validate_options,
    )
    rule_executor = RuleExecutor(
        dbentry, rules, result_collector, validate_options=validate_options
    )
    rule_executor.apply_rules_to_data()
    results = result_collector.results
    return results


def _check_imas_version() -> None:
    """Check if the installed IMAS version is sufficient."""
    # TODO: check if this is the best level to test for the IMAS version
    if not has_imas:
        raise IMASVersionError()
    if ll_interface._al_version < Version("5.1"):
        raise IMASVersionError(ll_interface._al_version)
