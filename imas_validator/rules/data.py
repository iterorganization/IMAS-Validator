"""
This file describes the data class for rules that are saved and generated for
the validation tool
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import imas  # type: ignore

from imas_validator.validate.ids_wrapper import IDSWrapper


class IDSValidationRule:
    """
    Object holding the validation rule function and other relevant data
    """

    def __init__(
        self,
        rule_path: Path,
        func: Callable,
        *ids_names: str,
        version: str = "",
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
        self.name = f"{rule_path.parts[-2]}/{rule_path.parts[-1]}:{self.func.__name__}"
        self.ids_names, self.ids_occs = self.parse_ids_names(*ids_names)
        self.version = version
        self.kwfields = kwfields
        # kwfields explicitly parsed

    def apply_func(self, ids_instances: List[imas.ids_toplevel.IDSToplevel]) -> None:
        """Run the validation function with wrapped input arguments

        Args:
            ids_instances: ids instances to be validated
        """
        args = [IDSWrapper(ids) for ids in ids_instances]
        self.func(*args)

    def parse_ids_names(
        self, *ids_names: str
    ) -> Tuple[Tuple[str, ...], Tuple[Optional[int], ...]]:
        """Extract ids names and occurrences from ids_names input

        Args:
            ids_names: Names of ids instances to be validated

        Returns:
            Parsed IDS names and occurrence numbers.
        """
        ids_names_list = []
        ids_occs_list = []
        for ids_name in ids_names:
            name, sep, occ = ids_name.partition(":")
            if sep and not occ.isnumeric():
                raise ValueError(
                    f"Cannot parse '{name}': the occurrence number {occ} should be an "
                    "integer"
                )
            ids_names_list.append(name)
            ids_occs_list.append(None if not sep else int(occ))
        if not (len(ids_names_list) == len(ids_occs_list) >= 1):
            raise ValueError(
                "No IDS names provided to '@validator'. Provide at least one IDS name "
                "that the validation rule applies to."
            )
        if len(ids_occs_list) > 1 and any([x is None for x in ids_occs_list]):
            raise ValueError(
                "No occurence numbers provided to '@validator' for multi-IDS "
                "validation. For more information, visit: "
                "https://imas-validator.readthedocs.io/en/stable/defining_rules.html"
            )
        return tuple(ids_names_list), tuple(ids_occs_list)


class ValidatorRegistry:
    """
    Example:
        .. code-block:: python

            @val_registry.validator('core_profiles')
            def ids_rule(cp):
                assert cp != None
    """

    def __init__(self, rule_path: Path) -> None:
        self.validators: List[IDSValidationRule] = []
        self.rule_path: Path = rule_path

    def validator(self, *ids_names: str, version: str = "") -> Callable:
        """Decorator to register functions as validation rules

        The validation rule function will be called with the requested IDSs as
        arguments.

        Args:
            ids_names: Names of ids instances to be validated, for example
                ``"core_profiles"`` or ``"pf_active"``. Use a wildcard ``"*"`` to accept
                any IDS. Add the occurrence number by appending the ids name with
                an integer `>=0` like ``"summary:2"``. Occurrence number is required
                for multi-IDS validation.

        Example:
            .. code-block:: python

                @validator("core_profiles")
                def rule_for_core_profiles(cp):
                    \"\"\"Rule that applies to any core_profiles IDS.\"\"\"
                    ... # Write rules

                @validator("*")
                def rule_for_any_ids(ids):
                    \"\"\"Rule that applies to any IDS.\"\"\"
                    ... # Write rules
        """

        # explicit kwfields
        def decorator(func: Callable) -> Callable:
            rule = IDSValidationRule(self.rule_path, func, *ids_names, version=version)
            self.validators.append(rule)
            return func

        return decorator
