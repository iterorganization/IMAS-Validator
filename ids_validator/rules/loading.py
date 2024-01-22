"""This file describes the functionality for discovering and loading validation rules"""
import os
from typing import List
from pathlib import Path

from ids_validator.validate.result_collector import ResultCollector
from .data import IDSValidationRule, ValidatorRegistry
from ids_validator.rules.ast_rewrite import run_path
from ids_validator.exceptions import (
    InvalidRulesetPath,
    InvalidRulesetName,
    EmptyRuleFileWarning,
    WrongFileExtensionError,
)


def load_rules(
    rulesets: List[str],
    apply_generic: bool,
    extra_rule_dirs: List[Path],
    result_collector: ResultCollector,
) -> List[IDSValidationRule]:
    """
    Load IDSValidationRule objects from given rulesets and directories

    Args:
        rulesets: List of identifiers of for ruleset groups like 'ITER-MD'
            or 'Generic'
        apply_generic: Whether or not to apply the generic ruleset that applies to
            all IDSs
        extra_rule_dirs: List of directories in which to look for rulesets
        result_collector: ResultCollector where the found tests will deposit their
            results after being run

    Returns:
        Loaded validation rules.
    """
    ruleset_dirs = discover_rulesets(extra_rule_dirs=extra_rule_dirs)
    filtered_dirs = filter_rulesets(
        ruleset_dirs, rulesets=rulesets, apply_generic=apply_generic
    )
    paths = discover_rule_modules(filtered_dirs)
    rules = []
    for path in paths:
        rules += load_rules_from_path(path, result_collector)
    return rules


def discover_rulesets(extra_rule_dirs: List[Path] = []) -> List[Path]:
    """
    Make a list of directories and child directories which might contain rules.

    Args:
        extra_rule_dirs: List of directories in which to look for rulesets

    Returns:
        List of directories that might contain rules
    """
    # ARG PARSING
    rule_dirs = []
    for rule_dir in extra_rule_dirs:
        if not rule_dir.exists():
            raise InvalidRulesetPath(rule_dir)
        rule_dirs += get_child_dirs(rule_dir)
    # ENV VARIABLE PARSING:
    env_var_dir_list = handle_env_var_rule_dirs()
    # OPTIONAL ENTRY POINT HANDLING
    entrypoint_dir_list = handle_entrypoints()
    # COMBINE ALL
    ruleset_dirs = list(set(rule_dirs + env_var_dir_list + entrypoint_dir_list))
    return ruleset_dirs


def filter_rulesets(
    ruleset_dirs: List[Path], rulesets: List[str], apply_generic: bool
) -> List[Path]:
    """
    filter list of directories to only those that contain rulesets which should be
    applied

    Args:
        ruleset_dirs: List of directories in which to look for rulesets
        rulesets: List of names for ruleset groups that should be applied
        apply_generic: Whether or not to apply the generic ruleset

    Returns:
        List of directories corresponding to given rule sets
    """
    filtered_rulesets: List[Path] = []
    for ruleset_dir in ruleset_dirs:
        name = ruleset_dir.name
        if apply_generic and name == "generic":
            filtered_rulesets.append(ruleset_dir)
        elif name in rulesets:
            filtered_rulesets.append(ruleset_dir)
    filtered_ruleset_names = [p.name for p in filtered_rulesets]
    for ruleset in rulesets:
        if ruleset not in filtered_ruleset_names:
            raise InvalidRulesetName(ruleset, ruleset_dirs)
    return filtered_rulesets


def discover_rule_modules(ruleset_dirs: List[Path]) -> List[Path]:
    """
    Make a list of files that might contain rulesets

    Args:
        ruleset_dirs: List of directories in which to look for rulesets

    Returns:
        List of files that migth contain rulesets
    """
    rule_modules = []
    for ruleset_dir in ruleset_dirs:
        for path in ruleset_dir.iterdir():
            if path.is_file():
                rule_modules.append(path)
    rule_modules = list(set(rule_modules))
    return rule_modules


def load_rules_from_path(
    rule_path: Path, result_collector: ResultCollector
) -> List[IDSValidationRule]:
    """
    Make a list of files that might contain rulesets

    Args:
        rule_path: Path for file that might contain rulesets
        result_collector: ResultCollector where the found tests will deposit their
            results after being run

    Returns:
        List IDSValidationRule objects from given file
    """
    if rule_path.suffix != ".py":
        raise WrongFileExtensionError(rule_path)
    val_registry = ValidatorRegistry(rule_path)

    run_path(rule_path, val_registry, result_collector)
    if len(val_registry.validators) == 0:
        raise EmptyRuleFileWarning(rule_path)
    return val_registry.validators


def handle_env_var_rule_dirs() -> List[Path]:
    """
    Make a list of directories and child directories which might contain rules based on
    environment variable

    Returns:
        List of directories corresponding to given rule sets
    """
    env_ruleset_paths = os.environ.get("RULESET_PATH", "")
    rule_dirs = [Path(part) for part in env_ruleset_paths.split(":") if part]
    env_var_dirs = []
    for rule_dir in rule_dirs:
        if not rule_dir.exists():
            raise InvalidRulesetPath(rule_dir)
        env_var_dirs += get_child_dirs(rule_dir)

    return env_var_dirs


def handle_entrypoints() -> List[IDSValidationRule]:
    """
    TODO: enable locating rulesets through entrypoints
    """
    return []


def get_child_dirs(dir: Path) -> List[Path]:
    child_dirs = [path for path in dir.iterdir() if path.is_dir()]
    return child_dirs
