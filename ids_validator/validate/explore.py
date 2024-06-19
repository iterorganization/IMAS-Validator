"""
This file describes the main function for the IMAS IDS validation tool
"""

import logging
from pathlib import Path

from rich import print
from rich.tree import Tree

from ids_validator.rules.loading import load_docs
from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate_options import ValidateOptions

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
    for rule_dir in docs.rule_dirs:
        rule_dir_branch = tree.add(f"[red]{rule_dir.name}")

        for rule_set in rule_dir.rule_sets:
            rule_set_branch = rule_dir_branch.add(f"[red]{rule_set.name}")
            rule_set_branch.add(f"[blue]{rule_set.docstring}")

            for rule_file in rule_set.rule_files:
                file_name_branch = rule_set_branch.add(f"[red]{rule_file.name}")
                file_name_branch.add(f"[blue]{rule_file.docstring}")

                for rule in rule_file.rules:
                    func_name_branch = file_name_branch.add(f"[red]{rule.name}")
                    ids_names = ", ".join(rule.ids_names)
                    func_name_branch.add(
                        f"[dim white]Applies to IDSs: [/][green]{ids_names}"
                    )
                    if docstring_level == 0:
                        ds = ""
                    elif docstring_level == 1:
                        ds = rule.docstring.split("\n")[0]
                        ds = f"{ds}..."
                        func_name_branch.add(f"[blue]{ds}")
                    elif docstring_level == 2:
                        ds = rule.docstring
                        func_name_branch.add(f"[blue]{ds}")
    print(tree)
