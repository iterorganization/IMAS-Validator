from typing import Any, List


def get_all_ids_names() -> List[str]:
    try:
        from data_dictionary import idsinfo  # type: ignore

        return idsinfo.IDSInfo().get_ids_names()
    except ImportError:
        try:
            from data_dictionary.idsdef import IDSDef  # type: ignore

            ids_def = IDSDef()
            return ids_def.get_ids_names()
        except ImportError:
            import imas  # type: ignore

            return [ids.value for ids in list(imas.IDSName)]


def flatten_2d_list_or_return_empty(list_2d: List[List[Any]]) -> List[Any]:
    """
    Returns flattened 2d list
    NOTE: when [str] will be passed instead of [[str]],
    list of single characters will be returned
    """
    return [
        nested_element for nested_array in list_2d for nested_element in nested_array
    ]
