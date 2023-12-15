"""
This file describes the main function for the IMAS IDS validation tool
"""
from typing import List, Union
from pathlib import Path

from imaspy import DBEntry

from .result import IDSValidationResult
from .apply_loop import apply_rules_to_data
from ..rules.loading import load_rules
from ..report.main import report_func

def validate(ids_url: Path, rule_dir: Union[Path, List[Path]], apply_generic: bool=True) -> List[IDSValidationResult]:
  """Main function"""
  dbentry = DBEntry(url=ids_url)
  rules = load_rules(rule_dir, apply_generic=apply_generic)
  results = apply_rules_to_data(dbentry, rules)
  report_func(results)
  return results
