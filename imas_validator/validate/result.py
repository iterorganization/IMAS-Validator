"""
This file describes the data class for successes and failures of the
validation tool
"""

import traceback
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from imas_validator.rules.data import IDSValidationRule
from imas_validator.validate_options import ValidateOptions

NodesDict = Dict[Tuple[str, int], Set[str]]


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
    nodes_dict: NodesDict
    """
    Set of nodes that have contributed in this result, identified by a combination of
    the ids name and occurence
    """
    exc: Optional[Exception] = None
    """Exception that was encountered while running validation test"""


@dataclass
class CoverageMap:
    """Class for tracking coverage of given IDSTopLevel"""

    filled: int
    """Number of filled nodes in validation process"""
    visited: int
    """Number of visited nodes in validation process"""
    overlap: int
    """Number of nodes both filled and visited in validation process"""


CoverageDict = Dict[Tuple[str, int], CoverageMap]


@dataclass
class IDSValidationResultCollection:
    """Class for collection of all results of validation run"""

    results: List[IDSValidationResult]
    """List of result objects"""
    coverage_dict: CoverageDict
    """Dict with number of filled, visited and overlapping nodes per ids/occ"""
    validate_options: ValidateOptions
    """Options which with validation run was started"""
    imas_uri: str
    """URI of dbentry being tested"""
