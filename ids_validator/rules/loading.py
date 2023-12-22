"""This file describes the functionality for discovering and loading validation rules"""
import os
from typing import List
from pathlib import Path
from runpy import run_path

from .data import IDSValidationRule, ValidatorRegistry


def load_rules(
    rulesets: List[str], apply_generic: bool, extra_rule_dirs: List[Path] = []
) -> List[IDSValidationRule]:
    """
    Load IDSValidationRule objects from given rulesets and directories

    Args:
        rulesets [List[str]]: List of identifiers of for ruleset groups like 'ITER-MD'
            or 'Generic'
        apply_generic [bool]: Whether or not to apply the generic rulesets that apply to
            all IDSs
        extra_rule_dirs [List[Pathlib.Path]]: List of directories in which to look for
            rulesets

    Returns:
        List of IDSValidationRule objects
    """
    ruleset_dirs = discover_rulesets(extra_rule_dirs=extra_rule_dirs)
    filtered_dirs = filter_rulesets(
        ruleset_dirs, rulesets=rulesets, apply_generic=apply_generic
    )
    paths = discover_rule_modules(filtered_dirs)
    rules = []
    for path in paths:
        rules += load_rules_from_path(path)
    return rules


def discover_rulesets(extra_rule_dirs: List[Path] = []) -> List[Path]:
    """
    Make a list of directories and child directories which might contain rules based on
    input, entry points and environment variable

    Args:
        extra_rule_dirs [List[Pathlib.Path]]: List of directories in which to look for
            rulesets

    Returns:
        List of directories that might contain rules
    """
    # ARG PARSING
    rule_dirs = []
    for rule_dir in extra_rule_dirs:
        for path in get_child_dirs(rule_dir):
            if "ruleset" in str(path):
                rule_dirs.append(path)
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
        ruleset_dirs [List[Pathlib.Path]]: List of directories in which to look for
            rulesets
        rulesets [List[str]]: List of names for ruleset groups that should be applied
        apply_generic [bool]: Whether or not to apply the generic ruleset

    Returns:
        List of directories corresponding to given rule sets
    """
    filtered_rulesets = []
    for ruleset_dir in ruleset_dirs:
        parts = ruleset_dir.parts
        if apply_generic and "generic" in parts:
            filtered_rulesets.append(ruleset_dir)
        elif any([(ruleset in parts) for ruleset in rulesets]):
            filtered_rulesets.append(ruleset_dir)
    return filtered_rulesets


def discover_rule_modules(ruleset_dirs: List[Path]) -> List[Path]:
    """
    Make a list of files that might contain rulesets

    Args:
        ruleset_dirs [List[Pathlib.Path]]: List of directories in which to look for
            rulesets

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


def load_rules_from_path(rule_path: Path) -> List[IDSValidationRule]:
    """
    Make a list of files that might contain rulesets

    Args:
        rule_path [Pathlib.Path]: Path for file that might contain rulesets

    Returns:
        List IDSValidationRule objects from given file
    """
    val_registry = ValidatorRegistry(rule_path)
    run_path(rule_path, init_globals={"val_registry": val_registry})
    return val_registry.validators


def handle_env_var_rule_dirs() -> List[Path]:
    """
    Make a list of directories and child directories which might contain rules based on
    environment variable

    Returns:
        List of directories corresponding to given rule sets
    """
    env_var_dir_string_list = os.environ.get("RULESET_PATH", "").split(":")
    env_var_dirs = []
    for env_var_dir in env_var_dir_string_list:
        for path in get_child_dirs(Path(env_var_dir)):
            if "ruleset" in str(path):
                env_var_dirs.append(path)
    return env_var_dirs


def handle_entrypoints() -> List[IDSValidationRule]:
    """
    TODO: enable locating rulesets through entrypoints
    """
    return []


def get_child_dirs(dir: Path) -> List[Path]:
    child_dirs = [path for path in dir.iterdir() if path.is_dir()]
    return child_dirs
