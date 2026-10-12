"""Select candidate rules before reading their IDS data."""

from pathlib import Path
from unittest.mock import Mock, call

import imas
import pytest

from imas_validator.rules.data import IDSValidationRule
from imas_validator.validate.result_collector import ResultCollector
from imas_validator.validate.rule_executor import RuleExecutor
from imas_validator.validate.validate import validate
from imas_validator.validate_options import RuleFilter, ValidateOptions


def make_rule(*names, version=""):
    def check(*ids):
        pass

    return IDSValidationRule(Path("rules/selection.py"), check, *names, version=version)


@pytest.fixture
def executor():
    factory = imas.IDSFactory("3.40.1")
    data = {
        (name, occ): factory.new(name)
        for name, occ in [
            ("core_profiles", 0),
            ("core_profiles", 3),
            ("equilibrium", 1),
            ("waves", 0),
        ]
    }
    db = Mock()
    # The entry's DD can differ from a stored IDS's DD (autoconvert=False).
    db.factory = imas.IDSFactory("4.0.0")
    db.dd_version = "4.0.0"
    db.list_all_occurrences.side_effect = lambda name: [
        occ for ids_name, occ in data if ids_name == name
    ]
    db.get.side_effect = lambda name, occ, **kwargs: data[name, occ]
    options = ValidateOptions()
    return RuleExecutor(db, [], ResultCollector(options, ""), options)


@pytest.mark.parametrize(
    "spec, expected",
    [
        (None, []),
        ("summary", []),
        ("core_profiles:2", []),
        ("core_profiles:3", [("core_profiles", 3)]),
        ("core_profiles", [("core_profiles", 0), ("core_profiles", 3)]),
        ("*:0", [("core_profiles", 0), ("waves", 0)]),
        (
            "*",
            [
                ("core_profiles", 0),
                ("core_profiles", 3),
                ("equilibrium", 1),
                ("waves", 0),
            ],
        ),
    ],
)
def test_reads_only_candidates(executor, spec, expected):
    executor.rules = [] if spec is None else [make_rule(spec)]
    matches = list(executor.find_matching_rules())
    assert sorted((idss[0][1], idss[0][2]) for idss, _ in matches) == sorted(expected)
    assert executor.db_entry.get.call_count == len(expected)
    executor.db_entry.get.assert_has_calls(
        [call(name, occ, autoconvert=False) for name, occ in expected], any_order=True
    )


@pytest.mark.parametrize("version, count", [("==3.40.1", 1), ("==4.0.0", 0)])
def test_version_filter_uses_loaded_ids(executor, version, count):
    executor.rules = [make_rule("core_profiles:3", version=version)]
    assert len(list(executor.find_matching_rules())) == count
    executor.db_entry.get.assert_called_once_with("core_profiles", 3, autoconvert=False)


def test_cross_ids_dependency_without_standalone_rule(executor):
    executor.rules = [make_rule("core_profiles:3", "equilibrium:1")]
    matches = list(executor.find_matching_rules())
    assert len(matches) == 1
    assert [(name, occ) for _, name, occ in matches[0][0]] == [
        ("core_profiles", 3),
        ("equilibrium", 1),
    ]
    assert executor.db_entry.get.call_args_list == [
        call("core_profiles", 3, autoconvert=False),
        call("equilibrium", 1, autoconvert=False),
    ]


@pytest.mark.parametrize("stop", [False, True])
def test_unmatched_unreadable_ids_do_not_affect_selected_rule(executor, stop, caplog):
    executor.validate_options = ValidateOptions(stop_at_load_error=stop)
    executor.rules = [make_rule("core_profiles:3")]
    original_get = executor.db_entry.get.side_effect

    def get(name, occ, **kwargs):
        if (name, occ) != ("core_profiles", 3):
            raise RuntimeError("Unrelated IDS cannot be read")
        return original_get(name, occ, **kwargs)

    executor.db_entry.get.side_effect = get
    assert len(list(executor.find_matching_rules())) == 1
    executor.db_entry.get.assert_called_once_with("core_profiles", 3, autoconvert=False)
    assert "Unable to load IDS" not in caplog.text


@pytest.mark.parametrize("stop", [False, True])
@pytest.mark.parametrize("dependency", [False, True])
def test_required_load_errors_keep_their_policy(executor, stop, dependency, caplog):
    executor.validate_options = ValidateOptions(stop_at_load_error=stop)
    executor.rules = [
        (
            make_rule("core_profiles:3", "equilibrium:2")
            if dependency
            else make_rule("core_profiles:3")
        )
    ]
    if dependency:
        error_type = KeyError
    else:
        error_type = RuntimeError
        executor.db_entry.get.side_effect = RuntimeError("Required IDS cannot be read")
    if stop:
        with pytest.raises(error_type):
            list(executor.find_matching_rules())
    else:
        assert list(executor.find_matching_rules()) == []
    assert "Unable to load IDS" in caplog.text


@pytest.mark.parametrize("coverage", [False, True])
def test_filtered_validation_reads_only_selected_occurrence(
    tmp_path, monkeypatch, coverage
):
    uri = str(tmp_path / "selection.nc")
    with imas.DBEntry(uri, "x", dd_version="3.40.1") as entry:
        for name, occ in [
            ("core_profiles", 0),
            ("core_profiles", 3),
            ("equilibrium", 1),
        ]:
            ids = entry.factory.new(name)
            ids.ids_properties.homogeneous_time = 0
            entry.put(ids, occ)

    ruleset = tmp_path / "rules" / "selection"
    ruleset.mkdir(parents=True)
    (ruleset / "check.py").write_text(
        '@validator("core_profiles:3")\n'
        "def selected(cp):\n"
        "    assert cp.ids_properties.homogeneous_time == 0\n"
        '@validator("equilibrium:1")\n'
        "def excluded(eq):\n"
        "    assert False\n"
    )
    original_get = imas.DBEntry.get
    reads = []

    def get(entry, name, occurrence=0, **kwargs):
        reads.append((name, occurrence))
        return original_get(entry, name, occurrence, **kwargs)

    monkeypatch.setattr(imas.DBEntry, "get", get)
    result = validate(
        uri,
        ValidateOptions(
            rulesets=["selection"],
            extra_rule_dirs=[ruleset.parent],
            apply_generic=False,
            use_bundled_rulesets=False,
            rule_filter=RuleFilter(ids=["core_profiles"]),
            track_node_dict=coverage,
            stop_at_load_error=True,
        ),
    )
    assert reads == [("core_profiles", 3)]
    assert len(result.results) == 1
    assert result.results[0].success
    assert result.results[0].idss == [("core_profiles", 3)]
    assert result.results[0].nodes_dict == {
        ("core_profiles", 3): {"ids_properties/homogeneous_time"}
    }
    assert bool(result.coverage_dict) is coverage
