Defining validation rules
===========================

Ruleset folder structure
------------------------

IDSValidationRule functions are defined in directories as provided by the user.
They are grouped in directories per ruleset by name based on which they are filtered in the loading function.
Inside these directories are python files which contain the rules.
The folder structure is as follows:

- rule directories contain rulesets (rule_dir, rule_dir_custom) and are found using the CLI argument --extra-rule-dirs/-e or through the env variable RULESET_PATH
- rulesets contain validation rule files (Diagnostics, ITER-MD, ECR, MyCustomRules) and are found using the CLI argument ruleset --ruleset/-r
- validation rule files contain validation functions

This structure is shown underneath:

.. code-block:: text

  ├── rule_dir
  |   ├── Diagnostics
  |   |   ├── common_ids.py
  |   |   └── equilibrium.py
  |   └── ITER-MD
  |       ├── common_ids.py
  |       └── core_profiles.py
  └── rule_dir_custom
      ├── ECR
      |   ├── common_ids.py
      |   └── core_profiles.py
      └── MyCustomRules
          ├── common_ids.py
          └── equilibrium.py


Rule definition
---------------

The rules are defined inside the python files as follows:

.. code-block:: python

  @validator("*")
  def validate_ids_plugins_metadata(ids):
    plugins = ids.ids_properties.plugins
    for node in plugins.node:
      assert node.path != ""
      for name in node.put_operation:
        assert name != ""
    # etc.

  @validator("gyrokinetics")
  def validate_gyrokinetics_electron_definition(gk):
    # check electron definition
    for species in gk.species:
      if species.charge_norm != -1:
        continue
      assert species.mass_norm == 2.724437108e-4
      assert species.temperature_norm == 1.0
      assert species.density_norm == 1.0
      break
    else:
      error("No electron species found", gk.species)

  @validator("core_profiles")
  def validate_ion_charge(cp):
    """Validate that profiles_1d/ion/z_ion is defined"""
    for p1d in cp.profiles_1d:
      for ion in p1d.ion:
        assert ion.z_ion.has_value
        
For a step-by-step tutorial on how to define rules, see :ref:`rule tutorial`
.. seealso:: :py:class:`Helper methods<ids_validator.rules.helpers>` were made to make it easier to define validation rules.
