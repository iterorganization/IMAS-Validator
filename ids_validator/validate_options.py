from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class ValidateOptions:
    """Dataclass for validate options"""

    rulesets: List[str] = field(default_factory=list)
    """Names of rulesets to be applied"""
    extra_rule_dirs: List[Path] = field(default_factory=list)
    """List of names for ruleset groups that should be applied"""
    apply_generic: bool = True
    """Whether or not to apply the generic ruleset"""
    use_pdb: bool = False
    """Whether or not to drop into debugger for failed tests"""
    func_filter: Dict[str, List[str]] = ({},)
    """Dictionary of filter criteria"""
