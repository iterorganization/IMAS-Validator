"""
This file describes the data class for successes and failures of the
validation tool
"""

from typing import List, Union
from pathlib import Path
import traceback

from ids_validator.validate.ids_wrapper import IDSWrapper


class IDSValidationResult:
    """"""

    def __init__(
        self, test: Union[IDSWrapper, bool], msg: str, rule, ids_names, ids_occurrences
    ):
        func = rule.func
        self.func_name = func.__name__
        self.func_docs = func.__doc__
        self.ids_names: list[str] = ids_names
        self.ids_occurences: List[int] = ids_occurrences

        info = traceback.extract_stack()
        idx = -3
        assert info[idx + 1].name == "assert_"
        assert info[idx].name == self.func_name
        file_path = Path(info[idx].filename)
        self.file_name = file_path.relative_to(file_path.parents[2])
        self.lineno: int = info[idx].lineno
        self.code_context = info[idx].line
        self.bool_result: bool = bool(test)
        self.msg = msg
