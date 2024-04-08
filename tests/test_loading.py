import logging
from collections import Counter
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from ids_validator.exceptions import (
    InvalidRulesetName,
    InvalidRulesetPath,
    WrongFileExtensionWarning,
)
from ids_validator.rules.ast_rewrite import run_path
from ids_validator.rules.data import ValidatorRegistry
from ids_validator.rules.loading import (
    discover_rule_modules,
    discover_rulesets,
    filter_rules,
    filter_rulesets,
    load_rules_from_path,
)
from ids_validator.validate_options import RuleFilter, ValidateOptions


@pytest.fixture(scope="function")
def res_collector():
    mock = MagicMock()
    # MagicMock doesn't automatically create mock attributes starting with 'assert'
    mock.assert_ = Mock()
    return mock


def test_load_bundled_rulesets():
    discovered_rulesets = discover_rulesets(ValidateOptions(use_bundled_rulesets=True))
    assert len(discovered_rulesets) == 1
    assert (
        discovered_rulesets[0]
        == discovered_rulesets[0].parents[2] / "assets" / "rulesets" / "generic"
    )


def test_discover_rulesets_explicit(caplog):
    extra_rule_dirs = [
        Path("tests/rulesets"),
        Path("tests/rulesets/base"),
        Path("tests/rulesets/base/generic"),
    ]
    unfiltered_rulesets = [
        Path("tests/rulesets/base"),
        Path("tests/rulesets/env_var"),
        Path("tests/rulesets/env_var2"),
        Path("tests/rulesets/exceptions"),
        Path("tests/rulesets/base/generic"),
        Path("tests/rulesets/base/ITER-MD"),
        Path("tests/rulesets/validate-test"),
        Path("tests/rulesets/filter_test"),
    ]
    validate_options = ValidateOptions(
        extra_rule_dirs=extra_rule_dirs,
        use_bundled_rulesets=False,
    )
    assert Counter(discover_rulesets(validate_options=validate_options)) == Counter(
        unfiltered_rulesets
    )
    log_text = (
        "Found 8 rulesets: ITER-MD, base, env_var, env_var2, exceptions, filter_test, "
        "generic, validate-test"
    )
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.INFO, log_text)
    ]


def test_discover_rulesets_env_var(monkeypatch, caplog):
    monkeypatch.setenv("RULESET_PATH", "tests/rulesets/env_var:tests/rulesets/env_var2")
    unfiltered_rulesets = [
        Path("tests/rulesets/env_var/generic"),
        Path("tests/rulesets/env_var/ITER-MD"),
        Path("tests/rulesets/env_var2/generic"),
    ]
    validate_options = ValidateOptions(extra_rule_dirs=[], use_bundled_rulesets=False)
    assert Counter(discover_rulesets(validate_options=validate_options)) == Counter(
        unfiltered_rulesets
    )
    assert caplog.record_tuples == [
        (
            "ids_validator.rules.loading",
            logging.INFO,
            "Found 3 rulesets: ITER-MD, generic, generic",
        )
    ]


def test_discover_rulesets_invalid_env_var(monkeypatch):
    monkeypatch.setenv(
        "RULESET_PATH", "tests/rulesets/env_var:tests/rulesets/env_var_invalid"
    )
    validate_options = ValidateOptions(extra_rule_dirs=[])
    with pytest.raises(InvalidRulesetPath):
        discover_rulesets(validate_options=validate_options)


# def test_discover_rulesets_entrypoints():
#     pass


def test_filter_rulesets_all(caplog):
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    filtered_rulesets = [Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    validate_options = ValidateOptions(
        rulesets=["ITER-MD"],
        apply_generic=True,
    )
    assert Counter(
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)
    ) == Counter(filtered_rulesets)
    assert caplog.record_tuples == [
        (
            "ids_validator.rules.loading",
            logging.INFO,
            "Using 2 / 3 rulesets",
        )
    ]


def test_filter_rulesets_none(caplog):
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    filtered_rulesets = []
    validate_options = ValidateOptions(
        rulesets=[],
        apply_generic=False,
    )
    assert Counter(
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)
    ) == Counter(filtered_rulesets)
    assert caplog.record_tuples == [
        (
            "ids_validator.rules.loading",
            logging.INFO,
            "Using 0 / 3 rulesets",
        )
    ]


def test_filter_rulesets_apply_generic(caplog):
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    filtered_rulesets = [Path(f"{base}/generic")]
    validate_options = ValidateOptions(
        rulesets=[],
        apply_generic=True,
    )
    assert Counter(
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)
    ) == Counter(filtered_rulesets)
    assert caplog.record_tuples == [
        (
            "ids_validator.rules.loading",
            logging.INFO,
            "Using 1 / 3 rulesets",
        )
    ]


def test_filter_rulesets_with_rulesets(caplog):
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    filtered_rulesets = [Path(f"{base}/ITER-MD")]
    validate_options = ValidateOptions(
        rulesets=["ITER-MD"],
        apply_generic=False,
    )
    assert Counter(
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)
    ) == Counter(filtered_rulesets)
    assert caplog.record_tuples == [
        (
            "ids_validator.rules.loading",
            logging.INFO,
            "Using 1 / 3 rulesets",
        )
    ]


def test_filter_rulesets_invalid_ruleset():
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    validate_options = ValidateOptions(
        rulesets=["ITER-MD-woops-typo"],
        apply_generic=False,
    )
    with pytest.raises(InvalidRulesetName):
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)


def test_discover_rule_modules():
    base = "tests/rulesets/base"
    filtered_rulesets = [Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    rule_modules = [
        Path(f"{base}/generic/common_ids.py"),
        Path(f"{base}/generic/core_profiles.py"),
        Path(f"{base}/ITER-MD/common_ids.py"),
        Path(f"{base}/ITER-MD/core_profiles.py"),
    ]
    assert Counter(discover_rule_modules(filtered_rulesets)) == Counter(rule_modules)


def test_load_rules_from_path(res_collector):
    rule_modules = [
        Path("tests/rulesets/base/generic/core_profiles.py"),
    ]
    rules = []
    for path in rule_modules:
        rules += load_rules_from_path(path, res_collector)
    assert len(rules) == 1
    assert rules[0].name == "generic/core_profiles.py/core_profiles_rule"
    assert rules[0].ids_names == ("core_profiles",)
    assert rules[0].kwfields == {}


def test_load_rules_from_path_empty_file(res_collector, caplog):
    path = Path("tests/rulesets/exceptions/generic/empty.py")
    rules = load_rules_from_path(path, res_collector)
    assert len(rules) == 0
    assert caplog.record_tuples == [
        (
            "ids_validator.rules.loading",
            logging.WARNING,
            f"No rules in rule file {path}",
        )
    ]


def test_load_rules_syntax_error(res_collector):
    path = Path("tests/rulesets/exceptions/generic/syntax_error.py")
    with pytest.raises(ZeroDivisionError):
        load_rules_from_path(path, res_collector)


def test_load_rules_file_extension_error(res_collector):
    path = Path("tests/rulesets/exceptions/generic/wrong_file_extension.pie")
    with pytest.raises(WrongFileExtensionWarning):
        load_rules_from_path(path, res_collector)


def test_rewrite_assert_in_loaded_func(res_collector):
    path = Path("tests/rulesets/base/generic/core_profiles.py")
    rules = load_rules_from_path(path, res_collector)
    assert len(rules) == 1
    rules[0].func(1)
    res_collector.assert_.assert_called_with(True)
    res_collector.assert_.reset_mock()
    rules[0].func(None)
    res_collector.assert_.assert_called_with(False)


def test_run_path(res_collector):
    rule_path = Path("tests/rulesets/base/generic/core_profiles.py")
    val_registry = ValidatorRegistry(rule_path)
    run_path(rule_path, val_registry, res_collector)
    assert len(val_registry.validators) == 1


def test_filter_rules(res_collector):
    path = Path("tests/rulesets/filter_test/ITER-MD/core_profiles.py")
    rules = load_rules_from_path(path, res_collector)
    path = Path("tests/rulesets/filter_test/ITER-MD/equilibrium.py")
    rules += load_rules_from_path(path, res_collector)
    assert_filter_rules(rules, 8, RuleFilter())
    assert_filter_rules(rules, 8, RuleFilter(name=[], ids=[]))
    assert_filter_rules(rules, 2, RuleFilter(name=["val_core_profiles"]))
    assert_filter_rules(rules, 2, RuleFilter(name=["val_equilibrium"]))
    assert_filter_rules(rules, 4, RuleFilter(name=["core_profiles"]))
    assert_filter_rules(rules, 4, RuleFilter(name=["equilibrium"]))
    assert_filter_rules(rules, 4, RuleFilter(name=["test"]))
    assert_filter_rules(rules, 4, RuleFilter(ids=["equilibrium"]))
    assert_filter_rules(rules, 4, RuleFilter(ids=["core_profiles"]))
    assert_filter_rules(rules, 2, RuleFilter(name=["test"], ids=["core_profiles"]))
    assert_filter_rules(rules, 2, RuleFilter(name=["test", "4"]))


def assert_filter_rules(rules, res, rule_filter):
    validate_options = ValidateOptions(rule_filter=rule_filter)
    assert len(filter_rules(rules, validate_options=validate_options)) == res
