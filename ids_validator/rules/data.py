"""
This file describes the data class for rules that are saved and generated for
the validation tool
"""
from typing import List, Any, Dict, Callable
from pathlib import Path

from ids_validator.validate.ids_wrapper import IDSWrapper


class IDSValidationRule:
    """"""

    def __init__(
        self,
        rule_path: Path,
        func: Callable,
        *ids_names: str,
        **kwfields: Dict[str, Any],
    ):
        self.func = func
        # name: ruleset/file/func_name
        self.name = f"{rule_path.parts[-2]}/{rule_path.parts[-1]}/{self.func.__name__}"
        self.ids_names = ids_names
        self.kwfields = kwfields
        # kwfields explicitly parsed

    def apply(self, *args, **kwargs):
        if set(arg.name for arg in args) != set(self.ids_names):
            raise ValueError()
        args = [IDSWrapper(arg) for arg in args]
        self.func(*args, **kwargs)


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
