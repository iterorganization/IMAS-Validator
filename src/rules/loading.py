"""This file describes the functionality for loading all discovered rules"""
from typing import List, Union
from pathlib import Path
from runpy import run_path

from .data import IDSValidationRule, ValidatorRegistry

def load_rules(rule_dir: Union[Path, List[Path]], apply_generic: bool=True) -> List[IDSValidationRule]:
  """"""
  paths = discover_rules(rule_dir, apply_generic=apply_generic)
  rules = []
  for path in paths:
    rules += load_rules_from_path(path)
  return rules

def load_rules_from_path(rule_path: Path) -> List[IDSValidationRule]:
  """"""
  val_registry = ValidatorRegistry()
  run_path(rule_path, init_globals={'val_registry': val_registry})
  # filter rules based on rule_sets
  return val_registry.validators()

def discover_rulesets(rule_dir: Path) -> List[Path]:
  pass

def discover_rules(rule_dir: Path, apply_generic=True) -> List[Path]:
  """"""
  # define identifier for files that contain rules
  # recursively go through dir to find files that contain rules based on identifier
  # filter generic rulesets based on apply_generic
  # return list of paths of files
  pass