.. _`rule filtering`:

Rule Filtering
==============

When running the validator, you can filter which subset of the found validation
rules should be applied.
This is done through the options:

name
    Checks whether or not a list of given strings are included in the rule name.
    Rule names are defined as ``ruleset/file.py:function_name``
    (e.g. ``iter/core_profiles.py:validate_temperature``).
    A string equal to a ruleset name (e.g. ``iter``), optionally followed by
    ``/...``, also selects that ruleset, so it does not need to be listed in
    ``rulesets``.

ids
    Checks whether or not a list of given IDS names are all included in the rule
    ``ids_names`` (exact match). Rule ids_names are defined as
    ``('ids_name_1', 'ids_name_2')``.

The filter returns only the rules that adhere to all supplied conditions.

On the command line, these options are ``--filter_name``, ``--filter_ids`` and
``--filter`` (which sends IDS names to ``ids`` and other strings to ``name``).
For example, ``imas_validator validate <uri> --filter_name iter`` runs the
rules of the ``iter`` ruleset. Because these options take several values, put
them after the URIs (or end them with ``--``).

IDS data is loaded only when its name and occurrence match a selected rule,
or when it is an additional input to a selected cross-IDS rule. Wildcard rules
can still require all IDSs. Version constraints are checked after loading,
using the stored IDS's Data Dictionary version.

Examples
--------

- Only run rules with ``time`` in their name

  .. code-block:: python

    rule_filter = RuleFilter(name = ['time'])

- Only run rules concerning ``core_profiles`` IDSs

  .. code-block:: python

    rule_filter = RuleFilter(ids = ['core_profiles'])

- Only run rules with both ``core`` and ``density`` in their name

  .. code-block:: python

    rule_filter = RuleFilter(name = ['core', 'density'])

- Only run rules with ``temperature`` in their name concerning ``equilibrium`` IDSs

  .. code-block:: python

    rule_filter = RuleFilter(name = ['temperature'], ids = ['equilibrium'])

.. seealso:: API documentation for :py:class:`~imas_validator.validate_options.RuleFilter`.
