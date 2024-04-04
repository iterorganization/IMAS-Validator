Rule definition tutorial
========================

Here is a step-by-step tutorial to build an ids-validator ruleset for the first time from scratch.
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

The validation rules are defined inside the python files as follows:

- function with IDS instances as input
- @validator decorator with IDS toplevel which the validation rule should be applied on as input
- python logic using standard python, IMASPy IDSs and predefined :py:class:`helper methods<ids_validator.rules.helpers>`
- assert statements describing which conditions should be tested

.. note:: There is no need to separately import the helper functions and validator decorator.

For the first example we make sure that all equilibrium IDSs have a comment.
Add the following validation rule to your rule file.

.. code-block:: python

  @validator("equilibrium")
  def validate_comment(eq):
    assert eq.ids_properties.comment.exists

For the second example we make sure that all IDSs with a 1D time array have strictly increasing time arrays.
Add the following validation rule to your rule file.

.. code-block:: python

  @validator("*")
  def validate_increasing_time(ids):
    for time_quantity in Select(ids, "(^|/)time$", has_value=True):
        # 1D time array:
        if time_quantity.metadata.ndim == 1:
            assert Increasing(time_quantity)


Now check if the rules are working:

.. code-block:: bash

  cd ids_validator
  ids_validator my_ids_uri -e ../my_rulesets -r my_ruleset
