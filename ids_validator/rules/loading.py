"""This file describes the functionality for loading all discovered rules"""
from typing import List
from pathlib import Path
from runpy import run_path

from .data import IDSValidationRule, ValidatorRegistry


def load_rules(
    rule_sets: List[str], apply_generic: bool, extra_rule_dirs: List[Path] = []
) -> List[IDSValidationRule]:
    """"""
    rule_set_dirs = discover_rulesets(extra_rule_dirs=extra_rule_dirs)
    filtered_dirs = filter_rule_sets(
        rule_set_dirs, rule_sets=rule_sets, apply_generic=apply_generic
    )
    paths = discover_rule_modules(filtered_dirs)
    rules = []
    for path in paths:
        rules += load_rules_from_path(path)
    return rules


def discover_rulesets(extra_rule_dirs: List[Path] = []) -> List[Path]:
    # env variable parsing
    # optional entry point handling
    pass


def filter_rule_sets(
    rule_set_dirs: List[Path], rule_sets: List[str], apply_generic: bool
) -> List[Path]:
    pass


def discover_rule_modules(rule_set_dirs: List[Path]) -> List[Path]:
    """"""
    # define identifier for files that contain rules
    # recursively go through dir to find files that contain rules based on identifier
    # return list of paths of files
    pass


def load_rules_from_path(rule_path: Path) -> List[IDSValidationRule]:
    """"""
    val_registry = ValidatorRegistry()
    run_path(rule_path, init_globals={"val_registry": val_registry})
    return val_registry.validators()
