"""
This file describes the validation loop in which the rules are applied to the
IDS data
"""

from typing import List, Tuple, Generator

from imaspy import DBEntry

from ids_validator.rules.data import IDSValidationRule


def apply_rules_to_data(db_entry: DBEntry, rules: List[IDSValidationRule]) -> None:
    """Apply set of rules to the Data Entry.

    Args:
        db_entry: An opened DBEntry.
        rules: List of rules to apply to the data.
    """
    for ids_instances, rule in find_matching_rules(db_entry, rules):
        rule.apply_func(ids_instances)


def find_matching_rules(db_entry: DBEntry, rules: List[IDSValidationRule]) -> Generator:
    """Find combinations of rules and their relevant ids instances

    Args:
        db_entry: An opened DBEntry.
        rules: List of rules to apply to the data.

    Yields:
        Tuple[Tuple[IDSToplevel], IDSValidationRule]: idss
    """
    if any([len(rule.ids_names) > 1 for rule in rules]):
        raise NotImplementedError("Multi-IDS validation rules not implemented yet")
    idss = _get_ids_list(db_entry)
    for ids_name, occurrence in idss:
        ids = db_entry.get(ids_name, occurrence)
        filtered_rules = [
            rule
            for rule in rules
            if (rule.ids_names[0] == ids_name or rule.ids_names[0] == "*")
        ]
        for rule in filtered_rules:
            yield (ids,), rule


def _get_ids_list(db_entry: DBEntry) -> List[Tuple[str, int]]:
    """Get list of all ids occurrences combined with their corresponding names

    Args:
        db_entry: An opened DBEntry.

    Returns:
        List of tuples with ids names and occurrences
    """
    idss: List[Tuple[str, int]] = []  # (ids_name, occurrence)
    for ids_name in db_entry.factory.ids_names():
        occurrence_list = db_entry.list_all_occurrences(ids_name)
        for occurrence in occurrence_list:
            idss.append((ids_name, occurrence))
    return idss
