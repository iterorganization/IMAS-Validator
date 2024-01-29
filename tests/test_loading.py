import pytest
from pathlib import Path
from collections import Counter
import unittest.mock

from ids_validator.rules.data import ValidatorRegistry
from ids_validator.rules.loading import (
    discover_rule_modules,
    discover_rulesets,
    filter_rulesets,
    load_rules_from_path,
)
from ids_validator.exceptions import (
    InvalidRulesetPath,
    InvalidRulesetName,
    EmptyRuleFileWarning,
    WrongFileExtensionError,
)
from ids_validator.rules.ast_rewrite import run_path


@pytest.fixture(scope="function")
def res_collector():
    mock = unittest.mock.MagicMock()
    # MagicMock doesn't automatically create mock attributes starting with 'assert'
    mock.assert_ = unittest.mock.Mock()
    return mock


def test_discover_rulesets_explicit():
    rulesets_dirs = [
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
    ]
    assert Counter(discover_rulesets(rulesets_dirs)) == Counter(unfiltered_rulesets)


def test_discover_rulesets_env_var(monkeypatch):
    monkeypatch.setenv("RULESET_PATH", "tests/rulesets/env_var:tests/rulesets/env_var2")
    unfiltered_rulesets = [
        Path("tests/rulesets/env_var/generic"),
        Path("tests/rulesets/env_var/ITER-MD"),
        Path("tests/rulesets/env_var2/generic"),
    ]
    assert Counter(discover_rulesets([])) == Counter(unfiltered_rulesets)


def test_discover_rulesets_invalid_env_var(monkeypatch):
    monkeypatch.setenv(
        "RULESET_PATH", "tests/rulesets/env_var:tests/rulesets/env_var_invalid"
    )
    with pytest.raises(InvalidRulesetPath):
        discover_rulesets([])


# def test_discover_rulesets_entrypoints():
#     pass


def test_filter_rulesets_all():
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    rulesets = ["ITER-MD"]
    apply_generic = True
    filtered_rulesets = [Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    assert Counter(
        filter_rulesets(unfiltered_rulesets, rulesets, apply_generic)
    ) == Counter(filtered_rulesets)


def test_filter_rulesets_none():
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    rulesets = []
    apply_generic = False
    filtered_rulesets = []
    assert Counter(
        filter_rulesets(unfiltered_rulesets, rulesets, apply_generic)
    ) == Counter(filtered_rulesets)


def test_filter_rulesets_apply_generic():
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    rulesets = []
    apply_generic = True
    filtered_rulesets = [Path(f"{base}/generic")]
    assert Counter(
        filter_rulesets(unfiltered_rulesets, rulesets, apply_generic)
    ) == Counter(filtered_rulesets)


def test_filter_rulesets_with_rulesets():
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    rulesets = ["ITER-MD"]
    apply_generic = False
    filtered_rulesets = [Path(f"{base}/ITER-MD")]
    assert Counter(
        filter_rulesets(unfiltered_rulesets, rulesets, apply_generic)
    ) == Counter(filtered_rulesets)


def test_filter_rulesets_invalid_ruleset():
    base = "tests/rulesets/base"
    unfiltered_rulesets = [Path(base), Path(f"{base}/generic"), Path(f"{base}/ITER-MD")]
    rulesets = ["ITER-MD-woops-typo"]
    apply_generic = False
    with pytest.raises(InvalidRulesetName):
        filter_rulesets(unfiltered_rulesets, rulesets, apply_generic)


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
    assert rules[0].dd_types == ("core_profiles",)
    assert rules[0].kwfields == {}


def test_load_rules_from_path_empty_file(res_collector):
    path = Path("tests/rulesets/exceptions/generic/empty.py")
    with pytest.raises(EmptyRuleFileWarning):
        rules = load_rules_from_path(path, res_collector)
        assert len(rules) == 0


def test_load_rules_syntax_error(res_collector):
    path = Path("tests/rulesets/exceptions/generic/syntax_error.py")
    with pytest.raises(ZeroDivisionError):
        load_rules_from_path(path, res_collector)


def test_load_rules_file_extension_error(res_collector):
    path = Path("tests/rulesets/exceptions/generic/wrong_file_extension.pie")
    with pytest.raises(WrongFileExtensionError):
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
