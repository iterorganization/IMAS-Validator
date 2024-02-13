Using the IMAS IDS validator
=========================

.. note::
  This is the API mostly for developers,  documentation for CLI usage will be added when it becomes available.


Validating rulesets
-------------------

Provide a list of rulesets, an ids url, a list of paths where to look for rulesets and whether or not to apply the generic ruleset.

.. code-block:: python

  from ids_validator.validate.validate import validate

  rulesets = ['ITER-MD', 'MyCustomRules']
  ids_url = "url/to/specific/ids"
  extra_rule_dirs = ['path/to/my/custom/rule/dirs/rulesets', 'another/path/rulesets_custom']
  apply_generic = True

  results = validate(rulesets, ids_url, extra_rule_dirs, apply_generic)

You can also set the environment variable `RULESET_PATH` to show the loading tool where to look for rule sets.

.. code-block:: bash

  export RULESET_PATH=path/to/my/custom/rule/dirs/rulesets:another/path/rulesets_custom

Loading IDSValidationRules
--------------------------

Provide a list of rulesets, whether or not to apply the generic ruleset and a list of paths where to look for rulesets.

.. code-block:: python

  from ids_validator.rules.loading import load_rules
  from ids_validator.validate.result import ResultCollector

  rulesets = ['ITER-MD', 'MyCustomRules']
  apply_generic = True
  extra_rule_dirs = ['path/to/my/custom/rule/dirs/rulesets', 'another/path/rulesets_custom']
  result_collector = ResultCollector()
  rules_list = load_rules(
    rulesets=rulesets,
    apply_generic=apply_generic,
    extra_rule_dirs=extra_rule_dirs,
    result_collector=result_collector
  )
