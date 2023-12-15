"""This file describes the functionality for loading all discovered rules"""
from typing import List, Union

from .data import IDSValidationRule

def load_rules(rule_dir: Union[str, List[str]], apply_generic: bool=True) -> List[IDSValidationRule]:
  """"""
  paths = discover_rules(rule_dir, apply_generic=apply_generic)
  rules = []
  for path in paths:
    rules += load_rules_from_path(path)
  return rules

def load_rules_from_path(rule_path: str) -> List[IDSValidationRule]:
  """"""
  # load ValidatorRegistry
  # filter rules based on rule_sets
  # return list of IDSValidationRules
  pass

def discover_rules(rule_dir: str, apply_generic=True) -> List[str]:
  """"""
  # define identifier for files that contain rules
  # recursively go through dir to find files that contain rules based on identifier
  # filter generic rulesets based on apply_generic
  # return list of paths of files
  pass