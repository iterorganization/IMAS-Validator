"""Generic rules applying to the equilibrium IDS"""

from imas_validator.common.cocos import compute_COCOS

dd_cocos = {"3": 11, "4": 17}


@validator("equilibrium")
def validate_cocos(ids):
    """
    Validate that COCOS computed corresponds to the one in DD.
    """

    ver = str(ids.ids_properties.version_put.data_dictionary.value)[0]
    ref = dd_cocos.get(ver)
    if ref is None:
        raise ValueError(f"Unsupported DD version_put: {ver}")

    # time_slice[:]
    for itime, time_slice in enumerate(ids.time_slice):

        # time_slice[:].profiles_2d
        for i1, profiles_2d in enumerate(time_slice.profiles_2d):

            if not (
                ids.vacuum_toroidal_field.b0.has_value
                and time_slice.global_quantities.ip.has_value
                and time_slice.global_quantities.magnetic_axis.z.has_value
                and time_slice.profiles_1d.psi.has_value
                and time_slice.profiles_1d.q.has_value
                and time_slice.profiles_1d.dpressure_dpsi.has_value
                and profiles_2d.b_field_z.has_value
                and profiles_2d.grid_type.index == 1
                and profiles_2d.psi.has_value
                and profiles_2d.r.has_value
            ):
                continue

            # Compute COCOS
            try:
                # ids._obj instead of ids since '&' operator not supported
                # yet in IMAS-Validator
                cocos = compute_COCOS(ids._obj, itime, i1)["COCOS"]
            except Exception:
                cocos = None

            assert ref == cocos, (
                f"COCOS mismatch for time_slice {itime}, profiles_2d {i1}, "
                f"DD version_put/computed: {ref}/{cocos}"
            )
