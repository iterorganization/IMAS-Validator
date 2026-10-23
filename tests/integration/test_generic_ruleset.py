import imas  # type: ignore
from imas.test.test_helpers import fill_consistent # type: ignore
import pytest
from packaging.version import Version

from imas_validator.validate.validate import validate
from imas_validator.validate_options import RuleFilter, ValidateOptions


@pytest.mark.skipif(
    Version(imas.__version__) < Version("1.1"),
    reason="fill_consistent needs arg leave_empty",
)
@pytest.mark.parametrize("track_node_dict", [False, True], ids=["", "coverage"])
@pytest.mark.parametrize("ids_name", imas.IDSFactory().ids_names())
def test_generic_tests_with_randomly_generated_ids(ids_name, track_node_dict, tmp_path):
    if ids_name == "amns_data":
        pytest.skip("amns_data IDS is not supported by IMAS-Python's fill_consistent")

    ids = imas.IDSFactory().new(ids_name)
    fill_consistent(ids, leave_empty=0)

    uri = f"{tmp_path}/pulse.nc"
    dbentry = imas.DBEntry(uri, "w")
    dbentry.put(ids)
    dbentry.close()

    validate_options = ValidateOptions(track_node_dict=track_node_dict)
    results_collection = validate(uri, validate_options=validate_options)
    assert len(results_collection.results) > 0
    for result in results_collection.results:
        # Generic tests should generally not lead to an Exception
        # fill_consistent might create incompatible ggd ion and density data
        assert result.exc is None or (
            "operands could not be broadcast together" in str(result.exc)
        )

    if not track_node_dict:
        return
    coverage = results_collection.coverage_dict[ids_name, 0]
    assert coverage.filled > 0
    assert coverage.overlap <= min(coverage.filled, coverage.visited)


def _validate_ids(tmp_path, dd_version, *idss, rule_name):
    uri = f"{tmp_path}/pulse.nc"
    with imas.DBEntry(uri, "w", dd_version=dd_version) as dbentry:
        for ids in idss:
            dbentry.put(ids)
    validate_options = ValidateOptions(rule_filter=RuleFilter(name=[rule_name]))
    return validate(uri, validate_options=validate_options).results


def _new_ids(dd_version, ids_name):
    ids = imas.IDSFactory(dd_version).new(ids_name)
    ids.ids_properties.homogeneous_time = imas.ids_defs.IDS_TIME_MODE_INDEPENDENT
    return ids


def test_validate_unique_names(tmp_path):
    pf_active = _new_ids("4.0.0", "pf_active")
    pf_active.coil.resize(4)
    for coil, name in zip(pf_active.coil, ["a", "b", "a", ""]):
        coil.name = name

    # Same target names in different divertors are allowed
    divertors = _new_ids("4.0.0", "divertors")
    divertors.divertor.resize(2)
    for divertor in divertors.divertor:
        divertor.target.resize(2)
        divertor.target[0].name = "t1"
        divertor.target[1].name = "t2"

    results = _validate_ids(
        tmp_path, "4.0.0", pf_active, divertors, rule_name="validate_unique_names"
    )
    assert all(result.exc is None for result in results)
    divertors_results = [r for r in results if r.idss[0][0] == "divertors"]
    assert len(divertors_results) == 4
    assert all(result.success for result in divertors_results)

    pf_active_results = [r for r in results if r.idss[0][0] == "pf_active"]
    assert len(pf_active_results) == 3  # the empty name is ignored
    failed = [r for r in pf_active_results if not r.success]
    assert len(failed) == 2
    failed_paths = {path for r in failed for path in r.nodes_dict[("pf_active", 0)]}
    assert failed_paths == {"coil[0]/name", "coil[2]/name"}


@pytest.mark.parametrize("dd_version, applied", [("3.40.1", True), ("4.0.0", False)])
def test_validate_coil_name_dd_version(tmp_path, dd_version, applied):
    pf_active = _new_ids(dd_version, "pf_active")
    pf_active.coil.resize(2)
    pf_active.coil[0].name = pf_active.coil[1].name = "a"

    results = _validate_ids(
        tmp_path, dd_version, pf_active, rule_name="validate_coil_name"
    )
    assert bool(results) == applied
