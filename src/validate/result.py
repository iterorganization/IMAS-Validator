"""
This file describes the data class for successes and failures of the
validation tool
"""
class IDSValidationResult():
  """"""
  def __init__(self):
    # file
    # rule_name
    # List[IDSValidationLineResult]
    pass
  
  def save_line_result():
    # save IDSValidationLineResult
    pass

class IDSValidationLineResult():
  def __init__(self):
    # line_num
    # vars
    # rule/line (var1 + var2 == var3)
    # result
    # take size into account (only save part of array)
    pass
