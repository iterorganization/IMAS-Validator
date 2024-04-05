.. _`rule tutorial`:

Rule definition tutorial
========================

Here is a step-by-step tutorial to build an ids-validator ruleset for the first
time from scratch.

.. seealso::
  :ref:`defining rules` for a more in-depth description of validation rules.


Setting up ``ids_validator``
----------------------------

First make a projects folder.

.. code-block:: bash

  mkdir my_projects
  cd my_projects

Follow the :ref:`installation instructions<installing>` to install
``ids_validator`` inside the ``my_projects`` folder. Let's start with creating
the folder structure for our new ruleset:

.. code-block:: console

  my_projects$ ls
  ids-validator
  my_projects$ mkdir -p my_rulesets/my_ruleset
  my_projects$ touch my_rulesets/my_ruleset/my_tests.py

We have created a new rule set ``my_ruleset`` with one (empty) rule file
``my_tests.py``.


Defining validation rules
-------------------------

Next we need to define validation rules in our new rule file. 

1. :py:class:`@validator<ids_validator.rules.data.ValidatorRegistry.validator>`
   decorator
2. Function definition accepting IDS instances as arguments
3. A short description of the tests
4. The tests, which can use standard python logic, IMASPy IDSs and predefined
   :py:class:`helper methods<ids_validator.rules.helpers>`. Assert statements
   describe which conditions should be adhered to.

See :ref:`rule definition` for more information.

.. note:: There is no need to separately import the helper functions and validator decorator.

Examples
''''''''

For the first example we make sure that all ``equilibrium`` IDSs have a comment.
Add the following validation rule to your rule file. Select ``"equilibrium"`` in
the ``@validator`` decorator, then check that ``ids_properties.comment`` is not
empty:

.. code-block:: python
  :caption: ``my_rulesets/my_ruleset/my_tests.py``

  @validator("equilibrium")
  def validate_comment(eq):
    """Validate that ids_properties.comment is filled."""
    assert eq.ids_properties.comment != ""

For the second example we make sure that all ``time`` arrays in all IDSs are
strictly increasing.

1. Select all IDSs in the ``@validator`` decorator using a wildcard selector
   ``'*'``.
2. Use the :py:class:`~ids_validator.rules.helpers.Select` helper method to find
   all quantities that are called ``"time"`` or have a path that ends in
   ``"/time"``.
3. Use IMASPy metadata to select only 1D time arrays (and filter out 0D time
   variables as found in dynamic Arrays of Structures)
4. Check that their values are strictly with the
   :py:class:`~ids_validator.rules.helpers.Increasing` helper method.

.. code-block:: python
  :caption: ``my_rulesets/my_ruleset/my_tests.py``

  @validator("*")
  def validate_increasing_time(ids):
    """Validate all time arrays are strictly increasing"""
    for time_quantity in Select(ids, "(^|/)time$", has_value=True):
        # 1D time array:
        if time_quantity.metadata.ndim == 1:
            assert Increasing(time_quantity)


Run the validations
-------------------

Now we run the IDS validation tool to check if the rules are working. The
arguments we supply are:

- The IMAS URI. You can use the example URI from the public database on SDCC, or
  use a custom data entry.
- ``-e ./my_rulesets`` to indicate that the ``my_rulesets`` folder contains rule
  sets.
- ``-r my_ruleset`` to enable the ``my_ruleset`` rule set that we just created.
- ``--no-generic`` to disable the generic checks, so only our two rules are
  executed.

.. code-block:: console

  my_projects$ ids_validator validate \
    'imas:hdf5?path=/work/imas/shared/imasdb/ITER/3/134102/41' \
    -e ./my_rulesets \
    -r my_ruleset \
    --no-generic


.. note::

  The validator will need to load all data in the supplied data entry. Depending
  on the size of your data entry it may take some time to load this data and
  execut the rules.
