.. _`basic/run`:
Running validations with IDS validator
======================================

In this section we start with the core functionality of the IDS validator: running tests on IDS data.
Some DBentry objects were built specifically for this training course that we will use. You can access them by ............

The easiest way of using the IDS validator is by using the CLI from your terminal.
The only required argument is the imas_uri of the DBentry object.

.. code-block:: console

    $ ids_validator validate '.........'

You can use the generic tests or custom built validation tests.
We start with the generic tests.

# run base test
Exercise 1
.. md-tab-set::

    .. md-tab-item:: Exercise

        Run the IDS validator generic tests for the db_entry with url .................

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

Apart from the bundled tests you can use customly built tests by using the CLI arguments (-e, --extra-rule-dirs)
to determine in which ruleset folders the tool should look for IDS validation rules. 
The structure of these rulesets folders is explained in :ref:`defining rules`.

# run local custom test
Exercise 2
.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator including custom tests for the db_entry with url .................
        The custom rules are defined in the ................. folder.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

# filter rules/rulesets
If you only want to test specific rules you can filter on:
- Rule name (....)
- IDS name (....)
- Rulesets (-r, --ruleset)
- Whether or not to use bundled rules (....)
- Whether or not to use tests for all IDSs (-g, --no-generic)

Exercise 3
.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator including custom tests for the db_entry with url .................
        The custom rules are defined in the ................. folder.
        Run only the ..... tests.
        Try out all the filtering options.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla


# drop in using pdb
Sometimes you want to take a closer look at the data when a test fails.
You can use the (-d, --debug) argument to drop into a debugger console when a test returns an assertion error.

Exercise 4
.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator bundled tests for the db_entry with url ................. with the debugger argument. 
        What is the problem with this DBentry?
        

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

.. note::

    If you want to run the IDS validator tool from a python script, you can do so by importing ``ids_validator.validate``
    The input arguments can be found in the :py:class:`documentation<ids_validator.validate.validate>`
