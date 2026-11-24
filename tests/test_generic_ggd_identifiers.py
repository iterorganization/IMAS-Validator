"""Identifier checks of the generic GGD rules (generic/ggd.py)."""

import imas
import pytest

from imas_validator.rules.loading import load_rules
from imas_validator.validate.result_collector import ResultCollector
from imas_validator.validate.rule_executor import RuleExecutor
from imas_validator.validate_options import RuleFilter, ValidateOptions

VERSIONS = ["3.40.1", imas.dd_zip.latest_dd_version()]


def _identifier(node, index, enum):
    node.index = index
    node.name = enum(index).name if index in [m.index for m in enum] else "private"
    node.description = "description"


def _edge_profiles(version, coordinates_type=(1, 2), subset_index=5):
    ids = imas.IDSFactory(version).edge_profiles()
    ids.ids_properties.homogeneous_time = imas.ids_defs.IDS_TIME_MODE_HOMOGENEOUS
    ids.time = [0.0]
    ids.grid_ggd.resize(1)
    grid = ids.grid_ggd[0]
    grid.time = 0.0
    _identifier(grid.identifier, 1, imas.identifiers.ggd_identifier)
    grid.space.resize(1)
    space = grid.space[0]
    _identifier(space.identifier, 1, imas.identifiers.ggd_space_identifier)
    space.geometry_type.index = 0
    if space.coordinates_type.metadata.data_type == imas.ids_data_type.IDSDataType.INT:
        space.coordinates_type = list(coordinates_type)  # DD3: INT_1D
    else:
        space.coordinates_type.resize(len(coordinates_type))
        for node, index in zip(space.coordinates_type, coordinates_type):
            _identifier(node, index, imas.identifiers.coordinate_identifier)
    space.objects_per_dimension.resize(1)
    nodes = space.objects_per_dimension[0]
    nodes.geometry_content.index = 1  # node_coordinates
    nodes.object.resize(2)
    for i, obj in enumerate(nodes.object):
        obj.geometry = [float(i)] * len(coordinates_type)
    grid.grid_subset.resize(1)
    subset = grid.grid_subset[0]
    _identifier(subset.identifier, subset_index, imas.identifiers.ggd_subset_identifier)
    subset.dimension = 1
    return ids


def _run(ids, rule_name):
    options = ValidateOptions(rule_filter=RuleFilter(name=[rule_name]))
    collector = ResultCollector(options, "")
    rules = [
        rule
        for rule in load_rules(collector, options)
        if rule.ids_names[0] in ("*", "edge_profiles")
    ]
    executor = RuleExecutor(None, rules, collector, options)
    for rule in rules:
        collector.set_context(rule, [(ids, ids.metadata.name, 0)])
        executor.run(rule, [ids])
    assert all(result.exc is None for result in collector.results)
    return {
        result.rule.name.split(":")[-1]
        for result in collector.results
        if not result.success
    }


@pytest.mark.parametrize("version", VERSIONS)
def test_valid_grid(version):
    assert _run(_edge_profiles(version), "generic/") == set()


@pytest.mark.parametrize("version", VERSIONS)
def test_unknown_subset_index_reported_once(version):
    failed = _run(_edge_profiles(version, subset_index=999), "generic/")
    assert failed == {"validate_identifier_index"}


@pytest.mark.parametrize("version", VERSIONS)
def test_unknown_coordinates_type(version):
    failed = _run(_edge_profiles(version, coordinates_type=(1, 9999)), "generic/")
    if version.startswith("3."):
        # DD3 INT_1D has no identifier metadata: only ggd.py can check it
        assert failed == {"validate_space_coordinates_type_identifier"}
    else:
        assert failed == {"validate_identifier_index"}


@pytest.mark.parametrize("version", VERSIONS)
def test_private_coordinates_type_not_checked(version):
    assert _run(_edge_profiles(version, coordinates_type=(1, -7)), "generic/") == set()


@pytest.mark.parametrize("version", VERSIONS)
def test_unfilled_identifier(version):
    ids = _edge_profiles(version)
    ids.grid_ggd[0].grid_subset[0].identifier.description = ""
    failed = _run(ids, "ggd.py")
    assert failed == {"validate_grid_subset_identifier"}


@pytest.mark.parametrize("version", VERSIONS)
def test_geometry_size_uses_geometry_content_index(version):
    ids = _edge_profiles(version)
    ids.grid_ggd[0].space[0].objects_per_dimension[0].object[0].geometry = [0.0] * 5
    assert _run(ids, "validate_obj_per_dim_geometry_size") == {
        "validate_obj_per_dim_geometry_size"
    }


@pytest.mark.parametrize("version", VERSIONS)
def test_geometry_content_per_dimension(version):
    ids = _edge_profiles(version)
    ids.grid_ggd[0].space[0].objects_per_dimension[0].geometry_content.index = 21
    assert _run(ids, "validate_obj_per_dim_geometry_content") == {
        "validate_obj_per_dim_geometry_content"
    }
