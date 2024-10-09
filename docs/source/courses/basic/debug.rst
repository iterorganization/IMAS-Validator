.. _`basic/debug`:

Debugging with IDS validator
============================

In this section we zoom in on what you can do when a validation test fails

First, let's filter the tests so that we only run the failing test.
We do this by adding flags to our command.
If you only want to test specific rules you can filter on:

- Rule name (-f, --filter, --filter_name) 
- IDS name (-f, --filter, --filter_ids)
- Whether or not to use bundled rules (-b, --no-bundled)
- Whether or not to use tests for all IDSs (-g, --no-generic)

.. note::

    Rule name consists of ``<ruleset_name>/<file_name>:<rule_name>``,
    so you can use the --filter option to filter on a specific rule file.


Exercise 1
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator for the db_entry with uri ``imas:hdf5?path=ids-validator-course/bad``

        Run only the failing tests.

        (You can also try out all the filtering options.)

    .. md-tab-item:: Tip

        Use the -f, --filter or --filter_name flag to filter on the name of the failing test.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ ids_validator validate 'imas:hdf5?path=ids-validator-course/bad' -f increasing_time

        The summary report should only show the failing test for all IDS instances.

Sometimes you want to take a closer look at the data when a test fails.
The IDS validator has an optional feature to drop into a Python debugger (`pdb <https://docs.python.org/3/library/pdb.html>`_) console when a test returns an assertion error.
This gives you access in the terminal to the stack traces and local variables in the code.
While the documentation shows a lot more functionality, in this case we focus only on the local variables. 
To activate the Python debugger, use the flag:

- Python debugger (-d, --debug)

Exercise 2
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IDS validator bundled tests for the db_entry with uri ``imas:hdf5?path=ids-validator-course/bad`` with the debugger argument. 
        What is the problem with this DBEntry?
        
    .. md-tab-item:: Tip

        Use the locals() function to list all local variables when in the Python debugger.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ ids_validator validate 'imas:hdf5?path=ids-validator-course/bad' -f increasing_time -d

        Time axis at toplevel is decreasing instead of increasing.
