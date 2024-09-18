.. _`basic/write`:

Writing validation rulesets for IDS validator
=============================================

This section explains how to write your own tests.
First set up your ruledir with a ruleset folder and a rule file.
For a quick reminder of the ruleset structure look at :ref:`defining rules`.

.. hint::
    :collapsible:

    To create a new ruleset ``my_ruleset`` with one (empty) rule file, run

    .. code-block:: console

        $ mkdir -p tmp/my_ruledir/my_ruleset/
        $ touch tmp/my_ruledir/my_ruleset/my_rulefile.py

If you have your new empty rule file, we need to define validation rules inside.
These are python functions structured like:

1. :py:class:`@validator<ids_validator.rules.data.ValidatorRegistry.validator>`
   decorator specifying which IDSs to target with the function.
2. Function definition accepting IDS instances as arguments.
3. Docstring with a short description of the tests.
4. The tests, which can use standard python logic, IMASPy IDSs and predefined
   :py:class:`helper methods<ids_validator.rules.helpers>`. ``assert`` statements
   describe which conditions should be adhered to.

See :ref:`rule definition` for more information.

.. note:: There is no need to separately import the helper functions and @validator decorator.

Exercise 1
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a simple test to determine whether all ``core_profiles`` IDSs have a comment in their ``ids_properties`` attribute.
        Does the DBentry for ``imas:hdf5?path=ids-validator-course/good`` pass the test?

        .. note::
            If the assert statement is clear on its own, no need to add a custom message.
            Better to use those if the problem is not immediately recognizable from the test and/or code.

    .. md-tab-item:: Tip

        Add ``core_profiles`` in the ``@validator`` decorator to make sure the test is run against all ``core_profiles`` IDSs.
        
        Use ``assert`` to make sure your rule is actually being tested.

    .. md-tab-item:: Solution

        .. code-block:: python
            :caption: ``my_ruledir/my_ruleset/my_rulefile.py``

            """Very informative docstring for the rule file"""
            
            @validator('core_profiles')
            def test_core_profiles_comment(cp):
                """Test whether the comments are filled in for all core_profiles IDSs"""
                assert cp.ids_properties.comment is not None

Exercise 2
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test for ``core_profiles`` IDSs to determine whether the ``time`` array is strictly increasing.
        Use the :py:class:`~ids_validator.rules.helpers.Increasing` helper function.
        Does the DBentry for ``imas:hdf5?path=ids-validator-course/good`` pass the test?

    .. md-tab-item:: Solution

        .. code-block:: python
            :caption: ``my_ruledir/my_ruleset/my_rulefile.py``

            """Very informative docstring for the rule file"""
            
            @validator('core_profiles')
            def test_core_profiles_comment(cp):
                """Test whether the core_profiles base level time arrays are strictly increasing"""
                assert Increasing(cp.time)

Exercise 3
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test for ``core_profiles`` IDSs to determine whether the profiles follow electroneutrality.
        Use the :py:class:`~ids_validator.rules.helpers.Approx` helper function.
        Does the DBentry for ``imas:hdf5?path=ids-validator-course/good`` pass the test?
        What if you use a comparison operator ``==`` instead of the ``Approx`` helper function?

    .. md-tab-item:: Tip

        The positive and negative charges can be determined using

        - profiles_1d[i].ion[j].density

        - profiles_1d[i].ion[j].z_ion

        - profiles_1d[i].electrons.density

    .. md-tab-item:: Solution

        .. code-block:: python
            :caption: ``my_ruledir/my_ruleset/my_rulefile.py``

            """Very informative docstring for the rule file"""

            @validator("core_profiles")
            def validate_electroneutrality_core_profiles(cp):
                """Test whether the core_profiles have electroneutrality"""
                for profiles_1d in cp.profiles_1d:
                    if len(profiles_1d.ion) == 0 or not profiles_1d.ion[0].density.has_value:
                        continue
                    ni_zi = sum(ion.density * ion.z_ion for ion in profiles_1d.ion)
                    assert Approx(profiles_1d.electrons.density, ni_zi)

Exercise 4
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test for all IDSs to determine whether any ``_error_lower`` values are positive.
        Use the :py:class:`~ids_validator.rules.helpers.Select` helper function.
        Does the DBentry for ``imas:hdf5?path=ids-validator-course/good`` pass the test?

    .. md-tab-item:: Tip

        Select all IDSs in the ``@validator`` decorator using a wildcard selector ``'*'``.
        The filtering in the Select helper is done using `Regex <https://www.rexegg.com/regex-quickstart.php>`_ logic.
        Select(ids, "_error_lower$", has_value=True) will get the needed nodes for this test.

    .. md-tab-item:: Solution

        .. code-block:: python
            :caption: ``my_ruledir/my_ruleset/my_rulefile.py``

            """Very informative docstring for the rule file"""

            @validator("*")
            def validate_errors_positive(ids):
                """Validate whether all error bar values are positive"""
                for error_lower in Select(ids, "_error_lower$", has_value=True):
                    assert error_lower >= 0

Exercise 5
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test for all IDSs to determine whether in any case where a ``_min`` and its corresponding ``_max``
        value both exist, the ``_min`` is lower than the ``_max``.
        Use the :py:class:`~ids_validator.rules.helpers.Parent` helper function.
        Does the DBentry for ``imas:hdf5?path=ids-validator-course/good`` pass the test?

    .. md-tab-item:: Tip

        You can get the name of a ``_min`` attribute using ``attr.metadata.name`` and then
        get its ``_max`` counterpart using ``getattr`` on the parent node.

    .. md-tab-item:: Solution

        .. code-block:: python
            :caption: ``my_ruledir/my_ruleset/my_rulefile.py``

            """Very informative docstring for the rule file"""

            @validator("*")
            def validate_min_max(ids):
                """Validate that ``*_min`` values are lower than ``*_max`` values"""
                for quantity_min in Select(ids, "_min$", has_value=True):
                    quantity_name = str(quantity_min.metadata.name)[:-4]  # strip off _min
                    quantity_max = getattr(Parent(quantity_min), quantity_name + "_max", None)

                    # If _max exists and is filled, check that it is >= _min
                    if quantity_max is not None and quantity_max.has_value:
                        assert quantity_min <= quantity_max

Exercise 6
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        What happens if you add ``version=..........`` to the ``@validator`` decorator?
        Why?

    .. md-tab-item:: Solution

        .. code-block:: python
            :caption: ``my_ruledir/my_ruleset/my_rulefile.py``

            bla bla
            bla bla

You can write tests that combine multiple IDSs by adding both of their names in the ``@validator`` decorator.
In that case the occurrence numbers need to be explicitly added like ``@validator("summary:0", "core_profiles:0")``.

Exercise 7
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Write a test that checks if the time arrays for core_profiles and waves are approximately the same.
        Use the :py:class:`~ids_validator.rules.helpers.Approx` helper function.
        Keep in mind that the occurrence number of an IDS needs to be specified for multi-ids validation.
        You can specify the occurrence number by writing the ids name like
        ``core_profiles:0`` in the ``@validator`` decorator.
        Does the DBentry for ``imas:hdf5?path=ids-validator-course/good`` pass the test?
        What happens if you do not specify the occurrence number?

    .. md-tab-item:: Solution

        .. code-block:: python
            :caption: ``my_ruledir/my_ruleset/my_rulefile.py``

            """Very informative docstring for the rule file"""

            @validator("core_profiles:0", "waves:0")
            def validate_min_max(cp, wv):
                """Validate that time array of core_profiles and waves are approximately the same"""
                assert Approx(cp.time, wv.time)
