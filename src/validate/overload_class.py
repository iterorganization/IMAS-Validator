"""
This file describes the overload class for the operators
"""
from typing import Any, Union

from .result import IDSValidationResult

class OverloadClass():
  # how to handle if statements? (asserts?)
  # error on assignment operators
  # ids_primitive for operator list
   
  def __init__(self, x: Any, val_result: IDSValidationResult):
    # check if value/array/whatever
    self.x = x
    self.val_result = val_result
    
  def __getattr__(self, x: Any):
    return OverloadClass(self.__getattr__(x), self.val_result)

  def __getitem__(self, x: Any):
    return OverloadClass(self.__getitem__(x), self.val_result)

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
