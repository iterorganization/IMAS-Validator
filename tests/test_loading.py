import logging
from collections import Counter
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from ids_validator.exceptions import InvalidRulesetName, InvalidRulesetPath
from ids_validator.rules.ast_rewrite import run_path
from ids_validator.rules.data import ValidatorRegistry
from ids_validator.rules.docs_dataclass import (
    ExplorerData,
    RuleData,
    RuleDirData,
    RuleFileData,
    RuleSetData,
)
from ids_validator.rules.loading import (
    discover_rule_modules,
    discover_rulesets,
    filter_rules,
    filter_rulesets,
    load_docs,
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
    # At least the `generic` ruleset is bundled, but possibly more
    assert len(discovered_rulesets) >= 1
    # Verify that all rulesets are in the "assets/rulesets" directory
    ruleset_parents = set(ruleset.parent for ruleset in discovered_rulesets)
    expected_parent = discovered_rulesets[0].parent
    assert ruleset_parents == {expected_parent}
    assert expected_parent.parents[1] / "assets" / "rulesets" == expected_parent
    # Verify there is one generic ruleset bundled:
    ruleset_names = [ruleset.name for ruleset in discovered_rulesets]
    assert "generic" in ruleset_names
    # Verify that all bundled rulesets have a unique name
    assert len(set(ruleset_names)) == len(ruleset_names)


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
        Path("tests/rulesets/base/test-ruleset"),
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
        "Found 8 rulesets: base, env_var, env_var2, exceptions, "
        "filter_test, generic, test-ruleset, validate-test"
    )
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.INFO, log_text)
    ]


def test_discover_rulesets_env_var(monkeypatch, caplog):
    monkeypatch.setenv("RULESET_PATH", "tests/rulesets/env_var:tests/rulesets/env_var2")
    unfiltered_rulesets = [
        Path("tests/rulesets/env_var/generic"),
        Path("tests/rulesets/env_var/test-ruleset"),
        Path("tests/rulesets/env_var2/generic"),
    ]
    validate_options = ValidateOptions(extra_rule_dirs=[], use_bundled_rulesets=False)
    assert Counter(discover_rulesets(validate_options=validate_options)) == Counter(
        unfiltered_rulesets
    )
    log_test = "Found 3 rulesets: generic, generic, test-ruleset"
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.INFO, log_test)
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
    unfiltered_rulesets = [
        Path(base),
        Path(f"{base}/generic"),
        Path(f"{base}/test-ruleset"),
    ]
    filtered_rulesets = [Path(f"{base}/generic"), Path(f"{base}/test-ruleset")]
    validate_options = ValidateOptions(
        rulesets=["test-ruleset"],
        apply_generic=True,
    )
    assert Counter(
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)
    ) == Counter(filtered_rulesets)
    log_test = "Using 2 / 3 rulesets"
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.INFO, log_test)
    ]


def test_filter_rulesets_none(caplog):
    base = "tests/rulesets/base"
    unfiltered_rulesets = [
        Path(base),
        Path(f"{base}/generic"),
        Path(f"{base}/test-ruleset"),
    ]
    filtered_rulesets = []
    validate_options = ValidateOptions(
        rulesets=[],
        apply_generic=False,
    )
    assert Counter(
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)
    ) == Counter(filtered_rulesets)
    log_test = "Using 0 / 3 rulesets"
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.INFO, log_test)
    ]


def test_filter_rulesets_apply_generic(caplog):
    base = "tests/rulesets/base"
    unfiltered_rulesets = [
        Path(base),
        Path(f"{base}/generic"),
        Path(f"{base}/test-ruleset"),
    ]
    filtered_rulesets = [Path(f"{base}/generic")]
    validate_options = ValidateOptions(
        rulesets=[],
        apply_generic=True,
    )
    assert Counter(
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)
    ) == Counter(filtered_rulesets)
    log_test = "Using 1 / 3 rulesets"
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.INFO, log_test)
    ]


def test_filter_rulesets_with_rulesets(caplog):
    base = "tests/rulesets/base"
    unfiltered_rulesets = [
        Path(base),
        Path(f"{base}/generic"),
        Path(f"{base}/test-ruleset"),
    ]
    filtered_rulesets = [Path(f"{base}/test-ruleset")]
    validate_options = ValidateOptions(
        rulesets=["test-ruleset"],
        apply_generic=False,
    )
    assert Counter(
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)
    ) == Counter(filtered_rulesets)
    log_test = "Using 1 / 3 rulesets"
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.INFO, log_test)
    ]


def test_filter_rulesets_invalid_ruleset():
    base = "tests/rulesets/base"
    unfiltered_rulesets = [
        Path(base),
        Path(f"{base}/generic"),
        Path(f"{base}/test-ruleset"),
    ]
    validate_options = ValidateOptions(
        rulesets=["test-ruleset-woops-typo"],
        apply_generic=False,
    )
    with pytest.raises(InvalidRulesetName):
        filter_rulesets(unfiltered_rulesets, validate_options=validate_options)


def test_discover_rule_modules():
    base = "tests/rulesets/base"
    filtered_rulesets = [Path(f"{base}/generic"), Path(f"{base}/test-ruleset")]
    rule_modules = [
        Path(f"{base}/generic/common_ids.py"),
        Path(f"{base}/generic/core_profiles.py"),
        Path(f"{base}/test-ruleset/common_ids.py"),
        Path(f"{base}/test-ruleset/core_profiles.py"),
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
    log_test = f"No rules in rule file {path}"
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.WARNING, log_test)
    ]


def test_load_rules_syntax_error(res_collector):
    path = Path("tests/rulesets/exceptions/generic/syntax_error.py")
    with pytest.raises(ZeroDivisionError):
        load_rules_from_path(path, res_collector)


def test_load_rules_file_extension_error(res_collector, caplog):
    path = Path("tests/rulesets/exceptions/generic/wrong_file_extension.pie")
    load_rules_from_path(path, res_collector)
    log_test = f"Ignoring ruleset file: {str(path)!r} is not a python file"
    assert caplog.record_tuples == [
        ("ids_validator.rules.loading", logging.WARNING, log_test)
    ]


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
    path = Path("tests/rulesets/filter_test/test-ruleset/core_profiles.py")
    rules = load_rules_from_path(path, res_collector)
    path = Path("tests/rulesets/filter_test/test-ruleset/equilibrium.py")
    rules += load_rules_from_path(path, res_collector)
    assert_filter_rules(rules, 8, RuleFilter())
    assert_filter_rules(rules, 8, RuleFilter(name=[], ids=[]))
    assert_filter_rules(rules, 2, RuleFilter(name=["val_core_profiles"]))
    assert_filter_rules(rules, 2, RuleFilter(name=["val_equilibrium"]))
    assert_filter_rules(rules, 4, RuleFilter(name=["core_profiles"]))
    assert_filter_rules(rules, 4, RuleFilter(name=["equilibrium"]))
    assert_filter_rules(rules, 8, RuleFilter(name=["test"]))
    assert_filter_rules(rules, 4, RuleFilter(ids=["equilibrium"]))
    assert_filter_rules(rules, 4, RuleFilter(ids=["core_profiles"]))
    assert_filter_rules(rules, 4, RuleFilter(name=["test"], ids=["core_profiles"]))
    assert_filter_rules(rules, 2, RuleFilter(name=["test", "4"]))


def assert_filter_rules(rules, res, rule_filter):
    validate_options = ValidateOptions(rule_filter=rule_filter)
    assert len(filter_rules(rules, validate_options=validate_options)) == res


def test_load_docs(res_collector):
    rule_dirs = [
        Path("tests/rulesets/base"),
    ]
    val_options = ValidateOptions(
        rulesets=["test-ruleset"],
        use_bundled_rulesets=False,
        apply_generic=False,
        extra_rule_dirs=rule_dirs,
        rule_filter=RuleFilter(name=["common_ids"], ids=[]),
    )
    docs = load_docs(res_collector, val_options)
    rules = [
        RuleData(
            path=Path("tests/rulesets/base/test-ruleset/common_ids.py"),
            name="common_ids_rule",
            docstring="Function level docstring for validation tests",
            ids_names=("*",),
        )
    ]
    rule_files = [
        RuleFileData(
            name="common_ids.py",
            docstring="Module level docstring for validation tests",
            rules=rules,
        )
    ]
    rule_sets = [
        RuleSetData(
            name="test-ruleset",
            docstring="Folder level docstring for validation tests",
            rule_files=rule_files,
        )
    ]
    rule_dir_data_list = [RuleDirData(name="base", rule_sets=rule_sets)]
    expected_docs = ExplorerData(rule_dir_data_list)
    assert docs == expected_docs


def test_load_docs_no_docs(res_collector):
    rule_dirs = [
        Path("tests/rulesets/base"),
    ]
    val_options = ValidateOptions(
        use_bundled_rulesets=False,
        apply_generic=True,
        extra_rule_dirs=rule_dirs,
        rule_filter=RuleFilter(name=["common_ids"], ids=[]),
    )
    docs = load_docs(res_collector, val_options)
    rules = [
        RuleData(
            path=Path("tests/rulesets/base/generic/common_ids.py"),
            name="common_ids_rule",
            docstring=(
                "No function docstring available. Add a docstring to your function."
            ),
            ids_names=("*",),
        )
    ]
    rule_files = [
        RuleFileData(
            name="common_ids.py",
            docstring=(
                "No module docstring available. Add a docstring at the top of "
                "your ruleset."
            ),
            rules=rules,
        )
    ]
    rule_sets = [
        RuleSetData(
            name="generic",
            docstring=(
                "No folder docstring available. Add an __init__.py file to your "
                "rule directory with a docstring."
            ),
            rule_files=rule_files,
        )
    ]
    rule_dir_data_list = [RuleDirData(name="base", rule_sets=rule_sets)]
    expected_docs = ExplorerData(rule_dir_data_list)
    assert docs == expected_docs
