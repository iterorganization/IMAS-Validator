try:
    import imaspy as imas  # type: ignore
except ImportError:
    import imas  # type: ignore

from typing import List


import numpy as np
import pytest

from ids_validator.rules.helpers import Approx, Decreasing, Increasing, Parent, Select
from ids_validator.validate.ids_wrapper import IDSWrapper


@pytest.fixture
def select_ids() -> imas.ids_toplevel.IDSToplevel:
    ids = imas.IDSFactory("3.40.1").new("core_profiles")
    ids.ids_properties.homogeneous_time = 0
    ids.ids_properties.comment = "Test comment"
    ids.time = [0.0, 1.1, 2.2]

    ids.profiles_1d.resize(2)
    ids.profiles_1d[0].time = 1.1
    # profiles_1d[1].time is unset

    return ids


def test_select(select_ids):
    with pytest.raises(TypeError):
        Select(select_ids, "")  # IDS must be wrapped
    with pytest.raises(TypeError):
        Select(IDSWrapper(False), "")  # Wrapped object must be an IDS
    Select(IDSWrapper(select_ids), "")
    Select(IDSWrapper(select_ids.time), "")


def assert_select_matches(selection: Select, expected: List[imas.ids_base.IDSBase]) -> None:
    """Test helper for asserting that the selection matches expected IDS elements"""
    unwrapped_selections = sorted((wrapped._obj for wrapped in selection), key=id)
    expected.sort(key=id)
    assert unwrapped_selections == expected


def test_select_regex(select_ids):
    # Match everything containing time
    assert_select_matches(
        Select(IDSWrapper(select_ids), "time"),
        [
            select_ids.ids_properties.homogeneous_time,
            select_ids.profiles_1d[0].time,
            select_ids.time,
        ],
    )
    # Match everything starting with time
    assert_select_matches(
        Select(IDSWrapper(select_ids), "^time"),
        [
            select_ids.time,
        ],
    )
    # Match everythin for which the name is time
    assert_select_matches(
        Select(IDSWrapper(select_ids), "(^|/)time$"),
        [
            select_ids.profiles_1d[0].time,
            select_ids.time,
        ],
    )


def test_select_leaf_only(select_ids):
    # Match everything in ids_properties (leafs only)
    assert_select_matches(
        Select(IDSWrapper(select_ids), "ids_properties"),
        [
            select_ids.ids_properties.homogeneous_time,
            select_ids.ids_properties.comment,
        ],
    )
    # Match everything in ids_properties (also structures)
    assert_select_matches(
        Select(IDSWrapper(select_ids), "ids_properties", leaf_only=False),
        [
            select_ids.ids_properties,
            select_ids.ids_properties.homogeneous_time,
            select_ids.ids_properties.comment,
        ],
    )
    # Match AOS
    assert_select_matches(
        Select(IDSWrapper(select_ids), "profiles_1d", leaf_only=False),
        [
            select_ids.profiles_1d,
            select_ids.profiles_1d[0],
            select_ids.profiles_1d[0].time,
            select_ids.profiles_1d[1],
        ],
    )


def test_select_empty_nodes(select_ids):
    # Select regex only selects empty nodes
    assert_select_matches(Select(IDSWrapper(select_ids), "creation_date"), [])
    assert_select_matches(
        Select(IDSWrapper(select_ids), "creation_date", has_value=False),
        [select_ids.ids_properties.creation_date],
    )
    # Match everythin for which the name is time
    assert_select_matches(
        Select(IDSWrapper(select_ids), "(^|/)time$", has_value=False),
        [
            select_ids.profiles_1d[0].time,
            select_ids.profiles_1d[1].time,
            select_ids.time,
        ],
    )


@pytest.mark.parametrize("func", (Increasing, Decreasing))
def test_increasing_decreasing_errors(select_ids, func):
    with pytest.raises(TypeError):  # IDS must be wrapped
        func(select_ids)
    with pytest.raises(ValueError):  # Wrapped object must be an IDS
        func(IDSWrapper(False))
    with pytest.raises(ValueError):  # Wrapped object must be 1d
        func(IDSWrapper(select_ids.ids_properties.homogeneous_time))
    with pytest.raises(ValueError):  # Wrapped object must be 1d
        func(IDSWrapper(np.arange(6).reshape([2, 3])))
    assert Increasing(IDSWrapper(np.arange(6)))


def test_increasing():
    assert Increasing(IDSWrapper([1, 2, 3]))
    assert not Increasing(IDSWrapper([1, 3, 2]))
    assert not Increasing(IDSWrapper([1, 2, 2]))
    assert not Increasing(IDSWrapper([3, 2, 1]))
    assert Increasing(IDSWrapper([]))
    assert Increasing(IDSWrapper([1]))


def test_decreasing():
    assert not Decreasing(IDSWrapper([1, 2, 3]))
    assert not Decreasing(IDSWrapper([1, 3, 2]))
    assert not Decreasing(IDSWrapper([2, 2, 1]))
    assert Decreasing(IDSWrapper([3, 2, 1]))
    assert Decreasing(IDSWrapper([]))
    assert Decreasing(IDSWrapper([1]))


def test_increasing_works_on_ids(select_ids):
    select_ids.time = [1, 2, 3]
    assert Increasing(IDSWrapper(select_ids).time)
    select_ids.time = [3, 2, 1]
    assert not Increasing(IDSWrapper(select_ids).time)


def test_increasing_ids_nodes():
    a = IDSWrapper([1, 2, 3], ids_nodes=[("a", 0)])
    b = IDSWrapper([4, 5, 6], ids_nodes=[("b", 1)])
    c = Increasing(a + b)
    assert c
    assert c._ids_nodes == [("a", 0), ("b", 1)]


def test_approx():
    for x, y, rtol, atol, z in [
        ([1, 2], [3, 4], 1e-5, 1e-8, False),
        ([1.0, 2.0], [1.0, 2.0 + 1e-6], 1e-5, 1e-8, True),
        (1.0, 1.0 + 1e-6, 1e-5, 1e-8, True),
        (1.0, 1.0 + 1e-6, 1e-5, 1e-5, True),
        (1.0, 1.0 + 1e-4, 1e-5, 1e-8, False),
        (1.0, 1.0 + 1e-6, 1e-8, 1e-8, False),
        (0.0, 0.0 - 1e-6, 1e-5, 1e-8, False),
    ]:
        a = IDSWrapper(x, ids_nodes=[("a", 0)])
        b = IDSWrapper(y, ids_nodes=[("b", 1)])
        c = Approx(a, b, rtol=rtol, atol=atol)
        assert c == z
        assert c._ids_nodes == [("a", 0), ("b", 1)]


def test_approx_non_wrapper():
    a = IDSWrapper(1.0, ids_nodes=[("a", 0)])
    b = 1.0 + 1e-6
    c = Approx(a, b, rtol=1e-5, atol=1e-8)
    assert c
    assert c._ids_nodes == [("a", 0)]
    d = Approx(a, b, rtol=1e-7, atol=1e-8)
    assert not d
    assert d._ids_nodes == [("a", 0)]


def test_parent(select_ids):
    node = IDSWrapper(select_ids.ids_properties.homogeneous_time)
    assert Parent(node)._obj is select_ids.ids_properties
    assert Parent(Parent(node))._obj is Parent(node, 2)._obj is select_ids
    with pytest.raises(ValueError):
        Parent(node, 3)
    with pytest.raises(ValueError):
        Parent(IDSWrapper(select_ids))

    node = IDSWrapper(select_ids.profiles_1d[0].time)
    assert Parent(node, 1)._obj is select_ids.profiles_1d[0]
    assert Parent(node, 2)._obj is select_ids.profiles_1d
    assert Parent(node, 3)._obj is select_ids

    # Getting parents <= 0 will just return and IDSWrapper with the same node:
    assert Parent(node, 0)._obj is node._obj
    assert Parent(node, -1)._obj is node._obj
