Defining validation rules
===========================

Ruleset folder structure
------------------------

IDSValidationRule functions are defined in directories as provided by the user.
They are grouped in directories per ruleset by name based on which they are filtered in the loading function.
Inside these directories are python files which contain the rules
The folder structure is as follows:

.. code-block:: text

  ├── rulesets
  |   ├── generic
  |   |   ├── common_ids.py
  |   |   └── core_profiles.py
  |   └── ITER-MD
  |       ├── common_ids.py
  |       └── core_profiles.py
  └── rulesets_custom
      ├── ITER-MD
      |   ├── common_ids.py
      |   └── core_profiles.py
      └── MyCustomRules
          ├── common_ids.py
          └── equilibrium.py


Rule definition
---------------

The rules are defined inside the python files as follows:

.. code-block:: python

  @validator("*", min_dd_version="3.39.0")  # noqa: F821
  def validate_ids_plugins_metadata(ids):
    plugins = ids.ids_properties.plugins
    assert plugins.node[:].path != ""
    assert plugins.node[:].put_operation[:].name != ""
    # etc.

  @validator("gyrokinetics")  # noqa: F821
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

  # use ids.attr.has_value to check whether a value is set
  @ids_validator("core_profiles")  # noqa: F821
  def validate_core_profiles_filled_in(cp):
    # Unset float 0D:
    assert cp.profiles_1d[0].ion[0].z_ion.has_value  # False, no value set
    assert cp.profiles_1d[0].ion[0].z_ion  # True! Default value is -9e40
    # float 0D equal to 0.0
    cp.profiles_1d[0].ion[0].z_ion = 0.0
    assert cp.profiles_1d[0].ion[0].z_ion.has_value  # True, value set (0.0)
    assert cp.profiles_1d[0].ion[0].z_ion  # False! bool(0.0) is False
