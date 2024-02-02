"""
This file describes the validation loop in which the rules are applied to the
IDS data
"""

from typing import Iterator, List, Tuple

from imaspy import DBEntry
from imaspy.ids_toplevel import IDSToplevel

from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.result_collector import ResultCollector

IDSInstance = Tuple[IDSToplevel, str, int]


class RuleExecutor:
    """Class for matching rules and idss and executing rules"""

    def __init__(
        self,
        db_entry: DBEntry,
        rules: List[IDSValidationRule],
        result_collector: ResultCollector,
    ):
        """Initialize RuleExecutor

        Args:
            db_entry: An opened DBEntry.
            rules: List of rules to apply to the data.
            result_collector: ResultCollector object that stores the results after
                execution
        """
        self.db_entry = db_entry
        self.rules = rules
        self.result_collector = result_collector

    def apply_rules_to_data(self) -> None:
        """Apply set of rules to the Data Entry."""
        for ids_instances, rule in self.find_matching_rules():
            ids_toplevels = [ids[0] for ids in ids_instances]
            idss = [(ids[1], ids[2]) for ids in ids_instances]
            self.result_collector.set_context(rule, idss)
            try:
                rule.apply_func(ids_toplevels)
            except Exception as e:
                self.result_collector.add_error_result(e)

    def find_matching_rules(
        self,
    ) -> Iterator[Tuple[List[IDSInstance], IDSValidationRule]]:
        """Find combinations of rules and their relevant ids instances

        Yields:
            Tuple[List[IDSInstance], IDSValidationRule]:
                tuple of ids_instances, ids_names, ids_occurrences, validation rule
        """

        if any([len(rule.ids_names) > 1 for rule in self.rules]):
            raise NotImplementedError("Multi-IDS validation rules not implemented yet")
        ids_list = self._get_ids_list()
        for ids_name, occurrence in ids_list:
            idss = [(self.db_entry.get(ids_name, occurrence), ids_name, occurrence)]
            filtered_rules = [
                rule
                for rule in self.rules
                if (rule.ids_names[0] == ids_name or rule.ids_names[0] == "*")
            ]
            for rule in filtered_rules:
                yield idss, rule

    def _get_ids_list(self) -> List[Tuple[str, int]]:
        """Get list of all ids occurrences combined with their corresponding names

        Returns:
            List of tuples with ids names and occurrences
        """
        ids_list: List[Tuple[str, int]] = []  # (ids_name, occurrence)
        for ids_name in self.db_entry.factory.ids_names():
            occurrence_list = self.db_entry.list_all_occurrences(ids_name)
            for occurrence in occurrence_list:
                ids_list.append((ids_name, occurrence))
        return ids_list
