"""Generic rules applying to all IDSs"""

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
            # Use IMASPy's metadata to check that this quantity is not dynamic
            # https://sharepoint.iter.org/departments/POP/CM/IMDesign/Code%20Documentation/IMASPy-doc/generated/imaspy.ids_metadata.IDSType.html#imaspy.ids_metadata.IDSType
            assert (
                not node.metadata.type.is_dynamic
            ), "Dynamic quantity may not be filled when homogeneous_time == 2"


@validator("*")
def validate_increasing_time(ids):
    """Validate that all non-empty time vectors are strictly increasing."""
    dynamic_aos = []
    for time_quantity in Select(ids, "(^|/)time$", has_value=True):
        # 1D time array:
        if time_quantity.metadata.ndim == 1:
            assert Increasing(time_quantity)
        # FLT_0D times also occur for timed arrays of structures
        else:
            # Get the corresponding AoS quantity (e.g. profiles_1d for
            # profiles_1d[0].time):d
            aos = Parent(time_quantity, 2)
            if aos not in dynamic_aos:
                dynamic_aos.append(aos)

    # Validate time "vectors" for timed arrays of structures
    for aos in dynamic_aos:
        last_time = float("-inf")
        for struct in aos:
            assert (
                last_time < struct.time
            ), f"Non-increasing time found for dynamic Array of Structures: {aos!r}"
            last_time = struct.time


@validator("*")
def validate_min_max(ids):
    """Validate that ``*_min`` values are lower than ``*_max`` values, and the related
    value is within the bounds.

    Notes:

    * ``{value}_min <= {value}_max`` is only checked when both values are filled.
    * ``{value}_min <= {value} <= {value}_max`` (value is within bounds) is only
      validated when all three quantities are filled.
    """
    for quantity_min in Select(ids, "_min$", has_value=True):
        quantity_name = str(quantity_min.metadata.name)[:-4]  # strip off _min
        quantity = getattr(Parent(quantity_min), quantity_name, None)
        quantity_max = getattr(Parent(quantity_min), quantity_name + "_max", None)

        # If _max exists and is filled, check that it is >= _min
        if quantity_max is not None and quantity_max.has_value:
            assert quantity_min <= quantity_max

            # quantity exist, is not a structure and is filled, check that the quantity
            # is within bounds:
            if (
                quantity is not None
                and not quantity.metadata.data_type.value.startswith("struct")
                and quantity.has_value
            ):
                assert quantity_min <= quantity <= quantity_max


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
def validate_density_range(ids):
    """Validate that density values are positive and below 1e23"""
    for node in Select(ids, "^((?!_error_).)*$", has_value=True):
        if node.metadata.units == "m^-3":
            assert (
                node >= 0 and node <= 1e23
            ), "Value out of range (0-1e23 m-3) found for a density"


@validator("*")
def validate_temperature_range(ids):
    """Validate that temperature and energy values are positive and below 5 MeV"""
    for node in Select(ids, "^((?!_error_).)*$", has_value=True):
        if node.metadata.units == "eV":
            assert (
                node >= 0 and node <= 5e6
            ), "Value out of range (0-5 MeV) found for a temperature or energy"


# Rules related to max(abs(Ip))
IP_MAX = 1e8


@validator("core_profiles")
def validate_ip_range_cp(ids):
    """Validate that plasma current absolute values are below IP_MAX in core_profiles"""
    if ids.global_quantities.ip.has_value:
        assert (
            abs(ids.global_quantities.ip) <= IP_MAX
        ), "Value out of range found for the plasma current"


@validator("equilibrium")
def validate_ip_range_eq(ids):
    """Validate that plasma current absolute values are below IP_MAX in equilibrium"""
    for time_slice in ids.time_slice:
        if time_slice.constraints.ip.measured.has_value:
            assert (
                abs(time_slice.constraints.ip.measured) <= IP_MAX
            ), "Value out of range found for the plasma current"
        if time_slice.constraints.ip.reconstructed.has_value:
            assert (
                abs(time_slice.constraints.ip.reconstructed) <= IP_MAX
            ), "Value out of range found for the plasma current"
        if time_slice.global_quantities.ip.has_value:
            assert (
                abs(time_slice.global_quantities.ip) <= IP_MAX
            ), "Value out of range found for the plasma current"


@validator("magnetics")
def validate_ip_range_magnetics(ids):
    """Validate that plasma current absolute values are below IP_MAX in magnetics"""
    for ip in ids.ip:
        if ip.data.has_value:
            assert ip.data <= IP_MAX, "Value out of range found for the plasma current"


@validator("summary")
def validate_ip_range_summary(ids):
    """Validate that plasma current absolute values are below IP_MAX in summary"""
    if ids.global_quantities.ip.value.has_value:
        assert (
            abs(ids.global_quantities.ip.value) <= IP_MAX
        ), "Value out of range found for the plasma current"


@validator("core_profiles")
def validate_electroneutrality_core_profiles(ids):
    """Validate that electroneutrality is verified in the CORE_PROFILES IDS"""
    for profiles_1d in ids.profiles_1d:
        if len(profiles_1d.ion) == 0 or not profiles_1d.ion[0].density.has_value:
            continue
        ni_zi = sum(ion.density * ion.z_ion for ion in profiles_1d.ion)
        assert Approx(
            profiles_1d.electrons.density,
            ni_zi,
        ), "Electroneutrality is not verified"


@validator("core_profiles")
def validate_z_ion_core_profiles(ids):
    """Validate that the ion average charge z_ion is consistent
    with ion elements in the CORE_PROFILES IDS"""
    for profiles_1d in ids.profiles_1d:
        if len(profiles_1d.ion) == 0 or not profiles_1d.ion[0].z_ion.has_value:
            continue
        for ion in profiles_1d.ion:
            if len(ion.element) == 0:
                assert len(ion.element) > 0, "ion/element structure must be allocated"
            else:
                zi = sum(abs(element.z_n) * element.atoms_n for element in ion.element)
                assert Approx(
                    abs(ion.z_ion),
                    zi,
                ), "Average ion charge not consistent with ion elements"
