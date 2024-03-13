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


  imas_uri = "imas:hdf5?path=path/to/data/entry"
  validate_options = ValidateOptions(
    rulesets = ['ITER-MD', 'MyCustomRules'],
    extra_rule_dirs = ['path/to/my/custom/rule/dirs/rulesets', 'another/path/rulesets_custom'],
    apply_generic = True,
    use_pdb = False,
  )
  results = validate(imas_uri=imas_uri, validate_options=validate_options)

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


  validate_options = ValidateOptions(
    rulesets = ['ITER-MD', 'MyCustomRules']
    extra_rule_dirs = ['path/to/my/custom/rule/dirs/rulesets', 'another/path/rulesets_custom']
    apply_generic = True
    use_pdb = False
  )
  result_collector = ResultCollector(validate_options=validate_options)
  rules_list = load_rules(validate_options=validate_options)
