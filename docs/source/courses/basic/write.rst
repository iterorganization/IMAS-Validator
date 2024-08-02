.. _`basic/write`:
Writing validation rulesets for IDS validator
=============================================

This section explains how to write your own tests.
# explain folder/file structure
First set up your ruledir with a ruleset folder and a rule file.
For a quick reminder of the ruleset structure look at :ref:`defining rules`.
.. hint::
    :collapsible:

    .. code-block:: console

        $ mkdir -p my_ruledir/my_ruleset/my_rulefile.py

Read through :ref:`defining rules` and :ref:`rule tutorual` for information about writing IDS validation rules.

# write obvious test, then write test with optional message
Exercise x
.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a simple test to determine whether all ``core_profiles`` IDSs have a comment in their ``ids_properties`` attribute.
        Does the DBentry for 'imas:hdf5?path=ids-validator-course/good' pass the test?
        .. note::
            If the assert statement is clear on its own, no need to add a custom message.
            Better to use those if the problem is not immediately recognizable from the test/code.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

# go through available helper funcs (also imaspy has_value)
Exercise x
.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test for ``core_profiles`` IDSs to determine whether the ``time`` array is strictly increasing.
        Use the :py:class:`~ids_validator.rules.helpers.Increasing` helper function.
        Does the DBentry for 'imas:hdf5?path=ids-validator-course/good' pass the test?

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

Exercise x
.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test for ``waves`` IDSs to determine whether the ... is approximately the same as ....
        Use the :py:class:`~ids_validator.rules.helpers.Approx` helper function.
        Does the DBentry for 'imas:hdf5?path=ids-validator-course/good' pass the test?
        What if you use a comparison operator ``==`` instead of the ``Approx`` helper function?

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

Exercise x
.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test for all IDSs to determine whether any ``_error_lower`` values are positive.
        Use the :py:class:`~ids_validator.rules.helpers.Select` helper function.
        Does the DBentry for 'imas:hdf5?path=ids-validator-course/good' pass the test?

        .. hint::
            :collapsible:
            Select all IDSs in the ``@validator`` decorator using a wildcard selector ``'*'``.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

Exercise x
.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test for all IDSs to determine whether any case where a ``_min`` and its corresponding ``_max``
        value both exist, the ``_min`` is lower than the ``_max``.
        Use the :py:class:`~ids_validator.rules.helpers.Parent` helper function.
        Does the DBentry for 'imas:hdf5?path=ids-validator-course/good' pass the test?

        .. hint::
            :collapsible:
                You can get the name of a ``_min`` attribute using ``attr.metadata.name`` and then
                get its ``_max`` counterpart using ``getattr`` on the parent node.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

# write test that only works for specific db_entry version
Exercise x
.. md-tab-set::

    .. md-tab-item:: Exercise

        What happens if you add ``version=..........`` to the ``@validator`` decorator?
        Why?

    .. md-tab-item:: Solution

        .. code-block:: console

            $ bla bla
            bla bla

# write test for multi ids
