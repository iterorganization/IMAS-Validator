from unittest.mock import patch

import imas  # type: ignore
import numpy
import pytest

from imas_validator.validate.validate import validate
from imas_validator.validate_options import RuleFilter, ValidateOptions

RULE_NAME = "validate_aos_name_not_empty"


def new_pf_active():
    ids = imas.IDSFactory("3.40.1").pf_active()
    ids.ids_properties.homogeneous_time = 2
    return ids


def run_rule(ids, **options):
    """Run the bundled pedantic validate_aos_name_not_empty rule on ids."""
    options.setdefault("rulesets", ["pedantic"])

    def list_all_occurrences(ids_name):
        return numpy.array([0]) if ids_name == ids.metadata.name else []

    def get(ids_name, occurrence=0, autoconvert=False):
        return ids

    with patch(
        "imas_validator.validate.validate.imas.DBEntry",
        spec=True,
        list_all_occurrences=list_all_occurrences,
        get=get,
        uri="",
        factory=imas.IDSFactory("3.40.1"),
    ):
        options = ValidateOptions(rule_filter=RuleFilter(name=[RULE_NAME]), **options)
        results = validate(imas_uri="", validate_options=options).results
    assert all(res.rule.name == f"pedantic/generic.py:{RULE_NAME}" for res in results)
    assert all(res.exc is None for res in results)
    return results


def failed_paths(results):
    """Set of the IDS paths involved in failed asserts."""
    return {
        path
        for res in results
        if not res.success
        for path in res.nodes_dict[("pf_active", 0)]
    }


def test_all_names_filled():
    ids = new_pf_active()
    ids.coil.resize(2)
    ids.coil[0].name = "PF1"
    ids.coil[1].name = "PF2"
    results = run_rule(ids)
    assert len(results) == 2
    assert all(res.success for res in results)


@pytest.mark.parametrize("bad_name", ["", "   "])
def test_empty_coil_name(bad_name):
    ids = new_pf_active()
    ids.coil.resize(2)
    ids.coil[0].name = "PF1"
    ids.coil[1].name = bad_name
    results = run_rule(ids)
    assert [res.success for res in results].count(False) == 1
    assert failed_paths(results) == {"coil[1]/name"}


def test_nested_aos_name():
    ids = new_pf_active()
    ids.coil.resize(1)
    ids.coil[0].name = "PF1"
    ids.coil[0].element.resize(1)
    results = run_rule(ids)
    assert failed_paths(results) == {"coil[0]/element[0]/name"}


def test_infrastructure_aos_name():
    ids = new_pf_active()
    ids.code.library.resize(1)
    results = run_rule(ids)
    assert failed_paths(results) == {"code/library[0]/name"}


def test_plain_structure_name_ignored():
    ids = new_pf_active()
    ids.code.name = ""  # name of a plain structure, not checked
    results = run_rule(ids)
    assert results == []


def test_not_applied_by_default():
    ids = new_pf_active()
    ids.coil.resize(1)  # coil[0].name is empty
    assert run_rule(ids, rulesets=[]) == []
