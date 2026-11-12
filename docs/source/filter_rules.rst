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

ids
    Checks whether or not a list of given IDS names are all included in the rule
    ``ids_names`` (exact match). Rule ids_names are defined as
    ``('ids_name_1', 'ids_name_2')``.

exclude_name
    Discards the rules whose name contains any of the given strings. Because rule
    names start with the ruleset name, ``iter/`` discards a whole ruleset.

exclude_ids
    Discards the rules that apply to any of the given IDS names (exact match).

The filter returns only the rules that adhere to all supplied conditions.

When ``name`` or ``ids`` is given and no ruleset is named in ``rulesets``,
all rulesets are searched for matching rules, not only ``generic``. This way,
``validate`` applies the same rules as ``explore`` lists for the same options.
Naming rulesets restricts the search to them (and ``generic``, unless it is
disabled). Exclusions alone don't extend the search: they only remove rules
from the default selection.

On the command line, these options are ``--filter_name``, ``--filter_ids``,
``--exclude_name`` and ``--exclude_ids``. The shortcuts ``-f``/``--filter``
and ``-x``/``--exclude`` take both kinds of strings: a string equal to an IDS
name goes to ``ids`` (``exclude_ids``), any other string to ``name``
(``exclude_name``). For example,
``imas_validator validate <uri> --filter_name validate_profiles_1d_q`` runs
the matching rule of the ``iter`` ruleset without naming the ruleset, and
``imas_validator validate <uri> -r iter -x ggd`` runs the ``generic`` and
``iter`` rules except the ones about GGD. Because these options take several
values, put them after the URIs (or end them with ``--``).

Use the explicit options rather than the shortcuts when:

- a string is also an IDS name but you want to match it in rule names. For
  example, ``--filter_name equilibrium`` selects the rules of the
  ``equilibrium.py`` files, while ``-f equilibrium`` (like
  ``--filter_ids equilibrium``) selects all the rules applying to the
  ``equilibrium`` IDS, including generic GGD rules;
- the command must behave the same in every environment, e.g. in scripts or
  CI. The shortcuts tell IDS names apart using the default Data Dictionary
  version of ``imas-python`` (set by ``IMAS_VERSION``), so an IDS that exists
  only in some DD versions (e.g. ``plasma_profiles``, new in DD 4) may be
  treated as a rule name in other environments.

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

- Run the ``core_profiles`` rules of all rulesets, except the ``scenarios`` ones

  .. code-block:: python

    rule_filter = RuleFilter(ids = ['core_profiles'], exclude_name = ['scenarios/'])

.. seealso:: API documentation for :py:class:`~imas_validator.validate_options.RuleFilter`.
