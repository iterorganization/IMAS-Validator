.. _`basic/explore`:

Exploring rulesets with IMAS-Validator
======================================

As more rules become available, we need a way to keep track of them.
In this section of the training we look at the explore functionality of the IMAS-Validator tool.

The explore functionality can be called from the terminal by 

.. code-block:: console

    $ imas_validator explore

It can use the same filtering flags as the validate module.

Exercise 1
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        1) Call the IMAS-Validator explore tool.

        2) Call the IMAS-Validator explore tool including the custom tests in 'imas-validator-training-rulesets/custom-rulesets'.

        3) Call the IMAS-Validator explore tool filtering only for tests with 'errorbars' in the name.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ imas_validator explore

            $ imas_validator explore -e imas-validator-training-rulesets/ -r custom_ruleset

            $ imas_validator explore -f errorbars

        The output should be a summary of the bundled rules.

        For the second part the summary should be extended with the custom ruleset.

        for the third part the summary should be shortened to only contain the errorbars function.

Since the rule folders can contain a lot of tests and information, the explore function offers the possibility to change the verbosity.

- The --verbose and --no-docstring flags can be used to change the verbosity of the descriptions.
- The --show-empty flag can be used to change whether or not folders/files without any found rules should be shown.

Exercise 2
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        1) Call the IMAS-Validator explore tool showing the empty folders and files.

        2) Call the IMAS-Validator explore tool for different verbosity levels

        3) What are the differences?

    .. md-tab-item:: Solution

        .. code-block:: console

            $ imas_validator explore --show-empty

            $ imas_validator explore --verbose

            $ imas_validator explore --no-docstring
        
       --show-empty will show some folders without any tests.
       --verbose will show full docstrings for all tests.  
       --no_docstring will show no docstrings for tests (but will still show docstrings for rulesets).
