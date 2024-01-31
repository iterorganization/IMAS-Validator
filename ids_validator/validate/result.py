"""
This file describes the data class for successes and failures of the
validation tool
"""

from typing import List, Union
import inspect
from pathlib import Path
import traceback

from ids_validator.validate.ids_wrapper import IDSWrapper


class IDSValidationResult:
    """"""

    def __init__(self, test: Union[IDSWrapper, bool], msg: str):
        if isinstance(test, IDSWrapper):
            func = test.func
            self.wrapped = True
            self.func_docs = func.__doc__
            self.ids_names: list[str] = list(inspect.signature(func).parameters.keys())
            self.ids_occurences: List[int] = test.ids_occurences
        else:
            self.wrapped = False
            self.func_docs = ""
            self.ids_names: list[str] = []
            self.ids_occurences: List[int] = []

        info = traceback.extract_stack()
        idx = -3
        assert info[idx + 1].name == "assert_"
        self.file_name = Path(info[idx].filename).parts[-3:]
        self.func_name = info[idx].name
        self.lineno: int = info[idx].lineno
        self.code_context = info[idx].line
        self.bool_result: bool = bool(test)
        self.msg = msg
