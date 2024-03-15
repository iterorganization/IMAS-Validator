from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from ids_validator.rules.data import IDSValidationRule


@dataclass(frozen=True)
class RuleFilter:
    """Class for filtering individual rules.

    For more information, see :ref:`rule filtering`
    """

    name: List[str] = field(default_factory=list)
    """List of strings that should be present in rule name"""
    ids: List[str] = field(default_factory=list)
    """List of strings that should be present rule ids_names"""

    def is_selected(self, rule: IDSValidationRule) -> bool:
        """Check whether rule should be applied or not

        Args:
            rule: rule to be checked

        Returns:
            Whether or not validation rule should be applied
        """
        if not all(x in rule.name for x in self.name):
            return False
        if not all(x in rule.ids_names for x in self.ids):
            return False
        return True


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
    rule_filter: RuleFilter = field(default_factory=RuleFilter)
    """Dictionary of filter criteria"""
