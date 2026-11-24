.. _`changelog`:

Changelog
=========


Unreleased
----------

Breaking changes
''''''''''''''''

- The command line tool now returns a non-zero exit status when validation
  fails (``1`` when a rule fails, ``2`` for an unknown command), instead of
  always returning ``0``. Scripts and CI jobs that run
  ``imas_validator validate`` now fail on invalid data.
- ``generic/equilibrium.py:validate_sign``, added during this development cycle,
  is removed. Its checks are replaced by the COCOS rules
  ``generic/cocos.py:validate_cocos{11,17}_*`` and by
  ``generic/equilibrium.py:validate_phi_on_axis``. Rule filters on
  ``validate_sign`` no longer select any rule: use ``--filter cocos`` instead.

New rules
'''''''''

- ``generic/cocos.py``: COCOS sign conventions (COCOS 11 for DD3, COCOS 17 for
  DD4) of the ``equilibrium``, ``core_profiles``, ``edge_profiles``,
  ``plasma_profiles`` and ``summary`` IDSs: signs of q, psi, F, phi and the
  toroidal current density against the signs of Ip and B0.
- ``generic/equilibrium.py``: non-negative pressure, and toroidal flux phi zero
  on the magnetic axis.
- ``generic/ggd.py``: consistency of GGD grids and quantities (filled grid,
  space and subset identifiers, DD3 coordinate types, geometry content and size,
  number of elements per subset, time modes) for the IDSs that use GGD.
- ``generic/identifiers.py``: identifier indices (singular ``index`` and plural
  ``indices``) of every IDS must be defined in their Data Dictionary identifier
  enumeration, and identifier names must match the name or an alias of their
  index. These rules also cover the GGD identifiers, which ``generic/ggd.py`` no
  longer checks against their enumeration. Negative (private) indices are not
  checked. imas-python bundles only the identifier enumerations of its newest DD
  version, which are used for data of every DD version. Because names can change
  between DD versions, a name unknown to the bundled enumeration is not reported; a
  name that the bundled enumeration gives to another index, or that only differs in
  case, is.

New features
''''''''''''

- ``@validator(..., lazy=True)`` declares rules that read only a few nodes. The
  IDS is then lazy loaded when all selected rules applying to it are lazy (see
  :ref:`rule filtering`).
- A ``--filter_name``/``--filter`` string equal to a ruleset name (for example
  ``iter``) also selects that ruleset, so ``-r`` is no longer needed.
- ``validate_min_max`` has a configurable ``underflow_threshold``.

Improvements and bug fixes
''''''''''''''''''''''''''

- IDSs are only read when a selected rule matches their name and occurrence.
- Faster bookkeeping of asserts and of the node coverage.
- NaN values are ignored in the positive temperature and density rules and when
  checking ``error_upper``/``error_lower``.
- The electroneutrality, ``zeff`` and ``n_i_total_over_n_e`` rules of
  ``core_profiles``, ``edge_profiles`` and ``plasma_profiles`` no longer raise
  an error when an ion has no density (or no charge), and no longer use the
  fill value of an unset ``z_ion``: such time slices are skipped.
  ``z_ion_1d`` is used when ``z_ion`` is not set. The ``validate_z_ion`` rules
  of these IDSs check every ion that has a ``z_ion``, not only when the first
  ion has one.
- Node coverage is not computed when disabled, also when a rule raises.
- ``generic/ggd.py:validate_obj_per_dim_geometry_size`` compared the
  ``geometry_content`` structure instead of its index, so the geometry lengths
  were never checked. It now checks them.
- The CLI help explains that options taking several values must come after the
  URIs.
- ``imas-python`` 2.2.0 or later is required.


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

