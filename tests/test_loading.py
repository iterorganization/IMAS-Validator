import pytest
from pathlib import Path
from collections import Counter

from ids_validator.rules.loading import (
    discover_rulesets,
    filter_rulesets,
    discover_rule_modules,
    load_rules_from_path,
)


@pytest.fixture(params=[False, True])
def use_env_var(request, monkeypatch):
    use_env_var = request.param
    if use_env_var:
        ruleset_path = "tests/rulesets_env_var"
    else:
        ruleset_path = ""
    monkeypatch.setenv("RULESET_PATH", ruleset_path)
    return use_env_var


@pytest.fixture(params=[[""], ["ITER-MD"]])
def rulesets(request):
    return request.param


@pytest.fixture(params=[True, False])
def apply_generic(request):
    return request.param


@pytest.fixture
def rulesets_dirs():
    return [
        Path("tests"),
        Path("tests/rulesets"),
        Path("tests/rulesets/generic"),
    ]


@pytest.fixture
def unfiltered_rulesets(use_env_var):
    unfiltered_rulesets = [
        Path("tests/rulesets"),
        Path("tests/rulesets_env_var"),
        Path("tests/rulesets_empty"),
        Path("tests/rulesets/generic"),
        Path("tests/rulesets/ITER-MD"),
    ]
    if use_env_var:
        unfiltered_rulesets += [
            Path("tests/rulesets_env_var/generic"),
            Path("tests/rulesets_env_var/ITER-MD"),
        ]
    return unfiltered_rulesets


@pytest.fixture
def filtered_rulesets(use_env_var, rulesets, apply_generic):
    filtered_rulesets = []
    if apply_generic:
        filtered_rulesets += [Path("tests/rulesets/generic")]
        if use_env_var:
            filtered_rulesets += [Path("tests/rulesets_env_var/generic")]
    if "ITER-MD" in rulesets:
        filtered_rulesets += [Path("tests/rulesets/ITER-MD")]
        if use_env_var:
            filtered_rulesets += [Path("tests/rulesets_env_var/ITER-MD")]
    return filtered_rulesets


@pytest.fixture
def rule_modules(use_env_var, rulesets, apply_generic):
    rule_modules = []
    if apply_generic:
        rule_modules += [
            Path("tests/rulesets/generic/common_ids.py"),
            Path("tests/rulesets/generic/core_profiles.py"),
        ]
        if use_env_var:
            rule_modules += [
                Path("tests/rulesets_env_var/generic/common_ids.py"),
                Path("tests/rulesets_env_var/generic/core_profiles.py"),
            ]
    if "ITER-MD" in rulesets:
        rule_modules += [
            Path("tests/rulesets/ITER-MD/common_ids.py"),
            Path("tests/rulesets/ITER-MD/core_profiles.py"),
        ]
        if use_env_var:
            rule_modules += [
                Path("tests/rulesets_env_var/ITER-MD/common_ids.py"),
                Path("tests/rulesets_env_var/ITER-MD/core_profiles.py"),
            ]
    return rule_modules


def test_discover_rulesets(rulesets_dirs, unfiltered_rulesets):
    assert Counter(discover_rulesets(rulesets_dirs)) == Counter(unfiltered_rulesets)


def test_filter_rulesets(
    unfiltered_rulesets, filtered_rulesets, rulesets, apply_generic
):
    assert Counter(
        filter_rulesets(unfiltered_rulesets, rulesets, apply_generic)
    ) == Counter(filtered_rulesets)


def test_discover_rule_modules(filtered_rulesets, rule_modules):
    assert Counter(discover_rule_modules(filtered_rulesets)) == Counter(rule_modules)


def test_load_rules_from_path():
    rule_modules = [
        Path("tests/rulesets/generic/core_profiles.py"),
    ]
    rules = []
    for path in rule_modules:
        rules += load_rules_from_path(path)
    assert len(rules) == 1
    assert rules[0].name == "generic/core_profiles.py/core_profiles_rule"
    assert rules[0].dd_types == ("core_profiles",)
    assert rules[0].kwfields == {}


def test_load_rules_from_path_empty_file():
    rule_modules = [
        Path("tests/rulesets_empty/generic/common_ids.py"),
    ]
    rules = []
    for path in rule_modules:
        rules += load_rules_from_path(path)
    assert len(rules) == 0


# def test_handle_entrypoints():
#     pass
