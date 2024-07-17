.. _`defining rules`:

Defining validation rules
===========================

On this page we explain the structure of rules. For a step-by-step guide to
creating new rules, see the :ref:`rule tutorial`.

Rule grouping
-------------

IDS validation is done by applying rules to IDS structures. In this section we
explain how rules are grouped together:

..
  TODO: update Rule definition when multi-IDS validation is implemented

**Rule**
  A Rule is a set of checks that logically belong together. Rules are defined in
  a Python function and applied to one IDS. See the section :ref:`rule
  definition` for more information on rules.

**Rule file**
  Multiple rules can be put in a rule file to group them together. This can be
  useful to, for example, group all checks belonging to a certain IDS together.

  Rules could also be grouped based on functionality instead of IDS. This is
  completely up to the rule developer.

**Rule set**
  Multiple rule files in one folder make up a rule set. Rule sets can be
  selected by users when they want to validate a data entry. They are useful to
  group checks for, for example, specific scenarios (e.g. checking ITER machine
  limits) or specific workflows (e.g. checking constraints expected by the H&CD
  workflow).

  Rules that check the validity of the data according to the generic Data
  Dictionary definition are grouped in a special rule set called ``generic``.
  This generic ruleset is built in to the IDS validator and enabled by default.
  You can specifically disable the generic tests by supplying the
  ``--no-generic`` flag to the Command Line Interface.


Ruleset folder structure
''''''''''''''''''''''''

See below code block for an example directory structure. We can interpret the
folder structure as follows:

- Directories containing **rule sets** (``rule_dir``, ``rule_dir_custom``). The
  IDS Validator can find the rule sets in these directories through the Command
  Line Interface argument ``--extra-rule-dirs /path/to/rule_dir
  /path/to/rule_dir_custom`` or through by setting the environment variable
  ``RULESET_PATH=/path/to/rule_dir:/path/to/rule_dir_custom``.
- Inside these directories we find the **rule sets**: ``Diagnostics``,
  ``ITER-MD``, ``ECR``, ``MyCustomRules``. They can be enabled for validation
  with the Command Line Interface argument ``--ruleset <ruleset_name>``.
- Inside the **rule sets** directories we find the validation rule files
  containing validation functions.

.. code-block:: text
  :caption: Example directory structure for rule sets

  ├── rule_dir
  |   ├── Diagnostics
  |   |   ├── common_ids.py
  |   |   └── equilibrium.py
  |   └── ITER-MD
  |       ├── common_ids.py
  |       └── core_profiles.py
  └── rule_dir_custom
      ├── ECR
      |   ├── common_ids.py
      |   └── core_profiles.py
      └── MyCustomRules
          ├── common_ids.py
          └── equilibrium.py


.. note::

  To make sure that anyone working with the tests or using the ``explore`` tool can 
  properly understand your validation rules, make sure to add docstrings explaining
  your tests. Docstrings are surrounded by triple quotes (``"""my explanation docstring"""``) and defined:

  - At rule level (under function definition)
  - At file level (top of validation rule file)
  - At ruleset level (top of ``__init__.py`` file in ruleset folder)


.. _`rule definition`:

Rule definition
---------------

Validation rules are defined inside the python files as follows:

1. An ``@validator`` decorator indicates which IDS to apply the validator
   function. More details on this decorator can be found in the API
   documentation:
   :py:class:`@validator<ids_validator.rules.data.ValidatorRegistry.validator>`.
2. The ``@validator`` decorator is followed by a Python function definition:
   ``def <rule_name>(arguments...):``. This sets the name of the rule, which
   should be unique.

   .. note::

    The full name of the rule is ``<rule_set>/<rule_file>/<rule_name>``, for
    example a rule ``validate_ids_plugins_metadata`` in the rule file
    ``common_ids.py`` in the rule set ``MyCustomRules`` will be called
    ``MyCustomRules/common_ids.py/validate_plugins_metadata``.

3. A Python docstring describing what the rule checks. This description is
   available to users when any of the assertions in the rule fail. Therefore, it
   should give users an indication of what is being checked and how to fix any
   failing checks.

   The docstring starts and ends with three double quotes (``"""``). See below
   examples.

4. The checks are written in the function body of the rule. Use ``assert``
   statements to check criteria. Several :py:mod:`helper methods
   <ids_validator.rules.helpers>` are available for common types of checks.

   You can write an assertion as follows: ``assert <check>[, "optional
   message"]``, see below examples. When the check evaluates to ``False``, this
   is reported as a failed validation. You can provide an optional message to
   clarify this specific check: this is recommended when the check itself is a
   complex expression and/or not immediately clear to users.

   .. important::

    In contrast to regular Python ``assert`` statements, the validation rule
    continues to be evaluated after a failed ``assert``. This allows to catch
    multiple validation failures in a single rule, instead of stopping after the
    first. It may, however, be surprising to regular Python developers:

    .. code-block:: python
      :caption: Rules continue evaluation after a failed assert

      @validator("core_profiles")
      def validate_profiles_1d(cp):
        assert len(cp.profiles_1d) > 0
        # In regular Python, we don't reach this line when profiles_1d is empty.
        # However, this is a validation rule and we could get an IndexError
        # because evaluation continues even when len(cp.profiles_1d) == 0
        first_profiles = cp.profiles_1d[0]
        ...


.. attention::

  The ``@validator`` decorator and all :py:mod:`helper methods
  <ids_validator.rules.helpers>` are automatically available in rule files. You
  should not try to import them manually from the ``ids_validator`` package.

  Your IDE might complain about undefined variables, but you can safely ignore
  that.


.. code-block:: python
  :caption: Example rule file
  
  """This validation rule file shows example cases of how to define IDS validation rules"""

  @validator("*")
  def validate_ids_plugins_metadata(ids):
    """Validate mandatory attributes in the ids_properties.plugins."""
    plugins = ids.ids_properties.plugins
    for node in plugins.node:
      assert node.path != ""
      for name in node.put_operation:
        assert name != ""
    # etc.

  @validator("gyrokinetics_local")
  def validate_gyrokinetics_electron_definition(gk):
    """Validate that there is an electron species in the species AoS."""
    for species in gk.species:
      if species.charge_norm != -1:
        continue
      assert species.mass_norm == 2.724437108e-4
      assert species.temperature_norm == 1.0
      assert species.density_norm == 1.0
      break
    else:
      assert False, "No electron species found"

  @validator("core_profiles")
  def validate_ion_charge(cp, version=">=3.38.0, <4.0.0"):
    """Validate that profiles_1d/ion/z_ion is defined."""
    for p1d in cp.profiles_1d:
      for ion in p1d.ion:
        assert ion.z_ion.has_value

.. note::

  The dd_version formatting is done according to the
  `packaging module specifiers <https://packaging.pypa.io/en/latest/specifiers.html>`_.
  If a specific version number is required it is formatted as "==3.38.1"
