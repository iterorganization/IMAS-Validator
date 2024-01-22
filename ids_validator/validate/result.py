"""
This file describes the data class for successes and failures of the
validation tool
"""
from typing import List
import inspect
from pathlib import Path


class IDSValidationResult:
    """"""

    def __init__(self, func: function, ids_names: List[str], bool_result: bool):
        self.file_name = Path(inspect.getfile(func)).parts[-3:]
        self.func_name = func.__name__
        self.func_docs = func.__doc__
        self.ids_names: list[str] = list(inspect.signature(func).parameters.keys())
        self.ids_occurences: List[int] = ...
        self.lineno: int = ...
        self.bool_result: bool = bool_result
        # rule/line (var1 + var2 == var3)

        # import traceback
        # info = traceback.extract_stack()
        # self.file_name = info.filename
        # self.lineno = info.lineno
        # self.func_name = info.name
        # self.code_context = info.line
