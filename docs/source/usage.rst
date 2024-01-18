Using IMAS IDS Validation
=================

Defining IDSValidationRules
---------------------------

IDSValidationRule functions are defined in directories as provided by the user.
They are grouped in directories per ruleset by name based on which they are filtered in the loading function.
Inside these directories are python files which contain the rules
The folder structure is as follows:
.. code-block:: text

  |-- rulesets
  |   |-- generic
  |   |   |-- common_ids.py
  |   |   └-- core_profiles.py
  |   └-- ITER-MD
  |       |-- common_ids.py
  |       └-- core_profiles.py
  └-- rulesets_custom
      |-- ITER-MD
      |   |-- common_ids.py
      |   └-- core_profiles.py
      └-- MyCustomRules
          |-- common_ids.py
          └-- equilibrium.py


The rules are defined inside the python files as follows:

.. code-block:: python

  @ids_validator("*", min_dd_version="3.39.0")  # noqa: F821
  def validate_ids_plugins_metadata(ids):
    plugins = ids.ids_properties.plugins
    plugins.node[:].path != ""
    plugins.node[:].put_operation[:].name != ""
    # etc.

  @ids_validator("gyrokinetics")  # noqa: F821
  def validate_gyrokinetics_electron_definition(gk):
    # check electron definition
    for species in gk.species:
      if species.charge_norm != -1:
        continue
      species.mass_norm == 2.724437108e-4
      species.temperature_norm == 1.0
      species.density_norm == 1.0
      break
    else:
      error("No electron species found", gk.species)

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

You can also set the environment variable `RULESET_PATH` to show the loading tool where to look for rule sets.

.. code-block:: bash

  export RULESET_PATH=path/to/my/custom/rule/dirs/rulesets:another/path/rulesets_custom
