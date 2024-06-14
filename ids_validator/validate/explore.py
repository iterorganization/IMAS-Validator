"""
This file describes the main function for the IMAS IDS validation tool
"""

import logging

from rich import print
from rich.tree import Tree
from pathlib import Path

from ids_validator.validate_options import RuleFilter, ValidateOptions
from ids_validator.rules.loading import load_docs
from ids_validator.validate.result_collector import ResultCollector

logger = logging.getLogger(__name__)

default_val_opts = ValidateOptions()


def explore(
    validate_options: ValidateOptions = default_val_opts,
    show_empty: bool = True,
    docstring_level: int = 1,
) -> None:
    """
    Main function
    Args:
        imas_uri: url for DBEntry object
        validate_options: dataclass with options for validate function

    Returns:
        List of IDSValidationResult objects
    """

    result_collector = ResultCollector(validate_options=validate_options)
    docs = load_docs(
        result_collector=result_collector,
        validate_options=validate_options,
        show_empty=show_empty,
    )
    tree = Tree("[red]Explore Tool")
    for rule_dir, rule_dir_dict in docs.items():
        rule_dir_branch = tree.add(f"[red]{rule_dir}")

        for rule_set, rule_set_dict in rule_dir_dict.items():
            if rule_set == "docstring":
                continue
            rule_set_branch = rule_dir_branch.add(f"[red]{rule_set}")
            rule_set_branch.add(f"[blue]{rule_set_dict['docstring']}")

            for file_name, file_name_dict in rule_set_dict.items():
                if file_name == "docstring":
                    continue
                file_name_branch = rule_set_branch.add(f"[red]{file_name}")
                file_name_branch.add(f"[blue]{file_name_dict['docstring']}")

                for func_name, func_name_dict in file_name_dict.items():
                    if func_name == "docstring":
                        continue
                    func_name_branch = file_name_branch.add(f"[red]{func_name}")
                    func_name_branch.add(f"[dim white]Applies to IDSs: [/][green]{', '.join(func_name_dict['ids_names'])}")
                    if docstring_level == 0:
                        ds = ''
                    elif docstring_level == 1:
                        beep = func_name_dict['docstring'].split('\n')[0]
                        ds = f"{beep}..."
                        func_name_branch.add(f"[blue]{ds}")
                    elif docstring_level == 2:
                        ds = func_name_dict['docstring']
                        func_name_branch.add(f"[blue]{ds}")

    print(tree)


if __name__ == "__main__":

    rule_dirs = [
        Path("tests/rulesets/base"),
    ]
    val_options = ValidateOptions(
        use_bundled_rulesets=True,
        apply_generic=True,
        extra_rule_dirs=rule_dirs,
        # rule_filter=RuleFilter(name=["common_ids"], ids=[]),
    )
    explore(
        validate_options=val_options,
        show_empty=True,
        docstring_level=2,
    )
