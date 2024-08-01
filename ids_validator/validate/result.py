"""
This file describes the data class for successes and failures of the
validation tool
"""

import traceback
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate_options import ValidateOptions


@dataclass
class IDSValidationResult:
    """Class for storing data regarding IDS validation test results"""

    success: bool
    """Whether or not the validation test was successful"""
    msg: str
    """Given message for failed assertion"""
    rule: IDSValidationRule
    """Rule to apply to IDS data"""
    idss: List[Tuple[str, int]]
    """Tuple of ids_names and occurrences"""
    tb: traceback.StackSummary
    """A stack of traceback frames"""
    nodes_dict: Dict[Tuple[str, int], Set[str]]
    """
    Set of nodes that have contributed in this result, identified by a combination of
    the ids name and occurence
    """
    imas_uri: str
    """URI of dbentry being tested"""
    exc: Optional[Exception] = None
    """Exception that was encountered while running validation test"""


@dataclass
class IDSValidationResultCollection:
    """Class for collection of all results of validation run"""

    results: List[IDSValidationResult]
    """List of result objects"""
    coverage_dict: Dict[Tuple[str, int], Dict[str, float]]
    """Dict with number of filled, visited and overlapping nodes per ids/occ"""
    validate_options: ValidateOptions
    """Options which with validation run was started"""
