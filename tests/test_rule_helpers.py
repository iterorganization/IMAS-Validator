from typing import List

import imaspy
import pytest
from imaspy.ids_base import IDSBase
from imaspy.ids_toplevel import IDSToplevel

from ids_validator.rules.helpers import Select
from ids_validator.validate.ids_wrapper import IDSWrapper


@pytest.fixture
def select_ids() -> IDSToplevel:
    ids = imaspy.IDSFactory("3.40.1").new("core_profiles")
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


def assert_select_matches(selection: Select, expected: List[IDSBase]) -> None:
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
