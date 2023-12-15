"""
This file describes the data class for rules that are saved and generated for
the validation tool
"""
from typing import List, Any, Dict, Union


class IDSValidationRule():
  """"""
  def __init__(self, func: function, *dd_types: str, **kwfields: Dict[str, Any]):
    self.func = func
    self.dd_types = dd_types
    self.kwfields = kwfields

  def apply(self, *args, **kwargs):
    return self.func(*list(map(lambda x: OverloadClass(x), args)), **kwargs)

class ValidatorRegistry():
  def __init__(self):
    self.validators: List[IDSValidationRule] = []

  def ids_validator(self, *dd_types: str, **kwfields: Dict[str, Any]):
    def decorator(func: function):
      self.validators.append(IDSValidationRule(func, *dd_types, **kwfields))
      def wrapper(*args: str, **kwargs: Dict[str, Any]):
        return func(*list(map(lambda x: OverloadClass(x), args)), **kwargs)
      return wrapper
    return decorator

class OverloadClass():
  def __init__(self, x: Any):
    # check if value/array/whatever
    self.x = x
    
  def __getattr__(self, x: Any):
    return OverloadClass(self.__getattr__(x))

  def __getitem__(self, x: Any):
    return OverloadClass(self.__getitem__(x))

  def log_stuff(self, var1: Any, var2: Any, operator: str, result: bool):
    pass

  def __lt__(self, other: Union[int, float]):
    self.log_stuff(self.x, other, 'lt', self.x < other)
  
  def __gt__(self, other: Union[int, float]):
    self.log_stuff(self.x, other, 'gt', self.x > other)
  
  def __le__(self, other: Union[int, float]):
    self.log_stuff(self.x, other, 'le', self.x <= other)
  
  def __ge__(self, other: Union[int, float]):
    self.log_stuff(self.x, other, 'ge', self.x >= other)
  
  def __eq__(self, other: Union[int, float]):
    self.log_stuff(self.x, other, 'eq', self.x == other)
  
  def __ne__(self, other: Union[int, float]):
    self.log_stuff(self.x, other, 'ne', self.x != other)

  def Increasing(self):
    """"""
    pass

  def Decreasing(self):
    """"""
    pass

  def Match(self):
    """"""
    pass

  def Exists(self):
    """"""
    pass


## EXAMPLE
# valreg = ValidatorRegistry()
#
# @valreg.ids_validator('core_profiles')
# def ids_rule(cp):
#   cp != None
