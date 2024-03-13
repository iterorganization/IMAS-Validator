Using the IMAS IDS validator
============================

.. note::
  This is the API mostly for developers,  documentation for CLI usage will be added when it becomes available.


Validating rulesets
-------------------

Provide a list of rulesets, an ids url, a list of paths where to look for rulesets and whether or not to apply the generic ruleset.

.. code-block:: python

  from ids_validator.validate_options import ValidateOptions
  from ids_validator.validate.validate import validate

  rulesets = ['ITER-MD', 'MyCustomRules']
  imas_uri = "imas:hdf5?path=path/to/data/entry"
  extra_rule_dirs = ['path/to/my/custom/rule/dirs/rulesets', 'another/path/rulesets_custom']
  apply_generic = True
  use_pdb = False

  validate_options = ValidateOptions(extra_rule_dirs=extra_rule_dirs, apply_generic=apply_generic, use_pdb=use_pdb)
  results = validate(rulesets, imas_uri, validate_options=validate_options)

You can also set the environment variable `RULESET_PATH` to show the loading tool where to look for rule sets.

.. code-block:: bash

  export RULESET_PATH=path/to/my/custom/rule/dirs/rulesets:another/path/rulesets_custom

Loading IDSValidationRules
--------------------------

Provide a list of rulesets, whether or not to apply the generic ruleset and a list of paths where to look for rulesets.

.. code-block:: python

  from ids_validator.validate_options import ValidateOptions
  from ids_validator.rules.loading import load_rules
  from ids_validator.validate.result import ResultCollector

  rulesets = ['ITER-MD', 'MyCustomRules']
  extra_rule_dirs = ['path/to/my/custom/rule/dirs/rulesets', 'another/path/rulesets_custom']
  apply_generic = True
  use_pdb = False

  validate_options = ValidateOptions(extra_rule_dirs=extra_rule_dirs, apply_generic=apply_generic, use_pdb=use_pdb)
  result_collector = ResultCollector(validate_options=validate_options)
  rules_list = load_rules(
    rulesets=rulesets,
    result_collector=result_collector,
    validate_options=validate_options,
  )
