"""Generic rules applying to all IDSs"""

import numpy as np

@validator("*")
def validate_homogeneous_time(ids):
    """Validation function for the time mode (ids_properties.homogeneous_time).

    Executed validations are:

    * homogeneous_time must be set to a valid value (0, 1 or 2)
    * "Static" IDSs must have homogeneous_time = 2
    * Root time must be non-empty when homogeneous_time = 1
    * All dynamic quantities must be empty when homogeneous_time = 2
    """
    assert 0 <= ids.ids_properties.homogeneous_time <= 2
    if not hasattr(ids, "time"):  # static IDSs don't have a root time attribute
        assert (
            ids.ids_properties.homogeneous_time == 2
        ), "Static IDS must have homogeneous_time == 2."

    if ids.ids_properties.homogeneous_time == 1:
        assert ids.time.has_value, "time must be non-empty when homogeneous_time == 1"

    if ids.ids_properties.homogeneous_time == 2:
        # Loop over all filled quantities and assert they are not dynamic
        for node in Select(ids, ".*", has_value=True):
            # Use IMAS-Python's metadata to check that this quantity is not dynamic
            # https://imas-python.readthedocs.io/en/stable/generated/imas.ids_metadata.IDSType.html#imas.ids_metadata.IDSType
            assert (
                not node.metadata.type.is_dynamic
            ), "Dynamic quantity may not be filled when homogeneous_time == 2"


@validator("*")
def validate_increasing_time(ids):
    """Validate that all non-empty time vectors are strictly increasing."""
    if ids.ids_properties.homogeneous_time == 1:
        assert Increasing(ids.time)
    else:
        aos_dict = {}
        for time_quantity in Select(ids, "(^|/)time$", has_value=True):
            # 1D time array:
            if time_quantity.metadata.ndim == 1:
                assert Increasing(time_quantity)
            # FLT_0D times also occur for timed arrays of structures
            else:
                # Get the corresponding AoS quantity (e.g. profiles_1d for
                # profiles_1d[0].time):d
                aos = Parent(time_quantity, 2)
                aos_name = aos._obj.metadata.name
                if aos_name in aos_dict.keys():
                    aos_dict[aos_name] = aos

        # Validate time "vectors" for timed arrays of structures
        for aos in aos_dict.values():
            last_time = float("-inf")
            for struct in aos:
                assert (
                    last_time < struct.time
                ), f"Non-increasing time found for dynamic Array of Structures: {aos!r}"
                last_time = struct.time

@validator("*")
def validate_min_max(ids, underflow_threshold=1e-100):
    """
    Validate that quantity_min <= quantity_max and quantity_min <= quantity <= quantity_max.
    Ignores NaN elements during comparisons and handles IMAS primitive objects.
    """
    def _extract_clean_array(node):
        """Extract float array from IMAS node and filter out NaNs."""
        if node is None or not getattr(node, "has_value", False):
            return None
        val = getattr(node, "value", node)
        try:
            arr = np.asarray(val, dtype=float)
            # Flush float underflow noise directly to 0.0
            return np.where(np.abs(arr) < underflow_threshold, 0.0, arr)
        except (TypeError, ValueError):
            return None

    for quantity_min in Select(ids, "_min$", has_value=True):
        quantity_name = str(quantity_min.metadata.name)[:-4]
        parent = Parent(quantity_min)

        quantity_max = getattr(parent, f"{quantity_name}_max", None)
        quantity = getattr(parent, quantity_name, None)

        val_min = _extract_clean_array(quantity_min)
        val_max = _extract_clean_array(quantity_max)

        if val_min is None or val_max is None:
            continue

        # 1. Validate min <= max (ignoring NaNs)
        mask = ~(np.isnan(val_min) | np.isnan(val_max))
        if np.any(mask):
            assert np.all(val_min[mask] <= val_max[mask]), (
                f"Validation failed: min > max for '{quantity_name}' at path: {quantity_min.metadata.path}"
            )

        # 2. Validate min <= core <= max (ignoring NaNs)
        if (
            quantity is not None
            and getattr(quantity, "has_value", False)
            and not str(getattr(quantity.metadata.data_type, "value", "")).startswith("struct")
        ):
            val_core = _extract_clean_array(quantity)
            if val_core is not None:
                mask_core = mask & ~np.isnan(val_core)
                if np.any(mask_core):
                    in_bounds = (val_min[mask_core] <= val_core[mask_core]) & (val_core[mask_core] <= val_max[mask_core])
                    assert np.all(in_bounds), (
                        f"Validation failed: '{quantity_name}' out of [min, max] bounds at path: {quantity.metadata.path}"
                    )

@validator("*")
def validate_errorbars(ids):
    """Validate that ``*_error_upper`` and `*_error_lower`` values are positive, and
    that error_upper is also filled whenever ``error_lower`` is non empty
    """
    for error_upper in Select(ids, "_error_upper$", has_value=True):
        assert (
            error_upper >= 0
        ), "Negative value found for errorbar, while their values must be positive."

    for error_lower in Select(ids, "_error_lower$", has_value=True):
        assert (
            error_lower >= 0
        ), "Negative value found for errorbar, while their values must be positive."
        error_lower_name = str(error_lower.metadata.name)
        error_upper_name = error_lower_name.replace("_error_lower", "_error_upper")
        error_upper = getattr(Parent(error_lower), error_upper_name, None)
        assert (
            error_upper is not None and error_upper.has_value
        ), "No value found for error_upper, while the related error_lower is filled."


@validator("*")
def validate_density_positive(ids):
    """Validate that density values are positive."""
    for node in Select(ids, r"^((?!_error_).)*$", has_value=True):
        if (
            getattr(node.metadata, "units", None) == "m^-3"
            and "derivative" not in str(node.metadata.path)
        ):
            val = getattr(node, "value", node)
            try:
                arr = np.asarray(val, dtype=float)
            except (TypeError, ValueError):
                continue

            valid_vals = arr[~np.isnan(arr)]
            if valid_vals.size > 0:
                assert np.min(valid_vals) >= 0, (
                    f"Negative value found for a density at path: {node.metadata.path}"
                )

@validator("*")
def validate_temperature_positive(ids):
    """Validate that temperature and energy values are positive."""
    for node in Select(ids, r"^((?!_error_).)*$", has_value=True):
        if (
            getattr(node.metadata, "units", None) == "eV"
            and "derivative" not in str(node.metadata.path)
        ):
            val = getattr(node, "value", node)
            try:
                arr = np.asarray(val, dtype=float)
            except (TypeError, ValueError):
                continue

            valid_vals = arr[~np.isnan(arr)]
            if valid_vals.size > 0:
                assert np.min(valid_vals) >= 0, (
                    f"Negative value found for a temperature or energy at path: {node.metadata.path}"
                )
