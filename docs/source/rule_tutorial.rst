.. _`rule tutorial`:

Rule definition tutorial
========================

Here is a step-by-step tutorial to build an ids-validator ruleset for the first time from scratch.

Setting up ids_validator
------------------------

First make a projects folder.

.. code-block:: bash

  mkdir my_projects
  cd my_projects

Follow the :ref:`installation instructions<installing>` to install ids_validator inside the projects folder.
Then go back to the projects folder and create the following ruleset folder structure

.. code-block:: bash

  cd my_projects
  mkdir my_rulesets
  mkdir my_rulesets/my_ruleset
  touch my_rulesets/my_ruleset/my_tests.py

Defining validation rules
-------------------------

The validation rules are defined inside the python files as follows:

- Function with IDS instances
- :py:class:`@validator<ids_validator.rules.data.ValidatorRegistry.validator>` decorator
- Python logic using standard python, IMASPy IDSs and predefined :py:class:`helper methods<ids_validator.rules.helpers>`
- Assert statements describing which conditions should be tested

The function argument is the IDS instance being tested. The IDSs are selected based on the @validator decorator argument

.. note:: There is no need to separately import the helper functions and validator decorator.

Examples
--------

For the first example we make sure that all equilibrium IDSs have a comment.
Add the following validation rule to your rule file.
Select 'equilibrium' in the @validator decorator

.. code-block:: python
  :caption: ``my_rulesets/my_ruleset/my_tests.py``

  @validator("equilibrium")
  def validate_comment(eq):
    assert eq.ids_properties.comment != ""

For the second example we make sure that all IDSs with a 1D time array have strictly increasing time arrays.
Add the following validation rule to your rule file.
Select all IDSs in the @validator decorator using a wildcard selector ``'*'``
Use :py:class:`Select<ids_validator.rules.helpers.Select>` to find all quantities that are called ``"time"`` or have a path that ends in ``"/time"``
Use IMASPy metadata to select only 1D time arrays (and filter out 0D time variables as found in dynamic Arrays of Structures)
Check that their values are strictly :py:class:`Increasing<ids_validator.rules.helpers.Increasing>`

.. code-block:: python
  :caption: ``my_rulesets/my_ruleset/my_tests.py``

  @validator("*")
  def validate_increasing_time(ids):
    for time_quantity in Select(ids, "(^|/)time$", has_value=True):
        # 1D time array:
        if time_quantity.metadata.ndim == 1:
            assert Increasing(time_quantity)


Test run
--------

Now check if the rules are working:
You can use your own data entries or use the one from this example

.. code-block:: bash

  cd ids_validator
  ids_validator validate 'imas:hdf5?path=/work/imas/shared/imasdb/ITER/3/134173/106/' -e ../my_rulesets -r my_ruleset
