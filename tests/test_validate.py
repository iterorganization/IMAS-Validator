import logging
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch

import numpy
from imaspy import IDSFactory
from imaspy.exception import DataEntryException

from ids_validator.validate.result import IDSValidationResult
from ids_validator.validate.validate import validate
from ids_validator.validate_options import ValidateOptions

_occurrence_dict = {
    "core_profiles": numpy.array([0]),
    "equilibrium": numpy.array([0]),
}


def list_all_occurrences(ids_name: str):
    return _occurrence_dict.get(ids_name, [])


@lru_cache
def get(ids_name: str, occurrence: int = 0):
    # Trying to get an IDS that isn't filled is an error:
    if occurrence not in list_all_occurrences(ids_name):
        raise DataEntryException(f"IDS {ids_name!r}, occurrence {occurrence} is empty.")

    ids = IDSFactory("3.40.1").new(ids_name)
    ids.ids_properties.comment = f"Test IDS: {ids_name}/{occurrence}"
    ids.ids_properties.homogeneous_time = 1
    # TODO: if needed, we can fill IDSs with specific data
    return ids


def test_validate(caplog):
    module = "ids_validator.validate.validate"
    # patch _check_imas_version for now
    with patch(
        f"{module}.DBEntry",
        spec=True,
        list_all_occurrences=list_all_occurrences,
        get=get,
        factory=IDSFactory("3.40.1"),
    ), patch(f"{module}._check_imas_version"):
        validate_options = ValidateOptions(
            rulesets=["ITER-MD"],
            extra_rule_dirs=[Path("tests/rulesets/validate-test")],
            apply_generic=False,
        )
        results = validate(
            imas_uri="",
            validate_options=validate_options,
        )
        assert len(results) == 3
        assert all(isinstance(res, IDSValidationResult) for res in results)
        results = sorted(results, key=lambda x: x.rule.func.__name__)

        assert results[0].success is False
        assert results[0].msg == ""
        assert results[0].rule.func.__name__ == "validate_test_rule_error"
        assert results[0].idss == [("core_profiles", 0)]
        assert results[0].tb[-1].name == "validate_test_rule_error"
        assert isinstance(results[0].exc, ZeroDivisionError)

        assert results[1].success is False
        assert results[1].msg == "Oh noes it didn't work"
        assert results[1].rule.func.__name__ == "validate_test_rule_fail"
        assert results[1].idss == [("equilibrium", 0)]
        assert results[1].tb[-1].name == "validate_test_rule_fail"
        assert results[1].exc is None

        assert results[2].success is True
        assert results[2].msg == ""
        assert results[2].rule.func.__name__ == "validate_test_rule_success"
        assert results[2].idss == [("core_profiles", 0)]
        assert results[2].tb[-1].name == "validate_test_rule_success"
        assert results[2].exc is None

        assert caplog.record_tuples == [
            (
                "ids_validator.validate.validate",
                logging.WARNING,
                "3 results obtained",
            )
        ]
