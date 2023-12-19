"""
This file describes the data class for rules that are saved and generated for
the validation tool
"""
from typing import List, Any, Dict

class IDSValidationRule():
  """"""
  def __init__(self, func: function, *dd_types: str, **kwfields: Dict[str, Any]):
    # self.name = ruleset/file/func_name
    self.func = func
    self.dd_types = dd_types
    self.kwfields = kwfields
    # kwfields explicitly parsed

class ValidatorRegistry():
  """
  EXAMPLE:
  @val_registry.ids_validator('core_profiles')
  def ids_rule(cp):
    cp != None
  """
  def __init__(self):
    self.validators: List[IDSValidationRule] = []

  def ids_validator(self, *dd_types: str, **kwfields: Dict[str, Any]):
    # explicit kwfields
    def decorator(func: function):
      self.validators.append(IDSValidationRule(func, *dd_types, **kwfields))
      return func
    return decorator
