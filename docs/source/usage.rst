.. _`usage`:

Using the IMAS-Validator
========================

.. note::
  This is the API mostly for developers,  documentation for CLI usage will be added when it becomes available.


Validating rulesets
-------------------

You should provide:

- IDS url
- Names of rulesets to be applied (optional)
- Whether or not to load the rulesets bundled with imas_validator (optional)
- Paths where to look for rule sets (optional)
- Whether or not to apply the generic ruleset (optional)
- Whether or not to drop into debugger for failed tests (optional)
- Filter criteria (optional)

You can also set the logging level of the imas_validator tool.
This can be set to 'WARNING' (default) to get messages when something is potentially wrong,
or it can be set to 'INFO' to get more information for debugging purposes

.. code-block:: python

  import logging
  from imas_validator.validate_options import ValidateOptions, RuleFilter
  from imas_validator.validate.validate import validate
  logger = logging.getLogger('imas_validator')
  logger.setLevel(logging.INFO)


  imas_uri = "imas:hdf5?path=path/to/data/entry"
  validate_options = ValidateOptions(
    rulesets = ['ITER-MD', 'MyCustomRules'],
    use_bundled_rulesets = True,
    extra_rule_dirs = ['path/to/my/custom/rule/dirs/rulesets', 'another/path/rulesets_custom'],
    apply_generic = True,
    use_pdb = False,
    rule_filter = RuleFilter(name = ['time'], ids = ['core_profile']),
  )
  results = validate(imas_uri=imas_uri, validate_options=validate_options)

You can also set the environment variable `RULESET_PATH` to show the loading tool where to look for rule sets.

.. code-block:: bash

  export RULESET_PATH=path/to/my/custom/rule/dirs/rulesets:another/path/rulesets_custom

Loading IMASValidationRules
---------------------------

Provide a list of rulesets, whether or not to apply the generic ruleset and a list of paths where to look for rulesets.

.. code-block:: python

  from imas import DBEntry

  from imas_validator.validate_options import ValidateOptions, RuleFilter
  from imas_validator.rules.loading import load_rules
  from imas_validator.validate.result import ResultCollector


  imas_uri = "imas:hdf5?path=path/to/data/entry"
  validate_options = ValidateOptions(
    rulesets = ['ITER-MD', 'MyCustomRules'],
    extra_rule_dirs = ['path/to/my/custom/rule/dirs/rulesets', 'another/path/rulesets_custom'],
    apply_generic = True,
    use_pdb = False,
    rule_filter = RuleFilter(name = ['time'], ids = ['core_profile']),
  )
  result_collector = ResultCollector(validate_options=validate_options, imas_uri=imas_uri)
  rules_list = load_rules(validate_options=validate_options)
