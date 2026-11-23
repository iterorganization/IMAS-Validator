"""Generic rules applying to the PF_ACTIVE IDS"""

import numpy as np
from imas.ids_defs import EMPTY_FLOAT

# Order of the force columns of force_limits/combination_matrix for each coil
FORCE_NAMES = (
    "force_radial",
    "force_vertical",
    "force_radial_crushing",
    "force_vertical_crushing",
)


def current_limit_at(b_field, b_grid, limits):
    """Current limit at b_field, linearly interpolated in the table (b_grid must be
    increasing) and extrapolated beyond it, and never negative"""
    allowed = np.interp(b_field, b_grid, limits)
    if len(b_grid) < 2:
        return allowed
    low = (limits[1] - limits[0]) / (b_grid[1] - b_grid[0])
    high = (limits[-1] - limits[-2]) / (b_grid[-1] - b_grid[-2])
    allowed = allowed + low * np.minimum(b_field - b_grid[0], 0.0)
    allowed = allowed + high * np.maximum(b_field - b_grid[-1], 0.0)
    return np.maximum(allowed, 0.0)


@validator("pf_active", version="<4")
def validate_coil_name(ids):
    """Validate that pf_active/coil/name is filled in a unique way

    Only for DD < 4: from DD 4 on, uniqueness is checked by
    ``generic/generic.py:validate_unique_names``.
    """
    name_list = [str(coil.name) for coil in ids.coil]
    assert all(len(ele) > 0 for ele in name_list), "All coil/name nodes must be filled"
    assert len(name_list) == len(set(name_list)), "Each coil/name must be unique"


@validator("pf_active", version=">=3.32.1")
def validate_coil_current_limit(ids):
    """Validate that coil(:)/current/data stays within coil(:)/current_limit_max

    Applied to each coil where both nodes are filled. ``current_limit_max`` is
    tabulated against ``b_field_max`` and ``temperature``. The conductor
    temperature is not stored, so the largest limit over all temperatures is used.
    When ``b_field_max_timed/data`` is filled on the same time base as the current,
    the limit is linearly interpolated at that field, and extrapolated beyond the
    tabulated range (as specified for ITER in ITER_D_2ACJT3), but never below
    zero. Otherwise the current is checked against the largest tabulated limit.

    Not applied before DD 3.32.1, when ``coil/current`` was the total current of
    the coil (in ampere-turns) instead of the current per turn.
    """
    for coil in ids.coil:
        limit = coil.current_limit_max
        current = coil.current.data
        if not limit.has_value or not current.has_value:
            continue
        limit_b = np.max(limit, axis=1)
        b_field = coil.b_field_max_timed.data
        b_grid = coil.b_field_max
        if (
            b_field.has_value
            and len(b_field) == len(current)
            and len(b_grid) == len(limit_b)
        ):
            order = np.argsort(b_grid)
            allowed = current_limit_at(
                b_field, np.take(b_grid, order), np.take(limit_b, order)
            )
            assert abs(current) <= allowed, (
                f"Current of coil {coil.name} exceeds current_limit_max"
                " at b_field_max_timed"
            )
        else:
            largest = np.max(limit_b)
            assert (
                abs(current) <= largest
            ), f"Current of coil {coil.name} exceeds the largest current_limit_max"


@validator("pf_active")
def validate_supply_limits(ids):
    """Validate that supply(:)/current/data and supply(:)/voltage/data stay within
    supply(:)/current_limit_min/max and supply(:)/voltage_limit_min/max

    Each bound is only applied when it is filled.
    """
    for supply in ids.supply:
        for quantity in ("current", "voltage"):
            data = getattr(supply, quantity).data
            if not data.has_value:
                continue
            lower = getattr(supply, f"{quantity}_limit_min")
            upper = getattr(supply, f"{quantity}_limit_max")
            if lower.has_value:
                assert (
                    data >= lower
                ), f"{quantity} of supply {supply.name} below {quantity}_limit_min"
            if upper.has_value:
                assert (
                    data <= upper
                ), f"{quantity} of supply {supply.name} above {quantity}_limit_max"


@validator("pf_active", version=">=3.40.0")
def validate_force_limits(ids):
    """Validate that the coil force combinations given by
    force_limits/combination_matrix stay within force_limits/limit_min and limit_max

    Row i of the matrix weights the forces of all coils, in the order
    [coil1 radial, coil1 vertical, coil1 radial crushing, coil1 vertical crushing,
    coil2 radial, ...]. An empty limit value means unbounded. A limit is only
    checked when all the coil forces it uses are filled on the same time base.
    """
    matrix = ids.force_limits.combination_matrix
    if not matrix.has_value:
        return
    assert matrix.shape[1] == 4 * len(
        ids.coil
    ), "force_limits/combination_matrix must have 4 columns per coil"
    if matrix.shape[1] != 4 * len(ids.coil):
        return
    forces = [getattr(coil, name).data for coil in ids.coil for name in FORCE_NAMES]
    limit_min = ids.force_limits.limit_min
    limit_max = ids.force_limits.limit_max
    for i, row in enumerate(matrix):
        columns = [int(j) for j in np.flatnonzero(row)]
        if not columns or not all(forces[j].has_value for j in columns):
            continue
        if len({len(forces[j]) for j in columns}) != 1:
            continue
        combination = sum(row[j] * forces[j] for j in columns)
        if len(limit_min) > i and limit_min[i] != EMPTY_FLOAT:
            assert combination >= limit_min[i], f"Force limit {i} below limit_min"
        if len(limit_max) > i and limit_max[i] != EMPTY_FLOAT:
            assert combination <= limit_max[i], f"Force limit {i} above limit_max"
