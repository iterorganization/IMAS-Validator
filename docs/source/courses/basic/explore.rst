.. _`basic/explore`:

Exploring rulesets with IDS validator
=====================================

As more rules become available, we need a way to keep track of them.
In this section of the training we look at the explore functionality of the IDS validator tool.

The explore functionality can be called from the terminal by 

.. code-block:: console

    $ ids_validator explore

It can use the same filtering flags as the validate module.

Exercise 1
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator explore tool.

        Call the IDS validator explore tool including the custom tests in 'ids-validator-training-rulesets/custom-rulesets'.

        Call the IDS validator explore tool filtering only for tests with 'errorbars' in the name.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ ids_validator explore

            $ ids_validator explore -e ids-validator-training-rulesets/ -r custom_ruleset

            $ ids_validator explore -f errorbars

Since the rule folders can contain a lot of tests and information, the explore function offers the possibility to change the verbosity.

- The --verbose and --no-docstring flags can be used to change the verbosity of the descriptions.
- The --show-empty flag can be used to change whether or not folders/files without any found rules should be shown.

Exercise 2
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator explore tool showing the empty folders and files.

        Call the IDS validator explore tool for different verbosity levels

        What are the differences?

    .. md-tab-item:: Solution

        .. code-block:: console

            $ ids_validator explore --show-empty

            $ ids_validator explore --verbose

            $ ids_validator explore --no_docstring
