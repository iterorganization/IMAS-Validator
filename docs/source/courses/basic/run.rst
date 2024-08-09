.. _`basic/run`:

Running validations with IDS validator
======================================

In this section we start with the core functionality of the IDS validator: running tests on IDS data.
The easiest way of using the IDS validator is by using the CLI from your terminal.
The only required argument is the imas_uri of the DBentry object you want to validate.

.. code-block:: console

    $ ids_validator validate 'imas:hdf5?path=ids-validator-course/good'

You can use the generic tests or custom built validation tests.
We start with the generic tests.

Exercise 1
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Run the IDS validator generic tests for the db_entry with url ``imas:hdf5?path=ids-validator-course/good``

    .. md-tab-item:: Solution

        .. code-block:: console

            $ ids_validator validate 'imas:hdf5?path=ids-validator-course/good'

# TODO: explain how to interpret the summary report

You might want to develop or simply use your own custom tests in addition to the standard
bundled validation tests. You can add customly built tests to the validation process by adding CLI flags
to determine in which ruleset folders the tool should look for IDS validation rules. 
You can find custom rule folders with the (-e, --extra-rule-dirs) flag and define rulesets
with the (-r, --ruleset) flag.
A ruleset is a folder that can contain multiple validation test files, typically grouped per use case.
A rule directory is a folder containing multiple ruleset folders so that the IDS validator can be 
easily told where to look.
The structure of these rulesets folders is further explained in :ref:`defining rules`.

.. code-block:: console

    $ ids_validator validate 'imas:hdf5?path=ids-validator-course/good' -e path/to/my_rule_folder -r my_ruleset

Exercise 2
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator including custom tests for the db_entry with url ``imas:hdf5?path=ids-validator-course/good``
        The custom rules are defined in the 'ids-validator-training-rulesets/custom-rulesets' ruleset folder.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ ids_validator validate 'imas:hdf5?path=ids-validator-course/good' -e ids-validator-training-rulesets/ -r custom_ruleset
            
Exercise 3
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        What happens if you run the tests with ``imas:hdf5?path=ids-validator-course/bad``?

    .. md-tab-item:: Solution

        .. code-block:: console

            Failed validation
            
.. note::

    You can also run the IDS validator tool from a python script. This might be helpful if you want to automatically run your
    data through the validation tool after it is measured/generated.
    You can do so by importing and running ``ids_validator.validate`` in your python script.
    The input arguments can be found in the :py:class:`documentation<ids_validator.validate.validate>`