"""ITER-specific validation rules for the ``pf_active`` IDS.

Sources of the limits:

- [2ACJT3] Y. Gribov, CS and PF coils data and requirements to separatrix
  positioning for analysis of ITER plasma equilibria and poloidal field
  scenarios, ITER_D_2ACJT3 v3.1 (2010), applicable document of the Project
  Requirements (ITER_D_27ZRW8): maximum current per turn vs. maximum field on the
  conductor (Table 2), PF2-PF5 imbalance current, vertical force limits on the
  PF coils (Table 3).
- [3LDS93] Y. Gribov, S. McIntosh, Limits on vertical (axial) forces acting on
  CS, ITER_D_3LDS93 v1.2 (2020): net vertical force on the CS.
- [28B6XQ] SRD-41 (Coil Power Supply and Distribution), ITER_D_28B6XQ v6.0
  (2025, consistent with Baseline 2024): current ratings of the CS/PF power
  supplies (Table 2.2.3). The power supplies are in their full configuration
  from the start of SRO (Section 7.1), so the limits apply to all phases of
  Baseline 2024 (SRO, DT-1, DT-2).

The same values are stored in the ITER machine description ``pf_active`` IDS
(``ITER_MD`` database, pulse 111001, run 204). ``tests/test_pf_active_rules.py``
checks the constants below against it when it is available.

Power supply voltage limits are not checked here, because the supplies are not
identified consistently in scenario data. The generic rules check them when
``supply(:)/voltage_limit_min/max`` are filled.
"""

import numpy as np

_CS = ([12.6, 13.0], [4.3], [[45000.0], [40000.0]])

# Maximum current per turn [A] vs. maximum field on the conductor [2ACJT3, Table 2]
# as (b_field_max [T], temperature [K], current_limit_max[b_field_max, temperature]),
# as in coil(:)/current_limit_max. The 3.9 K column of PF6 is its operation with
# 0.4 K subcooling. A zero limit means that the coil cannot operate at that field
# and temperature.
COIL_CURRENT_LIMITS = {
    "CS3U": _CS,
    "CS2U": _CS,
    "CS1U": _CS,
    "CS1L": _CS,
    "CS2L": _CS,
    "CS3L": _CS,
    "PF1": ([6.4, 6.5], [4.3], [[48000.0], [41000.0]]),
    "PF2": ([4.8, 5.0], [4.3], [[55000.0], [50000.0]]),
    "PF3": ([4.8, 5.0], [4.3], [[55000.0], [50000.0]]),
    "PF4": ([4.8, 5.0], [4.3], [[55000.0], [50000.0]]),
    "PF5": ([5.7, 6.0], [4.3], [[52000.0], [33000.0]]),
    "PF6": (
        [6.4, 6.5, 6.8, 7.0],
        [3.9, 4.3],
        [[52000.0, 48000.0], [52000.0, 41000.0], [52000.0, 0.0], [41000.0, 0.0]],
    ),
}

# Current limit [A] of the power supply feeding each coil, as in
# supply(:)/current_limit_max of ITER_MD 111001/204 (the supplies are symmetric:
# limit_min = -limit_max). Note: SRD-41 v6.0 [28B6XQ, Table 2.2.3] gives 52 kA
# for PF5 and PF6.
SUPPLY_CURRENT_LIMITS = {
    "CS3U": 45000.0,
    "CS2U": 45000.0,
    "CS1U": 45000.0,
    "CS1L": 45000.0,
    "CS2L": 45000.0,
    "CS3L": 45000.0,
    "PF1": 48000.0,
    "PF2": 55000.0,
    "PF3": 55000.0,
    "PF4": 55000.0,
    "PF5": 55000.0,
    "PF6": 48000.0,
}

# Maximum absolute imbalance current I_PF2 + I_PF3 - I_PF4 - I_PF5 [A], the
# current in the VS1 converter [2ACJT3]
IMBALANCE_CURRENT_LIMIT = 22500.0

# Scenario codes often model CS1U and CS1L, which are connected in series, as a
# single coil CS1
ALIASES = {"CS1": "CS1U"}

CS_STACK = ("CS3U", "CS2U", "CS1U", "CS1L", "CS2L", "CS3L")

# Vertical force limits [N] as (coils, limit_min, limit_max): the sum of
# coil(:)/force_vertical of the coils must stay within the limits [2ACJT3, Table 3],
# [3LDS93, Section 2]. The limits on the forces across the CS gaps [3LDS93,
# Section 1] also need the radial and crushing forces: the generic rule checks
# them when force_limits is filled.
VERTICAL_FORCE_LIMITS = {
    "CS stack": (CS_STACK, -60e6, 60e6),
    "PF1": (("PF1",), -150e6, 110e6),
    "PF2": (("PF2",), -75e6, 15e6),
    "PF3": (("PF3",), -90e6, 40e6),
    "PF4": (("PF4",), -40e6, 90e6),
    "PF5": (("PF5",), -10e6, 160e6),
    "PF6": (("PF6",), -190e6, 170e6),
    "PF3+PF4": (("PF3", "PF4"), -60e6, 10e6),
}


def coil_key(coil):
    """Return the name of the coil in the tables above (or in ALIASES), or None
    if it is unknown

    The coil is identified by its identifier (DD3), its name, or the text between
    the last brackets of its name, for example "Poloidal Field Coil 1 (PF1)".
    """
    candidates = [str(getattr(coil, "identifier", "")).strip()]
    name = str(coil.name).strip()
    candidates.append(name)
    if name.endswith(")") and "(" in name:
        candidates.append(name[name.rindex("(") + 1 : -1].strip())
    for candidate in candidates:
        key = candidate.upper()
        if key in COIL_CURRENT_LIMITS or key in ALIASES:
            return key
    return None


def current_limit_at(b_field, b_grid, limits):
    """Current limit at b_field, linearly interpolated in the table and
    extrapolated beyond it [2ACJT3], and never negative"""
    allowed = np.interp(b_field, b_grid, limits)
    if len(b_grid) < 2:
        return allowed
    low = (limits[1] - limits[0]) / (b_grid[1] - b_grid[0])
    high = (limits[-1] - limits[-2]) / (b_grid[-1] - b_grid[-2])
    allowed = allowed + low * np.minimum(b_field - b_grid[0], 0.0)
    allowed = allowed + high * np.maximum(b_field - b_grid[-1], 0.0)
    return np.maximum(allowed, 0.0)


@validator("pf_active", version=">=3.32.1")
def validate_coil_current(ids):
    """Validate that coil(:)/current/data of the ITER CS and PF coils stays within
    the conductor current limit and the current limit of the power supply

    The conductor limit is linearly interpolated (or extrapolated) at
    coil(:)/b_field_max_timed/data when it is filled on the same time base as the
    current, and is otherwise the largest tabulated value. The most permissive
    conductor temperature is assumed (for PF6: operation with 0.4 K subcooling).
    Coils are identified by identifier or name; other coils (for example VS) are
    not checked.

    Not applied before DD 3.32.1, when coil/current was the total current of the
    coil (in ampere-turns) instead of the current per turn.
    """
    for coil in ids.coil:
        key = coil_key(coil)
        current = coil.current.data
        if key is None or not current.has_value:
            continue
        b_grid, _, table = COIL_CURRENT_LIMITS[ALIASES.get(key, key)]
        b_grid = np.array(b_grid)
        limit_b = np.max(table, axis=1)
        b_field = coil.b_field_max_timed.data
        if b_field.has_value and len(b_field) == len(current):
            allowed = current_limit_at(b_field, b_grid, limit_b)
            assert abs(current) <= allowed, (
                f"Current of coil {key} exceeds the conductor limit at"
                " b_field_max_timed"
            )
        else:
            assert abs(current) <= np.max(limit_b), (
                f"Current of coil {key} exceeds the conductor limit"
                f" {np.max(limit_b)} A"
            )
        supply_limit = SUPPLY_CURRENT_LIMITS[ALIASES.get(key, key)]
        assert (
            abs(current) <= supply_limit
        ), f"Current of coil {key} exceeds the power supply limit {supply_limit} A"


@validator("pf_active", version=">=3.32.1")
def validate_imbalance_current(ids):
    """Validate that the PF2-PF5 imbalance current I_PF2 + I_PF3 - I_PF4 - I_PF5,
    which flows in the VS1 converter, stays within +-22.5 kA

    Checked when coil(:)/current/data of PF2 to PF5 are filled on the same time
    base. Not applied before DD 3.32.1 (current in ampere-turns).
    """
    currents = {}
    for coil in ids.coil:
        key = coil_key(coil)
        if key in ("PF2", "PF3", "PF4", "PF5") and coil.current.data.has_value:
            currents[key] = coil.current.data
    if len(currents) != 4 or len({len(c) for c in currents.values()}) != 1:
        return
    imbalance = currents["PF2"] + currents["PF3"] - currents["PF4"] - currents["PF5"]
    assert (
        abs(imbalance) <= IMBALANCE_CURRENT_LIMIT
    ), f"PF2-PF5 imbalance current exceeds {IMBALANCE_CURRENT_LIMIT} A"


@validator("pf_active", version=">=3.40.0")
def validate_vertical_force(ids):
    """Validate that coil(:)/force_vertical/data of the ITER PF coils and of the CS
    stack stays within the vertical force limits

    A limit is checked when the vertical force of all its coils is filled on the
    same time base. For the CS stack, a single CS1 coil replaces CS1U and CS1L.
    """
    forces = {}
    for coil in ids.coil:
        key = coil_key(coil)
        if key is not None and coil.force_vertical.data.has_value:
            forces[key] = coil.force_vertical.data
    for label, (coils, lower, upper) in VERTICAL_FORCE_LIMITS.items():
        if coils == CS_STACK and "CS1" in forces:
            coils = ("CS3U", "CS2U", "CS1", "CS2L", "CS3L")
        if not all(c in forces for c in coils):
            continue
        if len({len(forces[c]) for c in coils}) != 1:
            continue
        total = sum(forces[c] for c in coils)
        assert (
            lower <= total <= upper
        ), f"Vertical force on {label} outside [{lower}, {upper}] N"
