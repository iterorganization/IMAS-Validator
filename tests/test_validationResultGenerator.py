import pytest
import os
from datetime import datetime
from typing import List, Optional
from xml.dom import minidom
import traceback
from pathlib import Path

from ids_validator.report.validationResultGenerator import ValidationResultGenerator
from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.result import IDSValidationResult


def dummy_rule_function():
    pass


def test_error_result():
    # Create an error result, similar to ResultCollector.add_error_result()
    result = IDSValidationResult(
        False,
        "",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {},
        exc=RuntimeError("Dummy exception"),
    )
    result_generator = ValidationResultGenerator([result])
    print(str(result_generator))
    # Write tests below....


def test_successful_assert():
    # Create a successful assert result, similar to ResultCollector.assert_()
    result = IDSValidationResult(
        True,
        "Optional message",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): ["a", "b", "c"]},
        exc=None,
    )
    result_generator = ValidationResultGenerator([result])
    # Write tests below....


def test_failed_assert():
    # Create a failed assert esult, similar to ResultCollector.assert_()
    result = IDSValidationResult(
        False,
        "Optional message",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): ["a", "b", "c"]},
        exc=None,
    )
    result_generator = ValidationResultGenerator([result])
    # Write tests below....
