"""Ruleset with extra rules that are not strictly required by the Data Dictionary.

These rules check good practices that give more confidence in the data, for
example that each element of an array of structures is identified by a non-empty
``name``. They are only applied when the ruleset is selected explicitly, e.g. with
``imas_validator validate <URI> -r pedantic``.

A rule may move to the ``generic`` ruleset if the Data Dictionary later makes the
corresponding requirement explicit.
"""
