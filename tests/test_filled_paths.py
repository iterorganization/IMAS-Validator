"""Coverage paths must retain AoS indices without searching parent arrays."""

from collections import Counter
from unittest.mock import Mock

import imas
import pytest
from imas.ids_base import IDSBase
from imas.ids_struct_array import IDSStructArray
from imas.ids_structure import IDSStructure

from imas_validator.validate.result import CoverageMap
from imas_validator.validate.result_collector import ResultCollector
from imas_validator.validate.validate import validate
from imas_validator.validate_options import ValidateOptions


@pytest.fixture
def collector():
    return ResultCollector(ValidateOptions(track_node_dict=True), "")


def legacy_paths(ids):
    paths = set()
    imas.util.visit_children(
        lambda node: paths.add(node._path), ids, leaf_only=True, visit_empty=False
    )
    return paths


def collect(collector, ids, occurrence=0):
    key = (ids.metadata.name, occurrence)
    collector.append_nodes_dict({}, [(ids, *key)])
    return collector.filled_nodes_dict[key]


@pytest.mark.parametrize("fixture", ["test_data_core_profiles", "test_data_waves"])
def test_paths_match_existing_traversal(collector, request, fixture):
    ids = request.getfixturevalue(fixture)._obj
    assert collect(collector, ids) == legacy_paths(ids)


@pytest.mark.parametrize("dd_version", ["3.40.1", "4.0.0"])
def test_sparse_nested_arrays(collector, dd_version):
    ids = imas.IDSFactory(dd_version).core_profiles()
    ids.ids_properties.comment = "Nested arrays"
    ids.profiles_1d.resize(12)
    ids.profiles_1d[0].electrons.temperature = [1.0, 2.0]
    ids.profiles_1d[3].ion.resize(4)
    ids.profiles_1d[3].ion[2].state.resize(3)
    ids.profiles_1d[3].ion[2].state[1].z_min = 0.0
    ids.profiles_1d[11].ion.resize(11)
    ids.profiles_1d[11].ion[10].temperature = [3.0]
    # Materialized but empty primitives/structures/AoS must not become coverage.
    ids.time
    ids.profiles_1d[1].grid.rho_tor_norm
    ids.profiles_1d[2].ion.resize(2)
    ids.profiles_1d[4].ion.resize(0)

    expected = {
        "ids_properties/comment",
        "profiles_1d[0]/electrons/temperature",
        "profiles_1d[3]/ion[2]/state[1]/z_min",
        "profiles_1d[11]/ion[10]/temperature",
    }
    assert collect(collector, ids) == legacy_paths(ids) == expected


@pytest.mark.parametrize("allocated", [False, True])
def test_empty_ids(collector, allocated):
    ids = imas.IDSFactory("3.40.1").core_profiles()
    if allocated:
        ids.ids_properties.comment
        ids.profiles_1d.resize(3)
        ids.profiles_1d[1].ion.resize(2)
        ids.profiles_1d[1].ion[0].temperature
    assert collect(collector, ids) == legacy_paths(ids) == set()


def test_paths_do_not_use_parent_search(
    collector, test_data_core_profiles, monkeypatch
):
    ids = test_data_core_profiles._obj
    expected = legacy_paths(ids)

    def forbidden_path(node):
        pytest.fail("Filled paths must not be reconstructed with node._path")

    monkeypatch.setattr(IDSBase, "_path", property(forbidden_path))
    assert collect(collector, ids) == expected


@pytest.mark.parametrize("size", [100, 1_000, 10_000])
def test_array_accesses_scale_linearly(collector, monkeypatch, size):
    ids = imas.IDSFactory("3.40.1").core_profiles()
    ids.profiles_1d.resize(size)
    expected = set()
    for index, profile in enumerate(ids.profiles_1d):
        profile.time = float(index)
        expected.add(f"profiles_1d[{index}]/time")
        profile.ion.resize(2)
        for ion_index, ion in enumerate(profile.ion):
            ion.temperature = [1.0]
            ion.density = [2.0]
            prefix = f"profiles_1d[{index}]/ion[{ion_index}]"
            expected.update([f"{prefix}/temperature", f"{prefix}/density"])

    accesses = 0
    original_getitem = IDSStructArray.__getitem__

    def counted_getitem(array, index):
        nonlocal accesses
        accesses += 1
        return original_getitem(array, index)

    monkeypatch.setattr(IDSStructArray, "__getitem__", counted_getitem)
    assert collect(collector, ids) == expected
    # One pass through the outer AoS and each inner AoS, including end probes.
    # Allow a constant factor without imposing a machine-dependent time limit.
    assert accesses <= 6 * size + 2


def test_collect_once_per_ids_and_occurrence(collector, monkeypatch):
    factory = imas.IDSFactory("3.40.1")
    first, second, waves, empty = (
        factory.core_profiles(),
        factory.core_profiles(),
        factory.waves(),
        factory.core_profiles(),
    )
    first.ids_properties.comment = "First"
    second.profiles_1d.resize(2)
    second.profiles_1d[1].time = 1.0
    waves.ids_properties.homogeneous_time = 0
    idss = [
        (first, "core_profiles", 0),
        (second, "core_profiles", 3),
        (waves, "waves", 0),
        (empty, "core_profiles", 7),
    ]
    roots = {id(ids) for ids, _, _ in idss}
    visits = Counter()
    original_iter = IDSStructure.iter_nonempty_

    def counted_iter(node, **kwargs):
        if id(node) in roots:
            visits[id(node)] += 1
        yield from original_iter(node, **kwargs)

    monkeypatch.setattr(IDSStructure, "iter_nonempty_", counted_iter)
    for _ in range(3):
        for ids, name, occurrence in idss:
            collector.set_context(Mock(), [(ids, name, occurrence)])
            collector.assert_(True)
    collector.append_nodes_dict(
        {("core_profiles", 3): {"profiles_1d[1]/time", "time"}}, idss
    )

    assert visits == {root: 1 for root in roots}
    assert collector.filled_nodes_dict == {
        ("core_profiles", 0): {"ids_properties/comment"},
        ("core_profiles", 3): {"profiles_1d[1]/time"},
        ("waves", 0): {"ids_properties/homogeneous_time"},
        ("core_profiles", 7): set(),
    }
    assert collector.coverage_dict() == {
        ("core_profiles", 0): CoverageMap(1, 0, 0),
        ("core_profiles", 3): CoverageMap(1, 2, 1),
        ("waves", 0): CoverageMap(1, 0, 0),
        ("core_profiles", 7): CoverageMap(0, 0, 0),
    }


def test_paths_after_reordering_and_resizing(collector):
    ids = imas.IDSFactory("3.40.1").core_profiles()
    ids.profiles_1d.resize(3)
    ids.profiles_1d[0].time = 1.0
    ids.profiles_1d[2].electrons.temperature = [2.0]
    assert collect(collector, ids) == legacy_paths(ids)

    profiles = ids.profiles_1d
    profiles[0], profiles[2] = profiles[2], profiles[0]
    profiles.resize(2, keep=True)
    profiles.resize(4, keep=True)
    profiles[3].time = 3.0
    # A new collector models a new validation run; no paths are cached on nodes.
    fresh = ResultCollector(ValidateOptions(track_node_dict=True), "")
    assert (
        collect(fresh, ids)
        == legacy_paths(ids)
        == {
            "profiles_1d[0]/electrons/temperature",
            "profiles_1d[3]/time",
        }
    )


@pytest.mark.parametrize("preload", [False, True])
def test_lazy_ids_rejected_without_caching_partial_coverage(
    collector, tmp_path, preload
):
    uri = str(tmp_path / "coverage.nc")
    with imas.DBEntry(uri, "x", dd_version="3.40.1") as entry:
        ids = entry.factory.core_profiles()
        ids.ids_properties.homogeneous_time = 0
        ids.profiles_1d.resize(2)
        for index, profile in enumerate(ids.profiles_1d):
            profile.time = float(index)
        entry.put(ids)
        lazy = entry.get("core_profiles", lazy=True)
        if preload:
            assert lazy.profiles_1d[1].time == 1.0

        with pytest.raises(RuntimeError, match="lazy loaded IDS"):
            legacy_paths(lazy)
        for _ in range(2):
            with pytest.raises(RuntimeError, match="lazy loaded IDS"):
                collect(collector, lazy)
            assert ("core_profiles", 0) not in collector.filled_nodes_dict

        eager = entry.get("core_profiles")
        assert collect(collector, eager) == legacy_paths(eager)


def test_failed_traversal_can_be_retried(collector, monkeypatch):
    ids = imas.IDSFactory("3.40.1").core_profiles()
    ids.ids_properties.comment = "Visited before the failing AoS"
    ids.profiles_1d.resize(2)
    ids.profiles_1d[0].time = 0.0
    ids.profiles_1d[1].time = 1.0
    expected = legacy_paths(ids)
    original_getitem = IDSStructArray.__getitem__

    def failing_getitem(array, index):
        if array is ids.profiles_1d and index == 1:
            raise RuntimeError("Interrupted traversal")
        return original_getitem(array, index)

    with monkeypatch.context() as patch:
        patch.setattr(IDSStructArray, "__getitem__", failing_getitem)
        with pytest.raises(RuntimeError, match="Interrupted traversal"):
            collect(collector, ids)
    assert ("core_profiles", 0) not in collector.filled_nodes_dict
    assert collect(collector, ids) == expected


def test_validate_netcdf_occurrences(tmp_path):
    uri = str(tmp_path / "coverage.nc")
    expected = {}
    with imas.DBEntry(uri, "x", dd_version="3.40.1") as entry:
        for occurrence, size in [(0, 2), (3, 4)]:
            ids = entry.factory.core_profiles()
            ids.ids_properties.homogeneous_time = 0
            ids.profiles_1d.resize(size)
            for index, profile in enumerate(ids.profiles_1d):
                profile.time = float(index)
                profile.ion.resize(2)
                profile.ion[1].z_ion = 1.0
            entry.put(ids, occurrence)
            # Include any metadata added by DBEntry.put in the reference count.
            expected[("core_profiles", occurrence)] = CoverageMap(
                len(legacy_paths(entry.get("core_profiles", occurrence))), 1, 1
            )

    ruleset = tmp_path / "rules" / "coverage"
    ruleset.mkdir(parents=True)
    (ruleset / "check.py").write_text(
        '@validator("core_profiles")\n'
        "def check(cp):\n"
        "    assert cp.profiles_1d[1].ion[1].z_ion == 1.0\n"
        "    assert cp.profiles_1d[1].ion[1].z_ion > 0.0\n"
    )
    result = validate(
        uri,
        ValidateOptions(
            rulesets=["coverage"],
            extra_rule_dirs=[ruleset.parent],
            use_bundled_rulesets=False,
            apply_generic=False,
            track_node_dict=True,
        ),
    )
    assert len(result.results) == 4
    assert all(item.success and item.exc is None for item in result.results)
    assert result.coverage_dict == expected
    for item in result.results:
        assert item.nodes_dict == {item.idss[0]: {"profiles_1d[1]/ion[1]/z_ion"}}
