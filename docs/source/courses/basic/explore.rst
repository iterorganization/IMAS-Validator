.. _`basic/explore`:
Exploring rulesets with IDS validator
=====================================

As more rules become available, we need a way to keep track of them.
In this section of the training we look at the explore functionality of the IDS validator tool.

The explore functionality can be called from the terminal by 

.. code-block:: console

    $ ids_validator explore '.........'

It can use the same filtering flags as the validate module.
# Do first explore
# Do explore with custom tests
# Filter functions explore
Exercise 1
.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator explore tool.
        Call the IDS validator explore tool including the custom tests in ......................
        Call the IDS validator explore tool filtering only for tests using ..................

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

# Change verbosity
# Change whether to show empty folders/files
Since the rule folders can contain a lot of tests and information, the explore function offers the possibility to change the verbosity.
The --verbose and --no-docstring arguments can be used to change the verbosity of the descriptions.
The --show-empty argument can be used to change whether or not folders/files without any found rules should be shown.

Exercise 2
.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator explore tool filtering out the empty folders and files.
        Call the IDS validator explore tool for different verbosity levels
        What are the differences?

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla
