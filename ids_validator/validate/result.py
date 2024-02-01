"""
This file describes the data class for successes and failures of the
validation tool
"""

import traceback
from dataclasses import dataclass
from typing import Optional, Tuple

from ids_validator.rules.data import IDSValidationRule


@dataclass
class IDSValidationResult:
    """Class for storing data regarding IDS validation test results"""

    success: bool
    """Whether or not the validation test was successful"""
    msg: str
    """Given message for failed assertion"""
    rule: IDSValidationRule
    """Rule to apply to IDS data"""
    idss: Tuple[Tuple[str, int], ...]
    """Tuple of ids_names and occurrences"""
    tb: traceback.StackSummary
    """A stack of traceback frames"""
    exc: Optional[Exception] = None
    """Exception that was encountered while running validation test"""
