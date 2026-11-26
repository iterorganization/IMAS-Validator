"""Rule errors must respect the same coverage option as assertions."""

from pathlib import Path
from xml.etree import ElementTree

import imas
import pytest
from imas.ids_structure import IDSStructure

from imas_validator.report.validationReportGenerator import ValidationReportGenerator
from imas_validator.rules.data import IDSValidationRule
from imas_validator.validate.result import CoverageMap
from imas_validator.validate.result_collector import ResultCollector
from imas_validator.validate.rule_executor import RuleExecutor
from imas_validator.validate.validate import validate
from imas_validator.validate_options import ValidateOptions


@pytest.mark.parametrize("coverage", [False, True])
@pytest.mark.parametrize("assert_first", [False, True])
def test_rule_error_preserves_results_and_optional_coverage(
    monkeypatch, coverage, assert_first
):
    options = ValidateOptions(track_node_dict=coverage)
    collector = ResultCollector(options, "test-entry")
    factory = imas.IDSFactory("3.40.1")
    cp, waves = factory.core_profiles(), factory.waves()
    cp.ids_properties.homogeneous_time = 0
    waves.ids_properties.homogeneous_time = 0
    cp.profiles_1d.resize(2)
    cp.profiles_1d[1].time = 1.0
    error = ValueError("Rule execution failed")

    def broken_rule(cp, waves):
        if assert_first:
            collector.assert_(cp.ids_properties.homogeneous_time == 0)
        raise error

    rule = IDSValidationRule(
        Path("rules/errors.py"), broken_rule, "core_profiles:3", "waves:1"
    )
    collector.set_context(rule, [(cp, "core_profiles", 3), (waves, "waves", 1)])
    if not coverage:

        def forbidden_traversal(*args, **kwargs):
            pytest.fail("Coverage disabled: must not traverse filled nodes")

        monkeypatch.setattr(IDSStructure, "iter_nonempty_", forbidden_traversal)

    executor = RuleExecutor(None, [rule], collector, options)
    executor.run(rule, [cp, waves])
    result = collector.result_collection()
    assert len(result.results) == 1 + int(assert_first)
    failed = result.results[-1]
    assert failed.success is False
    assert failed.exc is error
    assert failed.rule is rule
    assert failed.idss == [("core_profiles", 3), ("waves", 1)]
    assert failed.nodes_dict == {}
    assert failed.tb[-1].name == "broken_rule"
    assert failed.tb[-1].line == "raise error"
    if coverage:
        assert result.coverage_dict == {
            ("core_profiles", 3): CoverageMap(2, int(assert_first), int(assert_first)),
            ("waves", 1): CoverageMap(1, 0, 0),
        }
    else:
        assert result.coverage_dict == {}

    report = ValidationReportGenerator(result)
    xml = ElementTree.fromstring(report.xml)
    assert xml.attrib["failures"] == "1"
    assert {suite.attrib["name"] for suite in xml.findall("testsuite")} == {
        "core_profiles:3",
        "waves:1",
    }
    assert any(
        "broken_rule" in case.attrib["name"]
        for case in ElementTree.fromstring(report.xml).iter("testcase")
    )
    assert "Number of failed tests : 1" in report.txt
    assert "- IDS core_profiles occurrence 3" in report.txt
    assert ("Coverage map:" in report.txt) is coverage


@pytest.mark.parametrize("coverage", [False, True])
def test_error_only_netcdf_validation(tmp_path, coverage):
    uri = str(tmp_path / "errors.nc")
    with imas.DBEntry(uri, "x", dd_version="3.40.1") as entry:
        ids = entry.factory.core_profiles()
        ids.ids_properties.homogeneous_time = 0
        entry.put(ids, 3)
    ruleset = tmp_path / "rules" / "errors"
    ruleset.mkdir(parents=True)
    (ruleset / "check.py").write_text(
        '@validator("core_profiles:3")\n'
        "def broken_rule(cp):\n"
        '    raise ValueError("Invalid test data")\n'
    )
    result = validate(
        uri,
        ValidateOptions(
            rulesets=["errors"],
            extra_rule_dirs=[ruleset.parent],
            use_bundled_rulesets=False,
            apply_generic=False,
            track_node_dict=coverage,
        ),
    )
    assert len(result.results) == 1
    failed = result.results[0]
    assert failed.success is False
    assert isinstance(failed.exc, ValueError)
    assert str(failed.exc) == "Invalid test data"
    assert failed.idss == [("core_profiles", 3)]
    assert failed.tb[-1].name == "broken_rule"
    assert failed.tb[-1].lineno == 3
    assert bool(result.coverage_dict) is coverage
    report = ValidationReportGenerator(result)
    assert ElementTree.fromstring(report.xml).attrib["failures"] == "1"
    assert any(
        "broken_rule" in case.attrib["name"]
        for case in ElementTree.fromstring(report.xml).iter("testcase")
    )
    assert "Number of failed tests : 1" in report.txt
    assert "- IDS core_profiles occurrence 3" in report.txt
    assert ("Coverage map:" in report.txt) is coverage
