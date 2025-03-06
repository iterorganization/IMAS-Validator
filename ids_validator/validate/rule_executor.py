"""
This file describes the validation loop in which the rules are applied to the
IDS data
"""

import logging
import pdb
import sys
from typing import Iterator, List, Optional, Tuple

from imaspy import DBEntry
from imaspy.ids_toplevel import IDSToplevel
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from rich.progress import Progress

from ids_validator.exceptions import InternalValidateDebugException
from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate_options import ValidateOptions

logger = logging.getLogger(__name__)

IDSInstance = Tuple[IDSToplevel, str, int]


class RuleExecutor:
    """Class for matching rules and idss and executing rules"""

    def __init__(
        self,
        db_entry: DBEntry,
        rules: List[IDSValidationRule],
        result_collector: ResultCollector,
        validate_options: ValidateOptions,
    ):
        """Initialize RuleExecutor

        Args:
            db_entry: An opened DBEntry.
            rules: List of rules to apply to the data.
            result_collector: ResultCollector object that stores the results after
                execution
            validate_options: Dataclass for validate options
        """
        if validate_options is None:
            validate_options = ValidateOptions()
        self.db_entry = db_entry
        self.rules = rules
        self.result_collector = result_collector
        self.validate_options = validate_options
        self.progress = Progress()

    def apply_rules_to_data(self) -> None:
        """Apply set of rules to the Data Entry."""
        logger.info("Started executing rules")
        for ids_instances, rule in self.find_matching_rules():
            ids_toplevels = [ids[0] for ids in ids_instances]
            idss = [(ids[1], ids[2]) for ids in ids_instances]
            self.result_collector.set_context(rule, ids_instances)
            idss_str = ", ".join(
                sorted(f"{ids_name}:{ids_occ}" for ids_name, ids_occ in idss)
            )
            logger.info(f"Running {rule.name} on {idss_str}")
            self.run(rule, ids_toplevels)

    def run(self, rule: IDSValidationRule, ids_toplevels: List[IDSToplevel]) -> None:
        res_num = len(self.result_collector.results)
        try:
            rule.apply_func(ids_toplevels)
        except Exception as exc:
            tb = exc.__traceback__
            if isinstance(exc, InternalValidateDebugException):
                tbi = tb
                # make sure the last frame in the traceback (where pdb is dropped)
                # represents the validation function itself, not the assert_ function
                while tbi is not None and tbi.tb_next is not None:
                    if tbi.tb_next.tb_frame.f_code.co_name == "assert_":
                        tbi.tb_next = None
                        break
                    tbi = tbi.tb_next
            else:
                self.result_collector.add_error_result(exc)
            if self.validate_options.use_pdb:
                self.progress_stop()
                pdb.post_mortem(tb)
                self.progress_start()
        finally:
            if len(self.result_collector.results) == res_num:
                logger.info(
                    f"No assertions in {rule.name}. "
                    "Make sure the validation test is testing something "
                    "with an assert statement."
                )

    def find_matching_rules(
        self,
    ) -> Iterator[Tuple[List[IDSInstance], IDSValidationRule]]:
        """Find combinations of rules and their relevant ids instances

        Yields:
            tuple of ids_instances, ids_names, ids_occurrences, validation rule
        """

        ids_list = self._get_ids_list()
        self.progress_start()
        t1 = self.progress.add_task("[red]Processing...", total=len(ids_list))
        for ids_name, occurrence in ids_list:
            ids_instance = self._load_ids_instance(ids_name, occurrence)
            if ids_instance is None:
                continue
            ids_version = Version(ids_instance[0]._dd_version)
            # match with first ids_name to prevent matching the same rule multiple
            # times for multi-ids
            filtered_rules = [
                rule
                for rule in self.rules
                if (rule.ids_names[0] == ids_name or rule.ids_names[0] == "*")
                and (rule.ids_occs[0] == occurrence or rule.ids_occs[0] is None)
                and ids_version in SpecifierSet(rule.version)
            ]
            for rule in filtered_rules:
                self.progress.update(t1, advance=1 / len(filtered_rules))
                idss = [ids_instance]
                # get rest of idss for multi-validation rules.
                # unoptimized algorithm, change if performance ever becomes problem.
                for name, occ in zip(rule.ids_names[1:], rule.ids_occs[1:]):
                    assert occ is not None
                    instance = self._load_ids_instance(name, occ)
                    if instance is None:
                        continue
                    idss.append(instance)
                if not len(idss) == len(rule.ids_names):
                    if self.validate_options.stop_at_load_error:
                        raise ValueError("Number of inputs not the same as required")
                    else:
                        continue
                yield idss, rule
        self.progress_stop()

    def _load_ids_instance(
        self, ids_name: str, occurrence: int
    ) -> Optional[IDSInstance]:
        logger.debug(f"Processing IDS: {ids_name}, occurrence = {occurrence}")
        try:
            ids_instance = (
                self.db_entry.get(ids_name, occurrence, autoconvert=False),
                ids_name,
                occurrence,
            )
        except Exception as e:
            logger.error(
                f"Unable to load IDS: {ids_name}, occurrence = {occurrence}, "
                f"uri: {self.db_entry.uri}"
            )
            if self.validate_options.stop_at_load_error:
                raise e
            else:
                ids_instance = None
        return ids_instance

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

    def progress_start(self) -> None:
        """Start progress object if in interactive environment"""
        if sys.stdout.isatty():
            self.progress.start()
            # self.progress.refresh()

    def progress_stop(self) -> None:
        """Stop progress object if in interactive environment"""
        self.progress.stop()
