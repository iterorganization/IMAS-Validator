import argparse

from imas_validator.common.utils import (
    flatten_2d_list_or_return_empty,
    prepare_rule_filter_object,
)
from imas_validator.validate_options import RuleFilter


def test_flatten_2d_list_or_return_empty():
    assert flatten_2d_list_or_return_empty([]) == []
    assert flatten_2d_list_or_return_empty([["some_data", "some_data_2"]]) == [
        "some_data",
        "some_data_2",
    ]


def test_prepare_rule_filter_object():
    args = argparse.Namespace(
        filter=[
            [
                "rulename1",
                "core_profiles",
                "core_profiles:5",
                "summary/3",
                "equilibrium_rule_name",
            ]
        ],
        filter_name=[["rulename2", " rulename3", "summary"]],
        filter_ids=[["core_sources", "edge_profiles:3", "rulename3"]],
    )

    returned_rule_filter = prepare_rule_filter_object(args)

    assert isinstance(returned_rule_filter, RuleFilter)
    # name array contains everything passed by `filter_name` argument
    # and elements from 'filter' that are not IDS names
    # do not be confused by presence of "core_profiles:5" and "summary/3" here
    # for the moment of the development of this functionality
    # filtering does not support occurrences
    assert (
        returned_rule_filter.name.sort()
        == [
            "rulename2",
            " rulename3",
            "summary",
            "rulename1",
            "core_profiles:5",
            "summary/3",
            "equilibrium_rule_name",
        ].sort()
    )
    # ids array contains everything passed by `filter_ids` argument
    # and elements from 'filter' that exactly matches IDS names
    assert (
        returned_rule_filter.ids.sort()
        == ["core_sources", "edge_profiles:3", "rulename3", "core_profiles"].sort()
    )
