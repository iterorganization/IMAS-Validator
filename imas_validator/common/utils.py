import argparse
from typing import Any, List, Tuple

import imas  # type: ignore

from imas_validator.validate_options import RuleFilter


def get_all_ids_names() -> List[str]:
    """
    Returns list of strings representing all IDSs from Data Dictionary
    """
    return imas.IDSFactory().ids_names()


def flatten_2d_list_or_return_empty(list_2d: List[List[Any]]) -> List[Any]:
    """
    Returns flattened 2d list
    NOTE: when [str] will be passed instead of [[str]],
    list of single characters will be returned
    """
    return [
        nested_element for nested_array in list_2d for nested_element in nested_array
    ]


def _split_names_and_ids(
    mixed: List[str], names: List[str], ids: List[str]
) -> Tuple[List[str], List[str]]:
    """Return (names, ids), adding the IDS names of ``mixed`` to ``ids`` and its
    other strings to ``names``"""
    mixed_ids = set(mixed).intersection(get_all_ids_names())
    return names + list(set(mixed) - mixed_ids), ids + list(mixed_ids)


def prepare_rule_filter_object(args: argparse.Namespace) -> RuleFilter:
    """
    Returns RuleFilter object filled with data from CLI arguments
    Uses args.filter, args.filter_name, args.filter_ids, and the matching
    args.exclude, args.exclude_name and args.exclude_ids
    """

    def get(option: str) -> List[str]:
        return flatten_2d_list_or_return_empty(getattr(args, option, None) or [])

    # --filter and --exclude are split into rule names and IDS names
    name_filter, ids_filter = _split_names_and_ids(
        get("filter"), get("filter_name"), get("filter_ids")
    )
    exclude_name, exclude_ids = _split_names_and_ids(
        get("exclude"), get("exclude_name"), get("exclude_ids")
    )
    return RuleFilter(
        name=name_filter,
        ids=ids_filter,
        exclude_name=exclude_name,
        exclude_ids=exclude_ids,
    )
