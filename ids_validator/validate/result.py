"""
This file describes the data class for successes and failures of the
validation tool
"""

from typing import Union, Tuple
from pathlib import Path
import traceback

from ids_validator.validate.ids_wrapper import IDSWrapper
from ids_validator.rules.data import IDSValidationRule


class IDSValidationResult:
    """Class for storing data regarding IDS validation test results"""

    def __init__(
        self,
        test: Union[IDSWrapper, bool],
        msg: str,
        rule: IDSValidationRule,
        idss: Tuple[Tuple[str, int]],
        exc: Union[None, Exception] = None,
    ):
        """Initialize IDSValidationResult

        Args:
            test: Expression to evaluate in test
            msg: Given message for failed assertion
            rule: Rule to apply to IDS data
            idss: Tuple of ids_names and occurrences
            exc: Exception that was encountered while running validation test
        """
        self.bool_result: bool = bool(test)
        self.msg = msg
        self.rule = rule
        self.idss = idss

        if exc is None:
            info = traceback.extract_stack()
            idx = -3
            assert info[idx + 1].name == "assert_"
            assert info[idx].name == self.func_name
            self.error = False
        else:
            info = traceback.extract_tb(exc.__traceback__)
            idx = 1
            assert info[idx].name == self.func_name
            self.error = True
        file_path = Path(info[idx].filename)
        self.file_name = file_path.relative_to(file_path.parents[2])
        self.lineno: int = info[idx].lineno
        self.code_context = info[idx].line

    @property
    def func_name(self):
        return self.rule.func.__name__

    @property
    def func_docs(self):
        return self.rule.func.__doc__
