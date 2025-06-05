import argparse
from typing import Any, List

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


def prepare_rule_filter_object(args: argparse.Namespace) -> RuleFilter:
    """
    Returns RuleFilter object filled with data from CLI arguments
    Uses args.filter, args.filter_name and args.filter_ids
    """
    name_filter = []
    ids_filter = []

    # parse --filter_name and --filter_ids
    name_filter.extend(flatten_2d_list_or_return_empty(args.filter_name))
    ids_filter.extend(flatten_2d_list_or_return_empty(args.filter_ids))

    # parse --filter and split it into names and ids_names
    ids_filter.extend(
        list(
            set(flatten_2d_list_or_return_empty(args.filter)).intersection(
                get_all_ids_names()
            )
        )
    )
    name_filter.extend(
        list(set(flatten_2d_list_or_return_empty(args.filter)) - set(ids_filter))
    )

    return RuleFilter(name=name_filter, ids=ids_filter)
