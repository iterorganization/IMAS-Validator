"""This file contains the dataclass object for the explorer tool"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass(frozen=True)
class RuleData:
    """Dataclass for explorer rule data"""

    name: str
    """Name of validation function"""
    docstring: str
    """Function level docstring"""
    path: Path = field(default_factory=Path)
    """Path to file in which validation function is defined"""
    ids_names: Tuple[str] = field(default_factory=tuple)
    """IDS names that the validation function should be applied to"""


@dataclass(frozen=True)
class RuleFileData:
    """Dataclass for explorer rule file data"""

    name: str
    """Name of file"""
    docstring: str
    """Module level docstring"""
    rules: List[RuleData] = field(default_factory=list)
    """List of RuleData objects"""


@dataclass(frozen=True)
class RuleSetData:
    """Dataclass for explorer rule set data"""

    name: str
    """Name of ruleset"""
    docstring: str
    """Folder level docstring"""
    rule_files: List[RuleFileData] = field(default_factory=list)
    """List of RuleFile objects"""


@dataclass(frozen=True)
class RuleDirData:
    """Dataclass for explorer rule dir data"""

    name: str
    """Name of ruledir"""
    rule_sets: List[RuleSetData] = field(default_factory=list)
    """List of RuleSet objects"""


@dataclass(frozen=True)
class ExplorerData:
    """Dataclass for explorer data"""

    rule_dirs: List[RuleDirData] = field(default_factory=list)
    """List of RuleDir objects"""
