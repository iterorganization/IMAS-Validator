.. _`rule filtering`:

Rule Filtering
==============

When running the validator, you can filter which subset of the found validation
rules should be applied.
This is done through the options:

name
    Checks whether or not a list of given strings are included in the rule name.
    Rule names are defined as ``ruleset/file/function_name``
    (e.g. ``ITER-MD/core_profiles.py/validate_temperature``).

ids
    Checks whether or not a list of given strings are included in the rule
    ``ids_names``. Rule ids_names are defined as ``('ids_name_1', 'ids_name_2')``.

The filter returns only the rules that adhere to all supplied conditions.

Examples
--------

- Only run rules with ``time`` in their name

  .. code-block:: python

    rule_filter = RuleFilter(name = ['time'])

- Only run rules concerning ``core_profile`` IDSs

  .. code-block:: python

    rule_filter = RuleFilter(ids = ['core_profile'])

- Only run rules with both ``core`` and ``density`` in their name

  .. code-block:: python

    rule_filter = RuleFilter(name = ['core', 'density'])

- Only run rules with ``temperature`` in their name concerning ``equilibrium`` IDSs

  .. code-block:: python

    rule_filter = RuleFilter(name = ['temperature'], ids = ['equilibrium'])

.. seealso:: API documentation for :py:class:`~imas_validator.validate_options.RuleFilter`.
