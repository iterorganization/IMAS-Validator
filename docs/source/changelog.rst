.. _`changelog`:

Changelog
=========


1.1.0
-----

Breaking changes
''''''''''''''''

- :merge:`25`: CLI tool now returns a non-zero exit status when validation
  fails (``1`` when a rule fails, ``2`` for an unknown command), instead of
  always returning ``0``. 

New rules
'''''''''

- :merge:`37`: ``generic/cocos.py``: COCOS sign conventions (COCOS 11 for DD3, COCOS 17 for
  DD4) of the ``equilibrium``, ``core_profiles``, ``edge_profiles``,
  ``plasma_profiles`` and ``summary`` IDSs: signs of q, psi, F, phi and the
  toroidal current density against the signs of Ip and B0.
- ``generic/equilibrium.py``: non-negative pressure, and toroidal flux phi zero
  on the magnetic axis.
- :merge:`11`, :merge:`18`, :merge:`28`: ``generic/ggd.py``: consistency of GGD grids
  and quantities (grid and subset identifiers and indices, coordinate types, number of
  elements per subset, time modes) for the IDSs that use GGD.

New features
''''''''''''

- ``@validator(..., lazy=True)`` declares rules that read only a few nodes. The
  IDS is then lazy loaded when all selected rules applying to it are lazy (see
  :ref:`rule filtering`).
- :merge:`35`: add a new generic rule to check uniqueness of ``name`` identifiers.
- :merge:`38`: add a ``pedantic`` ruleset with generic rules that go beyond strict
  definitions of the DD (until the DD has clearer/stricter description), first rule
  added is checking that all ``AoS/name`` identifiers are not empty.
- ``validate_min_max`` has a configurable ``underflow_threshold``.

Improvements and bug fixes
''''''''''''''''''''''''''

- :merge:`32`, :merge:`39`: fix and improve filtering, add ``-x/--exclude`` option
  and apply same behavior in explore and validate.
- :merge:`23`, :merge:`24`, :merge:`26`, :merge:`27`: performance improvements
  in asserts and node coverage.
- :merge:`30`, :merge:`29`: NaN values are ignored in positive temperature and
  density rules, and when checking ``error_upper``/``error_lower``.
- The electroneutrality, ``zeff`` and ``n_i_total_over_n_e`` rules no longer
  raise an error when an ion has no density (or no charge), and no longer use
  the fill value of an unset ``z_ion``: such time slices are skipped.
  ``z_ion_1d`` is used when ``z_ion`` is not set. The ``validate_z_ion`` rules
  of these IDSs check every ion that has a ``z_ion``, not only when the first
  ion has one.
- :merge:`31`: CLI help explains that options taking several values must come
  after the URIs.
- ``imas-python`` 2.2.0 or later is required, fix pyproject.toml dep.


1.0.0
-----

Breaking changes
''''''''''''''''

- The package is renamed to ``imas_validator`` (was ``ids_validator``).
- The command line tool is renamed to ``imas_validator`` (was
  ``ids_validator``).
- IDS data is accessed with ``imas-python`` (instead of ``imaspy``).

Improvements
''''''''''''

- LGPL license.
- Improved reporting.
- Improved performance when applying the validation rulesets.
- Improved built-in rulesets.
- Various bug fixes.

