from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ValidateOptions:
    """Dataclass for validate options"""

    extra_rule_dirs: List[Path] = field(default_factory=list)
    """List of names for ruleset groups that should be applied"""
    apply_generic: bool = True
    """Whether or not to apply the generic ruleset"""
    use_pdb: bool = False
    """Whether or not to drop into debugger for failed tests"""
