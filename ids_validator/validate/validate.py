"""
This file describes the main function for the IMAS IDS validation tool
"""
from typing import List
from pathlib import Path

from imaspy import DBEntry

from .result import IDSValidationResult
from .apply_loop import apply_rules_to_data
from ..rules.loading import load_rules


def validate(
    ids_url: str, extra_rule_dirs: List[Path] = [], apply_generic: bool = True
) -> List[IDSValidationResult]:
    """Main function"""
    dbentry = DBEntry(url=ids_url)
    rules = load_rules(extra_rule_dirs, apply_generic=apply_generic)
    results = apply_rules_to_data(dbentry, rules)
    return results
