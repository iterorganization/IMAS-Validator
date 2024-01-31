"""
This file describes the data class for rules that are saved and generated for
the validation tool
"""

from typing import List, Any, Dict, Callable
from pathlib import Path

from imaspy.ids_toplevel import IDSToplevel

from ids_validator.validate.ids_wrapper import IDSWrapper


class IDSValidationRule:
    """
    Object holding the validation rule function and other relevant data
    """

    def __init__(
        self,
        rule_path: Path,
        func: Callable,
        *ids_names: str,
        **kwfields: Dict[str, Any],
    ):
        """Initialize IDSValidationRule

        Args:
            rule_path: Path to file where the rule is defined
            func: Function that defines validation rules
            ids_names: Names of ids instances to be validated
            kwfields: keyword arguments to be inputted in the validation function
        """
        self.func = func
        # name: ruleset/file/func_name
        self.name = f"{rule_path.parts[-2]}/{rule_path.parts[-1]}/{self.func.__name__}"
        self.ids_names = list(ids_names)
        self.kwfields = kwfields
        # kwfields explicitly parsed

    def apply_func(self, ids_instances: List[IDSToplevel]):
        """Run the validation function with wrapped input arguments

        Args:
            ids_instances: ids instances to be validated
        """
        if len(ids_instances) > 1:
            raise NotImplementedError("Multi-IDS validation rules not implemented yet")
        args = [IDSWrapper(ids) for ids in ids_instances]
        self.func(*args, **self.kwfields)


class ValidatorRegistry:
    """
    EXAMPLE:
    @val_registry.ids_validator('core_profiles')
    def ids_rule(cp):
      cp != None
    """

    def __init__(self, rule_path: Path):
        self.validators: List[IDSValidationRule] = []
        self.rule_path: Path = rule_path

    def ids_validator(self, *ids_names: str):
        # explicit kwfields
        def decorator(func: Callable):
            self.validators.append(IDSValidationRule(self.rule_path, func, *ids_names))
            return func

        return decorator
