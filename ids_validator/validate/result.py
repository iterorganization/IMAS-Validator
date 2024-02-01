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

    bool_result: bool
    msg: str
    rule: IDSValidationRule
    idss: Tuple[Tuple[str, int]]
    tb: traceback.StackSummary
    frame_idx: int
    exc: Optional[Exception] = None
