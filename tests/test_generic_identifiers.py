"""Generic identifier rules."""

import imas
import pytest

from imas_validator.validate.validate import validate
from imas_validator.validate_options import RuleFilter, ValidateOptions


def _validate_sources(tmp_path, rule_name, identifiers):
    ids = imas.IDSFactory().new("core_sources")
    ids.ids_properties.homogeneous_time = imas.ids_defs.IDS_TIME_MODE_HOMOGENEOUS
    ids.time = [0.0]
    ids.source.resize(len(identifiers))
    for source, (index, name) in zip(ids.source, identifiers):
        if index is not None:
            source.identifier.index = index
        if name is not None:
            source.identifier.name = name
    uri = str(tmp_path / "identifiers.nc")
    with imas.DBEntry(uri, "w") as entry:
        entry.put(ids)

    result = validate(uri, ValidateOptions(rule_filter=RuleFilter(name=[rule_name])))
    assert all(r.exc is None for r in result.results)
    return [r.success for r in result.results]


@pytest.mark.parametrize(
    "identifiers, expected",
    [
        ([(1, "total")], [True]),  # standard value
        ([(0, "unspecified")], [True]),  # index 0 is a listed value
        ([(99, None)], [False]),  # index not in core_source_identifier
        ([(-1, "my_private_source")], []),  # private value: not checked
        ([(None, "total")], []),  # no index: nothing to check
        ([(1, "total"), (99, "total")], [True, False]),
    ],
)
def test_identifier_index(tmp_path, identifiers, expected):
    rule = "validate_identifier_index"
    assert _validate_sources(tmp_path, rule, identifiers) == expected


@pytest.mark.parametrize(
    "identifiers, expected",
    [
        ([(1, "total")], [True]),  # name matches index
        ([(2, "nbi")], [True]),
        ([(1, "nbi")], [False]),  # name of another index
        ([(1, "Total")], [False]),  # names are case sensitive
        ([(1, None)], []),  # no name: nothing to check
        ([(99, "total")], []),  # unknown index: reported by the index rule
        ([(-1, "total")], []),  # private value: not checked
        ([(1, "total"), (2, "ec")], [True, False]),
    ],
)
def test_identifier_name(tmp_path, identifiers, expected):
    rule = "validate_identifier_name"
    assert _validate_sources(tmp_path, rule, identifiers) == expected


def _run_identifier_rules(ids, rule_name):
    """Use real assert rewriting and result collection without storage constraints."""
    from imas_validator.rules.loading import load_rules
    from imas_validator.validate.result_collector import ResultCollector
    from imas_validator.validate.rule_executor import RuleExecutor

    options = ValidateOptions(rule_filter=RuleFilter(name=[rule_name]))
    collector = ResultCollector(options, "")
    rules = load_rules(collector, options)
    executor = RuleExecutor(None, rules, collector, options)
    for rule in rules:
        collector.set_context(rule, [(ids, ids.metadata.name, 0)])
        executor.run(rule, [ids])
    assert all(result.exc is None for result in collector.results)
    return collector.results


def test_identifier_name_tracks_index_and_name():
    ids = imas.IDSFactory("3.40.1").core_sources()
    ids.source.resize(1)
    ids.source[0].identifier.index = 1
    ids.source[0].identifier.name = "nbi"
    results = _run_identifier_rules(ids, "validate_identifier_name")
    assert len(results) == 1
    assert not results[0].success
    assert results[0].nodes_dict == {
        ("core_sources", 0): {
            "source[0]/identifier/index",
            "source[0]/identifier/name",
        }
    }


@pytest.fixture(params=["3.38.1", "3.40.1", "4.1.1"])
def wall_identifiers(request):
    ids = imas.IDSFactory(request.param).wall()
    ids.description_ggd.resize(1)
    ids.description_ggd[0].material.resize(1)
    ids.description_ggd[0].material[0].grid_subset.resize(1)
    node = ids.description_ggd[0].material[0].grid_subset[0].identifiers
    return ids, node


@pytest.mark.parametrize(
    "indices, expected",
    [
        ([20], [True]),
        ([999999], [False]),
        ([-1], []),
        ([20, -1, 999999], [True, False]),
        ([], []),
    ],
)
def test_plural_identifier_indices(wall_identifiers, indices, expected):
    ids, node = wall_identifiers
    node.indices = indices
    results = _run_identifier_rules(ids, "validate_identifier_indices")
    assert [r.success for r in results] == expected
    for result in results:
        assert result.nodes_dict == {("wall", 0): {node.indices._path}}


@pytest.mark.parametrize(
    "indices, names, expected",
    [
        ([20], ["235U"], [True]),
        ([20], ["U_235"], [True]),  # real DD alias
        ([20], ["invalid"], [False]),
        ([20, 20], ["235U", "invalid"], [True, False]),
        ([20, 20], ["235U"], [True, True]),  # singleton name
        ([20], ["235U", "U_235"], [True, True]),  # singleton index
        ([20, 20], ["235U", "235U", "235U"], [False]),
        ([20, -1, 999999], ["", "private", "unknown"], []),
        ([20], [], []),
        ([], ["235U"], []),
    ],
)
def test_plural_identifier_names(wall_identifiers, indices, names, expected):
    ids, node = wall_identifiers
    node.indices = indices
    node.names = names
    results = _run_identifier_rules(ids, "validate_identifier_names")
    assert [r.success for r in results] == expected
    for result in results:
        assert result.nodes_dict == {
            ("wall", 0): {node.indices._path, node.names._path}
        }


def test_plural_identifier_brdf_uses_its_own_enumeration():
    ids = imas.IDSFactory("4.1.1").wall()
    ids.description_ggd.resize(1)
    ids.description_ggd[0].brdf.resize(1)
    ids.description_ggd[0].brdf[0].type.resize(1)
    node = ids.description_ggd[0].brdf[0].type[0].identifiers
    node.indices = [2]
    node.names = ["lambertian"]
    results = _run_identifier_rules(ids, "generic/identifiers.py")
    assert [r.success for r in results] == [True, True]


def test_plural_identifier_netcdf(tmp_path):
    ids = imas.IDSFactory("4.1.1").wall()
    ids.ids_properties.homogeneous_time = 1
    ids.time = [0.0]
    ids.description_ggd.resize(1)
    ids.description_ggd[0].material.resize(1)
    material = ids.description_ggd[0].material[0]
    material.time = 0.0
    ids.description_ggd[0].grid_ggd.resize(1)
    ids.description_ggd[0].grid_ggd[0].time = 0.0
    material.grid_subset.resize(1)
    node = material.grid_subset[0].identifiers
    node.indices = [20, 999999]
    node.names = ["invalid", "unknown"]
    uri = str(tmp_path / "wall.nc")
    with imas.DBEntry(uri, "x", dd_version="4.1.1") as entry:
        entry.put(ids)
    results = validate(
        uri, ValidateOptions(rule_filter=RuleFilter(name=["generic/identifiers.py"]))
    ).results
    assert all(r.exc is None for r in results)
    assert [r.success for r in results] == [True, False, False]
    assert results[-1].nodes_dict == {
        ("wall", 0): {node.indices._path, node.names._path}
    }


@pytest.mark.parametrize("version", ["3.40.1", "4.1.1"])
@pytest.mark.parametrize(
    "ids_name, path, valid_index, valid_name",
    [
        (
            "equilibrium",
            "time_slice[0]/convergence/grad_shafranov_deviation_expression",
            1,
            "absolute_gs_difference",
        ),
        (
            "transport_solver_numerics",
            "solver_1d[0]/equation[0]/computation_mode",
            1,
            "interpretative",
        ),
        (
            "transport_solver_numerics",
            "solver_1d[0]/equation[0]/boundary_condition[0]/type",
            1,
            "value",
        ),
    ],
)
def test_legacy_identifier_references(version, ids_name, path, valid_index, valid_name):
    ids = imas.IDSFactory(version).new(ids_name)
    if ids_name == "equilibrium":
        ids.time_slice.resize(1)
    else:
        ids.solver_1d.resize(1)
        ids.solver_1d[0].equation.resize(1)
    if "boundary_condition" in path:
        ids.solver_1d[0].equation[0].boundary_condition.resize(1)
    node = ids[path]
    node.index = valid_index
    node.name = valid_name
    results = _run_identifier_rules(ids, "generic/identifiers.py")
    assert [r.success for r in results] == [True, True]
    node.name = "invalid"
    results = _run_identifier_rules(ids, "generic/identifiers.py")
    assert [r.success for r in results] == [True, False]
    assert results[-1].nodes_dict == {
        (ids_name, 0): {node.index._path, node.name._path}
    }
    node.index = 999999
    results = _run_identifier_rules(ids, "generic/identifiers.py")
    assert [r.success for r in results] == [False]


def test_legacy_identifier_reference_without_suffix():
    # DD 3.41.0 to 4.0.0 refer to equilibrium_convergence_status.xml, while the
    # enumeration is registered as equilibrium_convergence_status_identifier
    ids = imas.IDSFactory("3.42.0").equilibrium()
    ids.time_slice.resize(1)
    node = ids.time_slice[0].convergence.result
    node.index = 1
    node.name = "converged"
    results = _run_identifier_rules(ids, "generic/identifiers.py")
    assert [r.success for r in results] == [True, True]
    node.index = 999999
    results = _run_identifier_rules(ids, "generic/identifiers.py")
    assert [r.success for r in results] == [False]


@pytest.mark.parametrize(
    "version, ids_name, path",
    [
        ("3.30.0", "spectrometer_x_ray_crystal", "crystal/geometry_type"),
        (
            "3.35.0",
            "spectrometer_visible",
            "channel[0]/geometry_matrix/emission_grid/grid_type",
        ),
    ],
)
def test_unresolvable_identifier_reference_is_skipped(version, ids_name, path):
    # These DDs refer to identifier files for which no enumeration is registered
    ids = imas.IDSFactory(version).new(ids_name)
    if ids_name == "spectrometer_visible":
        ids.channel.resize(1)
    ids[path].index = 999999
    assert _run_identifier_rules(ids, "generic/identifiers.py") == []
